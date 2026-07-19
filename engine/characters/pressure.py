"""Per-character social pressure compute per §7.4."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from engine.resources.models import EffectActivation

_W_ACCUSATION: float = 0.5
_W_DIRECTED_QUESTIONS: float = 0.3
_W_ALLIANCE_ISOLATION: float = 0.2
_W_GAZE_SIGNAL: float = 0.0  # zero-weighted at v1; no surface emits gaze data yet


@dataclass(frozen=True)
class SocialPressureSignals:
    accusation_weight: float
    question_intensity: float
    alliance_isolation: float
    gaze_signal: float = 0.0


@dataclass(frozen=True)
class SocialPressureWeights:
    accusation: float = _W_ACCUSATION
    directed_questions: float = _W_DIRECTED_QUESTIONS
    alliance_isolation: float = _W_ALLIANCE_ISOLATION
    gaze_signal: float = _W_GAZE_SIGNAL


def compute_social_pressure(
    signals: SocialPressureSignals,
    weights: SocialPressureWeights | None = None,
) -> float:
    """Return per-character social pressure as a 0.0-1.0 weighted sum per §7.4.

    Gaze-signal slot exists but is zero-weighted at v1; no surface emits it yet.
    """
    w = weights if weights is not None else SocialPressureWeights()
    raw = (
        signals.accusation_weight * w.accusation
        + signals.question_intensity * w.directed_questions
        + signals.alliance_isolation * w.alliance_isolation
        + signals.gaze_signal * w.gaze_signal
    )
    return min(max(raw, 0.0), 1.0)


def apply_per_question_pressure_boost(
    baseline: float | None,
    *,
    activation: EffectActivation | None,
    target_id: UUID,
    pressure_effect_key: str,
    boost: float,
) -> float | None:
    """Apply one resolved effect's pressure boost to its targeted question only."""
    if (
        activation is None
        or activation.effect_key != pressure_effect_key
        or activation.target_id != str(target_id)
    ):
        return baseline
    return min(max((baseline or 0.0) + boost, 0.0), 1.0)
