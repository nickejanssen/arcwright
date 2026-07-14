"""Generation logging and the db-aware generation entrypoint."""

from __future__ import annotations

import json
import os
from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from engine.db.orm import Event, GenerationLog
from engine.routing.router import RouteResult, compute_cost, route_generation
from engine.safety import (
    build_l1_hard_stop_route_result,
    build_l2_blocked_route_result,
    build_l2_classification_messages,
    build_l2_classification_payload,
    build_safety_hard_stop_payload,
    evaluate_l1_hard_stops,
    inject_l3_policy_block,
    parse_l2_classification,
)

if TYPE_CHECKING:
    from engine.arc.models import ContentRailsConfig


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
    safety_policy_context: dict[str, Any] | str | None = None,
    content_rails: "ContentRailsConfig | None" = None,
) -> RouteResult:
    """Route a generation call, enforce all safety layers, and log it.

    This is the only approved way to make a generation call in the engine.
    Calling route_generation directly bypasses all safety layers and is not
    permitted outside this module and engine/routing/router.py.

    Safety layers run in this order:

    1. L1 hard stops: deterministic, no AI call, catches the most severe
       content categories unconditionally.
    2. L2 classification: AI-based classification of whether the assembled
       prompt falls inside the arc's permitted territory.
    3. L3 policy injection: adds plain-language rules to the prompt telling
       the main model what it must not write.  This is the "rules in the
       prompt" backstop for anything L2 did not catch.
    4. Main generation: the actual content call, only reached if L1 and L2
       both allow it.

    Args:
        db_session: The active SQLAlchemy async session for logging writes.
        session_id: The Arcwright session this generation belongs to.
        task_type: Routing key such as "character_dialogue" or
            "narrative_generation".  Safety classification tasks skip L2
            to avoid recursive classification.
        quality_tier: Quality tier key, e.g. "standard" or "premium".
        messages: The assembled prompt messages.  L3 may prepend a policy
            message to this list before the main call; the original list is
            never mutated.
        temperature: Sampling temperature for the main generation call.
        tension_score: Optional pacing tension score, written to the
            generation log for telemetry.
        safety_policy_context: Optional serialised L2 policy context passed
            to the classifier.  When None the default platform policy is used.
        content_rails: Optional arc `ContentRailsConfig` used to build the L3
            policy block.  When None, the platform minimum policy (mirroring
            the four L1 hard-stop categories) is injected as a backstop so
            L3 always runs.

    Returns:
        A RouteResult.  If L1 fires, returns the L1 neutral bridge sentinel.
        If L2 blocks, returns the L2 neutral bridge sentinel.  Otherwise,
        returns the main generation result.
    """
    # -----------------------------------------------------------------------
    # L1: Hard stops are deterministic checks with no model call or latency.
    # If any hard stop fires, we log a safety_hard_stop event and return a
    # neutral bridge.  No model is ever called when L1 fires.
    # -----------------------------------------------------------------------
    hard_stop = evaluate_l1_hard_stops(messages)
    if hard_stop is not None:
        event = Event(
            session_id=session_id,
            actor_char_id=None,
            event_type="safety_hard_stop",
            payload=build_safety_hard_stop_payload(hard_stop),
            content_text=None,
        )
        db_session.add(event)
        await db_session.flush()
        return build_l1_hard_stop_route_result()

    if task_type != "safety_classification":
        # -------------------------------------------------------------------
        # L2: Pre-generation classification.
        # This sends the assembled prompt to a small, fast classifier model.
        # The classifier checks whether the prompt is within the arc's
        # permitted territory before we spend money on the main generation.
        # -------------------------------------------------------------------
        classification_messages = build_l2_classification_messages(
            messages,
            safety_policy_context=safety_policy_context,
        )
        classification_result = await route_generation(
            "safety_classification",
            quality_tier,
            classification_messages,
            0.0,
        )
        await log_generation(
            db_session,
            session_id=session_id,
            task_type="safety_classification",
            quality_tier=quality_tier,
            result=classification_result,
            messages=classification_messages,
            tension_score=tension_score,
        )
        classification = parse_l2_classification(classification_result.content)
        event = Event(
            session_id=session_id,
            actor_char_id=None,
            event_type="safety_classification",
            payload=build_l2_classification_payload(classification),
            content_text=None,
        )
        db_session.add(event)
        await db_session.flush()
        if classification.blocked:
            return build_l2_blocked_route_result()

        # -------------------------------------------------------------------
        # L3: In-generation policy injection.
        # This block tells the main AI model what it is not allowed to write,
        # based on the rules the game designer set up in the arc definition.
        # It is injected here, after L2 has approved the prompt but before
        # the main model sees it, so the rules are always present.
        #
        # When content_rails is None, inject_l3_policy_block falls back to
        # the platform minimum policy (the four L1 hard-stop categories
        # expressed as prompt instructions) so L3 always runs.
        # -------------------------------------------------------------------
        messages = inject_l3_policy_block(
            messages,
            content_rails,
        )

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
