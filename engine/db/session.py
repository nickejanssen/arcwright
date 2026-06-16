"""Async DB session factory + FastAPI dependency for the API layer.

Architecture: docs/architecture/05-session-persistence.md (Postgres at MVP),
docs/architecture/09-developer-api.md §9.2.

Behavior:
  - Reads ``ARCWRIGHT_DATABASE_URL`` from the environment.
  - If unset, falls back to an in-memory SQLite engine (single-process MVP
    behavior + local development convenience). The SQLite path applies the
    ORM-to-SQLite shim from ``engine.db.testing`` once at engine creation.
  - Exposes ``get_async_session()`` as a FastAPI dependency that yields a
    request-scoped ``AsyncSession`` and commits on success, rolls back on
    failure, and closes always.

For tests, prefer ``app.dependency_overrides[get_async_session] = ...`` so
the test owns the engine and session factory.
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


def _build_engine() -> AsyncEngine:
    """Create the process-level async engine.

    Production callers set ``ARCWRIGHT_DATABASE_URL`` to the Cloud SQL
    Postgres URL. When unset, a single in-memory SQLite engine is used —
    suitable for local development only; never for production.
    """
    url = os.environ.get("ARCWRIGHT_DATABASE_URL")
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
        _session_factory = async_sessionmaker(
            get_engine(), class_=AsyncSession, expire_on_commit=False
        )
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
