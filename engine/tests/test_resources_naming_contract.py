"""Repo-wide static check: no Nightcap-specific effect/resource name, character
name, or the game name itself may leak into an engine/resources/ (or
engine/telemetry/resources.py) Python identifier.

engine/ is game-agnostic platform code (see AGENTS.md, "Architecture Principles" /
"Configurable composition"). Nightcap's specific advantage/sabotage names (Leverage,
Deep Read, Follow the Thread, Sting Operation, Rattle the Witness, Listen In, Make
Them Wait), its cast's character names (Priya, Marcus, Jordan, Zoe), and the literal
game name "nightcap" are all arc-configuration/content data, not engine vocabulary.
They may appear as *string values* inside engine/resources/ or
engine/telemetry/resources.py (e.g. an effect_key literal used in a docstring
example or test fixture elsewhere), but must never appear inside an actual Python
identifier (function/class/variable/attribute/argument name) in either module. This
test parses every engine/resources/*.py file plus engine/telemetry/resources.py
with `ast` and fails on any identifier that contains a forbidden term, so it stays
broken until the leak is fixed even if someone quietly reintroduces the term later.

Scope is deliberately limited to engine/resources/ and engine/telemetry/resources.py
(not the whole engine/ tree): other engine/tests/*.py files legitimately reference
"nightcap" and its cast's names as string fixture data (and, in a few pre-existing,
unrelated test names, as identifiers — e.g. test_nightcap_arc_json_validates) when
exercising the canonical Nightcap arc as a generic test fixture. That is a separate,
pre-existing pattern outside AW-287's scope, not the class of leak this test guards
against.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

ENGINE_DIR = Path(__file__).resolve().parent.parent
RESOURCES_DIR = ENGINE_DIR / "resources"
TELEMETRY_RESOURCES_FILE = ENGINE_DIR / "telemetry" / "resources.py"

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


def _resource_files() -> list[Path]:
    files = sorted(RESOURCES_DIR.glob("*.py"))
    assert files, f"expected to find .py files under {RESOURCES_DIR}"
    assert TELEMETRY_RESOURCES_FILE.exists(), (
        f"expected to find {TELEMETRY_RESOURCES_FILE}"
    )
    files.append(TELEMETRY_RESOURCES_FILE)
    return files


def _identifier_names(tree: ast.AST) -> list[str]:
    """Collect every function/class/variable/attribute/argument identifier in the
    tree. Deliberately does NOT look at ast.Constant/string literal values — those
    are data, not identifiers, and are explicitly allowed to carry Nightcap-specific
    names (e.g. effect_key="advantage.deep_read").
    """
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


@pytest.mark.parametrize("path", _resource_files(), ids=lambda p: p.name)
def test_no_forbidden_identifier_names_in_resources_module(path: Path) -> None:
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
        f"{path}: found Nightcap-specific term(s) in engine/resources/ identifiers: "
        f"{violations}"
    )
