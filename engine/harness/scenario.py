"""Declarative scripted scenario support for harness runs."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from pydantic import BaseModel, Field

from engine.harness.models import HarnessAction, HarnessRun
from engine.harness.runner import HarnessRunner

ARC_PATH = Path(__file__).resolve().parents[2] / "nightcap" / "arc.json"


class ScenarioValidationError(Exception):
    """Raised when a scripted scenario fails validation before live execution."""


class SyntheticPlayer(BaseModel):
    player_id: str
    display_name: str
    is_killer: bool = False


class ScenarioStep(BaseModel):
    actor_id: str
    action_type: str
    payload: dict[str, Any] = Field(default_factory=dict)
    expected_beat: str | None = None


class HarnessScenario(BaseModel):
    scenario_id: str
    seed: int
    players: list[SyntheticPlayer]
    steps: list[ScenarioStep]


class HarnessRunResult(BaseModel):
    scenario_id: str
    seed: int
    run: HarnessRun
    passed: bool
    failure_reason: str | None = None


class ScenarioExecutor:
    def __init__(
        self,
        *,
        arc_path: Path = ARC_PATH,
        runner_factory: Callable[[Path, int], HarnessRunner] | None = None,
        preflight_runner_factory: Callable[[Path, int], HarnessRunner] | None = None,
    ) -> None:
        self._arc_path = arc_path
        self._runner_factory = runner_factory
        self._preflight_runner_factory = preflight_runner_factory

    def run(self, scenario: HarnessScenario) -> HarnessRunResult:
        self._validate_structure(scenario)
        self._preflight_validate(scenario)

        runner = self._build_runner(scenario.seed)
        runner.start()
        runner.set_participants([player.player_id for player in scenario.players])

        try:
            self._execute_steps(runner, scenario.steps)
        except Exception as exc:
            return HarnessRunResult(
                scenario_id=scenario.scenario_id,
                seed=scenario.seed,
                run=runner.current_run(),
                passed=False,
                failure_reason=str(exc),
            )

        return HarnessRunResult(
            scenario_id=scenario.scenario_id,
            seed=scenario.seed,
            run=runner.current_run(),
            passed=True,
        )

    def _build_runner(self, seed: int, *, preflight: bool = False) -> HarnessRunner:
        factory = (
            self._preflight_runner_factory
            if preflight and self._preflight_runner_factory is not None
            else self._runner_factory
        )
        if factory is not None:
            return factory(self._arc_path, seed)
        return HarnessRunner(arc_path=self._arc_path, seed=seed)

    def _validate_structure(self, scenario: HarnessScenario) -> None:
        known_players = {player.player_id for player in scenario.players}
        allowed_actions = self._build_runner(
            scenario.seed, preflight=True
        ).transition_names
        errors: list[str] = []

        for step_index, step in enumerate(scenario.steps, start=1):
            if step.actor_id not in known_players:
                errors.append(f"step {step_index}: unknown actor_id {step.actor_id!r}")

            if not step.action_type.strip():
                errors.append(f"step {step_index}: action_type must be non-empty")
            elif step.action_type not in allowed_actions:
                errors.append(
                    f"step {step_index}: unknown action_type {step.action_type!r}"
                )

            if step.expected_beat is not None and not step.expected_beat.strip():
                errors.append(f"step {step_index}: expected_beat must be non-empty")

        if errors:
            raise ScenarioValidationError("\n".join(errors))

    def _preflight_validate(self, scenario: HarnessScenario) -> None:
        runner = self._build_runner(scenario.seed, preflight=True)
        runner.start()
        errors: list[str] = []

        for step_index, step in enumerate(scenario.steps, start=1):
            try:
                self._apply_step(runner, step_index, step)
            except ScenarioValidationError as exc:
                errors.append(str(exc))
                if step.expected_beat is None:
                    break

        if errors:
            raise ScenarioValidationError("\n".join(errors))

    def _execute_steps(
        self,
        runner: HarnessRunner,
        steps: list[ScenarioStep],
    ) -> None:
        for step_index, step in enumerate(steps, start=1):
            self._apply_step(runner, step_index, step)

    def _apply_step(
        self,
        runner: HarnessRunner,
        step_index: int,
        step: ScenarioStep,
    ) -> None:
        action = HarnessAction(
            transition_name=step.action_type,
            payload=step.payload,
        )
        try:
            trace_entry = runner.apply_action(action)
        except Exception as exc:
            raise ScenarioValidationError(
                f"step {step_index}: action {step.action_type!r} failed: {exc}"
            ) from exc

        if (
            step.expected_beat is not None
            and step.expected_beat not in trace_entry.to_configuration
        ):
            raise ScenarioValidationError(
                "step "
                f"{step_index}: expected beat {step.expected_beat!r}, "
                f"got {trace_entry.to_configuration!r}"
            )
