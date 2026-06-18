"""Generated StateChart runtime for authored arc beat graphs."""

from __future__ import annotations

import logging
import re
from typing import Any, Callable, Dict, Type

from statemachine import State, StateChart

from engine.arc.models import ArcDefinition, BeatDefinition

logger = logging.getLogger(__name__)

_IDENTIFIER_PATTERN = re.compile(r"[^0-9a-zA-Z_]+")


class GeneratedArcStateChart(StateChart[Any]):
    """Base behavior shared by generated arc StateChart subclasses."""

    arc_definition: ArcDefinition
    session_context: Dict[str, Any]
    transition_names: frozenset[str]

    def __init__(self, arc_definition: ArcDefinition, *, start_value: Any = None):
        self.arc_definition = arc_definition
        self.session_context = {}
        super().__init__(start_value=start_value)
        logger.info("Generated ArcStateChart initialized")

    def update_context(self, key: str, value: Any) -> None:
        self.session_context[key] = value
        logger.debug("ArcStateChart context updated: %s = %s", key, value)

    def get_context(self, key: str, default: Any = None) -> Any:
        return self.session_context.get(key, default)

    def satisfy_condition(self, condition: str) -> None:
        self.update_context(condition, True)

    def clear_condition(self, condition: str) -> None:
        self.update_context(condition, False)

    def _conditions_satisfied(self, conditions: list[str]) -> bool:
        return all(
            bool(self.session_context.get(condition)) for condition in conditions
        )


def ArcStateChart(
    arc_definition: ArcDefinition, *, start_value: Any = None
) -> GeneratedArcStateChart:
    """Instantiate a StateChart generated from an arc definition.

    ``start_value`` is forwarded to the underlying ``StateChart`` to resume
    an existing session at a specific beat boundary; defaults to the first
    beat in the definition for fresh sessions.
    """

    chart_class = build_arc_state_chart_class(arc_definition)
    return chart_class(arc_definition, start_value=start_value)


def build_arc_state_chart_class(
    arc_definition: ArcDefinition,
) -> Type[GeneratedArcStateChart]:
    """Build a StateChart subclass from ArcDefinition beat graph data."""

    beats_by_id = {beat.beat_id: beat for beat in arc_definition.beats}
    state_attrs = _build_state_attributes(arc_definition)
    transition_attrs, transition_names = _build_transition_attributes(
        arc_definition,
        beats_by_id,
        state_attrs,
    )
    class_name = f"{_to_identifier(arc_definition.arc_id, 'arc')}_ArcStateChart"
    return type(
        class_name,
        (GeneratedArcStateChart,),
        {
            **state_attrs,
            **transition_attrs,
            "transition_names": frozenset(transition_names),
        },
    )


def transition_name_for(source_beat_id: str, target_beat_id: str) -> str:
    return (
        f"advance_{_to_identifier(source_beat_id, 'beat')}"
        f"_to_{_to_identifier(target_beat_id, 'beat')}"
    )


def _build_state_attributes(arc_definition: ArcDefinition) -> dict[str, State]:
    attrs: dict[str, State] = {}
    used_names: set[str] = set()
    initial_beat_id = arc_definition.beats[0].beat_id
    for beat in arc_definition.beats:
        attr_name = _unique_identifier(beat.beat_id, "beat", used_names)
        attrs[attr_name] = State(
            beat.beat_name,
            value=beat.beat_id,
            initial=beat.beat_id == initial_beat_id,
            final=not arc_definition.beat_graph.get(beat.beat_id),
        )
    return attrs


def _build_transition_attributes(
    arc_definition: ArcDefinition,
    beats_by_id: dict[str, BeatDefinition],
    states_by_attr: dict[str, State],
) -> tuple[dict[str, Any], set[str]]:
    states_by_beat_id = {state.value: state for state in states_by_attr.values()}
    attrs: dict[str, Any] = {}
    transition_names: set[str] = set()
    for source_beat_id, target_beat_ids in arc_definition.beat_graph.items():
        for target_beat_id in target_beat_ids:
            event_name = transition_name_for(source_beat_id, target_beat_id)
            if event_name in transition_names:
                msg = f"duplicate generated transition: {event_name}"
                raise ValueError(msg)
            guard_name = f"can_{event_name}"
            source_beat = beats_by_id[source_beat_id]
            target_beat = beats_by_id[target_beat_id]
            attrs[guard_name] = _make_guard(source_beat, target_beat)
            attrs[event_name] = states_by_beat_id[source_beat_id].to(
                states_by_beat_id[target_beat_id],
                cond=guard_name,
            )
            transition_names.add(event_name)
    return attrs, transition_names


def _make_guard(
    source_beat: BeatDefinition, target_beat: BeatDefinition
) -> Callable[[GeneratedArcStateChart], bool]:
    def guard(self: GeneratedArcStateChart) -> bool:
        return self._conditions_satisfied(
            [*source_beat.exit_conditions, *target_beat.entry_conditions]
        )

    return guard


def _unique_identifier(value: str, prefix: str, used_names: set[str]) -> str:
    identifier = _to_identifier(value, prefix)
    if identifier in used_names:
        msg = f"duplicate generated identifier: {identifier}"
        raise ValueError(msg)
    used_names.add(identifier)
    return identifier


def _to_identifier(value: str, prefix: str) -> str:
    identifier = _IDENTIFIER_PATTERN.sub("_", value).strip("_").lower()
    if not identifier:
        identifier = prefix
    if identifier[0].isdigit():
        identifier = f"{prefix}_{identifier}"
    return identifier
