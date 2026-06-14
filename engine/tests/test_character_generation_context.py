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
from engine.db.orm import Base, Character, Fact, RelationshipState, SessionParticipant
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


async def _make_character(
    session: AsyncSession,
    *,
    character_id: UUID | None = None,
    behavior_profile: dict[str, object] | None = None,
) -> Character:
    character = Character(
        character_id=character_id or uuid4(),
        behavior_profile=behavior_profile or {},
    )
    session.add(character)
    await session.flush()
    return character


async def _make_participant(
    session: AsyncSession,
    *,
    session_id: UUID,
    character_id: UUID,
    is_ai_controlled: bool,
) -> SessionParticipant:
    participant = SessionParticipant(
        participant_id=uuid4(),
        session_id=session_id,
        character_id=character_id,
        account_id=None,
        join_token="join-token",
        surface_type="phone",
        is_ai_controlled=is_ai_controlled,
    )
    session.add(participant)
    await session.flush()
    return participant


async def _make_relationship(
    session: AsyncSession,
    *,
    session_id: UUID,
    source_character_id: UUID,
    target_character_id: UUID,
    trust_level: float,
    history_tag: str,
    current_affect: str,
) -> RelationshipState:
    relationship = RelationshipState(
        relationship_id=uuid4(),
        session_id=session_id,
        source_char_id=source_character_id,
        target_char_id=target_character_id,
        trust_level=trust_level,
        history_tag=history_tag,
        current_affect=current_affect,
    )
    session.add(relationship)
    await session.flush()
    return relationship


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


async def test_build_character_generation_context_includes_killer_behavior_profile(
    session: AsyncSession,
) -> None:
    session_id = uuid4()
    killer_id = uuid4()
    target_id = uuid4()
    await _make_character(session, character_id=target_id)
    await _make_character(
        session,
        character_id=killer_id,
        behavior_profile={
            "personality": {
                "traits": ["charming", "evasive"],
                "communication_style": "deflects with humor",
                "under_pressure_style": "over-precise about timings",
            },
            "goals": [
                "Conceal my role as the killer",
                "Redirect suspicion toward another guest",
            ],
            "secrets": [
                {
                    "content": "I killed the victim",
                    "concealment_priority": "highest",
                    "crumble_threshold": 0.9,
                }
            ],
            "tells": ["Mentions exact times without being asked"],
        },
    )
    await _make_participant(
        session,
        session_id=session_id,
        character_id=killer_id,
        is_ai_controlled=False,
    )
    await _make_relationship(
        session,
        session_id=session_id,
        source_character_id=killer_id,
        target_character_id=target_id,
        trust_level=0.2,
        history_tag="rivalry",
        current_affect="guarded",
    )

    context = await build_character_generation_context(
        session,
        session_id=session_id,
        character_id=killer_id,
    )

    assert context.behavior_profile.personality == {
        "traits": ["charming", "evasive"],
        "communication_style": "deflects with humor",
        "under_pressure_style": "over-precise about timings",
    }
    assert context.behavior_profile.goals == (
        "Conceal my role as the killer",
        "Redirect suspicion toward another guest",
    )
    assert context.behavior_profile.secrets == (
        {
            "content": "I killed the victim",
            "concealment_priority": "highest",
            "crumble_threshold": 0.9,
        },
    )
    assert context.behavior_profile.tells == (
        "Mentions exact times without being asked",
    )
    assert len(context.relationship_dispositions) == 1
    assert context.relationship_dispositions[0].target_character_id == target_id
    assert context.relationship_dispositions[0].trust == 0.2
    assert context.relationship_dispositions[0].history == "rivalry"
    assert context.relationship_dispositions[0].current_affect == "guarded"
    assert context.is_ai_controlled is False


async def test_build_character_generation_context_includes_non_killer_profile_for_ai(
    session: AsyncSession,
) -> None:
    session_id = uuid4()
    character_id = uuid4()
    target_id = uuid4()
    await _make_character(session, character_id=target_id)
    await _make_character(
        session,
        character_id=character_id,
        behavior_profile={
            "personality": {
                "traits": ["observant", "warm"],
                "communication_style": "answers directly",
                "under_pressure_style": "becomes quieter",
            },
            "goals": [
                "Find out who killed the victim",
                "Protect a professional embarrassment",
            ],
            "secrets": [
                {
                    "content": "I lied about where I was before dinner",
                    "concealment_priority": "medium",
                    "crumble_threshold": 0.5,
                }
            ],
            "tells": ["Looks away before discussing the study"],
        },
    )
    await _make_participant(
        session,
        session_id=session_id,
        character_id=character_id,
        is_ai_controlled=True,
    )
    await _make_relationship(
        session,
        session_id=session_id,
        source_character_id=character_id,
        target_character_id=target_id,
        trust_level=0.7,
        history_tag="old-friend",
        current_affect="protective",
    )

    context = await build_character_generation_context(
        session,
        session_id=session_id,
        character_id=character_id,
    )

    assert context.behavior_profile.personality == {
        "traits": ["observant", "warm"],
        "communication_style": "answers directly",
        "under_pressure_style": "becomes quieter",
    }
    assert context.behavior_profile.goals == (
        "Find out who killed the victim",
        "Protect a professional embarrassment",
    )
    assert context.behavior_profile.secrets == (
        {
            "content": "I lied about where I was before dinner",
            "concealment_priority": "medium",
            "crumble_threshold": 0.5,
        },
    )
    assert context.behavior_profile.tells == ("Looks away before discussing the study",)
    assert len(context.relationship_dispositions) == 1
    assert context.relationship_dispositions[0].target_character_id == target_id
    assert context.relationship_dispositions[0].trust == 0.7
    assert context.relationship_dispositions[0].history == "old-friend"
    assert context.relationship_dispositions[0].current_affect == "protective"
    assert context.is_ai_controlled is True


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
