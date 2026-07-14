"""Arc definition registry.

Maps arc ids to arc definition files. The engine itself has no knowledge of
any specific game: which arcs exist, and where their definition JSON lives,
is deployment configuration in ``config/arcs.json`` — the same pattern as
``config/routing_table.json`` for model routing. Adding a new game is a
config change, never an engine code change.

Registry file format::

    {
      "arcs": [
        {"id_prefix": "nightcap", "path": "nightcap/arc.json"}
      ]
    }

``id_prefix`` matches any ``arc_id`` that starts with the prefix (arc ids
carry version suffixes, e.g. ``nightcap-v1``). ``path`` is relative to the
repository root. Entries are matched in order; the first match wins.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.arc.models import ArcDefinition

_REPO_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_REGISTRY_PATH = _REPO_ROOT / "config" / "arcs.json"


class ArcRegistryError(Exception):
    """Raised when the arc registry config is missing or malformed."""


@lru_cache(maxsize=1)
def _registry_entries(
    registry_path: Path = DEFAULT_REGISTRY_PATH,
) -> tuple[tuple[str, Path], ...]:
    """Load and validate the registry file into (id_prefix, absolute_path) pairs."""
    try:
        raw = json.loads(registry_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ArcRegistryError(f"Arc registry not found: {registry_path}") from exc
    except json.JSONDecodeError as exc:
        raise ArcRegistryError(
            f"Arc registry is not valid JSON: {registry_path}"
        ) from exc

    arcs = raw.get("arcs")
    if not isinstance(arcs, list) or not arcs:
        raise ArcRegistryError(
            f"Arc registry must contain a non-empty 'arcs' list: {registry_path}"
        )

    entries: list[tuple[str, Path]] = []
    for entry in arcs:
        prefix = entry.get("id_prefix")
        rel_path = entry.get("path")
        if not prefix or not rel_path:
            raise ArcRegistryError(
                f"Each registry entry needs 'id_prefix' and 'path': {entry!r}"
            )
        entries.append((prefix, registry_path.parent.parent / rel_path))
    return tuple(entries)


def resolve_arc_path(arc_id: str) -> Path | None:
    """Return the arc definition path for ``arc_id``, or None if unregistered."""
    for prefix, path in _registry_entries():
        if arc_id.startswith(prefix):
            return path
    return None


@lru_cache(maxsize=8)
def _load_definition_from_path(arc_path: Path) -> "ArcDefinition":
    from engine.arc.models import ArcDefinition

    return ArcDefinition.model_validate_json(arc_path.read_text(encoding="utf-8"))


def load_arc_definition(arc_id: str) -> "ArcDefinition | None":
    """Load the arc definition registered for ``arc_id``.

    Returns None when no registry entry matches, so callers can decide
    whether an unknown arc is an error (session creation) or a no-op
    (advancing a session type the engine does not manage).
    """
    arc_path = resolve_arc_path(arc_id)
    if arc_path is None:
        return None
    return _load_definition_from_path(arc_path)


def default_arc_path() -> Path:
    """Return the first registered arc's definition path.

    Used as the default arc for tooling (e.g. the headless harness) when no
    arc is specified explicitly.
    """
    return _registry_entries()[0][1]
