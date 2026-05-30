"""Tests for engine/knowledge/graph.py — knowledge graph assertion API."""

from __future__ import annotations

import uuid
from uuid import UUID, uuid4

import pytest
from sqlalchemy import JSON, Text, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.schema import ColumnDefault, DefaultClause

from engine.db.orm import Base, Character, Fact, KnowledgeState, Session
from engine.knowledge import assert_knowledge, get_character_knowledge, revoke_knowledge

# ---------------------------------------------------------------------------
# One-time metadata patch so Base.metadata.create_all works with SQLite.
# Patches are applied module-wide before any test runs.
# ---------------------------------------------------------------------------

_PATCHED = False


def _patch_metadata_for_sqlite() -> None:
    global _PATCHED
    if _PATCHED:
        return
    _PATCHED = True

    for table in Base.metadata.tables.values():
        for col in table.columns:
            # Replace pgvector Vector types (not supported by SQLite)
            if type(col.type).__name__ == "VECTOR":
                col.type = Text()

            # Replace JSONB with JSON (SQLite has no JSONB type compiler)
            if isinstance(col.type, JSONB):
                col.type = JSON()

            sd = col.server_default
            if sd is None:
                continue
            arg_str = str(getattr(sd, "arg", ""))

            if "gen_random_uuid" in arg_str:
                # Replace PG-specific UUID generation with Python-side uuid4
                col.server_default = None
                col.default = ColumnDefault(uuid.uuid4)
            elif arg_str.strip() == "now()":
                # SQLite recognises CURRENT_TIMESTAMP natively
                col.server_default = DefaultClause(text("CURRENT_TIMESTAMP"))
            elif "::jsonb" in arg_str:
                # Strip the PG cast; raw JSON literals are valid in SQLite
                col.server_default = DefaultClause(text(arg_str.replace("::jsonb", "")))


_patch_metadata_for_sqlite()


# ---------------------------------------------------------------------------
# Async session fixture
# ---------------------------------------------------------------------------


@pytest.fixture
async def session() -> AsyncSession:  # type: ignore[override]
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as sess:  # type: ignore[attr-defined]
        yield sess  # type: ignore[misc]

    await engine.dispose()


# ---------------------------------------------------------------------------
# Helpers for creating minimal parent objects required by selectinload.
# SQLite does not enforce FK constraints, so only the Fact row is strictly
# required (get_character_knowledge eager-loads it via selectinload).
# ---------------------------------------------------------------------------


async def _make_fact(
    session: AsyncSession,
    *,
    session_id: UUID,
    fact_id: UUID | None = None,
) -> Fact:
    fact = Fact(
        fact_id=fact_id or uuid4(),
        session_id=session_id,
        fact_type="test_type",
        fact_content={"key": "value"},
    )
    session.add(fact)
    await session.flush()
    return fact


async def _make_session_row(
    db: AsyncSession,
    *,
    session_id: UUID | None = None,
) -> Session:
    s = Session(
        session_id=session_id or uuid4(),
        arc_id="arc-1",
        status="active",
        host_account_id=uuid4(),
        current_beat_id="beat-1",
        quality_tier="standard",
        player_count=3,
    )
    db.add(s)
    await db.flush()
    return s


async def _make_character(
    db: AsyncSession,
    *,
    character_id: UUID | None = None,
) -> Character:
    c = Character(
        character_id=character_id or uuid4(),
        behavior_profile={},
    )
    db.add(c)
    await db.flush()
    return c


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


async def test_assert_knowledge_inserts_record(session: AsyncSession) -> None:
    sess_id = uuid4()
    char_id = uuid4()
    fact = await _make_fact(session, session_id=sess_id)

    ks = await assert_knowledge(
        session,
        session_id=sess_id,
        character_id=char_id,
        fact_id=fact.fact_id,
        confidence=1.0,
    )

    assert ks.ks_id is not None
    assert ks.fact_id == fact.fact_id
    assert ks.character_id == char_id
    assert ks.confidence == 1.0
    assert ks.superseded_by is None

    # Re-query by ks_id to confirm persistence
    from sqlalchemy import select

    result = await session.execute(
        select(KnowledgeState).where(KnowledgeState.ks_id == ks.ks_id)
    )
    fetched = result.scalar_one()
    assert fetched.fact_id == fact.fact_id
    assert fetched.character_id == char_id


async def test_assert_knowledge_provenance_chain_round_trips(
    session: AsyncSession,
) -> None:
    sess_id = uuid4()
    char_id = uuid4()
    fact = await _make_fact(session, session_id=sess_id)

    uid_a = uuid4()
    uid_b = uuid4()

    ks = await assert_knowledge(
        session,
        session_id=sess_id,
        character_id=char_id,
        fact_id=fact.fact_id,
        provenance_chain=[uid_a, uid_b],
    )

    # Expire to force re-read from DB
    session.expire(ks)
    await session.refresh(ks)

    chain = ks.provenance_chain
    assert isinstance(chain, list)
    assert len(chain) == 2
    assert chain[0] == str(uid_a).lower()
    assert chain[1] == str(uid_b).lower()


async def test_assert_knowledge_confidence_below_1(session: AsyncSession) -> None:
    sess_id = uuid4()
    char_id = uuid4()
    fact = await _make_fact(session, session_id=sess_id)

    ks = await assert_knowledge(
        session,
        session_id=sess_id,
        character_id=char_id,
        fact_id=fact.fact_id,
        confidence=0.42,
    )

    session.expire(ks)
    await session.refresh(ks)

    assert abs(ks.confidence - 0.42) < 1e-9


async def test_get_character_knowledge_excludes_other_characters(
    session: AsyncSession,
) -> None:
    sess_id = uuid4()
    char_a = uuid4()
    char_b = uuid4()
    fact = await _make_fact(session, session_id=sess_id)

    await assert_knowledge(
        session, session_id=sess_id, character_id=char_a, fact_id=fact.fact_id
    )
    await assert_knowledge(
        session, session_id=sess_id, character_id=char_b, fact_id=fact.fact_id
    )

    results = await get_character_knowledge(
        session, session_id=sess_id, character_id=char_a
    )
    assert len(results) == 1
    assert results[0].character_id == char_a


async def test_get_character_knowledge_excludes_other_sessions(
    session: AsyncSession,
) -> None:
    sess_a = uuid4()
    sess_b = uuid4()
    char_id = uuid4()
    fact_a = await _make_fact(session, session_id=sess_a)
    fact_b = await _make_fact(session, session_id=sess_b)

    await assert_knowledge(
        session, session_id=sess_a, character_id=char_id, fact_id=fact_a.fact_id
    )
    await assert_knowledge(
        session, session_id=sess_b, character_id=char_id, fact_id=fact_b.fact_id
    )

    results = await get_character_knowledge(
        session, session_id=sess_a, character_id=char_id
    )
    assert len(results) == 1
    assert results[0].session_id == sess_a


async def test_get_character_knowledge_excludes_superseded_records(
    session: AsyncSession,
) -> None:
    sess_id = uuid4()
    char_id = uuid4()
    fact = await _make_fact(session, session_id=sess_id)

    original = await assert_knowledge(
        session, session_id=sess_id, character_id=char_id, fact_id=fact.fact_id
    )
    replacement = await assert_knowledge(
        session, session_id=sess_id, character_id=char_id, fact_id=fact.fact_id
    )
    await revoke_knowledge(
        session, existing_ks_id=original.ks_id, replacement=replacement
    )

    results = await get_character_knowledge(
        session, session_id=sess_id, character_id=char_id
    )
    returned_ids = [r.ks_id for r in results]
    assert original.ks_id not in returned_ids
    assert replacement.ks_id in returned_ids


async def test_revoke_sets_superseded_by(session: AsyncSession) -> None:
    sess_id = uuid4()
    char_id = uuid4()
    fact = await _make_fact(session, session_id=sess_id)

    original = await assert_knowledge(
        session, session_id=sess_id, character_id=char_id, fact_id=fact.fact_id
    )
    replacement = await assert_knowledge(
        session, session_id=sess_id, character_id=char_id, fact_id=fact.fact_id
    )

    old = await revoke_knowledge(
        session, existing_ks_id=original.ks_id, replacement=replacement
    )

    assert old.superseded_by == replacement.ks_id


async def test_revoked_records_not_returned_by_get(session: AsyncSession) -> None:
    sess_id = uuid4()
    char_id = uuid4()
    fact = await _make_fact(session, session_id=sess_id)

    original = await assert_knowledge(
        session, session_id=sess_id, character_id=char_id, fact_id=fact.fact_id
    )
    replacement = await assert_knowledge(
        session, session_id=sess_id, character_id=char_id, fact_id=fact.fact_id
    )
    await revoke_knowledge(
        session, existing_ks_id=original.ks_id, replacement=replacement
    )

    results = await get_character_knowledge(
        session, session_id=sess_id, character_id=char_id
    )
    assert all(r.ks_id != original.ks_id for r in results)
