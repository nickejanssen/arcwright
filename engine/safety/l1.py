"""Deterministic Layer 1 safety hard stops."""

from __future__ import annotations

import re
from enum import Enum
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    from engine.arc.models import ContentRailsConfig
    from engine.routing.router import RouteResult

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
        "arc",
        "scene",
    }
)
_FICTIONAL_FRAME_PHRASES = (
    "in game",
    "in story",
    "murder mystery",
)

# Arc-supplied fictional-frame vocabulary (content_rails.fictional_frame_terms)
# can only be single alphabetic tokens of four or more characters, and never
# a word the harm detectors key on. This keeps the arc's ability limited to
# marking its own game vocabulary as fiction; it cannot blunt the detectors
# themselves. Safety stays engine-enforced per AGENTS.md.
_ARC_FRAME_TERM_PATTERN = re.compile(r"^[a-z]{4,}$")

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
        list_parts: list[str] = []
        for item in value:
            list_parts.extend(_extract_text_block(item))
        return list_parts
    if isinstance(value, dict):
        dict_parts: list[str] = []
        for key in ("text", "content"):
            if key in value:
                dict_parts.extend(_extract_text_block(value[key]))
        return dict_parts
    return []


def evaluate_l1_hard_stops(
    messages: list[dict[str, Any]],
    content_rails: "ContentRailsConfig | None" = None,
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
    if _matches_real_world_harm_facilitation(
        normalized, tokens, arc_frame_terms=_arc_fictional_frame_terms(content_rails)
    ):
        return _result(SafetyHardStopCategory.real_world_harm_facilitation)
    return None


def _arc_fictional_frame_terms(
    content_rails: "ContentRailsConfig | None",
) -> frozenset[str]:
    """Return the arc's admissible fictional-frame vocabulary.

    Terms that fail the guard (multi-word, too short, non-alphabetic, or a
    word the harm detectors key on) are silently dropped: an arc can mark
    its own game vocabulary as fiction, never weaken the detectors.
    """
    if content_rails is None or not content_rails.fictional_frame_terms:
        return frozenset()
    guarded = (
        _HARMFUL_ACTION_TERMS
        | _OPERATIONAL_HARM_TERMS
        | _FACILITATION_TERMS
        | _INSTRUCTION_TERMS
        | _WEAPON_ATTACK_TERMS
        | _SEXUAL_CONTENT_TERMS
        | _UNDER_18_TERMS
    )
    admissible = set()
    for term in content_rails.fictional_frame_terms:
        normalized_term = normalize_text(term)
        if _ARC_FRAME_TERM_PATTERN.match(normalized_term) and (
            normalized_term not in guarded
        ):
            admissible.add(normalized_term)
    return frozenset(admissible)


def build_safety_hard_stop_payload(result: SafetyHardStopResult) -> dict[str, Any]:
    return {
        "layer": "L1",
        "category": result.category.value,
        "code": result.code,
        "source": "generation_messages",
        "blocked": True,
    }


def build_l1_hard_stop_route_result() -> "RouteResult":
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
    sexual_indexes = _indicator_indexes(tokens, terms=_SEXUAL_CONTENT_TERMS)
    under_18_indexes = _indicator_indexes(
        tokens,
        terms=_UNDER_18_TERMS,
        phrases=_UNDER_18_PHRASES,
    )
    return _indexes_near(sexual_indexes, under_18_indexes)


def _matches_real_person_harm_targeting(
    raw_text: str,
    normalized: str,
    tokens: list[str],
) -> bool:
    if not any(phrase in normalized for phrase in _REAL_PERSON_PHRASES):
        return False
    if not _has_person_name_shape(raw_text, normalized):
        return False
    harmful_indexes = _indicator_indexes(tokens, terms=_HARMFUL_ACTION_TERMS)
    marker_indexes = _indicator_indexes(tokens, phrases=_REAL_PERSON_PHRASES)
    return _indexes_near(harmful_indexes, marker_indexes)


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
    instruction_indexes = _indicator_indexes(
        tokens,
        terms=_INSTRUCTION_TERMS,
        phrases=_INSTRUCTION_PHRASES,
    )
    weapon_indexes = _indicator_indexes(
        tokens,
        terms=_WEAPON_ATTACK_TERMS,
        phrases=_WEAPON_ATTACK_PHRASES,
    )
    return _indexes_near(instruction_indexes, weapon_indexes)


def _matches_real_world_harm_facilitation(
    normalized: str,
    tokens: list[str],
    *,
    arc_frame_terms: frozenset[str] = frozenset(),
) -> bool:
    facilitation_indexes = _indicator_indexes(
        tokens,
        terms=_FACILITATION_TERMS,
        phrases=_FACILITATION_PHRASES,
    )
    harm_indexes = _indicator_indexes(
        tokens,
        terms=_OPERATIONAL_HARM_TERMS,
        phrases=_OPERATIONAL_HARM_PHRASES,
    )
    if not _indexes_near(facilitation_indexes, harm_indexes):
        return False
    if any(phrase in normalized for phrase in _REAL_WORLD_MARKERS):
        return True
    fictional_indexes = _indicator_indexes(
        tokens,
        terms=_FICTIONAL_FRAME_TERMS | arc_frame_terms,
        phrases=_FICTIONAL_FRAME_PHRASES,
    )
    return not _indexes_near(harm_indexes, fictional_indexes)


def _indicator_indexes(
    tokens: list[str],
    *,
    terms: set[str] | frozenset[str] = frozenset(),
    phrases: tuple[str, ...] = (),
) -> list[int]:
    indexes = [idx for idx, token in enumerate(tokens) if token in terms]
    indexes.extend(_phrase_indexes(tokens, phrases))
    return indexes


def _phrase_indexes(tokens: list[str], phrases: tuple[str, ...]) -> list[int]:
    indexes: list[int] = []
    for phrase in phrases:
        phrase_tokens = tokenize(phrase)
        if not phrase_tokens:
            continue
        phrase_length = len(phrase_tokens)
        for start_idx in range(len(tokens) - phrase_length + 1):
            end_idx = start_idx + phrase_length
            if tokens[start_idx:end_idx] == phrase_tokens:
                indexes.extend(range(start_idx, end_idx))
    return indexes


def _indexes_near(left_indexes: list[int], right_indexes: list[int]) -> bool:
    return any(
        abs(left_idx - right_idx) <= _TOKEN_WINDOW
        for left_idx in left_indexes
        for right_idx in right_indexes
    )
