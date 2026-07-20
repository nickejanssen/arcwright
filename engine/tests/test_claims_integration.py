from datetime import datetime, timezone
from uuid import UUID

from engine.characters.pressure import apply_per_question_pressure_boost
from engine.resources.models import EffectDefinition, EffectFamily, ResourceBalance
from engine.resources.resolver import ResourceResolver


def test_rattle_effect_boosts_only_its_target_question_pressure() -> None:
    target = "00000000-0000-0000-0000-000000000203"
    activator = "00000000-0000-0000-0000-000000000201"
    resolver = ResourceResolver()
    resolver.set_balance(
        ResourceBalance(
            player_id=activator,
            session_id="00000000-0000-0000-0000-000000000040",
            current_amount=5,
            bank_cap=20,
            protected_floor=0,
        )
    )
    activation = resolver.activate(
        effect=EffectDefinition(
            effect_key="sabotage.rattle_the_witness",
            family=EffectFamily.witness_pressure,
            cost=2,
            requires_target=True,
            is_offensive=True,
        ),
        activator_id=activator,
        target_id=target,
        window_id="question-1",
        beat_id="beat-1",
        now=datetime.now(timezone.utc),
    )

    boosted = apply_per_question_pressure_boost(
        0.4,
        activation=activation,
        target_id=UUID(target),
        pressure_effect_key="sabotage.rattle_the_witness",
        boost=0.25,
    )
    unchanged = apply_per_question_pressure_boost(
        0.4,
        activation=activation,
        target_id=UUID("00000000-0000-0000-0000-000000000204"),
        pressure_effect_key="sabotage.rattle_the_witness",
        boost=0.25,
    )

    assert boosted == 0.65
    assert unchanged == 0.4
    assert (
        apply_per_question_pressure_boost(
            0.4,
            activation=None,
            target_id=UUID(target),
            pressure_effect_key="sabotage.rattle_the_witness",
            boost=0.25,
        )
        == 0.4
    )
