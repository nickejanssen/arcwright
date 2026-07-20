"""add_accusations_table

Revision ID: 0007_add_accusations_table
Revises: 0006_claims_contradiction_flags
Create Date: 2026-07-19

Adds the accusations and suspect_locks tables (AW-284). Accusation attempts
are gameplay-critical, replay-reproducible state that reveal accounting and
superlative computation read after the fact, so they get a dedicated indexed
schema rather than the generic events table.
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID as PGUUID

revision = "0007_add_accusations_table"
down_revision = "0006_claims_contradiction_flags"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "accusations",
        sa.Column(
            "accusation_id",
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
            "accuser_participant_id",
            PGUUID(as_uuid=True),
            sa.ForeignKey("session_participants.participant_id"),
            nullable=False,
        ),
        sa.Column("beat_id", sa.Text(), nullable=False),
        sa.Column("accused_cast_member_id", sa.Text(), nullable=False),
        sa.Column("motive_correct", sa.Boolean(), nullable=True),
        sa.Column("method_correct", sa.Boolean(), nullable=True),
        sa.Column("outcome", sa.Text(), nullable=False),
        sa.Column("catches_banked_at_submission", sa.Integer(), nullable=False),
        sa.Column("points_awarded", sa.Integer(), nullable=False),
        sa.Column(
            "repeat_offense_count", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column("lockout_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "used_last_word",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "triggered_last_call",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "submitted_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index(
        "ix_accusations_session_id_accuser",
        "accusations",
        ["session_id", "accuser_participant_id"],
    )
    op.create_index(
        "ix_accusations_session_id_outcome_submitted_at",
        "accusations",
        ["session_id", "outcome", "submitted_at"],
    )

    op.create_table(
        "suspect_locks",
        sa.Column(
            "suspect_lock_id",
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
            "participant_id",
            PGUUID(as_uuid=True),
            sa.ForeignKey("session_participants.participant_id"),
            nullable=False,
        ),
        sa.Column("suspect_cast_member_id", sa.Text(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_unique_constraint(
        "uq_suspect_locks_session_participant",
        "suspect_locks",
        ["session_id", "participant_id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_suspect_locks_session_participant", "suspect_locks", type_="unique"
    )
    op.drop_table("suspect_locks")
    op.drop_index(
        "ix_accusations_session_id_outcome_submitted_at", table_name="accusations"
    )
    op.drop_index("ix_accusations_session_id_accuser", table_name="accusations")
    op.drop_table("accusations")
