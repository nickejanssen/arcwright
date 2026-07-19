"""Static guard that claims code stays game and character agnostic."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

ENGINE_DIR = Path(__file__).resolve().parent.parent
CLAIMS_DIR = ENGINE_DIR / "claims"
TELEMETRY_CLAIMS_FILE = ENGINE_DIR / "telemetry" / "claims.py"

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
    "suspect",
    "murder",
    "victim",
    "culprit",
    "detective",
    "crime",
]


def _normalize(text: str) -> str:
    return text.replace("_", "").lower()


def _claim_files() -> list[Path]:
    files = sorted(CLAIMS_DIR.glob("*.py"))
    assert files, f"expected to find .py files under {CLAIMS_DIR}"
    assert TELEMETRY_CLAIMS_FILE.exists(), f"expected to find {TELEMETRY_CLAIMS_FILE}"
    files.append(TELEMETRY_CLAIMS_FILE)
    return files


def _identifier_names(tree: ast.AST) -> list[str]:
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
            names.append(node.name)
            if node.asname:
                names.append(node.asname)
        elif isinstance(node, ast.keyword) and node.arg is not None:
            names.append(node.arg)
    return names


@pytest.mark.parametrize("path", _claim_files(), ids=lambda p: p.name)
def test_no_game_specific_identifier_names_in_claims_modules(path: Path) -> None:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    normalized_forbidden = [_normalize(term) for term in FORBIDDEN_TERMS]
    violations = [
        f"identifier {identifier!r} contains {term!r}"
        for identifier in _identifier_names(tree)
        for term, normalized in zip(FORBIDDEN_TERMS, normalized_forbidden)
        if normalized in _normalize(identifier)
    ]

    assert not violations, (
        f"{path}: forbidden game-specific identifier(s): {violations}"
    )
