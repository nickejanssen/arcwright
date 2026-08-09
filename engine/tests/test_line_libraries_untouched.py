from __future__ import annotations

import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LINE_LIBRARY_DIR = REPO_ROOT / "docs" / "design" / "line-libraries"


def test_line_libraries_are_unmodified_against_main() -> None:
    result = subprocess.run(
        ["git", "diff", "--stat", "main", "--", "docs/design/line-libraries/"],
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
