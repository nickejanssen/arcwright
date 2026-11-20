"""Rounds that move by rule (spec 0093, Part C).

A beat may be divided into ordered phases (``scene``, ``choices``,
``mini_game``, ``bridge``). This module moves a session from phase to phase,
and from the last phase to the next beat, by rule only:

  - every player has marked ready (scene, choices, bridge),
  - the authored time is up,
  - the host moves on,
  - the mini-game's run ends, or the phase's time limit passes (see
    ``engine.session.mini_game_phase``).

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
from collections import deque
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Literal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from engine.arc.models import (
    ArcDefinition,
    BeatDefinition,
    PhaseDefinition,
    PhaseKind,
    PhaseLine,
)
from engine.arc.registry import load_arc_definition
from engine.case.authored import AuthoredCase
from engine.db.orm import Decision, Event, SessionParticipant
from engine.db.orm import Session as OrmSession
from engine.events.models import (
    AudienceTarget,
    ContentEvent,
    EventCategory,
    PresentationHints,
)
from engine.session import commit_phase, mini_game_phase
from engine.session.case_seating import cached_arc_case
from engine.session.models import SessionStatus

logger = logging.getLogger(__name__)

PHASE_EVENT = "phase_state"
READY_DECISION = "ready"
PHASE_CHANGED_EVENT = "phase_changed"
PHASE_LINE_EVENT = "phase_line"

Publish = Callable[[ContentEvent], Awaitable[Any]] | None
"""Where engine functions send events. They publish as they go, inside the
caller's open transaction, so a caller that commits afterwards must pass an
``Outbox`` and flush it after the commit (AW-338). A plain publisher gets each
event at once, which is only safe where nothing can fail after the call."""
Status = Literal["running", "paused", "ended"]

_READY_PHASES = frozenset(
    {
        PhaseKind.scene,
        PhaseKind.choices,
        PhaseKind.bridge,
        PhaseKind.reveal,
        PhaseKind.result,
        PhaseKind.recap,
    }
)
_CLOSING_PHASES = frozenset({PhaseKind.reveal, PhaseKind.result, PhaseKind.recap})
_PUBLIC_AUDIENCES = frozenset({AudienceTarget.all, AudienceTarget.shared_display})
_MAX_STEPS = 8


MAX_PUBLISH_ATTEMPTS = 10
_PENDING: dict[UUID, deque[list[Any]]] = {}
_DELIVERY_LOCKS: weakref.WeakValueDictionary[tuple[int, UUID], asyncio.Lock] = (
    weakref.WeakValueDictionary()
)


@asynccontextmanager
async def delivery_lock(session_id: UUID) -> AsyncIterator[None]:
    """One change-and-delivery at a time per session.

    Take it before calling an engine function, and release it after the commit
    and the flush. The database lock ends at commit, so without this a later
    change could commit and publish while an earlier one is between its commit
    and its flush, and screens would see the phases out of order. Taken before
    ``session_lock``, never inside it. In-process only, like ``session_lock``.
    """
    key = (id(asyncio.get_running_loop()), session_id)
    lock = _DELIVERY_LOCKS.get(key)
    if lock is None:
        lock = asyncio.Lock()
        _DELIVERY_LOCKS[key] = lock
    async with lock:
        yield


async def drain_pending(session_id: UUID, publish: Publish) -> None:
    """Send the session's saved-but-unsent events, oldest first. Call it with
    the delivery lock held.

    An event that fails stays at the front with everything behind it, so order
    is kept and the next call retries it: the tick loop calls this every pass.
    After ``MAX_PUBLISH_ATTEMPTS`` failures it is dropped and logged as an
    error, so one bad event cannot block the session for good."""
    queue = _PENDING.get(session_id)
    if queue is None or publish is None:
        return
    while queue:
        item = queue[0]
        event: ContentEvent = item[0]
        try:
            await publish(event)
        except Exception:
            item[1] += 1
            if item[1] < MAX_PUBLISH_ATTEMPTS:
                logger.warning(
                    "publishing %s for session %s failed (attempt %d); will retry",
                    event.event_type,
                    session_id,
                    item[1],
                    exc_info=True,
                )
                return
            logger.error(
                "dropping %s for session %s after %d failed attempts",
                event.event_type,
                session_id,
                item[1],
                exc_info=True,
            )
        queue.popleft()
    del _PENDING[session_id]


class Outbox:
    """Holds a session's events until the caller's transaction has committed.

    Pass it as ``publish``; hold ``delivery_lock`` around the engine call, the
    commit and ``flush``. After a successful commit ``flush`` queues the events
    behind any still waiting from an earlier failure and sends them in order. A
    rollback calls ``discard``, so a rolled-back change tells nobody anything
    and the next tick sends its lines exactly once. A send that fails is kept
    and retried (see ``drain_pending``) rather than lost.
    """

    def __init__(self, session_id: UUID) -> None:
        self._session_id = session_id
        self._held: list[ContentEvent] = []

    async def __call__(self, event: ContentEvent) -> ContentEvent:
        self._held.append(event)
        return event

    def __len__(self) -> int:
        return len(self._held)

    def discard(self) -> None:
        self._held.clear()

    async def flush(self, publish: Publish) -> None:
        held, self._held = self._held, []
        if publish is not None and held:
            queue = _PENDING.setdefault(self._session_id, deque())
            queue.extend([event, 0] for event in held)
        await drain_pending(self._session_id, publish)


class RoundError(Exception):
    """A request the rules refuse. ``code`` is stable; routes map it to a status."""

    def __init__(self, code: str, message: str | None = None) -> None:
        super().__init__(message or code)
        self.code = code


@dataclass(frozen=True)
class PhaseState:
    seq: int
    entry: int
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
    phase_entry: int | None
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
        entry=int(payload["entry"]),
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
    payloads: list[dict[str, Any]] = list(result.scalars().all())
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
    new_entry: bool = False,
) -> PhaseState:
    """Save the next state. ``entry`` names one visit to a phase: a new
    visit (``new_entry``) takes the next number; ending, pausing and resuming
    the same visit carry it forward, so readiness survives a pause and a late
    request can tell which visit it was meant for."""
    if previous is None:
        entry = 1
    else:
        entry = previous.entry + 1 if new_entry else previous.entry
    payload: dict[str, Any] = {
        "seq": (previous.seq + 1) if previous else 1,
        "entry": entry,
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


async def _ready_ids(db: AsyncSession, session_id: UUID, phase_entry: int) -> set[str]:
    result = await db.execute(
        select(Decision.context).where(
            Decision.session_id == session_id,
            Decision.decision_type == READY_DECISION,
        )
    )
    contexts: list[dict[str, Any]] = list(result.scalars().all())
    return {
        str(ctx["participant_id"])
        for ctx in contexts
        if ctx.get("phase_entry") == phase_entry
    }


async def ready_ids(db: AsyncSession, session_id: UUID, phase_entry: int) -> set[str]:
    """Who has marked ready in this visit to a phase, for a read that is not
    part of the rounds code (the room view)."""
    return await _ready_ids(db, session_id, phase_entry)


async def _everyone_ready(
    db: AsyncSession, session_id: UUID, state: PhaseState
) -> bool:
    humans = {str(pid) for pid in await human_player_ids(db, session_id)}
    if not humans:
        return False
    return humans <= await _ready_ids(db, session_id, state.entry)


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


def _mini_game_slot(beat: BeatDefinition, index: int) -> int:
    """Which mini-game slot of the beat the phase at ``index`` is, from 0."""
    return sum(1 for p in _phases(beat)[:index] if p.kind is PhaseKind.mini_game)


async def _enter(
    db: AsyncSession,
    orm: OrmSession,
    arc: ArcDefinition,
    previous: PhaseState | None,
    beat_id: str,
    index: int,
    now: datetime,
    publish: Publish,
) -> PhaseState:
    session_id = orm.session_id
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
        new_entry=True,
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
                "phase_entry": state.entry,
                "seconds": definition.seconds,
                "deadline_at": state.deadline_at.isoformat()
                if state.deadline_at
                else None,
            },
        ),
    )
    lines = phase_lines(arc, definition)
    for line_index, line in enumerate(lines):
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
                    "line_count": len(lines),
                    "text": line.text,
                    "speaker": line.speaker,
                },
                hints=line.hints,
            ),
        )
    if definition.kind is PhaseKind.commit:
        await _begin_commit(db, orm, arc)
    if definition.kind in _CLOSING_PHASES:
        from engine.session import closing

        await closing.enter(
            db, arc, session_id, definition.kind, state, now, publish, index
        )
    if definition.kind is PhaseKind.mini_game:
        ending = await mini_game_phase.begin(
            db,
            orm,
            arc,
            beat_id,
            state.entry,
            now,
            publish,
            slot=_mini_game_slot(_beat(arc, beat_id), index),
            player_count=len(await human_player_ids(db, session_id)),
        )
        if ending is not None:
            return await _end(db, orm, arc, state, ending, now, publish)
    return state


def _commit_case(arc: ArcDefinition) -> AuthoredCase:
    case = cached_arc_case(arc)
    if case is None:
        raise RoundError("no_written_case", "this game has no written case")
    return case


def phase_lines(arc: ArcDefinition, definition: PhaseDefinition) -> list[PhaseLine]:
    """The written lines of a phase: its own, or for a scene that says so, the
    case's written ``closing``."""
    if definition.source == "case_closing":
        return [PhaseLine(text=text) for text in _commit_case(arc).closing if text]
    return definition.lines


async def _begin_commit(db: AsyncSession, orm: OrmSession, arc: ArcDefinition) -> None:
    await commit_phase.begin(
        db,
        orm.session_id,
        _commit_case(arc),
        await human_player_ids(db, orm.session_id),
    )


async def _close_commit(
    db: AsyncSession,
    orm: OrmSession,
    arc: ArcDefinition,
    state: PhaseState,
    now: datetime,
    publish: Publish,
) -> None:
    await commit_phase.close(
        db,
        orm.session_id,
        _commit_case(arc),
        entry=state.entry,
        beat_id=state.beat_id,
        humans=await human_player_ids(db, orm.session_id),
        now=now,
        publish=publish,
    )


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
    return await _enter(db, orm, arc, state, orm.current_beat_id, 0, now, publish)


async def _count_choices(db: AsyncSession, session_id: UUID, beat_id: str) -> int:
    result = await db.execute(
        select(Decision.context).where(
            Decision.session_id == session_id, Decision.decision_type == "choice"
        )
    )
    contexts: list[dict[str, Any]] = list(result.scalars().all())
    return len([ctx for ctx in contexts if ctx.get("beat_id") == beat_id])


async def _end(
    db: AsyncSession,
    orm: OrmSession,
    arc: ArcDefinition,
    state: PhaseState,
    reason: str,
    now: datetime,
    publish: Publish,
) -> PhaseState:
    if state.phase == PhaseKind.mini_game.value:
        await mini_game_phase.stop_open_run(
            db, orm.session_id, state.beat_id, state.entry, now, publish
        )
    if state.phase == PhaseKind.commit.value:
        await _close_commit(db, orm, arc, state, now, publish)
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
            orm,
            arc,
            ended,
            state.beat_id,
            state.phase_index + 1,
            now,
            publish,
        )
    return await _advance_beat(db, orm, arc, ended, now, publish) or ended


async def _due_reason(
    db: AsyncSession,
    session_id: UUID,
    state: PhaseState,
    now: datetime,
    publish: Publish,
) -> str | None:
    if state.phase == PhaseKind.mini_game.value:
        return await mini_game_phase.advance(
            db,
            session_id,
            state.beat_id,
            state.entry,
            state.deadline_at,
            now,
            publish,
        )
    if state.phase == PhaseKind.commit.value and await commit_phase.everyone_locked(
        db, session_id, state.entry, await human_player_ids(db, session_id)
    ):
        return "locked"
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
            await _enter(db, orm, arc, None, orm.current_beat_id, 0, now, publish)
            changes.append("entered")
            continue
        if state.status == "paused":
            break
        if state.status == "running":
            reason = await _due_reason(db, orm.session_id, state, now, publish)
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
    phase_entry: int | None = None,
) -> PhaseState:
    """A player says they are done with this phase. Ends it when every player
    has. Marking twice saves once.

    ``phase_entry`` is the visit the player saw (from the round view). If the
    round has since moved on, the request is stale: nothing is saved and the
    current state comes back, so a retry or a late tap cannot mark the player
    ready for a phase they never saw. ``None`` means "the current one", for
    callers inside the engine."""
    async with session_lock(db, session_id) as locked:
        orm, arc = _require_active_phased(locked)
        if participant_id not in await human_player_ids(db, session_id):
            raise RoundError("not_a_participant")
        state = await current_phase(db, session_id)
        if state is None or state.status != "running":
            raise RoundError("phase_not_running")
        if phase_entry is not None and phase_entry != state.entry:
            return state
        if PhaseKind(state.phase) not in _READY_PHASES:
            raise RoundError("phase_not_ready_able", f"{state.phase} ends on its own")
        if str(participant_id) not in await _ready_ids(db, session_id, state.entry):
            db.add(
                Decision(
                    session_id=session_id,
                    timestamp=now,
                    decision_type=READY_DECISION,
                    context={
                        "participant_id": str(participant_id),
                        "beat_id": state.beat_id,
                        "phase": state.phase,
                        "phase_entry": state.entry,
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
    """The mini-game's run has reached an end state: end its phase and go on.

    For a caller outside the tick (the tick reaches the same rule from inside
    the lock it already holds). Returns False, changing nothing, when the
    session is not in a running mini-game phase, or its run is not over (a
    repeated, late or early call).

    It publishes inside the caller's open transaction. There is no production
    caller yet; any caller must run under ``delivery_lock`` with an ``Outbox``
    as ``publish``, commit, and then flush it, as the round routes do.
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
        if not await mini_game_phase.run_is_over(
            db, session_id, state.beat_id, state.entry
        ):
            return False
        await _end(db, orm, arc, state, mini_game_phase.ENDED, now, publish)
        return True


def _commit_refusal(refusal: commit_phase.CommitRefusal) -> RoundError:
    return RoundError(refusal.code, str(refusal))


async def _commit_visit(
    db: AsyncSession,
    session_id: UUID,
    participant_id: UUID,
    now: datetime,
    *,
    editing: bool,
) -> PhaseState:
    """The running commit phase this player may change, or a refusal."""
    if participant_id not in await human_player_ids(db, session_id):
        raise RoundError("not_a_participant")
    state = await current_phase(db, session_id)
    if state is None or state.phase != PhaseKind.commit.value:
        raise RoundError("not_in_commit_phase")
    if editing:
        if state.status != "running":
            raise RoundError("phase_not_running")
        if state.deadline_at is not None and now >= state.deadline_at:
            raise RoundError("phase_time_up", "the time for this phase is up")
    return state


async def read_theory_form(
    db: AsyncSession, session_id: UUID, participant_id: UUID, now: datetime
) -> commit_phase.TheoryForm:
    """This player's theory form: the slots, what they may pick, the account
    text, their own saved draft or lock, and the time left. Private to them. It
    never says whether anything is right."""
    async with session_lock(db, session_id) as orm:
        if orm is None:
            raise RoundError("session_not_found")
        if participant_id not in await human_player_ids(db, session_id):
            raise RoundError("not_a_participant")
        arc = load_arc_definition(orm.arc_id)
        if arc is None or not arc.is_phased:
            raise RoundError("not_phased", "this game does not run by phases")
        state = await current_phase(db, session_id)
        building = (
            state is not None
            and state.phase == PhaseKind.commit.value
            and state.status in ("running", "paused")
        )
        seconds_left: float | None = None
        deadline: datetime | None = None
        open_now = False
        if state is not None and building:
            if state.status == "running" and state.deadline_at is not None:
                deadline = state.deadline_at
                seconds_left = max(0.0, (deadline - now).total_seconds())
                open_now = seconds_left > 0
            elif state.status == "paused":
                seconds_left = state.remaining_seconds
        try:
            return await commit_phase.read_form(
                db,
                session_id,
                _commit_case(arc),
                participant_id,
                entry=state.entry if state is not None and building else None,
                open_now=open_now,
                deadline_at=deadline,
                seconds_left=seconds_left,
            )
        except commit_phase.CommitRefusal as refusal:
            raise _commit_refusal(refusal) from refusal


async def save_theory_draft(
    db: AsyncSession,
    session_id: UUID,
    participant_id: UUID,
    answers: dict[str, str],
    proof: str | None,
    now: datetime,
    publish: Publish = None,
) -> commit_phase.Theory:
    """Replace this player's draft. The draft goes to this player only."""
    async with session_lock(db, session_id) as locked:
        orm, arc = _require_active_phased(locked)
        state = await _commit_visit(db, session_id, participant_id, now, editing=True)
        try:
            return await commit_phase.save_draft(
                db,
                session_id,
                _commit_case(arc),
                participant_id,
                entry=state.entry,
                beat_id=state.beat_id,
                answers=answers,
                proof=proof,
                now=now,
                publish=publish,
            )
        except commit_phase.CommitRefusal as refusal:
            raise _commit_refusal(refusal) from refusal


async def lock_theory(
    db: AsyncSession,
    session_id: UUID,
    participant_id: UUID,
    now: datetime,
    publish: Publish = None,
) -> commit_phase.Theory:
    """Lock this player's saved draft. When that makes everyone locked, the
    phase ends in the same call. Publishes inside the caller's transaction, so
    run it under ``delivery_lock`` with an ``Outbox``, as the round routes do."""
    async with session_lock(db, session_id) as locked:
        orm, arc = _require_active_phased(locked)
        state = await _commit_visit(db, session_id, participant_id, now, editing=True)
        try:
            theory = await commit_phase.lock(
                db,
                session_id,
                _commit_case(arc),
                participant_id,
                entry=state.entry,
                beat_id=state.beat_id,
                humans=await human_player_ids(db, session_id),
                now=now,
                publish=publish,
            )
        except commit_phase.CommitRefusal as refusal:
            raise _commit_refusal(refusal) from refusal
        await _settle(db, orm, arc, now, publish)
        return theory


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
        if state.phase == PhaseKind.mini_game.value:
            await mini_game_phase.pause_bound_run(
                db, session_id, state.beat_id, state.entry, now
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
        if state.phase == PhaseKind.mini_game.value:
            await mini_game_phase.resume_bound_run(
                db, session_id, state.beat_id, state.entry, now
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
            phase_entry=None,
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
                for line in phase_lines(arc, definition)
            )
    if state.phase == PhaseKind.commit.value:
        ready = await commit_phase.locked_ids(db, session_id, state.entry)
    else:
        ready = await _ready_ids(db, session_id, state.entry)
    return RoundView(
        session_status=orm.status,
        beat_id=state.beat_id,
        beat_name=_beat_name(arc, state.beat_id),
        phase_entry=state.entry,
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
    One session failing is logged and does not stop the others. Events are held
    until that session's commit succeeds, then sent in order; any that failed
    to send earlier are retried first, including for sessions no longer active."""
    async with factory() as db:
        result = await db.execute(
            select(OrmSession.session_id, OrmSession.arc_id).where(
                OrmSession.status == SessionStatus.active.value
            )
        )
        active = list(result.all())
    ticked = 0
    seen: set[UUID] = set()
    for session_id, arc_id in active:
        seen.add(session_id)
        arc = load_arc_definition(arc_id)
        if arc is None or not arc.is_phased:
            continue
        async with delivery_lock(session_id):
            outbox = Outbox(session_id)
            committed = False
            try:
                async with factory() as db:
                    try:
                        publisher = publisher_for(session_id)
                        await tick(db, session_id, now, outbox)
                        await db.commit()
                        committed = True
                    except Exception:
                        await db.rollback()
                        outbox.discard()
                        logger.exception("tick failed for session %s", session_id)
            except Exception:
                # Only the session's close can fail here. If the commit went
                # through, the state is saved and its events must still go out.
                logger.exception(
                    "closing the database session failed for %s", session_id
                )
            if not committed:
                continue
            await outbox.flush(publisher)
        ticked += 1
    for session_id in [sid for sid in _PENDING if sid not in seen]:
        async with delivery_lock(session_id):
            try:
                await drain_pending(session_id, publisher_for(session_id))
            except Exception:
                logger.exception("retrying events failed for session %s", session_id)
    return ticked
