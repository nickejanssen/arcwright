"""Deterministic dramatic tension scoring and pacing intervention selection."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from engine.arc.models import PacingConfig


class PacingSignalSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    beat_id: str
    time_pressure: float = Field(ge=0.0, le=1.0)
    action_rate: float = Field(ge=0.0, le=1.0)
    suspicion: float = Field(ge=0.0, le=1.0)
    clue_coverage: float = Field(ge=0.0, le=1.0)


class PacingInterventionType(str, Enum):
    stall = "stall"
    misdirection = "misdirection"
    quality_upgrade = "quality_upgrade"


class PacingRecommendedAction(str, Enum):
    inject_clue_or_narrator_prompt = "inject_clue_or_narrator_prompt"
    inject_misdirection = "inject_misdirection"
    upgrade_quality_tier = "upgrade_quality_tier"


class PacingIntervention(BaseModel):
    model_config = ConfigDict(extra="forbid")

    intervention_type: PacingInterventionType
    recommended_action: PacingRecommendedAction
    beat_id: str
    tension_score_at_trigger: float = Field(ge=0.0, le=1.0)
    threshold: float
    signal_snapshot: PacingSignalSnapshot


class DramaticTensionScore:
    def compute(
        self,
        snapshot: PacingSignalSnapshot,
        config: PacingConfig,
    ) -> float:
        return (
            config.w_time * snapshot.time_pressure
            + config.w_action * snapshot.action_rate
            + config.w_suspicion * snapshot.suspicion
            + config.w_coverage * snapshot.clue_coverage
        )

    def evaluate(
        self,
        snapshot: PacingSignalSnapshot,
        config: PacingConfig,
    ) -> list[PacingIntervention]:
        score = self.compute(snapshot, config)

        if score < config.stall_threshold:
            return [
                PacingIntervention(
                    intervention_type=PacingInterventionType.stall,
                    recommended_action=(
                        PacingRecommendedAction.inject_clue_or_narrator_prompt
                    ),
                    beat_id=snapshot.beat_id,
                    tension_score_at_trigger=score,
                    threshold=config.stall_threshold,
                    signal_snapshot=snapshot,
                )
            ]

        if score >= config.premium_threshold:
            return [
                PacingIntervention(
                    intervention_type=PacingInterventionType.quality_upgrade,
                    recommended_action=PacingRecommendedAction.upgrade_quality_tier,
                    beat_id=snapshot.beat_id,
                    tension_score_at_trigger=score,
                    threshold=config.premium_threshold,
                    signal_snapshot=snapshot,
                )
            ]

        if score > config.misdirection_threshold:
            return [
                PacingIntervention(
                    intervention_type=PacingInterventionType.misdirection,
                    recommended_action=PacingRecommendedAction.inject_misdirection,
                    beat_id=snapshot.beat_id,
                    tension_score_at_trigger=score,
                    threshold=config.misdirection_threshold,
                    signal_snapshot=snapshot,
                )
            ]

        return []


def compute_dramatic_tension_score(
    snapshot: PacingSignalSnapshot,
    config: PacingConfig,
) -> float:
    return DramaticTensionScore().compute(snapshot, config)


def evaluate_pacing_interventions(
    snapshot: PacingSignalSnapshot,
    config: PacingConfig,
) -> list[PacingIntervention]:
    return DramaticTensionScore().evaluate(snapshot, config)
