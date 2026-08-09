from __future__ import annotations

from pathlib import Path

from pydantic import ValidationError

from engine.dressing.errors import (
    DressingPackNotAuthored,
    DressingRegistryError,
    UnknownWrapper,
)
from engine.dressing.models import DressingCatalog, DressingPack, DressingRegistry

_REPO_ROOT = Path(__file__).resolve().parents[2]
_REGISTRY_PATH = _REPO_ROOT / "config" / "dressing_registry.json"


def declared_wrapper_ids(arc_id: str) -> tuple[str, ...]:
    return _load_catalog_for_arc(arc_id).declared_wrapper_ids


def load_dressing_pack(arc_id: str, wrapper_id: str) -> DressingPack:
    catalog = _load_catalog_for_arc(arc_id)
    if wrapper_id not in catalog.wrappers:
        raise UnknownWrapper(f"unknown wrapper id: {wrapper_id}")
    pack = catalog.wrappers[wrapper_id]
    if not pack.authored:
        raise DressingPackNotAuthored(
            f"dressing pack not authored for wrapper: {wrapper_id}"
        )
    return pack


def _load_catalog_for_arc(arc_id: str) -> DressingCatalog:
    pack_path = _resolve_pack_path(arc_id, _REGISTRY_PATH)
    return _load_catalog(pack_path)


def _resolve_pack_path(arc_id: str, registry_path: Path) -> Path:
    registry = _load_registry(registry_path)
    for registration in registry.registrations:
        if arc_id.startswith(registration.arc_id_prefix):
            return _resolve_repo_relative_path(
                registry_path.parent.parent, registration.pack_path
            )
    raise DressingRegistryError(
        f"no dressing registration found for arc_id={arc_id!r} in {registry_path}"
    )


def _load_registry(registry_path: Path) -> DressingRegistry:
    return _load_model(
        registry_path,
        DressingRegistry,
        missing_message="dressing registry missing",
        invalid_message="invalid dressing registry",
    )


def _load_catalog(pack_path: Path) -> DressingCatalog:
    return _load_model(
        pack_path,
        DressingCatalog,
        missing_message="dressing pack missing",
        invalid_message="invalid dressing pack",
    )


def _load_model(
    path: Path, model_type: type, missing_message: str, invalid_message: str
):
    if not path.is_file():
        raise DressingRegistryError(f"{missing_message}: {path}")
    try:
        return model_type.model_validate_json(path.read_text(encoding="utf-8"))
    except (OSError, ValidationError, ValueError) as exc:
        raise DressingRegistryError(f"{invalid_message} {path}: {exc}") from exc


def _resolve_repo_relative_path(repo_root: Path, relative_path: str) -> Path:
    resolved = (repo_root / relative_path).resolve()
    if not resolved.is_relative_to(repo_root):
        raise DressingRegistryError(
            f"dressing path escapes repository root: {relative_path}"
        )
    return resolved
