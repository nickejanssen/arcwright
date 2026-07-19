from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

import pytest

from engine.events.models import AudienceTarget, EventCategory
from engine.resources.events import (
    build_balance_changed_event,
    build_effect_outcome_event,
    build_source_reveal_event,
)

SESSION_ID = UUID("00000000-0000-0000-0000-000000000020")
PLAYER_ID = UUID("00000000-0000-0000-0000-000000000021")
SABOTEUR_ID = UUID("00000000-0000-0000-0000-000000000022")
SOURCE_ID = UUID("00000000-0000-0000-0000-000000000023")
TIMESTAMP = datetime(2026, 7, 18, tzinfo=timezone.utc)


def test_balance_changed_event_always_targets_all() -> None:
    event = build_balance_changed_event(
        session_id=SESSION_ID,
        player_id=PLAYER_ID,
        new_amount=7,
        timestamp=TIMESTAMP,
    )

    assert event.category is EventCategory.state_transition
    assert event.event_type == "resource_balance_changed"
    assert event.actor_id == PLAYER_ID
    assert event.target_audience is AudienceTarget.all
    assert event.target_player_id is None
    assert event.payload == {
        "player_id": str(PLAYER_ID),
        "current_amount": 7,
    }


def test_listen_in_effect_outcome_is_private_to_the_saboteur() -> None:
    event = build_effect_outcome_event(
        session_id=SESSION_ID,
        effect_key="listen_in",
        outcome_payload={"copied_content": "The note reads: meet at midnight."},
        audience=AudienceTarget.specific_player,
        recipient_id=SABOTEUR_ID,
        timestamp=TIMESTAMP,
    )

    assert event.category is EventCategory.private_delivery
    assert event.event_type == "resource_effect_outcome"
    assert event.target_audience is AudienceTarget.specific_player
    assert event.target_player_id == SABOTEUR_ID
    assert event.payload == {
        "effect_key": "listen_in",
        "outcome": {"copied_content": "The note reads: meet at midnight."},
    }


def test_effect_outcome_requires_recipient_for_specific_player_audience() -> None:
    with pytest.raises(ValueError):
        build_effect_outcome_event(
            session_id=SESSION_ID,
            effect_key="listen_in",
            outcome_payload={"copied_content": "..."},
            audience=AudienceTarget.specific_player,
            recipient_id=None,
            timestamp=TIMESTAMP,
        )


def test_public_effect_outcome_event_targets_all() -> None:
    event = build_effect_outcome_event(
        session_id=SESSION_ID,
        effect_key="rattle_the_witness",
        outcome_payload={"witness_state": "shaken"},
        audience=AudienceTarget.all,
        recipient_id=None,
        timestamp=TIMESTAMP,
    )

    assert event.event_type == "resource_effect_outcome"
    assert event.target_audience is AudienceTarget.all
    assert event.target_player_id is None
    assert event.payload == {
        "effect_key": "rattle_the_witness",
        "outcome": {"witness_state": "shaken"},
    }


def test_make_them_wait_effect_outcome_event_targets_all() -> None:
    event = build_effect_outcome_event(
        session_id=SESSION_ID,
        effect_key="make_them_wait",
        outcome_payload={"queue_state": "delayed"},
        audience=AudienceTarget.all,
        recipient_id=None,
        timestamp=TIMESTAMP,
    )

    assert event.target_audience is AudienceTarget.all
    assert event.target_player_id is None


def test_sting_operation_source_reveal_targets_only_the_sting_user() -> None:
    event = build_source_reveal_event(
        session_id=SESSION_ID,
        revealed_source_id=SOURCE_ID,
        recipient_id=PLAYER_ID,
        timestamp=TIMESTAMP,
    )

    assert event.category is EventCategory.private_delivery
    assert event.event_type == "resource_effect_source_revealed"
    assert event.target_audience is AudienceTarget.specific_player
    assert event.target_audience is not AudienceTarget.all
    assert event.target_player_id == PLAYER_ID
    assert event.payload == {"revealed_source_id": str(SOURCE_ID)}
