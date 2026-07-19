"""Evidence-delivery integration with the session knowledge graph."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from engine.case.models import EvidenceEntry
from engine.db.orm import KnowledgeState, SessionParticipant
from engine.knowledge import assert_knowledge, get_character_knowledge


async def record_evidence_delivery(
    session: AsyncSession,
    *,
    session_id: UUID,
    evidence: EvidenceEntry,
    participant_id: UUID,
) -> KnowledgeState:
    """Record a delivered evidence entry as participant character knowledge."""
    character_id = await _resolve_character_id(
        session,
        session_id=session_id,
        participant_id=participant_id,
    )
    return await assert_knowledge(
        session,
        session_id=session_id,
        character_id=character_id,
        fact_type="evidence_delivered",
        fact_content={
            "evidence_id": evidence.evidence_id,
            "evidence_type": evidence.evidence_type,
        },
    )


async def participant_has_evidence(
    session: AsyncSession,
    *,
    session_id: UUID,
    participant_id: UUID,
    evidence_ids: list[str],
) -> bool:
    """Return whether a participant's character knows any requested evidence."""
    return (
        await participant_matching_evidence(
            session,
            session_id=session_id,
            participant_id=participant_id,
            evidence_ids=evidence_ids,
        )
    ) is not None


async def participant_matching_evidence(
    session: AsyncSession,
    *,
    session_id: UUID,
    participant_id: UUID,
    evidence_ids: list[str],
) -> str | None:
    """Return the first delivered evidence ID from one knowledge-graph read."""
    if not evidence_ids:
        return None

    character_id = await _resolve_character_id(
        session,
        session_id=session_id,
        participant_id=participant_id,
    )
    knowledge_states = await get_character_knowledge(
        session,
        session_id=session_id,
        character_id=character_id,
    )
    delivered_ids = {
        state.fact.fact_content.get("evidence_id")
        for state in knowledge_states
        if state.fact.fact_type == "evidence_delivered"
    }
    return next(
        (evidence_id for evidence_id in evidence_ids if evidence_id in delivered_ids),
        None,
    )


async def _resolve_character_id(
    session: AsyncSession,
    *,
    session_id: UUID,
    participant_id: UUID,
) -> UUID:
    result = await session.execute(
        select(SessionParticipant.character_id).where(
            SessionParticipant.session_id == session_id,
            SessionParticipant.participant_id == participant_id,
        )
    )
    character_id = result.scalar_one_or_none()
    if character_id is None:
        raise ValueError(f"participant {participant_id} is not in session {session_id}")
    return character_id
