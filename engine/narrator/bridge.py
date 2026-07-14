"""Narrator bridge generation for session resume.

On resume, the engine emits a short narrator recap that re-grounds players
in the story before normal play continues. Architecture reference:
docs/architecture/05-session-persistence.md §5.3-5.4 (resume step 5).

Safety pipeline (L1 -> L2 -> L3 -> route_generation) is delegated entirely
to engine.routing.logging.generate, which is the only approved entry point
for generation calls in the engine.

Human arc primacy: the prompt is seeded from structured state resolved by
the engine (beat_id, session_context, transition_history). The LLM composes
language from those facts; it does not infer or manage session state.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from engine.events.models import (
    AudienceTarget,
    ContentEvent,
    EventCategory,
    PresentationHints,
)
from engine.routing.logging import generate

if TYPE_CHECKING:
    from engine.db.orm import ArcBeatState

_AUTHORED_FALLBACK_TEXT = "The session begins."
_BRIDGE_HINTS = PresentationHints(emotion="warm", urgency="low", pause_before_ms=1500)


async def generate_narrator_bridge(
    db: AsyncSession,
    session_id: UUID,
    snapshot: "ArcBeatState | None",
    quality_tier: str,
    arc_id: str | None = None,
) -> ContentEvent:
    """Return a narrator bridge ContentEvent for the resume flow.

    AC4 (no-snapshot): returns an authored event immediately, no LLM call.
    AC1-3 (snapshot present): builds a prompt from structured snapshot state
    and runs it through the full safety pipeline via generate().

    When ``arc_id`` is provided, the arc's ``content_rails`` are resolved
    through the arc registry and passed to ``generate()``, so the L3 policy
    block carries the arc's authored rails instead of only the platform
    minimum.  When ``arc_id`` is None or unregistered, ``generate()`` falls
    back to the platform-minimum policy as before.
    """
    if snapshot is None:
        return _make_event(session_id, _AUTHORED_FALLBACK_TEXT)

    content_rails = None
    if arc_id is not None:
        from engine.arc.registry import load_arc_definition

        arc_definition = load_arc_definition(arc_id)
        if arc_definition is not None:
            content_rails = arc_definition.content_rails

    session_context = (snapshot.statemachine_config or {}).get("session_context", {})
    transition_history = snapshot.transition_history or []

    messages = [
        {
            "role": "system",
            "content": (
                "You are the narrator of a live interactive experience. "
                "Write a 2-3 sentence recap that re-grounds players in the "
                "story after a brief pause. Speak directly to the players. "
                "Do not mention the interruption.\n\n"
                f"Current beat: {snapshot.beat_id}\n"
                f"Session context: {json.dumps(session_context)}\n"
                f"Arc path: {', '.join(str(t) for t in transition_history) or 'none yet'}"
            ),
        },
        {
            "role": "user",
            "content": "Continue the session.",
        },
    ]

    result = await generate(
        db,
        session_id=session_id,
        task_type="narrator_bridge",
        quality_tier=quality_tier,
        messages=messages,
        content_rails=content_rails,
    )

    return _make_event(session_id, result.content)


def _make_event(session_id: UUID, text: str) -> ContentEvent:
    return ContentEvent(
        session_id=session_id,
        timestamp=datetime.now(tz=timezone.utc),
        category=EventCategory.narrative,
        event_type="narrator_bridge",
        target_audience=AudienceTarget.all,
        payload={"text": text},
        presentation_hints=_BRIDGE_HINTS,
    )
