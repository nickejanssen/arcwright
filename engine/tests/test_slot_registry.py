from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = REPO_ROOT / "nightcap" / "content" / "slot_registry.json"
LIBRARY_DIR = REPO_ROOT / "docs" / "design" / "line-libraries"

EXCLUDED_SLOTS = {
    "complication_object",
    "flavor_clause",
    "slot",
    "suspect_3",
    "time_1",
    "time_2",
    "time_3",
}

ALLOWED_SOURCES = {
    "case_anchor",
    "case_field",
    "dressing_pack",
    "identity_aw279",
    "scoring",
    "session",
    "session_timer",
}

EXPECTED_SLOTS = {
    "callback",
    "count",
    "deck",
    "detective",
    "detective_name",
    "drink",
    "evidence",
    "errata",
    "floor",
    "flavor",
    "habit",
    "killer",
    "location",
    "minutes",
    "occasion",
    "room",
    "seconds",
    "stage_name",
    "suspect",
    "suspect_2",
    "tier",
    "title",
    "time",
    "victim",
    "weather",
}


def _load_registry() -> dict[str, object]:
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def _library_tokens() -> set[str]:
    token_pattern = re.compile(r"\{\{([a-z_0-9]+)\}\}")
    tokens: set[str] = set()
    for path in LIBRARY_DIR.glob("*.md"):
        tokens.update(token_pattern.findall(path.read_text(encoding="utf-8")))
    return tokens


def test_registry_slots_all_have_sources() -> None:
    registry = _load_registry()

    assert set(registry["source_vocab"]) == ALLOWED_SOURCES

    for slot_name, slot_entry in registry["slots"].items():
        assert slot_entry["source"], f"{slot_name} has no source"
        assert slot_entry["source"] in ALLOWED_SOURCES, (
            f"{slot_name} has unknown source {slot_entry['source']}"
        )

    assert registry["slots"]["occasion"]["source"] == "session"


def test_registry_matches_authored_token_inventory() -> None:
    registry = _load_registry()
    registry_slots = set(registry["slots"])
    authored_slots = _library_tokens() - EXCLUDED_SLOTS

    assert registry_slots == EXPECTED_SLOTS
    assert registry_slots == authored_slots
