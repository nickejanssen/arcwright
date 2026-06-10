"""Tests for deterministic dramatic tension scoring."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from engine.arc.models import PacingConfig
from engine.arc.pacing import (
    PacingInterventionType,
    PacingRecommendedAction,
    PacingSignalSnapshot,
    compute_dramatic_tension_score,
    evaluate_pacing_interventions,
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


def snapshot_with_score(score: float) -> PacingSignalSnapshot:
    return PacingSignalSnapshot(
        beat_id="investigation",
        time_pressure=score,
        action_rate=score,
        suspicion=score,
        clue_coverage=score,
    )


def test_dramatic_tension_score_uses_configured_weights() -> None:
    snapshot = PacingSignalSnapshot(
        beat_id="investigation",
        time_pressure=0.2,
        action_rate=0.4,
        suspicion=0.6,
        clue_coverage=0.8,
    )

    score = compute_dramatic_tension_score(snapshot, pacing_config())

    assert score == pytest.approx(0.46)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("time_pressure", -0.01),
        ("action_rate", 1.01),
        ("suspicion", -0.01),
        ("clue_coverage", 1.01),
    ],
)
def test_signal_snapshot_rejects_values_outside_unit_interval(
    field: str,
    value: float,
) -> None:
    payload = {
        "beat_id": "investigation",
        "time_pressure": 0.5,
        "action_rate": 0.5,
        "suspicion": 0.5,
        "clue_coverage": 0.5,
        field: value,
    }

    with pytest.raises(ValidationError):
        PacingSignalSnapshot.model_validate(payload)


def test_stall_threshold_emits_stall_intervention() -> None:
    interventions = evaluate_pacing_interventions(
        snapshot_with_score(0.24),
        pacing_config(),
    )

    assert len(interventions) == 1
    intervention = interventions[0]
    assert intervention.intervention_type == PacingInterventionType.stall
    assert (
        intervention.recommended_action
        == PacingRecommendedAction.inject_clue_or_narrator_prompt
    )
    assert intervention.beat_id == "investigation"
    assert intervention.tension_score_at_trigger == pytest.approx(0.24)
    assert intervention.threshold == pytest.approx(0.25)


def test_misdirection_threshold_emits_misdirection_intervention() -> None:
    interventions = evaluate_pacing_interventions(
        snapshot_with_score(0.84),
        pacing_config(),
    )

    assert len(interventions) == 1
    intervention = interventions[0]
    assert intervention.intervention_type == PacingInterventionType.misdirection
    assert (
        intervention.recommended_action == PacingRecommendedAction.inject_misdirection
    )
    assert intervention.tension_score_at_trigger == pytest.approx(0.84)
    assert intervention.threshold == pytest.approx(0.80)


def test_premium_threshold_takes_precedence_over_misdirection() -> None:
    interventions = evaluate_pacing_interventions(
        snapshot_with_score(0.86),
        pacing_config(),
    )

    assert len(interventions) == 1
    intervention = interventions[0]
    assert intervention.intervention_type == PacingInterventionType.quality_upgrade
    assert (
        intervention.recommended_action == PacingRecommendedAction.upgrade_quality_tier
    )
    assert intervention.tension_score_at_trigger == pytest.approx(0.86)
    assert intervention.threshold == pytest.approx(0.85)


@pytest.mark.parametrize("score", [0.25, 0.5, 0.80])
def test_no_intervention_when_no_threshold_is_crossed(score: float) -> None:
    interventions = evaluate_pacing_interventions(
        snapshot_with_score(score),
        pacing_config(),
    )

    assert interventions == []
