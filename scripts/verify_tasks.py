#!/usr/bin/env python3
"""Simple repository verification for roadmap milestones.

This script checks for the presence of key artifacts required to mark
milestone tasks as completed. It's intentionally conservative — it looks
for files and symbols that are strong indicators of work having been
implemented.

Use in CI to gate milestone completion claims.
"""

from __future__ import annotations

import argparse
import os


def file_exists(path: str) -> bool:
    return os.path.exists(os.path.join(repo_root(), path))


def repo_root() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def contains(path: str, token: str) -> bool:
    try:
        with open(os.path.join(repo_root(), path), "r", encoding="utf-8") as f:
            return token in f.read()
    except Exception:
        return False


def check_aw_101() -> tuple[bool, str]:
    required = [
        "pyproject.toml",
        "Makefile",
        "engine/__init__.py",
        "api/__init__.py",
        "tests/arc",
        "tests/knowledge_graph",
        "tests/routing",
        "tests/safety",
    ]
    missing = [p for p in required if not file_exists(p)]
    if missing:
        return False, f"AW-101 missing: {missing}"
    return True, "AW-101 OK"


def check_aw_102_104() -> tuple[bool, str]:
    # Check migrations exist and alembic.ini exists
    if not file_exists("alembic.ini"):
        return False, "alembic.ini missing"
    versions_dir = os.path.join(repo_root(), "migrations", "versions")
    if not os.path.isdir(versions_dir):
        return False, "migrations/versions missing"
    files = os.listdir(versions_dir)
    has_0001 = any(f.startswith("0001_") or f.startswith("0001") for f in files)
    has_0002 = any(f.startswith("0002_") or f.startswith("0002") for f in files)
    if not (has_0001 and has_0002):
        return (
            False,
            f"expected migration files 0001/0002 in migrations/versions, found: {files}",
        )
    return True, "AW-102/AW-104 OK"


def check_aw_103() -> tuple[bool, str]:
    if not file_exists("engine/db/orm.py"):
        return False, "engine/db/orm.py missing"
    # check for GenerationLog table presence as a heuristic
    if not contains("engine/db/orm.py", "class GenerationLog"):
        return False, "GenerationLog model not present in engine/db/orm.py"
    return True, "AW-103 OK"


def check_aw_105_106() -> tuple[bool, str]:
    if not file_exists("engine/knowledge/graph.py"):
        return False, "engine/knowledge/graph.py missing"
    tokens = ["def assert_knowledge", "def get_character_knowledge"]
    missing = [t for t in tokens if not contains("engine/knowledge/graph.py", t)]
    if missing:
        return False, f"engine/knowledge/graph.py missing functions: {missing}"
    return True, "AW-105/AW-106 OK"


def check_aw_107_108() -> tuple[bool, str]:
    if not file_exists("engine/routing/router.py"):
        return False, "engine/routing/router.py missing"
    if not contains("engine/routing/router.py", "resolve_model_key"):
        return False, "router.py missing resolve_model_key"
    # generation logging heuristic already covered by GenerationLog in orm
    return True, "AW-107/AW-108 OK"


def check_aw_110_111_112() -> tuple[bool, str]:
    harness_dir = os.path.join(repo_root(), "engine", "harness")
    if not os.path.isdir(harness_dir):
        return False, "engine/harness missing"
    files = os.listdir(harness_dir)
    required = ["runner.py", "replay.py", "batch.py"]
    missing = [f for f in required if f not in files]
    if missing:
        return False, f"engine/harness missing files: {missing}"
    return True, "AW-110/111/112 OK"


def run_checks(milestone: str) -> int:
    checks = []
    # Support M1, M2, M3 basic checks
    if milestone == "M1":
        checks = [
            ("AW-101", check_aw_101),
            ("AW-102/AW-104", check_aw_102_104),
            ("AW-103", check_aw_103),
            ("AW-105/AW-106", check_aw_105_106),
            ("AW-107/AW-108", check_aw_107_108),
            ("AW-110/111/112", check_aw_110_111_112),
        ]
    elif milestone == "M2":
        checks = [
            (
                "AW-203: ArcDefinition schema",
                lambda: (
                    file_exists("engine/arc/arc_definition.py")
                    or file_exists("engine/arc/models.py"),
                    "arc definition model exists",
                ),
            ),
            (
                "AW-205: Nightcap canonical arc",
                lambda: (file_exists("nightcap/arc.json"), "nightcap/arc.json present"),
            ),
            (
                "AW-206: Killer assignment",
                lambda: (
                    contains("engine/harness/runner.py", "killer_assignment")
                    or contains("engine/harness/runner.py", "KILLER_ASSIGNMENT_KEY"),
                    "killer assignment logic present in harness",
                ),
            ),
        ]
    elif milestone == "M3":
        checks = [
            (
                "AW-215: ContentEvent model",
                lambda: (
                    contains("engine/db/orm.py", "class Event")
                    and contains("engine/db/orm.py", "content_text"),
                    "Event model with content_text present",
                ),
            ),
            (
                "AW-217: Session Lifecycle API",
                lambda: (
                    file_exists("api/routers")
                    and any(
                        name.endswith(".py")
                        for name in os.listdir(
                            os.path.join(repo_root(), "api", "routers")
                        )
                    ),
                    "api routers present",
                ),
            ),
            (
                "AW-222: Telemetry signals",
                lambda: (
                    contains(
                        "docs/architecture/11-telemetry.md",
                        "Five MVP Telemetry Signals",
                    )
                    or contains("docs/architecture/11-telemetry.md", "five"),
                    "telemetry doc present",
                ),
            ),
        ]
    else:
        print(f"No automated checks defined for milestone: {milestone}")
        return 1

    all_ok = True
    for name, fn in checks:
        ok, msg = fn()
        print(f"{name}: {'OK' if ok else 'FAIL'} - {msg}")
        if not ok:
            all_ok = False

    return 0 if all_ok else 2


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--milestone", default="M1", help="Milestone id to verify")
    args = parser.parse_args()
    return run_checks(args.milestone)


if __name__ == "__main__":
    raise SystemExit(main())
