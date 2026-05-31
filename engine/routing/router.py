"""Provider-agnostic routing helpers for LLM-backed generation."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import litellm

ROUTING_TABLE_PATH = (
    Path(__file__).resolve().parents[2] / "config" / "routing_table.json"
)
_ROUTING_TABLE: Dict[str, Dict[str, str]] = json.loads(ROUTING_TABLE_PATH.read_text())


@dataclass(frozen=True)
class RouteResult:
    content: str
    model_used: str
    input_tokens: int
    output_tokens: int
    latency_ms: int
    used_fallback: bool


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
    model_key = resolve_model_key(task_type, quality_tier)
    fallback_key = resolve_fallback_model_key(task_type, quality_tier)

    try:
        response, latency_ms = await _complete_with_model(
            model_key=model_key,
            messages=messages,
            temperature=temperature,
        )
        model_used = model_key
        used_fallback = False
    except Exception:
        if not fallback_key:
            raise
        response, latency_ms = await _complete_with_model(
            model_key=fallback_key,
            messages=messages,
            temperature=temperature,
        )
        model_used = fallback_key
        used_fallback = True

    return RouteResult(
        content=response.choices[0].message.content,
        model_used=model_used,
        input_tokens=response.usage.prompt_tokens,
        output_tokens=response.usage.completion_tokens,
        latency_ms=latency_ms,
        used_fallback=used_fallback,
    )
