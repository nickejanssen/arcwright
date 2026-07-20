"""ContentEvent factories for public claim and contradiction outcomes."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from engine.events.models import AudienceTarget, ContentEvent, EventCategory


def build_claim_recorded_event(
    *,
    session_id: UUID,
    claim_id: str,
    speaker_id: UUID,
    claim_text: str,
    timestamp: datetime,
    is_authorized_lie: bool = False,
    falsehood_id: str | None = None,
) -> ContentEvent:
    """Build a public claim event without exposing lie classification."""
    del is_authorized_lie, falsehood_id
    return ContentEvent(
        session_id=session_id,
        timestamp=timestamp,
        category=EventCategory.character_dialogue,
        event_type="claim_recorded",
        actor_id=speaker_id,
        target_audience=AudienceTarget.all,
        payload={
            "claim_id": claim_id,
            "speaker_id": str(speaker_id),
            "claim_text": claim_text,
        },
    )


def build_contradiction_outcome_event(
    *,
    session_id: UUID,
    claim_id: str,
    outcome: str,
    evidence_id_used: str | None,
    timestamp: datetime,
) -> ContentEvent:
    """Build a public contradiction outcome event without scoring data."""
    return ContentEvent(
        session_id=session_id,
        timestamp=timestamp,
        category=EventCategory.state_transition,
        event_type=f"contradiction_{outcome}",
        target_audience=AudienceTarget.all,
        payload={
            "claim_id": claim_id,
            "outcome": outcome,
            "evidence_id_used": evidence_id_used,
        },
    )
