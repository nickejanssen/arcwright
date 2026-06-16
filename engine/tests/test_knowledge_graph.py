"""Tests for engine/knowledge/graph.py — knowledge graph assert/revoke/query."""

from __future__ import annotations

from uuid import UUID, uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from engine.db.orm import Base, Character, Fact, KnowledgeState, Session
from engine.db.testing import patch_metadata_for_sqlite
from engine.knowledge import (
    assert_knowledge,
    get_character_knowledge,
    revoke_fact_in_session,
    revoke_knowledge,
)

patch_metadata_for_sqlite()


@pytest.fixture
async def session() -> AsyncSession:  # type: ignore[override]
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as sess:  # type: ignore[attr-defined]
        yield sess  # type: ignore[misc]

    await engine.dispose()


# Helpers ---------------------------------------------------------------------


async def _make_session_row(
    db: AsyncSession, *, session_id: UUID | None = None
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
    db: AsyncSession, *, character_id: UUID | None = None
) -> Character:
    c = Character(character_id=character_id or uuid4(), behavior_profile={})
    db.add(c)
    await db.flush()
    return c


# Assert ----------------------------------------------------------------------


async def test_assert_inserts_fact_and_knowledge_state(session: AsyncSession) -> None:
    sess_id = uuid4()
    char_id = uuid4()

    ks = await assert_knowledge(
        session,
        session_id=sess_id,
        character_id=char_id,
        fact_type="clue",
        fact_content={"detail": "library, 9pm"},
    )

    assert ks.ks_id is not None
    assert ks.character_id == char_id
    assert ks.confidence == 1.0
    assert ks.superseded_by is None

    facts = (await session.execute(select(Fact))).scalars().all()
    assert len(facts) == 1
    assert facts[0].fact_id == ks.fact_id
    assert facts[0].fact_type == "clue"
    assert facts[0].fact_content == {"detail": "library, 9pm"}


async def test_assert_dedupes_identical_facts_in_same_session(
    session: AsyncSession,
) -> None:
    sess_id = uuid4()
    char_a = uuid4()
    char_b = uuid4()

    ks_a = await assert_knowledge(
        session,
        session_id=sess_id,
        character_id=char_a,
        fact_type="clue",
        fact_content={"detail": "library, 9pm"},
    )
    ks_b = await assert_knowledge(
        session,
        session_id=sess_id,
        character_id=char_b,
        fact_type="clue",
        fact_content={"detail": "library, 9pm"},
    )

    assert ks_a.fact_id == ks_b.fact_id
    assert ks_a.ks_id != ks_b.ks_id

    facts = (await session.execute(select(Fact))).scalars().all()
    assert len(facts) == 1


async def test_assert_different_session_creates_new_fact(session: AsyncSession) -> None:
    sess_a = uuid4()
    sess_b = uuid4()
    char_id = uuid4()
    content = {"detail": "library, 9pm"}

    ks_a = await assert_knowledge(
        session,
        session_id=sess_a,
        character_id=char_id,
        fact_type="clue",
        fact_content=content,
    )
    ks_b = await assert_knowledge(
        session,
        session_id=sess_b,
        character_id=char_id,
        fact_type="clue",
        fact_content=content,
    )

    assert ks_a.fact_id != ks_b.fact_id
    facts = (await session.execute(select(Fact))).scalars().all()
    assert len(facts) == 2


async def test_assert_direct_observation_chain_is_just_self(
    session: AsyncSession,
) -> None:
    sess_id = uuid4()
    char_id = uuid4()
    ks = await assert_knowledge(
        session,
        session_id=sess_id,
        character_id=char_id,
        fact_type="clue",
        fact_content={"x": 1},
    )
    assert ks.provenance_chain == [str(char_id).lower()]


async def test_assert_with_source_extends_chain(session: AsyncSession) -> None:
    sess_id = uuid4()
    witness = uuid4()
    detective = uuid4()

    await assert_knowledge(
        session,
        session_id=sess_id,
        character_id=witness,
        fact_type="clue",
        fact_content={"x": 1},
    )
    ks = await assert_knowledge(
        session,
        session_id=sess_id,
        character_id=detective,
        fact_type="clue",
        fact_content={"x": 1},
        source_character_id=witness,
    )

    assert ks.provenance_chain == [str(witness).lower(), str(detective).lower()]


async def test_assert_with_unknown_source_starts_two_link_chain(
    session: AsyncSession,
) -> None:
    sess_id = uuid4()
    detective = uuid4()
    rumored_source = uuid4()

    ks = await assert_knowledge(
        session,
        session_id=sess_id,
        character_id=detective,
        fact_type="clue",
        fact_content={"x": 1},
        source_character_id=rumored_source,
    )

    assert ks.provenance_chain == [
        str(rumored_source).lower(),
        str(detective).lower(),
    ]


async def test_assert_records_confidence(session: AsyncSession) -> None:
    sess_id = uuid4()
    ks = await assert_knowledge(
        session,
        session_id=sess_id,
        character_id=uuid4(),
        fact_type="clue",
        fact_content={"x": 1},
        confidence=0.42,
    )
    assert abs(ks.confidence - 0.42) < 1e-9


# Query -----------------------------------------------------------------------


async def test_query_isolates_by_character(session: AsyncSession) -> None:
    sess_id = uuid4()
    char_a = uuid4()
    char_b = uuid4()

    await assert_knowledge(
        session,
        session_id=sess_id,
        character_id=char_a,
        fact_type="clue",
        fact_content={"x": 1},
    )
    await assert_knowledge(
        session,
        session_id=sess_id,
        character_id=char_b,
        fact_type="clue",
        fact_content={"x": 1},
    )

    results = await get_character_knowledge(
        session, session_id=sess_id, character_id=char_a
    )
    assert len(results) == 1
    assert results[0].character_id == char_a


async def test_query_isolates_by_session(session: AsyncSession) -> None:
    sess_a = uuid4()
    sess_b = uuid4()
    char_id = uuid4()

    await assert_knowledge(
        session,
        session_id=sess_a,
        character_id=char_id,
        fact_type="clue",
        fact_content={"x": 1},
    )
    await assert_knowledge(
        session,
        session_id=sess_b,
        character_id=char_id,
        fact_type="clue",
        fact_content={"x": 1},
    )

    results = await get_character_knowledge(
        session, session_id=sess_a, character_id=char_id
    )
    assert len(results) == 1
    assert results[0].session_id == sess_a


# Revoke (low-level) ----------------------------------------------------------


async def test_revoke_knowledge_sets_superseded_by(session: AsyncSession) -> None:
    sess_id = uuid4()
    char_id = uuid4()

    original = await assert_knowledge(
        session,
        session_id=sess_id,
        character_id=char_id,
        fact_type="clue",
        fact_content={"x": 1},
    )
    replacement = await assert_knowledge(
        session,
        session_id=sess_id,
        character_id=char_id,
        fact_type="clue",
        fact_content={"x": 1},
    )
    old = await revoke_knowledge(
        session, existing_ks_id=original.ks_id, replacement=replacement
    )

    assert old.superseded_by == replacement.ks_id


async def test_query_excludes_superseded_records(session: AsyncSession) -> None:
    sess_id = uuid4()
    char_id = uuid4()

    original = await assert_knowledge(
        session,
        session_id=sess_id,
        character_id=char_id,
        fact_type="clue",
        fact_content={"x": 1},
    )
    replacement = await assert_knowledge(
        session,
        session_id=sess_id,
        character_id=char_id,
        fact_type="clue",
        fact_content={"x": 1},
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


# Revoke (mass, by fact_id) ---------------------------------------------------


async def test_revoke_fact_tombstones_all_active_records(
    session: AsyncSession,
) -> None:
    sess_id = uuid4()
    char_a = uuid4()
    char_b = uuid4()
    content = {"x": 1}

    ks_a = await assert_knowledge(
        session,
        session_id=sess_id,
        character_id=char_a,
        fact_type="clue",
        fact_content=content,
    )
    ks_b = await assert_knowledge(
        session,
        session_id=sess_id,
        character_id=char_b,
        fact_type="clue",
        fact_content=content,
    )

    tombstones = await revoke_fact_in_session(
        session, session_id=sess_id, fact_id=ks_a.fact_id
    )

    assert len(tombstones) == 2
    for ts in tombstones:
        assert ts.confidence == 0.0
        assert ts.superseded_by == ts.ks_id

    a_active = await get_character_knowledge(
        session, session_id=sess_id, character_id=char_a
    )
    b_active = await get_character_knowledge(
        session, session_id=sess_id, character_id=char_b
    )
    assert a_active == []
    assert b_active == []

    # Originals are not deleted; only superseded.
    surviving = (
        (
            await session.execute(
                select(KnowledgeState).where(
                    KnowledgeState.ks_id.in_([ks_a.ks_id, ks_b.ks_id])
                )
            )
        )
        .scalars()
        .all()
    )
    assert len(surviving) == 2
    for row in surviving:
        assert row.superseded_by is not None
        assert row.superseded_by != row.ks_id


async def test_revoke_fact_is_idempotent(session: AsyncSession) -> None:
    sess_id = uuid4()
    char_id = uuid4()
    ks = await assert_knowledge(
        session,
        session_id=sess_id,
        character_id=char_id,
        fact_type="clue",
        fact_content={"x": 1},
    )
    await revoke_fact_in_session(session, session_id=sess_id, fact_id=ks.fact_id)
    second = await revoke_fact_in_session(
        session, session_id=sess_id, fact_id=ks.fact_id
    )
    assert second == []
