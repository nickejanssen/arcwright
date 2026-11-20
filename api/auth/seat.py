"""Who may use the host's controls, decided from the saved host seat (AW-331,
spec 0095 Q1 and M6, D-133).

Token minting and checking stay in ``api.auth``; nothing here reads a key,
secret or Firebase setting. These dependencies take the claims
``require_player_or_host_jwt`` already verified and ask the engine one question
about the seat, so the role can move without anyone signing in again.

  require_host_control    the host seat's player token, or the host token
                          (the session creator's operator key)
  require_seated_or_host  any seated human player's token, or the host token
                          (pause and resume)

A display token, a token for another session, and a player who is not seated
are refused with 403.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth import JwtClaims, require_player_or_host_jwt
from engine.db import get_async_session
from engine.session import host_seat


def _same_session(session_id: UUID, claims: JwtClaims) -> None:
    if claims.session_id is not None and claims.session_id != session_id:
        raise HTTPException(
            status_code=403,
            detail="Token session_id does not match requested session",
        )


async def require_host_control(
    session_id: UUID,
    claims: JwtClaims = Depends(require_player_or_host_jwt),
    db: AsyncSession = Depends(get_async_session),
) -> JwtClaims:
    _same_session(session_id, claims)
    if claims.role == "host":
        return claims
    if claims.role == "player" and await host_seat.is_host_seat(
        db, session_id, claims.player_id
    ):
        return claims
    raise HTTPException(status_code=403, detail="Host seat required")


async def require_seated_or_host(
    session_id: UUID,
    claims: JwtClaims = Depends(require_player_or_host_jwt),
    db: AsyncSession = Depends(get_async_session),
) -> JwtClaims:
    _same_session(session_id, claims)
    if claims.role == "host":
        return claims
    if claims.role == "player" and await host_seat.is_seated_player(
        db, session_id, claims.player_id
    ):
        return claims
    raise HTTPException(status_code=403, detail="A seated player is required")
