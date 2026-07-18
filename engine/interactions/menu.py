from __future__ import annotations

from collections.abc import Collection

from engine.interactions.models import InteractionDefinition, InteractionOption


def build_option_menu(
    definition: InteractionDefinition,
    held_evidence_ids: Collection[str],
) -> list[InteractionOption]:
    """Build a deterministic authored menu for one participant."""

    options_by_id = {option.option_id: option for option in definition.options}
    menu = [
        options_by_id[option_id].model_copy(deep=True)
        for option_id in definition.baseline_option_ids
    ]
    held = set(held_evidence_ids)
    for option in definition.options:
        if not option.required_evidence_ids:
            continue
        if set(option.required_evidence_ids).issubset(held):
            menu.append(option.model_copy(deep=True))
    return menu
