"""A beat may run several mini-games, chosen to fit the group (AW-344, D-145).

A beat lists its ``mini_game`` phases one after another; each is a slot with its
own clock, and the number listed is the cap. ``mini_game_pick`` says how a slot
chooses its game: ``listed`` (the default) takes the binding in the same
position, and ``fitting`` takes the first binding, in arc-file order, whose
package allows the player count and whose mechanic has not been started in the
session. The mini-games are test-only packages under
``fixtures/mini_game_packages``; no model is ever called. Time is a value passed
in, and every test reads saved state back.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from datetime import timezone
from typing import Any
from uuid import UUID

import pytest
import pytest_asyncio
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from engine.arc.models import ArcDefinition
from engine.db.orm import Event, MiniGameRun
from engine.db.testing import make_sqlite_session_factory
from engine.events.bus import SessionEventBus
from engine.events.models import AudienceTarget
from engine.mini_games.runtime import MechanicRegistry, MiniGameRuntime
from engine.session.phases import (
    PHASE_EVENT,
    current_phase,
    host_move_on,
    tick,
)
from engine.session.service import SessionService
from engine.tests.rounds_support import (
    MINI_GAME_DURATION,
    MINI_GAME_SECONDS,
    TIMER_RACE_BINDING,
    Recorder,
    Seated,
    TimerRacePlugin,
    at,
    phased_arc,
    reach_phase,
    round_phases,
    seat_session,
    where,
)

ENTERED = 100  # the second at which a test enters the first slot of beat_one
FIRST_ENDS = ENTERED + MINI_GAME_DURATION + 5  # the first game is over, its slot is not
SECOND_ENDS = FIRST_ENDS + MINI_GAME_DURATION + 5


@pytest_asyncio.fixture()
async def db() -> AsyncIterator[AsyncSession]:
    engine, factory = await make_sqlite_session_factory()
    async with factory() as session:
        try:
            yield session
        finally:
            await session.rollback()
    await engine.dispose()


class _Plugin(TimerRacePlugin):
    def __init__(self, mechanic_type: str) -> None:
        self.mechanic_type = mechanic_type


def all_registry() -> MechanicRegistry:
    return MechanicRegistry(
        [_Plugin("timer-race"), _Plugin("quick-race"), _Plugin("duel")]
    )


def bind(game_id: str, **more: Any) -> dict[str, Any]:
    return {
        "binding_id": f"{game_id}-here",
        "game_id": game_id,
        "version": "0.1.0",
        **more,
    }


TIMER = TIMER_RACE_BINDING  # mechanic timer-race, two to eight players
COPY = bind("timer-race-copy")  # the same mechanic as TIMER under another game
QUICK = bind("quick-race")  # another mechanic, two to eight players
DUEL = bind("duel")  # another mechanic, three or four players only


def slots(count: int, seconds: int = MINI_GAME_SECONDS) -> list[dict[str, Any]]:
    """A round's phases with ``count`` mini-game slots in a row."""
    phases: list[dict[str, Any]] = []
    for phase in round_phases("beat_one"):
        if phase["kind"] == "mini_game":
            phases += [{**phase, "seconds": seconds} for _ in range(count)]
        else:
            phases.append(phase)
    return phases


def slotted_arc(
    count: int,
    bindings: list[dict[str, Any]],
    *,
    pick: str | None = None,
    later: list[dict[str, Any]] | None = None,
) -> ArcDefinition:
    """The fixture arc where beat_one has ``count`` slots over ``bindings``.
    ``later`` binds beat_two and beat_three (one slot each, as in the fixture).
    ``pick`` is set on every round beat."""
    return phased_arc(
        phases={"beat_one": slots(count)},
        mini_games={
            "beat_one": bindings,
            "beat_two": later or [],
            "beat_three": later or [],
        },
        mini_game_pick=pick,
    )


async def start(
    db: AsyncSession,
    registered: Callable[[ArcDefinition], None],
    monkeypatch: pytest.MonkeyPatch,
    arc: ArcDefinition,
    *,
    players: int = 2,
    registry: Callable[[], MechanicRegistry] = all_registry,
) -> tuple[Seated, Recorder]:
    """A started session standing in the first mini-game slot of beat_one."""
    registered(arc)
    monkeypatch.setattr("engine.session.mini_game_phase.build_registry", registry)
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
        if run.deadline is not None and run.deadline.tzinfo is None:
            run.deadline = run.deadline.replace(tzinfo=timezone.utc)
    found.sort(key=lambda r: r.definition_snapshot["binding"]["phase_entry"])
    return found


async def games(db: AsyncSession, session_id: UUID) -> list[str]:
    return [r.definition_snapshot["game_id"] for r in await runs(db, session_id)]


async def reasons(db: AsyncSession, session_id: UUID) -> list[str]:
    result = await db.execute(
        select(Event.payload).where(
            Event.session_id == session_id, Event.event_type == PHASE_EVENT
        )
    )
    rows = sorted(result.scalars().all(), key=lambda p: p["seq"])
    return [p["reason"] for p in rows if p["status"] == "ended"]


async def slot_index(db: AsyncSession, session_id: UUID) -> int:
    state = await current_phase(db, session_id)
    assert state is not None
    return state.phase_index


def first_slot_index() -> int:
    return [p["kind"] for p in slots(1)].index("mini_game")


# --- listed: the slot takes the binding in its own position -------------------------


class TestListedSlots:
    @pytest.mark.asyncio
    async def test_two_slots_run_both_games_in_order_and_then_the_round_goes_on(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        monkeypatch: pytest.MonkeyPatch,
        no_model_calls: None,
    ) -> None:
        seated, rec = await start(
            db, registered, monkeypatch, slotted_arc(2, [TIMER, QUICK])
        )
        assert await games(db, seated.session_id) == ["timer-race"]
        assert await slot_index(db, seated.session_id) == first_slot_index()

        await tick(db, seated.session_id, at(FIRST_ENDS), rec)
        assert await games(db, seated.session_id) == ["timer-race", "quick-race"]
        assert await slot_index(db, seated.session_id) == first_slot_index() + 1
        assert (await where(db, seated.session_id))[1:] == ("mini_game", "running")

        await tick(db, seated.session_id, at(SECOND_ENDS), rec)
        assert await where(db, seated.session_id) == ("beat_one", "bridge", "running")
        assert (await reasons(db, seated.session_id))[-2:] == ["mini_game_ended"] * 2
        assert {r.status for r in await runs(db, seated.session_id)} == {"timed_out"}

    @pytest.mark.asyncio
    async def test_a_tick_repeated_at_the_same_moment_starts_no_second_run(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        monkeypatch: pytest.MonkeyPatch,
        no_model_calls: None,
    ) -> None:
        seated, rec = await start(
            db, registered, monkeypatch, slotted_arc(2, [TIMER, QUICK])
        )
        await tick(db, seated.session_id, at(FIRST_ENDS), rec)
        await tick(db, seated.session_id, at(FIRST_ENDS), rec)
        assert len(await runs(db, seated.session_id)) == 2

    @pytest.mark.asyncio
    async def test_every_run_saves_its_own_beat_binding_and_visit(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        monkeypatch: pytest.MonkeyPatch,
        no_model_calls: None,
    ) -> None:
        seated, rec = await start(
            db, registered, monkeypatch, slotted_arc(2, [TIMER, QUICK])
        )
        await tick(db, seated.session_id, at(FIRST_ENDS), rec)
        first, second = [
            r.definition_snapshot["binding"] for r in await runs(db, seated.session_id)
        ]
        assert (first["beat_id"], first["binding_id"]) == (
            "beat_one",
            TIMER["binding_id"],
        )
        assert (second["beat_id"], second["binding_id"]) == (
            "beat_one",
            QUICK["binding_id"],
        )
        assert first["phase_entry"] != second["phase_entry"]

    @pytest.mark.asyncio
    async def test_the_host_moving_on_ends_only_the_slot_it_is_in(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        monkeypatch: pytest.MonkeyPatch,
        no_model_calls: None,
    ) -> None:
        seated, rec = await start(
            db, registered, monkeypatch, slotted_arc(2, [TIMER, QUICK])
        )
        await host_move_on(db, seated.session_id, at(ENTERED + 3), rec)
        first, second = await runs(db, seated.session_id)
        assert (first.status, second.status) == ("cancelled", "active")
        assert await slot_index(db, seated.session_id) == first_slot_index() + 1

        await host_move_on(db, seated.session_id, at(ENTERED + 6), rec)
        assert [r.status for r in await runs(db, seated.session_id)] == [
            "cancelled"
        ] * 2
        assert (await where(db, seated.session_id))[:2] == ("beat_one", "bridge")

    @pytest.mark.asyncio
    async def test_the_second_run_pauses_and_resumes_with_its_own_time_left(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        monkeypatch: pytest.MonkeyPatch,
        no_model_calls: None,
    ) -> None:
        seated, rec = await start(
            db, registered, monkeypatch, slotted_arc(2, [TIMER, QUICK])
        )
        await tick(db, seated.session_id, at(FIRST_ENDS), rec)
        svc = SessionService()
        await svc.pause_session(db, seated.session_id, now=at(FIRST_ENDS + 5))
        first, second = await runs(db, seated.session_id)
        assert (first.status, second.status) == ("timed_out", "paused")
        assert second.pause_deadline_remaining_seconds == MINI_GAME_DURATION - 5

        await svc.resume_session(db, seated.session_id, now=at(900))
        second = (await runs(db, seated.session_id))[1]
        assert second.status == "active"
        await tick(db, seated.session_id, at(900 + MINI_GAME_DURATION - 6), rec)
        assert (await runs(db, seated.session_id))[1].status == "active"
        await tick(db, seated.session_id, at(900 + MINI_GAME_DURATION - 4), rec)
        assert (await runs(db, seated.session_id))[1].status == "timed_out"
        assert (await where(db, seated.session_id))[1] == "bridge"

    @pytest.mark.asyncio
    async def test_each_run_gives_its_own_reward_once(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        monkeypatch: pytest.MonkeyPatch,
        no_model_calls: None,
    ) -> None:
        from engine.session.choices import remaining_budget
        from engine.tests.mini_game_reward_support import ranked_registry

        reward = {"kind": "investigation", "amount": 1, "to": "top_ranked"}
        first_binding = {**TIMER, "binding_id": "first-prize", "reward": reward}
        second_binding = {**TIMER, "binding_id": "second-prize", "reward": reward}
        seated, rec = await start(
            db,
            registered,
            monkeypatch,
            slotted_arc(2, [first_binding, second_binding]),
            players=3,
            registry=ranked_registry,
        )

        async def place(index: int, places: list[int], now: float) -> None:
            run = (await runs(db, seated.session_id))[index]
            rt = MiniGameRuntime(
                db, SessionEventBus(), ranked_registry(), clock=lambda: at(now)
            )
            for who, place_ in enumerate(places):
                await rt.submit_action(
                    run.run_id,
                    f"sub-{index}-{who}",
                    seated.characters[who],
                    {"done": True, "place": place_},
                )

        async def budgets() -> list[int]:
            return [
                await remaining_budget(db, seated.session_id, who)
                for who in seated.participants
            ]

        base = (await budgets())[0]
        await place(0, [1, 2, 3], ENTERED + 5)
        await tick(db, seated.session_id, at(FIRST_ENDS), rec)
        assert await budgets() == [base + 1, base, base]
        await place(1, [3, 1, 2], FIRST_ENDS + 5)
        await tick(db, seated.session_id, at(SECOND_ENDS), rec)
        await tick(db, seated.session_id, at(SECOND_ENDS + 1), rec)
        assert await budgets() == [base + 1, base + 1, base]
        assert len(rec.of_type("mini_game_reward_granted")) == 2


# --- fitting: the first game left, in arc-file order --------------------------------


class TestFittingPick:
    @pytest.mark.asyncio
    async def test_a_mechanic_already_started_is_not_picked_again(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        monkeypatch: pytest.MonkeyPatch,
        no_model_calls: None,
    ) -> None:
        arc = slotted_arc(2, [TIMER, COPY, QUICK], pick="fitting")
        seated, rec = await start(db, registered, monkeypatch, arc)
        await tick(db, seated.session_id, at(FIRST_ENDS), rec)
        assert await games(db, seated.session_id) == ["timer-race", "quick-race"]

    @pytest.mark.asyncio
    async def test_a_game_that_was_cancelled_still_counts_as_played(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        monkeypatch: pytest.MonkeyPatch,
        no_model_calls: None,
    ) -> None:
        arc = slotted_arc(2, [TIMER, QUICK], pick="fitting")
        seated, rec = await start(db, registered, monkeypatch, arc)
        await host_move_on(db, seated.session_id, at(ENTERED + 2), rec)
        assert await games(db, seated.session_id) == ["timer-race", "quick-race"]

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("players", "expected"), [(2, "quick-race"), (3, "duel"), (4, "duel")]
    )
    async def test_a_game_outside_the_players_it_declares_is_not_picked(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        monkeypatch: pytest.MonkeyPatch,
        no_model_calls: None,
        players: int,
        expected: str,
    ) -> None:
        arc = slotted_arc(1, [DUEL, QUICK], pick="fitting")
        seated, _ = await start(db, registered, monkeypatch, arc, players=players)
        assert await games(db, seated.session_id) == [expected]

    @pytest.mark.asyncio
    async def test_arc_file_order_decides_between_games_that_both_fit(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        monkeypatch: pytest.MonkeyPatch,
        no_model_calls: None,
    ) -> None:
        arc = slotted_arc(1, [QUICK, TIMER, DUEL], pick="fitting")
        seated, _ = await start(db, registered, monkeypatch, arc, players=3)
        assert await games(db, seated.session_id) == ["quick-race"]

    @pytest.mark.asyncio
    async def test_a_mechanic_played_in_an_earlier_beat_is_not_picked_in_a_later_one(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        monkeypatch: pytest.MonkeyPatch,
        no_model_calls: None,
    ) -> None:
        arc = slotted_arc(1, [TIMER, QUICK], pick="fitting", later=[TIMER, QUICK])
        seated, rec = await start(db, registered, monkeypatch, arc)
        await reach_phase(db, seated, "beat_two", "mini_game", at(ENTERED + 50), rec)
        assert await games(db, seated.session_id) == ["timer-race", "quick-race"]

    @pytest.mark.asyncio
    async def test_a_pool_longer_than_the_slots_runs_only_as_many_as_there_are_slots(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        monkeypatch: pytest.MonkeyPatch,
        no_model_calls: None,
    ) -> None:
        arc = slotted_arc(1, [TIMER, QUICK, DUEL], pick="fitting")
        seated, rec = await start(db, registered, monkeypatch, arc, players=3)
        await tick(db, seated.session_id, at(FIRST_ENDS), rec)
        assert await games(db, seated.session_id) == ["timer-race"]
        assert (await where(db, seated.session_id))[1] == "bridge"

    @pytest.mark.asyncio
    async def test_when_nothing_fits_the_slot_is_skipped_recorded_and_the_host_told(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        monkeypatch: pytest.MonkeyPatch,
        no_model_calls: None,
    ) -> None:
        arc = slotted_arc(2, [TIMER, COPY, DUEL], pick="fitting")
        seated, rec = await start(db, registered, monkeypatch, arc, players=2)
        await tick(db, seated.session_id, at(FIRST_ENDS), rec)
        assert await games(db, seated.session_id) == ["timer-race"]
        assert await where(db, seated.session_id) == ("beat_one", "bridge", "running")
        assert (await reasons(db, seated.session_id))[-2:] == [
            "mini_game_ended",
            "mini_game_skipped",
        ]
        told = rec.of_type("mini_game_unavailable")
        assert [e.payload["code"] for e in told] == ["none_fit"]
        assert told[0].target_audience is AudienceTarget.host_only

    @pytest.mark.asyncio
    async def test_slots_over_an_empty_pool_are_all_skipped(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        monkeypatch: pytest.MonkeyPatch,
        no_model_calls: None,
    ) -> None:
        arc = slotted_arc(2, [], pick="fitting")
        registered(arc)
        seated = await seat_session(db, arc)
        rec = Recorder()
        await tick(db, seated.session_id, at(0), rec)
        await reach_phase(db, seated, "beat_one", "bridge", at(ENTERED), rec)
        assert await runs(db, seated.session_id) == []
        assert (await reasons(db, seated.session_id)).count("mini_game_skipped") == 2


# --- the arc file ---------------------------------------------------------------------


class TestArcFile:
    def test_a_beat_may_list_mini_game_phases_in_a_row(self) -> None:
        arc = slotted_arc(3, [TIMER, QUICK, DUEL])
        beat = next(b for b in arc.beats if b.beat_id == "beat_one")
        assert [p.kind.value for p in beat.phases or []].count("mini_game") == 3
        assert beat.mini_game_pick == "listed"

    def test_other_phases_still_appear_at_most_once(self) -> None:
        phases = slots(1)
        phases.insert(1, {"kind": "scene", "seconds": 5})
        with pytest.raises(ValidationError, match="at most once"):
            phased_arc(phases={"beat_one": phases})

    def test_mini_game_phases_must_follow_each_other(self) -> None:
        phases = slots(1)
        bridge = next(i for i, p in enumerate(phases) if p["kind"] == "bridge")
        phases.insert(bridge + 1, {"kind": "mini_game", "seconds": 30})
        with pytest.raises(ValidationError):
            phased_arc(phases={"beat_one": phases})

    def test_listed_with_more_slots_than_games_is_refused_by_name(self) -> None:
        with pytest.raises(ValidationError, match="beat_one") as raised:
            slotted_arc(3, [TIMER, QUICK])
        assert "3 mini_game phases" in str(raised.value)

    def test_fitting_may_have_more_slots_than_games_or_none_listed(self) -> None:
        slotted_arc(3, [TIMER], pick="fitting")
        slotted_arc(2, [], pick="fitting")
        slotted_arc(2, [], pick=None)

    def test_a_setting_on_a_game_that_can_run_is_allowed(self) -> None:
        reward = {"kind": "investigation", "amount": 1, "to": "top_ranked"}
        slotted_arc(2, [TIMER, {**QUICK, "reward": reward}])
        slotted_arc(1, [TIMER, {**QUICK, "reward": reward}], pick="fitting")

    def test_a_setting_on_a_game_that_can_never_run_is_still_refused(self) -> None:
        with pytest.raises(ValidationError, match="can never run"):
            slotted_arc(1, [TIMER, {**QUICK, "release_content": False}])
        with pytest.raises(ValidationError, match="can never run"):
            slotted_arc(2, [TIMER, QUICK, {**DUEL, "release_content": False}])

    def test_an_unknown_pick_is_refused(self) -> None:
        with pytest.raises(ValidationError):
            slotted_arc(1, [TIMER], pick="random")
