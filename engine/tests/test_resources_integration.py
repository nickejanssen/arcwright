"""Privacy-matrix integration tests for ResourceRuntime.

Proves, end-to-end through the runtime (not just the resolver), that:
  - source-reveal scope is per-question (per interaction window), not per-round.
  - a Sting Operation counter's reveal event is never broadcast to everyone.

No shared "privacy harness" module exists in this codebase; each integration test
file writes its own direct assertions against event fields, following the pattern
in engine/tests/test_interactions_integration.py.
"""

from __future__ import annotations

import ast
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

import pytest

from engine.arc.models import ArcDefinition
from engine.events.models import AudienceTarget, EventCategory
from engine.resources.errors import ActivationNotFoundError
from engine.resources.models import (
    EffectActivation,
    EffectDefinition,
    EffectFamily,
    ResourceBalance,
)
from engine.resources.resolver import ResourceResolver
from engine.resources.runtime import ResourceRuntime

REPO_ROOT = Path(__file__).resolve().parents[2]
COUCH_RACE_PATH = REPO_ROOT / "nightcap" / "couch-race.arc.json"
IMPOSTER_ARC_PATH = REPO_ROOT / "nightcap" / "arc.json"

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
        outcome_category=EventCategory.character_dialogue,
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
        outcome_category=EventCategory.character_dialogue,
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
    with pytest.raises(ActivationNotFoundError):
        runtime.resolve_window(
            window_id="round1-question1",
            now=NOW,
            session_id=SESSION_ID,
            outcome_payload={"witness_state": "shaken"},
            outcome_audience=AudienceTarget.all,
            outcome_category=EventCategory.character_dialogue,
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


# AW-287 Task 8 - the six launch-set Leverage effects configured on the real
# Couch Race arc JSON. Costs below are tuning placeholders per spec 0075's
# "Risks and Unknowns" section and are expected to be retuned after
# rehearsal telemetry.
COUCH_RACE_LAUNCH_EFFECT_KEYS = {
    "advantage.deep_read",
    "advantage.follow_the_thread",
    "advantage.sting_operation",
    "sabotage.rattle_the_witness",
    "sabotage.listen_in",
    "sabotage.make_them_wait",
}


def test_couch_race_arc_configures_six_launch_set_effects() -> None:
    arc = ArcDefinition.model_validate_json(COUCH_RACE_PATH.read_text("utf-8"))

    assert len(arc.resource_effects) == 6
    effect_keys = {effect.effect_key for effect in arc.resource_effects}
    assert effect_keys == COUCH_RACE_LAUNCH_EFFECT_KEYS


def test_couch_race_launch_effects_match_spec_table() -> None:
    arc = ArcDefinition.model_validate_json(COUCH_RACE_PATH.read_text("utf-8"))
    by_key = {effect.effect_key: effect for effect in arc.resource_effects}

    deep_read = by_key["advantage.deep_read"]
    assert deep_read.family is EffectFamily.insight
    assert deep_read.cost == 2
    assert deep_read.requires_target is False
    assert deep_read.is_offensive is False
    assert deep_read.is_information_control is False

    follow_the_thread = by_key["advantage.follow_the_thread"]
    assert follow_the_thread.family is EffectFamily.access
    assert follow_the_thread.cost == 2
    assert follow_the_thread.requires_target is False
    assert follow_the_thread.is_offensive is False
    assert follow_the_thread.is_information_control is False

    sting_operation = by_key["advantage.sting_operation"]
    assert sting_operation.family is EffectFamily.counterplay
    assert sting_operation.cost == 3
    assert sting_operation.requires_target is False
    assert sting_operation.is_offensive is False
    assert sting_operation.is_information_control is False

    rattle_the_witness = by_key["sabotage.rattle_the_witness"]
    assert rattle_the_witness.family is EffectFamily.witness_pressure
    assert rattle_the_witness.cost == 2
    assert rattle_the_witness.requires_target is True
    assert rattle_the_witness.is_offensive is True
    assert rattle_the_witness.is_information_control is False

    listen_in = by_key["sabotage.listen_in"]
    assert listen_in.family is EffectFamily.information_control
    assert listen_in.cost == 2
    assert listen_in.requires_target is True
    assert listen_in.is_offensive is True
    assert listen_in.is_information_control is True

    make_them_wait = by_key["sabotage.make_them_wait"]
    assert make_them_wait.family is EffectFamily.tempo
    assert make_them_wait.cost == 2
    assert make_them_wait.requires_target is True
    assert make_them_wait.is_offensive is True
    assert make_them_wait.is_information_control is False


def test_imposter_arc_has_no_resource_effects_configured() -> None:
    """AW-287 acceptance criterion: games without Leverage configuration
    remain unaffected. The Imposter Variant arc does not author
    resource_effects, and the new field must default to an empty tuple/list
    rather than requiring every existing arc file to be touched.
    """
    arc = ArcDefinition.model_validate_json(IMPOSTER_ARC_PATH.read_text("utf-8"))
    assert arc.resource_effects == []


# ---------------------------------------------------------------------------
# AW-287 Task 9 - protected-earn-path guardrail (spec 0075).
#
# Proves, over a seeded multi-beat session driven directly through
# ResourceResolver, that:
#   1. mini-game rewards cannot create an unrecoverable lead — a player who
#      wins every mini-game grant across the whole session is still bounded
#      by bank_cap, so the gap to any other player is capped at
#      (bank_cap - protected_floor) no matter how many more mini-games they
#      win; and
#   2. every player has a protected earn path — a non-mini-game grant
#      source (e.g. a per-beat participation stipend) that on its own is
#      enough to bring every player who never won a mini-game up to
#      protected_floor by session end.
# ---------------------------------------------------------------------------

WINNER = "00000000-0000-0000-0000-000000000301"
NON_WINNERS = (
    "00000000-0000-0000-0000-000000000302",
    "00000000-0000-0000-0000-000000000303",
    "00000000-0000-0000-0000-000000000304",
)
ALL_PLAYERS = (WINNER, *NON_WINNERS)

PROTECTED_FLOOR = 6
BANK_CAP = 20
STIPEND_PER_BEAT = 2  # protected-earn path: paid to every player, every beat
MINI_GAME_REWARD_PER_BEAT = 10  # paid only to the winner
BEATS = ("beat_1", "beat_2", "beat_3")


def test_protected_earn_path_and_bounded_lead_hold_over_seeded_session() -> None:
    resolver = ResourceResolver()
    for player_id in ALL_PLAYERS:
        resolver.set_balance(
            ResourceBalance(
                player_id=player_id,
                session_id=str(SESSION_ID),
                current_amount=0,
                bank_cap=BANK_CAP,
                protected_floor=PROTECTED_FLOOR,
            )
        )

    for beat_id in BEATS:
        # Protected earn path: every player, including the winner, receives
        # the flat per-beat stipend regardless of mini-game outcomes.
        for player_id in ALL_PLAYERS:
            resolver.grant(
                player_id=player_id,
                amount=STIPEND_PER_BEAT,
                source="protected_earn_stipend",
                beat_id=beat_id,
                now=NOW,
            )
        # Mini-game reward: only the winner ever receives this grant, every
        # beat, for the entire session. The three non-winners receive zero
        # mini-game grants across all three beats.
        resolver.grant(
            player_id=WINNER,
            amount=MINI_GAME_REWARD_PER_BEAT,
            source="mini_game_reward",
            beat_id=beat_id,
            now=NOW,
        )

    # AC: every player who never won a mini-game still reached
    # protected_floor by session end, purely via the protected-earn path.
    for player_id in NON_WINNERS:
        balance = resolver.get_balance(player_id)
        assert balance.current_amount >= balance.protected_floor
        # Reached it via the stipend alone: three beats at STIPEND_PER_BEAT.
        assert balance.current_amount == 3 * STIPEND_PER_BEAT

    # AC: mini-game rewards cannot create an unrecoverable lead. The winner's
    # balance is bounded by bank_cap even though every mini-game grant across
    # every beat went to them, and the raw (uncapped) total they'd otherwise
    # have accumulated (3 * (10 + 2) = 36) would have far exceeded it.
    winner_balance = resolver.get_balance(WINNER)
    assert winner_balance.current_amount == BANK_CAP

    for player_id in NON_WINNERS:
        gap = (
            winner_balance.current_amount
            - resolver.get_balance(player_id).current_amount
        )
        assert gap <= BANK_CAP - PROTECTED_FLOOR

    # One more mini-game win for the winner, after the seeded session's three
    # beats, does not widen the lead any further — the cap already holds it,
    # proving the lead stays bounded no matter how many more times they win.
    resolver.grant(
        player_id=WINNER,
        amount=MINI_GAME_REWARD_PER_BEAT,
        source="mini_game_reward",
        beat_id="beat_4",
        now=NOW,
    )
    assert resolver.get_balance(WINNER).current_amount == BANK_CAP


# ---------------------------------------------------------------------------
# Spec 0075 acceptance criterion: "No effect can change canonical case truth,
# delete evidence, or create an unfalsifiable clue" (property/invariance test
# across all six configured effects).
#
# ResourceResolver has zero coupling to case-truth state by construction: the
# whole engine/resources/ module tree never imports engine.case (the module
# that owns canonical case-truth state), and ResourceResolver's public
# interface exposes no method or attribute referencing "truth", "killer", or
# "evidence" as a mutation target. These tests make that invariant explicit
# and checkable, rather than leaving it implicit in the module boundary.
# ---------------------------------------------------------------------------

CASE_TRUTH_TERMS = ("truth", "killer", "evidence")
RESOURCES_MODULE_DIR = REPO_ROOT / "engine" / "resources"


def _resolver_public_interface_names() -> list[str]:
    return [name for name in dir(ResourceResolver) if not name.startswith("_")]


def test_resource_resolver_public_interface_has_no_case_truth_surface() -> None:
    """ResourceResolver exposes no method or attribute referencing case-truth
    concepts - the invariant that makes "no effect can change canonical case
    truth" true by construction, not by convention.
    """
    violations = [
        name
        for name in _resolver_public_interface_names()
        for term in CASE_TRUTH_TERMS
        if term in name.lower()
    ]
    assert not violations, (
        f"ResourceResolver's public interface references case-truth concepts: "
        f"{violations}"
    )


def test_resources_module_tree_never_imports_case_module() -> None:
    """engine/resources/ has zero import coupling to engine.case, reinforcing
    that the invariant above isn't just an accident of today's method names -
    there is no import path through which a resource effect could reach
    canonical case-truth state.
    """
    violations: list[str] = []
    for path in sorted(RESOURCES_MODULE_DIR.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and (node.module or "").startswith(
                "engine.case"
            ):
                violations.append(f"{path.name} imports {node.module}")
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith("engine.case"):
                        violations.append(f"{path.name} imports {alias.name}")

    assert not violations, (
        f"engine/resources/ has an import dependency on engine.case: {violations}"
    )


def test_activating_every_couch_race_launch_effect_touches_no_case_truth_state() -> (
    None
):
    """Activates each of the six real launch-set effects - loaded from the
    actual arc JSON, not hand-authored duplicates - against a fresh resolver,
    and asserts the resulting EffectActivation carries no case-truth-shaped
    field name or value. The concrete, per-effect instance of the invariance
    property above.
    """
    arc = ArcDefinition.model_validate_json(COUCH_RACE_PATH.read_text("utf-8"))
    assert len(arc.resource_effects) == 6

    for index, effect in enumerate(arc.resource_effects):
        resolver = ResourceResolver()
        activator_id = f"invariance-activator-{index}"
        target_id = f"invariance-target-{index}"
        resolver.set_balance(_balance(activator_id))
        resolver.set_balance(_balance(target_id))

        activation = resolver.activate(
            effect=effect,
            activator_id=activator_id,
            target_id=target_id if effect.requires_target else None,
            window_id=f"invariance-check-{index}",
            beat_id="b1",
            now=NOW,
        )

        activation_dump = activation.model_dump()
        for key, value in activation_dump.items():
            for term in CASE_TRUTH_TERMS:
                assert term not in key.lower(), (
                    f"{effect.effect_key}: activation field {key!r} references "
                    f"case-truth concept {term!r}"
                )
                assert term not in str(value).lower(), (
                    f"{effect.effect_key}: activation field {key!r} value "
                    f"references case-truth concept {term!r}"
                )


# ---------------------------------------------------------------------------
# Spec 0075 acceptance criterion: "ResourceBalance.current_amount persists
# unchanged across a beat-transition test" - as an automated pytest, not just
# narratively demonstrated in nightcap/scripts/leverage_thin_slice_demo.py.
# ---------------------------------------------------------------------------


def test_resource_balance_persists_unchanged_across_beat_transition() -> None:
    """resolver.open_new_window() is what InteractionDirector calls at a beat
    boundary (clearing post-target protection for the next question/beat). No
    grant/spend/reset call happens here - the beat boundary itself must not
    touch balance state for anyone, activator or otherwise.
    """
    resolver, runtime = make_resolver_and_runtime()

    runtime.activate_effect(
        effect=RATTLE,
        activator_id=SABOTEUR_ONE,
        target_id=TARGET,
        window_id="beat-transition-window",
        beat_id="b1",
        now=NOW,
        session_id=SESSION_ID,
    )

    balances_before = {
        player_id: resolver.get_balance(player_id).current_amount
        for player_id in (SABOTEUR_ONE, SABOTEUR_TWO, TARGET)
    }

    resolver.open_new_window()

    for player_id in (SABOTEUR_ONE, SABOTEUR_TWO, TARGET):
        assert (
            resolver.get_balance(player_id).current_amount == balances_before[player_id]
        )
