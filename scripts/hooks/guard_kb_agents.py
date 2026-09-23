"""Keep knowledge-base agents inside the knowledge base.

A team-ai specialist answers from its documents. Told so in words, one read the
live-probe answer key under team-ai/evals/, another read engine code, a third
ran a roadmap script its permission was never meant to cover. This hook makes
the boundary mechanical for the agents emitted as `.claude/agents/team-ai-*.md`:

- Read, Grep and Glob only under the KB root recorded in team-ai/index.lock,
  plus index.lock itself, which is how an agent finds that root.
- Bash only for the ranked-search command, with no shell chaining.

Every other caller, including the main session, is untouched.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AGENTS = ROOT / ".claude" / "agents"
INDEX_LOCK = ROOT / "team-ai" / "index.lock"
SEARCH_COMMAND = "python scripts/team_ai_cli.py search "
SHELL_CONTROL = re.compile(r"[;&|`<>$\n]")


def kb_root() -> Path:
    try:
        text = INDEX_LOCK.read_text(encoding="utf-8")
    except OSError:
        return ROOT / "docs"
    match = re.search(r"^kb:\s*\n\s+root:\s*(\S+)", text, re.M)
    return (INDEX_LOCK.parent / (match.group(1) if match else "../docs")).resolve()


def kb_agents() -> set[str]:
    return {path.stem.removeprefix("team-ai-") for path in AGENTS.glob("team-ai-*.md")}


def within(path: Path, parent: Path) -> bool:
    child = os.path.normcase(str(path))
    base = os.path.normcase(str(parent))
    return child == base or child.startswith(base.rstrip("\\/") + os.sep)


def resolve(raw: str, cwd: str | None) -> Path:
    path = Path(raw)
    if not path.is_absolute():
        path = Path(cwd or ROOT) / path
    return path.resolve()


def verdict(event: dict) -> str | None:
    """A denial reason, or None to allow."""
    if event.get("agent_type") not in kb_agents():
        return None
    tool = event.get("tool_name")
    args = event.get("tool_input") or {}
    cwd = event.get("cwd")
    root = kb_root()
    rel_root = os.path.relpath(root, ROOT).replace(os.sep, "/")

    if tool == "Read":
        target = resolve(str(args.get("file_path", "")), cwd)
        if within(target, root) or target == INDEX_LOCK.resolve():
            return None
        return (
            f"Knowledge-base agents read only under {rel_root}/. "
            f"{target.name} is outside it: answer from your documents, or name the "
            "source that owns the answer."
        )
    if tool in ("Grep", "Glob"):
        raw = args.get("path")
        if raw and within(resolve(str(raw), cwd), root):
            return None
        return (
            f"Knowledge-base agents search only under {rel_root}/. "
            f'Pass path: "{rel_root}".'
        )
    if tool == "Bash":
        command = str(args.get("command", "")).strip()
        if command.startswith(SEARCH_COMMAND) and not SHELL_CONTROL.search(command):
            return None
        return (
            "Knowledge-base agents may run only the ranked-search command, alone, "
            "with none of ; & | ` $ < > in it. For status, code or history, name the "
            "source that owns the answer."
        )
    return None


def main() -> int:
    try:
        event = json.load(sys.stdin)
    except (ValueError, OSError):
        return 0
    reason = verdict(event)
    if reason is not None:
        json.dump(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            },
            sys.stdout,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
