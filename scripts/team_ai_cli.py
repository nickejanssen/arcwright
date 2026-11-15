"""Locate the team-ai CLI, and optionally run it.

The framework may live outside the active checkout. Every agent session here
runs in a git worktree, where the repository's parent is the worktree container
rather than the checkout's parent. `git rev-parse --git-common-dir` points at
the main repository's `.git` from anywhere, including a worktree, so the
checkout's real sibling stays reachable from all of them.

Callers decide what a missing CLI means. Hooks must not fail because a sibling
checkout is absent: a check that breaks every session is worse than no check.
"""

from __future__ import annotations

import sys

# A linked worktree can supply extra files next to this approved wrapper.
# Drop Python's implicit script directory before importing the standard library.
if __name__ == "__main__" and not sys.flags.safe_path:
    del sys.path[0]

import os  # noqa: E402
import shutil  # noqa: E402
import subprocess  # noqa: E402
from pathlib import Path  # noqa: E402

REL = Path("team-ai") / "dist" / "cli.js"


def _tool_on_path(name: str) -> str | None:
    filename = f"{name}.exe" if os.name == "nt" else name
    for directory in map(Path, os.get_exec_path()):
        if directory.is_absolute():
            match = shutil.which(str(directory / filename))
            if match:
                return match
    return None


def _main_checkout() -> Path | None:
    git = _tool_on_path("git")
    if git is None:
        return None
    try:
        out = subprocess.run(
            [git, "rev-parse", "--path-format=absolute", "--git-common-dir"],
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

    main = _main_checkout()
    here = Path(__file__).resolve().parents[1]
    roots = [main.parent] if main is not None else [here.parent, here.parent.parent]

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
    node = _tool_on_path("node")
    if node is None:
        print("Node.js not found on PATH.", file=sys.stderr)
        return 1
    command = [node, str(cli), *args]
    if args[:1] != ["search"]:
        return subprocess.run(command).returncode

    result = subprocess.run(command, stderr=subprocess.PIPE)
    sys.stderr.buffer.write(result.stderr)
    if result.returncode and result.stderr.startswith(b"index not built"):
        print(
            "Ranked search is unavailable in this checkout. Use plain search with "
            "Grep or Glob under docs/, then Read the matches in your namespace. "
            "A maintainer can restore ranked search by running "
            "`python scripts/team_ai_cli.py reindex --root team-ai` from the checkout root.",
            file=sys.stderr,
        )
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
