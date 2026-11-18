"""Test-only pieces for the mini-game reward tests (AW-328).

``RankedPlugin`` is a made-up game rule: it never completes by itself, and it
ranks players by the ``place`` each one sent with a submission. No shipped game
is used and no model is called.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import timezone
from typing import Any, cast
from uuid import UUID

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from engine.arc.models import ArcDefinition
from engine.db.orm import Decision, MiniGameRun, MiniGameSubmission
from engine.events.bus import SessionEventBus
from engine.mini_games.resolver import ResolvedMiniGameSnapshot
from engine.mini_games.runtime import MechanicRegistry, MiniGameRuntime
from engine.session.phases import tick
from engine.tests.rounds_support import (
    TIMER_RACE_BINDING,
    Recorder,
    Seated,
    at,
    phased_arc,
    reach_phase,
    seat_session,
)

ENTERED = 100  # the second at which a test enters beat_one's mini-game phase
AFTER_DEADLINE = ENTERED + 25  # past the game's 20 seconds, inside the phase's 30


class RankedPlugin:
    mechanic_type = "timer-race"

    def validate_payload(self, payload: dict[str, Any]) -> None:
        if payload.get("done") is not True:
            raise ValueError("payload must carry done=true")

    def is_threshold_met(
        self, snapshot: ResolvedMiniGameSnapshot, submissions: list[MiniGameSubmission]
    ) -> bool:
        return False

    def score(
        self, snapshot: ResolvedMiniGameSnapshot, submissions: list[MiniGameSubmission]
    ) -> dict[str, Any]:
        return {"submissions": len(submissions)}

    def standing(
        self,
        snapshot: ResolvedMiniGameSnapshot,
        submissions: list[MiniGameSubmission],
        outcome: dict[str, Any],
    ) -> list[list[str]]:
        places: dict[int, list[str]] = {}
        for sub in submissions:
            place = sub.payload.get("place")
            if isinstance(place, int):
                places.setdefault(place, []).append(str(sub.character_id))
        return [places[place] for place in sorted(places)]


def ranked_registry() -> MechanicRegistry:
    return MechanicRegistry([RankedPlugin()])


def reward_binding(
    amount: int | None = 1, *, release_content: bool | None = None
) -> dict[str, Any]:
    binding: dict[str, Any] = dict(TIMER_RACE_BINDING)
    if amount is not None:
        binding["reward"] = {
            "kind": "investigation",
            "amount": amount,
            "to": "top_ranked",
        }
    if release_content is not None:
        binding["release_content"] = release_content
    return binding


def reward_arc(amount: int | None = 1, **binding: Any) -> ArcDefinition:
    return phased_arc(mini_games={"beat_one": [reward_binding(amount, **binding)]})


async def in_mini_game(
    db: AsyncSession,
    registered: Callable[[ArcDefinition], None],
    monkeypatch: pytest.MonkeyPatch,
    arc: ArcDefinition,
    *,
    players: int = 3,
) -> tuple[Seated, Recorder]:
    registered(arc)
    monkeypatch.setattr(
        "engine.session.mini_game_phase.build_registry", ranked_registry
    )
    seated = await seat_session(db, arc, players=players)
    rec = Recorder()
    await tick(db, seated.session_id, at(0), rec)
    await reach_phase(db, seated, "beat_one", "mini_game", at(ENTERED), rec)
    return seated, rec


def runtime(
    db: AsyncSession, now: float, publish: Recorder | None = None
) -> MiniGameRuntime:
    bus: Any = publish if publish is not None else SessionEventBus()
    return MiniGameRuntime(
        db, cast(SessionEventBus, _Bus(bus)), ranked_registry(), clock=lambda: at(now)
    )


class _Bus:
    def __init__(self, target: Any) -> None:
        self._target = target

    async def publish(self, event: Any) -> Any:
        if callable(self._target):
            await self._target(event)
        return event


async def the_run(db: AsyncSession, session_id: UUID) -> MiniGameRun:
    result = await db.execute(
        select(MiniGameRun)
        .where(MiniGameRun.session_id == session_id)
        .execution_options(populate_existing=True)
    )
    (run,) = result.scalars().all()
    if run.deadline is not None and run.deadline.tzinfo is None:
        run.deadline = run.deadline.replace(tzinfo=timezone.utc)
    return run


async def place_players(
    db: AsyncSession, seated: Seated, places: list[int | None], now: float = ENTERED + 5
) -> MiniGameRun:
    """Each player sends a submission carrying their place (None sends nothing)."""
    run = await the_run(db, seated.session_id)
    rt = runtime(db, now)
    for index, place in enumerate(places):
        if place is None:
            continue
        await rt.submit_action(
            run.run_id,
            f"sub-{index}",
            seated.characters[index],
            {"done": True, "place": place},
        )
    return run


async def grants(db: AsyncSession, session_id: UUID) -> list[Decision]:
    result = await db.execute(
        select(Decision).where(
            Decision.session_id == session_id,
            Decision.decision_type == "budget_grant",
        )
    )
    return list(result.scalars().all())
