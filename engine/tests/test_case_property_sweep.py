"""AW-281 - exactly 1000 seeds per skeleton, forced (not sampled).

Asserts that no seed produces a case that violates a fairness invariant
or a resolver-shape invariant (cast size, unique culprit, non-empty
evidence), for exactly 1000 seeds against EACH of the three authored
skeletons via ``forced_skeleton_id``, matching the documented sweep
size per skeleton rather than approximating it through the seeded
skeleton pick's distribution.
"""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from engine.arc.models import ArcDefinition
from engine.case import resolve
from engine.case.errors import CaseInvariantError

REPO_ROOT = Path(__file__).resolve().parents[2]
ARC_PATH = REPO_ROOT / "nightcap" / "couch-race.arc.json"

SEEDS_PER_SKELETON = 1000
SKELETON_IDS = ("locked_room_poisoning", "alibi_collapse", "pre_conspiracy_fall")


@pytest.fixture(scope="module")
def arc() -> ArcDefinition:
    return ArcDefinition.model_validate_json(ARC_PATH.read_text("utf-8"))


@pytest.mark.slow
@pytest.mark.parametrize("skeleton_id", SKELETON_IDS)
def test_sweep_invariants_hold_for_exactly_1000_seeds(
    arc: ArcDefinition, skeleton_id: str
) -> None:
    start = time.perf_counter()
    failures: list[str] = []
    count = 0
    for seed in range(SEEDS_PER_SKELETON):
        try:
            case = resolve(
                arc,
                seed=seed,
                participant_ids=[f"p{i + 1}" for i in range((seed % 7) + 2)],
                forced_skeleton_id=skeleton_id,
            )
        except CaseInvariantError as exc:
            failures.append(f"seed={seed}: {exc}")
            continue
        count += 1
        assert case.skeleton_id == skeleton_id
        suspects = [m for m in case.cast if m.role == "suspect"]
        if not suspects:
            failures.append(f"seed={seed}: no suspects")
        if len([m for m in suspects if m.is_culprit]) != 1:
            failures.append(f"seed={seed}: not exactly one culprit")
        genuine_evidence = [e for e in case.evidence if e.truth_value == "genuine"]
        if not genuine_evidence:
            failures.append(f"seed={seed}: no genuine evidence")
        predicates = {f.predicate for f in case.facts}
        expected_predicates = {"method", "motive", "secret", "relationship", "twist"}
        if predicates != expected_predicates:
            failures.append(
                f"seed={seed}: fact predicates {predicates} != {expected_predicates}"
            )
    elapsed = time.perf_counter() - start
    assert not failures, (
        f"{len(failures)} failures out of {SEEDS_PER_SKELETON} seeds "
        f"(skeleton={skeleton_id}); first 5: {failures[:5]}"
    )
    assert count == SEEDS_PER_SKELETON
    # Throughput sanity: fail if we cannot resolve 100 cases/second on this
    # machine for a single skeleton's share of the sweep.
    if elapsed > 15:
        pytest.fail(
            f"sweep for skeleton={skeleton_id} took {elapsed:.1f}s > 15s; "
            "either the resolver has regressed on perf or "
            "SEEDS_PER_SKELETON was raised without a matching throughput budget."
        )
