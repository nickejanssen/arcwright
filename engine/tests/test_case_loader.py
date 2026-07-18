"""AW-281 - Loader for skeletons, taxonomies, and case-resolution config."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from engine.case import CaseSkeleton
from engine.case.errors import CaseResolutionError
from engine.case.loader import (
    load_case_resolution_config,
    load_skeletons,
    load_taxonomy,
    resolve_case_resolution_config_path,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
SKELETON_DIR = REPO_ROOT / "nightcap" / "case_skeletons"
TAXONOMY_DIR = REPO_ROOT / "nightcap" / "case_taxonomy"
CONFIG_PATH = REPO_ROOT / "nightcap" / "case_resolution_config.json"
CASE_RESOLUTION_REGISTRY_PATH = REPO_ROOT / "config" / "case_resolution_registry.json"


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


def test_load_taxonomy_populates_cast_pool() -> None:
    tax = load_taxonomy(TAXONOMY_DIR)
    assert len(tax.suspect_roles) >= 3
    assert len(tax.suspect_names) >= 4
    assert len(tax.victim_names) >= 1


def test_load_taxonomy_populates_character_facts() -> None:
    tax = load_taxonomy(TAXONOMY_DIR)
    assert len(tax.secrets) >= 6
    assert len(tax.relationships) >= 6


def test_load_taxonomy_lie_topics_carry_templates() -> None:
    tax = load_taxonomy(TAXONOMY_DIR)
    by_id = {entry["topic_id"]: entry for entry in tax.lie_topics}
    for topic_id in ("location", "relationship", "observation", "possession"):
        assert topic_id in by_id
        assert len(by_id[topic_id]["claim_templates"]) >= 2
        assert len(by_id[topic_id]["contradiction_templates"]) >= 2
        assert "{speaker}" in by_id[topic_id]["contradiction_templates"][0]


def test_load_taxonomy_missing_directory() -> None:
    with pytest.raises(CaseResolutionError):
        load_taxonomy(Path("/definitely/does/not/exist/nc"))


def test_load_case_resolution_config() -> None:
    cfg = load_case_resolution_config(CONFIG_PATH)
    assert cfg.arc_id_prefix == "nightcap-couch-race"
    assert cfg.cast_size_by_player_count["2"] == 4
    assert cfg.cast_size_by_player_count["5"] == 5
    assert cfg.cast_size_by_player_count["8"] == 6


def test_load_skeletons_raises_on_duplicate_skeleton_id(tmp_path: Path) -> None:
    skeleton_payload = {
        "skeleton_id": "dup",
        "archetype": "poisoning",
        "method_family_id": "poison",
        "clue_chain_pattern": {"stages": []},
        "lie_shapes_by_role": {},
        "reveal_shape": {"steps": []},
    }
    (tmp_path / "a.json").write_text(json.dumps(skeleton_payload), encoding="utf-8")
    (tmp_path / "b.json").write_text(json.dumps(skeleton_payload), encoding="utf-8")
    with pytest.raises(CaseResolutionError, match="duplicate skeleton_id"):
        load_skeletons(tmp_path)


def test_load_skeletons_raises_on_empty_directory(tmp_path: Path) -> None:
    with pytest.raises(CaseResolutionError, match="no skeletons found"):
        load_skeletons(tmp_path)


def test_load_taxonomy_raises_on_missing_individual_subfile(tmp_path: Path) -> None:
    (tmp_path / "motive_families.json").write_text(
        json.dumps({"families": []}), encoding="utf-8"
    )
    (tmp_path / "method_families.json").write_text(
        json.dumps({"families": []}), encoding="utf-8"
    )
    (tmp_path / "lie_topics.json").write_text(
        json.dumps({"topics": []}), encoding="utf-8"
    )
    # evidence_types.json intentionally missing.
    with pytest.raises(CaseResolutionError, match="taxonomy file missing"):
        load_taxonomy(tmp_path)


def test_load_taxonomy_raises_on_missing_top_level_key(tmp_path: Path) -> None:
    (tmp_path / "motive_families.json").write_text(
        json.dumps({"wrong_key": []}), encoding="utf-8"
    )
    (tmp_path / "method_families.json").write_text(
        json.dumps({"families": []}), encoding="utf-8"
    )
    (tmp_path / "evidence_types.json").write_text(
        json.dumps({"types": []}), encoding="utf-8"
    )
    (tmp_path / "lie_topics.json").write_text(
        json.dumps({"topics": []}), encoding="utf-8"
    )
    with pytest.raises(CaseResolutionError, match="missing expected top-level key"):
        load_taxonomy(tmp_path)


def test_load_case_resolution_config_missing_path(tmp_path: Path) -> None:
    missing = tmp_path / "does_not_exist.json"
    with pytest.raises(CaseResolutionError, match="case-resolution config missing"):
        load_case_resolution_config(missing)


def test_resolve_case_resolution_config_path_matches_couch_race() -> None:
    path = resolve_case_resolution_config_path(
        "nightcap-couch-race-v1", CASE_RESOLUTION_REGISTRY_PATH
    )
    assert path.resolve() == CONFIG_PATH.resolve()


def test_resolve_case_resolution_config_path_no_match_raises() -> None:
    with pytest.raises(CaseResolutionError, match="no case-resolution registration"):
        resolve_case_resolution_config_path(
            "some-other-arc-v1", CASE_RESOLUTION_REGISTRY_PATH
        )


def test_resolve_case_resolution_config_path_missing_registry(tmp_path: Path) -> None:
    missing = tmp_path / "does_not_exist.json"
    with pytest.raises(CaseResolutionError, match="case-resolution registry missing"):
        resolve_case_resolution_config_path("nightcap-couch-race-v1", missing)


def test_resolve_case_resolution_config_path_empty_registry_raises(
    tmp_path: Path,
) -> None:
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps({"registrations": []}), encoding="utf-8")
    with pytest.raises(CaseResolutionError, match="non-empty"):
        resolve_case_resolution_config_path("nightcap-couch-race-v1", registry)


def test_resolve_case_resolution_config_path_malformed_entry_raises(
    tmp_path: Path,
) -> None:
    registry = tmp_path / "registry.json"
    registry.write_text(
        json.dumps({"registrations": [{"arc_id_prefix": "nightcap-couch-race"}]}),
        encoding="utf-8",
    )
    with pytest.raises(CaseResolutionError, match="needs 'arc_id_prefix'"):
        resolve_case_resolution_config_path("nightcap-couch-race-v1", registry)
