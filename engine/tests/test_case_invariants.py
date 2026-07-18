"""AW-281 - solvability and lie-falsifiability invariant checks."""

from __future__ import annotations

from engine.case.invariants import lie_falsifiability_check, solvability_check
from engine.case.models import (
    AuthorizedFalsehood,
    CastMember,
    EvidenceEntry,
    ResolvedCase,
)


def _base_case(**overrides) -> ResolvedCase:
    culprit = CastMember(
        member_id="s1", display_name="A", role="suspect", is_culprit=True
    )
    other = CastMember(member_id="s2", display_name="B", role="suspect")
    victim = CastMember(member_id="v1", display_name="V", role="victim")
    evidence = [
        EvidenceEntry(
            evidence_id="e1",
            evidence_type="trace",
            text="clue1",
            points_toward=["s1", "s2"],
            points_away_from=[],
            delivery="group",
            delivery_target=None,
        ),
        EvidenceEntry(
            evidence_id="e2",
            evidence_type="document",
            text="clue2",
            points_toward=["s1"],
            points_away_from=[],
            delivery="private",
            delivery_target="p1",
        ),
    ]
    lies = [
        AuthorizedFalsehood(
            falsehood_id="l1",
            speaker_id="s2",
            topic="location",
            claim_text="elsewhere",
            contradicted_by=["e1"],
        ),
    ]
    payload = {
        "case_id": "c1",
        "arc_id": "nightcap-couch-race-v1",
        "seed": 1,
        "skeleton_id": "locked_room_poisoning",
        "cast": [culprit, other, victim],
        "culprit_id": "s1",
        "evidence": evidence,
        "falsehoods": lies,
        "facts": [],
        "reveal_shape": {"steps": []},
    }
    payload.update(overrides)
    return ResolvedCase(**payload)


def test_solvability_passes_for_uniquely_identifying_chain() -> None:
    case = _base_case()
    ok, _ = solvability_check(case)
    assert ok


def test_solvability_fails_when_chain_does_not_narrow_to_culprit() -> None:
    case = _base_case(
        evidence=[
            EvidenceEntry(
                evidence_id="e1",
                evidence_type="trace",
                text="x",
                points_toward=["s1", "s2"],
                points_away_from=[],
                delivery="group",
                delivery_target=None,
            )
        ]
    )
    ok, _ = solvability_check(case)
    assert not ok


def test_lie_falsifiability_passes() -> None:
    case = _base_case()
    ok, _ = lie_falsifiability_check(case)
    assert ok


def test_lie_falsifiability_fails_with_empty_contradiction_list() -> None:
    lie = AuthorizedFalsehood(
        falsehood_id="l1",
        speaker_id="s2",
        topic="location",
        claim_text="x",
        contradicted_by=[],
    )
    case = _base_case(falsehoods=[lie])
    ok, _ = lie_falsifiability_check(case)
    assert not ok


def test_lie_falsifiability_fails_with_missing_evidence_id() -> None:
    lie = AuthorizedFalsehood(
        falsehood_id="l1",
        speaker_id="s2",
        topic="location",
        claim_text="x",
        contradicted_by=["e999"],
    )
    case = _base_case(falsehoods=[lie])
    ok, _ = lie_falsifiability_check(case)
    assert not ok
