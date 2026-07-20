import pytest
from pydantic import ValidationError

from engine.scoring.models import AccusationAttempt, AccusationOutcome, ScoreBreakdown


def test_accusation_attempt_defaults():
    attempt = AccusationAttempt(
        session_id="s1",
        accuser_participant_id="p1",
        beat_id="grill",
        accused_cast_member_id="marcus",
        outcome=AccusationOutcome.wrong,
        catches_banked_at_submission=0,
        points_awarded=-20,
    )
    assert attempt.motive_correct is None
    assert attempt.method_correct is None
    assert attempt.repeat_offense_count == 0
    assert attempt.used_last_word is False
    assert attempt.triggered_last_call is False


def test_accusation_attempt_rejects_extra_fields():
    with pytest.raises(ValidationError):
        AccusationAttempt(
            session_id="s1",
            accuser_participant_id="p1",
            beat_id="grill",
            accused_cast_member_id="marcus",
            outcome=AccusationOutcome.wrong,
            catches_banked_at_submission=0,
            points_awarded=-20,
            unexpected_field="nope",
        )


def test_score_breakdown_totals_are_explicit_not_derived():
    breakdown = ScoreBreakdown(
        evidence_points=40,
        catch_points=150,
        accusation_points=169,
        motive_bonus=25,
        method_bonus=0,
        total=384,
    )
    assert breakdown.total == 384
