"""Static check that scoring engine identifiers stay game-agnostic.

Arc-specific vocabulary belongs in arc configuration and content data.  This
test keeps the scoring implementation and its telemetry module aligned with
the generic engine naming contract while allowing string values to carry
content identifiers.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

ENGINE_DIR = Path(__file__).resolve().parent.parent
SCORING_DIR = ENGINE_DIR / "scoring"
TELEMETRY_SCORING_FILE = ENGINE_DIR / "telemetry" / "scoring.py"

FORBIDDEN_TERMS = [
    "leverage",
    "deep_read",
    "follow_the_thread",
    "sting_operation",
    "rattle_the_witness",
    "listen_in",
    "make_them_wait",
    "priya",
    "marcus",
    "jordan",
    "zoe",
    "nightcap",
]


def _normalize(text: str) -> str:
    return text.replace("_", "").lower()


NORMALIZED_FORBIDDEN_TERMS = [_normalize(term) for term in FORBIDDEN_TERMS]


def _scoring_files() -> list[Path]:
    files = sorted(SCORING_DIR.glob("*.py"))
    assert files, f"expected to find .py files under {SCORING_DIR}"
    assert TELEMETRY_SCORING_FILE.exists(), f"expected to find {TELEMETRY_SCORING_FILE}"
    files.append(TELEMETRY_SCORING_FILE)
    return files


def _identifier_names(tree: ast.AST) -> list[str]:
    """Collect identifiers without treating string literals as vocabulary."""
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.append(node.name)
        elif isinstance(node, ast.Name):
            names.append(node.id)
        elif isinstance(node, ast.Attribute):
            names.append(node.attr)
        elif isinstance(node, ast.arg):
            names.append(node.arg)
        elif isinstance(node, (ast.Global, ast.Nonlocal)):
            names.extend(node.names)
        elif isinstance(node, ast.alias):
            if node.asname:
                names.append(node.asname)
            names.append(node.name)
        elif isinstance(node, ast.keyword) and node.arg is not None:
            names.append(node.arg)
    return names


@pytest.mark.parametrize("path", _scoring_files(), ids=lambda path: path.name)
def test_no_forbidden_identifier_names_in_scoring_modules(path: Path) -> None:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))

    violations: list[str] = []
    for identifier in _identifier_names(tree):
        normalized = _normalize(identifier)
        for forbidden, normalized_forbidden in zip(
            FORBIDDEN_TERMS, NORMALIZED_FORBIDDEN_TERMS
        ):
            if normalized_forbidden in normalized:
                violations.append(f"identifier {identifier!r} contains {forbidden!r}")

    assert not violations, (
        f"{path}: found arc-specific term(s) in scoring identifiers: {violations}"
    )
