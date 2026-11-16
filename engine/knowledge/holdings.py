"""What each participant holds (spec 0093, Part B).

A *concept* is a unit of information a player can hold. It is saved as one
fixed type of fact in the knowledge graph:

  - no source character: the participant found it themselves. HELD.
  - a source character: the participant only heard it. NOT held. It stays in
    the knowledge graph as heard knowledge and is never counted here.

``concepts_held`` is the one function that answers "which concepts does this
participant hold". Everything that needs the answer calls it.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from engine.db.orm import Fact, KnowledgeState
from engine.knowledge.graph import assert_knowledge

CONCEPT_FACT_TYPE = "concept"


async def concepts_held(
    db: AsyncSession, *, session_id: UUID, character_id: UUID
) -> frozenset[str]:
    """Concept IDs this participant found themselves.

    Reads the tables directly rather than ``get_character_knowledge``, which
    writes a telemetry event on every call; a read of holdings is not a
    character generation.
    """
    result = await db.execute(
        select(Fact.fact_content)
        .join(KnowledgeState, KnowledgeState.fact_id == Fact.fact_id)
        .where(
            KnowledgeState.session_id == session_id,
            KnowledgeState.character_id == character_id,
            KnowledgeState.source_character_id.is_(None),
            KnowledgeState.superseded_by.is_(None),
            KnowledgeState.confidence > 0,
            Fact.fact_type == CONCEPT_FACT_TYPE,
        )
    )
    contents: list[dict[str, Any]] = list(result.scalars().all())
    return frozenset(str(content["concept_id"]) for content in contents)


async def grant_concept(
    db: AsyncSession,
    *,
    session_id: UUID,
    character_id: UUID,
    concept_id: str,
    text: str,
) -> bool:
    """Give a participant a concept they found themselves.

    The concept's written ``text`` is saved with its ID, so character
    generation, which copies fact content as it is, sees what the concept
    says and not only an opaque ID.

    Returns True if it was new, False if they already held it (nothing is
    saved the second time).
    """
    if concept_id in await concepts_held(
        db, session_id=session_id, character_id=character_id
    ):
        return False
    await assert_knowledge(
        db,
        session_id=session_id,
        character_id=character_id,
        fact_type=CONCEPT_FACT_TYPE,
        fact_content={"concept_id": concept_id, "text": text},
        source_character_id=None,
    )
    return True
