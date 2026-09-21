import json
import os
import subprocess
import sys
from pathlib import Path

from scripts.hooks import inject_session_context, snapshot_knowledge_state

ROOT = Path(__file__).resolve().parents[3]
BLOCK = ROOT / "scripts" / "hooks" / "block_generated_writes.py"
RECORD = ROOT / "scripts" / "hooks" / "record_observation.py"
INJECT = ROOT / "scripts" / "hooks" / "inject_session_context.py"


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


def test_injector_has_no_external_yaml_dependency():
    result = subprocess.run(
        [sys.executable, "-S", str(INJECT)],
        capture_output=True,
        text=True,
        cwd=ROOT,
        env={**os.environ, "ARCWRIGHT_HOOK_SESSION_CONTEXT": "0"},
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_injector_surfaces_freshness_failure(tmp_path, monkeypatch, capsys):
    manifest = tmp_path / "manifest.yaml"
    manifest.write_text(
        "domains:\n  - id: engineering-practice\n    subagent: practice-sme\n",
        encoding="utf-8",
    )
    snapshot = tmp_path / "snapshot.json"
    snapshot.write_text(
        json.dumps(
            {
                "validate_kb": {"ok": True, "output": "OK"},
                "validate_manifest": {"ok": True, "output": "OK"},
                "freshness": {"ok": False, "output": "freshness failed"},
            }
        ),
        encoding="utf-8",
    )
    baseline = tmp_path / "baseline.json"
    baseline.write_text(json.dumps({"summary": {}}), encoding="utf-8")
    monkeypatch.setattr(inject_session_context, "MANIFEST", manifest)
    monkeypatch.setattr(inject_session_context, "SNAPSHOT", snapshot)
    monkeypatch.setattr(inject_session_context, "BASELINE", baseline)

    assert inject_session_context.main() == 0
    assert "freshness" in capsys.readouterr().out


def test_snapshot_records_freshness_failure(monkeypatch):
    monkeypatch.setattr(snapshot_knowledge_state, "find_cli", lambda: Path("cli.js"))

    def fake_run(command, **_kwargs):
        if "freshness-audit" in command:
            return subprocess.CompletedProcess(command, 7, "", "freshness failed")
        return subprocess.CompletedProcess(command, 0, "OK", "")

    monkeypatch.setattr(snapshot_knowledge_state.subprocess, "run", fake_run)
    snapshot = snapshot_knowledge_state.run_checks()

    assert snapshot["freshness"]["ok"] is False
    assert snapshot["freshness"]["output"] == "freshness failed"
