"""Provider-agnostic routing helpers for LLM-backed generation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import litellm

ROUTING_TABLE_PATH = (
    Path(__file__).resolve().parents[2] / "config" / "routing_table.json"
)


def load_routing_table() -> Dict[str, Dict[str, str]]:
    return json.loads(ROUTING_TABLE_PATH.read_text())


def resolve_model_key(task_type: str, quality_tier: str) -> str:
    routing_table = load_routing_table()
    return routing_table[task_type][quality_tier]


def resolve_fallback_model_key(task_type: str, quality_tier: str) -> Optional[str]:
    routing_table = load_routing_table()
    return routing_table[task_type].get(f"{quality_tier}_fallback")


async def route_generation(
    task_type: str,
    quality_tier: str,
    messages: List[Dict[str, Any]],
    temperature: float = 0.7,
) -> str:
    model_key = resolve_model_key(task_type, quality_tier)
    fallback_key = resolve_fallback_model_key(task_type, quality_tier)

    try:
        response = await litellm.acompletion(
            model=model_key,
            messages=messages,
            temperature=temperature,
        )
    except Exception:
        if not fallback_key:
            raise
        response = await litellm.acompletion(
            model=fallback_key,
            messages=messages,
            temperature=temperature,
        )

    return response.choices[0].message.content
