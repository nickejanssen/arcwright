"""Rounds that move by rule (spec 0093, Part C).

A beat may be divided into ordered phases (``scene``, ``choices``,
``mini_game``, ``bridge``). This module moves a session from phase to phase,
and from the last phase to the next beat, by rule only:

  - every player has marked ready (scene, choices, bridge),
  - the authored time is up,
  - the host moves on,
  - the mini-game ends (the stand-in call here; AW-303 connects the real run).

Typed input and model calls never decide when a round moves on.

State is saved, not held in memory, so a restart loses nothing: each change of
phase is one ``events`` row (``phase_state``) carrying a counter, and the
newest counter is the current state. Readiness is a ``decisions`` row. All
changes to one session run under one lock (an in-process lock plus a row lock
on Postgres), and every change re-reads saved state first, so a second call at
the same moment finds nothing left to do.
"""

from __future__ import annotations

import asyncio
import logging
import weakref
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Literal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from engine.arc.models import ArcDefinition, BeatDefinition, PhaseDefinition, PhaseKind
from engine.arc.registry import load_arc_definition
from engine.db.orm import Decision, Event, SessionParticipant
from engine.db.orm import Session as OrmSession
from engine.events.models import (
    AudienceTarget,
    ContentEvent,
    EventCategory,
    PresentationHints,
)
from engine.session.models import SessionStatus

logger = logging.getLogger(__name__)

PHASE_EVENT = "phase_state"
READY_DECISION = "ready"
PHASE_CHANGED_EVENT = "phase_changed"
PHASE_LINE_EVENT = "phase_line"

Publish = Callable[[ContentEvent], Awaitable[Any]] | None
Status = Literal["running", "paused", "ended"]

_READY_PHASES = frozenset({PhaseKind.scene, PhaseKind.choices, PhaseKind.bridge})
_PUBLIC_AUDIENCES = frozenset({AudienceTarget.all, AudienceTarget.shared_display})
_MAX_STEPS = 8


class RoundError(Exception):
    """A request the rules refuse. ``code`` is stable; routes map it to a status."""

    def __init__(self, code: str, message: str | None = None) -> None:
        super().__init__(message or code)
        self.code = code


@dataclass(frozen=True)
class PhaseState:
    seq: int
    status: Status
    beat_id: str
    phase_index: int
    phase: str
    deadline_at: datetime | None
    remaining_seconds: float | None
    reason: str | None


@dataclass(frozen=True)
class RoundView:
    """What a screen needs to rebuild itself after a reconnect. No choice
    content, and no private information, is ever in here."""

    session_status: str
    beat_id: str
    beat_name: str | None
    phase: str | None
    phase_index: int | None
    status: Status | None
    deadline_at: datetime | None
    seconds_left: float | None
    ready_count: int
    player_count: int
    lines: tuple[dict[str, Any], ...]


# --- locking --------------------------------------------------------------------

_LOCKS: weakref.WeakValueDictionary[tuple[int, UUID], asyncio.Lock] = (
    weakref.WeakValueDictionary()
)


@asynccontextmanager
async def session_lock(
    db: AsyncSession, session_id: UUID
) -> AsyncIterator[OrmSession | None]:
    """One writer at a time per session.

    The in-process lock covers one API process and SQLite tests. The row lock
    (``FOR UPDATE``, ignored by SQLite) covers two connections on Postgres. It
    is held until the caller's transaction ends. Yields the session row, freshly
    read, or None when there is no such session.
    """
    key = (id(asyncio.get_running_loop()), session_id)
    lock = _LOCKS.get(key)
    if lock is None:
        lock = asyncio.Lock()
        _LOCKS[key] = lock
    async with lock:
        result = await db.execute(
            select(OrmSession)
            .where(OrmSession.session_id == session_id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        yield result.scalars().first()


# --- reading saved state --------------------------------------------------------


def _parse_time(raw: str | None) -> datetime | None:
    if raw is None:
        return None
    parsed = datetime.fromisoformat(raw)
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def _state_from(payload: dict[str, Any]) -> PhaseState:
    return PhaseState(
        seq=int(payload["seq"]),
        status=payload["status"],
        beat_id=payload["beat_id"],
        phase_index=int(payload["phase_index"]),
        phase=payload["phase"],
        deadline_at=_parse_time(payload.get("deadline_at")),
        remaining_seconds=payload.get("remaining_seconds"),
        reason=payload.get("reason"),
    )


async def current_phase(db: AsyncSession, session_id: UUID) -> PhaseState | None:
    """The newest saved phase state, or None if the session has none yet."""
    result = await db.execute(
        select(Event.payload).where(
            Event.session_id == session_id, Event.event_type == PHASE_EVENT
        )
    )
    payloads = list(result.scalars().all())
    if not payloads:
        return None
    return _state_from(max(payloads, key=lambda p: int(p["seq"])))


async def _save(
    db: AsyncSession,
    session_id: UUID,
    previous: PhaseState | None,
    now: datetime,
    *,
    status: Status,
    beat_id: str,
    phase_index: int,
    phase: str,
    deadline_at: datetime | None = None,
    remaining_seconds: float | None = None,
    reason: str | None = None,
) -> PhaseState:
    payload: dict[str, Any] = {
        "seq": (previous.seq + 1) if previous else 1,
        "status": status,
        "beat_id": beat_id,
        "phase_index": phase_index,
        "phase": phase,
        "deadline_at": deadline_at.isoformat() if deadline_at else None,
        "remaining_seconds": remaining_seconds,
        "reason": reason,
    }
    db.add(
        Event(
            session_id=session_id,
            timestamp=now,
            event_type=PHASE_EVENT,
            payload=payload,
        )
    )
    await db.flush()
    return _state_from(payload)


# --- participants and readiness -------------------------------------------------


async def human_player_ids(db: AsyncSession, session_id: UUID) -> list[UUID]:
    """The participants a round waits for: not the host, not an AI seat."""
    result = await db.execute(
        select(SessionParticipant.participant_id).where(
            SessionParticipant.session_id == session_id,
            SessionParticipant.surface_type != "host",
            SessionParticipant.is_ai_controlled.is_(False),
        )
    )
    return list(result.scalars().all())


async def _ready_ids(db: AsyncSession, session_id: UUID, phase_seq: int) -> set[str]:
    result = await db.execute(
        select(Decision.context).where(
            Decision.session_id == session_id,
            Decision.decision_type == READY_DECISION,
        )
    )
    return {
        str(ctx["participant_id"])
        for ctx in result.scalars().all()
        if ctx.get("phase_seq") == phase_seq
    }


async def _everyone_ready(
    db: AsyncSession, session_id: UUID, state: PhaseState
) -> bool:
    humans = {str(pid) for pid in await human_player_ids(db, session_id)}
    if not humans:
        return False
    return humans <= await _ready_ids(db, session_id, state.seq)


# --- publishing -----------------------------------------------------------------


async def emit(publish: Publish, event: ContentEvent) -> None:
    if publish is not None:
        await publish(event)


def content_event(
    session_id: UUID,
    now: datetime,
    *,
    category: EventCategory,
    event_type: str,
    audience: AudienceTarget,
    payload: dict[str, Any],
    target_player_id: UUID | None = None,
    hints: PresentationHints | None = None,
) -> ContentEvent:
    return ContentEvent(
        session_id=session_id,
        timestamp=now,
        category=category,
        event_type=event_type,
        target_audience=audience,
        target_player_id=target_player_id,
        payload=payload,
        presentation_hints=hints or PresentationHints(),
    )


# --- the rules ------------------------------------------------------------------


def _beat(arc: ArcDefinition, beat_id: str) -> BeatDefinition:
    for beat in arc.beats:
        if beat.beat_id == beat_id:
            return beat
    raise RoundError("unknown_beat", f"unknown beat {beat_id!r}")


def _phases(beat: BeatDefinition) -> list[PhaseDefinition]:
    if not beat.phases:
        raise RoundError("not_phased", f"beat {beat.beat_id!r} has no phases")
    return beat.phases


async def _enter(
    db: AsyncSession,
    session_id: UUID,
    arc: ArcDefinition,
    previous: PhaseState | None,
    beat_id: str,
    index: int,
    now: datetime,
    publish: Publish,
) -> PhaseState:
    definition = _phases(_beat(arc, beat_id))[index]
    state = await _save(
        db,
        session_id,
        previous,
        now,
        status="running",
        beat_id=beat_id,
        phase_index=index,
        phase=definition.kind.value,
        deadline_at=now + timedelta(seconds=definition.seconds),
    )
    await emit(
        publish,
        content_event(
            session_id,
            now,
            category=EventCategory.state_transition,
            event_type=PHASE_CHANGED_EVENT,
            audience=AudienceTarget.all,
            payload={
                "beat_id": beat_id,
                "phase": definition.kind.value,
                "phase_index": index,
                "seconds": definition.seconds,
                "deadline_at": state.deadline_at.isoformat()
                if state.deadline_at
                else None,
            },
        ),
    )
    for line_index, line in enumerate(definition.lines):
        await emit(
            publish,
            content_event(
                session_id,
                now,
                category=EventCategory.narrative,
                event_type=PHASE_LINE_EVENT,
                audience=definition.audience,
                payload={
                    "beat_id": beat_id,
                    "phase": definition.kind.value,
                    "line_index": line_index,
                    "line_count": len(definition.lines),
                    "text": line.text,
                    "speaker": line.speaker,
                },
                hints=line.hints,
            ),
        )
    return state


async def _advance_beat(
    db: AsyncSession,
    orm: OrmSession,
    arc: ArcDefinition,
    state: PhaseState,
    now: datetime,
    publish: Publish,
) -> PhaseState | None:
    """Move to the next beat, then read the session back to see whether it
    moved: a guarded transition that is refused is ignored, not raised. Returns
    the first phase of the new beat, or None when the session stayed where it
    was (the final beat, or an exit condition that is not met)."""
    from engine.session.service import _session_service

    left = orm.current_beat_id
    await _session_service.advance_live_session_on_input(
        db,
        orm.session_id,
        player_action_count=max(1, await _count_choices(db, orm.session_id, left)),
        by_rule=True,
    )
    await db.refresh(orm)
    if orm.current_beat_id == left:
        return None
    return await _enter(
        db, orm.session_id, arc, state, orm.current_beat_id, 0, now, publish
    )


async def _count_choices(db: AsyncSession, session_id: UUID, beat_id: str) -> int:
    result = await db.execute(
        select(Decision.context).where(
            Decision.session_id == session_id, Decision.decision_type == "choice"
        )
    )
    return sum(1 for ctx in result.scalars().all() if ctx.get("beat_id") == beat_id)


async def _end(
    db: AsyncSession,
    orm: OrmSession,
    arc: ArcDefinition,
    state: PhaseState,
    reason: str,
    now: datetime,
    publish: Publish,
) -> PhaseState:
    ended = await _save(
        db,
        orm.session_id,
        state,
        now,
        status="ended",
        beat_id=state.beat_id,
        phase_index=state.phase_index,
        phase=state.phase,
        reason=reason,
    )
    phases = _phases(_beat(arc, state.beat_id))
    if state.phase_index + 1 < len(phases):
        return await _enter(
            db,
            orm.session_id,
            arc,
            ended,
            state.beat_id,
            state.phase_index + 1,
            now,
            publish,
        )
    return await _advance_beat(db, orm, arc, ended, now, publish) or ended


async def _due_reason(
    db: AsyncSession, session_id: UUID, state: PhaseState, now: datetime
) -> str | None:
    if PhaseKind(state.phase) in _READY_PHASES and await _everyone_ready(
        db, session_id, state
    ):
        return "ready"
    if state.deadline_at is not None and now >= state.deadline_at:
        return "time"
    return None


async def _settle(
    db: AsyncSession,
    orm: OrmSession,
    arc: ArcDefinition,
    now: datetime,
    publish: Publish,
) -> list[str]:
    """Apply everything that is due, re-reading saved state before each change.

    Each phase entered has a deadline in the future, so this stops after at
    most one phase per call plus any beat change; a late tick never skips a
    phase. Returns what changed (empty when nothing was due).
    """
    changes: list[str] = []
    for _ in range(_MAX_STEPS):
        state = await current_phase(db, orm.session_id)
        if state is None:
            await _enter(
                db, orm.session_id, arc, None, orm.current_beat_id, 0, now, publish
            )
            changes.append("entered")
            continue
        if state.status == "paused":
            break
        if state.status == "running":
            reason = await _due_reason(db, orm.session_id, state, now)
            if reason is None:
                break
            await _end(db, orm, arc, state, reason, now, publish)
            changes.append(f"ended:{reason}")
            continue
        # "ended" is saved only for the last phase of a beat that could not move
        # on: the final beat, or an exit condition that is not met yet.
        if await _advance_beat(db, orm, arc, state, now, publish) is None:
            break
        changes.append("beat_advanced")
    return changes


def _require_active_phased(orm: OrmSession | None) -> tuple[OrmSession, ArcDefinition]:
    if orm is None:
        raise RoundError("session_not_found")
    if orm.status != SessionStatus.active.value:
        raise RoundError("session_not_active", f"session is {orm.status}")
    arc = load_arc_definition(orm.arc_id)
    if arc is None or not arc.is_phased:
        raise RoundError("not_phased", "this game does not run by phases")
    return orm, arc


# --- public engine functions ----------------------------------------------------


async def tick(
    db: AsyncSession, session_id: UUID, now: datetime, publish: Publish = None
) -> list[str]:
    """Apply every deadline that is due for ``session_id`` at ``now``.

    Safe to call twice: the second call finds nothing due and changes nothing.
    A session that is not active, or whose arc has no phases, is left alone. A
    phased session with no saved phase yet enters its first phase.
    """
    async with session_lock(db, session_id) as orm:
        if orm is None or orm.status != SessionStatus.active.value:
            return []
        arc = load_arc_definition(orm.arc_id)
        if arc is None or not arc.is_phased:
            return []
        return await _settle(db, orm, arc, now, publish)


async def mark_ready(
    db: AsyncSession,
    session_id: UUID,
    participant_id: UUID,
    now: datetime,
    publish: Publish = None,
) -> PhaseState:
    """A player says they are done with this phase. Ends it when every player
    has. Marking twice saves once."""
    async with session_lock(db, session_id) as locked:
        orm, arc = _require_active_phased(locked)
        if participant_id not in await human_player_ids(db, session_id):
            raise RoundError("not_a_participant")
        state = await current_phase(db, session_id)
        if state is None or state.status != "running":
            raise RoundError("phase_not_running")
        if PhaseKind(state.phase) not in _READY_PHASES:
            raise RoundError("phase_not_ready_able", f"{state.phase} ends on its own")
        if str(participant_id) not in await _ready_ids(db, session_id, state.seq):
            db.add(
                Decision(
                    session_id=session_id,
                    timestamp=now,
                    decision_type=READY_DECISION,
                    context={
                        "participant_id": str(participant_id),
                        "beat_id": state.beat_id,
                        "phase": state.phase,
                        "phase_seq": state.seq,
                    },
                    outcome={},
                )
            )
            await db.flush()
        await _settle(db, orm, arc, now, publish)
        newest = await current_phase(db, session_id)
        assert newest is not None
        return newest


async def host_move_on(
    db: AsyncSession, session_id: UUID, now: datetime, publish: Publish = None
) -> PhaseState:
    """The host ends the current phase by hand: the safety valve for a live room."""
    async with session_lock(db, session_id) as locked:
        orm, arc = _require_active_phased(locked)
        state = await current_phase(db, session_id)
        if state is None:
            raise RoundError("phase_not_running")
        if state.status == "running":
            await _end(db, orm, arc, state, "host", now, publish)
        elif state.status == "ended":
            await _advance_beat(db, orm, arc, state, now, publish)
        newest = await current_phase(db, session_id)
        assert newest is not None
        return newest


async def finish_mini_game_phase(
    db: AsyncSession, session_id: UUID, now: datetime, publish: Publish = None
) -> bool:
    """The mini-game has reached an end state: end its phase and go on.

    The stand-in for AW-303, which calls this when a real run completes, times
    out, or is resolved or cancelled by the host. Returns False, changing
    nothing, when the session is not in a running mini-game phase (a repeated
    or late call).
    """
    async with session_lock(db, session_id) as orm:
        if orm is None or orm.status != SessionStatus.active.value:
            return False
        arc = load_arc_definition(orm.arc_id)
        if arc is None or not arc.is_phased:
            return False
        state = await current_phase(db, session_id)
        if (
            state is None
            or state.status != "running"
            or state.phase != PhaseKind.mini_game.value
        ):
            return False
        await _end(db, orm, arc, state, "mini_game_ended", now, publish)
        return True


async def freeze_phase(db: AsyncSession, session_id: UUID, now: datetime) -> None:
    """Pause: keep the time that was left, and stop the clock."""
    async with session_lock(db, session_id):
        state = await current_phase(db, session_id)
        if state is None or state.status != "running" or state.deadline_at is None:
            return
        await _save(
            db,
            session_id,
            state,
            now,
            status="paused",
            beat_id=state.beat_id,
            phase_index=state.phase_index,
            phase=state.phase,
            remaining_seconds=max(0.0, (state.deadline_at - now).total_seconds()),
        )


async def thaw_phase(db: AsyncSession, session_id: UUID, now: datetime) -> None:
    """Resume: the clock restarts with the time that was left."""
    async with session_lock(db, session_id):
        state = await current_phase(db, session_id)
        if state is None or state.status != "paused":
            return
        await _save(
            db,
            session_id,
            state,
            now,
            status="running",
            beat_id=state.beat_id,
            phase_index=state.phase_index,
            phase=state.phase,
            deadline_at=now + timedelta(seconds=state.remaining_seconds or 0.0),
        )


def _beat_name(arc: ArcDefinition | None, beat_id: str) -> str | None:
    if arc is None:
        return None
    return next((b.beat_name for b in arc.beats if b.beat_id == beat_id), None)


async def round_view(db: AsyncSession, session_id: UUID, now: datetime) -> RoundView:
    """The current beat, phase and deadline, for a screen rebuilding itself."""
    orm = await db.get(OrmSession, session_id)
    if orm is None:
        raise RoundError("session_not_found")
    await db.refresh(orm)
    humans = await human_player_ids(db, session_id)
    state = await current_phase(db, session_id)
    arc = load_arc_definition(orm.arc_id)
    if state is None:
        return RoundView(
            session_status=orm.status,
            beat_id=orm.current_beat_id,
            beat_name=_beat_name(arc, orm.current_beat_id),
            phase=None,
            phase_index=None,
            status=None,
            deadline_at=None,
            seconds_left=None,
            ready_count=0,
            player_count=len(humans),
            lines=(),
        )
    seconds_left: float | None = None
    if state.status == "running" and state.deadline_at is not None:
        seconds_left = max(0.0, (state.deadline_at - now).total_seconds())
    elif state.status == "paused":
        seconds_left = state.remaining_seconds
    lines: tuple[dict[str, Any], ...] = ()
    if arc is not None and arc.is_phased:
        definition = _phases(_beat(arc, state.beat_id))[state.phase_index]
        if definition.audience in _PUBLIC_AUDIENCES:
            lines = tuple(
                {
                    "text": line.text,
                    "speaker": line.speaker,
                    "hints": line.hints.model_dump(),
                }
                for line in definition.lines
            )
    ready = await _ready_ids(db, session_id, state.seq)
    return RoundView(
        session_status=orm.status,
        beat_id=state.beat_id,
        beat_name=_beat_name(arc, state.beat_id),
        phase=state.phase,
        phase_index=state.phase_index,
        status=state.status,
        deadline_at=state.deadline_at,
        seconds_left=seconds_left,
        ready_count=len({str(p) for p in humans} & ready),
        player_count=len(humans),
        lines=lines,
    )


async def tick_active_sessions(
    factory: async_sessionmaker[AsyncSession],
    now: datetime,
    publisher_for: Callable[[UUID], Publish],
) -> int:
    """One pass of the API's once-a-second loop: tick every active session whose
    arc has phases, each in its own transaction. Returns how many were ticked.
    One session failing is logged and does not stop the others."""
    async with factory() as db:
        result = await db.execute(
            select(OrmSession.session_id, OrmSession.arc_id).where(
                OrmSession.status == SessionStatus.active.value
            )
        )
        active = list(result.all())
    ticked = 0
    for session_id, arc_id in active:
        arc = load_arc_definition(arc_id)
        if arc is None or not arc.is_phased:
            continue
        async with factory() as db:
            try:
                await tick(db, session_id, now, publisher_for(session_id))
                await db.commit()
            except Exception:
                await db.rollback()
                logger.exception("tick failed for session %s", session_id)
                continue
        ticked += 1
    return ticked
