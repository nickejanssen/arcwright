"""Core knowledge graph operations against the knowledge_states table."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from engine.db.orm import KnowledgeState


async def assert_knowledge(
    session: AsyncSession,
    *,
    session_id: UUID,
    character_id: UUID,
    fact_id: UUID,
    source_character_id: UUID | None = None,
    confidence: float = 1.0,
    provenance_chain: list[UUID] | None = None,
) -> KnowledgeState:
    """Insert a new KnowledgeState row and return the flushed record."""
    ks = KnowledgeState(
        session_id=session_id,
        character_id=character_id,
        fact_id=fact_id,
        source_character_id=source_character_id,
        confidence=confidence,
        provenance_chain=[str(uid) for uid in (provenance_chain or [])],
    )
    session.add(ks)
    await session.flush()
    return ks


async def get_character_knowledge(
    session: AsyncSession,
    *,
    session_id: UUID,
    character_id: UUID,
) -> list[KnowledgeState]:
    """Return all active (superseded_by IS NULL) knowledge states for a character in a session."""
    result = await session.execute(
        select(KnowledgeState)
        .where(
            KnowledgeState.session_id == session_id,
            KnowledgeState.character_id == character_id,
            KnowledgeState.superseded_by.is_(None),
        )
        .order_by(KnowledgeState.asserted_at, KnowledgeState.fact_id)
        .options(selectinload(KnowledgeState.fact))
    )
    return list(result.scalars().all())


async def revoke_knowledge(
    session: AsyncSession,
    *,
    existing_ks_id: UUID,
    replacement: KnowledgeState,
) -> KnowledgeState:
    """Mark an existing KnowledgeState as superseded by a replacement record.

    The replacement must already be flushed (has a valid ks_id). Caller should
    call ``await session.flush()`` before passing the replacement if it was just
    created.
    """
    result = await session.execute(
        select(KnowledgeState).where(KnowledgeState.ks_id == existing_ks_id)
    )
    old_record: KnowledgeState = result.scalar_one()
    old_record.superseded_by = replacement.ks_id
    await session.flush()
    return old_record
