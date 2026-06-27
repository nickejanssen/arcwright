from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from engine.mini_games import (
    ContentMode,
    MiniGameDefinition,
    MiniGameLifecycle,
    MiniGameManifest,
    MiniGamePackageError,
    ParticipationMode,
    load_mini_game_catalog,
    load_mini_game_package,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
MINI_GAME_ROOT = REPO_ROOT / "nightcap" / "mini_games"


@pytest.mark.parametrize(
    ("fixture_name", "expected_mode"),
    [
        ("individual", ParticipationMode.individual),
        ("collaborative", ParticipationMode.collaborative),
        ("group", ParticipationMode.group),
    ],
)
def test_non_shipping_fixtures_validate(
    fixture_name: str, expected_mode: ParticipationMode
) -> None:
    loaded = load_mini_game_package(MINI_GAME_ROOT / "_fixtures" / fixture_name)

    assert loaded.definition.participation_mode is expected_mode
    assert loaded.manifest.lifecycle is MiniGameLifecycle.playtest


def test_authoring_template_validates() -> None:
    loaded = load_mini_game_package(MINI_GAME_ROOT / "_template")

    assert loaded.manifest.lifecycle is MiniGameLifecycle.draft
    assert loaded.definition.version == "0.1.0"


def test_reserved_directories_are_not_loaded_as_production_catalog() -> None:
    catalog = load_mini_game_catalog(MINI_GAME_ROOT)
    assert set(catalog.keys()) == {"crime-scene-smash", "evidence-locker-402"}
    for game_id, loaded in catalog.items():
        assert loaded.manifest.lifecycle is MiniGameLifecycle.active, (
            f"production catalog must contain only active packages; "
            f"{game_id} is {loaded.manifest.lifecycle.value}"
        )


def test_non_active_packages_are_not_loaded_into_production_catalog(
    tmp_path: Path,
) -> None:
    _write_package(
        tmp_path / "draft-game", game_id="draft-game", lifecycle=MiniGameLifecycle.draft
    )
    _write_package(
        tmp_path / "playtest-game",
        game_id="playtest-game",
        lifecycle=MiniGameLifecycle.playtest,
    )
    _write_package(
        tmp_path / "active-game",
        game_id="active-game",
        lifecycle=MiniGameLifecycle.active,
    )

    catalog = load_mini_game_catalog(tmp_path)

    assert set(catalog) == {"active-game"}


def test_duplicate_game_ids_are_rejected(tmp_path: Path) -> None:
    _write_package(
        tmp_path / "duplicate-game",
        game_id="duplicate-game",
        lifecycle=MiniGameLifecycle.active,
    )
    _write_package(
        tmp_path / "duplicate-game-copy",
        game_id="duplicate-game",
        lifecycle=MiniGameLifecycle.active,
    )

    with pytest.raises(MiniGamePackageError, match="does not match"):
        load_mini_game_catalog(tmp_path)


def test_directory_name_must_match_manifest_game_id(tmp_path: Path) -> None:
    _write_package(
        tmp_path / "directory-name",
        game_id="different-id",
        lifecycle=MiniGameLifecycle.active,
    )

    with pytest.raises(MiniGamePackageError, match="does not match"):
        load_mini_game_catalog(tmp_path)


def test_matching_directory_and_game_id_loads(tmp_path: Path) -> None:
    _write_package(
        tmp_path / "matching-game",
        game_id="matching-game",
        lifecycle=MiniGameLifecycle.active,
    )

    catalog = load_mini_game_catalog(tmp_path)

    assert set(catalog) == {"matching-game"}


def test_missing_definition_is_rejected(tmp_path: Path) -> None:
    package_path = tmp_path / "missing-definition"
    package_path.mkdir()
    _write_json(package_path / "manifest.json", _manifest_payload("missing-game"))

    with pytest.raises(MiniGamePackageError, match="missing package file"):
        load_mini_game_package(package_path)


@pytest.mark.parametrize(
    "unsafe_path",
    ["../outside.json", "/absolute.json", "C:/outside.json", "bad\\path.json"],
)
def test_unsafe_definition_paths_are_rejected(unsafe_path: str) -> None:
    payload = _manifest_payload("unsafe-game")
    payload["definition_path"] = unsafe_path

    with pytest.raises(ValidationError, match="package path"):
        MiniGameManifest.model_validate(payload)


def test_invalid_lifecycle_is_rejected() -> None:
    payload = _manifest_payload("invalid-lifecycle")
    payload["lifecycle"] = "production"

    with pytest.raises(ValidationError):
        MiniGameManifest.model_validate(payload)


def test_invalid_semantic_version_is_rejected() -> None:
    payload = _manifest_payload("invalid-version")
    payload["current_version"] = "v1"

    with pytest.raises(ValidationError):
        MiniGameManifest.model_validate(payload)


def test_content_mode_requires_matching_content_inputs() -> None:
    payload = _definition_payload("generative-game")
    payload["content_mode"] = ContentMode.generative.value
    payload["authored_content"] = None
    payload["generation_constraints"] = None

    with pytest.raises(ValidationError, match="generation_constraints"):
        MiniGameDefinition.model_validate(payload)


def _write_package(
    package_path: Path,
    *,
    game_id: str,
    lifecycle: MiniGameLifecycle = MiniGameLifecycle.draft,
) -> None:
    definitions_path = package_path / "definitions"
    definitions_path.mkdir(parents=True)
    _write_json(
        package_path / "manifest.json",
        _manifest_payload(game_id, lifecycle=lifecycle),
    )
    _write_json(definitions_path / "0.1.0.json", _definition_payload(game_id))


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def _manifest_payload(
    game_id: str,
    *,
    lifecycle: MiniGameLifecycle = MiniGameLifecycle.draft,
) -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "game_id": game_id,
        "title": "Test Game",
        "lifecycle": lifecycle.value,
        "current_version": "0.1.0",
        "definition_path": "definitions/0.1.0.json",
        "asset_paths": [],
    }


def _definition_payload(game_id: str) -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "game_id": game_id,
        "version": "0.1.0",
        "mechanic_type": "test-mechanic",
        "participation_mode": "individual",
        "content_mode": "authored",
        "min_players": 1,
        "max_players": 10,
        "duration_seconds": 30,
        "rules": {},
        "authored_content": {"instructions": "Test"},
        "generation_constraints": None,
        "behavioral_outputs": [],
        "clue_fallback": {
            "delay_seconds": 10,
            "clue_variant": "reduced",
            "host_override": True,
        },
    }
