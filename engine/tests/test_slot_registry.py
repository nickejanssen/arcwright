from __future__ import annotations

import json
import re
from pathlib import Path

from engine.case import (
    AuthorizedFalsehood,
    CaseAnchor,
    CaseFact,
    CastMember,
    EvidenceEntry,
    ResolvedCase,
)
from engine.dressing.models import DressingPack

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

UNBUILT_SLOTS = {
    "count",
    "detective",
    "detective_name",
    "flavor",
    "habit",
    "minutes",
    "seconds",
}


CASE_MODEL_ATTRIBUTES = {
    attr
    for model in (
        AuthorizedFalsehood,
        CaseFact,
        CastMember,
        EvidenceEntry,
        ResolvedCase,
    )
    for attr in model.model_fields
}

ANCHOR_ATTRIBUTES = set(CaseAnchor.model_fields)
DRESSING_PACK_FIELDS = set(DressingPack.model_fields)

ATTRIBUTE_PATTERN = re.compile(r"\b([a-z_][a-z0-9_]*)\b")


def _load_registry() -> dict[str, object]:
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def _library_tokens() -> set[str]:
    token_pattern = re.compile(r"\{\{([a-z_0-9]+)\}\}")
    tokens: set[str] = set()
    for path in LIBRARY_DIR.glob("*.md"):
        tokens.update(token_pattern.findall(path.read_text(encoding="utf-8")))
    return tokens


def _detail_attributes(detail: str, candidates: set[str]) -> set[str]:
    return {match for match in ATTRIBUTE_PATTERN.findall(detail) if match in candidates}


def test_registry_slots_all_have_sources() -> None:
    registry = _load_registry()

    assert set(registry["source_vocab"]) == ALLOWED_SOURCES

    for slot_name, slot_entry in registry["slots"].items():
        assert slot_entry["source"], f"{slot_name} has no source"
        assert slot_entry["source"] in ALLOWED_SOURCES, (
            f"{slot_name} has unknown source {slot_entry['source']}"
        )

    assert registry["slots"]["occasion"]["source"] == "session"


def test_case_anchor_slots_map_to_real_anchor_attributes() -> None:
    registry = _load_registry()

    for slot_name, slot_entry in registry["slots"].items():
        if slot_entry["source"] != "case_anchor":
            continue

        attrs = _detail_attributes(slot_entry["detail"], ANCHOR_ATTRIBUTES)
        assert attrs, (
            f"{slot_name} claims {slot_entry['detail']!r} but it does not name any "
            "real CaseAnchor attribute"
        )


def test_case_field_slots_map_to_real_case_model_attributes() -> None:
    registry = _load_registry()

    for slot_name, slot_entry in registry["slots"].items():
        if slot_entry["source"] != "case_field":
            continue

        attrs = _detail_attributes(slot_entry["detail"], CASE_MODEL_ATTRIBUTES)
        assert attrs, (
            f"{slot_name} claims {slot_entry['detail']!r} but it does not name any "
            "real case model attribute"
        )


def test_dressing_pack_slots_map_to_real_fields_or_wrapper_scope() -> None:
    registry = _load_registry()

    for slot_name, slot_entry in registry["slots"].items():
        if slot_entry["source"] != "dressing_pack":
            continue

        attrs = _detail_attributes(slot_entry.get("detail", ""), DRESSING_PACK_FIELDS)
        if attrs:
            continue

        wrappers = slot_entry.get("wrappers")
        assert wrappers, (
            f"{slot_name} has no DressingPack field in {slot_entry.get('detail')!r} "
            "and no explicit wrapper-scoped exception"
        )


def test_declared_but_unbuilt_sources_are_exhaustive() -> None:
    registry = _load_registry()

    unbuilt = {
        slot_name
        for slot_name, slot_entry in registry["slots"].items()
        if slot_entry["source"] in {"identity_aw279", "session_timer", "scoring"}
    }

    assert unbuilt == UNBUILT_SLOTS


def test_registry_matches_authored_token_inventory() -> None:
    registry = _load_registry()
    registry_slots = set(registry["slots"])
    authored_slots = _library_tokens() - EXCLUDED_SLOTS

    assert registry_slots == EXPECTED_SLOTS
    assert registry_slots == authored_slots
