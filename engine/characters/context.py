"""Generation-time character context assembly."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from engine.db.orm import (
    Character,
    Fact,
    KnowledgeState,
    RelationshipState,
    SessionParticipant,
)


@dataclass(frozen=True)
class KnownFactContext:
    fact_id: UUID
    fact_type: str
    fact_content: dict[str, Any]
    confidence: float
    provenance_chain: tuple[str, ...]
    provenance_chain_length: int


@dataclass(frozen=True)
class UnknownFactContext:
    fact_id: UUID
    fact_type: str
    fact_content: dict[str, Any]


@dataclass(frozen=True)
class BehaviorProfileContext:
    personality: dict[str, Any]
    goals: tuple[str, ...]
    secrets: tuple[dict[str, Any], ...]
    tells: tuple[str, ...]


@dataclass(frozen=True)
class RelationshipDispositionContext:
    target_character_id: UUID
    trust: float
    history: str | None
    current_affect: str | None


@dataclass(frozen=True)
class CharacterGenerationContext:
    session_id: UUID
    character_id: UUID
    behavior_profile: BehaviorProfileContext
    relationship_dispositions: tuple[RelationshipDispositionContext, ...]
    is_ai_controlled: bool | None
    known_facts: tuple[KnownFactContext, ...]
    unknown_facts: tuple[UnknownFactContext, ...]


async def build_character_generation_context(
    session: AsyncSession,
    *,
    session_id: UUID,
    character_id: UUID,
) -> CharacterGenerationContext:
    """Build the only sanctioned generation-time character context."""
    character = await session.get(Character, character_id)
    profile_data = dict(character.behavior_profile) if character is not None else {}
    behavior_profile = _build_behavior_profile_context(profile_data)

    participant_result = await session.execute(
        select(SessionParticipant)
        .where(
            SessionParticipant.session_id == session_id,
            SessionParticipant.character_id == character_id,
        )
        .order_by(SessionParticipant.participant_id)
    )
    participant = participant_result.scalars().first()

    relationships_result = await session.execute(
        select(RelationshipState)
        .where(
            RelationshipState.session_id == session_id,
            RelationshipState.source_char_id == character_id,
        )
        .order_by(RelationshipState.target_char_id)
    )
    relationships = tuple(
        RelationshipDispositionContext(
            target_character_id=relationship.target_char_id,
            trust=relationship.trust_level,
            history=relationship.history_tag,
            current_affect=relationship.current_affect,
        )
        for relationship in relationships_result.scalars().all()
    )

    known_result = await session.execute(
        select(KnowledgeState)
        .where(
            KnowledgeState.session_id == session_id,
            KnowledgeState.character_id == character_id,
            KnowledgeState.superseded_by.is_(None),
        )
        .order_by(KnowledgeState.asserted_at, KnowledgeState.fact_id)
        .options(selectinload(KnowledgeState.fact))
    )
    known_states = list(known_result.scalars().all())
    known_fact_ids = {state.fact_id for state in known_states}

    all_facts_result = await session.execute(
        select(Fact).where(Fact.session_id == session_id).order_by(Fact.fact_id)
    )
    all_session_facts = list(all_facts_result.scalars().all())

    known_facts = tuple(
        KnownFactContext(
            fact_id=state.fact_id,
            fact_type=state.fact.fact_type,
            fact_content=dict(state.fact.fact_content),
            confidence=state.confidence,
            provenance_chain=tuple(str(item) for item in state.provenance_chain),
            provenance_chain_length=len(state.provenance_chain),
        )
        for state in known_states
    )
    unknown_facts = tuple(
        UnknownFactContext(
            fact_id=fact.fact_id,
            fact_type=fact.fact_type,
            fact_content=dict(fact.fact_content),
        )
        for fact in all_session_facts
        if fact.fact_id not in known_fact_ids
    )

    return CharacterGenerationContext(
        session_id=session_id,
        character_id=character_id,
        behavior_profile=behavior_profile,
        relationship_dispositions=relationships,
        is_ai_controlled=(
            participant.is_ai_controlled if participant is not None else None
        ),
        known_facts=known_facts,
        unknown_facts=unknown_facts,
    )


def _build_behavior_profile_context(
    profile_data: dict[str, Any],
) -> BehaviorProfileContext:
    personality = profile_data.get("personality")
    goals = profile_data.get("goals")
    secrets = profile_data.get("secrets")
    tells = profile_data.get("tells")

    return BehaviorProfileContext(
        personality=dict(personality) if isinstance(personality, dict) else {},
        goals=tuple(item for item in goals if isinstance(item, str))
        if isinstance(goals, list)
        else (),
        secrets=tuple(dict(item) for item in secrets if isinstance(item, dict))
        if isinstance(secrets, list)
        else (),
        tells=tuple(item for item in tells if isinstance(item, str))
        if isinstance(tells, list)
        else (),
    )
