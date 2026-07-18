from __future__ import annotations

from engine.interactions.menu import build_option_menu
from engine.interactions.models import (
    InteractionDefinition,
    InteractionLimit,
    InteractionOption,
    ResolutionVisibility,
)


def definition() -> InteractionDefinition:
    return InteractionDefinition(
        interaction_id="investigation",
        options=[
            InteractionOption(option_id="observe", prompt_key="observe"),
            InteractionOption(option_id="timeline", prompt_key="timeline"),
            InteractionOption(option_id="relationship", prompt_key="relationship"),
            InteractionOption(
                option_id="clue_read",
                prompt_key="clue_read",
                required_evidence_ids=["clue.ink"],
                resolution_visibility=ResolutionVisibility.private,
            ),
            InteractionOption(
                option_id="clue_pressure",
                prompt_key="clue_pressure",
                required_evidence_ids=["clue.watch"],
                resolution_visibility=ResolutionVisibility.public,
            ),
        ],
        baseline_option_ids=["observe", "timeline", "relationship"],
        limit=InteractionLimit(),
    )


def test_menu_contains_baseline_options_in_authored_order() -> None:
    assert [option.option_id for option in build_option_menu(definition(), set())] == [
        "observe",
        "timeline",
        "relationship",
    ]


def test_menu_unlocks_only_evidence_options_fully_supported() -> None:
    menu = build_option_menu(definition(), {"clue.watch"})

    assert [option.option_id for option in menu] == [
        "observe",
        "timeline",
        "relationship",
        "clue_pressure",
    ]


def test_menu_is_deterministic_and_does_not_share_definition_objects() -> None:
    first = build_option_menu(definition(), {"clue.ink", "clue.watch"})
    second = build_option_menu(definition(), {"clue.ink", "clue.watch"})

    assert [option.option_id for option in first] == [
        option.option_id for option in second
    ]
    assert first[0] is not second[0]
