"""A beat's mini-game starts, times out and returns to the round (AW-303).

Spec 0093, Part E. The mini-game here is a test-only package
(``fixtures/mini_game_packages/timer-race``): hand-written, so resolving it makes
no model call, and it allows two to eight players, which no shipped game does.
Time is a value passed in. Every test reads the saved state back, because a
refused state-machine transition is ignored silently and does not raise.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock, patch
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from engine.arc.models import ArcDefinition
from engine.arc.registry import load_arc_definition
from engine.db.orm import Event, MiniGameRun
from engine.db.testing import make_sqlite_session_factory
from engine.events.bus import SessionEventBus
from engine.events.models import AudienceTarget
from engine.mini_games.models import ClueVariant, DelayedClueFallback
from engine.mini_games.resolver import ResolvedMiniGameSnapshot
from engine.mini_games.runtime import (
    DerivedOutputValidationError,
    MechanicRegistry,
    MiniGameRuntime,
    RunStateError,
)
from engine.session.phases import (
    PHASE_EVENT,
    current_phase,
    finish_mini_game_phase,
    host_move_on,
    mark_ready,
    public_mini_game_result,
    tick,
)
from engine.session.service import SessionService
from engine.tests.rounds_support import (
    MINI_GAME_DURATION,
    MINI_GAME_SECONDS,
    TIMER_RACE_BINDING,
    Recorder,
    Seated,
    at,
    phased_arc,
    play_mini_game,
    reach_phase,
    round_phases,
    seat_session,
    timer_race_registry,
    where,
)

ENTERED = 100  # the second at which a test enters beat_one's mini-game phase


@pytest.mark.asyncio
async def test_public_result_hold_survives_tick_and_ends_on_ready(
    db: AsyncSession, registered: Callable[[ArcDefinition], None], no_model_calls: None
) -> None:
    data = phased_arc().model_dump(mode="json")
    beat = next(b for b in data["beats"] if b["beat_id"] == "beat_one")
    phase = next(p for p in beat["phases"] if p["kind"] == "mini_game")
    phase.update(result_hold_seconds=15, result_public=True)
    seated, rec = await in_mini_game(
        db, registered, arc=ArcDefinition.model_validate(data)
    )
    run = await the_run(db, seated.session_id)
    run.status = "completed"
    run.outcome = {
        "standing": [[str(p) for p in seated.participants]],
        "private": "secret",
    }
    await db.flush()
    before = await current_phase(db, seated.session_id)
    assert before is not None
    await tick(db, seated.session_id, at(ENTERED + 1), rec)
    hold = await current_phase(db, seated.session_id)
    assert (
        hold is not None
        and hold.entry == before.entry
        and hold.result_run_id == str(run.run_id)
    )
    result = await public_mini_game_result(db, seated.session_id)
    assert result is not None and "private" not in result
    assert set(result) == {
        "run_id",
        "game_id",
        "definition_version",
        "phase_entry",
        "deadline_at",
        "standing",
    }
    assert result["standing"] == [[str(p) for p in seated.participants]]
    original_outcome = run.outcome
    run.outcome = {"standing": [[str(seated.participants[0]), "outsider"]]}
    await db.flush()
    assert await public_mini_game_result(db, seated.session_id) is None
    run.outcome = original_outcome
    duplicate = MiniGameRun(
        run_id=uuid4(),
        session_id=seated.session_id,
        game_id=run.game_id,
        definition_version=run.definition_version,
        definition_snapshot=run.definition_snapshot,
        status="completed",
        outcome=run.outcome,
        clue_unlock_record={},
    )
    db.add(duplicate)
    await db.flush()
    assert await public_mini_game_result(db, seated.session_id) is None
    await db.delete(duplicate)
    await db.flush()
    await tick(db, seated.session_id, at(ENTERED + 2), rec)
    assert (await current_phase(db, seated.session_id)).entry == hold.entry
    for participant in seated.participants:
        await mark_ready(
            db,
            seated.session_id,
            participant,
            at(ENTERED + 3),
            rec,
            phase_entry=hold.entry,
        )
    assert await public_mini_game_result(db, seated.session_id) is None


@pytest.mark.asyncio
async def test_result_hold_clock_pauses_and_expires(
    db: AsyncSession, registered: Callable[[ArcDefinition], None], no_model_calls: None
) -> None:
    data = phased_arc().model_dump(mode="json")
    beat = next(b for b in data["beats"] if b["beat_id"] == "beat_one")
    phase = next(p for p in beat["phases"] if p["kind"] == "mini_game")
    phase.update(result_hold_seconds=15, result_public=True)
    seated, rec = await in_mini_game(
        db, registered, arc=ArcDefinition.model_validate(data)
    )
    run = await the_run(db, seated.session_id)
    run.status = "timed_out"
    run.outcome = {"standing": [[str(p) for p in seated.participants]]}
    await db.flush()
    await tick(db, seated.session_id, at(ENTERED + 1), rec)
    hold = await current_phase(db, seated.session_id)
    assert hold is not None and hold.result_run_id
    svc = SessionService()
    await svc.pause_session(db, seated.session_id, now=at(ENTERED + 5))
    paused = await current_phase(db, seated.session_id)
    assert paused is not None and paused.remaining_seconds == 11
    assert await public_mini_game_result(db, seated.session_id) is not None
    await svc.resume_session(db, seated.session_id, now=at(ENTERED + 30))
    resumed = await current_phase(db, seated.session_id)
    assert resumed is not None and resumed.deadline_at == at(ENTERED + 41)
    await tick(db, seated.session_id, at(ENTERED + 41), rec)
    assert await public_mini_game_result(db, seated.session_id) is None


@pytest.mark.asyncio
async def test_result_hold_deadline_takes_precedence_over_last_ready(
    db: AsyncSession, registered: Callable[[ArcDefinition], None], no_model_calls: None
) -> None:
    data = phased_arc().model_dump(mode="json")
    beat = next(b for b in data["beats"] if b["beat_id"] == "beat_one")
    phase = next(p for p in beat["phases"] if p["kind"] == "mini_game")
    phase.update(result_hold_seconds=15, result_public=True)
    seated, rec = await in_mini_game(
        db, registered, arc=ArcDefinition.model_validate(data)
    )
    run = await the_run(db, seated.session_id)
    run.status = "completed"
    run.outcome = {"standing": [[str(p) for p in seated.participants]]}
    await db.flush()
    await tick(db, seated.session_id, at(ENTERED + 1), rec)
    hold = await current_phase(db, seated.session_id)
    assert hold is not None
    await mark_ready(
        db,
        seated.session_id,
        seated.participants[0],
        at(ENTERED + 2),
        rec,
        phase_entry=hold.entry,
    )
    await mark_ready(
        db,
        seated.session_id,
        seated.participants[1],
        at(ENTERED + 16),
        rec,
        phase_entry=hold.entry,
    )
    assert (await reasons(db, seated.session_id))[-1] == "time"


@pytest.mark.asyncio
@pytest.mark.parametrize("finish", ["completed", "timed_out"])
async def test_real_run_transition_enters_result_hold(
    db: AsyncSession,
    registered: Callable[[ArcDefinition], None],
    no_model_calls: None,
    finish: str,
) -> None:
    data = phased_arc().model_dump(mode="json")
    beat = next(b for b in data["beats"] if b["beat_id"] == "beat_one")
    phase = next(p for p in beat["phases"] if p["kind"] == "mini_game")
    phase.update(result_hold_seconds=15, result_public=True)
    seated, rec = await in_mini_game(
        db, registered, arc=ArcDefinition.model_validate(data)
    )
    if finish == "completed":
        await play_mini_game(db, seated, ENTERED + 2, rec)
    else:
        await tick(db, seated.session_id, at(ENTERED + MINI_GAME_DURATION + 1), rec)
    run = await the_run(db, seated.session_id)
    assert run.status == finish
    hold = await current_phase(db, seated.session_id)
    assert hold is not None and hold.result_run_id == str(run.run_id)
    assert await public_mini_game_result(db, seated.session_id) is not None


@pytest_asyncio.fixture()
async def db() -> AsyncIterator[AsyncSession]:
    engine, factory = await make_sqlite_session_factory()
    async with factory() as session:
        try:
            yield session
        finally:
            await session.rollback()
    await engine.dispose()


async def in_mini_game(
    db: AsyncSession,
    registered: Callable[[ArcDefinition], None],
    *,
    players: int = 2,
    arc: ArcDefinition | None = None,
) -> tuple[Seated, Recorder]:
    """A started session standing in beat_one's mini-game phase, entered at 100."""
    arc = arc or phased_arc()
    registered(arc)
    seated = await seat_session(db, arc, players=players)
    rec = Recorder()
    await tick(db, seated.session_id, at(0), rec)
    await reach_phase(db, seated, "beat_one", "mini_game", at(ENTERED), rec)
    return seated, rec


async def runs(db: AsyncSession, session_id: UUID) -> list[MiniGameRun]:
    result = await db.execute(
        select(MiniGameRun)
        .where(MiniGameRun.session_id == session_id)
        .execution_options(populate_existing=True)
    )
    found = list(result.scalars().all())
    for run in found:  # SQLite returns times without a zone; the runtime needs one
        run.deadline = aware(run.deadline)
    return found


async def the_run(db: AsyncSession, session_id: UUID) -> MiniGameRun:
    (run,) = await runs(db, session_id)
    return run


def runtime(db: AsyncSession, now: float) -> MiniGameRuntime:
    return MiniGameRuntime(
        db, SessionEventBus(), timer_race_registry(), clock=lambda: at(now)
    )


def aware(value: datetime | None) -> datetime:
    assert value is not None
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


async def reasons(db: AsyncSession, session_id: UUID) -> list[str]:
    result = await db.execute(
        select(Event.payload).where(
            Event.session_id == session_id, Event.event_type == PHASE_EVENT
        )
    )
    rows = sorted(result.scalars().all(), key=lambda p: p["seq"])
    return [p["reason"] for p in rows if p["status"] == "ended"]


# --- start ------------------------------------------------------------------------


class TestStart:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("players", [2, 4])
    async def test_entering_the_phase_creates_and_starts_exactly_one_bound_run(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        no_model_calls: None,
        players: int,
    ) -> None:
        seated, rec = await in_mini_game(db, registered, players=players)
        run = await the_run(db, seated.session_id)
        state = await current_phase(db, seated.session_id)
        assert state is not None and state.phase == "mini_game"
        assert run.status == "active"
        assert aware(run.started_at) == at(ENTERED)
        assert aware(run.deadline) == at(ENTERED + MINI_GAME_DURATION)
        snapshot = ResolvedMiniGameSnapshot.model_validate(run.definition_snapshot)
        assert snapshot.binding is not None
        assert snapshot.binding.beat_id == "beat_one"
        assert snapshot.binding.binding_id == TIMER_RACE_BINDING["binding_id"]
        assert snapshot.binding.phase_entry == state.entry
        started = rec.of_type("mini_game_started")
        assert len(started) == 1
        assert started[0].target_audience is AudienceTarget.all

    @pytest.mark.asyncio
    async def test_ticking_again_makes_no_second_run(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        no_model_calls: None,
    ) -> None:
        seated, rec = await in_mini_game(db, registered)
        await tick(db, seated.session_id, at(ENTERED), rec)
        await tick(db, seated.session_id, at(ENTERED + 1), rec)
        assert len(await runs(db, seated.session_id)) == 1
        assert len(rec.of_type("mini_game_started")) == 1

    @pytest.mark.asyncio
    async def test_each_round_makes_its_own_run(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        no_model_calls: None,
    ) -> None:
        seated, rec = await in_mini_game(db, registered)
        await tick(db, seated.session_id, at(ENTERED + 25), rec)
        await reach_phase(db, seated, "beat_two", "mini_game", at(200), rec)
        all_runs = await runs(db, seated.session_id)
        beats = sorted(
            ResolvedMiniGameSnapshot.model_validate(
                r.definition_snapshot
            ).binding.beat_id  # type: ignore[union-attr]
            for r in all_runs
        )
        assert beats == ["beat_one", "beat_two"]
        assert sorted(r.status for r in all_runs) == ["active", "timed_out"]


# --- the clock --------------------------------------------------------------------


class TestTimeout:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("players", [2, 4])
    async def test_with_no_submissions_the_run_ends_at_its_deadline_and_the_round_goes_on(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        no_model_calls: None,
        players: int,
    ) -> None:
        seated, rec = await in_mini_game(db, registered, players=players)
        await tick(db, seated.session_id, at(ENTERED + MINI_GAME_DURATION - 1), rec)
        assert (await the_run(db, seated.session_id)).status == "active"
        assert await where(db, seated.session_id) == (
            "beat_one",
            "mini_game",
            "running",
        )

        await tick(db, seated.session_id, at(ENTERED + MINI_GAME_DURATION + 1), rec)
        run = await the_run(db, seated.session_id)
        assert run.status == "timed_out"
        assert await where(db, seated.session_id) == ("beat_one", "bridge", "running")
        assert (await reasons(db, seated.session_id))[-1] == "mini_game_ended"
        final = rec.of_type("mini_game_finalized")
        assert [e.payload["status"] for e in final] == ["timed_out"]

    @pytest.mark.asyncio
    async def test_a_late_tick_ends_the_run_and_the_phase_once(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        no_model_calls: None,
    ) -> None:
        seated, rec = await in_mini_game(db, registered)
        await tick(db, seated.session_id, at(5000), rec)
        await tick(db, seated.session_id, at(5000), rec)
        assert (await the_run(db, seated.session_id)).status == "timed_out"
        assert (await where(db, seated.session_id))[:2] == ("beat_one", "bridge")
        assert len(rec.of_type("mini_game_finalized")) == 1

    @pytest.mark.asyncio
    async def test_the_phase_time_limit_is_a_hard_cap_over_the_game(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        no_model_calls: None,
    ) -> None:
        short = round_phases("beat_one")
        short[2]["seconds"] = 10
        arc = phased_arc(phases={"beat_one": short})
        seated, rec = await in_mini_game(db, registered, arc=arc)
        await tick(db, seated.session_id, at(ENTERED + 9), rec)
        assert (await the_run(db, seated.session_id)).status == "active"
        await tick(db, seated.session_id, at(ENTERED + 10), rec)
        assert (await the_run(db, seated.session_id)).status == "cancelled"
        assert (await where(db, seated.session_id))[:2] == ("beat_one", "bridge")
        assert (await reasons(db, seated.session_id))[-1] == "time"


# --- every end state ends the phase ------------------------------------------------


class TestEndStates:
    @pytest.mark.asyncio
    async def test_a_completed_run_ends_the_phase_on_the_next_tick(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        no_model_calls: None,
    ) -> None:
        seated, rec = await in_mini_game(db, registered)
        run = await the_run(db, seated.session_id)
        await runtime(db, ENTERED + 5).submit_action(
            run.run_id, "s1", seated.characters[0], {"done": True}
        )
        assert (await the_run(db, seated.session_id)).status == "completed"
        assert (await where(db, seated.session_id))[:2] == ("beat_one", "mini_game")
        await tick(db, seated.session_id, at(ENTERED + 6), rec)
        assert (await where(db, seated.session_id))[:2] == ("beat_one", "bridge")
        assert (await reasons(db, seated.session_id))[-1] == "mini_game_ended"

    @pytest.mark.asyncio
    @pytest.mark.parametrize("command", ["resolve", "cancel"])
    async def test_a_host_command_on_the_run_ends_the_phase(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        no_model_calls: None,
        command: str,
    ) -> None:
        seated, rec = await in_mini_game(db, registered)
        run = await the_run(db, seated.session_id)
        rt = runtime(db, ENTERED + 5)
        if command == "resolve":
            await rt.resolve_run(run.run_id)
        else:
            await rt.cancel_run(run.run_id)
        await tick(db, seated.session_id, at(ENTERED + 6), rec)
        assert (await where(db, seated.session_id))[:2] == ("beat_one", "bridge")
        assert (await reasons(db, seated.session_id))[-1] == "mini_game_ended"
        expected = "completed" if command == "resolve" else "cancelled"
        assert (await the_run(db, seated.session_id)).status == expected

    @pytest.mark.asyncio
    async def test_the_host_moving_on_cancels_the_run_and_leaves_none_open(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        no_model_calls: None,
    ) -> None:
        seated, rec = await in_mini_game(db, registered)
        await host_move_on(db, seated.session_id, at(ENTERED + 3), rec)
        assert (await the_run(db, seated.session_id)).status == "cancelled"
        assert await runtime(db, ENTERED + 3).get_active_run(seated.session_id) is None
        assert (await where(db, seated.session_id))[:2] == ("beat_one", "bridge")
        assert (await reasons(db, seated.session_id))[-1] == "host"


class TestSubmissions:
    @pytest.mark.asyncio
    async def test_a_repeated_submission_id_is_saved_once_and_the_phase_stays(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        no_model_calls: None,
    ) -> None:
        seated, _ = await in_mini_game(db, registered)
        run = await the_run(db, seated.session_id)
        rt = runtime(db, ENTERED + 5)
        first = await rt.submit_action(
            run.run_id, "dup", seated.characters[0], {"done": False}
        )
        second = await rt.submit_action(
            run.run_id, "dup", seated.characters[0], {"done": False}
        )
        assert first.submission_id == second.submission_id
        assert not first.is_accepted
        assert (await where(db, seated.session_id))[:2] == ("beat_one", "mini_game")
        assert (await the_run(db, seated.session_id)).status == "active"

    @pytest.mark.asyncio
    async def test_a_late_submission_is_refused_and_the_round_still_moves_on_once(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        no_model_calls: None,
    ) -> None:
        seated, rec = await in_mini_game(db, registered)
        run = await the_run(db, seated.session_id)
        with pytest.raises(RunStateError):
            await runtime(db, ENTERED + MINI_GAME_DURATION + 2).submit_action(
                run.run_id, "late", seated.characters[0], {"done": True}
            )
        assert (await the_run(db, seated.session_id)).status == "timed_out"
        await tick(db, seated.session_id, at(ENTERED + MINI_GAME_DURATION + 3), rec)
        assert (await where(db, seated.session_id))[:2] == ("beat_one", "bridge")
        assert (await reasons(db, seated.session_id))[-1] == "mini_game_ended"


# --- pause and resume --------------------------------------------------------------


class TestPauseAndResume:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("players", [2, 4])
    async def test_pausing_the_session_pauses_the_run_and_resuming_keeps_the_time_left(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        no_model_calls: None,
        players: int,
    ) -> None:
        seated, rec = await in_mini_game(db, registered, players=players)
        svc = SessionService()
        await svc.pause_session(db, seated.session_id, now=at(ENTERED + 5))

        run = await the_run(db, seated.session_id)
        assert run.status == "paused"
        assert run.pause_deadline_remaining_seconds == MINI_GAME_DURATION - 5
        assert await where(db, seated.session_id) == ("beat_one", "mini_game", "paused")
        state = await current_phase(db, seated.session_id)
        assert state is not None
        assert state.remaining_seconds == MINI_GAME_SECONDS - 5

        await tick(db, seated.session_id, at(9000), rec)
        assert (await the_run(db, seated.session_id)).status == "paused"

        await svc.resume_session(db, seated.session_id, now=at(300))
        run = await the_run(db, seated.session_id)
        assert run.status == "active"
        assert aware(run.deadline) == at(300 + MINI_GAME_DURATION - 5)
        state = await current_phase(db, seated.session_id)
        assert state is not None and state.status == "running"
        assert state.deadline_at == at(300 + MINI_GAME_SECONDS - 5)

        await tick(db, seated.session_id, at(300 + MINI_GAME_DURATION - 6), rec)
        assert (await the_run(db, seated.session_id)).status == "active"
        await tick(db, seated.session_id, at(300 + MINI_GAME_DURATION - 4), rec)
        assert (await the_run(db, seated.session_id)).status == "timed_out"
        assert (await where(db, seated.session_id))[:2] == ("beat_one", "bridge")

    @pytest.mark.asyncio
    async def test_pausing_outside_a_mini_game_phase_touches_no_run(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        no_model_calls: None,
    ) -> None:
        arc = phased_arc()
        registered(arc)
        seated = await seat_session(db, arc)
        await tick(db, seated.session_id, at(0), Recorder())
        svc = SessionService()
        await svc.pause_session(db, seated.session_id, now=at(3))
        await svc.resume_session(db, seated.session_id, now=at(8))
        assert await runs(db, seated.session_id) == []
        assert await where(db, seated.session_id) == ("opening", "scene", "running")


# --- a beat with nothing to run, or nothing that can run ---------------------------


async def to_choices(
    db: AsyncSession,
    registered: Callable[[ArcDefinition], None],
    arc: ArcDefinition,
) -> tuple[Seated, Recorder]:
    registered(arc)
    seated = await seat_session(db, arc)
    rec = Recorder()
    await tick(db, seated.session_id, at(0), rec)
    await reach_phase(db, seated, "beat_one", "choices", at(ENTERED), rec)
    return seated, rec


class TestNothingToRun:
    @pytest.mark.asyncio
    async def test_a_beat_with_no_binding_skips_the_phase(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        no_model_calls: None,
    ) -> None:
        arc = phased_arc(mini_games={"beat_one": []})
        seated, rec = await to_choices(db, registered, arc)
        await host_move_on(db, seated.session_id, at(ENTERED + 1), rec)
        assert await where(db, seated.session_id) == ("beat_one", "bridge", "running")
        assert (await reasons(db, seated.session_id))[-2:] == [
            "host",
            "mini_game_skipped",
        ]
        assert await runs(db, seated.session_id) == []

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("code", "binding", "root", "empty_registry"),
        [
            ("package_missing", {"game_id": "no-such-game"}, "default", False),
            ("version_mismatch", {"version": "9.9.9"}, "default", False),
            ("no_root", {}, None, False),
            ("unknown_mechanic", {}, "default", True),
        ],
    )
    async def test_a_binding_that_cannot_run_ends_the_phase_with_a_recorded_error(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        no_model_calls: None,
        code: str,
        binding: dict[str, str],
        root: str | None,
        empty_registry: bool,
    ) -> None:
        kwargs: dict[str, Any] = {
            "mini_games": {"beat_one": [{**TIMER_RACE_BINDING, **binding}]}
        }
        if root != "default":
            kwargs["mini_game_root"] = root
        arc = phased_arc(**kwargs)
        seated, rec = await to_choices(db, registered, arc)
        with patch(
            "engine.session.mini_game_phase.build_registry",
            (lambda: MechanicRegistry([])) if empty_registry else timer_race_registry,
        ):
            await host_move_on(db, seated.session_id, at(ENTERED + 1), rec)
        assert await where(db, seated.session_id) == ("beat_one", "bridge", "running")
        assert (await reasons(db, seated.session_id))[-1] == f"mini_game_error:{code}"
        told = rec.of_type("mini_game_unavailable")
        assert len(told) == 1
        assert told[0].target_audience is AudienceTarget.host_only
        assert told[0].payload["code"] == code
        assert await runs(db, seated.session_id) == []


class TestAGameThatFails:
    """A game that breaks must end its phase with a recorded error, not hang
    the round by failing the tick again every second."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("code", "target", "failure"),
        [
            (
                "run_not_started",
                "engine.session.mini_game_phase.MiniGameRuntime.start_run",
                ValueError("a rule broke"),
            ),
            (
                "invalid_definition",
                "engine.session.mini_game_phase.MiniGameRuntime.create_run",
                DerivedOutputValidationError("bad output"),
            ),
            (
                "resolution_failed",
                "engine.session.mini_game_phase.resolve_loaded_mini_game_snapshot",
                RuntimeError("could not resolve"),
            ),
        ],
    )
    async def test_a_failure_starting_the_run_ends_the_phase_with_a_recorded_error(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        no_model_calls: None,
        code: str,
        target: str,
        failure: Exception,
    ) -> None:
        seated, rec = await to_choices(db, registered, phased_arc())
        with patch(target, AsyncMock(side_effect=failure)):
            await host_move_on(db, seated.session_id, at(ENTERED + 1), rec)
        assert await where(db, seated.session_id) == ("beat_one", "bridge", "running")
        assert (await reasons(db, seated.session_id))[-1] == f"mini_game_error:{code}"
        assert [e.payload["code"] for e in rec.of_type("mini_game_unavailable")] == [
            code
        ]
        assert all(r.status == "cancelled" for r in await runs(db, seated.session_id))

    @pytest.mark.asyncio
    async def test_a_database_error_is_not_turned_into_a_game_error(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        no_model_calls: None,
    ) -> None:
        seated, rec = await to_choices(db, registered, phased_arc())
        with (
            patch(
                "engine.session.mini_game_phase.resolve_loaded_mini_game_snapshot",
                AsyncMock(side_effect=SQLAlchemyError("connection lost")),
            ),
            pytest.raises(SQLAlchemyError),
        ):
            await host_move_on(db, seated.session_id, at(ENTERED + 1), rec)

    @pytest.mark.asyncio
    async def test_a_failure_while_the_run_ends_cancels_it_and_ends_the_phase(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        no_model_calls: None,
    ) -> None:
        seated, rec = await in_mini_game(db, registered)
        with patch.object(
            MiniGameRuntime,
            "check_timeout",
            AsyncMock(side_effect=ValueError("scoring broke")),
        ):
            await tick(db, seated.session_id, at(ENTERED + 5), rec)
        assert await where(db, seated.session_id) == ("beat_one", "bridge", "running")
        assert (await reasons(db, seated.session_id))[
            -1
        ] == "mini_game_error:run_failed"
        assert (await the_run(db, seated.session_id)).status == "cancelled"
        assert [e.payload["code"] for e in rec.of_type("mini_game_unavailable")] == [
            "run_failed"
        ]

    @pytest.mark.asyncio
    async def test_a_running_phase_whose_run_has_gone_ends_with_a_recorded_error(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        no_model_calls: None,
    ) -> None:
        seated, rec = await in_mini_game(db, registered)
        await db.delete(await the_run(db, seated.session_id))
        await db.flush()
        await tick(db, seated.session_id, at(ENTERED + 1), rec)
        assert (await where(db, seated.session_id))[:2] == ("beat_one", "bridge")
        assert (await reasons(db, seated.session_id))[
            -1
        ] == "mini_game_error:run_missing"


class TestPhaseLengthAgainstGameLength:
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("seconds", "warned"), [(MINI_GAME_DURATION, True), (10, True), (30, False)]
    )
    async def test_the_host_is_told_when_the_phase_is_not_longer_than_the_game(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        no_model_calls: None,
        seconds: int,
        warned: bool,
    ) -> None:
        phases = round_phases("beat_one")
        phases[2]["seconds"] = seconds
        arc = phased_arc(phases={"beat_one": phases})
        _, rec = await in_mini_game(db, registered, arc=arc)
        told = rec.of_type("mini_game_warning")
        assert len(told) == (1 if warned else 0)
        if warned:
            assert told[0].target_audience is AudienceTarget.host_only
            assert told[0].payload == {
                "beat_id": "beat_one",
                "code": "phase_not_longer_than_game",
                "phase_seconds": seconds,
                "game_seconds": MINI_GAME_DURATION,
            }


class TestArcFileBinding:
    def test_a_binding_on_a_beat_with_no_mini_game_phase_is_refused(self) -> None:
        without = [p for p in round_phases("beat_one") if p["kind"] != "mini_game"]
        with pytest.raises(ValidationError, match="mini_game phase"):
            phased_arc(phases={"beat_one": without})


# --- the hook the stand-in used to be ----------------------------------------------


class TestFinishHook:
    @pytest.mark.asyncio
    async def test_it_changes_nothing_while_the_run_is_going_and_ends_the_phase_once_over(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        no_model_calls: None,
    ) -> None:
        seated, rec = await in_mini_game(db, registered)
        assert not await finish_mini_game_phase(db, seated.session_id, at(101), rec)
        assert await where(db, seated.session_id) == (
            "beat_one",
            "mini_game",
            "running",
        )
        run = await the_run(db, seated.session_id)
        await runtime(db, ENTERED + 2).resolve_run(run.run_id)
        assert await finish_mini_game_phase(db, seated.session_id, at(103), rec)
        assert (await where(db, seated.session_id))[:2] == ("beat_one", "bridge")
        assert not await finish_mini_game_phase(db, seated.session_id, at(104), rec)


# --- saved data and files that must stay readable -----------------------------------


class TestOldDataStillLoads:
    def test_a_snapshot_saved_without_a_binding_still_reads(self) -> None:
        snapshot = ResolvedMiniGameSnapshot(
            game_id="old-game",
            definition_version="0.1.0",
            source_content_mode="authored",  # type: ignore[arg-type]
            mechanic_type="timer-race",
            participation_mode="individual",
            min_players=1,
            max_players=2,
            duration_seconds=10,
            rules={},
            behavioral_outputs=(),
            clue_fallback=DelayedClueFallback(
                delay_seconds=1, clue_variant=ClueVariant.reduced
            ),
            resolved_content={},
        )
        stored = snapshot.model_dump(mode="json")
        stored.pop("binding")
        assert ResolvedMiniGameSnapshot.model_validate(stored).binding is None

    def test_the_registered_arc_files_name_no_mini_game_root(self) -> None:
        for arc_id in ("nightcap-v1", "nightcap-couch-race-v1"):
            arc = load_arc_definition(arc_id)
            assert arc is not None
            assert arc.mini_game_root is None
