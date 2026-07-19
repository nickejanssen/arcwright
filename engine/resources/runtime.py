"""Session-facing orchestration wrapper binding ResourceResolver to ContentEvents.

Thin glue only: all deterministic balance/eligibility/reveal-timing logic lives in
ResourceResolver (engine/resources/resolver.py); all ContentEvent shaping lives in
engine/resources/events.py. This module just sequences resolver calls and builds the
events each call implies, per the effect's documented visibility.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from engine.events.models import AudienceTarget, ContentEvent
from engine.resources.events import (
    build_balance_changed_event,
    build_effect_outcome_event,
    build_source_reveal_event,
)
from engine.resources.models import EffectActivation, EffectDefinition
from engine.resources.resolver import ResourceResolver


class ResourceRuntime:
    """Orchestrates ResourceResolver calls and the ContentEvents each one implies."""

    def __init__(self, resolver: ResourceResolver) -> None:
        self._resolver = resolver

    def activate_effect(
        self,
        *,
        effect: EffectDefinition,
        activator_id: str,
        target_id: str | None,
        window_id: str,
        beat_id: str,
        now: datetime,
        session_id: UUID,
    ) -> tuple[EffectActivation, list[ContentEvent]]:
        activation = self._resolver.activate(
            effect=effect,
            activator_id=activator_id,
            target_id=target_id,
            window_id=window_id,
            beat_id=beat_id,
            now=now,
        )
        new_balance = self._resolver.get_balance(activator_id)
        balance_event = build_balance_changed_event(
            session_id=session_id,
            player_id=UUID(activator_id),
            new_amount=new_balance.current_amount,
            timestamp=now,
        )
        return activation, [balance_event]

    def resolve_window(
        self,
        *,
        window_id: str,
        now: datetime,
        session_id: UUID,
        outcome_payload: dict[str, Any],
        outcome_audience: AudienceTarget,
        outcome_recipient_id: UUID | None = None,
    ) -> tuple[EffectActivation, list[ContentEvent]]:
        activation = self._resolver.resolve_activation(window_id=window_id, now=now)

        events: list[ContentEvent] = [
            build_effect_outcome_event(
                session_id=session_id,
                effect_key=activation.effect_key,
                outcome_payload=outcome_payload,
                audience=outcome_audience,
                recipient_id=outcome_recipient_id,
                timestamp=now,
            )
        ]

        # Normal per-question reveal: the sabotage's source becomes visible to the
        # target it was aimed at, timed to this window's resolution (not to Sting
        # Operation's immediate-reveal exception, which is handled separately below).
        if activation.source_reveal_at is not None and activation.target_id is not None:
            events.append(
                build_source_reveal_event(
                    session_id=session_id,
                    revealed_source_id=UUID(activation.activator_id),
                    recipient_id=UUID(activation.target_id),
                    timestamp=now,
                )
            )

        return activation, events

    def counter_and_reveal_source(
        self,
        *,
        countering_activator_id: str,
        countered_window_id: str,
        now: datetime,
        session_id: UUID,
    ) -> tuple[EffectActivation, ContentEvent]:
        activation = self._resolver.counter_and_reveal_source(
            countering_activator_id=countering_activator_id,
            countered_window_id=countered_window_id,
            now=now,
        )
        # Reveal goes to the countering player, not to whoever the countered
        # sabotage originally targeted.
        reveal_event = build_source_reveal_event(
            session_id=session_id,
            revealed_source_id=UUID(activation.activator_id),
            recipient_id=UUID(countering_activator_id),
            timestamp=now,
        )
        return activation, reveal_event
