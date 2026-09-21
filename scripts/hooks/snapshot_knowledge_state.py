"""Run the knowledge-base checks detached and write a snapshot for the next session.

These are the same checks CI runs on every pull request. Running them
synchronously at session stop costs about 16 seconds each time and duplicates
CI. Running them detached costs nothing and still surfaces the result — the
next SessionStart reads the snapshot.

Verification note: if reliable detachment is not achievable on this platform,
fall back to running the checks only when the session touched docs/ or
team-ai/, and in parallel (about 6 seconds on those sessions, nothing on the
rest). Record which path is in use here.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from team_ai_cli import find_cli  # noqa: E402  (Task 16b)

SNAPSHOT = ROOT / "team-ai" / "graph" / "last-session-snapshot.json"


def run_checks() -> dict:
    # find_cli returns None rather than raising. A missing sibling checkout must
    # not break the session, but it must also not be reported as a clean run —
    # record that the checks could not execute and let SessionStart say so.
    cli = find_cli()
    if cli is None:
        return {
            "at": datetime.now(timezone.utc).isoformat(),
            "unavailable": "team-ai CLI not found; set TEAM_AI_CLI or build the framework",
        }

    def call(args: list[str]) -> tuple[int, str]:
        result = subprocess.run(
            ["node", str(cli), *args], capture_output=True, text=True, cwd=ROOT
        )
        return result.returncode, (result.stdout or result.stderr).strip()

    kb_code, kb_out = call(["validate-kb", "--instance", "team-ai"])
    mf_code, mf_out = call(["validate-manifest", "--root", "team-ai"])
    fr_code, fr_out = call(["freshness-audit", "--instance", "team-ai"])
    try:
        freshness = json.loads(fr_out)["summary"]
    except (json.JSONDecodeError, KeyError):
        freshness = {}
    return {
        "at": datetime.now(timezone.utc).isoformat(),
        "validate_kb": {"ok": kb_code == 0, "output": kb_out[-500:]},
        "validate_manifest": {"ok": mf_code == 0, "output": mf_out[-500:]},
        "freshness": freshness,
    }


def main() -> int:
    if os.environ.get("ARCWRIGHT_HOOK_SNAPSHOT", "1") != "1":
        return 0
    if os.environ.get("ARCWRIGHT_SNAPSHOT_CHILD") == "1":
        SNAPSHOT.parent.mkdir(parents=True, exist_ok=True)
        SNAPSHOT.write_text(json.dumps(run_checks(), indent=2), encoding="utf-8")
        return 0

    # Re-invoke self detached so the session stop returns immediately.
    env = {**os.environ, "ARCWRIGHT_SNAPSHOT_CHILD": "1"}
    kwargs: dict = {
        "cwd": ROOT,
        "env": env,
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
    }
    if os.name == "nt":
        kwargs["creationflags"] = (
            subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
        )
    else:
        kwargs["start_new_session"] = True
    subprocess.Popen([sys.executable, str(Path(__file__).resolve())], **kwargs)
    return 0


if __name__ == "__main__":
    sys.exit(main())
