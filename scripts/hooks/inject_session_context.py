"""Inject the domain map and the last session's findings at session start.

Reads files only — no CLI calls — so it costs milliseconds rather than the six
seconds a freshness audit takes.

Freshness is reported as a delta against a committed baseline. The absolute
figures are 0 stale, 0 unowned and 436 orphaned of 447; printing 436 every
session is noise, while a change against it is a signal.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "team-ai" / "manifest.yaml"
SNAPSHOT = ROOT / "team-ai" / "graph" / "last-session-snapshot.json"
BASELINE = ROOT / "team-ai" / "graph" / "freshness-baseline.json"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def main() -> int:
    if os.environ.get("ARCWRIGHT_HOOK_SESSION_CONTEXT", "1") != "1":
        return 0

    lines: list[str] = []
    try:
        manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError):
        manifest = {}
    domains = manifest.get("domains", [])
    if domains:
        lines.append("Knowledge domains and the agent that owns each:")
        for domain in domains:
            lines.append(f"  {domain['id']:24} -> {domain['subagent']}")

    snapshot = read_json(SNAPSHOT)
    if snapshot.get("unavailable"):
        lines.append("")
        lines.append(
            f"Knowledge-base checks did not run last session: {snapshot['unavailable']}"
        )
    elif snapshot:
        problems = [
            name
            for name in ("validate_kb", "validate_manifest")
            if isinstance(snapshot.get(name), dict)
            and snapshot[name].get("ok") is False
        ]
        if problems:
            lines.append("")
            lines.append(
                f"Knowledge base FAILING as of last session: {', '.join(problems)}"
            )

        baseline = read_json(BASELINE).get("summary", {})
        current = snapshot.get("freshness", {})
        deltas = [
            f"{key} {current[key] - baseline.get(key, 0):+d}"
            for key in ("stale", "orphaned", "unowned")
            if key in current and current[key] != baseline.get(key, 0)
        ]
        if deltas:
            lines.append(f"Freshness change since baseline: {', '.join(deltas)}")

    if lines:
        print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
