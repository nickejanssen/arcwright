"""Static guard that engine/case stays free of wrapper-dressing vocabulary.

Field-name policy (AW-290 / spec 0087): ``engine/case`` is arc-agnostic
domain code shared by every wrapper (Nightcap, and future wrappers). Its
schemas must never hardcode a specific wrapper's *dressing* -- the per-wrapper
aesthetic flavor layered on top of a case at presentation time (what a drink
is called, a stage name, a room's decor tier, ambient weather, which floor an
event happens on, an in-fiction errata note, wrapper-specific narration
framing, or the "seance"/"bigtop"/"nightcap" wrapper names themselves). That
dressing vocabulary is AW-293 scope and belongs in a wrapper's own dressing
pack, not in `engine/case` field or identifier names.

This list is deliberately NARROWER than
``engine/tests/test_claims_naming_contract.py``'s forbidden list. The claims
contract forbids murder-mystery-*genre* vocabulary (``suspect``, ``victim``,
``culprit``, ``detective``, ``murder``, ``crime``) from appearing in claims
identifiers at all, because claims text is meant to be fully game-agnostic
prose. ``engine/case`` is different: it already legitimately encodes
structural/mechanical case-resolution concepts as field names -- for example
``ResolvedCase.culprit_id`` and ``CastMember.is_culprit`` name *which cast
member did it*, a mechanical fact about case resolution, not genre flavor.
Genre words describing *why* something happened or *what kind* of person is
involved are meant to live inside string values (``role="suspect"``), per the
module docstring in ``engine/case/models.py``. Only wrapper *dressing*
vocabulary is banned from `engine/case` identifiers outright, because unlike
genre words, dressing has no legitimate structural use in this module at
all -- it is always presentation content owned by a specific wrapper.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

ENGINE_DIR = Path(__file__).resolve().parent.parent
CASE_DIR = ENGINE_DIR / "case"

FORBIDDEN_TERMS = [
    "drink",
    "stage_name",
    "tier",
    "room",
    "weather",
    "floor",
    "errata",
    "wrapper",
    "seance",
    "bigtop",
    "nightcap",
]

_WORD_RE = re.compile(r"[A-Z][a-z0-9]*|[a-z0-9]+|[A-Z]+(?![a-z])")


def _tokenize(identifier: str) -> list[str]:
    """Split an identifier into lowercase word tokens on `_` and case boundaries.

    Token-based, not substring, matching: this is what keeps a forbidden
    term like "tier" or "room" from false-positiving on an unrelated
    identifier that merely contains those letters (e.g. "frontier",
    "groom") -- the term must appear as a whole token, or contiguous
    sequence of tokens for multi-word terms like "stage_name".
    """
    tokens: list[str] = []
    for part in identifier.split("_"):
        tokens.extend(match.group(0).lower() for match in _WORD_RE.finditer(part))
    return tokens


def _contains_subsequence(tokens: list[str], sub: list[str]) -> bool:
    span = len(sub)
    return any(tokens[i : i + span] == sub for i in range(len(tokens) - span + 1))


def _case_files() -> list[Path]:
    files = sorted(CASE_DIR.glob("*.py"))
    assert files, f"expected to find .py files under {CASE_DIR}"
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


@pytest.mark.parametrize("path", _case_files(), ids=lambda p: p.name)
def test_no_wrapper_dressing_identifier_names_in_case_modules(path: Path) -> None:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    forbidden_token_sequences = [term.split("_") for term in FORBIDDEN_TERMS]
    violations = [
        f"identifier {identifier!r} contains {term!r}"
        for identifier in _identifier_names(tree)
        for term, term_tokens in zip(FORBIDDEN_TERMS, forbidden_token_sequences)
        if _contains_subsequence(_tokenize(identifier), term_tokens)
    ]

    assert not violations, (
        f"{path}: forbidden wrapper-dressing identifier(s): {violations}"
    )
