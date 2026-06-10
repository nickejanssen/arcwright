"""Telemetry payload builders for pacing decisions."""

from __future__ import annotations

from typing import Any

from engine.arc.models import PacingConfig
from engine.arc.pacing import PacingIntervention, PacingInterventionType

PLAYER_FACING_INTERVENTIONS = frozenset(
    {
        PacingInterventionType.stall,
        PacingInterventionType.misdirection,
    }
)


def build_tension_update_payload(*, score: float, beat_id: str) -> dict[str, Any]:
    return {
        "score": score,
        "beat_id": beat_id,
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
