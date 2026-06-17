"""Async DB session factory + FastAPI dependency for the API layer.

Architecture: docs/architecture/05-session-persistence.md (Postgres at MVP),
docs/architecture/09-developer-api.md §9.2.

DB URL resolution mirrors ``migrations/env.py`` so the API layer and
Alembic always point at the same database:
  1. ``DATABASE_URL`` if set
  2. composed from ``POSTGRES_HOST`` / ``POSTGRES_PORT`` / ``POSTGRES_DB``
     / ``POSTGRES_USER`` / ``POSTGRES_PASSWORD`` if all present
  3. in-memory SQLite (dev convenience only; never production)

``get_async_session()`` is a FastAPI dependency that yields a
request-scoped ``AsyncSession`` and commits on success, rolls back on
failure, and closes always. For tests, prefer
``app.dependency_overrides[get_async_session] = ...`` so the test owns
the engine and session factory.
"""

from __future__ import annotations

import os
from collections.abc import AsyncIterator
from typing import Optional

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

_engine: Optional[AsyncEngine] = None
_session_factory: Optional[async_sessionmaker[AsyncSession]] = None


def resolve_database_url() -> Optional[str]:
    """Return the configured database URL or ``None`` for the SQLite fallback.

    Convention matches ``migrations/env.py``:
      - ``DATABASE_URL`` wins if set.
      - Otherwise compose from ``POSTGRES_HOST`` / ``POSTGRES_PORT`` /
        ``POSTGRES_DB`` / ``POSTGRES_USER`` / ``POSTGRES_PASSWORD`` when
        all are present.
      - Return ``None`` if neither path resolves — callers fall back to
        in-memory SQLite (dev only).
    """
    direct = os.environ.get("DATABASE_URL")
    if direct:
        return direct

    keys = (
        "POSTGRES_HOST",
        "POSTGRES_PORT",
        "POSTGRES_DB",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
    )
    values = {key: os.environ.get(key) for key in keys}
    if any(not v for v in values.values()):
        return None
    return (
        "postgresql+asyncpg://"
        f"{values['POSTGRES_USER']}:{values['POSTGRES_PASSWORD']}"
        f"@{values['POSTGRES_HOST']}:{values['POSTGRES_PORT']}"
        f"/{values['POSTGRES_DB']}"
    )


def _build_engine() -> AsyncEngine:
    """Create the process-level async engine.

    Resolves the URL via ``resolve_database_url``. Falls back to an
    in-memory SQLite engine when no Postgres config is present — local
    development convenience only; never production.
    """
    url = resolve_database_url()
    if not url:
        from engine.db.testing import patch_metadata_for_sqlite

        patch_metadata_for_sqlite()
        return create_async_engine(
            "sqlite+aiosqlite:///:memory:",
            echo=False,
        )
    return create_async_engine(url, echo=False)


def get_engine() -> AsyncEngine:
    """Return the process-level engine, building it on first access."""
    global _engine
    if _engine is None:
        _engine = _build_engine()
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Return the process-level session factory."""
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(get_engine(), expire_on_commit=False)
    return _session_factory


async def get_async_session() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency: yield a request-scoped session.

    Commits on success, rolls back on exception, always closes.
    """
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
