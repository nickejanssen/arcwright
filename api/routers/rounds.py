"""Round endpoints: the current phase, the investigation menu, choices,
readiness, what a player holds, and the host's move-on (spec 0093, C and D).

Route handlers are thin: authenticate, call one engine function, map the
engine's refusal code to a status. No rule lives here.

Endpoints (base path /v1/sessions/{session_id}):
  GET  /round            optional JWT     Current beat, phase and deadline (public facts)
  GET  /me/menu          player JWT       This player's menu and budget
  POST /me/choices       player JWT       Make a choice (repeat-safe on choice_id)
  POST /me/ready         player JWT       Mark ready for the current phase
  GET  /me/holdings      player JWT       What this player found for themselves
  POST /round/move-on    host JWT         End the current phase by hand
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth import JwtClaims, optional_player_or_host_jwt, require_host_jwt
from api.routers.events import _get_or_create_session_state
from api.routers.mini_games import ParticipantContext, require_valid_participant
from api.schemas import (
    ChoiceRequest,
    ChoiceResponse,
    HeldConceptResponse,
    HoldingsResponse,
    MenuItemResponse,
    MenuResponse,
    PhaseStateResponse,
    RoundStateResponse,
)
from engine.db import get_async_session
from engine.events.models import ContentEvent
from engine.session import choices, phases
from engine.session.phases import RoundError

router = APIRouter(prefix="/sessions", tags=["rounds"])

_NOT_FOUND = {"session_not_found"}
_FORBIDDEN = {"not_a_participant"}


def _now() -> datetime:
    return datetime.now(tz=timezone.utc)


def _publisher(session_id: UUID) -> Callable[[ContentEvent], Awaitable[ContentEvent]]:
    bus, _registry = _get_or_create_session_state(session_id)
    return bus.publish


def _refuse(error: RoundError) -> HTTPException:
    if error.code in _NOT_FOUND:
        status = 404
    elif error.code in _FORBIDDEN:
        status = 403
    else:
        status = 409
    return HTTPException(
        status_code=status, detail={"code": error.code, "message": str(error)}
    )


def _require_session_match(session_id: UUID, claims: JwtClaims) -> None:
    if claims.session_id is not None and claims.session_id != session_id:
        raise HTTPException(
            status_code=403,
            detail="Token session_id does not match requested session",
        )


def _phase_state_response(state: phases.PhaseState) -> PhaseStateResponse:
    return PhaseStateResponse(
        beat_id=state.beat_id,
        phase=state.phase,
        status=state.status,
        deadline_at=state.deadline_at,
    )


@router.get("/{session_id}/round", response_model=RoundStateResponse)
async def get_round(
    session_id: UUID,
    claims: JwtClaims | None = Depends(optional_player_or_host_jwt),
    db: AsyncSession = Depends(get_async_session),
) -> RoundStateResponse:
    """Current beat, phase and deadline, so a screen can rebuild after a
    reconnect. Public facts only; a display surface has no token."""
    if claims is not None:
        _require_session_match(session_id, claims)
    try:
        view = await phases.round_view(db, session_id, _now())
    except RoundError as error:
        raise _refuse(error)
    return RoundStateResponse(
        session_status=view.session_status,
        beat_id=view.beat_id,
        phase=view.phase,
        phase_index=view.phase_index,
        status=view.status,
        deadline_at=view.deadline_at,
        seconds_left=view.seconds_left,
        ready_count=view.ready_count,
        player_count=view.player_count,
        lines=list(view.lines),
    )


@router.get("/{session_id}/me/menu", response_model=MenuResponse)
async def get_menu(
    session_id: UUID,
    who: ParticipantContext = Depends(require_valid_participant),
    db: AsyncSession = Depends(get_async_session),
) -> MenuResponse:
    """This player's investigation menu and remaining budget."""
    assert who.claims.player_id is not None
    try:
        menu = await choices.read_menu(db, session_id, who.claims.player_id)
    except RoundError as error:
        raise _refuse(error)
    return MenuResponse(
        open=menu.open,
        remaining_budget=menu.remaining_budget,
        items=[
            MenuItemResponse(
                opportunity_id=i.opportunity_id,
                subject_id=i.subject_id,
                subject_kind=i.subject_kind,
                subject_label=i.subject_label,
                label=i.label,
                cost=i.cost,
                taken=i.taken,
            )
            for i in menu.items
        ],
    )


@router.post("/{session_id}/me/choices", response_model=ChoiceResponse)
async def make_choice(
    session_id: UUID,
    body: ChoiceRequest,
    who: ParticipantContext = Depends(require_valid_participant),
    db: AsyncSession = Depends(get_async_session),
) -> ChoiceResponse:
    """Choose from the menu. Sending the same choice_id twice has one effect
    and returns the same answer."""
    assert who.claims.player_id is not None
    try:
        result = await choices.choose(
            db,
            session_id,
            who.claims.player_id,
            body.choice_id,
            body.opportunity_id,
            _now(),
            _publisher(session_id),
        )
    except RoundError as error:
        raise _refuse(error)
    return ChoiceResponse(
        choice_id=result.choice_id,
        opportunity_id=result.opportunity_id,
        content=result.content,
        gave=result.gave,
        cost=result.cost,
        first_time=result.first_time,
        replayed=result.replayed,
        remaining_budget=result.remaining_budget,
    )


@router.post("/{session_id}/me/ready", response_model=PhaseStateResponse)
async def mark_ready(
    session_id: UUID,
    who: ParticipantContext = Depends(require_valid_participant),
    db: AsyncSession = Depends(get_async_session),
) -> PhaseStateResponse:
    """Mark this player ready for the current phase."""
    assert who.claims.player_id is not None
    try:
        state = await phases.mark_ready(
            db, session_id, who.claims.player_id, _now(), _publisher(session_id)
        )
    except RoundError as error:
        raise _refuse(error)
    return _phase_state_response(state)


@router.get("/{session_id}/me/holdings", response_model=HoldingsResponse)
async def get_holdings(
    session_id: UUID,
    who: ParticipantContext = Depends(require_valid_participant),
    db: AsyncSession = Depends(get_async_session),
) -> HoldingsResponse:
    """What this player found for themselves, with its written text."""
    assert who.claims.player_id is not None
    try:
        held = await choices.read_holdings(db, session_id, who.claims.player_id)
    except RoundError as error:
        raise _refuse(error)
    return HoldingsResponse(
        concepts=[
            HeldConceptResponse(concept_id=h.concept_id, label=h.label, text=h.text)
            for h in held
        ]
    )


@router.post("/{session_id}/round/move-on", response_model=PhaseStateResponse)
async def move_on(
    session_id: UUID,
    claims: JwtClaims = Depends(require_host_jwt),
    db: AsyncSession = Depends(get_async_session),
) -> PhaseStateResponse:
    """The host ends the current phase by hand."""
    _require_session_match(session_id, claims)
    try:
        state = await phases.host_move_on(
            db, session_id, _now(), _publisher(session_id)
        )
    except RoundError as error:
        raise _refuse(error)
    return _phase_state_response(state)
