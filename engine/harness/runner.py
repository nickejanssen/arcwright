"""Headless deterministic session runner for arc harness tests."""

from __future__ import annotations

import random
from pathlib import Path
from typing import Any, Callable, Literal, cast
from uuid import UUID

from engine.arc.arc_state import ArcStateChart, transition_name_for
from engine.arc.models import ArcDefinition, PlayMode
from engine.harness.models import (
    HarnessAction,
    HarnessRun,
    HarnessSnapshot,
    HarnessTraceEntry,
)
from engine.session import SessionRuntimeState, TransitionBypassLogEntry

_HOST_BYPASS_KEY = "host_bypass"
_HOST_ROLE = "host"
_KILLER_ROLE = "killer"
_KILLER_ASSIGNMENT_KEY = "killer_assignment"
_REVEAL_BEAT_ID = "truth"


class HarnessRunner:
    def __init__(
        self,
        *,
        arc_path: Path | None = None,
        arc_definition: ArcDefinition | None = None,
        seed: int,
        generate: Callable[..., Any] | None = None,
    ) -> None:
        if arc_definition is not None:
            self._arc_definition = arc_definition
        elif arc_path is not None:
            self._arc_definition = ArcDefinition.model_validate_json(
                arc_path.read_text(encoding="utf-8")
            )
        else:
            msg = "HarnessRunner requires either arc_path or arc_definition."
            raise ValueError(msg)
        self._seed = seed
        self._rng = random.Random(seed)
        self._chart = ArcStateChart(self._arc_definition)
        self._assignment_rng = random.Random(seed)
        self._transition_edges = self._build_transition_edges()
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
            runtime_state=SessionRuntimeState(seed=self._seed),
            trace=[],
        )
        return self._run.model_copy(deep=True)

    def apply_action(self, action: HarnessAction) -> HarnessTraceEntry:
        run = self._require_run()
        from_configuration = sorted(self._chart.configuration_values)
        context_snapshot = dict(self._chart.session_context)
        runtime_state_snapshot = run.runtime_state.model_copy(deep=True)
        try:
            self._apply_context_payload(action.payload)
            transition = self._resolve_transition(action.transition_name)
            transition_edge = self._transition_edges[action.transition_name]
            has_host_bypass = self._has_host_bypass_payload(action.payload)
            if has_host_bypass:
                self._validate_host_bypass_payload(action.payload)
            if action.transition_name in self._enabled_transition_names():
                transition()
                to_configuration = sorted(self._chart.configuration_values)
                self._record_reveal_if_needed(transition_edge[1], "authored_conditions")
            elif has_host_bypass:
                to_configuration = self._apply_host_bypass(
                    action,
                    transition,
                    transition_edge,
                )
            else:
                msg = (
                    f"Transition {action.transition_name!r} is not enabled "
                    f"from configuration {from_configuration!r}"
                )
                raise ValueError(msg)
        except Exception:
            self._chart.session_context = context_snapshot
            run.runtime_state = runtime_state_snapshot
            raise

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
        self._resolve_introduction_setup()
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

    def context_value(self, key: str, default: Any = None) -> Any:
        self._require_run()
        return self._chart.get_context(key, default)

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

    def _build_transition_edges(self) -> dict[str, tuple[str, str]]:
        return {
            transition_name_for(source_beat_id, target_beat_id): (
                source_beat_id,
                target_beat_id,
            )
            for source_beat_id, target_beat_ids in self._arc_definition.beat_graph.items()
            for target_beat_id in target_beat_ids
        }

    def _resolve_introduction_setup(self) -> None:
        run = self._require_run()
        arc = self._arc_definition
        if arc.play_mode == PlayMode.detective_race:
            self._resolve_case_for_detective_race(run)
            return
        if not arc.generative_elements.killer_assignment:
            return
        if _KILLER_ROLE in run.runtime_state.role_assignments:
            return
        if not run.participants:
            return
        initial_beat_id = arc.beats[0].beat_id
        if sorted(self._chart.configuration_values) != [initial_beat_id]:
            msg = f"killer assignment must resolve during the initial beat ({initial_beat_id!r})."
            raise RuntimeError(msg)

        assigned_participant = self._assignment_rng.choice(run.participants)
        run.runtime_state.role_assignments[_KILLER_ROLE] = assigned_participant
        run.runtime_state.resolved_generative_elements[_KILLER_ASSIGNMENT_KEY] = {
            "role": _KILLER_ROLE,
            "participant_id": assigned_participant,
            "seed": self._seed,
            "candidate_participants": list(run.participants),
        }

    def _resolve_case_for_detective_race(self, run: HarnessRun) -> None:
        if "case_resolution" in run.runtime_state.resolved_generative_elements:
            return
        if not run.participants:
            return
        # engine/case is a sibling module; import lazily to avoid a cycle
        # when engine.harness is imported at engine.arc load time.
        from engine.case import resolve as resolve_case

        case = resolve_case(
            self._arc_definition,
            seed=self._seed,
            participant_count=len(run.participants),
        )
        victim_members = case.members_by_role("victim")
        run.runtime_state.resolved_generative_elements["case_resolution"] = {
            "case_id": case.case_id,
            "arc_id": case.arc_id,
            "seed": case.seed,
            "skeleton_id": case.skeleton_id,
            "culprit_id": case.culprit_id,
            # Nightcap arc-content record; not part of engine/case schema.
            "victim_id": victim_members[0].member_id if victim_members else None,
            "cast_size": len([m for m in case.cast if m.role == "suspect"]),
            "evidence_count": len(case.evidence),
            "falsehood_count": len(case.falsehoods),
        }

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

    def _enabled_transition_names(self) -> set[str]:
        return {event.id for event in self._chart.enabled_events()}

    def _has_host_bypass_payload(self, payload: dict[str, Any]) -> bool:
        return _HOST_BYPASS_KEY in payload

    def _apply_host_bypass(
        self,
        action: HarnessAction,
        transition: Callable[[], Any],
        transition_edge: tuple[str, str],
    ) -> list[str]:
        run = self._require_run()
        source_beat_id, target_beat_id = transition_edge
        if target_beat_id != _REVEAL_BEAT_ID:
            msg = "host bypass is only supported for the truth reveal transition."
            raise ValueError(msg)

        actor_id, reason = self._validate_host_bypass_payload(action.payload)
        bypassed_conditions = self._unmet_transition_conditions(transition_edge)
        if not bypassed_conditions:
            msg = "host bypass requires at least one unmet authored condition."
            raise ValueError(msg)

        context_after_payload = dict(self._chart.session_context)
        for condition in bypassed_conditions:
            self._chart.update_context(condition, True)

        try:
            transition()
        finally:
            self._chart.session_context = context_after_payload

        sequence = len(run.runtime_state.transition_bypass_log) + 1
        bypass_entry = TransitionBypassLogEntry(
            sequence=sequence,
            actor_id=actor_id,
            reason=reason,
            source_transition=action.transition_name,
            source_beat_id=source_beat_id,
            target_beat_id=target_beat_id,
            bypassed_conditions=bypassed_conditions,
        )
        run.runtime_state.transition_bypass_log.append(bypass_entry)
        self._record_reveal_if_needed(
            target_beat_id,
            "host_bypass",
            bypass_sequence=sequence,
        )
        return sorted(self._chart.configuration_values)

    def _validate_host_bypass_payload(self, payload: dict[str, Any]) -> tuple[str, str]:
        bypass_payload = payload.get(_HOST_BYPASS_KEY)
        if not isinstance(bypass_payload, dict):
            msg = "host bypass payload must be an object."
            raise ValueError(msg)

        actor_id = bypass_payload.get("actor_id")
        actor_role = bypass_payload.get("actor_role")
        reason = bypass_payload.get("reason")

        if actor_role != _HOST_ROLE:
            msg = "host bypass requires actor_role='host'."
            raise ValueError(msg)
        if not isinstance(actor_id, str) or not actor_id.strip():
            msg = "host bypass requires a non-empty actor_id."
            raise ValueError(msg)
        if not isinstance(reason, str) or not reason.strip():
            msg = "host bypass requires a non-empty reason."
            raise ValueError(msg)

        return actor_id, reason

    def _unmet_transition_conditions(
        self,
        transition_edge: tuple[str, str],
    ) -> list[str]:
        source_beat_id, target_beat_id = transition_edge
        beats_by_id = {beat.beat_id: beat for beat in self._arc_definition.beats}
        required_conditions = [
            *beats_by_id[source_beat_id].exit_conditions,
            *beats_by_id[target_beat_id].entry_conditions,
        ]
        unmet_conditions: list[str] = []
        seen: set[str] = set()
        for condition in required_conditions:
            if condition in seen or self._chart.session_context.get(condition):
                continue
            seen.add(condition)
            unmet_conditions.append(condition)
        return unmet_conditions

    def _record_reveal_if_needed(
        self,
        target_beat_id: str,
        revealed_by: Literal["authored_conditions", "host_bypass"],
        *,
        bypass_sequence: int | None = None,
    ) -> None:
        if target_beat_id != _REVEAL_BEAT_ID:
            return
        run = self._require_run()
        run.runtime_state.reveal_state.is_revealed = True
        run.runtime_state.reveal_state.revealed_by = revealed_by
        run.runtime_state.reveal_state.bypass_sequence = bypass_sequence
