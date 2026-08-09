from __future__ import annotations

import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LINE_LIBRARY_DIR = REPO_ROOT / "docs" / "design" / "line-libraries"
MAIN_REF_CANDIDATES = ("origin/main", "main")


def _main_ref() -> str:
    for ref in MAIN_REF_CANDIDATES:
        result = subprocess.run(
            ["git", "rev-parse", "--verify", "--quiet", ref],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            return ref
    raise AssertionError("expected origin/main or main to exist for AW-290 guard")


def _diff_base() -> str:
    main_ref = _main_ref()
    result = subprocess.run(
        ["git", "merge-base", "HEAD", main_ref],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def test_line_libraries_are_unmodified_against_main() -> None:
    diff_base = _diff_base()
    result = subprocess.run(
        [
            "git",
            "diff",
            "--stat",
            diff_base,
            "--",
            "docs/design/line-libraries/",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.strip() == "", (
        f"AW-290 must not edit authored refrain lines; diff:\n{result.stdout}"
    )


def test_line_library_directory_still_has_its_files() -> None:
    files = sorted(LINE_LIBRARY_DIR.glob("*.md"))
    assert len(files) == 15, f"expected 15 library files, found {len(files)}"
