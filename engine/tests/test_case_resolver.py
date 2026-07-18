"""AW-281 — case resolver: determinism, cast-size formula, invariants."""

from __future__ import annotations

from pathlib import Path

import pytest

from engine.arc.models import ArcDefinition
from engine.case import resolve

REPO_ROOT = Path(__file__).resolve().parents[2]
ARC_PATH = REPO_ROOT / "nightcap" / "couch-race.arc.json"


@pytest.fixture(scope="module")
def arc() -> ArcDefinition:
    return ArcDefinition.model_validate_json(ARC_PATH.read_text("utf-8"))


def test_resolve_returns_resolved_case_with_expected_shape(arc: ArcDefinition) -> None:
    case = resolve(arc, seed=42, participant_count=4)
    suspects = [m for m in case.cast if m.role == "suspect"]
    victims = [m for m in case.cast if m.role == "victim"]
    assert len(suspects) == 4
    assert len(victims) == 1
    culprits = [m for m in suspects if m.is_culprit]
    assert len(culprits) == 1
    assert culprits[0].member_id == case.culprit_id


@pytest.mark.parametrize(
    "player_count,expected",
    [(2, 4), (4, 4), (5, 5), (6, 5), (7, 6), (8, 6)],
)
def test_cast_size_scales_with_player_count(
    arc: ArcDefinition, player_count: int, expected: int
) -> None:
    case = resolve(arc, seed=1, participant_count=player_count)
    suspects = [m for m in case.cast if m.role == "suspect"]
    assert len(suspects) == expected


def test_deterministic_replay(arc: ArcDefinition) -> None:
    case_a = resolve(arc, seed=99, participant_count=5)
    case_b = resolve(arc, seed=99, participant_count=5)
    assert case_a == case_b


def test_different_seeds_produce_different_cases(arc: ArcDefinition) -> None:
    cases = [resolve(arc, seed=i, participant_count=4) for i in range(20)]
    culprit_names = {c.cast[0].display_name for c in cases}
    assert len(culprit_names) > 1, "20 seeds should produce >1 distinct culprit name"


def test_participant_count_out_of_range(arc: ArcDefinition) -> None:
    from engine.case.errors import CaseResolutionError

    with pytest.raises(CaseResolutionError):
        resolve(arc, seed=1, participant_count=1)
    with pytest.raises(CaseResolutionError):
        resolve(arc, seed=1, participant_count=9)


def test_case_id_contains_arc_and_seed(arc: ArcDefinition) -> None:
    case = resolve(arc, seed=7, participant_count=4)
    assert "nightcap-couch-race" in case.case_id
    assert "7" in case.case_id
