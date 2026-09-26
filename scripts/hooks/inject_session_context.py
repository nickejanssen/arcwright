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
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "team-ai" / "manifest.yaml"
SNAPSHOT = ROOT / "team-ai" / "graph" / "last-session-snapshot.json"
BASELINE = ROOT / "team-ai" / "graph" / "freshness-baseline.json"
DOMAIN_ID = re.compile(r"^  - id: (.+)$")
SUBAGENT = re.compile(r"^    subagent: (.+)$")


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def read_domains(text: str) -> list[dict[str, str]]:
    domains: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for line in text.splitlines():
        id_match = DOMAIN_ID.match(line)
        if id_match:
            if current and "subagent" in current:
                domains.append(current)
            current = {"id": id_match.group(1).strip()}
            continue
        subagent_match = SUBAGENT.match(line)
        if current is not None and subagent_match:
            current["subagent"] = subagent_match.group(1).strip()
    if current and "subagent" in current:
        domains.append(current)
    return domains


def main() -> int:
    if os.environ.get("ARCWRIGHT_HOOK_SESSION_CONTEXT", "1") != "1":
        return 0

    lines: list[str] = []
    try:
        domains = read_domains(MANIFEST.read_text(encoding="utf-8"))
    except OSError:
        domains = []
    if domains:
        lines.append("Knowledge domains and the agent that owns each:")
        for domain in domains:
            lines.append(f"  {domain['id']:24} -> {domain['subagent']}")
        # No router agent is emitted (spec 0089, B-S6): this session routes.
        lines.append(
            "Dispatch the owning agent directly; for a question spanning two domains, "
            "dispatch both in parallel and reconcile. These agents answer design, scope and "
            "decisions only: task status is on GitHub (python scripts/roadmap_status.py), "
            "code existence in the code, history in git."
        )

    snapshot = read_json(SNAPSHOT)
    if snapshot.get("unavailable"):
        lines.append("")
        lines.append(
            f"Knowledge-base checks did not run last session: {snapshot['unavailable']}"
        )
    elif snapshot:
        problems = [
            name
            for name in ("validate_kb", "validate_manifest", "freshness")
            if isinstance(snapshot.get(name), dict)
            and snapshot[name].get("ok") is False
        ]
        if problems:
            lines.append("")
            lines.append(
                f"Knowledge base FAILING as of last session: {', '.join(problems)}"
            )

        baseline = read_json(BASELINE).get("summary", {})
        freshness = snapshot.get("freshness", {})
        current = freshness.get("summary", {}) if isinstance(freshness, dict) else {}
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
