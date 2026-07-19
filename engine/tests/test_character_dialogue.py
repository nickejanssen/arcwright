"""Tests for the AW-212 character dialogue pipeline."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch
from uuid import UUID, uuid4

import pytest
from sqlalchemy import JSON, Text, select, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.schema import ColumnDefault, DefaultClause

from engine.case.models import AuthorizedFalsehood
from engine.characters import (
    KnowledgeConstraintViolation,
    build_character_generation_context,
    build_dialogue_messages,
    generate_character_dialogue,
)
from engine.characters.context import (
    BehaviorProfileContext,
    CharacterGenerationContext,
)
from engine.db.orm import Base, Character, Event, Fact, Session, SessionParticipant
from engine.knowledge import assert_knowledge, get_character_knowledge
from engine.resources.models import EffectDefinition, EffectFamily, ResourceBalance
from engine.resources.resolver import ResourceResolver
from engine.routing.router import RouteResult, resolve_model_key
from engine.safety import L2_BLOCK_SENTINEL, NEUTRAL_L2_BRIDGE

CHARACTER_STANDARD_MODEL = resolve_model_key("character_dialogue", "standard")

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


async def _make_session_row(
    db: AsyncSession,
    *,
    session_id: UUID | None = None,
) -> Session:
    row = Session(
        session_id=session_id or uuid4(),
        arc_id="nightcap",
        status="active",
        host_account_id=uuid4(),
        current_beat_id="opening_move",
        quality_tier="standard",
        player_count=4,
    )
    db.add(row)
    await db.flush()
    return row


async def _make_character(
    db: AsyncSession,
    *,
    character_id: UUID | None = None,
) -> Character:
    character = Character(
        character_id=character_id or uuid4(),
        behavior_profile={
            "personality": {
                "traits": ["evasive"],
                "communication_style": "answers with careful understatement",
            },
            "goals": ["Appear cooperative"],
            "secrets": [{"content": "I am hiding a debt"}],
            "tells": ["Pauses before discussing money"],
        },
    )
    db.add(character)
    await db.flush()
    return character


async def _make_participant(
    db: AsyncSession,
    *,
    session_id: UUID,
    character_id: UUID,
) -> SessionParticipant:
    participant = SessionParticipant(
        participant_id=uuid4(),
        session_id=session_id,
        character_id=character_id,
        account_id=None,
        join_token="join-token",
        surface_type="phone",
        is_ai_controlled=True,
    )
    db.add(participant)
    await db.flush()
    return participant


async def _make_fact(
    db: AsyncSession,
    *,
    session_id: UUID,
    fact_content: dict[str, object],
    fact_type: str = "clue",
) -> Fact:
    fact = Fact(
        fact_id=uuid4(),
        session_id=session_id,
        fact_type=fact_type,
        fact_content=fact_content,
    )
    db.add(fact)
    await db.flush()
    return fact


def _route_result(content: str) -> RouteResult:
    return RouteResult(
        content=content,
        model_used=CHARACTER_STANDARD_MODEL,
        input_tokens=100,
        output_tokens=30,
        latency_ms=120,
        used_fallback=False,
    )


def _blocked_route_result() -> RouteResult:
    return RouteResult(
        content=NEUTRAL_L2_BRIDGE,
        model_used=L2_BLOCK_SENTINEL,
        input_tokens=0,
        output_tokens=0,
        latency_ms=0,
        used_fallback=False,
    )


async def _make_dialogue_fixture(
    db: AsyncSession,
) -> tuple[Session, Character, Fact, Fact]:
    session_row = await _make_session_row(db)
    character = await _make_character(db)
    await _make_participant(
        db,
        session_id=session_row.session_id,
        character_id=character.character_id,
    )
    known_fact = await _make_fact(
        db,
        session_id=session_row.session_id,
        fact_content={"detail": "The ledger was open on the study desk"},
    )
    unknown_fact = await _make_fact(
        db,
        session_id=session_row.session_id,
        fact_content={"detail": "The hidden safe is behind the portrait"},
    )
    await assert_knowledge(
        db,
        session_id=session_row.session_id,
        character_id=character.character_id,
        fact_type=known_fact.fact_type,
        fact_content=known_fact.fact_content,
        confidence=0.9,
    )
    return session_row, character, known_fact, unknown_fact


async def test_dialogue_messages_include_known_and_not_known_blocks(
    session: AsyncSession,
) -> None:
    session_row, character, known_fact, unknown_fact = await _make_dialogue_fixture(
        session
    )

    context = await build_character_generation_context(
        session,
        session_id=session_row.session_id,
        character_id=character.character_id,
    )
    messages = build_dialogue_messages(
        context,
        player_input="What did you see in the study?",
        current_beat_id="opening_move",
        scene_goal="Answer without leaking private information.",
    )

    system_prompt = messages[0]["content"]
    assert "[KNOWN KNOWLEDGE CONSTRAINTS]" in system_prompt
    assert "[NOT-KNOWN KNOWLEDGE CONSTRAINTS]" in system_prompt
    assert str(known_fact.fact_id) in system_prompt
    assert "The ledger was open on the study desk" in system_prompt
    assert str(unknown_fact.fact_id) in system_prompt
    assert "The hidden safe is behind the portrait" in system_prompt
    assert messages[1] == {
        "role": "user",
        "content": "What did you see in the study?",
    }


def test_dialogue_messages_render_authorized_falsehood_verbatim_without_evidence() -> (
    None
):
    context = _dialogue_context_for_lie()
    falsehood = AuthorizedFalsehood(
        falsehood_id="lie-1",
        speaker_id=str(context.character_id),
        topic="location",
        claim_text="I was in the garden.",
        contradicted_by=["evidence-secret"],
    )

    first = build_dialogue_messages(
        context,
        player_input="Where were you?",
        matched_answer=falsehood,
    )[0]["content"]
    second = build_dialogue_messages(
        context,
        player_input="Where were you again?",
        matched_answer=falsehood,
    )[0]["content"]

    assert "I was in the garden." in first
    assert "I was in the garden." in second
    assert "evidence-secret" not in first
    assert "slightly less specific" in first
    assert (
        first.split("[AUTHORIZED FALSEHOOD]")[1].split("[END AUTHORIZED FALSEHOOD]")[0]
        == second.split("[AUTHORIZED FALSEHOOD]")[1].split(
            "[END AUTHORIZED FALSEHOOD]"
        )[0]
    )


def _dialogue_context_for_lie() -> CharacterGenerationContext:
    return CharacterGenerationContext(
        session_id=uuid4(),
        character_id=uuid4(),
        behavior_profile=BehaviorProfileContext(
            personality={}, goals=(), secrets=(), tells=()
        ),
        relationship_dispositions=(),
        is_ai_controlled=True,
        known_facts=(),
        unknown_facts=(),
    )


async def test_generate_character_dialogue_routes_through_safe_generation_entrypoint(
    session: AsyncSession,
) -> None:
    session_row, character, known_fact, unknown_fact = await _make_dialogue_fixture(
        session
    )
    call_order: list[str] = []

    async def spy_get_character_knowledge(*args: object, **kwargs: object) -> object:
        call_order.append("knowledge")
        return await get_character_knowledge(*args, **kwargs)  # type: ignore[arg-type]

    async def spy_generate(*args: object, **kwargs: object) -> RouteResult:
        call_order.append("generate")
        return _route_result("I noticed the ledger in the study.")

    with (
        patch(
            "engine.characters.context.get_character_knowledge",
            new_callable=AsyncMock,
            side_effect=spy_get_character_knowledge,
        ) as mock_get_knowledge,
        patch(
            "engine.characters.dialogue.generate",
            new_callable=AsyncMock,
            side_effect=spy_generate,
        ) as mock_generate,
    ):
        event = await generate_character_dialogue(
            session,
            session_id=session_row.session_id,
            character_id=character.character_id,
            player_input="What did you notice?",
            quality_tier="standard",
            target_audience="specific_player",
            target_player_id=uuid4(),
            current_beat_id="opening_move",
        )

    mock_get_knowledge.assert_awaited_once()
    mock_generate.assert_awaited_once()
    assert call_order == ["knowledge", "generate"]
    kwargs = mock_generate.await_args.kwargs
    assert kwargs["task_type"] == "character_dialogue"
    assert kwargs["quality_tier"] == "standard"
    assert kwargs["session_id"] == session_row.session_id
    assert kwargs["messages"][0]["role"] == "system"
    assert str(known_fact.fact_id) in kwargs["messages"][0]["content"]
    assert str(unknown_fact.fact_id) in kwargs["messages"][0]["content"]
    assert event.session_id == session_row.session_id
    assert event.actor_character_id == character.character_id
    assert event.event_type == "dialogue"
    assert event.content == "I noticed the ledger in the study."
    assert event.payload["knowledge_constraint"]["known_fact_ids"] == [
        str(known_fact.fact_id)
    ]
    assert event.payload["knowledge_constraint"]["unknown_fact_ids"] == [
        str(unknown_fact.fact_id)
    ]


async def test_generate_character_dialogue_matches_falsehood_for_question_topic(
    session: AsyncSession,
) -> None:
    session_row, character, _, _ = await _make_dialogue_fixture(session)
    falsehood = AuthorizedFalsehood(
        falsehood_id="lie-1",
        speaker_id="s1",
        topic="location",
        claim_text="I was in the garden.",
        contradicted_by=["evidence-secret"],
    )

    with patch(
        "engine.characters.dialogue.generate",
        new_callable=AsyncMock,
        return_value=_route_result("I was in the garden."),
    ) as mock_generate:
        await generate_character_dialogue(
            session,
            session_id=session_row.session_id,
            character_id=character.character_id,
            player_input="Where were you?",
            quality_tier="standard",
            authorized_falsehoods=[falsehood],
            question_topic="location",
        )

    prompt = mock_generate.await_args.kwargs["messages"][0]["content"]
    assert "I was in the garden." in prompt
    assert "evidence-secret" not in prompt


async def test_generate_character_dialogue_applies_targeted_resource_pressure(
    session: AsyncSession,
) -> None:
    session_row, character, _, _ = await _make_dialogue_fixture(session)
    activator_id = str(uuid4())
    resolver = ResourceResolver()
    resolver.set_balance(
        ResourceBalance(
            player_id=activator_id,
            session_id=str(session_row.session_id),
            current_amount=5,
            bank_cap=20,
            protected_floor=0,
        )
    )
    activation = resolver.activate(
        effect=EffectDefinition(
            effect_key="sabotage.rattle_the_witness",
            family=EffectFamily.witness_pressure,
            cost=2,
            requires_target=True,
            is_offensive=True,
        ),
        activator_id=activator_id,
        target_id=str(character.character_id),
        window_id="question-1",
        beat_id="beat-1",
        now=datetime.now(UTC),
    )

    with patch(
        "engine.characters.dialogue.generate",
        new_callable=AsyncMock,
        return_value=_route_result("I noticed the ledger in the study."),
    ) as mock_generate:
        await generate_character_dialogue(
            session,
            session_id=session_row.session_id,
            character_id=character.character_id,
            player_input="What did you notice?",
            quality_tier="standard",
            social_pressure=0.8,
            pressure_activation=activation,
            pressure_effect_key="sabotage.rattle_the_witness",
        )

    prompt = mock_generate.await_args.kwargs["messages"][0]["content"]
    assert "social_pressure: 1.00" in prompt


async def test_generate_character_dialogue_persists_allowed_dialogue_event(
    session: AsyncSession,
) -> None:
    session_row, character, _, _ = await _make_dialogue_fixture(session)

    with patch(
        "engine.characters.dialogue.generate",
        new_callable=AsyncMock,
        return_value=_route_result("The ledger looked recently handled."),
    ):
        returned = await generate_character_dialogue(
            session,
            session_id=session_row.session_id,
            character_id=character.character_id,
            player_input="Say what you saw.",
            quality_tier="standard",
            target_audience="all",
        )

    persisted = await session.scalar(
        select(Event).where(Event.event_id == returned.event_id)
    )

    assert persisted is not None
    assert persisted.session_id == session_row.session_id
    assert persisted.actor_char_id == character.character_id
    assert persisted.event_type == "dialogue"
    assert persisted.content_text == "The ledger looked recently handled."
    assert persisted.payload["target_audience"] == "all"
    assert persisted.payload["task_type"] == "character_dialogue"


async def test_generate_character_dialogue_rejects_unknown_fact_output(
    session: AsyncSession,
) -> None:
    session_row, character, _, _ = await _make_dialogue_fixture(session)

    with patch(
        "engine.characters.dialogue.generate",
        new_callable=AsyncMock,
        return_value=_route_result("The hidden safe is behind the portrait."),
    ):
        with pytest.raises(KnowledgeConstraintViolation):
            await generate_character_dialogue(
                session,
                session_id=session_row.session_id,
                character_id=character.character_id,
                player_input="Tell me a secret.",
                quality_tier="standard",
            )

    events = (
        await session.scalars(
            select(Event).where(
                Event.session_id == session_row.session_id,
                Event.event_type == "dialogue",
            )
        )
    ).all()
    assert events == []


async def test_generate_character_dialogue_rejects_structured_short_unknown_fact(
    session: AsyncSession,
) -> None:
    session_row = await _make_session_row(session)
    character = await _make_character(session)
    await _make_participant(
        session,
        session_id=session_row.session_id,
        character_id=character.character_id,
    )
    unknown_fact = await _make_fact(
        session,
        session_id=session_row.session_id,
        fact_content={"object": "safe", "location": "portrait"},
    )

    with patch(
        "engine.characters.dialogue.generate",
        new_callable=AsyncMock,
        return_value=_route_result("The safe is behind the portrait."),
    ):
        with pytest.raises(KnowledgeConstraintViolation):
            await generate_character_dialogue(
                session,
                session_id=session_row.session_id,
                character_id=character.character_id,
                player_input="Where would someone hide papers?",
                quality_tier="standard",
            )

    events = (
        await session.scalars(
            select(Event).where(
                Event.session_id == session_row.session_id,
                Event.event_type == "dialogue",
            )
        )
    ).all()
    assert events == []

    context = await build_character_generation_context(
        session,
        session_id=session_row.session_id,
        character_id=character.character_id,
    )
    assert [fact.fact_id for fact in context.unknown_facts] == [unknown_fact.fact_id]


async def test_generate_character_dialogue_marks_safety_block_without_dialogue_event(
    session: AsyncSession,
) -> None:
    session_row, character, _, _ = await _make_dialogue_fixture(session)

    with patch(
        "engine.characters.dialogue.generate",
        new_callable=AsyncMock,
        return_value=_blocked_route_result(),
    ):
        returned = await generate_character_dialogue(
            session,
            session_id=session_row.session_id,
            character_id=character.character_id,
            player_input="Blocked input.",
            quality_tier="standard",
        )

    events = (
        await session.scalars(
            select(Event).where(Event.session_id == session_row.session_id)
        )
    ).all()
    event_types = [event.event_type for event in events]
    assert "dialogue_blocked" in event_types
    dialogue_blocked_event = next(
        e for e in events if e.event_type == "dialogue_blocked"
    )
    assert dialogue_blocked_event.actor_char_id is None
    assert dialogue_blocked_event.content_text is None
    assert dialogue_blocked_event.payload["safety_blocked"] is True
    assert dialogue_blocked_event.payload["safety_layer"] == "L2"

    assert returned.event_type == "dialogue_blocked"
    assert returned.actor_character_id is None
    assert returned.content == NEUTRAL_L2_BRIDGE


async def test_generate_character_dialogue_does_not_emit_out_of_scope_events(
    session: AsyncSession,
) -> None:
    session_row, character, _, _ = await _make_dialogue_fixture(session)

    with patch(
        "engine.characters.dialogue.generate",
        new_callable=AsyncMock,
        return_value=_route_result("I only know about the ledger."),
    ):
        await generate_character_dialogue(
            session,
            session_id=session_row.session_id,
            character_id=character.character_id,
            player_input="What do you know?",
            quality_tier="standard",
        )

    events = (
        await session.scalars(
            select(Event).where(Event.session_id == session_row.session_id)
        )
    ).all()
    event_types = {event.event_type for event in events}

    assert event_types == {
        "answer_generation_latency",
        "dialogue",
        "knowledge_constraint_activated",
    }
