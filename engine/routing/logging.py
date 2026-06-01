"""Generation logging and prompt caching helpers."""

from __future__ import annotations

import json
import os
from decimal import Decimal
from typing import Any
from uuid import UUID

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from engine.db.orm import Event, GenerationLog
from engine.routing.router import RouteResult

_COST_RATES: dict[str, tuple[float, float]] = {
    # key: (cost_per_input_token, cost_per_output_token)
    "anthropic/claude-haiku-4-5-20251001": (0.00000025, 0.00000125),
    "anthropic/claude-sonnet-4-6": (0.000003, 0.000015),
    "groq/llama-3.1-8b-instant": (0.00000005, 0.00000008),
    "groq/llama-3.3-70b-versatile": (0.00000059, 0.00000079),
    "groq/gpt-oss-safeguard-20b": (0.00000020, 0.00000020),
}


def compute_cost(model_used: str, input_tokens: int, output_tokens: int) -> Decimal:
    rates = _COST_RATES.get(model_used, (0.0, 0.0))
    if rates == (0.0, 0.0):
        structlog.get_logger().warning("unknown_model_cost", model_used=model_used)
    return Decimal(str(rates[0] * input_tokens + rates[1] * output_tokens)).quantize(
        Decimal("0.000001")
    )


async def log_generation(
    db_session: AsyncSession,
    *,
    session_id: UUID,
    task_type: str,
    quality_tier: str,
    result: RouteResult,
    messages: list[dict[str, Any]] | None = None,
    tension_score: float | None = None,
) -> GenerationLog:
    cost_usd = compute_cost(
        result.model_used, result.input_tokens, result.output_tokens
    )
    _content_logging = os.getenv("CONTENT_LOGGING_ENABLED", "false").lower() == "true"

    if _content_logging and messages is not None:
        prompt_text: str | None = json.dumps(messages)
        output_text: str | None = result.content
    else:
        prompt_text = None
        output_text = None

    if result.used_fallback:
        event = Event(
            session_id=session_id,
            actor_char_id=None,
            event_type="routing_fallback",
            payload={"task_type": task_type, "model_used": result.model_used},
        )
        db_session.add(event)

    log = GenerationLog(
        session_id=session_id,
        task_type=task_type,
        quality_tier=quality_tier,
        model_used=result.model_used,
        latency_ms=result.latency_ms,
        input_tokens=result.input_tokens,
        output_tokens=result.output_tokens,
        cost_usd=cost_usd,
        tension_score=tension_score,
        prompt_text=prompt_text,
        output_text=output_text,
    )
    db_session.add(log)
    await db_session.flush()
    return log


def mark_stable_context_cacheable(
    messages: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if not messages:
        return messages
    first = messages[0]
    if first.get("role") != "system" or not isinstance(first.get("content"), str):
        return messages
    new_first: dict[str, Any] = dict(first)
    new_first["content"] = [
        {
            "type": "text",
            "text": first["content"],
            "cache_control": {"type": "ephemeral"},
        }
    ]
    return [new_first] + list(messages[1:])
