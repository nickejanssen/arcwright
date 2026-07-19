"""Schema contracts for AW-283 claim persistence."""

from __future__ import annotations

from engine.db.orm import Claim, ContradictionFlag


def test_claim_tables_expose_the_approved_columns() -> None:
    assert set(Claim.__table__.columns.keys()) == {
        "claim_id",
        "session_id",
        "speaker_character_id",
        "asker_participant_id",
        "round_index",
        "beat_id",
        "interaction_window_id",
        "claim_text",
        "referenced_fact_ids",
        "is_authorized_lie",
        "falsehood_id",
        "created_at",
    }
    assert set(ContradictionFlag.__table__.columns.keys()) == {
        "flag_id",
        "claim_id",
        "session_id",
        "flagged_by_participant_id",
        "outcome",
        "evidence_id_used",
        "created_at",
    }
