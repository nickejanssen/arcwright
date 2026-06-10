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
INTRO_TO_INVESTIGATION = transition_name_for("introduction", "investigation")
INVESTIGATION_TO_REVEAL = transition_name_for("investigation", "reveal")
READY_CONTEXT = {"context": {"all_players_ready": True}}
REVEAL_CONTEXT = {"context": {"core_clues_revealed": True}}


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


def _happy_path_scenario(seed: int = 111) -> HarnessScenario:
    players = _players()
    return HarnessScenario(
        scenario_id="nightcap-happy-path",
        seed=seed,
        players=players,
        steps=[
            ScenarioStep(
                actor_id=players[0].player_id,
                action_type=INTRO_TO_INVESTIGATION,
                payload=READY_CONTEXT,
                expected_beat="investigation",
            ),
            ScenarioStep(
                actor_id=players[1].player_id,
                action_type=INVESTIGATION_TO_REVEAL,
                payload=REVEAL_CONTEXT,
                expected_beat="reveal",
            ),
        ],
    )


def test_canonicalize_trace_keeps_structural_fields() -> None:
    trace = [
        DebugTraceEntry(
            step_index=1,
            transition_name=INTRO_TO_INVESTIGATION,
            from_configuration=["introduction"],
            to_configuration=["investigation"],
            payload={"source": "scripted"},
            debug_label="ignored",
            elapsed_seconds=1.23,
        )
    ]

    canonical = canonicalize_trace(trace)

    assert canonical == [
        {
            "step_index": 1,
            "transition_name": INTRO_TO_INVESTIGATION,
            "from_configuration": ["introduction"],
            "to_configuration": ["investigation"],
            "payload": {"source": "scripted"},
        }
    ]


def test_canonicalize_trace_strips_debug_fields() -> None:
    trace = [
        DebugTraceEntry(
            step_index=2,
            transition_name=INVESTIGATION_TO_REVEAL,
            from_configuration=["investigation"],
            to_configuration=["reveal"],
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
