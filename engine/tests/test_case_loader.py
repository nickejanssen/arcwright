"""AW-281 — Loader for skeletons, taxonomies, and case-resolution config."""

from __future__ import annotations

from pathlib import Path

import pytest

from engine.case import CaseSkeleton
from engine.case.errors import CaseResolutionError
from engine.case.loader import (
    load_case_resolution_config,
    load_skeletons,
    load_taxonomy,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
SKELETON_DIR = REPO_ROOT / "nightcap" / "case_skeletons"
TAXONOMY_DIR = REPO_ROOT / "nightcap" / "case_taxonomy"
CONFIG_PATH = REPO_ROOT / "nightcap" / "case_resolution_config.json"


def test_load_skeletons_returns_three() -> None:
    skels = load_skeletons(SKELETON_DIR)
    assert set(skels.keys()) == {
        "locked_room_poisoning",
        "alibi_collapse",
        "pre_conspiracy_fall",
    }
    for value in skels.values():
        assert isinstance(value, CaseSkeleton)


def test_load_skeletons_missing_directory() -> None:
    with pytest.raises(CaseResolutionError):
        load_skeletons(Path("/definitely/does/not/exist/nc"))


def test_load_taxonomy_populates_all_lists() -> None:
    tax = load_taxonomy(TAXONOMY_DIR)
    assert len(tax.motive_families) >= 3
    assert len(tax.method_families) >= 3
    assert len(tax.evidence_types) >= 3
    assert len(tax.lie_topics) >= 3


def test_load_taxonomy_missing_directory() -> None:
    with pytest.raises(CaseResolutionError):
        load_taxonomy(Path("/definitely/does/not/exist/nc"))


def test_load_case_resolution_config() -> None:
    cfg = load_case_resolution_config(CONFIG_PATH)
    assert cfg.arc_id_prefix == "nightcap-couch-race"
    assert cfg.cast_size_by_player_count["2"] == 4
    assert cfg.cast_size_by_player_count["5"] == 5
    assert cfg.cast_size_by_player_count["8"] == 6
