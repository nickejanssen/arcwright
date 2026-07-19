from datetime import UTC, datetime
from uuid import uuid4

from engine.claims.events import (
    build_claim_recorded_event,
    build_contradiction_outcome_event,
)
from engine.events.models import AudienceTarget, EventCategory


def test_claim_recorded_event_is_public_and_does_not_leak_lie_markers() -> None:
    session_id = uuid4()
    speaker_id = uuid4()
    event = build_claim_recorded_event(
        session_id=session_id,
        claim_id="claim-1",
        speaker_id=speaker_id,
        claim_text="I was in the garden.",
        timestamp=datetime.now(UTC),
        is_authorized_lie=True,
        falsehood_id="lie-1",
    )

    assert event.session_id == session_id
    assert event.actor_id == speaker_id
    assert event.target_audience is AudienceTarget.all
    assert event.category is EventCategory.character_dialogue
    assert event.event_type == "claim_recorded"
    assert set(event.payload) == {"claim_id", "speaker_id", "claim_text"}
    assert "is_authorized_lie" not in event.payload
    assert "falsehood_id" not in event.payload


def test_contradiction_event_is_public_and_has_no_score() -> None:
    event = build_contradiction_outcome_event(
        session_id=uuid4(),
        claim_id="claim-1",
        outcome="confirmed",
        evidence_id_used="evidence-1",
        timestamp=datetime.now(UTC),
    )

    assert event.target_audience is AudienceTarget.all
    assert event.category is EventCategory.state_transition
    assert event.event_type == "contradiction_confirmed"
    assert event.payload == {
        "claim_id": "claim-1",
        "outcome": "confirmed",
        "evidence_id_used": "evidence-1",
    }
    assert not {"score", "points", "score_value"} & set(event.payload)
