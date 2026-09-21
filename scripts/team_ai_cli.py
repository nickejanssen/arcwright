"""Locate the team-ai CLI, and optionally run it.

`../team-ai` is correct only in the main checkout. Every agent session here runs
in a git worktree, where the repository's parent is the worktree container
rather than the checkout's parent. `git rev-parse --git-common-dir` points at
the main repository's `.git` from anywhere, including a worktree, so the
checkout's real sibling stays reachable from all of them.

Callers decide what a missing CLI means. Hooks must not fail because a sibling
checkout is absent: a check that breaks every session is worse than no check.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REL = Path("team-ai") / "dist" / "cli.js"


def _main_checkout() -> Path | None:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except (subprocess.CalledProcessError, OSError):
        return None
    return Path(out).parent if out else None


def find_cli() -> Path | None:
    """Return the CLI path, or None. Never raises."""
    override = os.environ.get("TEAM_AI_CLI")
    if override:
        candidate = Path(override)
        return candidate if candidate.is_file() else None

    roots: list[Path] = []
    main = _main_checkout()
    if main is not None:
        roots.append(main.parent)
    here = Path(__file__).resolve().parents[1]
    roots.extend([here.parent, here.parent.parent])

    for root in roots:
        candidate = root / REL
        if candidate.is_file():
            return candidate
    return None


def main() -> int:
    args = sys.argv[1:]
    cli = find_cli()
    if cli is None:
        print(
            "team-ai CLI not found. Set TEAM_AI_CLI, or clone team-ai beside "
            "this repository and run npm ci && npm run build.",
            file=sys.stderr,
        )
        return 1
    if args[:1] == ["--path"]:
        print(cli)
        return 0
    return subprocess.run(["node", str(cli), *args]).returncode


if __name__ == "__main__":
    sys.exit(main())
