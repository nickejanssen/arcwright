"""Knowledge state endpoints.

Architecture: docs/architecture/09-developer-api.md §9.2.
Route handlers are thin: validate input, call engine function, return response.
No arc execution logic here.

Endpoint summary (base path /v1/sessions/{session_id}/knowledge):
  POST   /                 Host JWT or API key  Assert fact for a character
  DELETE /{fact_id}        API key (internal)   Revoke a fact
  GET    /{character_id}   API key (internal)   Query character knowledge

The DELETE and GET routes are documented as "Arc engine (internal)" in §9.2.
``require_api_key`` accepts only the server-side X-Api-Key header and
naturally rejects player Bearer tokens — the privacy guarantee AW-218 AC3
requires.

Persistence: writes through ``engine.knowledge.graph`` so facts asserted
here are visible to ``engine.characters.context.build_character_generation_context``
at the next AI generation, satisfying §4.3's pre-generation knowledge
query invariant.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth import (
    ApiCaller,
    JwtClaims,
    require_api_key,
    require_api_key_or_host_jwt,
)
from api.schemas import (
    CharacterKnowledgeResponse,
    KnowledgeAssertRequest,
    KnowledgeFactResponse,
)
from engine.db import get_async_session
from engine.db.orm import Fact, KnowledgeState
from engine.knowledge import (
    assert_knowledge,
    get_character_knowledge,
    revoke_fact_in_session,
)
from engine.session.service import _session_service

router = APIRouter(prefix="/sessions", tags=["knowledge"])


@router.post(
    "/{session_id}/knowledge",
    response_model=KnowledgeFactResponse,
    status_code=201,
)
async def assert_knowledge_endpoint(
    session_id: UUID,
    body: KnowledgeAssertRequest,
    caller: ApiCaller | JwtClaims = Depends(require_api_key_or_host_jwt),
    db: AsyncSession = Depends(get_async_session),
) -> KnowledgeFactResponse:
    """Assert a fact into a character's knowledge state.

    Upserts a ``facts`` row keyed on ``(session_id, fact_type, fact_content)``
    and inserts a new ``knowledge_states`` row in one transaction. Two
    asserts with the same content produce one fact row and two knowledge
    state rows (§4.2).
    """
    if isinstance(caller, JwtClaims):
        _require_session_claim_match(session_id, caller)
    if _session_service.get_session(session_id) is None:
        raise HTTPException(status_code=404, detail="Session not found")
    ks = await assert_knowledge(
        db,
        session_id=session_id,
        character_id=body.character_id,
        fact_type=body.fact_type,
        fact_content=body.fact_content,
        source_character_id=body.source_character_id,
        confidence=body.confidence,
    )
    fact = await db.get(Fact, ks.fact_id)
    if fact is None:
        raise HTTPException(status_code=500, detail="Fact missing after assert")
    return _to_response(ks, fact)


@router.delete(
    "/{session_id}/knowledge/{fact_id}",
    response_model=KnowledgeFactResponse,
)
async def revoke_knowledge_endpoint(
    session_id: UUID,
    fact_id: UUID,
    caller: ApiCaller = Depends(require_api_key),
    db: AsyncSession = Depends(get_async_session),
) -> KnowledgeFactResponse:
    """Revoke a fact across every character that currently knows it.

    Append-only: writes one tombstone ``knowledge_states`` row per affected
    character with the original record's ``superseded_by`` set; the
    original row is never deleted (§4.3).
    """
    fact = await db.get(Fact, fact_id)
    if fact is None or fact.session_id != session_id:
        raise HTTPException(status_code=404, detail="Fact not found")
    tombstones = await revoke_fact_in_session(
        db, session_id=session_id, fact_id=fact_id
    )
    if not tombstones:
        # Already revoked; surface the fact in its revoked-state shape.
        latest = await _latest_tombstone(db, session_id=session_id, fact_id=fact_id)
        if latest is None:
            raise HTTPException(status_code=404, detail="Fact not found")
        return _to_response(latest, fact)
    return _to_response(tombstones[0], fact)


@router.get(
    "/{session_id}/knowledge/{character_id}",
    response_model=CharacterKnowledgeResponse,
)
async def get_character_knowledge_endpoint(
    session_id: UUID,
    character_id: UUID,
    caller: ApiCaller = Depends(require_api_key),
    db: AsyncSession = Depends(get_async_session),
) -> CharacterKnowledgeResponse:
    """Query a character's current knowledge state. Internal callers only."""
    states = await get_character_knowledge(
        db, session_id=session_id, character_id=character_id
    )
    return CharacterKnowledgeResponse(
        session_id=session_id,
        character_id=character_id,
        facts=[_to_response(ks, ks.fact) for ks in states],
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _to_response(ks: KnowledgeState, fact: Fact) -> KnowledgeFactResponse:
    """Map an ORM (KnowledgeState, Fact) pair to the §9.2 response shape.

    ``revoked_at`` is non-null when the knowledge state has been tombstoned
    (self-supersession); the originally-asserted record carries
    ``revoked_at = None`` and the tombstone carries the operation
    timestamp. AW-218 contract: ``KnowledgeFactResponse`` shape is
    byte-identical to the in-memory MVP.
    """
    revoked_at = ks.asserted_at if ks.superseded_by == ks.ks_id else None
    return KnowledgeFactResponse(
        fact_id=fact.fact_id,
        session_id=ks.session_id,
        character_id=ks.character_id,
        fact_type=fact.fact_type,
        fact_content=fact.fact_content,
        confidence=ks.confidence,
        source_character_id=ks.source_character_id,
        asserted_at=ks.asserted_at,
        revoked_at=revoked_at,
    )


async def _latest_tombstone(
    db: AsyncSession, *, session_id: UUID, fact_id: UUID
) -> KnowledgeState | None:
    result = await db.execute(
        select(KnowledgeState)
        .where(
            KnowledgeState.session_id == session_id,
            KnowledgeState.fact_id == fact_id,
            KnowledgeState.superseded_by == KnowledgeState.ks_id,
        )
        .order_by(KnowledgeState.asserted_at.desc())
        .limit(1)
    )
    return result.scalars().first()


def _require_session_claim_match(session_id: UUID, claims: JwtClaims) -> None:
    if claims.session_id is not None and claims.session_id != session_id:
        raise HTTPException(
            status_code=403,
            detail="Token session_id does not match requested session",
        )
