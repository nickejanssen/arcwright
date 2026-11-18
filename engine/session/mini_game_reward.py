"""The reward for a finished mini-game run (AW-328, D-126; spec 0093 Q1).

The arc file sets it on the beat's mini-game binding: what, how much and to
whom. The binding's settings are copied into the run when it starts, so a run
keeps the reward it started with. When the run's phase ends, the players in the top tier of the run's saved
standing each get a ``budget_grant`` row, which ``engine.session.choices`` adds
to their budget. Nothing is stored apart from that row, so the budget is the
same after a reload.

Called with the session lock held (``mini_game_phase.stop_open_run``, from
``phases._end``). It reads saved state first, so a second call for the same run
finds the rows and does nothing: no second row, no second message. Each row
records whether its player has been told; a message that fails to send stops the
phase from ending, and the next tick sends only the ones still owed.

When every eligible player is in the top tier, the run separated nobody and
nothing is given (D-127; approved in the AW-328 plan).
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from engine.db.orm import Decision
from engine.events.models import (
    AudienceTarget,
    ContentEvent,
    EventCategory,
    PresentationHints,
)
from engine.mini_games.models import MiniGameReward
from engine.session import mini_game_phase
from engine.session.mini_game_phase import Publish

REWARD_SOURCE = "mini_game_reward"
REWARD_EVENT = "mini_game_reward_granted"


def _winners(standing: Any) -> list[str]:
    """The top tier, or nobody when it holds every player (or there is no tier)."""
    if not isinstance(standing, list) or len(standing) < 2:
        return []
    top = standing[0]
    return [str(p) for p in top] if isinstance(top, list) else []


async def _already_given(db: AsyncSession, session_id: UUID, run_id: UUID) -> set[str]:
    from engine.session.choices import BUDGET_GRANT_DECISION  # avoids a cycle

    result = await db.execute(
        select(Decision.context).where(
            Decision.session_id == session_id,
            Decision.decision_type == BUDGET_GRANT_DECISION,
        )
    )
    contexts: list[dict[str, Any]] = list(result.scalars().all())
    return {
        str(ctx.get("participant_id"))
        for ctx in contexts
        if ctx.get("run_id") == str(run_id)
    }


async def give(
    db: AsyncSession,
    session_id: UUID,
    beat_id: str,
    phase_entry: int,
    now: datetime,
    publish: Publish,
) -> list[UUID]:
    """Save the reward for this visit's run, then tell each winner. Returns who
    was given it now. See ``grant`` and ``notify``."""
    newly = await grant(db, session_id, beat_id, phase_entry, now)
    await notify(db, session_id, beat_id, phase_entry, now, publish)
    return newly


async def grant(
    db: AsyncSession,
    session_id: UUID,
    beat_id: str,
    phase_entry: int,
    now: datetime,
) -> list[UUID]:
    """Save one ``budget_grant`` row for each top-tier player who has none for
    this run. Each row starts marked as not yet told."""
    from engine.session.choices import BUDGET_GRANT_DECISION

    run = await mini_game_phase.bound_run(db, session_id, beat_id, phase_entry)
    if run is None or run.status not in ("completed", "timed_out"):
        return []
    saved = (run.definition_snapshot or {}).get("binding") or {}
    if not saved.get("reward"):
        return []
    reward = MiniGameReward.model_validate(saved["reward"])
    binding_id = saved.get("binding_id")
    winners = _winners((run.outcome or {}).get("standing"))
    if not winners:
        return []
    given = await _already_given(db, session_id, run.run_id)
    newly: list[UUID] = []
    for participant in winners:
        if participant in given:
            continue
        db.add(
            Decision(
                session_id=session_id,
                timestamp=now,
                decision_type=BUDGET_GRANT_DECISION,
                context={
                    "participant_id": participant,
                    "run_id": str(run.run_id),
                    "beat_id": beat_id,
                    "binding_id": binding_id,
                    "source": REWARD_SOURCE,
                },
                outcome={
                    "amount": reward.amount,
                    "kind": reward.kind,
                    "told": False,
                },
            )
        )
        newly.append(UUID(participant))
    await db.flush()
    return newly


async def notify(
    db: AsyncSession,
    session_id: UUID,
    beat_id: str,
    phase_entry: int,
    now: datetime,
    publish: Publish,
) -> None:
    """Tell each winner whose grant is not yet marked told, marking each one
    after its message is sent. A failure propagates, so the phase does not end
    and the next tick tries again for the winners still not told; those already
    told are not told twice."""
    from engine.session.choices import BUDGET_GRANT_DECISION, remaining_budget

    run = await mini_game_phase.bound_run(db, session_id, beat_id, phase_entry)
    if run is None:
        return
    result = await db.execute(
        select(Decision)
        .where(
            Decision.session_id == session_id,
            Decision.decision_type == BUDGET_GRANT_DECISION,
        )
        .order_by(Decision.timestamp)
    )
    for row in result.scalars().all():
        if row.context.get("run_id") != str(run.run_id):
            continue
        if row.context.get("source") != REWARD_SOURCE or row.outcome.get("told"):
            continue
        participant_id = UUID(str(row.context["participant_id"]))
        await _tell(
            publish,
            session_id,
            now,
            participant_id,
            {
                "amount": row.outcome["amount"],
                "kind": row.outcome["kind"],
                "remaining_budget": await remaining_budget(
                    db, session_id, participant_id
                ),
            },
        )
        row.outcome = {**row.outcome, "told": True}
        await db.flush()


async def _tell(
    publish: Publish,
    session_id: UUID,
    now: datetime,
    participant_id: UUID,
    payload: dict[str, Any],
) -> None:
    """A private message to the rewarded player: how much, and what is left."""
    if publish is None:
        return
    await publish(
        ContentEvent(
            session_id=session_id,
            timestamp=now,
            category=EventCategory.private_delivery,
            event_type=REWARD_EVENT,
            target_audience=AudienceTarget.specific_player,
            target_player_id=participant_id,
            payload=payload,
            presentation_hints=PresentationHints(),
        )
    )
