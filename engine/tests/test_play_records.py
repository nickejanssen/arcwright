"""Play records: one query per fact, four questions (AW-304, spec 0093 Part F).

One scripted headless run is played, then every reader in
``engine.telemetry.play_records`` is asserted against it. The script, with two
players ``a`` and ``b`` (a third and fourth idle when there are four):

- ``beat_one`` scene: only ``a`` marks ready, so the scene ends on time (stall).
- ``beat_one`` choices: both open their menu; ``a`` takes the ledger, the
  porter and the shed, ``b`` takes nothing.
- ``mini_game``: the run the phase started is ended by one player's submission
  and given its placings.
- ``beat_two`` choices: each is given one extra budget (a reward); ``a`` spends
  past the base budget of four (and leaves the free note), ``b`` does not.

Everything is made up. No model is called.
"""

from __future__ import annotations

import ast
from collections.abc import AsyncIterator, Callable
from dataclasses import dataclass
from datetime import timezone
from pathlib import Path
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from engine.arc.models import ArcDefinition
from engine.characters.service import CharacterService
from engine.db.orm import (
    Claim,
    Decision,
    Event,
    MiniGameRun,
)
from engine.db.testing import make_sqlite_session_factory
from engine.events.bus import SessionEventBus
from engine.mini_games.runtime import MiniGameRuntime
from engine.routing import log_generation
from engine.routing.router import RouteResult, resolve_model_key
from engine.session.choices import choose, read_menu
from engine.session.phases import (
    finish_mini_game_phase,
    freeze_phase,
    mark_ready,
    thaw_phase,
    tick,
)
from engine.session.service import SessionService
from engine.telemetry import play_records as pack
from engine.tests.rounds_support import (
    Recorder,
    Seated,
    at,
    phased_arc,
    seat_session,
    timer_race_registry,
    where,
)

BASE_BUDGET = 4


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


def arc_with_targets() -> ArcDefinition:
    arc = phased_arc(budget=BASE_BUDGET)
    data = arc.model_dump(mode="json")
    data["authorial_intent"] = {
        "theme": "a quiet house",
        "tone": "uneasy",
        "emotional_targets": [
            {"beat_id": "beat_one", "target_tension": 0.4},
            {"beat_id": "beat_two", "target_tension": 0.6},
        ],
    }
    return ArcDefinition.model_validate(data)


@dataclass(frozen=True)
class Played:
    seated: Seated
    run_id: UUID

    @property
    def session_id(self) -> UUID:
        return self.seated.session_id

    @property
    def a(self) -> UUID:
        return self.seated.participants[0]

    @property
    def b(self) -> UUID:
        return self.seated.participants[1]

    @property
    def idle(self) -> tuple[UUID, ...]:
        return self.seated.participants[2:]


async def ticks_until(
    db: AsyncSession, seated: Seated, beat: str, phase: str, now: float, rec: Recorder
) -> None:
    for _ in range(6):
        await tick(db, seated.session_id, at(now), rec)
        if (await where(db, seated.session_id))[:2] == (beat, phase):
            return
    raise AssertionError(f"never reached {beat}/{phase}")


async def all_ready(
    db: AsyncSession, seated: Seated, now: float, rec: Recorder
) -> None:
    for participant in seated.participants:
        await mark_ready(db, seated.session_id, participant, at(now), rec)


@pytest_asyncio.fixture(params=[2, 4], ids=["two_players", "four_players"])
async def played(
    request: pytest.FixtureRequest,
    db: AsyncSession,
    registered: Callable[[ArcDefinition], None],
    no_model_calls: None,
) -> Played:
    arc = arc_with_targets()
    registered(arc)
    seated = await seat_session(db, arc, players=request.param)
    sid, a, b = seated.session_id, seated.participants[0], seated.participants[1]
    rec = Recorder()
    await tick(db, sid, at(0), rec)

    await all_ready(db, seated, 0, rec)  # opening scene
    await all_ready(db, seated, 0, rec)  # opening bridge
    assert (await where(db, sid))[:2] == ("beat_one", "scene")
    await mark_ready(db, sid, a, at(0), rec)
    await ticks_until(db, seated, "beat_one", "choices", 25, rec)

    await read_menu(db, sid, a, at(26))
    await read_menu(db, sid, b, at(26))
    await read_menu(db, sid, a, at(27))  # a second read saves nothing new
    await choose(db, sid, a, "a-1", "o_ledger", at(30), rec)
    await choose(db, sid, a, "a-2", "o_porter", at(31), rec)
    await choose(db, sid, a, "a-2b", "o_shed", at(32), rec)

    await ticks_until(db, seated, "beat_one", "mini_game", 86, rec)
    # The phase started a real run bound to this beat. One player submits, which
    # completes it (at 95), and the run is given placings; the phase then ends.
    runtime = MiniGameRuntime(
        db, SessionEventBus(), timer_race_registry(), clock=lambda: at(95)
    )
    run = await runtime.get_active_run(sid)
    assert run is not None and run.started_at is not None
    if run.deadline is not None and run.deadline.tzinfo is None:
        run.deadline = run.deadline.replace(tzinfo=timezone.utc)  # SQLite drops it
    await runtime.submit_action(run.run_id, "s-1", seated.characters[0], {"done": True})
    assert run.status == "completed"
    run.outcome = {"placings": [str(a), str(b)]}  # this test game does not rank
    await db.flush()
    assert await finish_mini_game_phase(db, sid, at(100), rec)

    await all_ready(db, seated, 101, rec)  # bridge
    await all_ready(db, seated, 102, rec)  # beat_two scene
    assert (await where(db, sid))[:2] == ("beat_two", "choices")
    for participant in (a, b):
        db.add(
            Decision(
                session_id=sid,
                timestamp=at(103),
                decision_type="budget_grant",
                context={"participant_id": str(participant)},
                outcome={"amount": 1},
            )
        )
    await db.flush()
    await read_menu(db, sid, a, at(104))
    await read_menu(db, sid, b, at(104))
    await choose(db, sid, a, "a-3", "o_gate", at(105), rec)
    await choose(db, sid, a, "a-4", "o_bench", at(106), rec)
    await choose(db, sid, b, "b-1", "o_bench", at(107), rec)
    return Played(seated, run.run_id)


class TestEveryFactReturnsRows:
    @pytest.mark.asyncio
    async def test_fact_1_story_units_with_times(
        self, db: AsyncSession, played: Played
    ) -> None:
        visits = await pack.story_unit_visits(db, played.session_id)
        assert [(v.beat_id, v.phase) for v in visits][:4] == [
            ("opening", "scene"),
            ("opening", "bridge"),
            ("beat_one", "scene"),
            ("beat_one", "choices"),
        ]
        scene = visits[2]
        assert scene.entered_at == at(0) and scene.left_at == at(25)
        assert scene.left_reason == "time" and scene.active_seconds == 25
        assert visits[-1].left_at is None  # still in beat_two choices

    @pytest.mark.asyncio
    async def test_fact_2_who_learned_what_and_from_whom(
        self, db: AsyncSession, played: Played
    ) -> None:
        rows = await pack.learned(db, played.session_id)
        mine = [r for r in rows if r.participant_id == played.a]
        assert {r.fact_ref for r in mine} >= {"c_open_a", "c_open_b", "c_ledger"}
        ledger = next(r for r in mine if r.fact_ref == "c_ledger")
        assert ledger.source_opportunity_id == "o_ledger"
        assert ledger.source_character_id is None
        opening = next(r for r in mine if r.fact_ref == "c_open_a")
        assert opening.source_opportunity_id is None

    @pytest.mark.asyncio
    async def test_fact_3_what_was_chosen_from_what_was_offered(
        self, db: AsyncSession, played: Played
    ) -> None:
        rows = await pack.choices(db, played.session_id)
        kinds = [r.kind for r in rows]
        assert kinds.count("choice") == 6
        assert kinds.count("menu_shown") == 4
        assert kinds.count("ready") >= 4
        assert kinds.count("mini_game_submission") == 1
        first = next(r for r in rows if r.kind == "choice")
        assert first.participant_id == played.a
        assert first.detail["opportunity_id"] == "o_ledger"
        assert set(first.detail["offered"]) == {"o_ledger", "o_shed", "o_porter"}
        assert first.detail["subject_id"] == "s_ledger"

    @pytest.mark.asyncio
    async def test_fact_4_what_each_character_said(
        self, db: AsyncSession, played: Played
    ) -> None:
        sid = played.session_id
        character = played.seated.characters[0]
        db.add(
            Claim(
                claim_id=(claim_id := uuid4()),
                session_id=sid,
                speaker_character_id=character,
                round_index=1,
                beat_id="beat_one",
                interaction_window_id="w",
                claim_text="I was at the gate.",
            )
        )
        db.add(
            Event(
                session_id=sid,
                actor_char_id=character,
                event_type="dialogue",
                payload={"claim_id": str(claim_id), "current_beat_id": "beat_one"},
                content_text="I was at the gate.",
            )
        )
        await db.flush()
        await CharacterService(sessions=SessionService()).submit_input(
            db, sid, character, played.a, "dialogue", "Where were you?"
        )
        rows = await pack.said(db, sid)
        assert sorted((r.source, r.text) for r in rows) == [
            ("dialogue", "I was at the gate."),
            ("player_input", "Where were you?"),
        ]
        typed = next(r for r in rows if r.source == "player_input")
        assert typed.character_id == character and typed.beat_id == "beat_two"

    @pytest.mark.asyncio
    async def test_fact_5_tension_against_the_target(
        self, db: AsyncSession, played: Played
    ) -> None:
        rows = await pack.tension(db, played.session_id)
        updates = [r for r in rows if r.kind == "update" and r.beat_id == "beat_one"]
        assert updates and updates[0].target_score == 0.4
        summary = [r for r in rows if r.kind == "summary" and r.beat_id == "beat_one"]
        assert summary and summary[0].target_score == 0.4

    @pytest.mark.asyncio
    async def test_fact_6_cost(self, db: AsyncSession, played: Played) -> None:
        empty = await pack.cost(db, played.session_id)
        assert empty.total_generation_count == 0
        await log_generation(
            db,
            session_id=played.session_id,
            task_type="character_dialogue",
            quality_tier="standard",
            result=RouteResult(
                content="x",
                model_used=resolve_model_key("character_dialogue", "standard"),
                input_tokens=100,
                output_tokens=20,
                latency_ms=5,
                used_fallback=False,
            ),
        )
        summary = await pack.cost(db, played.session_id)
        assert summary.total_generation_count == 1
        assert summary.total_cost_usd > 0


class TestTheFourQuestions:
    @pytest.mark.asyncio
    async def test_where_did_players_stall(
        self, db: AsyncSession, played: Played
    ) -> None:
        stalls = await pack.stalled_phases(db, played.session_id)
        scene = next(s for s in stalls if (s.beat_id, s.phase) == ("beat_one", "scene"))
        assert scene.ended_by == "time"
        assert set(scene.not_ready) == set(played.seated.participants[1:])
        opening = stalls[0]
        assert opening.ended_by == "ready" and opening.not_ready == ()
        slowest = max(
            (s for s in stalls if s.active_seconds is not None),
            key=lambda s: s.active_seconds or 0,
        )
        assert (slowest.beat_id, slowest.phase) == ("beat_one", "choices")

    @pytest.mark.asyncio
    async def test_what_content_did_nobody_see(
        self, db: AsyncSession, played: Played
    ) -> None:
        unseen = await pack.unchosen_opportunities(db, played.session_id)
        assert [u.opportunity_id for u in unseen] == ["o_note"]
        assert unseen[0].subject_id == "s_ledger" and unseen[0].times_offered == 1

    @pytest.mark.asyncio
    async def test_which_characters_drew_attention(
        self, db: AsyncSession, played: Played
    ) -> None:
        rows = await pack.attention_by_subject(db, played.session_id)
        assert rows[0].subject_id == "s_bench" and rows[0].choices == 2
        assert rows[0].subject_kind == "object" and rows[0].participants == 2
        assert {r.subject_id for r in rows} == {
            "s_bench",
            "s_ledger",
            "s_porter",
            "s_shed",
            "s_gate",
        }

    @pytest.mark.asyncio
    async def test_was_the_mini_game_reward_used(
        self, db: AsyncSession, played: Played
    ) -> None:
        report = await pack.reward_use(db, played.session_id)
        by_who = {g.participant_id: g for g in report.grants}
        assert by_who[played.a].granted == 1 and by_who[played.a].extra_spent == 1
        assert by_who[played.a].used is True
        assert by_who[played.b].granted == 1 and by_who[played.b].extra_spent == 0
        assert by_who[played.b].used is False
        (run,) = report.runs
        assert run.status == "completed" and run.beat_id == "beat_one"
        assert run.outcome == {"placings": [str(played.a), str(played.b)]}


class TestTheRecordIsEnoughOnItsOwn:
    @pytest.mark.asyncio
    async def test_no_reader_opens_a_content_file(
        self,
        db: AsyncSession,
        played: Played,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        def refuse(*_a: object, **_k: object) -> str:
            raise AssertionError("a content file was read")

        monkeypatch.setattr(Path, "read_text", refuse)
        monkeypatch.setattr(Path, "read_bytes", refuse)
        monkeypatch.setattr("builtins.open", refuse)
        sid = played.session_id
        await pack.story_unit_visits(db, sid)
        await pack.learned(db, sid)
        await pack.choices(db, sid)
        await pack.said(db, sid)
        await pack.tension(db, sid)
        await pack.stalled_phases(db, sid)
        await pack.unchosen_opportunities(db, sid)
        await pack.attention_by_subject(db, sid)
        await pack.reward_use(db, sid)

    def test_the_pack_imports_no_content_loader(self) -> None:
        source = Path(pack.__file__).read_text("utf-8")
        modules = {
            node.module or ""
            for node in ast.walk(ast.parse(source))
            if isinstance(node, ast.ImportFrom)
        }
        forbidden = ("engine.case", "engine.arc", "engine.session.case_seating")
        assert not [m for m in modules if m.startswith(forbidden)]

    @pytest.mark.asyncio
    async def test_rows_saved_before_this_task_do_not_break_the_readers(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        arc = arc_with_targets()
        registered(arc)
        seated = await seat_session(db, arc, players=2, start=False)
        sid, a = seated.session_id, seated.participants[0]
        db.add(
            Decision(
                session_id=sid,
                decision_type="choice",
                context={
                    "choice_id": "old",
                    "participant_id": str(a),
                    "beat_id": "beat_one",
                    "phase_entry": 1,
                    "offered": ["o_ledger"],
                    "opportunity_id": "o_ledger",
                },
                outcome={"cost": 1, "gave": ["c_ledger"], "first_time": True},
            )
        )
        await db.flush()
        rows = await pack.attention_by_subject(db, sid)
        assert [(r.subject_id, r.choices) for r in rows] == [(None, 1)]
        report = await pack.reward_use(db, sid)
        assert report.grants == [] and report.runs == []
        assert await pack.stalled_phases(db, sid) == []


class TestEdgeCases:
    @pytest.mark.asyncio
    async def test_a_paused_phase_does_not_count_the_pause(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        no_model_calls: None,
    ) -> None:
        arc = arc_with_targets()
        registered(arc)
        seated = await seat_session(db, arc, players=2)
        sid = seated.session_id
        rec = Recorder()
        await tick(db, sid, at(0), rec)
        await freeze_phase(db, sid, at(5))
        await thaw_phase(db, sid, at(50))
        await ticks_until(db, seated, "opening", "bridge", 66, rec)
        (scene, bridge) = (await pack.story_unit_visits(db, sid))[:2]
        assert scene.left_at == at(66) and scene.left_reason == "time"
        assert scene.active_seconds == 5 + 16  # 0 to 5, then 50 to 66
        assert bridge.active_seconds is None  # still inside it

    @pytest.mark.asyncio
    async def test_a_run_with_no_start_time_has_no_beat_and_does_not_break(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        arc = arc_with_targets()
        registered(arc)
        seated = await seat_session(db, arc, players=2, start=False)
        db.add(
            MiniGameRun(
                run_id=(run_id := uuid4()),
                session_id=seated.session_id,
                game_id="fixture-game",
                definition_version="1",
                definition_snapshot={},
                status="pending",
                started_at=None,
            )
        )
        await db.flush()
        report = await pack.reward_use(db, seated.session_id)
        (run,) = report.runs
        assert run.run_id == run_id and run.beat_id is None
        assert run.outcome is None and report.grants == []

    @pytest.mark.asyncio
    async def test_a_grant_with_no_later_choice_is_unused(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        arc = arc_with_targets()
        registered(arc)
        seated = await seat_session(db, arc, players=2, start=False)
        a = seated.participants[0]
        db.add(
            Decision(
                session_id=seated.session_id,
                timestamp=at(10),
                decision_type="budget_grant",
                context={"participant_id": str(a)},
                outcome={"amount": 1},
            )
        )
        await db.flush()
        report = await pack.reward_use(db, seated.session_id)
        assert [
            (g.participant_id, g.granted, g.extra_spent, g.used) for g in report.grants
        ] == [(a, 1, 0, False)]
