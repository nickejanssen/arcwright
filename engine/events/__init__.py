"""Multi-surface content event system.

Public surface for the engine's event layer. Models are defined in ``models``;
the in-memory per-session async bus lives in ``bus``; audience-filtered fanout
and the SSE connection registry live in ``fanout``.
"""

from engine.events.bus import DEFAULT_HISTORY_CAP, SessionEventBus, Subscription
from engine.events.fanout import (
    SessionConnectionRegistry,
    SSEConnection,
    run_fanout,
)
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
    "run_fanout",
    "SessionConnectionRegistry",
    "SessionEventBus",
    "SSEConnection",
    "Subscription",
]
