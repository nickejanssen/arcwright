"""Keep each knowledge-base agent inside its own part of the knowledge base.

A team-ai specialist answers from its documents. Told so in words, one read the
live-probe answer key under team-ai/evals/, another read engine code, a third
ran a roadmap script its permission was never meant to cover. This hook makes
the boundary mechanical for the agents emitted as `.claude/agents/team-ai-*.md`:

- Read: a document indexed under the KB root in team-ai/index.lock, outside its
  exclusions, whose front matter names one of the agent's own namespaces; or
  index.lock itself, which is how an agent finds that root.
- Grep and Glob: under the KB root and outside its exclusions. Grep may list
  matching files across the KB, but returns content only from the agent's own
  documents.
- Bash: only the ranked-search command, for the agent's own namespaces, with
  nothing chained to it.

Registered in .claude/settings.json, so it runs before every Read, Grep, Glob
and Bash call in the session. A declaration in an agent's own front matter was
measured not to run. Calls from the main session carry no `agent_type` and
return before any import, so they pay only the interpreter's start-up.
"""

from __future__ import annotations

import sys


def paths():
    from pathlib import Path

    root = Path(__file__).resolve().parents[2]
    return root, root / ".claude" / "agents", root / "team-ai" / "index.lock"


def kb_config():
    """The KB root and its exclusion patterns, from team-ai/index.lock."""
    import re

    root, _, index_lock = paths()
    try:
        text = index_lock.read_text(encoding="utf-8")
    except OSError:
        return root / "docs", []
    match = re.search(r"^kb:\s*\n\s+root:\s*(\S+)", text, re.M)
    kb_root = (index_lock.parent / (match.group(1) if match else "../docs")).resolve()
    excludes: list[str] = []
    block = re.search(r"^\s+exclude:\s*\n((?:\s+-\s+.*\n?)+)", text, re.M)
    if block:
        for line in block.group(1).splitlines():
            item = line.strip().removeprefix("-").strip().strip("'\"")
            if item:
                excludes.append(item)
    return kb_root, excludes


def kb_agents() -> dict[str, set[str]]:
    """Each emitted knowledge-base agent and the namespaces it owns."""
    import re

    _, agents, _ = paths()
    owned: dict[str, set[str]] = {}
    for path in agents.glob("team-ai-*.md"):
        text = path.read_text(encoding="utf-8")
        name = re.search(r"^name:\s*(\S+)", text, re.M)
        listed = re.search(r"^kb_namespaces:\s*\n((?:\s+-\s+.*\n?)+)", text, re.M)
        namespaces = (
            {
                line.strip().removeprefix("-").strip()
                for line in listed.group(1).splitlines()
            }
            if listed
            else set()
        )
        owned[name.group(1) if name else path.stem.removeprefix("team-ai-")] = (
            namespaces
        )
    return owned


def within(path, parent) -> bool:
    import os

    child = os.path.normcase(str(path))
    base = os.path.normcase(str(parent))
    return child == base or child.startswith(base.rstrip("\\/") + os.sep)


def resolve(raw: str, cwd: str | None):
    from pathlib import Path

    root, _, _ = paths()
    path = Path(raw)
    if not path.is_absolute():
        path = Path(cwd or root) / path
    return path.resolve()


def excluded(path, kb_root, excludes: list[str]) -> bool:
    import fnmatch
    import os

    rel = os.path.relpath(path, kb_root).replace(os.sep, "/")
    for pattern in excludes:
        if pattern.endswith("/"):
            if rel == pattern.rstrip("/") or rel.startswith(pattern):
                return True
        elif any(ch in pattern for ch in "*?["):
            if fnmatch.fnmatch(rel, pattern) or fnmatch.fnmatch(
                rel, pattern.removeprefix("**/")
            ):
                return True
        elif rel == pattern or rel.endswith("/" + pattern):
            return True
    return False


def document_namespace(path) -> str | None:
    import re

    try:
        with open(path, encoding="utf-8") as handle:
            head = handle.read(2048)
    except OSError:
        return None
    if not head.startswith("---"):
        return None
    match = re.search(r"^namespace:\s*(\S+)", head, re.M)
    return match.group(1) if match else None


def search_command(owned: set[str]) -> str:
    namespace = (
        " ".join(f"--namespace {ns}" for ns in sorted(owned)) or "--namespace <yours>"
    )
    return f'python scripts/team_ai_cli.py search "<the question>" --root team-ai {namespace} --k 8'


def bash_verdict(command: str, owned: set[str], cwd: str | None) -> str | None:
    import re
    import shlex

    root, _, _ = paths()
    refusal = (
        "Refused by the knowledge-base boundary, not by a missing interpreter: "
        "Python is available. Knowledge-base agents may run only this command, "
        f"exactly, from the repository root: {search_command(owned)}. "
        "For status, code or history, name the source that owns the answer."
    )
    # A trailing stderr redirect is harmless and habitual; refusing it set off
    # retry cascades that ended in agents misreporting a missing interpreter.
    command = re.sub(r"\s+2>&1\s*$", "", command)
    if re.search(r"[;|`<>$\n]", command):
        return refusal
    try:
        tokens = shlex.split(command)
    except ValueError:
        return refusal
    if tokens[:1] == ["cd"] and len(tokens) > 3 and tokens[2] == "&&":
        if resolve(tokens[1], cwd) != root.resolve():
            return refusal
        tokens = tokens[3:]
    if "&" in "".join(tokens) or tokens[:3] != [
        "python",
        "scripts/team_ai_cli.py",
        "search",
    ]:
        return refusal
    rest = tokens[3:]
    if not rest or rest[0].startswith("--"):
        return refusal
    namespaces: set[str] = set()
    seen_root = False
    index = 1
    while index < len(rest):
        flag = rest[index]
        value = rest[index + 1] if index + 1 < len(rest) else None
        if value is None:
            return refusal
        if flag == "--root" and value == "team-ai":
            seen_root = True
        elif flag == "--namespace":
            namespaces.add(value)
        elif flag == "--k" and value.isdigit():
            pass
        else:
            return refusal
        index += 2
    if not seen_root or not namespaces or not namespaces <= owned:
        return refusal
    return None


def verdict(event: dict) -> str | None:
    """A denial reason, or None to allow."""
    import os

    owned = kb_agents().get(event.get("agent_type"))
    if owned is None:
        return None
    root_dir, _, index_lock = paths()
    kb_root, excludes = kb_config()
    tool = event.get("tool_name")
    args = event.get("tool_input") or {}
    cwd = event.get("cwd")
    rel_root = os.path.relpath(kb_root, root_dir).replace(os.sep, "/")
    yours = ", ".join(sorted(owned))

    def readable(target) -> str | None:
        if not within(target, kb_root):
            return f"{target.name} is outside the knowledge base ({rel_root}/)."
        if excluded(target, kb_root, excludes):
            return f"{target.name} is excluded from the knowledge base index."
        if target.is_file():
            namespace = document_namespace(target)
            if namespace not in owned:
                return (
                    f"{target.name} belongs to namespace {namespace or 'none'}; "
                    f"yours is {yours}. Name that namespace's agent as the owner."
                )
        return None

    if tool == "Read":
        target = resolve(str(args.get("file_path", "")), cwd)
        if target == index_lock.resolve():
            return None
        problem = readable(target)
        return None if problem is None else f"Refused: {problem}"
    if tool in ("Grep", "Glob"):
        raw = args.get("path")
        if not raw:
            return f'Refused: pass path: "{rel_root}" to search the knowledge base.'
        target = resolve(str(raw), cwd)
        if target == index_lock.resolve():
            return None
        if not within(target, kb_root):
            return f'Refused: search only under {rel_root}/. Pass path: "{rel_root}".'
        if excluded(target, kb_root, excludes):
            return f"Refused: {target.name} is excluded from the knowledge base index."
        content = tool == "Grep" and args.get("output_mode") == "content"
        if content and not target.is_file():
            return (
                "Refused: across the knowledge base, Grep may list matching files "
                "(output_mode files_with_matches) but not return their content. "
                f"Read the matches that belong to your namespace ({yours})."
            )
        if content:
            problem = readable(target)
            return None if problem is None else f"Refused: {problem}"
        return None
    if tool == "Bash":
        return bash_verdict(str(args.get("command", "")).strip(), owned, cwd)
    return None


def main() -> int:
    raw = sys.stdin.read()
    # Main-session calls carry no agent_type: allow before paying for imports.
    if '"agent_type"' not in raw:
        return 0
    import json
    import os

    try:
        event = json.loads(raw)
    except ValueError:
        return 0
    reason = verdict(event)
    log = os.environ.get("TEAM_AI_GUARD_LOG")
    if log:
        # Set at a probe review to see what each agent tried and what was refused.
        args = event.get("tool_input") or {}
        record = {
            "agent": event.get("agent_type"),
            "tool": event.get("tool_name"),
            "target": args.get("file_path") or args.get("path") or args.get("command"),
            "denied": reason is not None,
            "reason": reason,
        }
        with open(log, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(record) + chr(10))
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
