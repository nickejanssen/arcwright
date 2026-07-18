"""AW-281 — Validate all shipped case skeletons against the CaseSkeleton schema."""

from __future__ import annotations

from pathlib import Path

import pytest

from engine.case import CaseSkeleton

REPO_ROOT = Path(__file__).resolve().parents[2]
SKELETON_DIR = REPO_ROOT / "nightcap" / "case_skeletons"

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
