from __future__ import annotations

from uuid import UUID

import pytest

from engine.interactions.director import InteractionDirector
from engine.interactions.errors import (
    InteractionLimitError,
    SelectionValidationError,
    WindowClosedError,
)
from engine.interactions.models import (
    InteractionDefinition,
    InteractionLimit,
    InteractionOption,
    InteractionTarget,
    ResolutionVisibility,
)

P1 = UUID("00000000-0000-0000-0000-000000000001")
P2 = UUID("00000000-0000-0000-0000-000000000002")
P3 = UUID("00000000-0000-0000-0000-000000000003")


def definition() -> InteractionDefinition:
    return InteractionDefinition(
        interaction_id="investigation",
        options=[
            InteractionOption(option_id="observe", prompt_key="observe"),
            InteractionOption(option_id="timeline", prompt_key="timeline"),
            InteractionOption(option_id="relationship", prompt_key="relationship"),
            InteractionOption(
                option_id="tell",
                prompt_key="tell",
                required_evidence_ids=["clue.ink"],
                resolution_visibility=ResolutionVisibility.private,
            ),
        ],
        baseline_option_ids=["observe", "timeline", "relationship"],
        limit=InteractionLimit(
            min_players=2,
            max_players=4,
            default_selections_per_player=1,
            selections_per_player_by_count={2: 2, 3: 2},
        ),
    )


def open_director() -> tuple[InteractionDirector, str]:
    director = InteractionDirector(definition(), seed=41)
    window = director.open_window(
        window_id="window-1",
        round_index=1,
        participant_ids=[P1, P2, P3],
        eligible_targets=[
            InteractionTarget(target_id="host"),
            InteractionTarget(target_id="guest"),
        ],
        held_evidence_by_participant={P1: set(), P2: {"clue.ink"}, P3: set()},
    )
    return director, window.window_id


def test_open_window_stages_target_deterministically_and_builds_menus() -> None:
    first, window_id = open_director()
    second, second_window_id = open_director()

    assert (
        first._windows[window_id].staged_target_id
        == second._windows[second_window_id].staged_target_id
    )
    assert [option.option_id for option in first.menu_for(window_id, P1)] == [
        "observe",
        "timeline",
        "relationship",
    ]
    assert [option.option_id for option in first.menu_for(window_id, P2)] == [
        "observe",
        "timeline",
        "relationship",
        "tell",
    ]


def test_revision_replaces_selection_without_spending_another_allowance() -> None:
    director, window_id = open_director()

    first = director.submit_selection(
        window_id=window_id,
        participant_id=P1,
        target_id="host",
        option_id="observe",
    )
    revised = director.submit_selection(
        window_id=window_id,
        participant_id=P1,
        target_id="guest",
        option_id="timeline",
        selection_id=first.selection_id,
    )

    assert first.selection_id == revised.selection_id
    assert director._windows[window_id].remaining_selections[P1] == 1
    assert (
        director._windows[window_id].selections[first.selection_id].target_id == "guest"
    )


def test_selection_rejects_unknown_target_or_unlocked_option() -> None:
    director, window_id = open_director()

    with pytest.raises(SelectionValidationError, match="target"):
        director.submit_selection(
            window_id=window_id,
            participant_id=P1,
            target_id="unknown",
            option_id="observe",
        )
    with pytest.raises(SelectionValidationError, match="option"):
        director.submit_selection(
            window_id=window_id,
            participant_id=P1,
            target_id="host",
            option_id="tell",
        )


def test_lock_rotates_seating_order_and_groups_public_options() -> None:
    director, window_id = open_director()
    for participant in (P1, P2, P3):
        director.submit_selection(
            window_id=window_id,
            participant_id=participant,
            target_id="host",
            option_id="observe",
        )

    resolution = director.lock_window(window_id=window_id)

    assert [
        selection.participant_id for selection in resolution.ordered_selections
    ] == [P2, P3, P1]
    assert len(resolution.public_groups) == 1
    assert resolution.public_groups[0].selection_ids == tuple(
        selection.selection_id for selection in resolution.ordered_selections
    )
    assert resolution.private_selections == ()


def test_allowance_exhaustion_and_closed_window_are_rejected() -> None:
    director, window_id = open_director()
    director.submit_selection(
        window_id=window_id,
        participant_id=P1,
        target_id="host",
        option_id="observe",
    )
    director.submit_selection(
        window_id=window_id,
        participant_id=P1,
        target_id="guest",
        option_id="timeline",
    )
    with pytest.raises(InteractionLimitError):
        director.submit_selection(
            window_id=window_id,
            participant_id=P1,
            target_id="host",
            option_id="relationship",
        )

    for participant in (P2, P3):
        director.submit_selection(
            window_id=window_id,
            participant_id=participant,
            target_id="host",
            option_id="observe",
        )
    director.lock_window(window_id=window_id)
    with pytest.raises(WindowClosedError):
        director.submit_selection(
            window_id=window_id,
            participant_id=P2,
            target_id="host",
            option_id="timeline",
        )


def test_allowance_is_shared_across_rounds_in_the_same_beat() -> None:
    director, window_id = open_director()
    director.submit_selection(
        window_id=window_id,
        participant_id=P1,
        target_id="host",
        option_id="observe",
    )
    director.submit_selection(
        window_id=window_id,
        participant_id=P1,
        target_id="guest",
        option_id="timeline",
    )
    director.lock_window(window_id=window_id, allow_missing=True)

    next_window = director.open_window(
        window_id="window-2",
        beat_id="investigation",
        round_index=2,
        participant_ids=[P1, P2, P3],
        eligible_targets=[InteractionTarget(target_id="host")],
        held_evidence_by_participant={},
    )

    assert next_window.remaining_selections[P1] == 0
    with pytest.raises(InteractionLimitError):
        director.submit_selection(
            window_id=next_window.window_id,
            participant_id=P1,
            target_id="host",
            option_id="observe",
        )


def test_single_player_single_target_configuration_is_supported() -> None:
    single_definition = definition().model_copy(deep=True)
    single_definition.limit = InteractionLimit(
        min_players=1,
        max_players=1,
        default_selections_per_player=1,
    )
    director = InteractionDirector(single_definition, seed=3)
    window = director.open_window(
        window_id="daily-case",
        beat_id="daily-case",
        round_index=0,
        participant_ids=[P1],
        eligible_targets=[InteractionTarget(target_id="suspect")],
        held_evidence_by_participant={},
    )

    director.submit_selection(
        window_id=window.window_id,
        participant_id=P1,
        target_id="suspect",
        option_id="observe",
    )
    resolution = director.lock_window(window_id=window.window_id)

    assert len(resolution.ordered_selections) == 1
