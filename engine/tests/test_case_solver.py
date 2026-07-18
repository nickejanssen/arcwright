"""AW-281 - synthetic detective: exactly 100 seeds per skeleton, per-player
viewpoints, and a negative proof that the solver depends on real evidence
text rather than the resolver's internal points_toward/points_away_from
bookkeeping."""

from __future__ import annotations

from pathlib import Path

import pytest

from engine.arc.models import ArcDefinition
from engine.case import resolve, synthetic_detective

REPO_ROOT = Path(__file__).resolve().parents[2]
ARC_PATH = REPO_ROOT / "nightcap" / "couch-race.arc.json"

SEEDS_PER_SKELETON = 100
SKELETON_IDS = ("locked_room_poisoning", "alibi_collapse", "pre_conspiracy_fall")


@pytest.fixture(scope="module")
def arc() -> ArcDefinition:
    return ArcDefinition.model_validate_json(ARC_PATH.read_text("utf-8"))


def _participant_ids(count: int) -> list[str]:
    return [f"p{i + 1}" for i in range(count)]


@pytest.mark.slow
@pytest.mark.parametrize("skeleton_id", SKELETON_IDS)
def test_detective_wins_exactly_100_seeds_per_skeleton_for_every_viewpoint(
    arc: ArcDefinition, skeleton_id: str
) -> None:
    losses: list[str] = []
    total = 0
    for seed in range(SEEDS_PER_SKELETON):
        participant_count = (seed % 7) + 2
        participant_ids = _participant_ids(participant_count)
        case = resolve(
            arc,
            seed=seed,
            participant_ids=participant_ids,
            forced_skeleton_id=skeleton_id,
        )
        assert case.skeleton_id == skeleton_id
        for viewpoint in participant_ids:
            total += 1
            verdict = synthetic_detective(case, viewpoint)
            if not verdict.won:
                losses.append(
                    f"seed={seed} skeleton={skeleton_id} viewpoint={viewpoint} "
                    f"culprit={case.culprit_id} guess={verdict.culprit_id}"
                )
    assert not losses, (
        f"{len(losses)} solver losses out of {total} (skeleton={skeleton_id}); "
        f"first 5: {losses[:5]}"
    )


def test_detective_matches_culprit_on_single_seed(arc: ArcDefinition) -> None:
    case = resolve(arc, seed=1, participant_ids=_participant_ids(4))
    verdict = synthetic_detective(case, "p1")
    assert verdict.won is True
    assert verdict.culprit_id == case.culprit_id


def test_detective_does_not_read_points_toward_labels(arc: ArcDefinition) -> None:
    # Non-circularity proof: strip points_toward/points_away_from from
    # every evidence entry (set them to empty lists) while leaving the
    # actual clue TEXT untouched. If the solver secretly depended on
    # those labels, this would break it. It must still win, because it
    # only reads text.
    case = resolve(arc, seed=3, participant_ids=_participant_ids(4))
    stripped = case.model_copy(deep=True)
    for e in stripped.evidence:
        e.points_toward = []
        e.points_away_from = []
    verdict = synthetic_detective(stripped, "p1")
    assert verdict.won is True, (
        "solver lost after stripping points_toward/points_away_from labels; "
        "it must derive suspicion from evidence text alone, not these "
        "resolver-internal bookkeeping fields"
    )


def test_detective_fails_on_meaningless_evidence_text(arc: ArcDefinition) -> None:
    # The negative case: if the clue TEXT never names anyone, no human
    # (and no honest solver) can deduce the culprit from it, regardless
    # of what internal labels the resolver happened to attach. A
    # fairness proof that cannot fail on meaningless content is not a
    # real proof.
    case = resolve(arc, seed=3, participant_ids=_participant_ids(4))
    garbled = case.model_copy(deep=True)
    for e in garbled.evidence:
        e.text = "nothing to see here"
    verdict = synthetic_detective(garbled, "p1")
    assert verdict.won is False, (
        "solver won on meaningless evidence text; it is not actually "
        "reading clue content"
    )


def test_detective_respects_private_delivery_partition() -> None:
    # A viewpoint player must not benefit from evidence delivered
    # privately to someone else. Construct a case by hand where the
    # only clue naming the culprit is private to a different player.
    from engine.case.models import CaseFact, CastMember, EvidenceEntry, ResolvedCase

    culprit = CastMember(
        member_id="s1", display_name="Ashford", role="suspect", is_culprit=True
    )
    other = CastMember(member_id="s2", display_name="Bellamy", role="suspect")
    victim = CastMember(member_id="v1", display_name="Marcus", role="victim")
    naming_evidence = EvidenceEntry(
        evidence_id="e1",
        evidence_type="document",
        text="A ledger page ties Ashford directly to the missing funds.",
        points_toward=["s1"],
        points_away_from=[],
        delivery="private",
        delivery_target="p2",
    )
    blank_group_evidence = EvidenceEntry(
        evidence_id="e2",
        evidence_type="trace",
        text="A faint mark, unremarkable, near the door.",
        points_toward=["s1"],
        points_away_from=[],
        delivery="group",
        delivery_target=None,
    )
    case = ResolvedCase(
        case_id="c1",
        arc_id="nightcap-couch-race-v1",
        seed=1,
        skeleton_id="locked_room_poisoning",
        cast=[culprit, other, victim],
        culprit_id="s1",
        evidence=[naming_evidence, blank_group_evidence],
        falsehoods=[],
        facts=[
            CaseFact(
                fact_id="fact_method",
                predicate="method",
                subject_id="s1",
                value="funds",
                known_by=["s1"],
            )
        ],
        reveal_shape={"steps": []},
    )
    # p1 never receives the naming evidence, only p2 does.
    verdict_p1 = synthetic_detective(case, "p1")
    assert verdict_p1.won is False
    verdict_p2 = synthetic_detective(case, "p2")
    assert verdict_p2.won is True
    assert verdict_p2.culprit_id == "s1"
