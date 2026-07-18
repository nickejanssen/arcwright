"""AW-281 — 1000-seed property sweep per skeleton.

Asserts that no seed produces a case that violates a fairness invariant
or a resolver-shape invariant (cast size, unique culprit, non-empty
evidence).
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
def test_sweep_invariants_hold_over_many_seeds(arc: ArcDefinition) -> None:
    start = time.perf_counter()
    failures: list[str] = []
    skeleton_counts: dict[str, int] = {sid: 0 for sid in SKELETON_IDS}
    count = 0
    # 3 * 1000 = 3000 cases total; seed range 0..2999.
    for seed in range(3 * SEEDS_PER_SKELETON):
        try:
            case = resolve(arc, seed=seed, participant_count=(seed % 7) + 2)
        except CaseInvariantError as exc:
            failures.append(f"seed={seed}: {exc}")
            continue
        count += 1
        skeleton_counts[case.skeleton_id] = skeleton_counts.get(case.skeleton_id, 0) + 1
        # Post-resolution shape invariants
        suspects = [m for m in case.cast if m.role == "suspect"]
        if not suspects:
            failures.append(f"seed={seed}: no suspects")
        if len([m for m in suspects if m.is_culprit]) != 1:
            failures.append(f"seed={seed}: not exactly one culprit")
        genuine_evidence = [e for e in case.evidence if e.truth_value == "genuine"]
        if not genuine_evidence:
            failures.append(f"seed={seed}: no genuine evidence")
    elapsed = time.perf_counter() - start
    assert not failures, (
        f"{len(failures)} failures out of {3 * SEEDS_PER_SKELETON} seeds; first 5: {failures[:5]}"
    )
    assert count == 3 * SEEDS_PER_SKELETON
    # Skeleton coverage: every authored skeleton must actually be exercised,
    # and with a non-trivial share of the sweep — a regression that biases
    # or drops a skeleton from rotation should fail this test, not pass
    # silently because the other two skeletons happened to cover the count.
    missing = [sid for sid in SKELETON_IDS if skeleton_counts.get(sid, 0) == 0]
    assert not missing, (
        f"skeleton(s) never selected across {count} resolutions: {missing}"
    )
    min_expected = int(0.5 * SEEDS_PER_SKELETON)  # generous floor; true target ~1000
    underrepresented = {
        sid: n for sid, n in skeleton_counts.items() if n < min_expected
    }
    assert not underrepresented, (
        f"skeleton(s) underrepresented (expected >= {min_expected} each, "
        f"got {underrepresented}) — possible bias in _pick_skeleton"
    )
    # Throughput sanity: fail if we cannot resolve 100 cases/second on this machine.
    if elapsed > 30:
        pytest.fail(
            f"sweep took {elapsed:.1f}s > 30s; either the resolver has "
            "regressed on perf or SEEDS_PER_SKELETON was raised without "
            "a matching throughput budget."
        )
