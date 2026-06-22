"""Session lifecycle endpoints.

Architecture: docs/architecture/09-developer-api.md §9.2.
Route handlers are thin: validate input, call engine service, return response.
No arc execution logic here.

Endpoint summary (base path /v1/sessions):
  POST   /                      API key          Create session
  GET    /{id}                   API key|host JWT Session state
  POST   /{id}/start             host JWT         Start arc
  POST   /{id}/pause             host JWT         Pause arc + snapshot
  POST   /{id}/resume            host JWT         Resume arc from snapshot
  POST   /{id}/end               host JWT         End session
  POST   /{id}/replay-intent     host JWT         Record post-session replay intent
  GET    /{id}/join              public           Exchange join token for player JWT
"""

from __future__ import annotations

from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from firebase_admin import auth as firebase_auth
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth import (
    ApiCaller,
    JwtClaims,
    _ensure_firebase_app,
    require_api_key,
    require_api_key_or_host_jwt,
    require_host_jwt,
)
from api.routers.events import _get_or_create_session_state
from api.schemas import (
    AddPlayerResponse,
    CreateSessionRequest,
    CreateSessionResponse,
    EndSessionRequest,
    JoinSessionResponse,
    ReplayIntentRequest,
    SessionStateResponse,
)
from engine.db import get_async_session
from engine.narrator.bridge import generate_narrator_bridge
from engine.session.service import (
    SessionCapacityError,
    SessionNotFoundError,
    SessionStateError,
    _session_service,
)
from engine.telemetry.costs import get_cost_summary

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=CreateSessionResponse, status_code=201)
async def create_session(
    body: CreateSessionRequest,
    caller: ApiCaller = Depends(require_api_key),
    db: AsyncSession = Depends(get_async_session),
) -> CreateSessionResponse:
    """Create a new session from an arc definition.

    Returns session_id, a join URL for players, and a host_token (Firebase custom
    token) the host exchanges for an ID token via the Firebase client SDK.
    """
    host_account_id = uuid4()
    session, host_join_token = await _session_service.create_session(
        db,
        arc_id=body.arc_id,
        host_account_id=host_account_id,
        quality_tier=body.quality_tier,
    )

    _ensure_firebase_app()
    host_uid = f"session:{session.session_id}:host"
    host_claims = {
        "arcwright_role": "host",
        "arcwright_session_id": str(session.session_id),
        "arcwright_player_id": str(host_account_id),
    }
    host_token_bytes = firebase_auth.create_custom_token(host_uid, host_claims)
    host_token = host_token_bytes.decode("utf-8")

    join_url = f"/v1/sessions/{session.session_id}/join"
    return CreateSessionResponse(
        session_id=session.session_id,
        join_url=join_url,
        host_token=host_token,
        host_join_token=host_join_token,
    )


@router.get("/{session_id}", response_model=SessionStateResponse)
async def get_session(
    session_id: UUID,
    caller: ApiCaller | JwtClaims = Depends(require_api_key_or_host_jwt),
    db: AsyncSession = Depends(get_async_session),
) -> SessionStateResponse:
    """Return current session state (status, beat, player count, cost consumed)."""
    if isinstance(caller, JwtClaims):
        _require_session_claim_match(session_id, caller)
    session = await _session_service.get_session(db, session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return await _session_to_state_response(db, session)


@router.post("/{session_id}/start", response_model=SessionStateResponse)
async def start_session(
    session_id: UUID,
    claims: JwtClaims = Depends(require_host_jwt),
    db: AsyncSession = Depends(get_async_session),
) -> SessionStateResponse:
    """Start the session arc; triggers the introduction beat."""
    _require_session_claim_match(session_id, claims)
    try:
        session = await _session_service.start_session(db, session_id)
    except SessionNotFoundError:
        raise HTTPException(status_code=404, detail="Session not found")
    except SessionStateError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    return await _session_to_state_response(db, session)


@router.post("/{session_id}/pause", response_model=SessionStateResponse)
async def pause_session(
    session_id: UUID,
    claims: JwtClaims = Depends(require_host_jwt),
    db: AsyncSession = Depends(get_async_session),
) -> SessionStateResponse:
    """Pause the arc and snapshot state at the current beat boundary."""
    _require_session_claim_match(session_id, claims)
    try:
        session = await _session_service.pause_session(db, session_id)
    except SessionNotFoundError:
        raise HTTPException(status_code=404, detail="Session not found")
    except SessionStateError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    return await _session_to_state_response(db, session)


@router.post("/{session_id}/resume", response_model=SessionStateResponse)
async def resume_session(
    session_id: UUID,
    claims: JwtClaims = Depends(require_host_jwt),
    db: AsyncSession = Depends(get_async_session),
) -> SessionStateResponse:
    """Resume the arc from the nearest beat snapshot."""
    _require_session_claim_match(session_id, claims)
    try:
        session, snapshot = await _session_service.resume_session(db, session_id)
    except SessionNotFoundError:
        raise HTTPException(status_code=404, detail="Session not found")
    except SessionStateError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    bridge_event = await generate_narrator_bridge(
        db, session_id, snapshot, session.quality_tier.value
    )
    bus, _registry = _get_or_create_session_state(session_id)
    await bus.publish(bridge_event)
    return await _session_to_state_response(db, session)


@router.post("/{session_id}/end", response_model=SessionStateResponse)
async def end_session(
    session_id: UUID,
    claims: JwtClaims = Depends(require_host_jwt),
    db: AsyncSession = Depends(get_async_session),
    body: EndSessionRequest | None = None,
) -> SessionStateResponse:
    """End the session and write the session_completed telemetry event."""
    _require_session_claim_match(session_id, claims)
    completion_type = body.completion_type if body is not None else "full_arc"
    killer_identified = body.killer_identified if body is not None else False
    try:
        session = await _session_service.end_session(
            db,
            session_id,
            completion_type=completion_type,
            killer_identified=killer_identified,
        )
    except SessionNotFoundError:
        raise HTTPException(status_code=404, detail="Session not found")
    except SessionStateError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    return await _session_to_state_response(db, session)


@router.post("/{session_id}/replay-intent", status_code=204)
async def write_replay_intent(
    session_id: UUID,
    body: ReplayIntentRequest,
    claims: JwtClaims = Depends(require_host_jwt),
    db: AsyncSession = Depends(get_async_session),
) -> None:
    """Write the host-reported replay-intent telemetry signal."""
    _require_session_claim_match(session_id, claims)
    try:
        await _session_service.write_replay_intent(
            db,
            session_id,
            intent=body.intent,
            collection_method=body.collection_method,
        )
    except SessionNotFoundError:
        raise HTTPException(status_code=404, detail="Session not found")


@router.post("/{session_id}/players", response_model=AddPlayerResponse, status_code=201)
async def add_player(
    session_id: UUID,
    caller: ApiCaller = Depends(require_api_key),
    db: AsyncSession = Depends(get_async_session),
) -> AddPlayerResponse:
    """Create a player participant slot and return a join token."""
    try:
        participant, join_token = await _session_service.add_player(db, session_id)
    except SessionNotFoundError:
        raise HTTPException(status_code=404, detail="Session not found")
    except SessionCapacityError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except SessionStateError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    join_url = f"/v1/sessions/{session_id}/join?token={join_token}"
    return AddPlayerResponse(
        participant_id=participant.participant_id,
        join_token=join_token,
        join_url=join_url,
    )


@router.get("/{session_id}/join", response_model=JoinSessionResponse)
async def join_session(
    session_id: UUID,
    token: str = Query(
        ..., description="Per-player join token distributed out of band"
    ),
    db: AsyncSession = Depends(get_async_session),
) -> JoinSessionResponse:
    """Validate a join token and return a Firebase custom token for the player."""
    participant = await _session_service.validate_join_token(db, session_id, token)
    if participant is None:
        raise HTTPException(status_code=403, detail="Invalid join token")

    _ensure_firebase_app()
    player_uid = f"session:{session_id}:player:{participant.participant_id}"
    player_claims = {
        "arcwright_role": participant.surface_type,
        "arcwright_session_id": str(session_id),
        "arcwright_player_id": str(participant.participant_id),
    }
    player_token_bytes = firebase_auth.create_custom_token(player_uid, player_claims)
    player_token = player_token_bytes.decode("utf-8")

    return JoinSessionResponse(
        session_id=session_id,
        player_id=participant.participant_id,
        character_id=participant.character_id,
        player_token=player_token,
    )


def _require_session_claim_match(session_id: UUID, claims: JwtClaims) -> None:
    """Reject requests where the JWT's session claim does not match the path."""
    if claims.session_id is not None and claims.session_id != session_id:
        raise HTTPException(
            status_code=403,
            detail="Token session_id does not match requested session",
        )


async def _session_to_state_response(db: AsyncSession, session) -> SessionStateResponse:  # type: ignore[no-untyped-def]
    cost_summary = await get_cost_summary(db, session_id=session.session_id)
    return SessionStateResponse(
        session_id=session.session_id,
        arc_id=session.arc_id,
        status=session.status,
        current_beat_id=session.current_beat_id,
        player_count=session.player_count,
        quality_tier=session.quality_tier,
        created_at=session.created_at,
        started_at=session.started_at,
        completed_at=session.completed_at,
        cost_consumed_usd=float(cost_summary.total_cost_usd),
    )
