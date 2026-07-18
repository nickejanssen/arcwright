from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from engine.events.models import AudienceTarget, EventCategory
from engine.interactions.events import (
    build_private_feedback_event,
    build_public_answer_event,
)
from engine.interactions.models import InteractionSelection, PublicInteractionGroup

SESSION_ID = UUID("00000000-0000-0000-0000-000000000010")
PLAYER_ID = UUID("00000000-0000-0000-0000-000000000011")
TIMESTAMP = datetime(2026, 7, 18, tzinfo=timezone.utc)


def test_public_answer_event_contains_grouped_selection_metadata() -> None:
    group = PublicInteractionGroup(
        group_id="window-1:host:observe",
        target_id="host",
        option_id="observe",
        selection_ids=["selection-1", "selection-2"],
    )

    event = build_public_answer_event(
        session_id=SESSION_ID,
        group=group,
        answer_payload={"text": "The room goes quiet."},
        timestamp=TIMESTAMP,
    )

    assert event.category is EventCategory.character_dialogue
    assert event.event_type == "interaction_answer"
    assert event.target_audience is AudienceTarget.all
    assert event.payload == {
        "group_id": "window-1:host:observe",
        "target_id": "host",
        "option_id": "observe",
        "selection_ids": ["selection-1", "selection-2"],
        "answer": {"text": "The room goes quiet."},
    }


def test_private_feedback_event_targets_only_the_asking_player() -> None:
    selection = InteractionSelection(
        selection_id="selection-1",
        participant_id=PLAYER_ID,
        target_id="host",
        option_id="tell",
    )

    event = build_private_feedback_event(
        session_id=SESSION_ID,
        selection=selection,
        feedback_payload={"observation": "Their hand trembles."},
        timestamp=TIMESTAMP,
    )

    assert event.category is EventCategory.private_delivery
    assert event.event_type == "interaction_feedback"
    assert event.target_audience is AudienceTarget.specific_player
    assert event.target_player_id == PLAYER_ID
    assert event.payload == {
        "selection_id": "selection-1",
        "target_id": "host",
        "option_id": "tell",
        "feedback": {"observation": "Their hand trembles."},
    }
