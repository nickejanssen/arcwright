"""Pure, deterministic point-math functions for the AW-284 scoring tables."""

from __future__ import annotations

EVIDENCE_POINT_VALUE = 10
CATCH_POINT_VALUE = 50

_MOMENTUM_TABLE = {0: 0.0, 1: 0.10, 2: 0.20, 3: 0.30, 4: 0.40}
_MOMENTUM_CAP = 0.50

# Anchors are ordered by session position: Grill start, Twist midpoint,
# and Last Call end. Progress is 0.0 at beat start and 1.0 at beat end.
_ACCUSATION_ANCHORS: list[tuple[str, float, int]] = [
    ("grill", 0.0, 200),
    ("twist", 0.5, 130),
    ("last_call", 1.0, 60),
]

_WRONG_ACCUSATION_COST: dict[str, tuple[float, int]] = {
    "grill": (1.0, -20),
    "twist": (1.5, -40),
    "last_call": (1.0, -60),
}
_ESCALATION_FACTOR = 1.5

_CHAIN_REACTION_CUT = 0.20
_CHAIN_REACTION_FLOOR_SECONDS = 30


def evidence_points(count: int) -> int:
    return count * EVIDENCE_POINT_VALUE


def momentum_multiplier(catches_banked: int) -> float:
    if catches_banked >= 5:
        return _MOMENTUM_CAP
    return _MOMENTUM_TABLE[catches_banked]


def accusation_base_value(beat_id: str, *, beat_progress_fraction: float) -> int:
    """Interpolate the accusation earliness curve across the approved anchors."""
    anchor_index = next(
        i for i, (bid, _, _) in enumerate(_ACCUSATION_ANCHORS) if bid == beat_id
    )
    _, frac, _ = _ACCUSATION_ANCHORS[anchor_index]
    if beat_progress_fraction <= frac or anchor_index == 0:
        if anchor_index == 0:
            lo = _ACCUSATION_ANCHORS[0]
            hi = _ACCUSATION_ANCHORS[1]
        else:
            lo = _ACCUSATION_ANCHORS[anchor_index - 1]
            hi = _ACCUSATION_ANCHORS[anchor_index]
    elif anchor_index == len(_ACCUSATION_ANCHORS) - 1:
        lo = _ACCUSATION_ANCHORS[anchor_index - 1]
        hi = _ACCUSATION_ANCHORS[anchor_index]
    else:
        lo = _ACCUSATION_ANCHORS[anchor_index]
        hi = _ACCUSATION_ANCHORS[anchor_index + 1]

    _, lo_frac, lo_value = lo
    _, hi_frac, hi_value = hi
    span = hi_frac - lo_frac
    t = 0.0 if span == 0 else (beat_progress_fraction - lo_frac) / span
    t = max(0.0, min(1.0, t))
    return round(lo_value + (hi_value - lo_value) * t)


def motive_method_bonus(*, motive_correct: bool, method_correct: bool) -> int:
    bonus = 0
    if motive_correct:
        bonus += 25
    if method_correct:
        bonus += 25
    return bonus


def wrong_accusation_cost(
    beat_id: str, *, repeat_offense_count: int
) -> tuple[float, int]:
    """Return the beat-scoped lockout and penalty for a wrong accusation."""
    base_lockout, base_penalty = _WRONG_ACCUSATION_COST[beat_id]
    escalation = _ESCALATION_FACTOR**repeat_offense_count
    return base_lockout * escalation, round(base_penalty * escalation)


def chain_reaction_countdown(
    remaining_seconds: float, *, additional_correct_count: int
) -> float:
    """Apply compounding 20 percent cuts while preserving the 30 second floor."""
    value = remaining_seconds
    for _ in range(additional_correct_count):
        value *= 1 - _CHAIN_REACTION_CUT
    return max(value, _CHAIN_REACTION_FLOOR_SECONDS)
