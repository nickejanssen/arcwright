import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "team_ai_cli.py"


def test_resolves_from_this_checkout():
    out = subprocess.run(
        [sys.executable, str(SCRIPT), "--path"],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    assert out.returncode == 0, out.stderr
    assert Path(out.stdout.strip()).exists()


def test_env_override_wins(tmp_path):
    fake = tmp_path / "cli.js"
    fake.write_text("", encoding="utf-8")
    env = {**os.environ, "TEAM_AI_CLI": str(fake)}
    out = subprocess.run(
        [sys.executable, str(SCRIPT), "--path"],
        capture_output=True,
        text=True,
        cwd=ROOT,
        env=env,
    )
    assert out.stdout.strip() == str(fake)


def test_missing_cli_exits_nonzero_without_raising(tmp_path):
    env = {**os.environ, "TEAM_AI_CLI": str(tmp_path / "absent.js")}
    out = subprocess.run(
        [sys.executable, str(SCRIPT), "--path"],
        capture_output=True,
        text=True,
        cwd=ROOT,
        env=env,
    )
    assert out.returncode != 0
    assert "Traceback" not in out.stderr
