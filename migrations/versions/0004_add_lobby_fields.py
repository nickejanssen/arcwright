"""add_lobby_fields

Revision ID: 0004_add_lobby_fields
Revises: 0003_add_mini_game_tables
Create Date: 2026-06-27

Adds join_code to sessions and display_name to session_participants
for the Nightcap rehearsal lobby (Rehearsal 1, AW-231).
"""

import sqlalchemy as sa
from alembic import op

revision = "0004_add_lobby_fields"
down_revision = "0003_add_mini_game_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "sessions",
        sa.Column("join_code", sa.Text(), nullable=True),
    )
    op.create_unique_constraint("uq_sessions_join_code", "sessions", ["join_code"])
    op.add_column(
        "session_participants",
        sa.Column("display_name", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("session_participants", "display_name")
    op.drop_constraint("uq_sessions_join_code", "sessions", type_="unique")
    op.drop_column("sessions", "join_code")
