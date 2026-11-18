"""The once-a-second loop that moves rounds by the clock (spec 0093, Part C).

It only calls ``engine.session.phases.tick_active_sessions``; every rule and
every deadline lives in the engine and in saved state, so a restart loses
nothing. Single process: with more than one, each change is still checked
against saved state first, but that case is untested (spec 0093, Risks).

What "single process" means in practice: the event bus for each session is an
in-memory object in this process, and the in-process lock is per process. With
two API processes each would run its own loop, saved state would stay correct
on Postgres, but a tick's events would reach only the screens connected to the
process that ran it. A multi-process deploy needs a shared event bus (or
routing every session to one process), exactly one tick-loop owner, and the
Postgres run of the locking tests (see AW-269).
"""

from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import Awaitable, Callable
from datetime import datetime, timezone
from uuid import UUID

from api.routers.events import _get_or_create_session_state
from engine.db import get_session_factory
from engine.events.models import ContentEvent
from engine.session.phases import tick_active_sessions

logger = logging.getLogger(__name__)

TICK_SECONDS = 1.0
LOG_WINDOW_SECONDS = 30.0
_monotonic = time.monotonic


def _publisher_for(
    session_id: UUID,
) -> Callable[[ContentEvent], Awaitable[ContentEvent]]:
    bus, _registry = _get_or_create_session_state(session_id)
    return bus.publish


async def run_tick_loop(interval: float = TICK_SECONDS) -> None:
    """Run until cancelled. A failed pass never stops the loop.

    The first failure of a run is logged at once. Later failures are counted
    and logged at most once per ``LOG_WINDOW_SECONDS`` with the number skipped,
    so a database outage stays visible without one line a second. When a pass
    works again, one line says how many passes had failed.
    """
    failed_passes = 0
    skipped = 0
    last_logged = 0.0
    while True:
        try:
            await tick_active_sessions(
                get_session_factory(), datetime.now(tz=timezone.utc), _publisher_for
            )
            if failed_passes:
                logger.info(
                    "round tick recovered after %d failed passes", failed_passes
                )
                failed_passes = skipped = 0
        except asyncio.CancelledError:
            raise
        except Exception:
            failed_passes += 1
            now = _monotonic()
            if failed_passes == 1 or now - last_logged >= LOG_WINDOW_SECONDS:
                note = (
                    f" ({skipped} more failures since the last log)" if skipped else ""
                )
                logger.exception("round tick pass failed; will keep trying%s", note)
                last_logged = now
                skipped = 0
            else:
                skipped += 1
        await asyncio.sleep(interval)
