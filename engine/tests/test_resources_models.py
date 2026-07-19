import pytest
from pydantic import ValidationError

from engine.resources.models import (
    EffectActivation,
    EffectDefinition,
    ResourceBalance,
)


def test_resource_balance_rejects_floor_above_cap():
    with pytest.raises(ValidationError):
        ResourceBalance(
            player_id="p1",
            session_id="s1",
            current_amount=0,
            bank_cap=5,
            protected_floor=6,
        )


def test_resource_balance_defaults():
    balance = ResourceBalance(
        player_id="p1", session_id="s1", bank_cap=20, protected_floor=0
    )
    assert balance.current_amount == 0


def test_effect_activation_reveal_defaults_none():
    activation = EffectActivation(
        effect_key="sabotage.rattle_the_witness",
        activator_id="p1",
        target_id="p2",
        interaction_window_id="w1",
    )
    assert activation.source_reveal_at is None


def test_effect_definition_rejects_unknown_family():
    with pytest.raises(ValidationError):
        EffectDefinition(
            effect_key="advantage.deep_read",
            family="not-a-family",
            cost=2,
            requires_target=False,
        )
