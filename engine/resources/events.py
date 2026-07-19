"""ContentEvent factories for resource-balance changes and effect outcomes.

Schema source of truth: engine/events/models.py.
Routes each effect outcome through the existing AudienceTarget/EventCategory
enums per the effect's documented visibility; no new audience primitive.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from engine.events.models import AudienceTarget, ContentEvent, EventCategory


def build_balance_changed_event(
    *,
    session_id: UUID,
    player_id: UUID,
    new_amount: int,
    timestamp: datetime,
) -> ContentEvent:
    return ContentEvent(
        session_id=session_id,
        timestamp=timestamp,
        category=EventCategory.state_transition,
        event_type="resource_balance_changed",
        actor_id=player_id,
        target_audience=AudienceTarget.all,
        payload={
            "player_id": str(player_id),
            "current_amount": new_amount,
        },
    )


def build_effect_outcome_event(
    *,
    session_id: UUID,
    effect_key: str,
    outcome_payload: dict[str, Any],
    audience: AudienceTarget,
    recipient_id: UUID | None,
    category: EventCategory,
    timestamp: datetime,
) -> ContentEvent:
    """Build the ContentEvent for an effect's outcome.

    ``category`` is the caller's call, not inferred from ``audience``: a
    specific_player outcome is always private_delivery, but a table-wide
    (``all``) outcome may be character_dialogue (a character's answer, e.g.
    Rattle the Witness/Follow the Thread) or state_transition (a public state
    change with no dialogue, e.g. Make Them Wait) depending on the effect.
    """
    if audience is AudienceTarget.specific_player:
        if recipient_id is None:
            raise ValueError(
                "recipient_id is required when audience is specific_player"
            )
        target_player_id = recipient_id
    else:
        target_player_id = None

    return ContentEvent(
        session_id=session_id,
        timestamp=timestamp,
        category=category,
        event_type="resource_effect_outcome",
        target_audience=audience,
        target_player_id=target_player_id,
        payload={
            "effect_key": effect_key,
            "outcome": outcome_payload,
        },
    )


def build_source_reveal_event(
    *,
    session_id: UUID,
    revealed_source_id: UUID,
    recipient_id: UUID,
    timestamp: datetime,
) -> ContentEvent:
    return ContentEvent(
        session_id=session_id,
        timestamp=timestamp,
        category=EventCategory.private_delivery,
        event_type="resource_effect_source_revealed",
        target_audience=AudienceTarget.specific_player,
        target_player_id=recipient_id,
        payload={
            "revealed_source_id": str(revealed_source_id),
        },
    )
