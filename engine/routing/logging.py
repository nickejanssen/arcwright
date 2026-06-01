"""Generation logging and the db-aware generation entrypoint."""

from __future__ import annotations

import json
import os
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from engine.db.orm import Event, GenerationLog
from engine.routing.router import RouteResult, compute_cost, route_generation


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


async def generate(
    db_session: AsyncSession,
    *,
    session_id: UUID,
    task_type: str,
    quality_tier: str,
    messages: list[dict[str, Any]],
    temperature: float = 0.7,
    tension_score: float | None = None,
) -> RouteResult:
    """Route a generation call and immediately log it to generation_logs."""
    result = await route_generation(task_type, quality_tier, messages, temperature)
    await log_generation(
        db_session,
        session_id=session_id,
        task_type=task_type,
        quality_tier=quality_tier,
        result=result,
        messages=messages,
        tension_score=tension_score,
    )
    return result
