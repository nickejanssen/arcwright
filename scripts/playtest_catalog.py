"""Load and validate the manifest for published playtest artifacts."""

import json
import re
from pathlib import Path, PurePosixPath
from typing import Any

_ENTRY_FIELDS = (
    "id",
    "game",
    "version",
    "title",
    "summary",
    "status",
    "route",
    "source_dir",
    "instrument_id",
    "instrument_version",
    "published",
)
_STATUSES = {"current", "archived", "draft"}
_SEMVER_LIKE = re.compile(r"^\d+\.\d+(?:\.\d+)?(?:-[0-9A-Za-z.-]+)?$")


def load_catalog(path: Path) -> dict:
    """Read a JSON catalog without modifying the catalog or its artifacts."""

    with path.open(encoding="utf-8") as stream:
        catalog = json.load(stream)
    if not isinstance(catalog, dict):
        raise ValueError("catalog root must be a JSON object")
    return catalog


def _path_within(root: Path, candidate: Path) -> bool:
    try:
        root_resolved = root.resolve()
        candidate_resolved = candidate.resolve(strict=False)
    except OSError:
        return False
    return (
        root_resolved == candidate_resolved
        or root_resolved in candidate_resolved.parents
    )


def _safe_route(value: Any, repo_root: Path) -> bool:
    if not isinstance(value, str) or not value.startswith("/"):
        return False
    if value.startswith("//") or value.startswith("\\\\"):
        return False
    if "\\" in value or "?" in value or "#" in value or ":" in value:
        return False
    path = Path(value.lstrip("/"))
    if path.is_absolute() or path.drive or path.anchor:
        return False
    parts = PurePosixPath(value).parts
    if ".." in parts:
        return False
    return _path_within(repo_root, repo_root / path)


def _safe_source(value: Any, repo_root: Path) -> bool:
    if not isinstance(value, str) or not value:
        return False
    if value.startswith("//") or value.startswith("\\\\") or "\\" in value:
        return False
    path = Path(value)
    if path.is_absolute() or path.drive or path.anchor:
        return False
    if ".." in PurePosixPath(value).parts:
        return False
    return _path_within(repo_root, repo_root / path)


def validate_catalog(catalog: dict, repo_root: Path) -> list[str]:
    """Return deterministic, actionable validation errors for *catalog*."""

    if not isinstance(catalog, dict):
        return ["catalog root must be a JSON object"]

    errors: list[str] = []
    if catalog.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if catalog.get("generated_at_policy") != "build-time":
        errors.append("generated_at_policy must be 'build-time'")
    declared_current = catalog.get("current_tests")
    if not isinstance(declared_current, dict):
        errors.append("current_tests must be an object")
        declared_current = {}
    entries = catalog.get("entries")
    if not isinstance(entries, list):
        return ["catalog entries must be a list"]

    seen_ids: dict[str, int] = {}
    seen_routes: dict[str, int] = {}
    current_games: dict[str, int] = {}
    for index, item in enumerate(entries):
        label = f"entries[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label} must be an object")
            continue
        missing = [field for field in _ENTRY_FIELDS if field not in item]
        if missing:
            errors.append(f"{label} missing required fields: {', '.join(missing)}")

        entry_id = item.get("id")
        if isinstance(entry_id, str):
            if entry_id in seen_ids:
                errors.append(
                    f"{label} duplicate id '{entry_id}' (already in entries[{seen_ids[entry_id]}])"
                )
            else:
                seen_ids[entry_id] = index

        game = item.get("game")
        if not isinstance(game, str) or not game:
            errors.append(f"{label} game must be a non-empty string")

        for field in ("version", "instrument_version"):
            value = item.get(field)
            if not isinstance(value, str) or not _SEMVER_LIKE.fullmatch(value):
                errors.append(f"{label} {field} must be semver-like (for example 2.2)")

        status = item.get("status")
        if status not in _STATUSES:
            errors.append(
                f"{label} status must be one of: {', '.join(sorted(_STATUSES))}"
            )

        route = item.get("route")
        if not _safe_route(route, repo_root):
            errors.append(f"{label} unsafe route '{route}'")
        elif route in seen_routes:
            errors.append(
                f"{label} duplicate route '{route}' (already in entries[{seen_routes[route]}])"
            )
        else:
            seen_routes[route] = index

        source_dir = item.get("source_dir")
        if not _safe_source(source_dir, repo_root):
            errors.append(f"{label} unsafe source_dir '{source_dir}'")
        elif not (repo_root / Path(source_dir)).is_dir():
            errors.append(f"{label} source directory does not exist: {source_dir}")

        if status == "current" and isinstance(game, str):
            if game in current_games:
                errors.append(
                    f"more than one current entry for game '{game}' "
                    f"(entries[{current_games[game]}] and entries[{index}])"
                )
            else:
                current_games[game] = index

    by_id = {item.get("id"): item for item in entries if isinstance(item, dict)}
    for game, entry_id in declared_current.items():
        if not isinstance(game, str) or not isinstance(entry_id, str):
            errors.append("current_tests keys and values must be strings")
            continue
        referenced = by_id.get(entry_id)
        if referenced is None:
            errors.append(f"current_tests['{game}'] references unknown id '{entry_id}'")
        elif referenced.get("game") != game:
            errors.append(
                f"current_tests['{game}'] references id '{entry_id}' for game "
                f"'{referenced.get('game')}'"
            )
        elif referenced.get("status") != "current":
            errors.append(
                f"current_tests['{game}'] must reference a current entry, "
                f"but '{entry_id}' is {referenced.get('status')!r}"
            )

    declared_ids = set(declared_current.values())
    for index, item in enumerate(entries):
        if isinstance(item, dict) and item.get("status") == "current":
            if item.get("id") not in declared_ids:
                errors.append(
                    f"entries[{index}] current entry '{item.get('id')}' is not declared in current_tests"
                )
    return errors


def current_tests(catalog: dict) -> list[dict]:
    """Resolve declared current entries in current_tests mapping order."""

    entries = catalog.get("entries", [])
    if not isinstance(entries, list):
        return []
    by_id = {entry.get("id"): entry for entry in entries if isinstance(entry, dict)}
    declared = catalog.get("current_tests", {})
    if not isinstance(declared, dict):
        return []
    return [
        by_id[entry_id]
        for entry_id in declared.values()
        if isinstance(entry_id, str) and entry_id in by_id
    ]


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Validate a playtest catalog")
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    loaded = load_catalog(args.path)
    problems = validate_catalog(loaded, args.path.parent.parent)
    if problems:
        for problem in problems:
            print(f"ERROR: {problem}")
        raise SystemExit(1)
    print(f"OK: {len(loaded['entries'])} catalog entries")
