from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from engine.events.models import AudienceTarget, ContentEvent, EventCategory
from engine.interactions.models import InteractionSelection, PublicInteractionGroup


def build_public_answer_event(
    *,
    session_id: UUID,
    group: PublicInteractionGroup,
    answer_payload: dict[str, Any],
    timestamp: datetime,
    actor_id: UUID | None = None,
) -> ContentEvent:
    return ContentEvent(
        session_id=session_id,
        timestamp=timestamp,
        category=EventCategory.character_dialogue,
        event_type="interaction_answer",
        actor_id=actor_id,
        target_audience=AudienceTarget.all,
        payload={
            "group_id": group.group_id,
            "target_id": group.target_id,
            "option_id": group.option_id,
            "selection_ids": list(group.selection_ids),
            "answer": answer_payload,
        },
    )


def build_private_feedback_event(
    *,
    session_id: UUID,
    selection: InteractionSelection,
    feedback_payload: dict[str, Any],
    timestamp: datetime,
) -> ContentEvent:
    return ContentEvent(
        session_id=session_id,
        timestamp=timestamp,
        category=EventCategory.private_delivery,
        event_type="interaction_feedback",
        target_audience=AudienceTarget.specific_player,
        target_player_id=selection.participant_id,
        payload={
            "selection_id": selection.selection_id,
            "target_id": selection.target_id,
            "option_id": selection.option_id,
            "feedback": feedback_payload,
        },
    )
