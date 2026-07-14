"""Telemetry payload builders and Event writers for pacing decisions (Signal 2)."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from engine.arc.models import PacingConfig
from engine.arc.pacing import PacingIntervention, PacingInterventionType
from engine.db.orm import Event

PLAYER_FACING_INTERVENTIONS = frozenset(
    {
        PacingInterventionType.stall,
        PacingInterventionType.misdirection,
    }
)


def build_tension_update_payload(
    *,
    score: float,
    beat_id: str,
    target_score: float | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "score": score,
        "beat_id": beat_id,
    }
    if target_score is not None:
        # Authored target from the arc's authorial_intent block (spec 0064).
        # Only present for beats with a declared emotional target.
        payload["target_score"] = target_score
    return payload


def build_intent_fidelity_summary_payload(
    *,
    beat_id: str,
    target_score: float,
    scores: list[float],
) -> dict[str, Any]:
    """Summarize realized-versus-intended tension for one completed beat.

    Emitted at beat exit only for beats with a declared emotional target
    (spec 0064). ``scores`` are the tension_update scores recorded while the
    beat was active.
    """
    if scores:
        mean_score = sum(scores) / len(scores)
        mean_abs_deviation = sum(abs(s - target_score) for s in scores) / len(scores)
    else:
        mean_score = None
        mean_abs_deviation = None
    return {
        "beat_id": beat_id,
        "target_score": target_score,
        "mean_score": mean_score,
        "mean_abs_deviation": mean_abs_deviation,
    }


def build_pacing_intervention_payload(
    intervention: PacingIntervention,
) -> dict[str, Any] | None:
    if intervention.intervention_type not in PLAYER_FACING_INTERVENTIONS:
        return None

    return {
        "trigger_type": intervention.intervention_type.value,
        "tension_score_at_trigger": intervention.tension_score_at_trigger,
        "beat_id": intervention.beat_id,
    }


def build_pacing_intervention_outcome_payload(
    intervention: PacingIntervention,
    *,
    outcome_resumed_within_60s: bool,
) -> dict[str, Any] | None:
    if intervention.intervention_type not in PLAYER_FACING_INTERVENTIONS:
        return None

    return {
        "trigger_type": intervention.intervention_type.value,
        "tension_score_at_trigger": intervention.tension_score_at_trigger,
        "beat_id": intervention.beat_id,
        "outcome_resumed_within_60s": outcome_resumed_within_60s,
    }


async def record_tension_update(
    db: AsyncSession,
    session_id: UUID,
    *,
    score: float,
    beat_id: str,
    target_score: float | None = None,
) -> None:
    db.add(
        Event(
            session_id=session_id,
            event_type="tension_update",
            payload=build_tension_update_payload(
                score=score, beat_id=beat_id, target_score=target_score
            ),
        )
    )
    await db.flush()


async def record_intent_fidelity_summary(
    db: AsyncSession,
    session_id: UUID,
    *,
    beat_id: str,
    target_score: float,
    scores: list[float],
) -> None:
    db.add(
        Event(
            session_id=session_id,
            event_type="intent_fidelity_summary",
            payload=build_intent_fidelity_summary_payload(
                beat_id=beat_id, target_score=target_score, scores=scores
            ),
        )
    )
    await db.flush()


async def record_pacing_intervention(
    db: AsyncSession,
    session_id: UUID,
    intervention: PacingIntervention,
) -> None:
    payload = build_pacing_intervention_payload(intervention)
    if payload is None:
        return
    db.add(
        Event(
            session_id=session_id,
            event_type="pacing_intervention",
            payload=payload,
        )
    )
    await db.flush()


async def record_pacing_intervention_outcome(
    db: AsyncSession,
    session_id: UUID,
    intervention: PacingIntervention,
    *,
    outcome_resumed_within_60s: bool,
) -> None:
    payload = build_pacing_intervention_outcome_payload(
        intervention, outcome_resumed_within_60s=outcome_resumed_within_60s
    )
    if payload is None:
        return
    db.add(
        Event(
            session_id=session_id,
            event_type="pacing_intervention_outcome",
            payload=payload,
        )
    )
    await db.flush()


def build_pacing_decision_log_payload(
    intervention: PacingIntervention,
    config: PacingConfig,
) -> dict[str, Any]:
    return {
        "decision_type": "pacing_intervention",
        "input_context": {
            "signal_snapshot": intervention.signal_snapshot.model_dump(mode="json"),
            "pacing_config": config.model_dump(mode="json"),
            "computed_score": intervention.tension_score_at_trigger,
        },
        "outcome": {
            "intervention_type": intervention.intervention_type.value,
            "recommended_action": intervention.recommended_action.value,
            "beat_id": intervention.beat_id,
            "tension_score_at_trigger": intervention.tension_score_at_trigger,
            "threshold": intervention.threshold,
        },
    }
