"""add_obligations_table

Revision ID: 0005_add_obligations_table
Revises: 0004_add_lobby_fields
Create Date: 2026-07-13

Adds the obligations table for the narrative obligations model
(AW-271, spec 0065, ADR-0012). Obligations track authored setups,
pacing misdirection injections, and generative promises as durable
session state, backing the reveal-readiness session-context condition.
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID

revision = "0005_add_obligations_table"
down_revision = "0004_add_lobby_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "obligations",
        sa.Column(
            "obligation_id",
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
        sa.Column("source_type", sa.Text(), nullable=False),
        sa.Column(
            "source_ref",
            JSONB,
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column(
            "mandatory",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "status",
            sa.Text(),
            nullable=False,
            server_default=sa.text("'open'"),
        ),
        sa.Column("created_beat", sa.Text(), nullable=False),
        sa.Column("resolved_beat", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_obligations_session_id_status",
        "obligations",
        ["session_id", "status"],
    )


def downgrade() -> None:
    op.drop_index("ix_obligations_session_id_status", table_name="obligations")
    op.drop_table("obligations")
