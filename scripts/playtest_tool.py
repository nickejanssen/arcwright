"""Safe Steward CLI for Arcwright Playtest Lab artifacts."""

from __future__ import annotations

import argparse
import json
import re
import sys
from copy import deepcopy
from pathlib import Path, PurePosixPath
from typing import Any, Sequence

if __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.build_playtest_site import build_site
from scripts.playtest_catalog import load_catalog, validate_catalog

SUCCESS = 0
OPERATIONAL_FAILURE = 1
INVALID_INPUT = 2

_SECRET_MARKERS = (
    "api_key",
    "apikey",
    "secret",
    "password",
    "token=",
    "bearer ",
    "sk-",
    "-----begin",
)
_NEUTRAL_SUMMARIES = {
    "Metadata-only draft scaffold.",
    "Research scaffold awaiting approved fixture content.",
    "Non-canon research scaffold awaiting approved fixture content.",
}
_PAPER_TEST_ID = re.compile(r"(?:^|-)paper-test-(\d+)(?:-|$)")


class PlaytestToolError(Exception):
    """Base error with a stable CLI exit code."""

    exit_code = OPERATIONAL_FAILURE


class InvalidInputError(PlaytestToolError):
    """User input is invalid and should return exit code 2."""

    exit_code = INVALID_INPUT


class OperationalError(PlaytestToolError):
    """Repository or filesystem state blocked the operation."""

    exit_code = OPERATIONAL_FAILURE


class PlaytestArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise InvalidInputError(message)


def _catalog_path(args: argparse.Namespace) -> Path:
    path = args.catalog
    return path if path.is_absolute() else args.repo_root / path


def _load_catalog(args: argparse.Namespace) -> dict[str, Any]:
    try:
        return load_catalog(_catalog_path(args))
    except OSError as exc:
        raise OperationalError(f"could not read catalog: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise InvalidInputError(f"catalog is not valid JSON: {exc}") from exc
    except ValueError as exc:
        raise InvalidInputError(str(exc)) from exc


def _write_catalog(args: argparse.Namespace, catalog: dict[str, Any]) -> None:
    path = _catalog_path(args)
    try:
        path.write_text(
            json.dumps(catalog, indent=2, sort_keys=False) + "\n",
            encoding="utf-8",
        )
    except OSError as exc:
        raise OperationalError(f"could not write catalog: {exc}") from exc


def _safe_relative_path(value: str) -> bool:
    if "\\" in value:
        return False
    path = PurePosixPath(value)
    return bool(value) and not path.is_absolute() and ".." not in path.parts


def _safe_route(value: str) -> bool:
    if not value.startswith("/") or "\\" in value:
        return False
    if "?" in value or "#" in value or "//" in value:
        return False
    return ".." not in PurePosixPath(value).parts


def _safe_playtests_source(value: str) -> bool:
    path = PurePosixPath(value)
    return (
        _safe_relative_path(value)
        and len(path.parts) >= 2
        and path.parts[0] == "playtests"
    )


def _reject_secret_like_metadata(values: Sequence[str | None]) -> None:
    for value in values:
        if value is None:
            continue
        lowered = value.lower()
        if any(marker in lowered for marker in _SECRET_MARKERS):
            raise InvalidInputError("metadata contains a secret-like value")


def _display_game(value: str) -> str:
    return " ".join(part.capitalize() for part in value.replace("_", "-").split("-"))


def _neutral_titles(entry_id: str, game: str, version: str) -> set[str]:
    display_game = _display_game(game)
    titles = {
        f"{display_game} Playtest v{version}",
        f"{display_game} Test v{version}",
    }
    match = _PAPER_TEST_ID.search(entry_id)
    if match:
        number = str(int(match.group(1)))
        titles.add(f"{display_game} Paper Test #{number} v{version}")
    return titles


def _reject_creative_metadata(args: argparse.Namespace) -> None:
    if args.title not in _neutral_titles(args.id, args.game, args.version):
        raise InvalidInputError(
            "creative content is not accepted by the Steward CLI; "
            "use a neutral title derived from game, test type, and version"
        )
    if args.summary not in _NEUTRAL_SUMMARIES:
        raise InvalidInputError(
            "creative content is not accepted by the Steward CLI; "
            "use an approved neutral scaffold summary"
        )


def _validate_full_catalog(catalog: dict[str, Any], repo_root: Path) -> list[str]:
    return validate_catalog(catalog, repo_root)


def _ensure_valid_catalog(catalog: dict[str, Any], repo_root: Path) -> None:
    problems = _validate_full_catalog(catalog, repo_root)
    if problems:
        raise InvalidInputError("; ".join(problems))


def _entry_summaries(catalog: dict[str, Any]) -> list[dict[str, Any]]:
    entries = catalog.get("entries", [])
    if not isinstance(entries, list):
        raise InvalidInputError("catalog entries must be a list")
    return [
        {
            "id": entry.get("id"),
            "game": entry.get("game"),
            "version": entry.get("version"),
            "status": entry.get("status"),
            "route": entry.get("route"),
            "source_dir": entry.get("source_dir"),
        }
        for entry in entries
        if isinstance(entry, dict)
    ]


def _emit(args: argparse.Namespace, payload: dict[str, Any], text: str) -> None:
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(text)


def _command_list(args: argparse.Namespace) -> int:
    catalog = _load_catalog(args)
    entries = _entry_summaries(catalog)
    if args.json:
        print(json.dumps({"ok": True, "entries": entries}, indent=2, sort_keys=True))
        return SUCCESS
    if not entries:
        print("No playtest entries.")
        return SUCCESS
    for entry in entries:
        print(
            f"{entry['id']} {entry['status']} {entry['version']} "
            f"{entry['route']} {entry['source_dir']}"
        )
    return SUCCESS


def _command_validate(args: argparse.Namespace) -> int:
    catalog = _load_catalog(args)
    problems = _validate_full_catalog(catalog, args.repo_root)
    if problems:
        _emit(
            args,
            {"ok": False, "errors": problems},
            "\n".join(f"ERROR: {problem}" for problem in problems),
        )
        return INVALID_INPUT
    _emit(args, {"ok": True, "errors": []}, "OK: catalog is valid")
    return SUCCESS


def _proposed_entry(args: argparse.Namespace) -> dict[str, Any]:
    metadata_values = [
        args.id,
        args.game,
        args.version,
        args.title,
        args.summary,
        args.route,
        args.source_dir,
        args.instrument_id,
        args.instrument_version,
        args.published,
    ]
    _reject_secret_like_metadata(metadata_values)
    _reject_creative_metadata(args)
    if not _safe_route(args.route):
        raise InvalidInputError(f"unsafe route '{args.route}'")
    if not _safe_playtests_source(args.source_dir):
        raise InvalidInputError(f"unsafe source_dir '{args.source_dir}'")
    return {
        "id": args.id,
        "game": args.game,
        "version": args.version,
        "title": args.title,
        "summary": args.summary,
        "status": "draft",
        "route": args.route,
        "source_dir": args.source_dir,
        "instrument_id": args.instrument_id,
        "instrument_version": args.instrument_version,
        "published": args.published,
    }


def _find_entry(entries: list[dict[str, Any]], entry_id: str) -> dict[str, Any] | None:
    for entry in entries:
        if entry.get("id") == entry_id:
            return entry
    return None


def _command_new(args: argparse.Namespace) -> int:
    catalog = _load_catalog(args)
    entries = catalog.get("entries")
    if not isinstance(entries, list):
        raise InvalidInputError("catalog entries must be a list")
    if _find_entry(entries, args.id) is not None:
        raise InvalidInputError(f"id already exists: {args.id}")
    if any(
        entry.get("game") == args.game and entry.get("version") == args.version
        for entry in entries
        if isinstance(entry, dict)
    ):
        raise InvalidInputError(
            f"version already exists for game '{args.game}': {args.version}"
        )

    entry = _proposed_entry(args)
    source_path = args.repo_root / Path(args.source_dir)
    source_exists = source_path.exists()
    if args.use_existing_source:
        if not source_exists or not source_path.is_dir():
            raise InvalidInputError(
                f"existing source directory does not exist: {args.source_dir}"
            )
    else:
        if source_exists:
            raise InvalidInputError(f"source directory already exists: {args.source_dir}")
        if not source_path.parent.is_dir():
            raise InvalidInputError(
                f"source parent directory does not exist: {source_path.parent}"
            )

    candidate = deepcopy(catalog)
    candidate_entries = candidate.setdefault("entries", [])
    if not isinstance(candidate_entries, list):
        raise InvalidInputError("catalog entries must be a list")
    candidate_entries.append(entry)

    if args.use_existing_source:
        _ensure_valid_catalog(candidate, args.repo_root)
        _write_catalog(args, candidate)
        _emit(
            args,
            {"ok": True, "entry": entry},
            f"Registered existing fixture: {args.id}",
        )
        return SUCCESS

    source_path.mkdir()
    readme_path = source_path / "README.md"
    readme_path.write_text(
        "\n".join(
            [
                f"# {args.title}",
                "",
                "Status: draft scaffold.",
                "",
                "This directory is a metadata-only scaffold for a non-canon",
                "playtest artifact. Add fixture content only after explicit",
                "founder approval and keep the catalog version immutable once",
                "published.",
                "",
                f"- ID: {args.id}",
                f"- Game: {args.game}",
                f"- Version: {args.version}",
                f"- Instrument ID: {args.instrument_id}",
                f"- Instrument version: {args.instrument_version}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    try:
        _ensure_valid_catalog(candidate, args.repo_root)
        _write_catalog(args, candidate)
    except Exception:
        readme_path.unlink(missing_ok=True)
        source_path.rmdir()
        raise

    _emit(args, {"ok": True, "entry": entry}, f"Created scaffold: {args.id}")
    return SUCCESS


def _command_archive(args: argparse.Namespace) -> int:
    catalog = _load_catalog(args)
    entries = catalog.get("entries")
    if not isinstance(entries, list):
        raise InvalidInputError("catalog entries must be a list")
    entry = _find_entry(entries, args.id)
    if entry is None:
        raise InvalidInputError(f"unknown playtest id: {args.id}")
    if entry.get("status") == "archived":
        raise InvalidInputError(f"entry already archived: {args.id}")
    current_tests = catalog.get("current_tests")
    if (
        entry.get("status") == "current"
        and isinstance(current_tests, dict)
        and current_tests.get(entry.get("game")) == args.id
    ):
        raise InvalidInputError(
            f"archiving '{args.id}' would leave the catalog without a current entry "
            f"for game '{entry.get('game')}'"
        )

    entry["status"] = "archived"
    entry["archived"] = args.archived_on
    if args.reason:
        _reject_secret_like_metadata([args.reason])
        entry["archive_reason"] = args.reason
    if isinstance(current_tests, dict):
        for game, current_id in list(current_tests.items()):
            if current_id == args.id:
                del current_tests[game]

    _ensure_valid_catalog(catalog, args.repo_root)
    _write_catalog(args, catalog)
    _emit(args, {"ok": True, "entry": entry}, f"Archived entry: {args.id}")
    return SUCCESS


def _command_build(args: argparse.Namespace) -> int:
    try:
        build_site(args.catalog, args.templates, args.output, args.repo_root)
    except ValueError as exc:
        raise InvalidInputError(str(exc)) from exc
    except OSError as exc:
        raise OperationalError(str(exc)) from exc
    _emit(
        args, {"ok": True, "output": str(args.output)}, f"Built site at {args.output}"
    )
    return SUCCESS


def _build_parser() -> argparse.ArgumentParser:
    parser = PlaytestArgumentParser(
        description=(
            "Manage Arcwright Playtest Lab metadata without mutating published "
            "artifacts or adding creative content."
        )
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--catalog", type=Path, default=Path("playtests/catalog.json"))
    parser.add_argument("--json", action="store_true")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List catalog entries")
    list_parser.set_defaults(handler=_command_list)

    validate_parser = subparsers.add_parser(
        "validate", help="Validate the catalog without changing files"
    )
    validate_parser.set_defaults(handler=_command_validate)

    new_parser = subparsers.add_parser(
        "new", help="Create or register a draft playtest"
    )
    for name in (
        "id",
        "game",
        "version",
        "title",
        "summary",
        "route",
        "source-dir",
        "instrument-id",
        "instrument-version",
    ):
        new_parser.add_argument(f"--{name}", required=True)
    new_parser.add_argument("--published")
    new_parser.add_argument(
        "--use-existing-source",
        action="store_true",
        help="register an already-approved existing fixture without modifying its files",
    )
    new_parser.set_defaults(handler=_command_new)

    archive_parser = subparsers.add_parser(
        "archive", help="Archive an exact catalog ID without moving artifacts"
    )
    archive_parser.add_argument("id")
    archive_parser.add_argument("--archived-on", required=True)
    archive_parser.add_argument("--reason")
    archive_parser.set_defaults(handler=_command_archive)

    build_parser = subparsers.add_parser(
        "build", help="Delegate to the deterministic static site builder"
    )
    build_parser.add_argument("--templates", type=Path, default=Path("playtests/site"))
    build_parser.add_argument("--output", type=Path, default=Path("_site"))
    build_parser.set_defaults(handler=_command_build)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    try:
        args = parser.parse_args(argv)
        args.repo_root = args.repo_root.resolve()
        return args.handler(args)
    except PlaytestToolError as exc:
        wants_json = "--json" in (argv or sys.argv[1:])
        if wants_json:
            print(json.dumps({"ok": False, "errors": [str(exc)]}, indent=2))
        else:
            print(f"ERROR: {exc}", file=sys.stderr)
        return exc.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
