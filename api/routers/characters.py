"""Character endpoints.

Architecture: docs/architecture/09-developer-api.md §9.2.
Route handlers are thin: validate input, call engine service, return response.
No arc execution logic here.

Endpoint summary (base path /v1/sessions/{session_id}/characters):
  GET    /                                Host JWT     List characters
  GET    /{character_id}                  Player JWT   Detail (own only)
  POST   /{character_id}/input            Player JWT   Submit action/dialogue
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth import JwtClaims, require_host_jwt, require_player_or_host_jwt
from api.schemas import (
    CharacterDetailResponse,
    CharacterListResponse,
    CharacterSummaryResponse,
    PlayerInputRequest,
    PlayerInputResponse,
)
from engine.characters.service import (
    CharacterAccessError,
    CharacterNotFoundError,
    _character_service,
)
from engine.db import get_async_session
from engine.session.service import _session_service

router = APIRouter(prefix="/sessions", tags=["characters"])

_PLAYER_INPUT_ROLE = "player"


@router.get("/{session_id}/characters", response_model=CharacterListResponse)
async def list_characters(
    session_id: UUID,
    claims: JwtClaims = Depends(require_host_jwt),
    db: AsyncSession = Depends(get_async_session),
) -> CharacterListResponse:
    """Return every character in the session with surface-level behavior state."""
    _require_session_claim_match(session_id, claims)
    if await _session_service.get_session(db, session_id) is None:
        raise HTTPException(status_code=404, detail="Session not found")
    characters = await _character_service.list_characters(db, session_id)
    return CharacterListResponse(
        session_id=session_id,
        characters=[
            CharacterSummaryResponse(
                character_id=c.character_id,
                participant_id=c.participant_id,
                surface_type=c.surface_type,
                is_ai_controlled=c.is_ai_controlled,
            )
            for c in characters
        ],
    )


@router.get(
    "/{session_id}/characters/{character_id}",
    response_model=CharacterDetailResponse,
)
async def get_character(
    session_id: UUID,
    character_id: UUID,
    claims: JwtClaims = Depends(require_player_or_host_jwt),
    db: AsyncSession = Depends(get_async_session),
) -> CharacterDetailResponse:
    """Return the requesting player's own character detail."""
    _require_session_claim_match(session_id, claims)
    if await _session_service.get_session(db, session_id) is None:
        raise HTTPException(status_code=404, detail="Session not found")
    if claims.role == "host":
        return await _detail_for_any_character(db, session_id, character_id)
    if claims.player_id is None:
        raise HTTPException(
            status_code=400,
            detail="Player token must include arcwright_player_id claim",
        )
    try:
        detail = await _character_service.get_character_for_player(
            db, session_id, character_id, claims.player_id
        )
    except CharacterNotFoundError:
        raise HTTPException(status_code=404, detail="Character not found")
    except CharacterAccessError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    return CharacterDetailResponse(
        session_id=session_id,
        character_id=detail.character_id,
        participant_id=detail.participant_id,
        surface_type=detail.surface_type,
        is_ai_controlled=detail.is_ai_controlled,
    )


@router.post(
    "/{session_id}/characters/{character_id}/input",
    response_model=PlayerInputResponse,
    status_code=201,
)
async def submit_character_input(
    session_id: UUID,
    character_id: UUID,
    body: PlayerInputRequest,
    claims: JwtClaims = Depends(require_player_or_host_jwt),
    db: AsyncSession = Depends(get_async_session),
) -> PlayerInputResponse:
    """Submit a typed player action or dialogue input as the named character."""
    _require_session_claim_match(session_id, claims)
    if await _session_service.get_session(db, session_id) is None:
        raise HTTPException(status_code=404, detail="Session not found")
    if claims.role != _PLAYER_INPUT_ROLE:
        raise HTTPException(
            status_code=403,
            detail="Player token required to submit character input",
        )
    if claims.player_id is None:
        raise HTTPException(
            status_code=400,
            detail="Token must include arcwright_player_id claim",
        )
    try:
        record = await _character_service.submit_input(
            db,
            session_id=session_id,
            character_id=character_id,
            requesting_participant_id=claims.player_id,
            kind=body.kind,
            content=body.content,
        )
    except CharacterNotFoundError:
        raise HTTPException(status_code=404, detail="Character not found")
    except CharacterAccessError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    return PlayerInputResponse(
        input_id=record.input_id,
        session_id=record.session_id,
        character_id=record.character_id,
        participant_id=record.participant_id,
        kind=record.kind,
        content=record.content,
        submitted_at=record.submitted_at,
    )


async def _detail_for_any_character(
    db: AsyncSession, session_id: UUID, character_id: UUID
) -> CharacterDetailResponse:
    participant = await _session_service.find_participant_by_character(
        db, session_id, character_id
    )
    if participant is None:
        raise HTTPException(status_code=404, detail="Character not found")
    return CharacterDetailResponse(
        session_id=session_id,
        character_id=participant.character_id,
        participant_id=participant.participant_id,
        surface_type=participant.surface_type,
        is_ai_controlled=participant.is_ai_controlled,
    )


def _require_session_claim_match(session_id: UUID, claims: JwtClaims) -> None:
    if claims.session_id is not None and claims.session_id != session_id:
        raise HTTPException(
            status_code=403,
            detail="Token session_id does not match requested session",
        )
