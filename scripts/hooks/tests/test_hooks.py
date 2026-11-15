import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.hooks import inject_session_context, snapshot_knowledge_state

ROOT = Path(__file__).resolve().parents[3]
BLOCK = ROOT / "scripts" / "hooks" / "block_generated_writes.py"
RECORD = ROOT / "scripts" / "hooks" / "record_observation.py"
INJECT = ROOT / "scripts" / "hooks" / "inject_session_context.py"
GUARD = ROOT / "scripts" / "hooks" / "guard_kb_agents.py"


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


def checkout_with_worktree(tmp_path):
    """A main checkout holding the guard hook, and a git worktree of it.

    Laid out as desktop sessions are: the worktree sits under the main
    checkout's .claude/worktrees/, and the registered hook may be the main
    checkout's copy while the agent works in the worktree.
    """
    main = tmp_path / "main"
    (main / "scripts" / "hooks").mkdir(parents=True)
    shutil.copy(GUARD, main / "scripts" / "hooks" / "guard_kb_agents.py")
    (main / "team-ai").mkdir()
    (main / "team-ai" / "index.lock").write_text(
        "kb:\n  root: ../docs\n  exclude:\n    - archive/\n", encoding="utf-8"
    )
    (main / ".claude" / "agents").mkdir(parents=True)
    (main / ".claude" / "agents" / "team-ai-safety-sme.md").write_text(
        "---\nname: safety-sme\nkb_namespaces:\n  - safety\n---\n", encoding="utf-8"
    )
    (main / "docs").mkdir()
    (main / "docs" / "safety.md").write_text(
        "---\nnamespace: safety\n---\n# Safety\n", encoding="utf-8"
    )
    (main / "engine").mkdir()
    (main / "engine" / "service.py").write_text("x = 1\n", encoding="utf-8")
    git = ["git", "-c", "user.name=t", "-c", "user.email=t@example.com"]
    for args in (["init", "-q"], ["add", "-A"], ["commit", "-q", "-m", "init"]):
        subprocess.run([*git, *args], cwd=main, check=True, capture_output=True)
    worktree = main / ".claude" / "worktrees" / "wt"
    subprocess.run(
        [*git, "worktree", "add", "-q", "-b", "wt", str(worktree)],
        cwd=main,
        check=True,
        capture_output=True,
    )
    return main, worktree


def guard_denies(hook_checkout, cwd, tool, **tool_input):
    result = run(
        hook_checkout / "scripts" / "hooks" / "guard_kb_agents.py",
        {
            "agent_type": "safety-sme",
            "tool_name": tool,
            "tool_input": tool_input,
            "cwd": str(cwd),
        },
    )
    assert result.returncode == 0, result.stderr
    return '"deny"' in result.stdout


@pytest.mark.skipif(shutil.which("git") is None, reason="needs git worktrees")
def test_kb_guard_allows_the_kb_from_a_worktree(tmp_path):
    main, worktree = checkout_with_worktree(tmp_path)
    for hook_checkout in (main, worktree):
        assert not guard_denies(
            hook_checkout, worktree, "Grep", pattern="x", path="docs"
        )
        assert not guard_denies(
            hook_checkout, worktree, "Glob", pattern="*", path="docs"
        )
        assert not guard_denies(
            hook_checkout, worktree, "Read", file_path="docs/safety.md"
        )
        assert not guard_denies(
            hook_checkout,
            worktree,
            "Bash",
            command=f'cd "{worktree}" && python scripts/team_ai_cli.py search "x" '
            "--root team-ai --namespace safety --k 8",
        )


@pytest.mark.skipif(shutil.which("git") is None, reason="needs git worktrees")
def test_kb_guard_refuses_outside_the_kb_from_main_and_worktree(tmp_path):
    main, worktree = checkout_with_worktree(tmp_path)
    for hook_checkout in (main, worktree):
        for cwd in (main, worktree):
            assert guard_denies(
                hook_checkout, cwd, "Read", file_path="engine/service.py"
            )
            assert guard_denies(hook_checkout, cwd, "Grep", pattern="x", path="engine")
            assert guard_denies(hook_checkout, cwd, "Glob", pattern="*", path=".")
            assert guard_denies(hook_checkout, cwd, "Grep", pattern="x", path="docs/..")
        assert guard_denies(
            hook_checkout,
            worktree,
            "Read",
            file_path=str(main / "engine" / "service.py"),
        )


@pytest.mark.skipif(shutil.which("bash") is None, reason="hooks run under bash")
def test_registered_hooks_run_from_a_subdirectory():
    # A Bash `cd` persists into the session, and hooks inherit that directory;
    # a command relative to the repository root then fails on every tool call.
    settings = json.loads(
        (ROOT / ".claude" / "settings.json").read_text(encoding="utf-8")
    )
    commands = [
        hook["command"]
        for entries in settings["hooks"].values()
        for entry in entries
        for hook in entry["hooks"]
    ]
    env = {
        **os.environ,
        "CLAUDE_PROJECT_DIR": str(ROOT),
        "ARCWRIGHT_HOOK_BLOCK_GENERATED": "0",
        "ARCWRIGHT_HOOK_RECORD_OBSERVATIONS": "0",
        "ARCWRIGHT_HOOK_SNAPSHOT": "0",
        "ARCWRIGHT_HOOK_SESSION_CONTEXT": "0",
    }
    for command in commands:
        result = subprocess.run(
            [shutil.which("bash"), "-c", command],
            input="{}",
            capture_output=True,
            text=True,
            cwd=ROOT / "scripts",
            env=env,
        )
        assert result.returncode == 0, f"{command}: {result.stderr}"
