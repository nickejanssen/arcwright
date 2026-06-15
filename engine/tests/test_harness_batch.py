"""Tests for deterministic harness replay and batch execution."""

from __future__ import annotations

from pathlib import Path

from engine.arc import transition_name_for
from engine.harness import (
    BatchRunner,
    HarnessScenario,
    HarnessTraceEntry,
    ScenarioExecutor,
    ScenarioStep,
    SyntheticPlayer,
    canonicalize_trace,
    traces_equal,
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


class DebugTraceEntry(HarnessTraceEntry):
    debug_label: str | None = None
    elapsed_seconds: float | None = None


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


def test_canonicalize_trace_keeps_structural_fields() -> None:
    trace = [
        DebugTraceEntry(
            step_index=1,
            transition_name=ARRIVAL_TO_BODY,
            from_configuration=["arrival"],
            to_configuration=["body"],
            payload={"source": "scripted"},
            debug_label="ignored",
            elapsed_seconds=1.23,
        )
    ]

    canonical = canonicalize_trace(trace)

    assert canonical == [
        {
            "step_index": 1,
            "transition_name": ARRIVAL_TO_BODY,
            "from_configuration": ["arrival"],
            "to_configuration": ["body"],
            "payload": {"source": "scripted"},
        }
    ]


def test_canonicalize_trace_strips_debug_fields() -> None:
    trace = [
        DebugTraceEntry(
            step_index=7,
            transition_name=CLOSE_TO_TRUTH,
            from_configuration=["close"],
            to_configuration=["truth"],
            payload={"source": "scripted"},
            debug_label="debug-only",
            elapsed_seconds=4.56,
        )
    ]

    canonical = canonicalize_trace(trace)

    assert set(canonical[0]) == {
        "step_index",
        "transition_name",
        "from_configuration",
        "to_configuration",
        "payload",
    }
    assert "debug_label" not in canonical[0]
    assert "elapsed_seconds" not in canonical[0]


def test_same_seed_produces_equal_traces() -> None:
    scenario = _happy_path_scenario(seed=222)
    executor = ScenarioExecutor(arc_path=ARC_PATH)

    first_result = executor.run(scenario)
    second_result = executor.run(scenario)

    assert first_result.passed is True
    assert second_result.passed is True
    assert traces_equal(first_result.run.trace, second_result.run.trace) is True


def test_batch_runner_executes_ten_runs() -> None:
    scenario = _happy_path_scenario()
    runner = BatchRunner(
        executor_factory=lambda: ScenarioExecutor(arc_path=ARC_PATH),
    )

    summary = runner.run(scenario, runs=10, base_seed=0)

    assert summary.scenario_id == scenario.scenario_id
    assert summary.total_runs == 10
    assert summary.passed == 10
    assert summary.failed == 0
    assert len(summary.results) == 10
    assert all(result.passed is True for result in summary.results)
    assert all(result.failure_reason is None for result in summary.results)


def test_batch_runner_seeds_incrementally() -> None:
    scenario = _happy_path_scenario()
    base_seed = 7
    runner = BatchRunner(
        executor_factory=lambda: ScenarioExecutor(arc_path=ARC_PATH),
    )

    summary = runner.run(scenario, runs=10, base_seed=base_seed)

    assert [result.seed for result in summary.results] == list(range(base_seed, 17))


def test_batch_runner_records_executor_exceptions_as_failed_runs() -> None:
    scenario = _happy_path_scenario()

    class FailingExecutor:
        def run(self, scenario: HarnessScenario):  # type: ignore[no-untyped-def]
            raise RuntimeError(f"seed {scenario.seed} failed preflight")

    runner = BatchRunner(executor_factory=lambda: FailingExecutor())

    summary = runner.run(scenario, runs=2, base_seed=3)

    assert summary.total_runs == 2
    assert summary.passed == 0
    assert summary.failed == 2
    assert [result.seed for result in summary.results] == [3, 4]
    assert all(result.passed is False for result in summary.results)
    assert (
        summary.results[0].failure_reason
        == "first execution failed: seed 3 failed preflight"
    )
    assert (
        summary.results[1].failure_reason
        == "first execution failed: seed 4 failed preflight"
    )
