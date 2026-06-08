"""Headless batch execution for deterministic harness scenarios."""

from __future__ import annotations

from itertools import zip_longest
from typing import Callable

from pydantic import BaseModel

from engine.harness.replay import canonicalize_trace, traces_equal
from engine.harness.scenario import HarnessRunResult, HarnessScenario, ScenarioExecutor


class BatchRunResult(BaseModel):
    run_index: int
    seed: int
    scenario_id: str
    passed: bool
    failure_reason: str | None = None


class BatchSummary(BaseModel):
    scenario_id: str
    total_runs: int
    passed: int
    failed: int
    results: list[BatchRunResult]


class BatchRunner:
    def __init__(
        self,
        *,
        executor_factory: Callable[[], ScenarioExecutor] | None = None,
    ) -> None:
        self._executor_factory = executor_factory

    def run(
        self,
        scenario: HarnessScenario,
        *,
        runs: int,
        base_seed: int,
    ) -> BatchSummary:
        results: list[BatchRunResult] = []

        for run_index in range(runs):
            seed = base_seed + run_index
            seeded_scenario = scenario.model_copy(update={"seed": seed}, deep=True)
            first_result = self._build_executor().run(seeded_scenario)
            second_result = self._build_executor().run(seeded_scenario)

            passed = (
                first_result.passed
                and second_result.passed
                and traces_equal(first_result.run.trace, second_result.run.trace)
            )
            failure_reason = None
            if not passed:
                failure_reason = self._build_failure_reason(
                    first_result,
                    second_result,
                )

            results.append(
                BatchRunResult(
                    run_index=run_index,
                    seed=seed,
                    scenario_id=scenario.scenario_id,
                    passed=passed,
                    failure_reason=failure_reason,
                )
            )

        passed_count = sum(result.passed for result in results)
        return BatchSummary(
            scenario_id=scenario.scenario_id,
            total_runs=runs,
            passed=passed_count,
            failed=runs - passed_count,
            results=results,
        )

    def _build_executor(self) -> ScenarioExecutor:
        if self._executor_factory is not None:
            return self._executor_factory()
        return ScenarioExecutor()

    def _build_failure_reason(
        self,
        first_result: HarnessRunResult,
        second_result: HarnessRunResult,
    ) -> str:
        if not first_result.passed:
            return f"first execution failed: {first_result.failure_reason or 'unknown error'}"
        if not second_result.passed:
            return f"second execution failed: {second_result.failure_reason or 'unknown error'}"

        first_trace = canonicalize_trace(first_result.run.trace)
        second_trace = canonicalize_trace(second_result.run.trace)

        for step_index, (left_entry, right_entry) in enumerate(
            zip_longest(first_trace, second_trace, fillvalue=None),
            start=1,
        ):
            if left_entry == right_entry:
                continue
            return (
                f"canonical trace mismatch at step {step_index}: "
                f"left={left_entry!r} right={right_entry!r}"
            )

        return "canonical trace mismatch"


__all__ = [
    "BatchRunResult",
    "BatchRunner",
    "BatchSummary",
]
