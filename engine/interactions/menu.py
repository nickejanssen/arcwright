from __future__ import annotations

from collections.abc import Collection

from engine.interactions.models import InteractionDefinition, InteractionOption


def build_option_menu(
    definition: InteractionDefinition,
    held_evidence_ids: Collection[str],
    *,
    evidence_start_index: int = 0,
) -> list[InteractionOption]:
    """Build a deterministic authored menu for one participant."""

    options_by_id = {option.option_id: option for option in definition.options}
    menu = [
        options_by_id[option_id].model_copy(deep=True)
        for option_id in definition.baseline_option_ids
    ]
    held = set(held_evidence_ids)
    eligible_evidence_options: list[InteractionOption] = []
    for option in definition.options:
        if not option.required_evidence_ids:
            continue
        if set(option.required_evidence_ids).issubset(held):
            eligible_evidence_options.append(option)
    if eligible_evidence_options:
        start = evidence_start_index % len(eligible_evidence_options)
        ordered_evidence = (
            eligible_evidence_options[start:] + eligible_evidence_options[:start]
        )
        menu.extend(option.model_copy(deep=True) for option in ordered_evidence[:2])
    return menu
