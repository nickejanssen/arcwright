"""Privacy-matrix integration tests for ResourceRuntime.

Proves, end-to-end through the runtime (not just the resolver), that:
  - source-reveal scope is per-question (per interaction window), not per-round.
  - a Sting Operation counter's reveal event is never broadcast to everyone.

No shared "privacy harness" module exists in this codebase; each integration test
file writes its own direct assertions against event fields, following the pattern
in engine/tests/test_interactions_integration.py.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

import pytest

from engine.events.models import AudienceTarget
from engine.resources.models import (
    EffectActivation,
    EffectDefinition,
    EffectFamily,
    ResourceBalance,
)
from engine.resources.resolver import ResourceResolver
from engine.resources.runtime import ResourceRuntime

NOW = datetime(2026, 7, 19, tzinfo=timezone.utc)
SESSION_ID = UUID("00000000-0000-0000-0000-000000000040")

SABOTEUR_ONE = "00000000-0000-0000-0000-000000000201"
SABOTEUR_TWO = "00000000-0000-0000-0000-000000000202"
TARGET = "00000000-0000-0000-0000-000000000203"

RATTLE = EffectDefinition(
    effect_key="sabotage.rattle_the_witness",
    family=EffectFamily.witness_pressure,
    cost=2,
    requires_target=True,
    is_offensive=True,
)


def _balance(player_id: str) -> ResourceBalance:
    return ResourceBalance(
        player_id=player_id,
        session_id=str(SESSION_ID),
        current_amount=5,
        bank_cap=20,
        protected_floor=0,
    )


def make_resolver_and_runtime() -> tuple[ResourceResolver, ResourceRuntime]:
    resolver = ResourceResolver()
    resolver.set_balance(_balance(SABOTEUR_ONE))
    resolver.set_balance(_balance(SABOTEUR_TWO))
    resolver.set_balance(_balance(TARGET))
    return resolver, ResourceRuntime(resolver)


def test_reveal_scope_is_per_question_not_per_round() -> None:
    """Two questions (two windows) queue sabotage against the same target in one
    round. Resolving one window's question must not resolve or reveal the other's.
    """
    resolver, runtime = make_resolver_and_runtime()

    activation_one, _ = runtime.activate_effect(
        effect=RATTLE,
        activator_id=SABOTEUR_ONE,
        target_id=TARGET,
        window_id="round1-question1",
        beat_id="b1",
        now=NOW,
        session_id=SESSION_ID,
    )
    # A new question/window opens against the same target; post-target protection
    # from the first activation is cleared, exactly as InteractionDirector would do
    # when moving from one question to the next.
    resolver.open_new_window()
    activation_two, _ = runtime.activate_effect(
        effect=RATTLE,
        activator_id=SABOTEUR_TWO,
        target_id=TARGET,
        window_id="round1-question2",
        beat_id="b1",
        now=NOW,
        session_id=SESSION_ID,
    )

    assert activation_one.interaction_window_id != activation_two.interaction_window_id
    assert activation_one.target_id == activation_two.target_id == TARGET

    resolved_one, events_one = runtime.resolve_window(
        window_id="round1-question1",
        now=NOW,
        session_id=SESSION_ID,
        outcome_payload={"witness_state": "shaken"},
        outcome_audience=AudienceTarget.all,
    )

    reveal_events_one = [
        event
        for event in events_one
        if event.event_type == "resource_effect_source_revealed"
    ]
    assert len(reveal_events_one) == 1
    assert reveal_events_one[0].payload == {"revealed_source_id": SABOTEUR_ONE}
    assert reveal_events_one[0].target_player_id == UUID(TARGET)
    assert resolved_one.interaction_window_id == "round1-question1"

    # The second question's activation was untouched by resolving the first: it is
    # still resolvable on its own, and produces its own independent reveal naming
    # its own (different) activator. If the first resolve_window call had leaked
    # across the round instead of staying scoped to its own window, this second
    # call would either raise (already resolved) or reveal the wrong activator.
    resolved_two, events_two = runtime.resolve_window(
        window_id="round1-question2",
        now=NOW,
        session_id=SESSION_ID,
        outcome_payload={"witness_state": "shaken"},
        outcome_audience=AudienceTarget.all,
    )

    reveal_events_two = [
        event
        for event in events_two
        if event.event_type == "resource_effect_source_revealed"
    ]
    assert len(reveal_events_two) == 1
    assert reveal_events_two[0].payload == {"revealed_source_id": SABOTEUR_TWO}
    assert reveal_events_two[0].target_player_id == UUID(TARGET)
    assert resolved_two.interaction_window_id == "round1-question2"

    # Each window resolves exactly once; re-resolving the first window now fails,
    # proving question 1's activation was never re-touched by question 2's call
    # (and vice versa) — resolution and reveal are strictly per-window.
    with pytest.raises(ValueError):
        runtime.resolve_window(
            window_id="round1-question1",
            now=NOW,
            session_id=SESSION_ID,
            outcome_payload={"witness_state": "shaken"},
            outcome_audience=AudienceTarget.all,
        )


def test_sting_operation_counter_reveal_is_never_public() -> None:
    """A Sting Operation counter's reveal must go only to the countering player —
    it must never be broadcast with target_audience == AudienceTarget.all.
    """
    _, runtime = make_resolver_and_runtime()
    runtime.activate_effect(
        effect=RATTLE,
        activator_id=SABOTEUR_ONE,
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

    assert reveal_event.target_audience is not AudienceTarget.all
    assert reveal_event.target_audience is AudienceTarget.specific_player
    assert reveal_event.target_player_id == UUID(TARGET)
    assert reveal_event.payload == {"revealed_source_id": SABOTEUR_ONE}
    assert countered.source_reveal_at == NOW


ADVANTAGE = EffectDefinition(
    effect_key="advantage.deep_read",
    family=EffectFamily.insight,
    cost=1,
    requires_target=False,
)


def _run_seeded_sequence(resolver: ResourceResolver) -> list[EffectActivation]:
    """Fixed sequence of activate/resolve_activation calls, identical ids/amounts/
    timestamps every time it's run, exercised against whichever resolver is passed
    in. Returns every EffectActivation record the sequence produces, in call order,
    so the caller can compare full activation state between independent runs
    without reaching into resolver-private state.
    """
    resolver.set_balance(_balance(SABOTEUR_ONE))
    resolver.set_balance(_balance(SABOTEUR_TWO))
    resolver.set_balance(_balance(TARGET))

    records: list[EffectActivation] = []

    records.append(
        resolver.activate(
            effect=ADVANTAGE,
            activator_id=SABOTEUR_ONE,
            target_id=None,
            window_id="round1-question1",
            beat_id="b1",
            now=NOW,
        )
    )
    records.append(
        resolver.activate(
            effect=RATTLE,
            activator_id=SABOTEUR_TWO,
            target_id=TARGET,
            window_id="round1-question2",
            beat_id="b1",
            now=NOW,
        )
    )
    records.append(resolver.resolve_activation(window_id="round1-question2", now=NOW))

    resolver.open_new_window()
    records.append(
        resolver.activate(
            effect=ADVANTAGE,
            activator_id=TARGET,
            target_id=None,
            window_id="round1-question3",
            beat_id="b1",
            now=NOW,
        )
    )

    return records


def test_seeded_replay_is_deterministic() -> None:
    """Two independent ResourceResolver instances fed the identical sequence of
    activate/resolve_activation calls, with identical ids, amounts, and timestamps,
    must end up with equal ResourceBalance state for every player and equal
    EffectActivation records. Compared via model_dump() equality, not identity,
    since the two runs produce distinct object instances.
    """
    resolver_a = ResourceResolver()
    resolver_b = ResourceResolver()

    activations_a = _run_seeded_sequence(resolver_a)
    activations_b = _run_seeded_sequence(resolver_b)

    for player_id in (SABOTEUR_ONE, SABOTEUR_TWO, TARGET):
        assert (
            resolver_a.get_balance(player_id).model_dump()
            == resolver_b.get_balance(player_id).model_dump()
        )

    assert len(activations_a) == len(activations_b)
    assert [activation.model_dump() for activation in activations_a] == [
        activation.model_dump() for activation in activations_b
    ]
