import importlib.util
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


def test_prose_may_discuss_an_unapproved_decision():
    # Reference integrity answers "does this id exist", which is what catches a
    # fabricated citation. A spec may legitimately write that a decision is
    # still tentative and therefore not build scope; rejecting that sentence
    # would block careful writing and report the decision as absent, which is
    # false. The approval gate is what refuses it as *evidence*, and a script
    # cannot tell "approved per D-047" from "D-047 is still open" -- that is
    # reading comprehension, which D-B2 ruled out.
    planted = ROOT / "docs" / "specs" / "9999-probe.md"
    planted.write_text(
        "D-047 is still tentative, so this doc does not treat it as build scope.\n",
        encoding="utf-8",
    )
    try:
        result = run()
        assert result.returncode == 0, result.stdout
    finally:
        planted.unlink()


def test_approval_set_excludes_unapproved_statuses():
    # The gate's set must be strictly smaller than the existence set, and must
    # exclude a decision the log records as tentative.
    spec = importlib.util.spec_from_file_location("scope_evidence_check", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    existing = module.existing_decision_ids()
    approved = module.approved_decision_ids()
    assert approved < existing
    assert "D-047" in existing
    assert "D-047" not in approved
