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
from typing import Any, cast
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError
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
    TMST_SUBMISSION_PAYLOAD_ADAPTER,
    HostCommandRequest,
    HostCommandResponse,
    MiniGameRunResponse,
    MiniGameSubmissionRequest,
    MiniGameSubmissionResponse,
    TmstInputActionPayload,
    TmstInputPhaseState,
    TmstPhaseState,
    TmstPresenceActionPayload,
    TmstSpotlightPhaseState,
    TmstSubmissionPayload,
    TmstVoteActionPayload,
)
from engine.db import get_async_session
from engine.db.orm import MiniGameRun, MiniGameSubmission, SessionParticipant
from engine.mini_games.plugins import default_registry
from engine.mini_games.runtime import MiniGameRuntime, MiniGameRuntimeError

router = APIRouter(prefix="/sessions", tags=["mini-games"])
_TMST_GAME_ID = "tell-me-something-true"


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


def _tmst_runtime_state(run: MiniGameRun) -> dict[str, Any]:
    record = dict(run.clue_unlock_record or {})
    state = record.get("runtime_state")
    if isinstance(state, dict):
        return state
    return {}


def _tmst_presence_map(
    state: dict[str, Any],
    submissions: list[MiniGameSubmission],
    participant_character_ids: list[UUID],
) -> dict[UUID, bool]:
    raw_presence = state.get("presence")
    presence: dict[UUID, bool] = {}
    if isinstance(raw_presence, dict):
        for raw_character_id, connected in raw_presence.items():
            try:
                presence[UUID(str(raw_character_id))] = bool(connected)
            except ValueError:
                continue

    for submission in submissions:
        if submission.payload.get("action") != "presence":
            continue
        presence[submission.character_id] = bool(submission.payload.get("connected"))

    for character_id in participant_character_ids:
        presence.setdefault(character_id, True)
    return presence


def _tmst_current_target(state: dict[str, Any]) -> UUID | None:
    raw_order = state.get("spotlight_order")
    if not isinstance(raw_order, list):
        return None

    try:
        order = [UUID(str(raw_character_id)) for raw_character_id in raw_order]
    except ValueError:
        return None

    try:
        index = int(state.get("current_spotlight_index", 0))
    except (TypeError, ValueError):
        return None

    if index < 0 or index >= len(order):
        return None
    return order[index]


def _tmst_has_submitted_input(
    submissions: list[MiniGameSubmission],
    character_id: UUID,
) -> bool:
    return any(
        submission.is_accepted
        and submission.character_id == character_id
        and submission.payload.get("action") == "input"
        for submission in submissions
    )


def _tmst_has_submitted_vote(
    submissions: list[MiniGameSubmission],
    character_id: UUID,
    target_character_id: UUID,
) -> bool:
    return any(
        submission.is_accepted
        and submission.character_id == character_id
        and submission.payload.get("action") == "vote"
        and str(submission.payload.get("target_character_id"))
        == str(target_character_id)
        for submission in submissions
    )


def _build_tmst_phase_state(
    run: MiniGameRun,
    *,
    claims: JwtClaims,
    character_id: UUID | None,
    participant_character_ids: list[UUID],
) -> TmstPhaseState | None:
    state = _tmst_runtime_state(run)
    phase = state.get("phase")

    if phase == "input":
        return TmstInputPhaseState(
            phase="input",
            deadline_at=run.deadline,
            prompt_ready=claims.role == "player" and character_id is not None,
            submitted=character_id is not None
            and _tmst_has_submitted_input(list(run.submissions), character_id),
        )

    if phase == "spotlight":
        target_character_id = _tmst_current_target(state)
        if target_character_id is None:
            return None

        presence = _tmst_presence_map(
            state, list(run.submissions), participant_character_ids
        )
        connected_character_ids = [
            participant_character_id
            for participant_character_id in participant_character_ids
            if presence.get(participant_character_id, True)
        ]
        eligible_voter_ids = [
            participant_character_id
            for participant_character_id in connected_character_ids
            if participant_character_id != target_character_id
        ]
        return TmstSpotlightPhaseState(
            phase="spotlight",
            deadline_at=run.deadline,
            target_character_id=target_character_id,
            connected_character_ids=connected_character_ids,
            eligible_voter_ids=eligible_voter_ids,
            is_spotlighted_player=character_id == target_character_id,
            can_vote=character_id is not None and character_id in eligible_voter_ids,
            has_voted=character_id is not None
            and _tmst_has_submitted_vote(
                list(run.submissions), character_id, target_character_id
            ),
        )

    return None


async def _participant_character_ids(
    db: AsyncSession,
    session_id: UUID,
) -> list[UUID]:
    result = await db.execute(
        select(SessionParticipant.character_id).where(
            SessionParticipant.session_id == session_id
        )
    )
    return list(result.scalars().all())


async def _character_id_for_claims(
    db: AsyncSession,
    *,
    session_id: UUID,
    claims: JwtClaims,
) -> UUID | None:
    if claims.role != "player" or claims.player_id is None:
        return None
    result = await db.execute(
        select(SessionParticipant.character_id).where(
            SessionParticipant.session_id == session_id,
            SessionParticipant.participant_id == claims.player_id,
        )
    )
    return result.scalar_one_or_none()


async def _load_run_or_404(
    db: AsyncSession,
    *,
    session_id: UUID,
    run_id: UUID,
) -> MiniGameRun:
    result = await db.execute(
        select(MiniGameRun).where(
            MiniGameRun.run_id == run_id,
            MiniGameRun.session_id == session_id,
        )
    )
    run = result.scalar_one_or_none()
    if run is None:
        raise HTTPException(status_code=404, detail="Mini-game run not found")
    return run


def _validate_tmst_submission_payload(payload: dict[str, Any]) -> TmstSubmissionPayload:
    try:
        return cast(
            TmstSubmissionPayload,
            TMST_SUBMISSION_PAYLOAD_ADAPTER.validate_python(payload),
        )
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


def _ensure_tmst_phase_accepts_action(
    run: MiniGameRun,
    payload: TmstSubmissionPayload,
) -> None:
    phase = _tmst_runtime_state(run).get("phase")
    if isinstance(payload, TmstInputActionPayload) and phase != "input":
        raise HTTPException(
            status_code=409,
            detail="input submissions are only accepted during input phase",
        )
    if isinstance(payload, TmstVoteActionPayload) and phase != "spotlight":
        raise HTTPException(
            status_code=409,
            detail="vote submissions are only accepted during spotlight phase",
        )
    if isinstance(payload, TmstPresenceActionPayload) and phase not in {
        "input",
        "spotlight",
        "scoreboard",
    }:
        raise HTTPException(
            status_code=409,
            detail="presence submissions are not accepted for this run phase",
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

    character_id = await _character_id_for_claims(
        db, session_id=session_id, claims=claims
    )
    participant_character_ids = await _participant_character_ids(db, session_id)

    if claims.role == "player" and claims.player_id is not None:
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
        mechanic_type=run.definition_snapshot.get("mechanic_type")
        if isinstance(run.definition_snapshot, dict)
        else None,
        deadline_at=run.deadline,
        phase_state=_build_tmst_phase_state(
            run,
            claims=claims,
            character_id=character_id,
            participant_character_ids=participant_character_ids,
        )
        if run.game_id == _TMST_GAME_ID
        else None,
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
    run = await _load_run_or_404(db, session_id=session_id, run_id=run_id)
    if run.game_id == _TMST_GAME_ID:
        payload = _validate_tmst_submission_payload(body.payload)
        _ensure_tmst_phase_accepts_action(run, payload)

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
