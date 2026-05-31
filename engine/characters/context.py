"""Generation-time character context assembly."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from engine.db.orm import Fact, KnowledgeState


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
class CharacterGenerationContext:
    session_id: UUID
    character_id: UUID
    known_facts: tuple[KnownFactContext, ...]
    unknown_facts: tuple[UnknownFactContext, ...]


async def build_character_generation_context(
    session: AsyncSession,
    *,
    session_id: UUID,
    character_id: UUID,
) -> CharacterGenerationContext:
    """Build the only sanctioned generation-time knowledge context."""
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
        known_facts=known_facts,
        unknown_facts=unknown_facts,
    )
