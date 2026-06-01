"""Headless deterministic session runner for arc harness tests."""

from __future__ import annotations

import random
from pathlib import Path
from uuid import uuid4

from engine.arc.arc_state import ArcStateChart
from engine.arc.models import ArcDefinition
from engine.harness.models import (
    HarnessAction,
    HarnessRun,
    HarnessSnapshot,
    HarnessTraceEntry,
)
from engine.routing.logging import generate as default_generate


class HarnessRunner:
    def __init__(self, *, arc_path: Path, seed: int) -> None:
        self._arc_path = arc_path
        self._seed = seed
        self._rng = random.Random(seed)
        self._arc_definition = ArcDefinition.model_validate_json(
            arc_path.read_text(encoding="utf-8")
        )
        self._chart = ArcStateChart(self._arc_definition)
        self._run: HarnessRun | None = None
        self._generate = default_generate

    def start(self) -> HarnessRun:
        if self._run is None:
            self._run = HarnessRun(
                seed=self._seed,
                session_id=uuid4(),
                arc_id=self._arc_definition.arc_id,
                configuration=sorted(self._chart.configuration_values),
                step_index=0,
                trace=[],
            )
        return self._run.model_copy(deep=True)

    def apply_action(self, action: HarnessAction) -> HarnessTraceEntry:
        run = self._require_run()
        from_configuration = sorted(self._chart.configuration_values)
        getattr(self._chart, action.transition_name)()
        to_configuration = sorted(self._chart.configuration_values)

        step_index = run.step_index + 1
        entry = HarnessTraceEntry(
            step_index=step_index,
            transition_name=action.transition_name,
            from_configuration=from_configuration,
            to_configuration=to_configuration,
            payload=action.payload,
        )
        run.step_index = step_index
        run.configuration = to_configuration
        run.trace.append(entry)
        return entry.model_copy(deep=True)

    def snapshot(self) -> HarnessSnapshot:
        run = self._require_run()
        return HarnessSnapshot(
            step_index=run.step_index,
            configuration=sorted(self._chart.configuration_values),
            seed=run.seed,
            session_id=run.session_id,
        )

    def trace(self) -> list[HarnessTraceEntry]:
        run = self._require_run()
        return [entry.model_copy(deep=True) for entry in run.trace]

    def _require_run(self) -> HarnessRun:
        if self._run is None:
            msg = "HarnessRunner.start() must be called before use."
            raise RuntimeError(msg)
        return self._run
