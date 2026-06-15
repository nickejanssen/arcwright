"""Multi-surface content event system.

Public surface for the engine's event layer. Models are defined in ``models``;
the in-memory per-session async bus lives in ``bus``. SSE transport and
audience-filtered fanout land in AW-216.
"""

from engine.events.bus import DEFAULT_HISTORY_CAP, SessionEventBus, Subscription
from engine.events.models import (
    AudienceTarget,
    ContentEvent,
    EventCategory,
    PresentationHints,
)

__all__ = [
    "AudienceTarget",
    "ContentEvent",
    "DEFAULT_HISTORY_CAP",
    "EventCategory",
    "PresentationHints",
    "SessionEventBus",
    "Subscription",
]
