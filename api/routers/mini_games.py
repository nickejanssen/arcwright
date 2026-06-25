"""Mini-game player and host API endpoints.

Architecture: docs/architecture/09-developer-api.md §9.2.
ADR-0008: docs/decisions/0008-content-event-type-layering.md (event schema).
ADR-0009: docs/decisions/0009-mini-game-runtime-boundary.md (runtime boundary).

Route handlers are thin: authenticate, validate, delegate to MiniGameRuntime.
No arc logic, scoring, or state decisions here.

Endpoints:
  GET  /v1/sessions/{session_id}/mini-games/active
       Player or host JWT. Returns active run state filtered to caller view.
  POST /v1/sessions/{session_id}/mini-games/{run_id}/submissions
       Player JWT only. Idempotent on submission_id.
  POST /v1/sessions/{session_id}/mini-games/{run_id}/host-commands
       Host JWT only. Commands: cancel | resolve | release_fallback.
"""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth import (
    JwtClaims,
    require_host_jwt,
    require_player_jwt,
    require_player_or_host_jwt,
)
from api.routers.events import _get_or_create_session_state
from api.schemas import (
    HostCommandRequest,
    HostCommandResponse,
    MiniGameRunResponse,
    MiniGameSubmissionRequest,
    MiniGameSubmissionResponse,
)
from engine.db import get_async_session
from engine.db.orm import SessionParticipant
from engine.mini_games.plugins import default_registry
from engine.mini_games.runtime import MiniGameRuntime, MiniGameRuntimeError

router = APIRouter(prefix="/sessions", tags=["mini-games"])


@dataclass(frozen=True)
class ParticipantContext:
    claims: JwtClaims
    character_id: UUID


async def require_valid_participant(
    session_id: UUID,
    claims: JwtClaims = Depends(require_player_jwt),
    db: AsyncSession = Depends(get_async_session),
) -> ParticipantContext:
    """Validate player JWT, session membership, and participant record in one step.

    Raises 403 if the token's session_id does not match the path, or if the
    authenticated player is not a participant in this session.
    """
    if claims.session_id is not None and claims.session_id != session_id:
        raise HTTPException(
            status_code=403,
            detail="Token session_id does not match requested session",
        )
    result = await db.execute(
        select(SessionParticipant.character_id).where(
            SessionParticipant.session_id == session_id,
            SessionParticipant.participant_id == claims.player_id,
        )
    )
    character_id = result.scalar_one_or_none()
    if character_id is None:
        raise HTTPException(status_code=403, detail="Not a participant in this session")
    return ParticipantContext(claims=claims, character_id=character_id)


def _make_runtime(db: AsyncSession, session_id: UUID) -> MiniGameRuntime:
    bus, _ = _get_or_create_session_state(session_id)
    return MiniGameRuntime(db, bus, default_registry())


def _require_session_match(session_id: UUID, claims: JwtClaims) -> None:
    if claims.session_id is not None and claims.session_id != session_id:
        raise HTTPException(
            status_code=403,
            detail="Token session_id does not match requested session",
        )


@router.get("/{session_id}/mini-games/active", response_model=MiniGameRunResponse)
async def get_active_mini_game(
    session_id: UUID,
    claims: JwtClaims = Depends(require_player_or_host_jwt),
    db: AsyncSession = Depends(get_async_session),
) -> MiniGameRunResponse:
    """Return the current non-terminal run, filtered to the caller's authorized view.

    Players see only their own submissions (reconnect path — AC5).
    Hosts see all submissions.
    """
    _require_session_match(session_id, claims)

    runtime = _make_runtime(db, session_id)
    run = await runtime.get_active_run(session_id)
    if run is None:
        raise HTTPException(status_code=404, detail="No active mini-game")

    if claims.role == "player" and claims.player_id is not None:
        result = await db.execute(
            select(SessionParticipant.character_id).where(
                SessionParticipant.session_id == session_id,
                SessionParticipant.participant_id == claims.player_id,
            )
        )
        character_id = result.scalar_one_or_none()
        visible_submissions = (
            [s for s in run.submissions if s.character_id == character_id]
            if character_id is not None
            else []
        )
    else:
        visible_submissions = list(run.submissions)

    return MiniGameRunResponse(
        run_id=run.run_id,
        game_id=run.game_id,
        status=run.status,
        deadline_at=run.deadline,
        my_submissions=[
            MiniGameSubmissionResponse(
                submission_id=s.submission_id,
                is_accepted=s.is_accepted,
                rejection_reason=s.rejection_reason,
            )
            for s in visible_submissions
        ],
    )


@router.post(
    "/{session_id}/mini-games/{run_id}/submissions",
    response_model=MiniGameSubmissionResponse,
)
async def submit_mini_game_action(
    session_id: UUID,
    run_id: UUID,
    body: MiniGameSubmissionRequest,
    participant: ParticipantContext = Depends(require_valid_participant),
    db: AsyncSession = Depends(get_async_session),
) -> MiniGameSubmissionResponse:
    """Record a player submission. Idempotent on submission_id (AC2).

    Scoped to the authenticated participant — host tokens and tokens from
    other sessions are rejected before reaching the runtime.
    """
    runtime = _make_runtime(db, session_id)
    try:
        submission = await runtime.submit_action(
            run_id,
            body.submission_id,
            participant.character_id,
            body.payload,
            participant_id=participant.claims.player_id,
        )
    except MiniGameRuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc))

    return MiniGameSubmissionResponse(
        submission_id=submission.submission_id,
        is_accepted=submission.is_accepted,
        rejection_reason=submission.rejection_reason,
    )


@router.post(
    "/{session_id}/mini-games/{run_id}/host-commands",
    response_model=HostCommandResponse,
)
async def send_host_command(
    session_id: UUID,
    run_id: UUID,
    body: HostCommandRequest,
    claims: JwtClaims = Depends(require_host_jwt),
    db: AsyncSession = Depends(get_async_session),
) -> HostCommandResponse:
    """Dispatch a host command to the runtime (AC1).

    cancel          → cancel_run: transition to cancelled from any non-terminal state.
    resolve         → resolve_run: force-complete with scoring.
    release_fallback → override_clue_release: release clues immediately.
    """
    _require_session_match(session_id, claims)

    runtime = _make_runtime(db, session_id)
    try:
        if body.command == "cancel":
            run = await runtime.cancel_run(run_id)
        elif body.command == "resolve":
            run = await runtime.resolve_run(run_id)
        else:
            clues = body.params.get("clues", [])
            if not isinstance(clues, list):
                raise HTTPException(
                    status_code=422, detail="params.clues must be a list"
                )
            host_account_id = claims.player_id
            if host_account_id is None:
                raise HTTPException(
                    status_code=400,
                    detail="Host token missing arcwright_player_id claim",
                )
            run = await runtime.override_clue_release(run_id, clues, host_account_id)
    except MiniGameRuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except NotImplementedError as exc:
        raise HTTPException(status_code=501, detail=str(exc))

    return HostCommandResponse(
        run_id=run.run_id,
        game_id=run.game_id,
        status=run.status,
    )
