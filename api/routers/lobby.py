"""Public lobby endpoints for the Nightcap rehearsal lobby.

No auth required — these are public endpoints for the display screen
and player phones. Production auth is deferred to M5 (AW-269).
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas import (
    LobbyJoinRequest,
    LobbyJoinResponse,
    LobbyPlayerEntry,
    LobbyStateResponse,
)
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

    return LobbyStateResponse(
        session_id=session_id,
        join_code=orm.join_code,
        status=orm.status,
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

    return LobbyJoinResponse(
        participant_id=participant.participant_id,
        session_id=participant.session_id,
        display_name=body.name,
    )
