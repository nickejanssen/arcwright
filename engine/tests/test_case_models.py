"""AW-281 — Pydantic validation for engine/case/ domain models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from engine.case import (
    AuthorizedFalsehood,
    CaseInvariantError,
    CaseResolutionError,
    CaseSkeleton,
    CastMember,
    EvidenceEntry,
    ResolvedCase,
)


def test_cast_member_minimal() -> None:
    m = CastMember(
        member_id="s1",
        display_name="Delacourt",
        role="suspect",
    )
    assert m.role == "suspect"
    assert m.is_culprit is False


def test_cast_member_culprit_flag() -> None:
    m = CastMember(
        member_id="s3",
        display_name="Ashford",
        role="suspect",
        is_culprit=True,
    )
    assert m.is_culprit is True


def test_evidence_entry_minimal() -> None:
    e = EvidenceEntry(
        evidence_id="e1",
        evidence_type="trace",
        text="A faint bruise on the left hand.",
        points_toward=["s3"],
        points_away_from=[],
        delivery="private",
        delivery_target="p1",
    )
    assert e.points_toward == ["s3"]


def test_authorized_falsehood_minimal() -> None:
    lie = AuthorizedFalsehood(
        falsehood_id="l1",
        speaker_id="s2",
        topic="location",
        claim_text="I was on the terrace at nine.",
        contradicted_by=["e5"],
    )
    assert lie.contradicted_by == ["e5"]


def test_resolved_case_minimal() -> None:
    culprit = CastMember(
        member_id="s1", display_name="A", role="suspect", is_culprit=True
    )
    victim = CastMember(member_id="v1", display_name="V", role="victim")
    ev = EvidenceEntry(
        evidence_id="e1",
        evidence_type="trace",
        text="a torn playbill",
        points_toward=["s1"],
        points_away_from=[],
        delivery="group",
        delivery_target=None,
    )
    case = ResolvedCase(
        case_id="c1",
        arc_id="nightcap-couch-race-v1",
        seed=42,
        skeleton_id="locked_room_poisoning",
        cast=[culprit, victim],
        culprit_id="s1",
        evidence=[ev],
        falsehoods=[],
        reveal_shape={"steps": []},
    )
    assert case.culprit_id == "s1"


def test_case_skeleton_forbids_extra() -> None:
    with pytest.raises(ValidationError):
        CaseSkeleton(
            skeleton_id="x",
            archetype="poisoning",
            clue_chain_pattern={"stages": []},
            lie_shapes_by_role={},
            reveal_shape={"steps": []},
            unknown_field="oops",  # type: ignore[call-arg]
        )


def test_resolved_case_forbids_extra() -> None:
    with pytest.raises(ValidationError):
        ResolvedCase(  # type: ignore[call-arg]
            case_id="c1",
            arc_id="nightcap-couch-race-v1",
            seed=42,
            skeleton_id="s",
            cast=[],
            culprit_id="",
            evidence=[],
            falsehoods=[],
            reveal_shape={"steps": []},
            unknown="nope",
        )


def test_error_types_are_exception_subclasses() -> None:
    assert issubclass(CaseInvariantError, Exception)
    assert issubclass(CaseResolutionError, Exception)


def test_round_trip_json() -> None:
    culprit = CastMember(
        member_id="s1", display_name="A", role="suspect", is_culprit=True
    )
    victim = CastMember(member_id="v1", display_name="V", role="victim")
    case = ResolvedCase(
        case_id="c1",
        arc_id="nightcap-couch-race-v1",
        seed=42,
        skeleton_id="locked_room_poisoning",
        cast=[culprit, victim],
        culprit_id="s1",
        evidence=[],
        falsehoods=[],
        reveal_shape={"steps": []},
    )
    payload = case.model_dump()
    restored = ResolvedCase.model_validate(payload)
    assert restored == case


def test_members_by_role() -> None:
    culprit = CastMember(
        member_id="s1", display_name="A", role="suspect", is_culprit=True
    )
    other_suspect = CastMember(member_id="s2", display_name="B", role="suspect")
    victim = CastMember(member_id="v1", display_name="V", role="victim")
    case = ResolvedCase(
        case_id="c1",
        arc_id="nightcap-couch-race-v1",
        seed=42,
        skeleton_id="locked_room_poisoning",
        cast=[culprit, other_suspect, victim],
        culprit_id="s1",
        evidence=[],
        falsehoods=[],
        reveal_shape={"steps": []},
    )
    suspects = case.members_by_role("suspect")
    assert len(suspects) == 2
    assert {m.member_id for m in suspects} == {"s1", "s2"}
    victims = case.members_by_role("victim")
    assert len(victims) == 1
    assert victims[0].member_id == "v1"
    assert case.members_by_role("witness") == []
