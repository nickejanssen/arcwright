"""Tests for claim and contradiction DTOs."""

import pytest
from pydantic import ValidationError

from engine.claims.models import ClaimRecord, ContradictionOutcome, FlagResult


def test_claim_record_defaults_not_a_lie() -> None:
    claim = ClaimRecord(
        speaker_id="char-1",
        asker_id="p1",
        round_index=1,
        beat_id="grill",
        interaction_window_id="w1",
        claim_text="I was on the terrace.",
    )
    assert claim.is_authorized_lie is False
    assert claim.falsehood_id is None


def test_claim_record_rejects_extra_fields() -> None:
    with pytest.raises(ValidationError):
        ClaimRecord(
            speaker_id="char-1",
            asker_id="p1",
            round_index=1,
            beat_id="grill",
            interaction_window_id="w1",
            claim_text="x",
            unexpected_field="nope",
        )


def test_flag_result_confirmed_requires_evidence_id() -> None:
    result = FlagResult(
        claim_id="claim-1",
        outcome=ContradictionOutcome.confirmed,
        evidence_id_used="evidence.coat_check_ticket",
    )
    assert result.outcome is ContradictionOutcome.confirmed
    assert result.evidence_id_used == "evidence.coat_check_ticket"


def test_flag_result_rejected_has_no_evidence_id() -> None:
    result = FlagResult(claim_id="claim-1", outcome=ContradictionOutcome.rejected)
    assert result.evidence_id_used is None
