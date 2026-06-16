"""Knowledge state endpoints.

Architecture: docs/architecture/09-developer-api.md §9.2.
Route handlers are thin: validate input, call engine service, return response.
No arc execution logic here.

Endpoint summary (base path /v1/sessions/{session_id}/knowledge):
  POST   /                 Host JWT or API key  Assert fact for a character
  DELETE /{fact_id}        API key (internal)   Revoke a fact
  GET    /{character_id}   API key (internal)   Query character knowledge

The DELETE and GET routes are documented as "Arc engine (internal)" in §9.2.
``require_api_key`` accepts only the server-side X-Api-Key header and
naturally rejects player Bearer tokens — the privacy guarantee the
acceptance criteria require.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

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
from engine.knowledge.service import (
    KnowledgeFact,
    KnowledgeFactNotFoundError,
    _knowledge_service,
)
from engine.session.service import _session_service

router = APIRouter(prefix="/sessions", tags=["knowledge"])


@router.post(
    "/{session_id}/knowledge",
    response_model=KnowledgeFactResponse,
    status_code=201,
)
async def assert_knowledge(
    session_id: UUID,
    body: KnowledgeAssertRequest,
    caller: ApiCaller | JwtClaims = Depends(require_api_key_or_host_jwt),
) -> KnowledgeFactResponse:
    """Assert a fact into a character's knowledge state."""
    if isinstance(caller, JwtClaims):
        _require_session_claim_match(session_id, caller)
    if _session_service.get_session(session_id) is None:
        raise HTTPException(status_code=404, detail="Session not found")
    fact = _knowledge_service.assert_fact(
        session_id=session_id,
        character_id=body.character_id,
        fact_type=body.fact_type,
        fact_content=body.fact_content,
        confidence=body.confidence,
        source_character_id=body.source_character_id,
    )
    return _to_response(fact)


@router.delete(
    "/{session_id}/knowledge/{fact_id}",
    response_model=KnowledgeFactResponse,
)
async def revoke_knowledge(
    session_id: UUID,
    fact_id: UUID,
    caller: ApiCaller = Depends(require_api_key),
) -> KnowledgeFactResponse:
    """Revoke a fact (deception, forgetting). Internal engine callers only."""
    if _session_service.get_session(session_id) is None:
        raise HTTPException(status_code=404, detail="Session not found")
    try:
        fact = _knowledge_service.revoke_fact(session_id, fact_id)
    except KnowledgeFactNotFoundError:
        raise HTTPException(status_code=404, detail="Fact not found")
    return _to_response(fact)


@router.get(
    "/{session_id}/knowledge/{character_id}",
    response_model=CharacterKnowledgeResponse,
)
async def get_character_knowledge(
    session_id: UUID,
    character_id: UUID,
    caller: ApiCaller = Depends(require_api_key),
) -> CharacterKnowledgeResponse:
    """Query a character's current knowledge state. Internal callers only."""
    if _session_service.get_session(session_id) is None:
        raise HTTPException(status_code=404, detail="Session not found")
    facts = _knowledge_service.get_character_knowledge(session_id, character_id)
    return CharacterKnowledgeResponse(
        session_id=session_id,
        character_id=character_id,
        facts=[_to_response(f) for f in facts],
    )


def _to_response(fact: KnowledgeFact) -> KnowledgeFactResponse:
    return KnowledgeFactResponse(
        fact_id=fact.fact_id,
        session_id=fact.session_id,
        character_id=fact.character_id,
        fact_type=fact.fact_type,
        fact_content=fact.fact_content,
        confidence=fact.confidence,
        source_character_id=fact.source_character_id,
        asserted_at=fact.asserted_at,
        revoked_at=fact.revoked_at,
    )


def _require_session_claim_match(session_id: UUID, claims: JwtClaims) -> None:
    if claims.session_id is not None and claims.session_id != session_id:
        raise HTTPException(
            status_code=403,
            detail="Token session_id does not match requested session",
        )
