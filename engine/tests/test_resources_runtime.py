from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

import pytest

from engine.events.models import AudienceTarget, EventCategory
from engine.resources.models import EffectDefinition, EffectFamily, ResourceBalance
from engine.resources.resolver import ResourceResolver
from engine.resources.runtime import ResourceRuntime

NOW = datetime(2026, 7, 19, tzinfo=timezone.utc)
SESSION_ID = UUID("00000000-0000-0000-0000-000000000030")

ACTIVATOR = "00000000-0000-0000-0000-000000000101"
TARGET = "00000000-0000-0000-0000-000000000102"

RATTLE = EffectDefinition(
    effect_key="sabotage.rattle_the_witness",
    family=EffectFamily.witness_pressure,
    cost=2,
    requires_target=True,
    is_offensive=True,
)
UNTARGETED_ADVANTAGE = EffectDefinition(
    effect_key="advantage.extra_draw",
    family=EffectFamily.economy,
    cost=1,
    requires_target=False,
)


def make_runtime() -> ResourceRuntime:
    resolver = ResourceResolver()
    resolver.set_balance(
        ResourceBalance(
            player_id=ACTIVATOR,
            session_id=str(SESSION_ID),
            current_amount=5,
            bank_cap=20,
            protected_floor=0,
        )
    )
    resolver.set_balance(
        ResourceBalance(
            player_id=TARGET,
            session_id=str(SESSION_ID),
            current_amount=5,
            bank_cap=20,
            protected_floor=0,
        )
    )
    return ResourceRuntime(resolver)


def test_activate_effect_returns_activation_and_balance_changed_event() -> None:
    runtime = make_runtime()

    activation, events = runtime.activate_effect(
        effect=RATTLE,
        activator_id=ACTIVATOR,
        target_id=TARGET,
        window_id="w1",
        beat_id="b1",
        now=NOW,
        session_id=SESSION_ID,
    )

    assert activation.effect_key == "sabotage.rattle_the_witness"
    assert activation.activator_id == ACTIVATOR
    assert activation.target_id == TARGET
    assert activation.interaction_window_id == "w1"
    assert activation.resolved_at is None

    assert len(events) == 1
    balance_event = events[0]
    assert balance_event.event_type == "resource_balance_changed"
    assert balance_event.target_audience is AudienceTarget.all
    assert balance_event.actor_id == UUID(ACTIVATOR)
    assert balance_event.payload == {
        "player_id": ACTIVATOR,
        "current_amount": 3,
    }


def test_resolve_window_returns_resolved_activation_outcome_and_reveal_events() -> None:
    runtime = make_runtime()
    runtime.activate_effect(
        effect=RATTLE,
        activator_id=ACTIVATOR,
        target_id=TARGET,
        window_id="w1",
        beat_id="b1",
        now=NOW,
        session_id=SESSION_ID,
    )

    resolved, events = runtime.resolve_window(
        window_id="w1",
        now=NOW,
        session_id=SESSION_ID,
        outcome_payload={"witness_state": "shaken"},
        outcome_audience=AudienceTarget.all,
        outcome_category=EventCategory.character_dialogue,
    )

    assert resolved.resolved_at == NOW
    assert resolved.source_reveal_at == NOW

    assert len(events) == 2
    outcome_event, reveal_event = events
    assert outcome_event.event_type == "resource_effect_outcome"
    assert outcome_event.target_audience is AudienceTarget.all
    assert outcome_event.category is EventCategory.character_dialogue
    assert outcome_event.payload == {
        "effect_key": "sabotage.rattle_the_witness",
        "outcome": {"witness_state": "shaken"},
    }

    assert reveal_event.event_type == "resource_effect_source_revealed"
    assert reveal_event.target_audience is AudienceTarget.specific_player
    assert reveal_event.target_player_id == UUID(TARGET)
    assert reveal_event.payload == {"revealed_source_id": ACTIVATOR}


def test_resolve_window_without_target_produces_no_reveal_event() -> None:
    runtime = make_runtime()
    runtime.activate_effect(
        effect=UNTARGETED_ADVANTAGE,
        activator_id=ACTIVATOR,
        target_id=None,
        window_id="w1",
        beat_id="b1",
        now=NOW,
        session_id=SESSION_ID,
    )

    resolved, events = runtime.resolve_window(
        window_id="w1",
        now=NOW,
        session_id=SESSION_ID,
        outcome_payload={"extra_cards": 1},
        outcome_audience=AudienceTarget.specific_player,
        outcome_category=EventCategory.private_delivery,
        outcome_recipient_id=UUID(ACTIVATOR),
    )

    assert resolved.target_id is None
    assert len(events) == 1
    assert events[0].event_type == "resource_effect_outcome"


def test_counter_and_reveal_source_returns_reveal_private_to_countering_user() -> None:
    runtime = make_runtime()
    runtime.activate_effect(
        effect=RATTLE,
        activator_id=ACTIVATOR,
        target_id=TARGET,
        window_id="w1",
        beat_id="b1",
        now=NOW,
        session_id=SESSION_ID,
    )

    countered, reveal_event = runtime.counter_and_reveal_source(
        countering_activator_id=TARGET,
        countered_window_id="w1",
        now=NOW,
        session_id=SESSION_ID,
    )

    assert countered.source_reveal_at == NOW
    assert countered.resolved_at is None

    assert reveal_event.event_type == "resource_effect_source_revealed"
    assert reveal_event.target_audience is AudienceTarget.specific_player
    assert reveal_event.target_player_id == UUID(TARGET)
    assert reveal_event.payload == {"revealed_source_id": ACTIVATOR}


def test_resolve_window_raises_for_unknown_window() -> None:
    runtime = make_runtime()
    with pytest.raises(ValueError):
        runtime.resolve_window(
            window_id="missing",
            now=NOW,
            session_id=SESSION_ID,
            outcome_payload={},
            outcome_audience=AudienceTarget.all,
            outcome_category=EventCategory.state_transition,
        )
