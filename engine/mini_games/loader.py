"""Filesystem loader for authored mini-game packages."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TypeVar

from pydantic import ValidationError

from engine.mini_games.models import (
    MiniGameDefinition,
    MiniGameLifecycle,
    MiniGameManifest,
)

_ModelT = TypeVar("_ModelT", MiniGameManifest, MiniGameDefinition)


class MiniGamePackageError(ValueError):
    """Raised when a mini-game package is incomplete or internally inconsistent."""


@dataclass(frozen=True)
class LoadedMiniGame:
    package_path: Path
    manifest: MiniGameManifest
    definition: MiniGameDefinition


def load_mini_game_package(package_path: Path) -> LoadedMiniGame:
    """Load and cross-check one package without executing client or runtime code."""
    resolved_package = package_path.resolve()
    manifest_path = resolved_package / "manifest.json"
    manifest = _load_model(manifest_path, MiniGameManifest)
    definition_path = _resolve_package_child(resolved_package, manifest.definition_path)
    definition = _load_model(definition_path, MiniGameDefinition)

    if definition.game_id != manifest.game_id:
        raise MiniGamePackageError(
            "definition game_id must match the package manifest game_id"
        )
    if definition.version != manifest.current_version:
        raise MiniGamePackageError(
            "definition version must match the manifest current_version"
        )

    for asset_path in manifest.asset_paths:
        resolved_asset = _resolve_package_child(resolved_package, asset_path)
        if not resolved_asset.exists():
            raise MiniGamePackageError(f"missing package asset: {asset_path}")

    return LoadedMiniGame(
        package_path=resolved_package,
        manifest=manifest,
        definition=definition,
    )


def load_mini_game_catalog(root_path: Path) -> dict[str, LoadedMiniGame]:
    """Load active packages only and reject duplicate game IDs."""
    resolved_root = root_path.resolve()
    if not resolved_root.is_dir():
        raise MiniGamePackageError(f"mini-game catalog does not exist: {root_path}")

    catalog: dict[str, LoadedMiniGame] = {}
    package_paths = sorted(
        path
        for path in resolved_root.iterdir()
        if path.is_dir() and not path.name.startswith("_")
    )
    for package_path in package_paths:
        loaded = load_mini_game_package(package_path)
        if loaded.manifest.lifecycle is not MiniGameLifecycle.active:
            continue
        game_id = loaded.manifest.game_id
        if package_path.name != game_id:
            raise MiniGamePackageError(
                f"package directory {package_path.name} does not match "
                f"manifest game_id {game_id}"
            )
        if game_id in catalog:
            raise MiniGamePackageError(f"duplicate mini-game ID: {game_id}")
        catalog[game_id] = loaded
    return catalog


def _load_model(
    path: Path,
    model_type: type[_ModelT],
) -> _ModelT:
    if not path.is_file():
        raise MiniGamePackageError(f"missing package file: {path}")
    try:
        return model_type.model_validate_json(path.read_text(encoding="utf-8"))
    except (OSError, ValidationError, ValueError) as exc:
        raise MiniGamePackageError(f"invalid package file {path}: {exc}") from exc


def _resolve_package_child(package_path: Path, relative_path: str) -> Path:
    child = (package_path / relative_path).resolve()
    if not child.is_relative_to(package_path):
        raise MiniGamePackageError(
            f"package path escapes the mini-game directory: {relative_path}"
        )
    return child
