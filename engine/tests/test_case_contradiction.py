"""AW-290 Task 3 - anchor-based contradiction detection.

A location alibi contradiction must be detected by comparing typed
CaseAnchor fields (time_ordinal, location_ref) only, never by matching
generated prose. See engine/case/contradiction.py's module docstring for
the architecture rationale.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from engine.arc.models import ArcDefinition
from engine.case import resolve
from engine.case.contradiction import find_anchor_contradictions
from engine.case.models import (
    AuthorizedFalsehood,
    CaseAnchor,
    EvidenceEntry,
    ResolvedCase,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
ARC_PATH = REPO_ROOT / "nightcap" / "couch-race.arc.json"
CONTRADICTION_MODULE_PATH = REPO_ROOT / "engine" / "case" / "contradiction.py"


@pytest.fixture(scope="module")
def arc() -> ArcDefinition:
    return ArcDefinition.model_validate_json(ARC_PATH.read_text("utf-8"))


def _evidence(evidence_id: str, anchor_id: str | None) -> EvidenceEntry:
    return EvidenceEntry(
        evidence_id=evidence_id,
        evidence_type="testimony",
        text="placeholder",
        points_toward=[],
        points_away_from=[],
        delivery="group",
        truth_value="genuine",
        short_label="placeholder",
        anchor_id=anchor_id,
    )


def _falsehood(
    falsehood_id: str, anchor_id: str | None, topic: str = "location"
) -> AuthorizedFalsehood:
    return AuthorizedFalsehood(
        falsehood_id=falsehood_id,
        speaker_id="s1",
        topic=topic,
        claim_text="placeholder",
        contradicted_by=["e1"],
        anchor_id=anchor_id,
    )


def _case_with(
    anchors: list[CaseAnchor],
    lie_anchor: str | None,
    evidence_anchor: str | None,
    topic: str = "location",
) -> ResolvedCase:
    return ResolvedCase(
        case_id="case::test",
        arc_id="arc::test",
        seed=1,
        skeleton_id="skeleton::test",
        cast=[],
        culprit_id="s1",
        evidence=[_evidence("e1", evidence_anchor)],
        falsehoods=[_falsehood("l1", lie_anchor, topic=topic)],
        facts=[],
        reveal_shape={},
        anchors=anchors,
    )


def test_same_time_different_place_is_a_contradiction() -> None:
    claimed = CaseAnchor(
        anchor_id="a1",
        location_ref="loc_study",
        location_label="the study",
        time_ordinal=3,
        time_label="at nine",
    )
    actual = CaseAnchor(
        anchor_id="a2",
        location_ref="loc_conservatory",
        location_label="the conservatory",
        time_ordinal=3,
        time_label="at nine",
    )
    case = _case_with(anchors=[claimed, actual], lie_anchor="a1", evidence_anchor="a2")
    assert find_anchor_contradictions(case) == [("l1", "e1")]


def test_same_time_same_place_is_not_a_contradiction() -> None:
    anchor = CaseAnchor(
        anchor_id="a1",
        location_ref="loc_study",
        location_label="the study",
        time_ordinal=3,
        time_label="at nine",
    )
    case = _case_with(anchors=[anchor], lie_anchor="a1", evidence_anchor="a1")
    assert find_anchor_contradictions(case) == []


def test_different_time_is_not_a_contradiction() -> None:
    claimed = CaseAnchor(
        anchor_id="a1",
        location_ref="loc_study",
        location_label="the study",
        time_ordinal=1,
        time_label="at eight",
    )
    actual = CaseAnchor(
        anchor_id="a2",
        location_ref="loc_conservatory",
        location_label="the conservatory",
        time_ordinal=3,
        time_label="at nine",
    )
    case = _case_with(anchors=[claimed, actual], lie_anchor="a1", evidence_anchor="a2")
    assert find_anchor_contradictions(case) == []


def test_resolved_case_yields_a_detected_contradiction(arc: ArcDefinition) -> None:
    case = resolve(arc, seed=4242, participant_ids=["p1", "p2", "p3"])
    assert find_anchor_contradictions(case), (
        "a resolved case must contain at least one anchor contradiction"
    )


def test_detection_uses_no_string_matching() -> None:
    source = CONTRADICTION_MODULE_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and node.attr in {
            "startswith",
            "endswith",
            "find",
            "index",
            "match",
            "search",
        }:
            raise AssertionError(f"string matching used: .{node.attr}()")
        if isinstance(node, ast.Compare):
            for op in node.ops:
                assert not isinstance(op, (ast.In, ast.NotIn)), (
                    "membership test on text is not a typed comparison"
                )
