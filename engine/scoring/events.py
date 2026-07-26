"""Surface-agnostic scoring events with pre-reveal leak guards."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from engine.events.models import (
    AudienceTarget,
    ContentEvent,
    EventCategory,
    PresentationHints,
)
from engine.scoring.models import ScoreBreakdown

_FORBIDDEN_PRE_REVEAL_TERMS = frozenset(
    {"evidence", "contradiction", "accusation", "score", "points"}
)


def build_scoring_sting_event(
    *,
    session_id: UUID,
    player_id: UUID,
    sting_key: str,
    message: str,
    timestamp: datetime,
) -> ContentEvent:
    """Build a neutral pre-reveal scoring moment without math or dimensions."""
    if not sting_key.strip() or not message.strip():
        raise ValueError("scoring stings require a non-empty key and message")
    payload_text = f"{sting_key} {message}".lower()
    if any(term in payload_text for term in _FORBIDDEN_PRE_REVEAL_TERMS):
        raise ValueError("pre-reveal scoring stings cannot name score dimensions")
    return ContentEvent(
        session_id=session_id,
        timestamp=timestamp,
        category=EventCategory.acknowledgement,
        event_type="scoring_sting",
        actor_id=player_id,
        target_audience=AudienceTarget.all,
        payload={"sting_key": sting_key, "message": message},
        presentation_hints=PresentationHints(
            emotion="triumphant",
            voice_hint="brief_narrator_sting",
            animation_hint="race_track_pulse",
        ),
    )


def build_race_track_position_event(
    *,
    session_id: UUID,
    player_id: UUID,
    relative_position: float,
    timestamp: datetime,
) -> ContentEvent:
    """Build blended race motion without exposing a scoring component."""
    if not 0.0 <= relative_position <= 1.0:
        raise ValueError("relative_position must be between 0.0 and 1.0")
    return ContentEvent(
        session_id=session_id,
        timestamp=timestamp,
        category=EventCategory.state_transition,
        event_type="race_track_motion",
        actor_id=player_id,
        target_audience=AudienceTarget.shared_display,
        payload={"position": relative_position},
        presentation_hints=PresentationHints(
            animation_hint="race_track_move",
            voice_hint="race_track_motion",
        ),
    )


def build_reveal_score_breakdown_event(
    *,
    session_id: UUID,
    player_id: UUID,
    breakdown: ScoreBreakdown,
    timestamp: datetime,
) -> ContentEvent:
    """Build the Truth-beat event where the full score is intentionally public."""
    return ContentEvent(
        session_id=session_id,
        timestamp=timestamp,
        category=EventCategory.narrative,
        event_type="score_reveal",
        actor_id=player_id,
        target_audience=AudienceTarget.all,
        payload={"score_breakdown": breakdown.model_dump()},
        presentation_hints=PresentationHints(
            animation_hint="scoreboard_reveal",
            voice_hint="truth_beat_score_reveal",
        ),
    )
