"""Provider-agnostic routing helpers for LLM-backed generation."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List, Optional

import litellm
import structlog

ROUTING_TABLE_PATH = (
    Path(__file__).resolve().parents[2] / "config" / "routing_table.json"
)
_ROUTING_TABLE: Dict[str, Dict[str, str]] = json.loads(ROUTING_TABLE_PATH.read_text())

# MVP cost rates — update only when provider pricing changes.
# All values are USD per token. Model keys must exactly match routing_table.json.
_COST_RATES: Dict[str, tuple[float, float]] = {
    # key: (cost_per_input_token, cost_per_output_token)
    "anthropic/claude-haiku-4-5-20251001": (0.00000025, 0.00000125),
    "anthropic/claude-sonnet-4-6": (0.000003, 0.000015),
    "groq/llama-3.1-8b-instant": (0.00000005, 0.00000008),
    "groq/llama-3.3-70b-versatile": (0.00000059, 0.00000079),
    "groq/gpt-oss-safeguard-20b": (0.00000020, 0.00000020),
}


@dataclass(frozen=True)
class RouteResult:
    content: str
    model_used: str
    input_tokens: int
    output_tokens: int
    latency_ms: int
    used_fallback: bool


_MIN_COST = Decimal("0.000001")


def compute_cost(model_used: str, input_tokens: int, output_tokens: int) -> Decimal:
    rates = _COST_RATES.get(model_used)
    if rates is None:
        raise ValueError(
            f"unknown model cost: {model_used!r} — add it to _COST_RATES in router.py"
        )
    raw = rates[0] * input_tokens + rates[1] * output_tokens
    quantized = Decimal(str(raw)).quantize(_MIN_COST)
    # Clamp sub-precision positive costs to the minimum representable value so
    # small pacing/safety calls don't appear free in per-session cost rollups.
    if raw > 0 and quantized == Decimal("0"):
        return _MIN_COST
    return quantized


def mark_stable_context_cacheable(
    messages: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Return a new list with the system message wrapped in Anthropic cache_control."""
    if not messages:
        return messages
    first = messages[0]
    if first.get("role") != "system" or not isinstance(first.get("content"), str):
        return messages
    new_first: Dict[str, Any] = dict(first)
    new_first["content"] = [
        {
            "type": "text",
            "text": first["content"],
            "cache_control": {"type": "ephemeral"},
        }
    ]
    return [new_first] + list(messages[1:])


def load_routing_table() -> Dict[str, Dict[str, str]]:
    return _ROUTING_TABLE


def resolve_model_key(task_type: str, quality_tier: str) -> str:
    routing_table = load_routing_table()
    return routing_table[task_type][quality_tier]


def resolve_fallback_model_key(task_type: str, quality_tier: str) -> Optional[str]:
    routing_table = load_routing_table()
    return routing_table[task_type].get(f"{quality_tier}_fallback")


async def _complete_with_model(
    model_key: str,
    messages: List[Dict[str, Any]],
    temperature: float,
) -> tuple[Any, int]:
    start = time.perf_counter()
    response = await litellm.acompletion(
        model=model_key,
        messages=messages,
        temperature=temperature,
    )
    end = time.perf_counter()
    return response, int((end - start) * 1000)


async def route_generation(
    task_type: str,
    quality_tier: str,
    messages: List[Dict[str, Any]],
    temperature: float = 0.7,
) -> RouteResult:
    cacheable_messages = mark_stable_context_cacheable(messages)
    model_key = resolve_model_key(task_type, quality_tier)
    fallback_key = resolve_fallback_model_key(task_type, quality_tier)

    try:
        response, latency_ms = await _complete_with_model(
            model_key=model_key,
            messages=cacheable_messages,
            temperature=temperature,
        )
        model_used = model_key
        used_fallback = False
    except Exception:
        if not fallback_key:
            raise
        response, latency_ms = await _complete_with_model(
            model_key=fallback_key,
            messages=cacheable_messages,
            temperature=temperature,
        )
        model_used = fallback_key
        used_fallback = True

    structlog.get_logger().debug(
        "route_generation_complete",
        task_type=task_type,
        quality_tier=quality_tier,
        model_used=model_used,
        used_fallback=used_fallback,
        latency_ms=latency_ms,
    )

    return RouteResult(
        content=response.choices[0].message.content,
        model_used=model_used,
        input_tokens=response.usage.prompt_tokens,
        output_tokens=response.usage.completion_tokens,
        latency_ms=latency_ms,
        used_fallback=used_fallback,
    )
