"""Tests for the pre-generation knowledge constraint hook."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from uuid import UUID, uuid4

import pytest
from sqlalchemy import JSON, Text, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.schema import ColumnDefault, DefaultClause

from engine.characters import build_character_generation_context
from engine.db.orm import Base, Fact
from engine.knowledge import assert_knowledge, revoke_knowledge

_PATCHED = False


def _patch_metadata_for_sqlite() -> None:
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


_patch_metadata_for_sqlite()


@pytest.fixture
async def session() -> AsyncSession:  # type: ignore[override]
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as sess:  # type: ignore[attr-defined]
        yield sess  # type: ignore[misc]

    await engine.dispose()


async def _make_fact(
    session: AsyncSession,
    *,
    session_id: UUID,
    fact_id: UUID | None = None,
    fact_type: str = "test_type",
    fact_content: dict[str, str] | None = None,
) -> Fact:
    fact = Fact(
        fact_id=fact_id or uuid4(),
        session_id=session_id,
        fact_type=fact_type,
        fact_content=fact_content or {"key": "value"},
    )
    session.add(fact)
    await session.flush()
    return fact


async def test_build_character_generation_context_scopes_known_and_unknown_facts(
    session: AsyncSession,
) -> None:
    session_id = uuid4()
    other_session_id = uuid4()
    character_id = uuid4()
    other_character_id = uuid4()

    known_fact = await _make_fact(
        session,
        session_id=session_id,
        fact_type="known",
        fact_content={"fact": "known"},
    )
    unknown_fact = await _make_fact(
        session,
        session_id=session_id,
        fact_type="unknown",
        fact_content={"fact": "unknown"},
    )
    other_character_fact = await _make_fact(
        session,
        session_id=session_id,
        fact_type="other-character",
        fact_content={"fact": "other-character"},
    )
    other_session_fact = await _make_fact(
        session,
        session_id=other_session_id,
        fact_type="other-session",
        fact_content={"fact": "other-session"},
    )

    await assert_knowledge(
        session,
        session_id=session_id,
        character_id=character_id,
        fact_id=known_fact.fact_id,
        confidence=0.8,
        provenance_chain=[uuid4(), character_id],
    )
    await assert_knowledge(
        session,
        session_id=session_id,
        character_id=other_character_id,
        fact_id=other_character_fact.fact_id,
    )
    await assert_knowledge(
        session,
        session_id=other_session_id,
        character_id=character_id,
        fact_id=other_session_fact.fact_id,
    )

    context = await build_character_generation_context(
        session,
        session_id=session_id,
        character_id=character_id,
    )

    assert [fact.fact_id for fact in context.known_facts] == [known_fact.fact_id]
    assert context.known_facts[0].confidence == 0.8
    assert context.known_facts[0].provenance_chain_length == 2
    assert set(fact.fact_id for fact in context.unknown_facts) == {
        unknown_fact.fact_id,
        other_character_fact.fact_id,
    }
    assert all(
        fact.fact_id != other_session_fact.fact_id for fact in context.unknown_facts
    )


async def test_build_character_generation_context_excludes_superseded_facts(
    session: AsyncSession,
) -> None:
    session_id = uuid4()
    character_id = uuid4()
    original_fact = await _make_fact(session, session_id=session_id)
    replacement_fact = await _make_fact(session, session_id=session_id)

    original = await assert_knowledge(
        session,
        session_id=session_id,
        character_id=character_id,
        fact_id=original_fact.fact_id,
    )
    replacement = await assert_knowledge(
        session,
        session_id=session_id,
        character_id=character_id,
        fact_id=replacement_fact.fact_id,
    )
    await revoke_knowledge(
        session, existing_ks_id=original.ks_id, replacement=replacement
    )

    context = await build_character_generation_context(
        session,
        session_id=session_id,
        character_id=character_id,
    )

    assert [fact.fact_id for fact in context.known_facts] == [replacement_fact.fact_id]
    assert [fact.fact_id for fact in context.unknown_facts] == [original_fact.fact_id]


async def test_build_character_generation_context_is_stably_ordered(
    session: AsyncSession,
) -> None:
    session_id = uuid4()
    character_id = uuid4()

    early_known_fact = await _make_fact(
        session,
        session_id=session_id,
        fact_id=UUID("00000000-0000-0000-0000-0000000000a2"),
        fact_content={"fact": "early"},
    )
    later_known_fact = await _make_fact(
        session,
        session_id=session_id,
        fact_id=UUID("00000000-0000-0000-0000-0000000000a1"),
        fact_content={"fact": "later"},
    )
    unknown_fact_b = await _make_fact(
        session,
        session_id=session_id,
        fact_id=UUID("00000000-0000-0000-0000-0000000000c2"),
        fact_content={"fact": "unknown-b"},
    )
    unknown_fact_a = await _make_fact(
        session,
        session_id=session_id,
        fact_id=UUID("00000000-0000-0000-0000-0000000000c1"),
        fact_content={"fact": "unknown-a"},
    )

    later_state = await assert_knowledge(
        session,
        session_id=session_id,
        character_id=character_id,
        fact_id=later_known_fact.fact_id,
    )
    early_state = await assert_knowledge(
        session,
        session_id=session_id,
        character_id=character_id,
        fact_id=early_known_fact.fact_id,
    )
    later_state.asserted_at = datetime(2026, 1, 2, tzinfo=timezone.utc)
    early_state.asserted_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
    await session.flush()

    first_context = await build_character_generation_context(
        session,
        session_id=session_id,
        character_id=character_id,
    )
    second_context = await build_character_generation_context(
        session,
        session_id=session_id,
        character_id=character_id,
    )

    assert [fact.fact_id for fact in first_context.known_facts] == [
        early_known_fact.fact_id,
        later_known_fact.fact_id,
    ]
    assert [fact.fact_id for fact in first_context.unknown_facts] == [
        unknown_fact_a.fact_id,
        unknown_fact_b.fact_id,
    ]
    assert first_context == second_context


async def test_build_character_generation_context_keeps_same_character_id_session_scoped(
    session: AsyncSession,
) -> None:
    character_id = uuid4()
    session_a = uuid4()
    session_b = uuid4()
    fact_a = await _make_fact(session, session_id=session_a, fact_content={"fact": "a"})
    fact_b = await _make_fact(session, session_id=session_b, fact_content={"fact": "b"})

    await assert_knowledge(
        session,
        session_id=session_a,
        character_id=character_id,
        fact_id=fact_a.fact_id,
    )
    await assert_knowledge(
        session,
        session_id=session_b,
        character_id=character_id,
        fact_id=fact_b.fact_id,
    )

    context = await build_character_generation_context(
        session,
        session_id=session_a,
        character_id=character_id,
    )

    assert [fact.fact_id for fact in context.known_facts] == [fact_a.fact_id]
    assert all(fact.fact_id != fact_b.fact_id for fact in context.unknown_facts)
