"""add_claims_and_contradiction_flags

Revision ID: 0006_claims_contradiction_flags
Revises: 0005_add_obligations_table
Create Date: 2026-07-19

Adds the claims and contradiction_flags tables (AW-283, D-078). Claims
are this platform's headline differentiated mechanic and a labeled
ground-truth source for AW-272 evals, so they get a dedicated indexed
schema rather than the generic events table.
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID

revision = "0006_claims_contradiction_flags"
down_revision = "0005_add_obligations_table"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "claims",
        sa.Column(
            "claim_id",
            PGUUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "session_id",
            PGUUID(as_uuid=True),
            sa.ForeignKey("sessions.session_id"),
            nullable=False,
        ),
        sa.Column(
            "speaker_character_id",
            PGUUID(as_uuid=True),
            sa.ForeignKey("characters.character_id"),
            nullable=False,
        ),
        sa.Column(
            "asker_participant_id",
            PGUUID(as_uuid=True),
            sa.ForeignKey("session_participants.participant_id"),
            nullable=True,
        ),
        sa.Column("round_index", sa.Integer(), nullable=False),
        sa.Column("beat_id", sa.Text(), nullable=False),
        sa.Column("interaction_window_id", sa.Text(), nullable=False),
        sa.Column("claim_text", sa.Text(), nullable=False),
        sa.Column(
            "referenced_fact_ids",
            JSONB,
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column(
            "is_authorized_lie",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column("falsehood_id", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index(
        "ix_claims_session_id_speaker",
        "claims",
        ["session_id", "speaker_character_id"],
    )
    op.create_index(
        "ix_claims_session_id_beat",
        "claims",
        ["session_id", "beat_id"],
    )

    op.create_table(
        "contradiction_flags",
        sa.Column(
            "flag_id",
            PGUUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "claim_id",
            PGUUID(as_uuid=True),
            sa.ForeignKey("claims.claim_id"),
            nullable=False,
        ),
        sa.Column(
            "session_id",
            PGUUID(as_uuid=True),
            sa.ForeignKey("sessions.session_id"),
            nullable=False,
        ),
        sa.Column(
            "flagged_by_participant_id",
            PGUUID(as_uuid=True),
            sa.ForeignKey("session_participants.participant_id"),
            nullable=False,
        ),
        sa.Column("outcome", sa.Text(), nullable=False),
        sa.Column("evidence_id_used", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index(
        "ix_contradiction_flags_claim_id",
        "contradiction_flags",
        ["claim_id"],
    )
    op.create_index(
        "ix_contradiction_flags_session_id",
        "contradiction_flags",
        ["session_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_contradiction_flags_session_id", table_name="contradiction_flags")
    op.drop_index("ix_contradiction_flags_claim_id", table_name="contradiction_flags")
    op.drop_table("contradiction_flags")
    op.drop_index("ix_claims_session_id_beat", table_name="claims")
    op.drop_index("ix_claims_session_id_speaker", table_name="claims")
    op.drop_table("claims")
