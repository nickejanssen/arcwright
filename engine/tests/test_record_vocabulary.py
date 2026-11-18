"""No new game-specific word enters ``engine/`` (AW-304, spec 0093 Part F).

Two ratchets, both on non-test code under ``engine/``:

1. The count of the murder-mystery words listed in the inventory (spec 0092
   WP0, section 7) per engine module may not rise above what it is today. It
   may fall; lower the number here when it does.
2. Every saved event type and decision type that carries one of those words
   must be on a short list of the names that already existed. A new one fails.

The names on the list are tracked for renaming by AW-274 (issue #220).
"""

from __future__ import annotations

import ast
import re
from collections import Counter
from pathlib import Path

ENGINE = Path(__file__).resolve().parents[1]
WORDS = re.compile(
    r"suspect|accus|killer|murder|detective|culprit|clue|victim|contradict"
    r"|interrogat|nightcap",
    re.IGNORECASE,
)

BASELINE = {
    "arc": 21,
    "case": 184,
    "characters": 12,
    "claims": 23,
    "db": 19,
    "harness": 25,
    "mini_games": 143,
    "safety": 4,
    "scoring": 119,
    "session": 7,
    "telemetry": 25,
}

EXISTING_GAME_WORDED_NAMES = {
    "contradiction_",
    "accusation_submitted",
    "last_call_triggered",
    "mini_game_clue_delivery",
    "mini_game_clue_acknowledged",
}


def engine_sources() -> list[Path]:
    return [
        path
        for path in ENGINE.rglob("*.py")
        if "tests" not in path.relative_to(ENGINE).parts
        and "__pycache__" not in path.parts
    ]


def module_of(path: Path) -> str:
    parts = path.relative_to(ENGINE).parts
    return parts[0] if len(parts) > 1 else "(root)"


def test_game_word_counts_do_not_rise() -> None:
    counts: Counter[str] = Counter()
    for path in engine_sources():
        counts[module_of(path)] += len(WORDS.findall(path.read_text("utf-8")))
    risen = {
        module: (count, BASELINE.get(module, 0))
        for module, count in counts.items()
        if count > BASELINE.get(module, 0)
    }
    assert not risen, f"game words rose (now, allowed) in: {risen}"


def _string_parts(node: ast.AST) -> list[str]:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return [node.value]
    if isinstance(node, ast.JoinedStr):
        return [
            part.value
            for part in node.values
            if isinstance(part, ast.Constant) and isinstance(part.value, str)
        ]
    return []


def saved_type_names(tree: ast.AST) -> list[str]:
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.keyword) and node.arg in {
            "event_type",
            "decision_type",
        }:
            names += _string_parts(node.value)
        if isinstance(node, ast.Assign) and node.value is not None:
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id.endswith(
                    ("_EVENT", "_DECISION")
                ):
                    names += _string_parts(node.value)
    return names


def test_saved_event_and_decision_types_use_no_new_game_word() -> None:
    new: dict[str, list[str]] = {}
    for path in engine_sources():
        tree = ast.parse(path.read_text("utf-8"))
        for name in saved_type_names(tree):
            if WORDS.search(name) and name not in EXISTING_GAME_WORDED_NAMES:
                new.setdefault(str(path.relative_to(ENGINE)), []).append(name)
    assert not new, f"new game-worded saved names: {new}"


def test_the_detector_sees_a_planted_name() -> None:
    tree = ast.parse('Event(event_type="culprit_named")\nX_EVENT = f"killer_{y}"')
    found = saved_type_names(tree)
    assert "culprit_named" in found and "killer_" in found
