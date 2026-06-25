"""add_mini_game_tables

Revision ID: 0003_add_mini_game_tables
Revises: 0002_create_platform_tables
Create Date: 2026-06-25

Adds mini_game_runs (canonical run state) and mini_game_submissions
(append-only player actions) per AW-251.

Schema source of truth: docs/specs/0048-aw-251-mini-game-runtime-persistence-and-clue-gating.md
ADR: docs/decisions/0009-mini-game-runtime-boundary.md
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0003_add_mini_game_tables"
down_revision = "0002_create_platform_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "mini_game_runs",
        sa.Column(
            "run_id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("session_id", sa.UUID(), nullable=False),
        sa.Column("game_id", sa.Text(), nullable=False),
        sa.Column("definition_version", sa.Text(), nullable=False),
        sa.Column(
            "definition_snapshot",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Text(),
            server_default=sa.text("'pending'"),
            nullable=False,
        ),
        sa.Column(
            "revision",
            sa.Integer(),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deadline", sa.DateTime(timezone=True), nullable=True),
        sa.Column("paused_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("pause_deadline_remaining_seconds", sa.Float(), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "outcome",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column(
            "behavioral_outputs",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column(
            "clue_unlock_record",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["sessions.session_id"],
        ),
        sa.PrimaryKeyConstraint("run_id"),
    )
    op.create_index(
        "ix_mini_game_runs_session_id_status",
        "mini_game_runs",
        ["session_id", "status"],
    )

    op.create_table(
        "mini_game_submissions",
        sa.Column(
            "submission_pk",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("run_id", sa.UUID(), nullable=False),
        sa.Column("submission_id", sa.Text(), nullable=False),
        sa.Column("character_id", sa.UUID(), nullable=False),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "payload",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column("is_accepted", sa.Boolean(), nullable=False),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column("scored_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["run_id"],
            ["mini_game_runs.run_id"],
        ),
        sa.ForeignKeyConstraint(
            ["character_id"],
            ["characters.character_id"],
        ),
        sa.PrimaryKeyConstraint("submission_pk"),
        sa.UniqueConstraint(
            "run_id",
            "submission_id",
            name="uq_mini_game_submissions_run_submission",
        ),
    )


def downgrade() -> None:
    op.drop_table("mini_game_submissions")
    op.drop_index("ix_mini_game_runs_session_id_status", table_name="mini_game_runs")
    op.drop_table("mini_game_runs")
