"""AW-281 — synthetic detective across 100 seeds × 3 skeletons."""

from __future__ import annotations

from pathlib import Path

import pytest

from engine.arc.models import ArcDefinition
from engine.case import resolve, synthetic_detective

REPO_ROOT = Path(__file__).resolve().parents[2]
ARC_PATH = REPO_ROOT / "nightcap" / "couch-race.arc.json"


@pytest.fixture(scope="module")
def arc() -> ArcDefinition:
    return ArcDefinition.model_validate_json(ARC_PATH.read_text("utf-8"))


@pytest.mark.slow
def test_detective_wins_across_seed_sweep(arc: ArcDefinition) -> None:
    losses: list[str] = []
    total = 0
    for seed in range(300):
        participant_count = (seed % 7) + 2
        case = resolve(arc, seed=seed, participant_count=participant_count)
        verdict = synthetic_detective(case)
        total += 1
        if not verdict.won:
            losses.append(
                f"seed={seed} skeleton={case.skeleton_id} "
                f"culprit={case.culprit_id} guess={verdict.culprit_id}"
            )
    assert not losses, (
        f"{len(losses)} solver losses out of {total}; first 5: {losses[:5]}"
    )


def test_detective_matches_culprit_on_single_seed(arc: ArcDefinition) -> None:
    case = resolve(arc, seed=1, participant_count=4)
    verdict = synthetic_detective(case)
    assert verdict.won is True
    assert verdict.culprit_id == case.culprit_id
