from datetime import datetime, timezone
from uuid import uuid4

import pytest

from engine.events.models import AudienceTarget, PresentationHints
from engine.scoring.events import (
    build_race_track_position_event,
    build_reveal_score_breakdown_event,
    build_scoring_sting_event,
)
from engine.scoring.models import ScoreBreakdown


def _timestamp() -> datetime:
    return datetime(2026, 7, 19, 12, 0, tzinfo=timezone.utc)


def test_scoring_sting_has_no_raw_math_or_dimension_leak():
    event = build_scoring_sting_event(
        session_id=uuid4(),
        player_id=uuid4(),
        sting_key="snap",
        message="The room tightens",
        timestamp=_timestamp(),
    )

    assert set(event.payload) == {"sting_key", "message"}
    flattened = str(event.payload).lower()
    assert not any(
        term in flattened
        for term in ("evidence", "contradiction", "accusation", "score", "points")
    )
    assert event.presentation_hints != PresentationHints()
    assert event.presentation_hints.animation_hint
    assert event.presentation_hints.voice_hint


def test_scoring_sting_rejects_dimension_names():
    with pytest.raises(ValueError, match="score dimensions"):
        build_scoring_sting_event(
            session_id=uuid4(),
            player_id=uuid4(),
            sting_key="evidence",
            message="A clue lands",
            timestamp=_timestamp(),
        )


def test_race_track_event_has_only_blended_relative_position():
    event = build_race_track_position_event(
        session_id=uuid4(),
        player_id=uuid4(),
        relative_position=0.65,
        timestamp=_timestamp(),
    )

    assert event.target_audience is AudienceTarget.shared_display
    assert event.payload == {"position": 0.65}


def test_reveal_breakdown_is_the_public_full_score_event():
    breakdown = ScoreBreakdown(
        evidence_points=40,
        catch_points=150,
        accusation_points=169,
        motive_bonus=25,
        method_bonus=0,
        total=384,
    )
    event = build_reveal_score_breakdown_event(
        session_id=uuid4(),
        player_id=uuid4(),
        breakdown=breakdown,
        timestamp=_timestamp(),
    )

    assert event.target_audience is AudienceTarget.all
    assert event.payload["score_breakdown"] == breakdown.model_dump()
