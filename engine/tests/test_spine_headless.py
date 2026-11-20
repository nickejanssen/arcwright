"""A whole game run headless: opening, three rounds, a final beat (AW-325).

Spec 0093, "Whole spine". The named proof: phases, readiness, choices, the clock
and, since AW-303, one real mini-game run per round (a test-only game, see
``rounds_support``) that starts on entry and ends by a player or by its clock.

No model is called anywhere (the ``no_model_calls`` fixture fails the test if
one is). Time is passed in.
"""

from __future__ import annotations

import asyncio
import time
from collections.abc import AsyncIterator, Callable
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from engine.arc.models import ArcDefinition
from engine.db.orm import Decision, Event, MiniGameRun
from engine.db.orm import Session as OrmSession
from engine.db.testing import make_sqlite_session_factory
from engine.events.bus import SessionEventBus
from engine.events.models import AudienceTarget, ContentEvent, EventCategory
from engine.session.choices import choose, read_menu, remaining_budget
from engine.session.phases import (
    MAX_PUBLISH_ATTEMPTS,
    PHASE_EVENT,
    Outbox,
    Publish,
    content_event,
    current_phase,
    emit,
    mark_ready,
    round_view,
    tick,
    tick_active_sessions,
)
from engine.tests.rounds_support import (
    BEATS,
    BRIDGE_SECONDS,
    CHOICES_SECONDS,
    MINI_GAME_SECONDS,
    SCENE_SECONDS,
    Recorder,
    Seated,
    at,
    phased_arc,
    play_mini_game,
    reach_phase,
    seat_session,
    where,
)

TIMED_TICKS = 5
# Spec 0093: the tick over twenty sessions takes under 200 ms. The limit is on
# the CPU time the tick uses (time.process_time, all threads), not the clock on
# the wall, so a busy machine cannot fail it by making the tick wait for a
# processor (AW-350). The wall-clock backstop is ten times the target: it only
# catches a tick that stalls on something other than the processor.
TICK_CPU_LIMIT_SECONDS = 0.2
TICK_WALL_BACKSTOP_SECONDS = 2.0

EXPECTED_ORDER = [
    ("opening", "scene"),
    ("opening", "bridge"),
    *[
        (beat, phase)
        for beat in BEATS[1:4]
        for phase in ("scene", "choices", "mini_game", "bridge")
    ],
    ("finale", "scene"),
]
ALL_SECONDS = (
    SCENE_SECONDS
    + BRIDGE_SECONDS
    + 3 * (SCENE_SECONDS + CHOICES_SECONDS + MINI_GAME_SECONDS + BRIDGE_SECONDS)
    + SCENE_SECONDS
)

PLAN = {  # what every participant picks, per round, in order
    "beat_one": ["o_ledger", "o_shed"],
    "beat_two": ["o_bench", "o_gate"],
    "beat_three": ["o_attic", "o_cellar"],
}


@pytest_asyncio.fixture()
async def factory() -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    engine, session_factory = await make_sqlite_session_factory()
    try:
        yield session_factory
    finally:
        await engine.dispose()


@pytest_asyncio.fixture()
async def db(
    factory: async_sessionmaker[AsyncSession],
) -> AsyncIterator[AsyncSession]:
    async with factory() as session:
        try:
            yield session
        finally:
            await session.rollback()


async def runs_by_beat(db: AsyncSession) -> dict[str, list[str]]:
    """Each beat's mini-game runs and how they ended, read back from the database."""
    result = await db.execute(select(MiniGameRun))
    by_beat: dict[str, list[str]] = {}
    for run in result.scalars().all():
        beat = run.definition_snapshot["binding"]["beat_id"]
        by_beat.setdefault(beat, []).append(run.status)
    return by_beat


async def phase_order(db: AsyncSession, session_id: UUID) -> list[tuple[str, str]]:
    """Every (beat, phase) entered, in the order it was entered."""
    result = await db.execute(
        select(Event.payload).where(
            Event.session_id == session_id, Event.event_type == PHASE_EVENT
        )
    )
    rows = sorted(result.scalars().all(), key=lambda p: p["seq"])
    return [(p["beat_id"], p["phase"]) for p in rows if p["status"] == "running"]


def entered_once(order: list[tuple[str, str]]) -> list[tuple[str, str]]:
    deduped: list[tuple[str, str]] = []
    for item in order:
        if not deduped or deduped[-1] != item:
            deduped.append(item)
    return deduped


async def play_a_round(
    db: AsyncSession, seated: Seated, rec: Recorder, beat: str, now: float
) -> float:
    """Everyone ready on the scene, two choices each, ready, one player finishes
    the round's real mini-game run, everyone ready on the bridge. Returns the
    new time."""
    for participant in seated.participants:
        await mark_ready(db, seated.session_id, participant, at(now), rec)
    assert (await where(db, seated.session_id))[:2] == (beat, "choices")
    now += 5
    for participant in seated.participants:
        for opportunity in PLAN[beat]:
            await choose(
                db,
                seated.session_id,
                participant,
                f"{participant}-{opportunity}",
                opportunity,
                at(now),
                rec,
            )
    for participant in seated.participants:
        await mark_ready(db, seated.session_id, participant, at(now), rec)
    assert (await where(db, seated.session_id))[:2] == (beat, "mini_game")
    now += 5
    await play_mini_game(db, seated, now, rec)
    assert (await where(db, seated.session_id))[:2] == (beat, "bridge")
    for participant in seated.participants:
        await mark_ready(db, seated.session_id, participant, at(now), rec)
    return now


class TestFullRun:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("players", [2, 4])
    async def test_full_run_reaches_final_beat(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        no_model_calls: None,
        players: int,
    ) -> None:
        arc = phased_arc()
        registered(arc)
        seated = await seat_session(db, arc, players=players)
        rec = Recorder()
        await tick(db, seated.session_id, at(0), rec)

        now = 0.0
        for participant in seated.participants:
            await mark_ready(db, seated.session_id, participant, at(now), rec)
        for participant in seated.participants:
            await mark_ready(db, seated.session_id, participant, at(now), rec)
        for beat in BEATS[1:4]:
            assert (await where(db, seated.session_id))[:2] == (beat, "scene")
            now = await play_a_round(db, seated, rec, beat, now + 1)
        assert await where(db, seated.session_id) == ("finale", "scene", "running")

        assert entered_once(await phase_order(db, seated.session_id)) == EXPECTED_ORDER
        for participant in seated.participants:
            assert await remaining_budget(db, seated.session_id, participant) == 0
        decisions = (
            (
                await db.execute(
                    select(Decision).where(Decision.decision_type == "choice")
                )
            )
            .scalars()
            .all()
        )
        assert len(decisions) == players * 6
        assert await runs_by_beat(db) == {beat: ["completed"] for beat in BEATS[1:4]}
        orm = await db.get(OrmSession, seated.session_id)
        assert orm is not None and orm.current_beat_id == "finale"

    @pytest.mark.asyncio
    @pytest.mark.parametrize("players", [2, 4])
    async def test_a_run_where_nobody_does_anything_reaches_the_final_beat_on_clocks_alone(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        no_model_calls: None,
        players: int,
    ) -> None:
        arc = phased_arc()
        registered(arc)
        seated = await seat_session(db, arc, players=players)
        rec = Recorder()
        now = 0.0
        await tick(db, seated.session_id, at(now), rec)
        for _ in range(len(EXPECTED_ORDER)):
            view = await round_view(db, seated.session_id, at(now))
            if view.beat_id == "finale":
                break
            assert view.seconds_left is not None
            now += view.seconds_left
            await tick(db, seated.session_id, at(now), rec)
        assert (await where(db, seated.session_id))[:2] == ("finale", "scene")
        assert entered_once(await phase_order(db, seated.session_id)) == EXPECTED_ORDER
        final = await tick(db, seated.session_id, at(now + SCENE_SECONDS), rec)
        assert final
        assert now == ALL_SECONDS - SCENE_SECONDS
        assert await runs_by_beat(db) == {beat: ["timed_out"] for beat in BEATS[1:4]}
        assert await where(db, seated.session_id) == ("finale", "scene", "ended")
        for participant in seated.participants:
            assert await remaining_budget(db, seated.session_id, participant) == 6
        assert (
            await db.scalar(
                select(Decision.decision_id).where(Decision.decision_type == "choice")
            )
        ) is None


class TestPrivacyOverAFullRun:
    @pytest.mark.asyncio
    async def test_no_shared_or_other_player_event_holds_what_a_choice_returned(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        no_model_calls: None,
    ) -> None:
        arc = phased_arc()
        registered(arc)
        seated = await seat_session(db, arc, players=3)
        rec = Recorder()
        await tick(db, seated.session_id, at(0), rec)
        now = 0.0
        for participant in seated.participants:
            await mark_ready(db, seated.session_id, participant, at(now), rec)
        for participant in seated.participants:
            await mark_ready(db, seated.session_id, participant, at(now), rec)
        for beat in BEATS[1:4]:
            now = await play_a_round(db, seated, rec, beat, now + 1)

        from engine.case.authored import load_authored_case
        from engine.tests.rounds_support import VALID_CASE

        case = load_authored_case(VALID_CASE, beat_order=BEATS)
        contents = [o.content for o in case.opportunities]
        results = rec.of_type("choice_result")
        assert len(results) == 3 * 6

        for event in rec.events:
            if event.event_type == "choice_result":
                assert event.target_audience is AudienceTarget.specific_player
                continue
            dumped = event.model_dump_json()
            for content in contents:
                assert content not in dumped, event.event_type
        for event in rec.events:
            if event.target_audience is AudienceTarget.specific_player:
                assert event.target_player_id in seated.participants


class TestMenuStaysSmallEachRound:
    @pytest.mark.asyncio
    async def test_every_round_offers_a_fresh_player_at_least_two_choices(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
    ) -> None:
        arc = phased_arc()
        registered(arc)
        seated = await seat_session(db, arc, players=2)
        rec = Recorder()
        await tick(db, seated.session_id, at(0), rec)
        for beat in BEATS[1:4]:
            for _ in range(40):
                state = await current_phase(db, seated.session_id)
                assert state is not None
                if (state.beat_id, state.phase) == (beat, "choices"):
                    break
                await tick(db, seated.session_id, at(10_000 * (1 + _)), rec)
            menu = await read_menu(db, seated.session_id, seated.participants[1])
            assert len([i for i in menu.items]) >= 2


class TestTheTickLoopBody:
    @pytest.mark.asyncio
    async def test_the_loop_body_ticks_every_active_phased_session_once(
        self,
        factory: async_sessionmaker[AsyncSession],
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
    ) -> None:
        arc = phased_arc()
        registered(arc)
        first = await seat_session(db, arc)
        second = await seat_session(db, arc)
        idle = await seat_session(db, arc, start=False)
        await db.commit()
        rec = Recorder()
        ticked = await tick_active_sessions(factory, at(0), lambda _sid: rec)
        assert ticked == 2
        async with factory() as fresh:
            assert (await where(fresh, first.session_id))[:2] == ("opening", "scene")
            assert (await where(fresh, second.session_id))[:2] == ("opening", "scene")
            assert await current_phase(fresh, idle.session_id) is None
        assert len(rec.of_type("phase_changed")) == 2

    @pytest.mark.asyncio
    async def test_twenty_sessions_tick_in_under_two_hundred_milliseconds(
        self,
        factory: async_sessionmaker[AsyncSession],
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
    ) -> None:
        arc = phased_arc()
        registered(arc)
        for _ in range(20):
            await seat_session(db, arc)
        await db.commit()
        rec = Recorder()
        await tick_active_sessions(factory, at(0), lambda _sid: rec)  # enters phases
        cpu_timings: list[float] = []
        wall_timings: list[float] = []
        for _ in range(TIMED_TICKS):
            cpu_started = time.process_time()
            started = time.perf_counter()
            ticked = await tick_active_sessions(factory, at(1), lambda _sid: rec)
            wall_timings.append(time.perf_counter() - started)
            cpu_timings.append(time.process_time() - cpu_started)
            assert ticked == 20
        assert min(cpu_timings) < TICK_CPU_LIMIT_SECONDS
        assert min(wall_timings) < TICK_WALL_BACKSTOP_SECONDS


class TestEventsWaitForTheCommit:
    """AW-338: events leave the engine only after the transaction is saved."""

    @pytest.mark.asyncio
    async def test_a_failed_commit_publishes_nothing_and_the_retry_publishes_once(
        self,
        factory: async_sessionmaker[AsyncSession],
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        arc = phased_arc()
        registered(arc)
        seated = await seat_session(db, arc)
        await db.commit()
        rec = Recorder()

        async def refuse(self: AsyncSession) -> None:
            raise RuntimeError("commit failed")

        with monkeypatch.context() as broken:
            broken.setattr(AsyncSession, "commit", refuse)
            await tick_active_sessions(factory, at(0), lambda _sid: rec)
        assert rec.events == []
        async with factory() as fresh:
            assert await current_phase(fresh, seated.session_id) is None

        await tick_active_sessions(factory, at(1), lambda _sid: rec)
        assert len(rec.of_type("phase_changed")) == 1
        assert len(rec.of_type("phase_line")) == 1

    @pytest.mark.asyncio
    async def test_events_are_published_after_the_commit_not_before(
        self,
        factory: async_sessionmaker[AsyncSession],
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        arc = phased_arc()
        registered(arc)
        await seat_session(db, arc)
        await db.commit()
        rec = Recorder()
        seen_at_commit: list[int] = []
        real_commit = AsyncSession.commit

        async def spy(self: AsyncSession) -> None:
            seen_at_commit.append(len(rec.events))
            await real_commit(self)

        monkeypatch.setattr(AsyncSession, "commit", spy)
        await tick_active_sessions(factory, at(0), lambda _sid: rec)
        assert seen_at_commit == [0]
        assert len(rec.events) > 0

    @pytest.mark.asyncio
    async def test_an_event_published_when_a_mini_game_phase_ends_waits_too(
        self,
        factory: async_sessionmaker[AsyncSession],
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        arc = phased_arc()
        registered(arc)
        seated = await seat_session(db, arc)
        await tick(db, seated.session_id, at(0))
        await reach_phase(db, seated, "beat_one", "mini_game", at(100))
        await db.commit()
        rec = Recorder()
        seen_at_commit: list[int] = []
        real_commit = AsyncSession.commit

        async def spy(self: AsyncSession) -> None:
            seen_at_commit.append(len(rec.of_type("reward_like")))
            await real_commit(self)

        async def end_with_event(
            _db: AsyncSession,
            session_id: UUID,
            _beat: str,
            _entry: int,
            now: datetime,
            publish: Publish,
        ) -> None:
            await emit(
                publish,
                content_event(
                    session_id,
                    now,
                    category=EventCategory.private_delivery,
                    event_type="reward_like",
                    audience=AudienceTarget.host_only,
                    payload={},
                ),
            )

        monkeypatch.setattr(AsyncSession, "commit", spy)
        monkeypatch.setattr(
            "engine.session.phases.mini_game_phase.stop_open_run", end_with_event
        )
        await tick_active_sessions(
            factory, at(100 + MINI_GAME_SECONDS + 1), lambda _sid: rec
        )
        assert len(rec.of_type("reward_like")) == 1
        assert seen_at_commit and seen_at_commit[0] == 0


class TestDeliveryKeepsStateChangeOrder:
    """AW-338 review: events reach the bus in the order the changes were saved,
    and one that fails to send is retried in order rather than lost."""

    @pytest.mark.asyncio
    async def test_a_later_tick_cannot_overtake_an_earlier_one_paused_after_its_commit(
        self,
        factory: async_sessionmaker[AsyncSession],
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        arc = phased_arc()
        registered(arc)
        await seat_session(db, arc)
        await db.commit()
        rec = Recorder()
        real_commit = AsyncSession.commit
        paused, release = asyncio.Event(), asyncio.Event()
        first = True

        async def slow_first(self: AsyncSession) -> None:
            nonlocal first
            await real_commit(self)
            if first:
                first = False
                paused.set()
                await release.wait()

        monkeypatch.setattr(AsyncSession, "commit", slow_first)
        one = asyncio.create_task(
            tick_active_sessions(factory, at(0), lambda _sid: rec)
        )
        await paused.wait()
        two = asyncio.create_task(
            tick_active_sessions(factory, at(SCENE_SECONDS + 1), lambda _sid: rec)
        )
        await asyncio.sleep(0.1)
        release.set()
        await asyncio.gather(one, two)
        entries = [e.payload["phase_entry"] for e in rec.of_type("phase_changed")]
        assert len(entries) >= 2
        assert entries == sorted(entries)

    @pytest.mark.asyncio
    async def test_a_failed_publish_is_retried_in_order_for_a_connected_client(
        self,
        factory: async_sessionmaker[AsyncSession],
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        arc = phased_arc()
        registered(arc)
        seated = await seat_session(db, arc)
        await tick(db, seated.session_id, at(0))
        await reach_phase(db, seated, "beat_one", "mini_game", at(100))
        await db.commit()

        async def end_with_private_event(
            _db: AsyncSession,
            session_id: UUID,
            _beat: str,
            _entry: int,
            now: datetime,
            publish: Publish,
        ) -> None:
            await emit(
                publish,
                content_event(
                    session_id,
                    now,
                    category=EventCategory.private_delivery,
                    event_type="reward_like",
                    audience=AudienceTarget.specific_player,
                    target_player_id=seated.participants[0],
                    payload={},
                ),
            )

        monkeypatch.setattr(
            "engine.session.phases.mini_game_phase.stop_open_run",
            end_with_private_event,
        )
        bus = SessionEventBus()
        connected = bus.subscribe()
        failures = {"left": 1}

        async def flaky(event: ContentEvent) -> ContentEvent:
            if event.event_type == "reward_like" and failures["left"]:
                failures["left"] -= 1
                raise RuntimeError("bus hiccup")
            return await bus.publish(event)

        end = at(100 + MINI_GAME_SECONDS + 1)
        await tick_active_sessions(factory, end, lambda _sid: flaky)
        # only what came before the failing event; nothing jumped ahead of it
        assert [e.event_type for e in bus.replay_since(0)] == ["mini_game_finalized"]
        await tick_active_sessions(factory, end, lambda _sid: flaky)
        types = [e.event_type for e in bus.replay_since(0)]
        assert types[:2] == ["mini_game_finalized", "reward_like"]
        assert types.count("reward_like") == 1
        assert types.index("phase_changed") > types.index("reward_like")
        await connected.aclose()

    @pytest.mark.asyncio
    async def test_an_event_that_never_sends_is_dropped_so_it_cannot_block_the_session(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        session_id = uuid4()
        outbox = Outbox(session_id)
        for kind in ("bad", "good"):
            await outbox(
                content_event(
                    session_id,
                    at(0),
                    category=EventCategory.state_transition,
                    event_type=kind,
                    audience=AudienceTarget.all,
                    payload={},
                )
            )
        sent: list[str] = []

        async def picky(event: ContentEvent) -> ContentEvent:
            if event.event_type == "bad":
                raise RuntimeError("never works")
            sent.append(event.event_type)
            return event

        for _ in range(MAX_PUBLISH_ATTEMPTS):
            assert sent == []
            await outbox.flush(picky)
        assert sent == ["good"]
        assert any("dropping bad" in r.getMessage() for r in caplog.records)

    @pytest.mark.asyncio
    async def test_a_failure_after_the_commit_still_sends_that_sessions_events(
        self,
        factory: async_sessionmaker[AsyncSession],
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
    ) -> None:
        arc = phased_arc()
        registered(arc)
        await seat_session(db, arc)
        await seat_session(db, arc)
        await db.commit()
        rec = Recorder()
        calls = {"n": 0}

        class _ClosingFails:
            def __init__(self) -> None:
                calls["n"] += 1
                self._first = calls["n"] == 1
                self._cm = factory()

            async def __aenter__(self) -> AsyncSession:
                return await self._cm.__aenter__()

            async def __aexit__(self, *exc: Any) -> None:
                await self._cm.__aexit__(*exc)
                if not self._first:
                    raise RuntimeError("closing the session failed")

        await tick_active_sessions(_ClosingFails, at(0), lambda _sid: rec)  # type: ignore[arg-type]
        assert len(rec.of_type("phase_changed")) == 2
