"""Layer 2 pre-generation safety classification helpers."""

from __future__ import annotations

import json
from typing import Any, Mapping

from pydantic import BaseModel, ConfigDict, Field

from engine.safety.l1 import extract_message_text

NEUTRAL_L2_BRIDGE = "The narrator redirects the moment back to the story."
L2_BLOCK_SENTINEL = "l2_safety_block"

_DEFAULT_POLICY_CONTEXT = {
    "permitted": [
        "murder mystery",
        "deception",
        "hidden motives",
        "dark social dynamics",
    ],
    "warnings": [
        "graphic descriptions of fictional violence",
        "explicit sexual content between adult characters",
    ],
    "prohibited": [
        "real-person targeting",
        "real-world harmful information outside the fictional frame",
        "sexual content involving anyone under 18",
    ],
}
_ALLOWED_CATEGORIES = frozenset(
    {
        "adult_sexual_content",
        "fictional_frame_break",
        "graphic_violence",
        "permitted",
        "prohibited",
        "real_person_targeting",
        "real_world_harm",
        "real_world_violence_instructions",
        "thematic_warning",
        "underage_sexual_content",
        "unknown",
    }
)


class SafetyClassificationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    blocked: bool
    confidence: float = Field(ge=0.0, le=1.0)
    category: str
    code: str


def build_l2_classification_messages(
    messages: list[dict[str, Any]],
    safety_policy_context: Mapping[str, Any] | str | None = None,
) -> list[dict[str, str]]:
    policy_context = _serialize_policy_context(safety_policy_context)
    prompt_text = extract_message_text(messages)

    return [
        {
            "role": "system",
            "content": (
                "You are Arcwright's Layer 2 safety classifier. "
                "Classify whether the generation request is prohibited by the "
                "policy context. Return only JSON with keys blocked, "
                "confidence, and category."
            ),
        },
        {
            "role": "user",
            "content": (
                "Policy context:\n"
                f"{policy_context}\n\n"
                "Generation request:\n"
                f"{prompt_text}"
            ),
        },
    ]


def parse_l2_classification(content: str) -> SafetyClassificationResult:
    data = _load_json_object(content)
    if data is None:
        return _classification_result(
            blocked=True,
            confidence=0.0,
            category="unknown",
        )

    blocked = _coerce_blocked(data)
    category = _coerce_category(data.get("category"), blocked=blocked)
    confidence = _coerce_confidence(data.get("confidence"))
    return _classification_result(
        blocked=blocked,
        confidence=confidence,
        category=category,
    )


def build_l2_classification_payload(
    result: SafetyClassificationResult,
) -> dict[str, Any]:
    return {
        "layer": "L2",
        "blocked": result.blocked,
        "confidence": result.confidence,
        "category": result.category,
        "code": result.code,
        "source": "generation_messages",
    }


def build_l2_blocked_route_result() -> Any:
    from engine.routing.router import RouteResult

    return RouteResult(
        content=NEUTRAL_L2_BRIDGE,
        model_used=L2_BLOCK_SENTINEL,
        input_tokens=0,
        output_tokens=0,
        latency_ms=0,
        used_fallback=False,
    )


def _serialize_policy_context(
    safety_policy_context: Mapping[str, Any] | str | None,
) -> str:
    if safety_policy_context is None:
        return json.dumps(_DEFAULT_POLICY_CONTEXT, sort_keys=True)
    if isinstance(safety_policy_context, str):
        return safety_policy_context
    return json.dumps(safety_policy_context, sort_keys=True, default=str)


def _load_json_object(content: str) -> dict[str, Any] | None:
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        start = content.find("{")
        end = content.rfind("}")
        if start == -1 or end == -1 or end <= start:
            return None
        try:
            parsed = json.loads(content[start : end + 1])
        except json.JSONDecodeError:
            return None
    if not isinstance(parsed, dict):
        return None
    return parsed


def _coerce_blocked(data: dict[str, Any]) -> bool:
    if "blocked" in data:
        return bool(data["blocked"])
    if "allowed" in data:
        return not bool(data["allowed"])
    return True


def _coerce_confidence(value: Any) -> float:
    try:
        confidence = float(value)
    except (TypeError, ValueError):
        return 0.0
    return max(0.0, min(confidence, 1.0))


def _coerce_category(value: Any, *, blocked: bool) -> str:
    if isinstance(value, str) and value in _ALLOWED_CATEGORIES:
        return value
    if blocked:
        return "prohibited"
    return "permitted"


def _classification_result(
    *,
    blocked: bool,
    confidence: float,
    category: str,
) -> SafetyClassificationResult:
    code = f"l2_{category}" if blocked else "l2_allowed"
    return SafetyClassificationResult(
        blocked=blocked,
        confidence=confidence,
        category=category,
        code=code,
    )
