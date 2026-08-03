#!/usr/bin/env python3
"""Authoring helper for Arcwright mini-game packages.

Deterministic package actions:

  scaffold  Copy an experience's ``_template`` into a new ``<game_id>`` package
            and stamp the ``game_id`` / ``title`` so the package validates
            immediately.
  validate  Load one package, or a whole experience catalog, through the engine
            loader and report problems in plain language.

Guided browser onboarding actions:

  onboard-browser  Import and analyze a browser source in a private workspace.
  resume           Continue one resumable onboarding session.
  status           Display one onboarding session without changing it.
  playtest         Record local preview-only playtest evidence.

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
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import UUID

# docs/skills/arcwright-minigame/scripts/minigame_tool.py -> repo root is parents[4]
REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ANSWER_SCHEMA_VERSION = "1.0"
GENERATION_CATEGORIES = frozenset(
    {"code", "art", "animation", "audio", "copy", "configuration"}
)
GENERATION_PERMISSION_PROMPT = (
    "Which categories may Arcwright generate: code, art, animation, audio, "
    "copy, or configuration? Use 'none' to deny generation."
)
STATE_LABELS = {
    "imported": "Imported",
    "reusable": "Reusable",
    "playtest_ready": "Playtest-ready",
    "production_ready": "Production-ready",
}
STATE_EXPLANATIONS = {
    "imported": (
        "The browser source is preserved in a private workspace and its "
        "observable behavior has been analyzed without changing the original."
    ),
    "reusable": "A destination-neutral package has supporting readiness evidence.",
    "playtest_ready": (
        "A destination adaptation has passed automated preflight and is locally testable."
    ),
    "production_ready": (
        "All applicable automated and human production gates have recorded evidence."
    ),
}


class GuidedCommandError(ValueError):
    """A user-correctable guided-command failure."""


def _fail(message: str) -> int:
    print(f"ERROR: {message}")
    return 1


def _guided_fail(message: str) -> int:
    print(f"ERROR: {message}", file=sys.stderr)
    return 2


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


def _authoring_components():
    from engine.mini_games.authoring import (
        BrowserImportSource,
        GenerationPermissionReceipt,
        LocalAuthoringWorkspace,
        MiniGameOnboardingRequest,
        MiniGameOnboardingService,
    )

    workspace = LocalAuthoringWorkspace()
    service = MiniGameOnboardingService(workspace=workspace)
    return (
        BrowserImportSource,
        GenerationPermissionReceipt,
        MiniGameOnboardingRequest,
        service,
        workspace,
    )


def _adaptation_alternatives(destination_game_id: str | None) -> list[dict[str, Any]]:
    if destination_game_id is None:
        return []
    return [
        {
            "id": "preserve-source-flow",
            "recommended": True,
            "summary": (
                "Preserve the source interaction and adapt only participation, "
                "presentation, and result mapping for the destination."
            ),
        },
        {
            "id": "individual-turns",
            "recommended": False,
            "summary": (
                "Run private individual turns, then publish a destination-owned "
                "shared summary."
            ),
        },
        {
            "id": "shared-group-round",
            "recommended": False,
            "summary": (
                "Run one shared group round while the browser remains preview-only "
                "and non-authoritative."
            ),
        },
    ]


def _session_payload(session) -> dict[str, Any]:
    analysis = session.analysis
    pending = (
        [
            confirmation.model_dump(mode="json")
            for confirmation in analysis.confirmations
            if confirmation.confirmed_value is None
        ]
        if analysis is not None
        else []
    )
    state_value = session.state.value
    readiness = session.readiness_report
    state_explanation = (
        readiness.state_explanation
        if readiness is not None
        else STATE_EXPLANATIONS[state_value]
    )
    blockers = list(readiness.blockers) if readiness is not None else []
    if readiness is None:
        blockers.extend(f"Confirmation required: {item['prompt']}" for item in pending)
        if session.permission_receipt is None:
            blockers.append("Generation permission has not been decided.")
        if session.proposed_package is None:
            blockers.append("No reusable package has been produced.")
        if (
            session.request.destination_game_id is not None
            and session.proposed_adaptation is None
        ):
            blockers.append("No destination adaptation has been produced.")

    if readiness is not None:
        next_action = readiness.next_action
    elif pending:
        next_action = f"Answer: {pending[0]['prompt']}"
    elif session.permission_receipt is None:
        next_action = "Decide which generation categories Arcwright may use."
    elif session.proposed_package is None:
        if session.permission_receipt.approved_categories:
            next_action = "Generate the source-preserving Draft package."
        else:
            next_action = "Create the Draft package without generated changes."
    elif session.proposed_adaptation is None:
        next_action = "Generate the approved destination adaptation."
    else:
        next_action = "Run the local playtest preflight."

    return {
        "schema_version": session.schema_version,
        "session_id": str(session.session_id),
        "revision": session.revision,
        "hosting_preference": session.request.hosting_preference,
        "destination_game_id": session.request.destination_game_id,
        "recommended_path": (
            analysis.recommended_path
            if analysis is not None
            else (
                "destination_first"
                if session.request.destination_game_id is not None
                else "reusable_first"
            )
        ),
        "current_state": state_value,
        "state_label": STATE_LABELS[state_value],
        "state_explanation": state_explanation,
        "blockers": blockers,
        "next_action": next_action,
        "pending_questions": pending,
        "permission_prompt": GENERATION_PERMISSION_PROMPT,
        "adaptation_alternatives": _adaptation_alternatives(
            session.request.destination_game_id
        ),
        "generation_permission": (
            session.permission_receipt.model_dump(mode="json")
            if session.permission_receipt is not None
            else None
        ),
        "original_source_unchanged": session.original_source_unchanged,
        "evidence": list(analysis.evidence) if analysis is not None else [],
        "uncertainty": list(analysis.uncertainty) if analysis is not None else [],
    }


def _print_session(session, *, as_json: bool) -> None:
    payload = _session_payload(session)
    if as_json:
        print(json.dumps(payload, indent=2))
        return

    print(f"Session: {payload['session_id']}")
    print(f"State: {payload['state_label']}")
    print(f"Why: {payload['state_explanation']}")
    print("Blockers:")
    if payload["blockers"]:
        for blocker in payload["blockers"]:
            print(f"  - {blocker}")
    else:
        print("  - None")
    print(f"Next action: {payload['next_action'] or 'None'}")
    if payload["pending_questions"]:
        print(f"Question: {payload['pending_questions'][0]['prompt']}")
    print(f"Permission: {payload['permission_prompt']}")
    if payload["adaptation_alternatives"]:
        print("Adaptation alternatives:")
        for alternative in payload["adaptation_alternatives"]:
            marker = "recommended" if alternative["recommended"] else "alternative"
            print(f"  - {alternative['id']} ({marker}): {alternative['summary']}")


def _read_answers(path: str | None) -> dict[str, Any]:
    if path is None:
        raise GuidedCommandError("generation permission required")
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise GuidedCommandError(f"could not read answer file: {exc}") from exc
    if not isinstance(data, dict):
        raise GuidedCommandError("answer file must contain a JSON object")
    if data.get("schema_version") != ANSWER_SCHEMA_VERSION:
        raise GuidedCommandError(
            f"answer file schema_version must be {ANSWER_SCHEMA_VERSION!r}"
        )
    return data


def _validated_answer_values(
    session,
    data: dict[str, Any],
) -> tuple[dict[str, str], dict[str, Any]]:
    permission = data.get("generation_permission")
    if not isinstance(permission, dict):
        raise GuidedCommandError("generation permission required")

    if session.analysis is None:
        raise GuidedCommandError("onboarding analysis is missing")
    confirmations = data.get("confirmations")
    if not isinstance(confirmations, dict):
        confirmations = {}
    required_keys = {item.key for item in session.analysis.confirmations}
    missing = sorted(
        key
        for key in required_keys
        if not isinstance(confirmations.get(key), str) or not confirmations[key].strip()
    )
    if missing:
        raise GuidedCommandError(
            "high-impact confirmations required: " + ", ".join(missing)
        )

    categories = permission.get("approved_categories")
    if not isinstance(categories, list) or any(
        not isinstance(category, str) or category not in GENERATION_CATEGORIES
        for category in categories
    ):
        raise GuidedCommandError(
            "generation permission approved_categories must use the supported categories"
        )
    approved_by = permission.get("approved_by")
    if not isinstance(approved_by, str) or not approved_by.strip():
        raise GuidedCommandError("generation permission approved_by is required")
    denied_asset_refs = permission.get("denied_asset_refs", [])
    if not isinstance(denied_asset_refs, list) or any(
        not isinstance(item, str) for item in denied_asset_refs
    ):
        raise GuidedCommandError(
            "generation permission denied_asset_refs must be strings"
        )
    remember_for_project = permission.get("remember_for_project", False)
    if not isinstance(remember_for_project, bool):
        raise GuidedCommandError(
            "generation permission remember_for_project must be true or false"
        )
    return (
        {key: confirmations[key].strip() for key in required_keys},
        {
            "approved_categories": tuple(categories),
            "denied_asset_refs": tuple(denied_asset_refs),
            "remember_for_project": remember_for_project,
            "approved_by": approved_by.strip(),
        },
    )


def _apply_answers(session, data: dict[str, Any], workspace_root: Path, workspace):
    _, GenerationPermissionReceipt, _, _, _ = _authoring_components()
    confirmation_values, permission_values = _validated_answer_values(session, data)
    destination = session.request.destination_game_id
    if destination is None:
        raise GuidedCommandError(
            "destination is required before recording generation permission"
        )
    confirmed = tuple(
        item.model_copy(update={"confirmed_value": confirmation_values[item.key]})
        for item in session.analysis.confirmations
    )
    analysis = session.analysis.model_copy(update={"confirmations": confirmed})
    receipt = GenerationPermissionReceipt(
        receipt_id=f"permission-{session.session_id}",
        destination_game_id=destination,
        adaptation_id=f"{destination}-draft",
        approved_at=datetime.now(timezone.utc),
        **permission_values,
    )
    updated = session.model_copy(
        update={
            "revision": session.revision + 1,
            "analysis": analysis,
            "permission_receipt": receipt,
        }
    )
    workspace.save(updated, workspace_root)
    return updated


def _save_confirmation(session, key: str, value: str, workspace_root: Path, workspace):
    confirmations = tuple(
        item.model_copy(update={"confirmed_value": value}) if item.key == key else item
        for item in session.analysis.confirmations
    )
    updated = session.model_copy(
        update={
            "revision": session.revision + 1,
            "analysis": session.analysis.model_copy(
                update={"confirmations": confirmations}
            ),
        }
    )
    workspace.save(updated, workspace_root)
    return updated


def _run_interactive(session, workspace_root: Path, workspace):
    if session.analysis is None:
        raise GuidedCommandError("onboarding analysis is missing")
    for confirmation in session.analysis.confirmations:
        if confirmation.confirmed_value is not None:
            continue
        try:
            answer = input(f"{confirmation.prompt}\n> ").strip()
        except EOFError:
            return session
        if not answer:
            raise GuidedCommandError(f"answer required for {confirmation.key}")
        session = _save_confirmation(
            session,
            confirmation.key,
            answer,
            workspace_root,
            workspace,
        )

    if session.permission_receipt is not None:
        return session
    destination = session.request.destination_game_id
    if destination is None:
        return session
    try:
        raw_categories = input(f"{GENERATION_PERMISSION_PROMPT}\n> ").strip()
    except EOFError:
        return session
    categories = (
        []
        if raw_categories.lower() == "none"
        else [item.strip() for item in raw_categories.split(",") if item.strip()]
    )
    data = {
        "schema_version": ANSWER_SCHEMA_VERSION,
        "confirmations": {
            item.key: item.confirmed_value for item in session.analysis.confirmations
        },
        "generation_permission": {
            "approved_categories": categories,
            "approved_by": "interactive-user",
        },
    }
    return _apply_answers(session, data, workspace_root, workspace)


def onboard_browser(args: argparse.Namespace) -> int:
    (
        BrowserImportSource,
        _,
        MiniGameOnboardingRequest,
        service,
        workspace,
    ) = _authoring_components()
    workspace_root = Path(args.workspace).resolve()
    session = None
    try:
        source = Path(args.source).resolve(strict=True)
        request = MiniGameOnboardingRequest(
            source=BrowserImportSource(
                source_type="static_bundle",
                source_ref=str(source),
                source_access="source_and_build",
            ),
            destination_game_id=args.destination,
            hosting_preference=args.hosting,
            cohort=args.cohort,
        )
        session = service.start(request, workspace_root=workspace_root)
        analysis_source = workspace_root / session.private_source_ref
        analysis = service.analyze(
            source=analysis_source,
            destination_game_id=args.destination,
        )
        session = session.model_copy(
            update={"revision": session.revision + 1, "analysis": analysis}
        )
        workspace.save(session, workspace_root)
        if args.non_interactive:
            try:
                session = _apply_answers(
                    session,
                    _read_answers(args.answers),
                    workspace_root,
                    workspace,
                )
            except GuidedCommandError as exc:
                _print_session(session, as_json=args.as_json)
                return _guided_fail(str(exc))
        elif not args.as_json:
            session = _run_interactive(session, workspace_root, workspace)
    except GuidedCommandError as exc:
        if session is not None:
            session = service.load(session.session_id, workspace_root=workspace_root)
            _print_session(session, as_json=args.as_json)
        return _guided_fail(str(exc))
    except (OSError, ValueError) as exc:
        return _guided_fail(str(exc))
    _print_session(session, as_json=args.as_json)
    return 0


def resume_onboarding(args: argparse.Namespace) -> int:
    *_, service, workspace = _authoring_components()
    workspace_root = Path(args.workspace).resolve()
    session = None
    try:
        session = service.load(UUID(args.session_id), workspace_root=workspace_root)
        if args.non_interactive:
            session = _apply_answers(
                session,
                _read_answers(args.answers),
                workspace_root,
                workspace,
            )
        elif not args.as_json:
            session = _run_interactive(session, workspace_root, workspace)
    except GuidedCommandError as exc:
        if session is not None:
            session = service.load(session.session_id, workspace_root=workspace_root)
            _print_session(session, as_json=args.as_json)
        return _guided_fail(str(exc))
    except (OSError, ValueError) as exc:
        return _guided_fail(str(exc))
    _print_session(session, as_json=args.as_json)
    return 0


def onboarding_status(args: argparse.Namespace) -> int:
    *_, service, _ = _authoring_components()
    try:
        session = service.load(
            UUID(args.session_id),
            workspace_root=Path(args.workspace).resolve(),
        )
    except (OSError, ValueError) as exc:
        return _guided_fail(str(exc))
    _print_session(session, as_json=args.as_json)
    return 0


def playtest(args: argparse.Namespace) -> int:
    script = REPO_ROOT / "nightcap-web" / "scripts" / "playtest-mini-game.mjs"
    cmd = [
        "node",
        str(script),
        "--session",
        args.session,
        "--scenario",
        args.scenario,
        "--players",
        str(args.players),
        "--surfaces",
        args.surfaces,
        "--out",
        args.out,
        "--serve-ms",
        str(args.serve_ms),
    ]
    if args.adaptation:
        cmd.extend(["--adaptation", args.adaptation])
    if args.as_json:
        cmd.append("--json")
    completed = subprocess.run(
        cmd,
        cwd=REPO_ROOT / "nightcap-web",
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.stdout:
        print(completed.stdout, end="")
    if completed.stderr:
        print(completed.stderr, end="", file=sys.stderr)
    return completed.returncode


def _add_guided_output_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--json", action="store_true", dest="as_json")


def _add_guided_input_arguments(parser: argparse.ArgumentParser) -> None:
    _add_guided_output_arguments(parser)
    parser.add_argument("--non-interactive", action="store_true")
    parser.add_argument(
        "--answers",
        help="path to a versioned JSON answer file for non-interactive mode",
    )


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

    onboard_parser = sub.add_parser(
        "onboard-browser",
        help="import and analyze one browser mini-game source",
    )
    onboard_parser.add_argument("source", help="path to a static browser bundle")
    onboard_parser.add_argument("--destination", default=None)
    onboard_parser.add_argument(
        "--hosting", choices=("managed", "external"), default="managed"
    )
    onboard_parser.add_argument(
        "--cohort", choices=("first_time", "returning"), default="first_time"
    )
    _add_guided_input_arguments(onboard_parser)

    resume_parser = sub.add_parser("resume", help="resume an onboarding session")
    resume_parser.add_argument("session_id")
    _add_guided_input_arguments(resume_parser)

    status_parser = sub.add_parser("status", help="show onboarding session status")
    status_parser.add_argument("session_id")
    _add_guided_output_arguments(status_parser)

    playtest_parser = sub.add_parser(
        "playtest",
        help="record local preview-only playtest evidence",
    )
    playtest_parser.add_argument("--session", required=True)
    playtest_parser.add_argument("--scenario", default="happy-path")
    playtest_parser.add_argument("--players", type=int, default=4)
    playtest_parser.add_argument(
        "--surfaces",
        default="phone,shared_display,host",
        help="comma-separated surfaces to include in preview evidence",
    )
    playtest_parser.add_argument(
        "--out",
        default=str(REPO_ROOT / "nightcap-web" / ".mini-game-playtests"),
    )
    playtest_parser.add_argument("--adaptation", default=None)
    playtest_parser.add_argument("--serve-ms", type=int, default=0)
    playtest_parser.add_argument("--json", action="store_true", dest="as_json")

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
    if args.command == "onboard-browser":
        return onboard_browser(args)
    if args.command == "resume":
        return resume_onboarding(args)
    if args.command == "status":
        return onboarding_status(args)
    if args.command == "playtest":
        return playtest(args)
    return _fail(f"unknown command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
