import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts" / "checks" / "scope_evidence_check.py"


def run(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args], capture_output=True, text=True, cwd=ROOT
    )


def test_clean_tree_has_no_dangling_references():
    result = run()
    assert result.returncode == 0, result.stdout + result.stderr


def test_resolves_a_quoted_csv_row():
    # D-034's row is quoted in the CSV; a line-based grep misses it.
    result = run("--explain", "D-034")
    assert "resolved" in result.stdout


def test_normalises_zero_padding():
    result = run("--explain", "D-45")
    assert "resolved" in result.stdout


def test_fails_on_a_fabricated_id():
    planted = ROOT / "docs" / "specs" / "9999-probe.md"
    planted.write_text("Approved per D-999.\n", encoding="utf-8")
    try:
        result = run()
        assert result.returncode != 0
        assert "D-999" in result.stdout
    finally:
        planted.unlink()
