"""The registered 1a schedule, exercised with synthetic case content."""

from __future__ import annotations

import json
from collections.abc import AsyncIterator, Callable
from datetime import timedelta
from pathlib import Path

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from engine.arc.models import ArcDefinition
from engine.arc.registry import load_arc_definition
from engine.db.testing import make_sqlite_session_factory
from engine.events.bus import SessionEventBus
from engine.mini_games.plugins import default_registry
from engine.mini_games.runtime import MiniGameRuntime
from engine.session.choices import choose, remaining_budget
from engine.session.phases import current_phase, lock_theory, save_theory_draft, tick
from engine.tests.rounds_support import VALID_CASE, Recorder, at, seat_session, where
from engine.tests.test_battle_of_wits import aware, choice
from engine.tests.test_spine_headless import entered_once, phase_order

ARC_ID = "nightcap-agency-race-1a"
ROUNDS = [f"round_{number}" for number in range(1, 5)]
SLOTS = [1, 2, 1, 1]


@pytest_asyncio.fixture()
async def db() -> AsyncIterator[AsyncSession]:
    engine, factory = await make_sqlite_session_factory()
    try:
        async with factory() as session:
            yield session
    finally:
        await engine.dispose()


def agency_arc() -> ArcDefinition:
    arc = load_arc_definition(ARC_ID)
    assert arc is not None and arc.arc_id == ARC_ID
    return arc


def test_registered_schedule():
    arc = agency_arc()
    assert (arc.min_players, arc.max_players, arc.choice_config.budget) == (2, 4, 6)
    assert arc.case_file == "nightcap/cases/local/agency-race-1a.json"
    assert [
        beat.beat_id
        for beat in arc.beats
        if any(phase.kind.value == "choices" for phase in beat.phases or [])
    ] == ROUNDS
    rounds = arc.beats[:4]
    assert [beat.mini_game_slots for beat in rounds] == SLOTS
    for beat in rounds:
        assert beat.mini_game_pick == "listed"
        assert beat.mini_games
        for binding in beat.mini_games:
            assert binding.game_id == "battle-of-wits"
            assert not binding.release_content
            assert binding.reward is not None
            assert (binding.reward.kind, binding.reward.amount, binding.reward.to) == (
                "investigation",
                1,
                "top_ranked",
            )
    for arc_id in ("nightcap", "nightcap-couch-race"):
        legacy = load_arc_definition(arc_id)
        assert legacy is not None and not legacy.is_phased


def synthetic_case(tmp_path: Path) -> Path:
    fixture = json.loads(VALID_CASE.read_text(encoding="utf-8"))
    mapped = dict(zip(("beat_one", "beat_two", "beat_three"), ROUNDS[:3], strict=True))
    for opportunity in fixture["opportunities"]:
        beats = [mapped[beat] for beat in opportunity["beats"]]
        if "round_3" in beats:
            beats.append("round_4")
        opportunity["beats"] = beats
    path = tmp_path / "case.json"
    path.write_text(json.dumps(fixture), encoding="utf-8")
    return path


@pytest.mark.asyncio
@pytest.mark.parametrize("players", [2, 4])
async def test_1a_plays_through_final_race_and_uses_its_standing(
    db: AsyncSession,
    registered: Callable[[ArcDefinition], None],
    monkeypatch: pytest.MonkeyPatch,
    no_model_calls: None,
    tmp_path: Path,
    players: int,
):
    arc = agency_arc().model_copy(update={"case_file": str(synthetic_case(tmp_path))})
    registered(arc)
    monkeypatch.setattr(
        "engine.session.mini_game_phase.build_registry", default_registry
    )
    seated = await seat_session(db, arc, players=players)
    rec = Recorder()
    now = at(0)
    await tick(db, seated.session_id, now, rec)
    played = []
    for round_id, slots in zip(ROUNDS, SLOTS, strict=True):
        for kind in ("scene", "choices", *("mini_game",) * slots):
            state = await current_phase(db, seated.session_id)
            assert state is not None and (state.beat_id, state.phase) == (
                round_id,
                kind,
            )
            if kind == "choices":
                for player in seated.participants:
                    if round_id == "round_1":
                        assert (
                            await remaining_budget(db, seated.session_id, player) == 6
                        )
                    if round_id in ("round_2", "round_3"):
                        opportunity = "o_bench" if round_id == "round_2" else "o_cellar"
                        await choose(
                            db,
                            seated.session_id,
                            player,
                            str(player) + opportunity,
                            opportunity,
                            now,
                            rec,
                        )
            if kind == "mini_game":
                game = MiniGameRuntime(
                    db, SessionEventBus(), default_registry(), clock=lambda: now
                )
                run = await game.get_active_run(seated.session_id)
                assert run is not None
                played.append(run)
                if round_id == "round_4":
                    await game.submit_action(
                        run.run_id, "winner", seated.characters[0], choice(0, "four")
                    )
                for _ in range(12):
                    if run.status in ("completed", "timed_out"):
                        break
                    now = aware(run.deadline) + timedelta(milliseconds=1)
                    await tick(db, seated.session_id, now, rec)
                assert run.status in ("completed", "timed_out")
                assert not run.clue_unlock_record["unlocked"]
            else:
                now = aware(state.deadline_at) + timedelta(milliseconds=1)
                await tick(db, seated.session_id, now, rec)
        if round_id != "round_4":
            state = await current_phase(db, seated.session_id)
            assert state is not None and state.phase == "bridge"
            now = aware(state.deadline_at) + timedelta(milliseconds=1)
            await tick(db, seated.session_id, now, rec)

    assert len(played) == 5
    assert await where(db, seated.session_id) == ("finale", "commit", "running")
    order = entered_once(await phase_order(db, seated.session_id))
    assert order[-2:] == [("round_4", "mini_game"), ("finale", "commit")]
    assert played[-1].outcome["standing"][0] == [str(seated.participants[0])]
    for player in seated.participants:
        await save_theory_draft(
            db,
            seated.session_id,
            player,
            {"slot_who": "marlowe", "slot_how": "c_how_true"},
            "c_how_true",
            now,
            rec,
        )
        await lock_theory(db, seated.session_id, player, now, rec)
    for kind in ("reveal", "scene", "result", "recap"):
        state = await current_phase(db, seated.session_id)
        assert state is not None and state.phase == kind
        now = aware(state.deadline_at) + timedelta(milliseconds=1)
        await tick(db, seated.session_id, now, rec)
    verdict = rec.of_type("endgame_result")[0].payload
    assert verdict["decided_by"] == "mini_game_wins"
    assert [winner["participant_id"] for winner in verdict["winners"]] == [
        str(seated.participants[0])
    ]
    assert await where(db, seated.session_id) == ("verdict", "recap", "ended")
