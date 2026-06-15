"""Tests for engine/harness/scenario.py."""

from __future__ import annotations

from pathlib import Path

import pytest

from engine.arc import transition_name_for
from engine.harness import (
    HarnessRunner,
    HarnessScenario,
    ScenarioExecutor,
    ScenarioStep,
    ScenarioValidationError,
    SyntheticPlayer,
)

ARC_PATH = Path(__file__).parents[2] / "nightcap" / "arc.json"

BEAT_SEQUENCE = [
    "arrival",
    "body",
    "opening_move",
    "dig",
    "thread",
    "reckoning",
    "close",
    "truth",
]
EXIT_CONDITIONS = {
    "arrival": "all_players_ready",
    "body": "body_discovered",
    "opening_move": "private_clues_distributed",
    "dig": "killer_revealed_to_themselves",
    "thread": "first_convergence_reached",
    "reckoning": "accusations_resolved",
    "close": "final_accusation_committed",
}

ARRIVAL_TO_BODY = transition_name_for("arrival", "body")
CLOSE_TO_TRUTH = transition_name_for("close", "truth")


def _players() -> list[SyntheticPlayer]:
    return [
        SyntheticPlayer(player_id="player-a", display_name="Player A"),
        SyntheticPlayer(player_id="player-b", display_name="Player B"),
        SyntheticPlayer(player_id="player-c", display_name="Player C"),
        SyntheticPlayer(player_id="player-d", display_name="Player D"),
    ]


def _happy_path_steps(players: list[SyntheticPlayer]) -> list[ScenarioStep]:
    steps: list[ScenarioStep] = []
    for index, source_beat in enumerate(BEAT_SEQUENCE[:-1]):
        target_beat = BEAT_SEQUENCE[index + 1]
        actor = players[index % len(players)].player_id
        steps.append(
            ScenarioStep(
                actor_id=actor,
                action_type=transition_name_for(source_beat, target_beat),
                payload={"context": {EXIT_CONDITIONS[source_beat]: True}},
                expected_beat=target_beat,
            )
        )
    return steps


def _happy_path_scenario(seed: int = 111) -> HarnessScenario:
    players = _players()
    return HarnessScenario(
        scenario_id="nightcap-happy-path",
        seed=seed,
        players=players,
        steps=_happy_path_steps(players),
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
                action_type=ARRIVAL_TO_BODY,
                payload={"context": {"all_players_ready": True}},
                expected_beat="truth",
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
        match=r"step 1: expected beat 'truth', got \['body'\]",
    ):
        executor.run(scenario)

    assert starts == [111]


def test_unenabled_transition_fails_before_real_run_starts() -> None:
    starts: list[int] = []

    class TrackingRunner(HarnessRunner):
        def start(self):  # type: ignore[override]
            starts.append(self._seed)
            return super().start()

    scenario = HarnessScenario(
        scenario_id="blocked-transition",
        seed=111,
        players=_players(),
        steps=[
            ScenarioStep(
                actor_id="player-a",
                action_type=ARRIVAL_TO_BODY,
                expected_beat="body",
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

    with pytest.raises(ScenarioValidationError, match="is not enabled"):
        executor.run(scenario)

    assert starts == [111]


def test_happy_path_scenario_completes_truth() -> None:
    scenario = _happy_path_scenario()

    result = ScenarioExecutor(arc_path=ARC_PATH).run(scenario)

    assert result.passed is True
    assert result.failure_reason is None
    assert result.run.configuration == ["truth"]
    assert result.run.step_index == 7


def test_live_run_expected_beat_assertion_is_enforced() -> None:
    class DivergentRunner(HarnessRunner):
        def apply_action(self, action):  # type: ignore[override]
            entry = super().apply_action(action)
            if action.transition_name == ARRIVAL_TO_BODY:
                entry.to_configuration = ["unexpected"]
            return entry

    scenario = HarnessScenario(
        scenario_id="live-run-beat-check",
        seed=111,
        players=_players(),
        steps=[
            ScenarioStep(
                actor_id="player-a",
                action_type=ARRIVAL_TO_BODY,
                payload={"context": {"all_players_ready": True}},
                expected_beat="body",
            )
        ],
    )

    executor = ScenarioExecutor(
        arc_path=ARC_PATH,
        runner_factory=lambda arc_path, seed: DivergentRunner(
            arc_path=arc_path,
            seed=seed,
        ),
        preflight_runner_factory=lambda arc_path, seed: HarnessRunner(
            arc_path=arc_path,
            seed=seed,
        ),
    )

    result = executor.run(scenario)

    assert result.passed is False
    assert result.failure_reason == "step 1: expected beat 'body', got ['unexpected']"


def test_same_scenario_same_seed_produces_identical_trace() -> None:
    scenario = _happy_path_scenario()
    executor = ScenarioExecutor(arc_path=ARC_PATH)

    first_result = executor.run(scenario)
    second_result = executor.run(scenario)

    assert first_result.run.trace == second_result.run.trace
    assert first_result.run.session_id == second_result.run.session_id


def test_participant_ids_are_stable_across_runs() -> None:
    scenario = _happy_path_scenario()
    executor = ScenarioExecutor(arc_path=ARC_PATH)

    first_result = executor.run(scenario)
    second_result = executor.run(scenario)

    assert first_result.run.participants == second_result.run.participants


def test_run_participants_match_input_order() -> None:
    scenario = _happy_path_scenario()

    result = ScenarioExecutor(arc_path=ARC_PATH).run(scenario)

    assert result.run.participants == [player.player_id for player in scenario.players]
