"""AW-281 - Validate all shipped case skeletons against the CaseSkeleton schema."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from engine.case import CaseSkeleton

REPO_ROOT = Path(__file__).resolve().parents[2]
SKELETON_DIR = REPO_ROOT / "nightcap" / "case_skeletons"
TAXONOMY_DIR = REPO_ROOT / "nightcap" / "case_taxonomy"

EXPECTED = ("locked_room_poisoning", "alibi_collapse", "pre_conspiracy_fall")


@pytest.mark.parametrize("skeleton_id", EXPECTED)
def test_skeleton_validates(skeleton_id: str) -> None:
    path = SKELETON_DIR / f"{skeleton_id}.json"
    assert path.exists(), f"missing skeleton: {path}"
    skel = CaseSkeleton.model_validate_json(path.read_text("utf-8"))
    assert skel.skeleton_id == skeleton_id


@pytest.mark.parametrize("skeleton_id", EXPECTED)
def test_skeleton_clue_chain_has_stages(skeleton_id: str) -> None:
    path = SKELETON_DIR / f"{skeleton_id}.json"
    skel = CaseSkeleton.model_validate_json(path.read_text("utf-8"))
    stages = skel.clue_chain_pattern.get("stages", [])
    assert len(stages) >= 3, f"{skeleton_id} needs >=3 deduction stages"


@pytest.mark.parametrize("skeleton_id", EXPECTED)
def test_skeleton_reveal_has_steps(skeleton_id: str) -> None:
    path = SKELETON_DIR / f"{skeleton_id}.json"
    skel = CaseSkeleton.model_validate_json(path.read_text("utf-8"))
    steps = skel.reveal_shape.get("steps", [])
    assert len(steps) >= 4, f"{skeleton_id} reveal needs >=4 steps"


@pytest.mark.parametrize("skeleton_id", EXPECTED)
def test_skeleton_covers_suspect_roles(skeleton_id: str) -> None:
    path = SKELETON_DIR / f"{skeleton_id}.json"
    skel = CaseSkeleton.model_validate_json(path.read_text("utf-8"))
    assert len(skel.lie_shapes_by_role) >= 3


@pytest.mark.parametrize("skeleton_id", EXPECTED)
def test_skeleton_method_family_id_exists_in_taxonomy(skeleton_id: str) -> None:
    path = SKELETON_DIR / f"{skeleton_id}.json"
    skel = CaseSkeleton.model_validate_json(path.read_text("utf-8"))
    method_families = json.loads(
        (TAXONOMY_DIR / "method_families.json").read_text("utf-8")
    )["families"]
    known_ids = {f["family_id"] for f in method_families}
    assert skel.method_family_id in known_ids, (
        f"{skeleton_id} references unknown method_family_id "
        f"{skel.method_family_id!r}; known ids: {sorted(known_ids)}"
    )


def test_skeletons_reference_distinct_method_families() -> None:
    # Not a hard requirement, but a coherence signal: if every skeleton
    # points at the same method family, the archetype/method coupling
    # this task exists to enforce is not actually being exercised.
    family_ids = set()
    for skeleton_id in EXPECTED:
        path = SKELETON_DIR / f"{skeleton_id}.json"
        skel = CaseSkeleton.model_validate_json(path.read_text("utf-8"))
        family_ids.add(skel.method_family_id)
    assert len(family_ids) == len(EXPECTED)
