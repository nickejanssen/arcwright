"""AW-281 - case resolver: determinism, cast-size formula, invariants."""

from __future__ import annotations

from pathlib import Path

import pytest

from engine.arc.models import ArcDefinition
from engine.case import resolve
from engine.case.errors import CaseResolutionError

REPO_ROOT = Path(__file__).resolve().parents[2]
ARC_PATH = REPO_ROOT / "nightcap" / "couch-race.arc.json"

SKELETON_IDS = ("locked_room_poisoning", "alibi_collapse", "pre_conspiracy_fall")


@pytest.fixture(scope="module")
def arc() -> ArcDefinition:
    return ArcDefinition.model_validate_json(ARC_PATH.read_text("utf-8"))


def _participant_ids(count: int) -> list[str]:
    return [f"p{i + 1}" for i in range(count)]


def test_resolve_returns_resolved_case_with_expected_shape(arc: ArcDefinition) -> None:
    case = resolve(arc, seed=42, participant_ids=_participant_ids(4))
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
    case = resolve(arc, seed=1, participant_ids=_participant_ids(player_count))
    suspects = [m for m in case.cast if m.role == "suspect"]
    assert len(suspects) == expected


def test_deterministic_replay(arc: ArcDefinition) -> None:
    case_a = resolve(arc, seed=99, participant_ids=_participant_ids(5))
    case_b = resolve(arc, seed=99, participant_ids=_participant_ids(5))
    assert case_a == case_b


def test_different_seeds_produce_different_cases(arc: ArcDefinition) -> None:
    cases = [
        resolve(arc, seed=i, participant_ids=_participant_ids(4)) for i in range(20)
    ]
    culprit_names = {c.cast[0].display_name for c in cases}
    assert len(culprit_names) > 1, "20 seeds should produce >1 distinct culprit name"


def test_participant_count_out_of_range(arc: ArcDefinition) -> None:
    with pytest.raises(CaseResolutionError):
        resolve(arc, seed=1, participant_ids=_participant_ids(1))
    with pytest.raises(CaseResolutionError):
        resolve(arc, seed=1, participant_ids=_participant_ids(9))


def test_duplicate_participant_ids_rejected(arc: ArcDefinition) -> None:
    with pytest.raises(CaseResolutionError, match="duplicates"):
        resolve(arc, seed=1, participant_ids=["p1", "p1", "p2", "p3"])


def test_case_id_contains_arc_and_seed(arc: ArcDefinition) -> None:
    case = resolve(arc, seed=7, participant_ids=_participant_ids(4))
    assert "nightcap-couch-race" in case.case_id
    assert "7" in case.case_id


@pytest.mark.parametrize("skeleton_id", SKELETON_IDS)
def test_forced_skeleton_id_selects_exact_skeleton(
    arc: ArcDefinition, skeleton_id: str
) -> None:
    case = resolve(
        arc,
        seed=1,
        participant_ids=_participant_ids(4),
        forced_skeleton_id=skeleton_id,
    )
    assert case.skeleton_id == skeleton_id


def test_forced_skeleton_id_unknown_raises(arc: ArcDefinition) -> None:
    with pytest.raises(CaseResolutionError, match="forced_skeleton_id"):
        resolve(
            arc,
            seed=1,
            participant_ids=_participant_ids(4),
            forced_skeleton_id="does_not_exist",
        )


def test_resolved_case_carries_case_truth_facts(arc: ArcDefinition) -> None:
    case = resolve(arc, seed=42, participant_ids=_participant_ids(4))
    predicates = {f.predicate for f in case.facts}
    assert predicates == {"method", "motive", "secret", "relationship", "twist"}
    method_facts = case.facts_by_predicate("method")
    assert len(method_facts) == 1
    assert method_facts[0].subject_id == case.culprit_id
    assert method_facts[0].known_by == [case.culprit_id]
    motive_facts = case.facts_by_predicate("motive")
    assert len(motive_facts) == 1
    assert motive_facts[0].subject_id == case.culprit_id
    victim_id = case.members_by_role("victim")[0].member_id
    assert motive_facts[0].object_id == victim_id
    suspects = case.members_by_role("suspect")
    secret_facts = case.facts_by_predicate("secret")
    assert {f.subject_id for f in secret_facts} == {m.member_id for m in suspects}
    relationship_facts = case.facts_by_predicate("relationship")
    assert {f.subject_id for f in relationship_facts} == {m.member_id for m in suspects}
    twist_facts = case.facts_by_predicate("twist")
    assert len(twist_facts) == 1
    assert twist_facts[0].known_by == []


def test_evidence_text_names_the_culprit_by_display_name(arc: ArcDefinition) -> None:
    # Non-circular content check: the resolver's own points_toward/
    # points_away_from bookkeeping is not what makes a case solvable to
    # a human, the actual clue TEXT has to name someone. At least one
    # genuine evidence entry must contain the culprit's display name.
    case = resolve(arc, seed=5, participant_ids=_participant_ids(4))
    culprit_name = next(
        m.display_name for m in case.cast if m.member_id == case.culprit_id
    )
    named_in_text = [e for e in case.evidence if culprit_name in e.text]
    assert named_in_text, (
        f"no genuine evidence names culprit {culprit_name!r}; "
        "a case where the answer only lives in points_toward labels "
        "is not solvable by a human reading the clue text"
    )


def test_private_evidence_has_a_real_delivery_target(arc: ArcDefinition) -> None:
    participant_ids = _participant_ids(4)
    case = resolve(arc, seed=8, participant_ids=participant_ids)
    private_entries = [e for e in case.evidence if e.delivery == "private"]
    assert private_entries, "expected at least one private-delivery evidence entry"
    for entry in private_entries:
        assert entry.delivery_target is not None
        assert entry.delivery_target in participant_ids


def test_lies_are_contradicted_by_topic_matching_evidence(arc: ArcDefinition) -> None:
    case = resolve(arc, seed=11, participant_ids=_participant_ids(4))
    evidence_by_id = {e.evidence_id: e for e in case.evidence}
    for lie in case.falsehoods:
        assert lie.contradicted_by
        for evidence_id in lie.contradicted_by:
            contradicting = evidence_by_id[evidence_id]
            speaker = next(
                m.display_name for m in case.cast if m.member_id == lie.speaker_id
            )
            assert speaker in contradicting.text, (
                f"lie {lie.falsehood_id!r} by {speaker!r} is contradicted by "
                f"evidence {evidence_id!r} which never mentions the speaker: "
                f"{contradicting.text!r}"
            )
