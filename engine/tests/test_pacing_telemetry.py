"""Tests for pacing telemetry payload contracts."""

from __future__ import annotations

import pytest

from engine.arc.models import PacingConfig
from engine.arc.pacing import (
    PacingIntervention,
    PacingInterventionType,
    PacingRecommendedAction,
    PacingSignalSnapshot,
)
from engine.telemetry.pacing import (
    build_pacing_decision_log_payload,
    build_pacing_intervention_outcome_payload,
    build_pacing_intervention_payload,
    build_tension_update_payload,
)


def pacing_config() -> PacingConfig:
    return PacingConfig(
        stall_threshold=0.25,
        misdirection_threshold=0.80,
        premium_threshold=0.85,
        w_time=0.3,
        w_action=0.3,
        w_suspicion=0.2,
        w_coverage=0.2,
    )


def signal_snapshot() -> PacingSignalSnapshot:
    return PacingSignalSnapshot(
        beat_id="investigation",
        time_pressure=0.2,
        action_rate=0.1,
        suspicion=0.3,
        clue_coverage=0.4,
    )


def pacing_intervention(
    intervention_type: PacingInterventionType = PacingInterventionType.stall,
) -> PacingIntervention:
    action_by_type = {
        PacingInterventionType.stall: (
            PacingRecommendedAction.inject_clue_or_narrator_prompt
        ),
        PacingInterventionType.misdirection: (
            PacingRecommendedAction.inject_misdirection
        ),
        PacingInterventionType.quality_upgrade: (
            PacingRecommendedAction.upgrade_quality_tier
        ),
    }
    threshold_by_type = {
        PacingInterventionType.stall: 0.25,
        PacingInterventionType.misdirection: 0.80,
        PacingInterventionType.quality_upgrade: 0.85,
    }

    return PacingIntervention(
        intervention_type=intervention_type,
        recommended_action=action_by_type[intervention_type],
        beat_id="investigation",
        tension_score_at_trigger=0.24,
        threshold=threshold_by_type[intervention_type],
        signal_snapshot=signal_snapshot(),
    )


def test_tension_update_payload_includes_score_and_beat_id() -> None:
    payload = build_tension_update_payload(score=0.42, beat_id="investigation")

    assert payload == {
        "score": 0.42,
        "beat_id": "investigation",
    }


def test_pacing_intervention_payload_omits_retrospective_outcome() -> None:
    payload = build_pacing_intervention_payload(pacing_intervention())

    assert payload == {
        "trigger_type": "stall",
        "tension_score_at_trigger": 0.24,
        "beat_id": "investigation",
    }
    assert "outcome_resumed_within_60s" not in payload


@pytest.mark.parametrize(
    "intervention_type",
    [PacingInterventionType.stall, PacingInterventionType.misdirection],
)
def test_pacing_intervention_outcome_payload_includes_resumed_flag(
    intervention_type: PacingInterventionType,
) -> None:
    payload = build_pacing_intervention_outcome_payload(
        pacing_intervention(intervention_type),
        outcome_resumed_within_60s=True,
    )

    assert payload == {
        "trigger_type": intervention_type.value,
        "tension_score_at_trigger": 0.24,
        "beat_id": "investigation",
        "outcome_resumed_within_60s": True,
    }


def test_quality_upgrade_does_not_emit_pacing_intervention_payloads() -> None:
    intervention = pacing_intervention(PacingInterventionType.quality_upgrade)

    assert build_pacing_intervention_payload(intervention) is None
    assert (
        build_pacing_intervention_outcome_payload(
            intervention,
            outcome_resumed_within_60s=True,
        )
        is None
    )


def test_decision_log_payload_contains_reproducible_input_context() -> None:
    intervention = pacing_intervention()

    payload = build_pacing_decision_log_payload(intervention, pacing_config())

    assert payload["decision_type"] == "pacing_intervention"
    assert payload["input_context"] == {
        "signal_snapshot": {
            "beat_id": "investigation",
            "time_pressure": 0.2,
            "action_rate": 0.1,
            "suspicion": 0.3,
            "clue_coverage": 0.4,
        },
        "pacing_config": {
            "stall_threshold": 0.25,
            "misdirection_threshold": 0.8,
            "premium_threshold": 0.85,
            "w_time": 0.3,
            "w_action": 0.3,
            "w_suspicion": 0.2,
            "w_coverage": 0.2,
        },
        "computed_score": 0.24,
    }


def test_decision_log_outcome_contains_descriptor_without_duplicate_snapshot() -> None:
    intervention = pacing_intervention()

    payload = build_pacing_decision_log_payload(intervention, pacing_config())

    assert payload["outcome"] == {
        "intervention_type": "stall",
        "recommended_action": "inject_clue_or_narrator_prompt",
        "beat_id": "investigation",
        "tension_score_at_trigger": 0.24,
        "threshold": 0.25,
    }
    assert "signal_snapshot" not in payload["outcome"]
