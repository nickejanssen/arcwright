from datetime import datetime, timezone

import pytest

from engine.resources.errors import (
    ActivationNotFoundError,
    InsufficientBalanceError,
    TargetIneligibleError,
)
from engine.resources.models import EffectDefinition, EffectFamily, ResourceBalance
from engine.resources.resolver import ResourceResolver

NOW = datetime(2026, 7, 19, tzinfo=timezone.utc)


def make_resolver():
    resolver = ResourceResolver()
    resolver.set_balance(
        ResourceBalance(
            player_id="p1",
            session_id="s1",
            current_amount=5,
            bank_cap=20,
            protected_floor=0,
        )
    )
    resolver.set_balance(
        ResourceBalance(
            player_id="p2",
            session_id="s1",
            current_amount=5,
            bank_cap=20,
            protected_floor=0,
        )
    )
    return resolver


RATTLE = EffectDefinition(
    effect_key="sabotage.rattle_the_witness",
    family=EffectFamily.witness_pressure,
    cost=2,
    requires_target=True,
    is_offensive=True,
)
LISTEN_IN = EffectDefinition(
    effect_key="sabotage.listen_in",
    family=EffectFamily.information_control,
    cost=2,
    requires_target=True,
    is_offensive=True,
    is_information_control=True,
)


def test_rejects_insufficient_balance():
    resolver = make_resolver()
    expensive = EffectDefinition(
        effect_key="advantage.sting_operation",
        family=EffectFamily.counterplay,
        cost=99,
        requires_target=False,
    )
    with pytest.raises(InsufficientBalanceError):
        resolver.activate(
            effect=expensive,
            activator_id="p1",
            target_id=None,
            window_id="w1",
            beat_id="b1",
            now=NOW,
        )


def test_rejects_second_offensive_modifier_same_window():
    resolver = make_resolver()
    resolver.activate(
        effect=RATTLE,
        activator_id="p1",
        target_id="p2",
        window_id="w1",
        beat_id="b1",
        now=NOW,
    )
    resolver.set_balance(
        ResourceBalance(
            player_id="p1",
            session_id="s1",
            current_amount=5,
            bank_cap=20,
            protected_floor=0,
        )
    )
    with pytest.raises(TargetIneligibleError):
        resolver.activate(
            effect=LISTEN_IN,
            activator_id="p1",
            target_id="p2",
            window_id="w1",
            beat_id="b1",
            now=NOW,
        )


def test_rejects_second_info_control_sabotage_same_beat():
    resolver = make_resolver()
    resolver.activate(
        effect=LISTEN_IN,
        activator_id="p1",
        target_id="p2",
        window_id="w1",
        beat_id="b1",
        now=NOW,
    )
    resolver.set_balance(
        ResourceBalance(
            player_id="p1",
            session_id="s1",
            current_amount=5,
            bank_cap=20,
            protected_floor=0,
        )
    )
    with pytest.raises(TargetIneligibleError):
        resolver.activate(
            effect=LISTEN_IN,
            activator_id="p1",
            target_id="p2",
            window_id="w2",
            beat_id="b1",
            now=NOW,
        )


def test_post_target_protection_clears_on_new_target():
    resolver = make_resolver()
    resolver.activate(
        effect=RATTLE,
        activator_id="p1",
        target_id="p2",
        window_id="w1",
        beat_id="b1",
        now=NOW,
    )
    resolver.set_balance(
        ResourceBalance(
            player_id="p1",
            session_id="s1",
            current_amount=5,
            bank_cap=20,
            protected_floor=0,
        )
    )
    with pytest.raises(TargetIneligibleError):
        resolver.activate(
            effect=RATTLE,
            activator_id="p1",
            target_id="p2",
            window_id="w2",
            beat_id="b1",
            now=NOW,
        )
    resolver.set_balance(
        ResourceBalance(
            player_id="p3",
            session_id="s1",
            current_amount=5,
            bank_cap=20,
            protected_floor=0,
        )
    )
    resolver.activate(
        effect=RATTLE,
        activator_id="p1",
        target_id="p3",
        window_id="w3",
        beat_id="b1",
        now=NOW,
    )


def test_protection_lifts_when_a_new_target_is_sabotaged():
    resolver = make_resolver()
    resolver.activate(
        effect=RATTLE,
        activator_id="p1",
        target_id="p2",
        window_id="w1",
        beat_id="b1",
        now=NOW,
    )
    resolver.set_balance(
        ResourceBalance(
            player_id="p1",
            session_id="s1",
            current_amount=5,
            bank_cap=20,
            protected_floor=0,
        )
    )
    resolver.set_balance(
        ResourceBalance(
            player_id="p3",
            session_id="s1",
            current_amount=5,
            bank_cap=20,
            protected_floor=0,
        )
    )
    resolver.activate(
        effect=RATTLE,
        activator_id="p1",
        target_id="p3",
        window_id="w2",
        beat_id="b1",
        now=NOW,
    )  # p3 now protected, p2's protection lifts
    resolver.set_balance(
        ResourceBalance(
            player_id="p1",
            session_id="s1",
            current_amount=5,
            bank_cap=20,
            protected_floor=0,
        )
    )
    # p2 should be targetable again now that p3 is the protected player
    resolver.activate(
        effect=RATTLE,
        activator_id="p1",
        target_id="p2",
        window_id="w3",
        beat_id="b1",
        now=NOW,
    )


def test_open_new_window_clears_protection():
    resolver = make_resolver()
    resolver.activate(
        effect=RATTLE,
        activator_id="p1",
        target_id="p2",
        window_id="w1",
        beat_id="b1",
        now=NOW,
    )
    resolver.open_new_window()
    resolver.set_balance(
        ResourceBalance(
            player_id="p1",
            session_id="s1",
            current_amount=5,
            bank_cap=20,
            protected_floor=0,
        )
    )
    resolver.activate(
        effect=RATTLE,
        activator_id="p1",
        target_id="p2",
        window_id="w2",
        beat_id="b1",
        now=NOW,
    )


def test_reveal_fires_on_resolve_not_on_activation():
    resolver = make_resolver()
    activation = resolver.activate(
        effect=RATTLE,
        activator_id="p1",
        target_id="p2",
        window_id="w1",
        beat_id="b1",
        now=NOW,
    )
    assert activation.source_reveal_at is None
    resolved = resolver.resolve_activation(window_id="w1", now=NOW)
    assert resolved.source_reveal_at == NOW


def test_grant_increases_balance_bounded_by_bank_cap():
    resolver = make_resolver()

    updated = resolver.grant(
        player_id="p1", amount=3, source="protected_earn", beat_id="b1", now=NOW
    )
    assert updated.current_amount == 8
    assert resolver.get_balance("p1").current_amount == 8

    # A grant that would push past bank_cap saturates at bank_cap rather than
    # overflowing it — no earn path can create an unbounded balance.
    saturated = resolver.grant(
        player_id="p1", amount=50, source="mini_game_reward", beat_id="b2", now=NOW
    )
    assert saturated.current_amount == 20

    # Already at bank_cap: a further grant is a no-op, not an error.
    unchanged = resolver.grant(
        player_id="p1", amount=1, source="mini_game_reward", beat_id="b3", now=NOW
    )
    assert unchanged.current_amount == 20


def test_grant_rejects_non_positive_amount():
    resolver = make_resolver()
    with pytest.raises(ValueError):
        resolver.grant(
            player_id="p1", amount=0, source="protected_earn", beat_id="b1", now=NOW
        )


def test_resolve_activation_raises_activation_not_found_for_unknown_window():
    resolver = make_resolver()
    with pytest.raises(ActivationNotFoundError):
        resolver.resolve_activation(window_id="no-such-window", now=NOW)


def test_counter_and_reveal_source_raises_activation_not_found_for_unknown_window():
    resolver = make_resolver()
    with pytest.raises(ActivationNotFoundError):
        resolver.counter_and_reveal_source(
            countering_activator_id="p2",
            countered_window_id="no-such-window",
            now=NOW,
        )


def test_sting_operation_counter_reveals_immediately_independent_of_resolution():
    resolver = make_resolver()
    activation = resolver.activate(
        effect=RATTLE,
        activator_id="p1",
        target_id="p2",
        window_id="w1",
        beat_id="b1",
        now=NOW,
    )
    assert activation.source_reveal_at is None
    # Sting Operation counters it — reveal fires immediately, before w1 has been resolved via resolve_activation
    countered = resolver.counter_and_reveal_source(
        countering_activator_id="p2", countered_window_id="w1", now=NOW
    )
    assert countered.source_reveal_at == NOW


def test_activate_rejects_missing_target_when_effect_requires_one():
    resolver = make_resolver()
    balance_before = resolver.get_balance("p1").current_amount
    with pytest.raises(TargetIneligibleError):
        resolver.activate(
            effect=RATTLE,
            activator_id="p1",
            target_id=None,
            window_id="w1",
            beat_id="b1",
            now=NOW,
        )
    # Cost must never be deducted for a rejected activation.
    assert resolver.get_balance("p1").current_amount == balance_before
