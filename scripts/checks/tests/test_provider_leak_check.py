import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts" / "checks" / "provider_leak_check.py"


def run(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args], capture_output=True, text=True, cwd=ROOT
    )


def test_passes_on_clean_tree():
    result = run()
    assert result.returncode == 0, result.stdout + result.stderr


def test_fails_on_planted_violation(tmp_path):
    planted = ROOT / "engine" / "session" / "_leak_probe.py"
    planted.write_text(
        'MODEL = "anthropic/claude-haiku-4-5-20251001"\n', encoding="utf-8"
    )
    try:
        result = run()
        assert result.returncode != 0
        assert "_leak_probe.py" in result.stdout
    finally:
        planted.unlink()


def test_permits_the_two_routing_files():
    result = run()
    assert "routing_table.json" not in result.stdout
    assert "routing/router.py" not in result.stdout
