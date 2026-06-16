"""Test-only helpers for running the Arcwright ORM against in-memory SQLite.

The production schema uses Postgres-specific types (``JSONB``, pgvector
``VECTOR(1536)``) and server defaults (``gen_random_uuid()``, ``now()``,
``'{}'::jsonb``). SQLite cannot compile those. ``patch_metadata_for_sqlite``
mutates the in-memory ORM ``Base.metadata`` once per process to substitute
SQLite-friendly equivalents so that ``Base.metadata.create_all`` succeeds
and tests can exercise the real ORM without Postgres.

This file is intentionally test-only. Production code never imports it.
Spec parity is validated separately by ``alembic upgrade head`` against
Postgres.
"""

from __future__ import annotations

import uuid

from sqlalchemy import JSON, Text, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.sql.schema import ColumnDefault, DefaultClause

from engine.db.orm import Base

_PATCHED = False


def patch_metadata_for_sqlite() -> None:
    """Substitute SQLite-friendly types and defaults on ``Base.metadata``.

    Idempotent — safe to call from every test module that needs it.
    Substitutions:
      - ``VECTOR(N)`` -> ``Text`` (pgvector is unavailable in SQLite)
      - ``JSONB`` -> ``JSON`` (SQLite has no JSONB compiler)
      - ``gen_random_uuid()`` server default -> Python-side ``uuid4`` default
      - ``now()`` server default -> SQLite ``CURRENT_TIMESTAMP``
      - ``'{}'::jsonb`` / ``'[]'::jsonb`` defaults -> the literal without cast
    """
    global _PATCHED
    if _PATCHED:
        return
    _PATCHED = True

    for table in Base.metadata.tables.values():
        for col in table.columns:
            if type(col.type).__name__ == "VECTOR":
                col.type = Text()

            if isinstance(col.type, JSONB):
                col.type = JSON()

            sd = col.server_default
            if sd is None:
                continue
            arg_str = str(getattr(sd, "arg", ""))

            if "gen_random_uuid" in arg_str:
                col.server_default = None
                col.default = ColumnDefault(uuid.uuid4)
            elif arg_str.strip() == "now()":
                col.server_default = DefaultClause(text("CURRENT_TIMESTAMP"))
            elif "::jsonb" in arg_str:
                col.server_default = DefaultClause(text(arg_str.replace("::jsonb", "")))


async def make_sqlite_session_factory() -> tuple[
    AsyncEngine, async_sessionmaker[AsyncSession]
]:
    """Build an in-memory SQLite engine with the patched schema applied.

    Returns ``(engine, factory)``. The caller owns disposal of the engine
    and lifecycle of sessions. ``patch_metadata_for_sqlite`` is called
    before ``create_all``.
    """
    patch_metadata_for_sqlite()
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    return engine, factory
