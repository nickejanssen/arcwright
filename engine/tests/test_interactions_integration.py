from __future__ import annotations

from uuid import UUID

import pytest

from engine.interactions.director import InteractionDirector
from engine.interactions.errors import InteractionLimitError
from engine.interactions.models import (
    InteractionDefinition,
    InteractionLimit,
    InteractionOption,
    InteractionTarget,
    ResolutionVisibility,
)

PLAYERS = [
    UUID("00000000-0000-0000-0000-000000000101"),
    UUID("00000000-0000-0000-0000-000000000102"),
    UUID("00000000-0000-0000-0000-000000000103"),
]


def test_synthetic_interaction_session_resolves_public_and_private_questions() -> None:
    definition = InteractionDefinition(
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
            max_players=8,
            default_selections_per_player=1,
            selections_per_player_by_count={3: 2},
        ),
    )
    director = InteractionDirector(definition, seed=99)
    window = director.open_window(
        window_id="synthetic-window",
        round_index=2,
        participant_ids=PLAYERS,
        eligible_targets=[InteractionTarget(target_id="host")],
        held_evidence_by_participant={
            PLAYERS[0]: set(),
            PLAYERS[1]: {"clue.ink"},
            PLAYERS[2]: set(),
        },
    )

    assert [
        option.option_id for option in director.menu_for(window.window_id, PLAYERS[1])
    ][-1] == "tell"
    first = director.submit_selection(
        window_id=window.window_id,
        participant_id=PLAYERS[0],
        target_id="host",
        option_id="observe",
    )
    director.submit_selection(
        window_id=window.window_id,
        participant_id=PLAYERS[0],
        target_id="host",
        option_id="observe",
    )
    director.submit_selection(
        window_id=window.window_id,
        participant_id=PLAYERS[1],
        target_id="host",
        option_id="tell",
    )
    director.submit_selection(
        window_id=window.window_id,
        participant_id=PLAYERS[2],
        target_id="host",
        option_id="observe",
    )

    resolution = director.lock_window(window_id=window.window_id)

    assert len(resolution.ordered_selections) == 4
    assert len(resolution.public_groups) == 1
    assert resolution.public_groups[0].selection_ids == [
        f"{window.window_id}:{PLAYERS[2]}:3",
        first.selection_id,
        f"{window.window_id}:{PLAYERS[0]}:1",
    ]
    assert [
        selection.participant_id for selection in resolution.private_selections
    ] == [PLAYERS[1]]


def test_synthetic_session_rejects_a_third_selection_after_two_allowances() -> None:
    definition = InteractionDefinition(
        interaction_id="investigation",
        options=[
            InteractionOption(option_id="observe", prompt_key="observe"),
            InteractionOption(option_id="timeline", prompt_key="timeline"),
            InteractionOption(option_id="relationship", prompt_key="relationship"),
        ],
        baseline_option_ids=["observe", "timeline", "relationship"],
        limit=InteractionLimit(
            min_players=2, max_players=8, selections_per_player_by_count={2: 2}
        ),
    )
    director = InteractionDirector(definition, seed=1)
    window = director.open_window(
        window_id="limit-window",
        round_index=0,
        participant_ids=PLAYERS[:2],
        eligible_targets=[InteractionTarget(target_id="host")],
        held_evidence_by_participant={},
    )
    for option_id in ("observe", "timeline"):
        director.submit_selection(
            window_id=window.window_id,
            participant_id=PLAYERS[0],
            target_id="host",
            option_id=option_id,
        )
    with pytest.raises(InteractionLimitError):
        director.submit_selection(
            window_id=window.window_id,
            participant_id=PLAYERS[0],
            target_id="host",
            option_id="relationship",
        )
