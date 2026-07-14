"""Arc definition registry.

Maps arc ids to arc definition files through `config/arc_registry.json`, so
engine code never hardcodes any game's arc location. This mirrors the
routing-table pattern: deployment-specific wiring lives in `config/`, and
the engine stays game-agnostic.

Registry format:

    {
      "default_arc_id": "nightcap",
      "arcs": [
        {"id_prefix": "nightcap", "path": "nightcap/arc.json"}
      ]
    }

`id_prefix` matching (rather than exact ids) is deliberate: session rows
store versioned arc ids such as "nightcap-v1" that resolve to the same
definition file.  Paths are relative to the repository root.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from engine.arc.models import ArcDefinition

_REPO_ROOT = Path(__file__).resolve().parents[2]
ARC_REGISTRY_PATH = _REPO_ROOT / "config" / "arc_registry.json"


class ArcRegistryError(Exception):
    """Raised when the arc registry file is missing or malformed."""


@lru_cache(maxsize=1)
def _load_registry() -> dict:
    try:
        raw = json.loads(ARC_REGISTRY_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ArcRegistryError(
            f"Arc registry not found at {ARC_REGISTRY_PATH}"
        ) from exc
    if "arcs" not in raw or not isinstance(raw["arcs"], list):
        raise ArcRegistryError("Arc registry must contain an 'arcs' list")
    return raw


def resolve_arc_path(arc_id: str) -> Path | None:
    """Return the definition path registered for arc_id, or None if unknown."""
    for entry in _load_registry()["arcs"]:
        if arc_id.startswith(entry["id_prefix"]):
            return _REPO_ROOT / entry["path"]
    return None


def default_arc_path() -> Path:
    """Return the definition path for the deployment's default arc.

    Used by tooling (e.g. the headless harness) that needs an arc to run
    against when the caller does not specify one.
    """
    registry = _load_registry()
    default_id = registry.get("default_arc_id")
    if not default_id:
        raise ArcRegistryError("Arc registry does not define 'default_arc_id'")
    path = resolve_arc_path(default_id)
    if path is None:
        raise ArcRegistryError(
            f"default_arc_id {default_id!r} does not match any registry entry"
        )
    return path


@lru_cache(maxsize=8)
def _load_arc_definition_from_path(path: Path) -> ArcDefinition:
    return ArcDefinition.model_validate_json(path.read_text(encoding="utf-8"))


def load_arc_definition(arc_id: str) -> ArcDefinition | None:
    """Return the arc definition registered for arc_id, or None if unknown.

    Definitions are cached per path, so repeated session-service calls do
    not re-read or re-validate the JSON file.
    """
    path = resolve_arc_path(arc_id)
    if path is None:
        return None
    return _load_arc_definition_from_path(path)
