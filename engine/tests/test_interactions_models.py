from __future__ import annotations

from uuid import uuid4

import pytest
from pydantic import ValidationError

from engine.interactions.models import (
    InteractionDefinition,
    InteractionLimit,
    InteractionOption,
    InteractionSelection,
    InteractionTarget,
    InteractionWindow,
    ResolutionVisibility,
    WindowStatus,
)


def option(option_id: str, *, evidence: list[str] | None = None) -> InteractionOption:
    return InteractionOption(
        option_id=option_id,
        prompt_key=f"prompt.{option_id}",
        required_evidence_ids=evidence or [],
        resolution_visibility=ResolutionVisibility.public,
    )


def test_interaction_definition_requires_three_baseline_options() -> None:
    with pytest.raises(ValidationError, match="exactly three baseline"):
        InteractionDefinition(
            interaction_id="investigation",
            options=[option("a"), option("b"), option("c")],
            baseline_option_ids=["a", "b"],
            limit=InteractionLimit(),
        )


def test_interaction_definition_allows_at_most_two_evidence_options() -> None:
    options = [
        option("a"),
        option("b"),
        option("c"),
        option("d", evidence=["clue.d"]),
        option("e", evidence=["clue.e"]),
        option("f", evidence=["clue.f"]),
    ]
    with pytest.raises(ValidationError, match="at most two evidence"):
        InteractionDefinition(
            interaction_id="investigation",
            options=options,
            baseline_option_ids=["a", "b", "c"],
            limit=InteractionLimit(),
        )


def test_interaction_limit_uses_count_specific_allowance() -> None:
    limit = InteractionLimit(
        default_selections_per_player=1,
        selections_per_player_by_count={2: 3, 3: 2, 4: 2},
    )

    assert limit.selections_for(2) == 3
    assert limit.selections_for(4) == 2
    assert limit.selections_for(8) == 1


def test_window_rejects_duplicate_participants_and_target_ids() -> None:
    participant = uuid4()
    with pytest.raises(ValidationError, match="unique"):
        InteractionWindow(
            window_id="window-1",
            interaction_id="investigation",
            round_index=0,
            participant_ids=[participant, participant],
            eligible_targets=[InteractionTarget(target_id="host")],
            menus_by_participant={participant: ["a"]},
            remaining_selections={participant: 1},
            status=WindowStatus.selecting,
        )


def test_selection_is_an_immutable_record() -> None:
    selection = InteractionSelection(
        selection_id="selection-1",
        participant_id=uuid4(),
        target_id="host",
        option_id="a",
    )

    with pytest.raises(ValidationError):
        selection.option_id = "b"
