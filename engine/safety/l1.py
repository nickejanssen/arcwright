"""Deterministic Layer 1 safety hard stops."""

from __future__ import annotations

import re
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict

NEUTRAL_L1_BRIDGE = "The narrator redirects the moment back to the story."
L1_HARD_STOP_SENTINEL = "l1_hard_stop"


class SafetyHardStopCategory(str, Enum):
    underage_sexual_content = "underage_sexual_content"
    real_person_harm_targeting = "real_person_harm_targeting"
    real_world_violence_instructions = "real_world_violence_instructions"
    real_world_harm_facilitation = "real_world_harm_facilitation"


class SafetyHardStopResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    category: SafetyHardStopCategory
    code: str


_TOKEN_WINDOW = 8

_UNDER_18_TERMS = frozenset(
    {
        "minor",
        "underage",
        "child",
        "kid",
        "infant",
        "baby",
        "toddler",
        "preteen",
        "adolescent",
        "teen",
        "teenager",
        "schoolgirl",
        "schoolboy",
    }
)
_UNDER_18_PHRASES = (
    tuple(f"{age} year old" for age in range(18))
    + tuple(f"{age} years old" for age in range(18))
    + (
        "under 18",
        "under eighteen",
    )
)
_SEXUAL_CONTENT_TERMS = frozenset(
    {
        "sexual",
        "sex",
        "erotic",
        "nude",
        "naked",
        "porn",
        "explicit",
        "intercourse",
    }
)
_CSAM_PHRASES = ("csam", "child sexual abuse material")

_REAL_PERSON_PHRASES = (
    "real person",
    "living person",
    "named person",
    "public figure",
    "actual person",
    "irl person",
    "in real life",
)
_REAL_WORLD_MARKERS = ("real life", "irl", "actual person", "living person")
_HARMFUL_ACTION_TERMS = frozenset(
    {
        "hurt",
        "harm",
        "attack",
        "kill",
        "threaten",
        "harass",
        "blackmail",
        "dox",
        "stalk",
    }
)

_INSTRUCTION_PHRASES = (
    "how to",
    "step by step",
    "teach me",
    "guide me",
    "walk me through",
    "recipe for",
)
_INSTRUCTION_TERMS = frozenset({"instructions", "build", "make"})
_WEAPON_ATTACK_TERMS = frozenset(
    {
        "bomb",
        "explosive",
        "gun",
        "firearm",
        "weapon",
        "poison",
        "toxin",
        "attack",
    }
)
_WEAPON_ATTACK_PHRASES = ("pipe bomb",)

_FACILITATION_PHRASES = (
    "help me",
    "how can i",
    "how do i",
    "tips for",
    "plan to",
    "avoid getting caught",
    "without getting caught",
    "hide evidence",
    "cover up",
)
_FACILITATION_TERMS = frozenset({"evade"})
_OPERATIONAL_HARM_TERMS = frozenset(
    {
        "stalk",
        "dox",
        "blackmail",
        "extort",
        "coerce",
        "swat",
        "suicide",
    }
)
_OPERATIONAL_HARM_PHRASES = (
    "self harm",
    "evade police",
    "bypass security",
)
_FICTIONAL_FRAME_TERMS = frozenset(
    {
        "fictional",
        "character",
        "villain",
        "suspect",
        "nightcap",
        "arc",
        "scene",
    }
)
_FICTIONAL_FRAME_PHRASES = (
    "in game",
    "in story",
    "murder mystery",
)

_NAME_SHAPED_PHRASE = re.compile(r"\b[A-Z][a-z]+ [A-Z][a-z]+\b")
_LOWERCASE_NAMED_PERSON_PHRASE = re.compile(r"\bnamed\s+[a-z][a-z]+ [a-z][a-z]+\b")
_LOWERCASE_MARKER_PERSON_PHRASE = re.compile(
    r"\b(?:real person|living person|public figure|actual person|irl person)"
    r"\s+[a-z][a-z]+ [a-z][a-z]+\b"
)


def normalize_text(text: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", " ", text.lower())
    return re.sub(r"\s+", " ", normalized).strip()


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z0-9]+", normalize_text(text))


def extract_message_text(messages: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for message in messages:
        parts.extend(_extract_content_text(message.get("content")))
    return "\n".join(parts)


def _extract_content_text(content: Any) -> list[str]:
    if isinstance(content, str):
        return [content]
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            parts.extend(_extract_text_block(item))
        return parts
    return []


def _extract_text_block(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        parts: list[str] = []
        for item in value:
            parts.extend(_extract_text_block(item))
        return parts
    if isinstance(value, dict):
        parts: list[str] = []
        for key in ("text", "content"):
            if key in value:
                parts.extend(_extract_text_block(value[key]))
        return parts
    return []


def evaluate_l1_hard_stops(
    messages: list[dict[str, Any]],
) -> SafetyHardStopResult | None:
    raw_text = extract_message_text(messages)
    normalized = normalize_text(raw_text)
    tokens = tokenize(raw_text)

    if _matches_underage_sexual_content(normalized, tokens):
        return _result(SafetyHardStopCategory.underage_sexual_content)
    if _matches_real_person_harm_targeting(raw_text, normalized, tokens):
        return _result(SafetyHardStopCategory.real_person_harm_targeting)
    if _matches_real_world_violence_instructions(normalized, tokens):
        return _result(SafetyHardStopCategory.real_world_violence_instructions)
    if _matches_real_world_harm_facilitation(normalized, tokens):
        return _result(SafetyHardStopCategory.real_world_harm_facilitation)
    return None


def build_safety_hard_stop_payload(result: SafetyHardStopResult) -> dict[str, Any]:
    return {
        "layer": "L1",
        "category": result.category.value,
        "code": result.code,
        "source": "generation_messages",
        "blocked": True,
    }


def build_l1_hard_stop_route_result() -> Any:
    from engine.routing.router import RouteResult

    return RouteResult(
        content=NEUTRAL_L1_BRIDGE,
        model_used=L1_HARD_STOP_SENTINEL,
        input_tokens=0,
        output_tokens=0,
        latency_ms=0,
        used_fallback=False,
    )


def _result(category: SafetyHardStopCategory) -> SafetyHardStopResult:
    return SafetyHardStopResult(
        category=category,
        code=f"l1_{category.value}",
    )


def _matches_underage_sexual_content(
    normalized: str,
    tokens: list[str],
) -> bool:
    if any(phrase in normalized for phrase in _CSAM_PHRASES):
        return True
    under_18_terms = set(_UNDER_18_TERMS)
    under_18_terms.update(_phrase_terms(normalized, _UNDER_18_PHRASES))
    return _terms_near(tokens, _SEXUAL_CONTENT_TERMS, under_18_terms)


def _matches_real_person_harm_targeting(
    raw_text: str,
    normalized: str,
    tokens: list[str],
) -> bool:
    if not any(phrase in normalized for phrase in _REAL_PERSON_PHRASES):
        return False
    if not _has_person_name_shape(raw_text, normalized):
        return False
    marker_terms = _phrase_terms(normalized, _REAL_PERSON_PHRASES)
    return _terms_near(tokens, _HARMFUL_ACTION_TERMS, marker_terms)


def _has_person_name_shape(raw_text: str, normalized: str) -> bool:
    return bool(
        _NAME_SHAPED_PHRASE.search(raw_text)
        or _LOWERCASE_NAMED_PERSON_PHRASE.search(normalized)
        or _LOWERCASE_MARKER_PERSON_PHRASE.search(normalized)
    )


def _matches_real_world_violence_instructions(
    normalized: str,
    tokens: list[str],
) -> bool:
    instruction_terms = set(_INSTRUCTION_TERMS)
    instruction_terms.update(_phrase_terms(normalized, _INSTRUCTION_PHRASES))
    weapon_terms = set(_WEAPON_ATTACK_TERMS)
    weapon_terms.update(_phrase_terms(normalized, _WEAPON_ATTACK_PHRASES))
    return _terms_near(tokens, instruction_terms, weapon_terms)


def _matches_real_world_harm_facilitation(
    normalized: str,
    tokens: list[str],
) -> bool:
    facilitation_terms = set(_FACILITATION_TERMS)
    facilitation_terms.update(_phrase_terms(normalized, _FACILITATION_PHRASES))
    harm_terms = set(_OPERATIONAL_HARM_TERMS)
    harm_terms.update(_phrase_terms(normalized, _OPERATIONAL_HARM_PHRASES))
    if not _terms_near(tokens, facilitation_terms, harm_terms):
        return False
    if any(phrase in normalized for phrase in _REAL_WORLD_MARKERS):
        return True
    fictional_terms = set(_FICTIONAL_FRAME_TERMS)
    fictional_terms.update(_phrase_terms(normalized, _FICTIONAL_FRAME_PHRASES))
    return not _terms_near(tokens, harm_terms, fictional_terms)


def _phrase_terms(normalized: str, phrases: tuple[str, ...]) -> set[str]:
    terms: set[str] = set()
    for phrase in phrases:
        normalized_phrase = normalize_text(phrase)
        if normalized_phrase in normalized:
            terms.update(normalized_phrase.split())
    return terms


def _terms_near(
    tokens: list[str],
    left_terms: set[str] | frozenset[str],
    right_terms: set[str] | frozenset[str],
) -> bool:
    left_indexes = [idx for idx, token in enumerate(tokens) if token in left_terms]
    right_indexes = [idx for idx, token in enumerate(tokens) if token in right_terms]
    return any(
        abs(left_idx - right_idx) <= _TOKEN_WINDOW
        for left_idx in left_indexes
        for right_idx in right_indexes
    )
