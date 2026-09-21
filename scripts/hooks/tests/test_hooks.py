import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BLOCK = ROOT / "scripts" / "hooks" / "block_generated_writes.py"
RECORD = ROOT / "scripts" / "hooks" / "record_observation.py"


def run(script, payload):
    return subprocess.run(
        [sys.executable, str(script)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=ROOT,
    )


def test_blocks_generated_agent_write():
    result = run(BLOCK, {"tool_input": {"file_path": ".claude/agents/team-ai-sme.md"}})
    assert result.returncode != 0
    assert "emit" in result.stdout + result.stderr


def test_allows_ordinary_doc_write():
    result = run(BLOCK, {"tool_input": {"file_path": "docs/specs/0089-x.md"}})
    assert result.returncode == 0


def test_records_one_raw_line(tmp_path):
    result = run(
        RECORD,
        {
            "session_id": "probe-session",
            "tool_input": {"file_path": "docs/specs/0089-x.md"},
        },
    )
    assert result.returncode == 0
    written = list(
        (ROOT / "team-ai" / "graph" / "observations").rglob("probe-session.jsonl")
    )
    assert written, "no observation file written"
    record = json.loads(written[0].read_text(encoding="utf-8").splitlines()[-1])
    assert set(record) == {"session_id", "at", "path"}
    written[0].unlink()
