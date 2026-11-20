"""Round endpoints: the current phase, the investigation menu, choices,
readiness, what a player holds, and the host's move-on (spec 0093, C and D).

Route handlers are thin: authenticate, call one engine function, map the
engine's refusal code to a status. No rule lives here.

Endpoints (base path /v1/sessions/{session_id}):
  GET  /round            optional JWT     Current beat, phase and deadline (public facts)
  GET  /me/menu          player JWT       This player's menu and budget
  POST /me/choices       player JWT       Make a choice (repeat-safe on choice_id)
  POST /me/ready         player JWT       Mark ready for the phase the player saw
  GET  /me/holdings      player JWT       What this player found for themselves
  POST /round/move-on    host seat|host JWT  End the current phase by hand
  GET  /me/theory        player JWT       This player's theory form and saved draft
  PUT  /me/theory        player JWT       Save (replace) this player's draft
  POST /me/theory/lock   player JWT       Lock the saved draft
  GET  /closing          optional JWT     Reveal, result and recap, as far as reached
  GET  /me/result        player JWT       This player's own part of the result
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth import JwtClaims, optional_player_or_host_jwt
from api.auth.seat import require_host_control
from api.routers.events import _get_or_create_session_state
from api.routers.mini_games import ParticipantContext, require_valid_participant
from api.schemas import (
    AccountPartResponse,
    ChoiceRequest,
    ChoiceResponse,
    ClosingResponse,
    HeldConceptResponse,
    HoldingsResponse,
    MenuItemResponse,
    MenuResponse,
    PhaseStateResponse,
    PrivateResultResponse,
    ReadyRequest,
    RewardGrantResponse,
    RoundStateResponse,
    TheoryDraftRequest,
    TheoryFormResponse,
    TheoryOptionResponse,
    TheoryResponse,
    TheorySlotResponse,
)
from engine.db import get_async_session
from engine.events.models import ContentEvent
from engine.session import choices, closing, commit_phase, phases
from engine.session.phases import RoundError

router = APIRouter(prefix="/sessions", tags=["rounds"])

_NOT_FOUND = {"session_not_found"}
_FORBIDDEN = {"not_a_participant"}


def _now() -> datetime:
    return datetime.now(tz=timezone.utc)


def _publisher(session_id: UUID) -> Callable[[ContentEvent], Awaitable[ContentEvent]]:
    bus, _registry = _get_or_create_session_state(session_id)
    return bus.publish


async def _commit_then_tell(
    db: AsyncSession, outbox: phases.Outbox, session_id: UUID
) -> None:
    """Save, and only then send what the engine queued. If the save fails
    nothing is sent. The request's own commit afterwards has nothing left.
    Call it with ``phases.delivery_lock`` held, taken before the engine call."""
    await db.commit()
    await outbox.flush(_publisher(session_id))


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
        phase_entry=state.entry,
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
        beat_name=view.beat_name,
        phase_entry=view.phase_entry,
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
        rewards=[
            RewardGrantResponse(
                grant_id=r.grant_id,
                run_id=r.run_id,
                beat_id=r.beat_id,
                amount=r.amount,
                kind=r.kind,
            )
            for r in menu.rewards
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
    outbox = phases.Outbox(session_id)
    async with phases.delivery_lock(session_id):
        try:
            result = await choices.choose(
                db,
                session_id,
                who.claims.player_id,
                body.choice_id,
                body.opportunity_id,
                _now(),
                outbox,
            )
        except RoundError as error:
            raise _refuse(error)
        await _commit_then_tell(db, outbox, session_id)
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
    body: ReadyRequest,
    who: ParticipantContext = Depends(require_valid_participant),
    db: AsyncSession = Depends(get_async_session),
) -> PhaseStateResponse:
    """Mark this player ready for the phase they saw. If the round has moved
    on since, nothing is saved and the current state comes back."""
    assert who.claims.player_id is not None
    outbox = phases.Outbox(session_id)
    async with phases.delivery_lock(session_id):
        try:
            state = await phases.mark_ready(
                db,
                session_id,
                who.claims.player_id,
                _now(),
                outbox,
                phase_entry=body.phase_entry,
            )
        except RoundError as error:
            raise _refuse(error)
        await _commit_then_tell(db, outbox, session_id)
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
            HeldConceptResponse(
                concept_id=h.concept_id,
                label=h.label,
                text=h.text,
                found_from=h.found_from,
                found_in_beat=h.found_in_beat,
                found_in_round_title=h.found_in_round_title,
                found_in_round_number=h.found_in_round_number,
            )
            for h in held
        ]
    )


@router.post("/{session_id}/round/move-on", response_model=PhaseStateResponse)
async def move_on(
    session_id: UUID,
    claims: JwtClaims = Depends(require_host_control),
    db: AsyncSession = Depends(get_async_session),
) -> PhaseStateResponse:
    """The host ends the current phase by hand."""
    _require_session_match(session_id, claims)
    outbox = phases.Outbox(session_id)
    async with phases.delivery_lock(session_id):
        try:
            state = await phases.host_move_on(db, session_id, _now(), outbox)
        except RoundError as error:
            raise _refuse(error)
        await _commit_then_tell(db, outbox, session_id)
    return _phase_state_response(state)


def _theory_response(theory: commit_phase.Theory) -> TheoryResponse:
    return TheoryResponse(
        state=theory.state,
        answers=theory.answers,
        proof=theory.proof,
        revision=theory.revision,
    )


def _option(option: commit_phase.FormOption) -> TheoryOptionResponse:
    return TheoryOptionResponse(
        value=option.value, label=option.label, text=option.text
    )


@router.get("/{session_id}/me/theory", response_model=TheoryFormResponse)
async def get_theory(
    session_id: UUID,
    who: ParticipantContext = Depends(require_valid_participant),
    db: AsyncSession = Depends(get_async_session),
) -> TheoryFormResponse:
    """This player's theory form and their own saved draft or lock. Private to
    them; it never says whether anything is right."""
    assert who.claims.player_id is not None
    try:
        form = await phases.read_theory_form(
            db, session_id, who.claims.player_id, _now()
        )
    except RoundError as error:
        raise _refuse(error)
    return TheoryFormResponse(
        open=form.open,
        phase_entry=form.phase_entry,
        deadline_at=form.deadline_at,
        seconds_left=form.seconds_left,
        slots=[
            TheorySlotResponse(
                slot_id=s.slot_id,
                label=s.label,
                kind=s.kind,  # type: ignore[arg-type]
                options=[_option(o) for o in s.options],
            )
            for s in form.slots
        ],
        account=[
            AccountPartResponse(text=p.text, slot_id=p.slot_id) for p in form.account
        ],
        proof_options=[_option(o) for o in form.proof_options],
        theory=_theory_response(form.theory),
    )


@router.put("/{session_id}/me/theory", response_model=TheoryResponse)
async def save_theory(
    session_id: UUID,
    body: TheoryDraftRequest,
    who: ParticipantContext = Depends(require_valid_participant),
    db: AsyncSession = Depends(get_async_session),
) -> TheoryResponse:
    """Save this player's draft, replacing the last. Refused after a lock."""
    assert who.claims.player_id is not None
    outbox = phases.Outbox(session_id)
    async with phases.delivery_lock(session_id):
        try:
            theory = await phases.save_theory_draft(
                db,
                session_id,
                who.claims.player_id,
                body.answers,
                body.proof,
                _now(),
                outbox,
            )
        except RoundError as error:
            raise _refuse(error)
        await _commit_then_tell(db, outbox, session_id)
    return _theory_response(theory)


@router.post("/{session_id}/me/theory/lock", response_model=TheoryResponse)
async def lock_theory(
    session_id: UUID,
    who: ParticipantContext = Depends(require_valid_participant),
    db: AsyncSession = Depends(get_async_session),
) -> TheoryResponse:
    """Lock this player's saved draft. Final: nothing more is accepted from
    them, and the shared screen and host learn only that they have locked."""
    assert who.claims.player_id is not None
    outbox = phases.Outbox(session_id)
    async with phases.delivery_lock(session_id):
        try:
            theory = await phases.lock_theory(
                db, session_id, who.claims.player_id, _now(), outbox
            )
        except RoundError as error:
            raise _refuse(error)
        await _commit_then_tell(db, outbox, session_id)
    return _theory_response(theory)


@router.get("/{session_id}/closing", response_model=ClosingResponse)
async def get_closing(
    session_id: UUID,
    claims: JwtClaims | None = Depends(optional_player_or_host_jwt),
    db: AsyncSession = Depends(get_async_session),
) -> ClosingResponse:
    """The reveal, the public result and the recap, each once its phase has
    begun, so a screen can rebuild after a reconnect. Public facts only (a
    display surface has no token); nothing private and, before the result
    phase, no right or wrong."""
    if claims is not None:
        _require_session_match(session_id, claims)
    try:
        view = await closing.closing_view(db, session_id)
    except RoundError as error:
        raise _refuse(error)
    return ClosingResponse(
        reveal=view.reveal,  # type: ignore[arg-type]
        result=view.result,  # type: ignore[arg-type]
        recap=view.recap,  # type: ignore[arg-type]
    )


@router.get("/{session_id}/me/result", response_model=PrivateResultResponse)
async def get_my_result(
    session_id: UUID,
    who: ParticipantContext = Depends(require_valid_participant),
    db: AsyncSession = Depends(get_async_session),
) -> PrivateResultResponse:
    """This player's own slots, right and wrong. Refused until the result phase
    has begun; never another player's."""
    assert who.claims.player_id is not None
    try:
        view = await closing.closing_view(db, session_id, who.claims.player_id)
    except RoundError as error:
        raise _refuse(error)
    if view.private is None:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "result_not_ready",
                "message": "the result has not been worked out",
            },
        )
    return PrivateResultResponse(**view.private)
