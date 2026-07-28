"""Public lobby endpoints for the Nightcap rehearsal lobby.

No auth required for lobby discovery and join-code entry. The join response
now includes a Firebase custom token for the player's authenticated path.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from firebase_admin import auth as firebase_auth
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth import _ensure_firebase_app
from api.schemas import (
    LobbyJoinRequest,
    LobbyJoinResponse,
    LobbyPlayerEntry,
    LobbyStateResponse,
)
from engine.arc import is_terminal_beat
from engine.arc.registry import load_arc_definition
from engine.db import get_async_session
from engine.db.orm import Session as OrmSession
from engine.db.orm import SessionParticipant as OrmParticipant
from engine.session.service import (
    SessionNotFoundError,
    SessionStateError,
    _session_service,
)

router = APIRouter(tags=["lobby"])


@router.get("/sessions/{session_id}/lobby", response_model=LobbyStateResponse)
async def get_lobby_state(
    session_id: UUID,
    db: AsyncSession = Depends(get_async_session),
) -> LobbyStateResponse:
    """Return the current lobby state for the shared display. No auth required."""
    orm = await db.get(OrmSession, session_id)
    if orm is None:
        raise HTTPException(status_code=404, detail="Session not found")

    result = await db.execute(
        select(OrmParticipant).where(
            OrmParticipant.session_id == session_id,
            OrmParticipant.surface_type == "player",
        )
    )
    participants = result.scalars().all()
    arc_definition = load_arc_definition(orm.arc_id)

    return LobbyStateResponse(
        session_id=session_id,
        join_code=orm.join_code,
        status=orm.status,
        current_beat_id=orm.current_beat_id,
        is_terminal=(
            is_terminal_beat(arc_definition, orm.current_beat_id)
            if arc_definition is not None
            else False
        ),
        min_players=arc_definition.min_players if arc_definition is not None else 1,
        player_count=orm.player_count,
        players=[
            LobbyPlayerEntry(
                participant_id=p.participant_id,
                display_name=p.display_name,
            )
            for p in participants
        ],
    )


@router.post("/lobby-join", response_model=LobbyJoinResponse, status_code=201)
async def lobby_join(
    body: LobbyJoinRequest,
    db: AsyncSession = Depends(get_async_session),
) -> LobbyJoinResponse:
    """Join a session by name and join_code. No auth required."""
    try:
        participant = await _session_service.lobby_join(
            db,
            join_code=body.join_code.upper(),
            display_name=body.name,
        )
    except SessionNotFoundError:
        raise HTTPException(status_code=404, detail="Invalid join code")
    except SessionStateError as exc:
        raise HTTPException(status_code=409, detail=str(exc))

    _ensure_firebase_app()
    player_uid = f"session:{participant.session_id}:player:{participant.participant_id}"
    player_claims = {
        "arcwright_role": participant.surface_type,
        "arcwright_session_id": str(participant.session_id),
        "arcwright_player_id": str(participant.participant_id),
    }
    player_token_bytes = firebase_auth.create_custom_token(player_uid, player_claims)
    player_token = player_token_bytes.decode("utf-8")

    return LobbyJoinResponse(
        participant_id=participant.participant_id,
        session_id=participant.session_id,
        display_name=body.name,
        character_id=participant.character_id,
        player_token=player_token,
    )
