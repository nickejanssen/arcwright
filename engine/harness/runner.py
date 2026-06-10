"""Headless deterministic session runner for arc harness tests."""

from __future__ import annotations

import random
from pathlib import Path
from typing import Any, Callable, cast
from uuid import UUID

from engine.arc.arc_state import ArcStateChart
from engine.arc.models import ArcDefinition
from engine.harness.models import (
    HarnessAction,
    HarnessRun,
    HarnessSnapshot,
    HarnessTraceEntry,
)


class HarnessRunner:
    def __init__(
        self,
        *,
        arc_path: Path,
        seed: int,
        generate: Callable[..., Any] | None = None,
    ) -> None:
        self._arc_path = arc_path
        self._seed = seed
        self._rng = random.Random(seed)
        self._arc_definition = ArcDefinition.model_validate_json(
            arc_path.read_text(encoding="utf-8")
        )
        self._chart = ArcStateChart(self._arc_definition)
        self._run: HarnessRun | None = None
        self._generate = generate

    def start(self) -> HarnessRun:
        if self._run is not None:
            msg = "HarnessRunner.start() has already been called."
            raise RuntimeError(msg)
        self._run = HarnessRun(
            seed=self._seed,
            session_id=self._build_session_id(),
            arc_id=self._arc_definition.arc_id,
            configuration=sorted(self._chart.configuration_values),
            step_index=0,
            trace=[],
        )
        return self._run.model_copy(deep=True)

    def apply_action(self, action: HarnessAction) -> HarnessTraceEntry:
        run = self._require_run()
        from_configuration = sorted(self._chart.configuration_values)
        context_snapshot = dict(self._chart.session_context)
        try:
            self._apply_context_payload(action.payload)
            transition = self._resolve_transition(action.transition_name)
            transition()
            to_configuration = sorted(self._chart.configuration_values)
        except Exception:
            self._chart.session_context = context_snapshot
            raise
        if to_configuration == from_configuration:
            self._chart.session_context = context_snapshot

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

    def set_participants(self, participants: list[str]) -> HarnessRun:
        run = self._require_run()
        run.participants = list(participants)
        return run.model_copy(deep=True)

    def current_run(self) -> HarnessRun:
        run = self._require_run()
        return run.model_copy(deep=True)

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

    @property
    def transition_names(self) -> frozenset[str]:
        return self._chart.transition_names

    def _require_run(self) -> HarnessRun:
        if self._run is None:
            msg = "HarnessRunner.start() must be called before use."
            raise RuntimeError(msg)
        return self._run

    def _build_session_id(self) -> UUID:
        return UUID(int=self._rng.getrandbits(128), version=4)

    def _apply_context_payload(self, payload: dict[str, Any]) -> None:
        context = payload.get("context")
        if not isinstance(context, dict):
            return
        for key, value in context.items():
            if isinstance(key, str):
                self._chart.update_context(key, value)

    def _resolve_transition(self, transition_name: str) -> Callable[[], Any]:
        if transition_name not in self._chart.transition_names:
            msg = f"Unknown transition: {transition_name!r}"
            raise ValueError(msg)
        transition = getattr(self._chart, transition_name, None)
        if not callable(transition):
            msg = f"Unknown transition: {transition_name!r}"
            raise ValueError(msg)
        return cast(Callable[[], Any], transition)
