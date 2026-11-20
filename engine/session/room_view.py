"""The room view (AW-331, spec 0095 M1) and who a display address may show.

``room_view`` is the one unsigned read a shared screen rebuilds itself from: the
round's title, phase and time left, whether the game is paused and by whom, the
scene lines, each seated player's flags, whether the game is over, and the
public closing view. It is built from ``phases.round_view`` and
``closing.closing_view`` so it cannot drift from them, and it holds nothing a
player keeps private: no choice, draft, concept, result slot or survey answer,
and no beat or concept ID. Players show only yes-or-no flags.

``display_subject`` is the rule behind M4: a display address names a character
and may return that player's own view only to a sign-in whose seat owns the
character.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from engine.db.orm import Event, SessionParticipant
from engine.db.orm import Session as OrmSession
from engine.session import closing, commit_phase, host_seat, phases, survey
from engine.session.models import SessionStatus
from engine.session.phases import RoundError

_NO_CLOSING = {"not_phased", "no_written_case"}
_OVER = {SessionStatus.completed.value, SessionStatus.abandoned.value}


@dataclass(frozen=True)
class RoomPlayer:
    participant_id: str
    display_name: str | None
    ready: bool
    locked: bool
    answered_survey: bool
    is_host: bool


@dataclass(frozen=True)
class RoomView:
    session_status: str
    round_title: str | None
    phase: str | None
    phase_entry: int | None
    deadline_at: datetime | None
    seconds_left: float | None
    paused: bool
    paused_by: str | None
    lines: tuple[dict[str, Any], ...]
    players: tuple[RoomPlayer, ...]
    ready_count: int
    player_count: int
    over: bool
    closing: dict[str, Any] | None


async def _paused_by(db: AsyncSession, session_id: UUID) -> str | None:
    """The name of the seat that paused the game, if a seat did."""
    result = await db.execute(
        select(Event.payload, Event.timestamp)
        .where(
            Event.session_id == session_id, Event.event_type == "session_interrupted"
        )
        .order_by(Event.timestamp.desc())
    )
    row = result.first()
    if row is None or not row[0].get("paused_by"):
        return None
    return await db.scalar(
        select(SessionParticipant.display_name).where(
            SessionParticipant.session_id == session_id,
            SessionParticipant.participant_id == UUID(str(row[0]["paused_by"])),
        )
    )


async def room_view(db: AsyncSession, session_id: UUID, now: datetime) -> RoomView:
    """What the shared screen needs, public only. Raises ``RoundError`` with
    ``session_not_found`` for an unknown session."""
    round_ = await phases.round_view(db, session_id, now)
    orm = await db.get(OrmSession, session_id)
    if orm is None:
        raise RoundError("session_not_found")

    ready: set[str] = set()
    locked: set[str] = set()
    if round_.phase_entry is not None:
        ready = await phases.ready_ids(db, session_id, round_.phase_entry)
        if round_.phase == "commit":
            locked = await commit_phase.locked_ids(db, session_id, round_.phase_entry)
    answered = await survey.answered_ids(db, session_id)
    host = await host_seat.current_host(db, session_id)

    rows = await db.execute(
        select(SessionParticipant.participant_id, SessionParticipant.display_name)
        .where(SessionParticipant.session_id == session_id)
        .where(
            SessionParticipant.participant_id.in_(
                await phases.human_player_ids(db, session_id)
            )
        )
    )
    seated = sorted(rows.all(), key=lambda r: ((r[1] or "").casefold(), str(r[0])))
    players = tuple(
        RoomPlayer(
            participant_id=str(pid),
            display_name=name,
            ready=str(pid) in ready,
            locked=str(pid) in locked,
            answered_survey=str(pid) in answered,
            is_host=pid == host,
        )
        for pid, name in seated
    )

    public: dict[str, Any] | None
    try:
        view = await closing.closing_view(db, session_id)
        public = {"reveal": view.reveal, "result": view.result, "recap": view.recap}
    except RoundError as error:
        if error.code not in _NO_CLOSING:
            raise
        public = None

    paused = round_.status == "paused" or round_.session_status == (
        SessionStatus.paused.value
    )
    return RoomView(
        session_status=round_.session_status,
        round_title=round_.beat_name,
        phase=round_.phase,
        phase_entry=round_.phase_entry,
        deadline_at=round_.deadline_at,
        seconds_left=round_.seconds_left,
        paused=paused,
        paused_by=await _paused_by(db, session_id) if paused else None,
        lines=round_.lines,
        players=players,
        ready_count=round_.ready_count,
        player_count=round_.player_count,
        over=round_.session_status in _OVER or round_.status == "ended",
        closing=public,
    )


async def display_subject(
    db: AsyncSession,
    session_id: UUID,
    *,
    character_id: UUID | None,
    signed_in: bool,
    participant_id: UUID | None,
) -> UUID | None:
    """The character a display address may personalise for, or None for the
    shared view.

    No character named, or no sign-in at all, is the shared view. A sign-in that
    names a character must be the seat that owns it; any other sign-in (another
    player, a host token, a display token) is refused with ``not_your_character``.
    """
    if character_id is None or not signed_in:
        return None
    if participant_id is not None:
        owned = await db.scalar(
            select(SessionParticipant.character_id).where(
                SessionParticipant.session_id == session_id,
                SessionParticipant.participant_id == participant_id,
            )
        )
        if owned == character_id:
            return character_id
    raise RoundError(
        "not_your_character", "that view belongs to another player's sign-in"
    )
