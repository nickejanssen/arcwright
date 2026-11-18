"""A beat's mini-game inside a round (spec 0093, Part E; AW-303).

``engine.session.phases`` moves a round from phase to phase. This module is
what it calls when the phase is a ``mini_game``:

  - ``begin``: find the beat's bound game, resolve it, create the run and start
    it. A beat with no binding skips the phase. A binding that cannot run ends
    the phase at once with a recorded error and a note to the host, so the game
    never hangs.
  - ``advance``: on each tick, ask the run whether its time is up, then read its
    saved state back. Any end state ends the phase. The phase's own time limit
    is a hard cap: a run still going at the cap is cancelled.
  - ``stop_open_run``: a phase that ends any other way leaves no run open.
  - ``pause_bound_run`` / ``resume_bound_run``: pausing the session keeps the
    run's time left, and resuming restarts it.

Every function here is called with the session lock already held by the caller,
and every one reads saved state first, so a repeated call finds nothing to do.
The run records its beat inside its stored definition (``RunBinding``); no
table changes. Timing, validity and scoring stay in ``engine.mini_games``.
"""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from engine.arc.models import ArcDefinition, BeatDefinition, PhaseKind
from engine.db.orm import MiniGameRun
from engine.db.orm import Session as OrmSession
from engine.events.bus import SessionEventBus
from engine.events.models import (
    AudienceTarget,
    ContentEvent,
    EventCategory,
    PresentationHints,
)
from engine.mini_games.loader import MiniGamePackageError, load_mini_game_package
from engine.mini_games.models import MiniGameBinding
from engine.mini_games.plugins import default_registry
from engine.mini_games.resolver import (
    ResolvedMiniGameSnapshot,
    RunBinding,
    resolve_loaded_mini_game_snapshot,
)
from engine.mini_games.runtime import (
    DerivedOutputValidationError,
    MechanicRegistry,
    MiniGameRuntime,
    RevisionConflictError,
    UnknownMechanicTypeError,
)

logger = logging.getLogger(__name__)

Publish = Callable[[ContentEvent], Awaitable[Any]] | None

ENDED = "mini_game_ended"
SKIPPED = "mini_game_skipped"
ERROR_PREFIX = "mini_game_error:"
UNAVAILABLE_EVENT = "mini_game_unavailable"
WARNING_EVENT = "mini_game_warning"

TERMINAL_STATUSES = frozenset({"completed", "timed_out", "cancelled"})
_REPO_ROOT = Path(__file__).resolve().parents[2]


class _Unavailable(Exception):
    """The beat's game cannot run. ``code`` is stable and goes into the saved
    reason and the host's note."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


class _PublishBus:
    """Lets the runtime publish through the caller's publisher. With none, the
    runtime's events are dropped; saved state is unaffected."""

    def __init__(self, publish: Publish) -> None:
        self._publish = publish

    async def publish(self, event: ContentEvent) -> ContentEvent:
        if self._publish is not None:
            await self._publish(event)
        return event


def build_registry() -> MechanicRegistry:
    """The closed set of game rules a run may use. Tests swap this."""
    return default_registry()


def _runtime(db: AsyncSession, now: datetime, publish: Publish) -> MiniGameRuntime:
    bus = cast(SessionEventBus, _PublishBus(publish))
    return MiniGameRuntime(db, bus, build_registry(), clock=lambda: now)


# --- finding the run -----------------------------------------------------------------


async def bound_run(
    db: AsyncSession, session_id: UUID, beat_id: str, phase_entry: int
) -> MiniGameRun | None:
    """The run made for this visit to this beat's mini-game phase, in any state."""
    result = await db.execute(
        select(MiniGameRun).where(MiniGameRun.session_id == session_id)
    )
    for run in result.scalars().all():
        binding = (run.definition_snapshot or {}).get("binding")
        if (
            isinstance(binding, dict)
            and binding.get("beat_id") == beat_id
            and binding.get("phase_entry") == phase_entry
        ):
            _keep_time_zone(run)
            return run
    return None


def _keep_time_zone(run: MiniGameRun) -> None:
    """SQLite (used by tests) returns saved times without a zone, and the
    runtime compares them with zoned clocks. Postgres already returns zoned
    times, so there this changes nothing."""
    if run.deadline is not None and run.deadline.tzinfo is None:
        run.deadline = run.deadline.replace(tzinfo=timezone.utc)


# --- starting ------------------------------------------------------------------------


async def _resolve(
    db: AsyncSession, orm: OrmSession, arc: ArcDefinition, binding: MiniGameBinding
) -> ResolvedMiniGameSnapshot:
    if not arc.mini_game_root:
        raise _Unavailable("no_root")
    try:
        loaded = load_mini_game_package(
            _REPO_ROOT / arc.mini_game_root / binding.game_id
        )
    except MiniGamePackageError as exc:
        logger.warning("mini-game package for %s unusable: %s", binding.game_id, exc)
        raise _Unavailable("package_missing") from exc
    if loaded.definition.version != binding.version:
        raise _Unavailable("version_mismatch")
    try:
        return await resolve_loaded_mini_game_snapshot(
            db,
            session_id=orm.session_id,
            loaded_game=loaded,
            quality_tier=orm.quality_tier,
            content_rails=arc.content_rails,
        )
    except SQLAlchemyError:
        raise  # the transaction is in doubt; the tick must fail and retry whole
    except Exception as exc:
        # Broad on purpose: resolving a generated game calls the model router,
        # which can fail in many ways, and the round must not hang on any of them.
        logger.exception("mini-game %s could not be resolved", binding.game_id)
        raise _Unavailable("resolution_failed") from exc


async def _tell_host(
    publish: Publish,
    session_id: UUID,
    now: datetime,
    event_type: str,
    payload: dict[str, Any],
) -> None:
    if publish is None:
        return
    await publish(
        ContentEvent(
            session_id=session_id,
            timestamp=now,
            category=EventCategory.state_transition,
            event_type=event_type,
            target_audience=AudienceTarget.host_only,
            payload=payload,
            presentation_hints=PresentationHints(),
        )
    )


async def _tell_host_unavailable(
    publish: Publish, session_id: UUID, now: datetime, beat_id: str, code: str
) -> None:
    await _tell_host(
        publish,
        session_id,
        now,
        UNAVAILABLE_EVENT,
        {"beat_id": beat_id, "code": code},
    )


async def begin(
    db: AsyncSession,
    orm: OrmSession,
    arc: ArcDefinition,
    beat_id: str,
    phase_entry: int,
    now: datetime,
    publish: Publish,
) -> str | None:
    """Create and start the beat's run. Returns None when the run is going, or
    the reason the phase must end at once (nothing to run, or it cannot run)."""
    beat = next(b for b in arc.beats if b.beat_id == beat_id)
    if not beat.mini_games:
        return SKIPPED
    binding = beat.mini_games[0]
    runtime = _runtime(db, now, publish)
    run: MiniGameRun | None = None
    try:
        snapshot = await _resolve(db, orm, arc, binding)
        snapshot = snapshot.model_copy(
            update={
                "binding": RunBinding(
                    beat_id=beat_id,
                    binding_id=binding.binding_id,
                    phase_entry=phase_entry,
                    release_content=binding.release_content,
                    reward=binding.reward,
                )
            }
        )
        run = await runtime.create_run(orm.session_id, snapshot)
        await runtime.start_run(run.run_id)
        await _warn_if_phase_is_short(
            publish, orm.session_id, now, beat, snapshot.duration_seconds
        )
        return None
    except _Unavailable as exc:
        code = exc.code
    except UnknownMechanicTypeError:
        code = "unknown_mechanic"
    except DerivedOutputValidationError:
        code = "invalid_definition"
    except SQLAlchemyError:
        raise
    except Exception:
        # A game's own rule raised while the run was being made or started. Left
        # alone it would fail the tick again every second and hang the round.
        logger.exception("mini-game run for beat %s did not start", beat_id)
        code = "run_not_started"
        if run is not None:
            await runtime.cancel_run(run.run_id)
    await _tell_host_unavailable(publish, orm.session_id, now, beat_id, code)
    return f"{ERROR_PREFIX}{code}"


async def _warn_if_phase_is_short(
    publish: Publish,
    session_id: UUID,
    now: datetime,
    beat: BeatDefinition,
    game_seconds: int,
) -> None:
    """The phase's time limit is a hard cap. If it is not longer than the game,
    the run is cancelled at the cap and never reaches its own end: tell the host."""
    phase = next(p for p in beat.phases or [] if p.kind is PhaseKind.mini_game)
    if phase.seconds > game_seconds:
        return
    await _tell_host(
        publish,
        session_id,
        now,
        WARNING_EVENT,
        {
            "beat_id": beat.beat_id,
            "code": "phase_not_longer_than_game",
            "phase_seconds": phase.seconds,
            "game_seconds": game_seconds,
        },
    )


# --- each tick -----------------------------------------------------------------------


async def advance(
    db: AsyncSession,
    session_id: UUID,
    beat_id: str,
    phase_entry: int,
    phase_deadline: datetime | None,
    now: datetime,
    publish: Publish,
) -> str | None:
    """What, if anything, ends the phase now. The run's end state is read back
    from saved state: a game that moves its own deadline instead of ending is
    not over, whatever ``check_timeout`` returned."""
    run = await bound_run(db, session_id, beat_id, phase_entry)
    if run is None:
        return f"{ERROR_PREFIX}run_missing"
    runtime = _runtime(db, now, publish)
    if run.status == "active":
        try:
            await runtime.check_timeout(run.run_id)  # changes ``run`` in place
        except (RevisionConflictError, SQLAlchemyError):
            raise  # a concurrent writer or a database fault: fail and retry
        except Exception:
            # The game's own end-of-run work raised (scoring, a content release).
            # Left alone the tick would fail again every second and the phase's
            # time limit would never apply.
            logger.exception("mini-game run %s failed while ending", run.run_id)
            await runtime.cancel_run(run.run_id)
            await _tell_host_unavailable(
                publish, session_id, now, beat_id, "run_failed"
            )
            return f"{ERROR_PREFIX}run_failed"
    if run.status in TERMINAL_STATUSES:
        return ENDED
    if phase_deadline is not None and now >= phase_deadline:
        await runtime.cancel_run(run.run_id)
        return "time"
    return None


async def run_is_over(
    db: AsyncSession, session_id: UUID, beat_id: str, phase_entry: int
) -> bool:
    run = await bound_run(db, session_id, beat_id, phase_entry)
    return run is not None and run.status in TERMINAL_STATUSES


async def stop_open_run(
    db: AsyncSession,
    session_id: UUID,
    beat_id: str,
    phase_entry: int,
    now: datetime,
    publish: Publish,
) -> None:
    """The phase is ending: leave no run open to block the next round, and give
    the reward of a run that finished.

    A run still going is cancelled (no standing, no reward). A run that is over
    is left as it is, and the reward set on its binding is given once
    (``mini_game_reward.give`` finds a repeat itself). ``phases._end`` calls this
    at every mini-game phase end, under the session lock."""
    run = await bound_run(db, session_id, beat_id, phase_entry)
    if run is not None and run.status not in TERMINAL_STATUSES:
        await _runtime(db, now, publish).cancel_run(run.run_id)
        return
    from engine.session import mini_game_reward  # at call time: avoids a cycle

    try:
        await mini_game_reward.give(db, session_id, beat_id, phase_entry, now, publish)
    except SQLAlchemyError:
        raise
    except Exception:
        # A reward that cannot be given must not fail the tick every second.
        logger.exception("mini-game reward for beat %s was not given", beat_id)


# --- pause and resume ----------------------------------------------------------------


async def pause_bound_run(
    db: AsyncSession, session_id: UUID, beat_id: str, phase_entry: int, now: datetime
) -> None:
    run = await bound_run(db, session_id, beat_id, phase_entry)
    if run is not None and run.status == "active":
        await _runtime(db, now, None).pause_run(run.run_id)


async def resume_bound_run(
    db: AsyncSession, session_id: UUID, beat_id: str, phase_entry: int, now: datetime
) -> None:
    run = await bound_run(db, session_id, beat_id, phase_entry)
    if run is not None and run.status == "paused":
        await _runtime(db, now, None).resume_run(run.run_id)
