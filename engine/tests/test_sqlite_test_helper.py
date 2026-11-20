"""Regression tests for the in-memory SQLite test helper (AW-342).

SQLite gives a column declared ``UUID`` numeric affinity, so a stored ID whose
32 hex characters read as a number in scientific notation (digits plus a single
``e``) came back as a float. ``patch_metadata_for_sqlite`` must store IDs as
text so every ID reads back as a ``uuid.UUID``.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from uuid import UUID

import pytest_asyncio
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.ext.asyncio import AsyncSession

from engine.db.orm import Account, Base
from engine.db.testing import make_sqlite_session_factory, patch_metadata_for_sqlite

# 32 hex characters: digits and one "e", so SQLite numeric affinity parses it
# as 8.16e+58 when the column is declared UUID.
NUMBER_LOOKING_ID = UUID("81601076-2124-4484-0000-000000000e31")


@pytest_asyncio.fixture()
async def db() -> AsyncIterator[AsyncSession]:
    engine, factory = await make_sqlite_session_factory()
    async with factory() as session:
        yield session
    await engine.dispose()


async def test_number_looking_id_round_trips_as_uuid(db: AsyncSession) -> None:
    db.add(Account(account_id=NUMBER_LOOKING_ID, firebase_uid="uid-aw342"))
    await db.commit()
    db.expunge_all()

    loaded = await db.get(Account, NUMBER_LOOKING_ID)

    assert loaded is not None
    assert isinstance(loaded.account_id, UUID)
    assert loaded.account_id == NUMBER_LOOKING_ID


def test_no_postgres_uuid_column_type_left_after_patch() -> None:
    patch_metadata_for_sqlite()
    leftovers = [
        f"{table.name}.{col.name}"
        for table in Base.metadata.tables.values()
        for col in table.columns
        if isinstance(col.type, PGUUID)
    ]
    assert leftovers == []


def test_patch_is_idempotent() -> None:
    patch_metadata_for_sqlite()
    before = {
        f"{t.name}.{c.name}": type(c.type)
        for t in Base.metadata.tables.values()
        for c in t.columns
    }
    patch_metadata_for_sqlite()
    after = {
        f"{t.name}.{c.name}": type(c.type)
        for t in Base.metadata.tables.values()
        for c in t.columns
    }
    assert before == after
