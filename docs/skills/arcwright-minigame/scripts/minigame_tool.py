#!/usr/bin/env python3
"""Authoring helper for Arcwright mini-game packages.

Two deterministic actions that every mini-game integration repeats:

  scaffold  Copy an experience's ``_template`` into a new ``<game_id>`` package
            and stamp the ``game_id`` / ``title`` so the package validates
            immediately.
  validate  Load one package, or a whole experience catalog, through the engine
            loader and report problems in plain language.

The engine is the single source of truth for the schema. This script never
re-encodes field rules: ``scaffold`` copies the template and substitutes ids,
and ``validate`` calls ``engine.mini_games`` directly. Run it from anywhere; it
locates the repo root from its own path.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

# docs/skills/arcwright-minigame/scripts/minigame_tool.py -> repo root is parents[4]
REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def _fail(message: str) -> int:
    print(f"ERROR: {message}")
    return 1


def _write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def scaffold(experience: str, game_id: str, title: str | None) -> int:
    if not SLUG_PATTERN.match(game_id):
        return _fail(f"game_id must be lowercase kebab-case: {game_id!r}")

    base = REPO_ROOT / experience / "mini_games"
    template = base / "_template"
    target = base / game_id

    if not template.is_dir():
        return _fail(
            f"no template at {template}. Confirm the experience has a "
            f"mini_games/_template/ directory."
        )
    if target.exists():
        return _fail(f"package already exists: {target}")

    shutil.copytree(template, target)

    resolved_title = title or game_id.replace("-", " ").title()

    manifest_path = target / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["game_id"] = game_id
    manifest["title"] = resolved_title
    _write_json(manifest_path, manifest)

    definition_path = target / manifest["definition_path"]
    definition = json.loads(definition_path.read_text(encoding="utf-8"))
    definition["game_id"] = game_id
    _write_json(definition_path, definition)

    print(f"Scaffolded {target}")
    print("Stamped game_id and title. Now edit the definition fields, then validate.")
    return validate(str(target))


def validate(path: str) -> int:
    try:
        # Imported here so a wrong working directory yields a friendly message.
        from engine.mini_games import (
            MiniGamePackageError,
            load_mini_game_catalog,
            load_mini_game_package,
        )
    except ImportError as exc:  # pragma: no cover - environment guard
        return _fail(
            f"could not import engine.mini_games ({exc}). Run from a checkout "
            f"with the engine package importable."
        )

    target = Path(path)
    if not target.is_absolute():
        target = (Path.cwd() / target).resolve()

    is_package = (target / "manifest.json").is_file()
    try:
        if is_package:
            loaded = load_mini_game_package(target)
            print(
                f"OK package: {loaded.manifest.game_id} "
                f"v{loaded.manifest.current_version} "
                f"({loaded.manifest.lifecycle.value})"
            )
        else:
            catalog = load_mini_game_catalog(target)
            print(f"OK catalog: {len(catalog)} package(s)")
            for game_id, loaded in sorted(catalog.items()):
                print(
                    f"  - {game_id} v{loaded.manifest.current_version} "
                    f"({loaded.manifest.lifecycle.value})"
                )
    except MiniGamePackageError as exc:
        return _fail(str(exc))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    scaffold_parser = sub.add_parser(
        "scaffold", help="create a new package from the template"
    )
    scaffold_parser.add_argument("--experience", default="nightcap")
    scaffold_parser.add_argument("--game-id", required=True)
    scaffold_parser.add_argument("--title", default=None)

    validate_parser = sub.add_parser("validate", help="validate a package or catalog")
    validate_parser.add_argument(
        "path", help="path to a package dir or a mini_games/ catalog dir"
    )
    validate_parser.add_argument(
        "--catalog",
        action="store_true",
        help="force catalog mode even if a manifest.json is present",
    )

    args = parser.parse_args(argv)

    if args.command == "scaffold":
        return scaffold(args.experience, args.game_id, args.title)
    if args.command == "validate":
        if args.catalog:
            # Re-point at the directory as a catalog by stripping any manifest detection.
            from engine.mini_games import (
                MiniGamePackageError,
                load_mini_game_catalog,
            )

            target = Path(args.path)
            if not target.is_absolute():
                target = (Path.cwd() / target).resolve()
            try:
                catalog = load_mini_game_catalog(target)
            except MiniGamePackageError as exc:
                return _fail(str(exc))
            print(f"OK catalog: {len(catalog)} package(s)")
            return 0
        return validate(args.path)
    return _fail(f"unknown command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
