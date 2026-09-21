"""Record one raw fact per write: which session touched which path, and when.

Deliberately records no edge type, no weight and no relationship. A statement
that "this session touched these paths" cannot be wrong, so Phase C derives
edges from it rather than being forced to reshape a format guessed here.

Files are sharded per session and only ever appended to by the session that
owns them, so two branches cannot conflict on the same file.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OBSERVATIONS = ROOT / "team-ai" / "graph" / "observations"


def main() -> int:
    if os.environ.get("ARCWRIGHT_HOOK_RECORD_OBSERVATIONS", "1") != "1":
        return 0
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    path = str(payload.get("tool_input", {}).get("file_path", "")).replace("\\", "/")
    session_id = str(payload.get("session_id", "")) or "unknown"
    if not path:
        return 0
    try:
        path = Path(path).resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return 0  # outside the repository; not ours to record

    now = datetime.now(timezone.utc)
    target = OBSERVATIONS / now.strftime("%Y-%m") / f"{session_id}.jsonl"
    target.parent.mkdir(parents=True, exist_ok=True)
    record = {"session_id": session_id, "at": now.isoformat(), "path": path}
    with target.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
