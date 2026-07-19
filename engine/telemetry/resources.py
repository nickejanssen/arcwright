"""Resource-economy telemetry (spec 0075, AW-287).

Six events, all written to the ``events`` table like every other telemetry
signal, covering the full lifecycle a resource effect can move through:

- ``resource_grant``: a balance grant (mini-game reward or protected earn
  path) landed for a player.
- ``resource_spend``: an effect activation's cost was deducted.
- ``resource_target``: a sabotage (offensive) effect was activated against a
  target.
- ``resource_outcome``: an effect activation resolved.
- ``resource_counterplay``: a Sting-Operation-style counter revealed a
  sabotage's source immediately, bypassing normal per-question reveal timing.
- ``resource_recovery``: a player who was under post-target protection
  became targetable again.

Every payload below is built from structural identifiers only — player ids
(as strings), effect_key, beat_id, window_id, amounts, and a fixed source
tag — never free text or copied private-observation content, per spec
0075's acceptance criterion that telemetry "records grants, spends,
targets, outcomes, counterplay, and player recovery without storing
unnecessary private content."
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from engine.db.orm import Event
from engine.resources.models import EffectActivation, ResourceGrant, ResourceSpend


def build_resource_grant_payload(grant: ResourceGrant) -> dict[str, Any]:
    return {
        "player_id": grant.player_id,
        "amount": grant.amount,
        "source": grant.source,
        "beat_id": grant.beat_id,
    }


def build_resource_spend_payload(spend: ResourceSpend) -> dict[str, Any]:
    return {
        "player_id": spend.player_id,
        "amount": spend.amount,
        "effect_key": spend.effect_key,
        "beat_id": spend.beat_id,
    }


def build_resource_target_payload(
    activation: EffectActivation, *, beat_id: str
) -> dict[str, Any]:
    if activation.target_id is None:
        raise ValueError("resource_target telemetry requires a targeted activation")
    return {
        "effect_key": activation.effect_key,
        "activator_id": activation.activator_id,
        "target_id": activation.target_id,
        "window_id": activation.interaction_window_id,
        "beat_id": beat_id,
    }


def build_resource_outcome_payload(
    activation: EffectActivation, *, beat_id: str
) -> dict[str, Any]:
    return {
        "effect_key": activation.effect_key,
        "activator_id": activation.activator_id,
        "target_id": activation.target_id,
        "window_id": activation.interaction_window_id,
        "beat_id": beat_id,
        "source_revealed": activation.source_reveal_at is not None,
    }


def build_resource_counterplay_payload(
    *,
    countering_activator_id: str,
    countered_activator_id: str,
    countered_window_id: str,
    beat_id: str,
) -> dict[str, Any]:
    return {
        "countering_activator_id": countering_activator_id,
        "countered_activator_id": countered_activator_id,
        "countered_window_id": countered_window_id,
        "beat_id": beat_id,
    }


def build_resource_recovery_payload(
    *, recovered_player_id: str, beat_id: str
) -> dict[str, Any]:
    return {
        "recovered_player_id": recovered_player_id,
        "beat_id": beat_id,
    }


async def record_resource_grant(
    db: AsyncSession, session_id: UUID, grant: ResourceGrant
) -> None:
    db.add(
        Event(
            session_id=session_id,
            event_type="resource_grant",
            payload=build_resource_grant_payload(grant),
        )
    )
    await db.flush()


async def record_resource_spend(
    db: AsyncSession, session_id: UUID, spend: ResourceSpend
) -> None:
    db.add(
        Event(
            session_id=session_id,
            event_type="resource_spend",
            payload=build_resource_spend_payload(spend),
        )
    )
    await db.flush()


async def record_resource_target(
    db: AsyncSession,
    session_id: UUID,
    activation: EffectActivation,
    *,
    beat_id: str,
) -> None:
    db.add(
        Event(
            session_id=session_id,
            event_type="resource_target",
            payload=build_resource_target_payload(activation, beat_id=beat_id),
        )
    )
    await db.flush()


async def record_resource_outcome(
    db: AsyncSession,
    session_id: UUID,
    activation: EffectActivation,
    *,
    beat_id: str,
) -> None:
    db.add(
        Event(
            session_id=session_id,
            event_type="resource_outcome",
            payload=build_resource_outcome_payload(activation, beat_id=beat_id),
        )
    )
    await db.flush()


async def record_resource_counterplay(
    db: AsyncSession,
    session_id: UUID,
    *,
    countering_activator_id: str,
    countered_activator_id: str,
    countered_window_id: str,
    beat_id: str,
) -> None:
    db.add(
        Event(
            session_id=session_id,
            event_type="resource_counterplay",
            payload=build_resource_counterplay_payload(
                countering_activator_id=countering_activator_id,
                countered_activator_id=countered_activator_id,
                countered_window_id=countered_window_id,
                beat_id=beat_id,
            ),
        )
    )
    await db.flush()


async def record_resource_recovery(
    db: AsyncSession,
    session_id: UUID,
    *,
    recovered_player_id: str,
    beat_id: str,
) -> None:
    db.add(
        Event(
            session_id=session_id,
            event_type="resource_recovery",
            payload=build_resource_recovery_payload(
                recovered_player_id=recovered_player_id, beat_id=beat_id
            ),
        )
    )
    await db.flush()
