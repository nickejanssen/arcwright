"""The room view, the seat, survey answers and hand-over (AW-331, spec 0095).

Route handlers are thin: authenticate, call one engine function, map the
engine's refusal code to a status. No rule lives here.

Endpoints (base path /v1/sessions/{session_id}):
  GET  /room             none          The public room view, for the shared screen
  GET  /me/seat          player JWT    This seat's role: host or player
  GET  /me/survey        player JWT    This player's newest survey answers
  PUT  /me/survey        player JWT    Save (replace) this player's survey answers
  POST /host/hand-over   host control  Give the host seat to another seated player
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth import JwtClaims
from api.auth.seat import require_host_control
from api.routers.events import _get_or_create_session_state
from api.routers.mini_games import ParticipantContext, require_valid_participant
from api.schemas.room import (
    HandOverRequest,
    HandOverResponse,
    RoomPlayerResponse,
    RoomResponse,
    SeatResponse,
    SurveyRequest,
    SurveyResponse,
)
from engine.db import get_async_session
from engine.db.orm import SessionParticipant
from engine.events.models import ContentEvent
from engine.session import host_seat, phases, survey
from engine.session.phases import RoundError
from engine.session.room_view import room_view

router = APIRouter(prefix="/sessions", tags=["room"])

_NOT_FOUND = {"session_not_found"}
_FORBIDDEN = {"not_a_participant", "not_your_character"}
_UNPROCESSABLE = {"invalid_survey"}


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
    elif error.code in _UNPROCESSABLE:
        status = 422
    else:
        status = 409
    return HTTPException(
        status_code=status, detail={"code": error.code, "message": str(error)}
    )


@router.get("/{session_id}/room", response_model=RoomResponse)
async def get_room(
    session_id: UUID,
    db: AsyncSession = Depends(get_async_session),
) -> RoomResponse:
    """The public room view. No sign-in: the shared screen holds none, and every
    caller gets the same answer."""
    try:
        view = await room_view(db, session_id, _now())
    except RoundError as error:
        raise _refuse(error)
    return RoomResponse(
        session_status=view.session_status,
        round_title=view.round_title,
        phase=view.phase,
        phase_entry=view.phase_entry,
        deadline_at=view.deadline_at,
        seconds_left=view.seconds_left,
        paused=view.paused,
        paused_by=view.paused_by,
        lines=list(view.lines),
        players=[
            RoomPlayerResponse(
                participant_id=p.participant_id,
                display_name=p.display_name,
                ready=p.ready,
                locked=p.locked,
                answered_survey=p.answered_survey,
                is_host=p.is_host,
            )
            for p in view.players
        ],
        ready_count=view.ready_count,
        player_count=view.player_count,
        over=view.over,
        closing=view.closing,
    )


@router.get("/{session_id}/me/seat", response_model=SeatResponse)
async def get_my_seat(
    session_id: UUID,
    who: ParticipantContext = Depends(require_valid_participant),
    db: AsyncSession = Depends(get_async_session),
) -> SeatResponse:
    """Whether this phone's seat is the host seat, so it knows which menu to show."""
    assert who.claims.player_id is not None
    name = await db.scalar(
        select(SessionParticipant.display_name).where(
            SessionParticipant.participant_id == who.claims.player_id
        )
    )
    is_host = await host_seat.is_host_seat(db, session_id, who.claims.player_id)
    return SeatResponse(
        participant_id=who.claims.player_id,
        display_name=name,
        role="host" if is_host else "player",
    )


@router.get("/{session_id}/me/survey", response_model=SurveyResponse)
async def get_my_survey(
    session_id: UUID,
    who: ParticipantContext = Depends(require_valid_participant),
    db: AsyncSession = Depends(get_async_session),
) -> SurveyResponse:
    """This player's newest answers. Nobody else can read them."""
    assert who.claims.player_id is not None
    try:
        saved = await survey.read_survey(db, session_id, who.claims.player_id)
    except RoundError as error:
        raise _refuse(error)
    if saved is None:
        return SurveyResponse(answered=False)
    return SurveyResponse(answered=True, answers=saved.answers, comment=saved.comment)


@router.put("/{session_id}/me/survey", response_model=SurveyResponse)
async def save_my_survey(
    session_id: UUID,
    body: SurveyRequest,
    who: ParticipantContext = Depends(require_valid_participant),
    db: AsyncSession = Depends(get_async_session),
) -> SurveyResponse:
    """Save this player's answers, replacing any earlier set."""
    assert who.claims.player_id is not None
    try:
        saved = await survey.save_survey(
            db,
            session_id,
            who.claims.player_id,
            dict(body.answers),
            body.comment,
            _now(),
        )
    except RoundError as error:
        raise _refuse(error)
    return SurveyResponse(answered=True, answers=saved.answers, comment=saved.comment)


@router.post("/{session_id}/host/hand-over", response_model=HandOverResponse)
async def hand_over(
    session_id: UUID,
    body: HandOverRequest,
    claims: JwtClaims = Depends(require_host_control),
    db: AsyncSession = Depends(get_async_session),
) -> HandOverResponse:
    """The host seat (or the operator key) gives the role to another seated
    player. The old host loses host controls at once."""
    outbox = phases.Outbox(session_id)
    async with phases.delivery_lock(session_id):
        try:
            new_host = await host_seat.hand_over(
                db, session_id, body.to_participant_id, _now(), outbox
            )
        except RoundError as error:
            raise _refuse(error)
        await db.commit()
        await outbox.flush(_publisher(session_id))
    return HandOverResponse(host_participant_id=new_host)
