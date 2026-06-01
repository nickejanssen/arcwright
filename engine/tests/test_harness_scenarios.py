"""Tests for engine/harness/scenario.py."""

from __future__ import annotations

from pathlib import Path

import pytest

from engine.harness import (
    HarnessRunner,
    HarnessScenario,
    ScenarioExecutor,
    ScenarioStep,
    ScenarioValidationError,
    SyntheticPlayer,
)

ARC_PATH = Path(__file__).parents[2] / "nightcap" / "arc.json"


def _players() -> list[SyntheticPlayer]:
    return [
        SyntheticPlayer(player_id="player-a", display_name="Player A"),
        SyntheticPlayer(player_id="player-b", display_name="Player B"),
        SyntheticPlayer(player_id="player-c", display_name="Player C"),
        SyntheticPlayer(player_id="player-d", display_name="Player D"),
    ]


def _happy_path_scenario() -> HarnessScenario:
    players = _players()
    return HarnessScenario(
        scenario_id="nightcap-happy-path",
        seed=111,
        players=players,
        steps=[
            ScenarioStep(
                actor_id=players[0].player_id,
                action_type="begin_game",
                expected_beat="killer_assignment",
            ),
            ScenarioStep(
                actor_id=players[1].player_id,
                action_type="motives_established",
                expected_beat="motive_reveal",
            ),
            ScenarioStep(
                actor_id=players[2].player_id,
                action_type="investigation_begins",
                expected_beat="investigation",
            ),
            ScenarioStep(
                actor_id=players[0].player_id,
                action_type="clues_sent",
                expected_beat="distributed",
            ),
            ScenarioStep(
                actor_id=players[1].player_id,
                action_type="interrogation_complete",
                expected_beat="closed",
            ),
            ScenarioStep(
                actor_id=players[2].player_id,
                action_type="phases_complete",
                expected_beat="resolution",
            ),
            ScenarioStep(
                actor_id=players[3].player_id,
                action_type="accusation_filed",
                expected_beat="reveal",
            ),
        ],
    )


def test_scenario_validation_rejects_unknown_actor() -> None:
    scenario = HarnessScenario(
        scenario_id="unknown-actor",
        seed=111,
        players=_players(),
        steps=[ScenarioStep(actor_id="missing-player", action_type="begin_game")],
    )

    with pytest.raises(ScenarioValidationError, match="unknown actor_id"):
        ScenarioExecutor(arc_path=ARC_PATH).run(scenario)


def test_scenario_validation_rejects_empty_action_type() -> None:
    scenario = HarnessScenario(
        scenario_id="empty-action",
        seed=111,
        players=_players(),
        steps=[ScenarioStep(actor_id="player-a", action_type="   ")],
    )

    with pytest.raises(ScenarioValidationError, match="action_type must be non-empty"):
        ScenarioExecutor(arc_path=ARC_PATH).run(scenario)


def test_scenario_validation_rejects_unknown_action_type() -> None:
    scenario = HarnessScenario(
        scenario_id="unknown-action",
        seed=111,
        players=_players(),
        steps=[ScenarioStep(actor_id="player-a", action_type="unknown_transition")],
    )

    with pytest.raises(ScenarioValidationError, match="unknown action_type"):
        ScenarioExecutor(arc_path=ARC_PATH).run(scenario)


def test_expected_beat_assertion_fails_before_real_run_starts() -> None:
    starts: list[int] = []

    class TrackingRunner(HarnessRunner):
        def start(self):  # type: ignore[override]
            starts.append(self._seed)
            return super().start()

    scenario = HarnessScenario(
        scenario_id="wrong-beat",
        seed=111,
        players=_players(),
        steps=[
            ScenarioStep(
                actor_id="player-a",
                action_type="begin_game",
                expected_beat="reveal",
            )
        ],
    )

    executor = ScenarioExecutor(
        arc_path=ARC_PATH,
        runner_factory=lambda arc_path, seed: TrackingRunner(
            arc_path=arc_path,
            seed=seed,
        ),
    )

    with pytest.raises(
        ScenarioValidationError,
        match=r"step 1: expected beat 'reveal', got \['introduction', 'killer_assignment'\]",
    ):
        executor.run(scenario)

    assert starts == [111]


def test_happy_path_scenario_completes_reveal() -> None:
    scenario = _happy_path_scenario()

    result = ScenarioExecutor(arc_path=ARC_PATH).run(scenario)

    assert result.passed is True
    assert result.failure_reason is None
    assert result.run.configuration == ["reveal"]
    assert result.run.step_index == 7


def test_same_scenario_same_seed_produces_identical_trace() -> None:
    scenario = _happy_path_scenario()
    executor = ScenarioExecutor(arc_path=ARC_PATH)

    first_result = executor.run(scenario)
    second_result = executor.run(scenario)

    assert first_result.run.trace == second_result.run.trace
    assert first_result.run.session_id == second_result.run.session_id


def test_run_participants_match_input_order() -> None:
    scenario = _happy_path_scenario()

    result = ScenarioExecutor(arc_path=ARC_PATH).run(scenario)

    assert result.run.participants == [
        "player-a",
        "player-b",
        "player-c",
        "player-d",
    ]
