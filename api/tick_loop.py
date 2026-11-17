"""The once-a-second loop that moves rounds by the clock (spec 0093, Part C).

It only calls ``engine.session.phases.tick_active_sessions``; every rule and
every deadline lives in the engine and in saved state, so a restart loses
nothing. Single process: with more than one, each change is still checked
against saved state first, but that case is untested (spec 0093, Risks).
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable
from datetime import datetime, timezone
from uuid import UUID

from api.routers.events import _get_or_create_session_state
from engine.db import get_session_factory
from engine.events.models import ContentEvent
from engine.session.phases import tick_active_sessions

logger = logging.getLogger(__name__)

TICK_SECONDS = 1.0


def _publisher_for(
    session_id: UUID,
) -> Callable[[ContentEvent], Awaitable[ContentEvent]]:
    bus, _registry = _get_or_create_session_state(session_id)
    return bus.publish


async def run_tick_loop(interval: float = TICK_SECONDS) -> None:
    """Run until cancelled. A failed pass is logged once per streak and the
    loop carries on."""
    failing = False
    while True:
        try:
            await tick_active_sessions(
                get_session_factory(), datetime.now(tz=timezone.utc), _publisher_for
            )
            failing = False
        except asyncio.CancelledError:
            raise
        except Exception:
            if not failing:
                logger.exception("round tick pass failed; will keep trying")
            failing = True
        await asyncio.sleep(interval)
