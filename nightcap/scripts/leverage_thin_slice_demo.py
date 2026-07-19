"""Thin-slice demo: AW-287 founder-review walkthrough, replayed on real code.

Replays docs/superpowers/specs/2026-07-18-aw287-leverage-walkthrough.md's six-step
scenario (Beat 3, "The Dig") against the actual ResourceResolver
(engine/resources/resolver.py) and the actual ContentEvent factories
(engine/resources/events.py), using the *real* EffectDefinitions configured on
nightcap/couch-race.arc.json (loaded via ArcDefinition.model_validate_json — no
hand-authored duplicate EffectDefinition literals).

This script is Nightcap-specific (named characters, a specific arc file) and lives
alongside nightcap/couch-race.arc.json rather than inside the game-agnostic
engine/ tree.

Run directly:

    python nightcap/scripts/leverage_thin_slice_demo.py

Every step prints: the player and effect involved, the balance before/after, and
(for steps that produce a ContentEvent) that event's target_audience and payload,
so a reviewer can visually confirm each privacy decision at a glance without
reading resolver internals.
"""

from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import UUID

REPO_ROOT = Path(__file__).resolve().parents[2]

# Allow `python nightcap/scripts/leverage_thin_slice_demo.py` to run directly (repo
# root is not installed as a package). Only needed when executed as a standalone
# script; a no-op when imported normally
# (e.g. `python -m nightcap.scripts.leverage_thin_slice_demo`).
if __package__ in (None, ""):
    sys.path.insert(0, str(REPO_ROOT))

from engine.arc.models import ArcDefinition  # noqa: E402
from engine.events.models import (  # noqa: E402
    AudienceTarget,
    ContentEvent,
    EventCategory,
)
from engine.resources.errors import TargetIneligibleError  # noqa: E402
from engine.resources.events import (  # noqa: E402
    build_balance_changed_event,
    build_effect_outcome_event,
    build_source_reveal_event,
)
from engine.resources.models import ResourceBalance  # noqa: E402
from engine.resources.resolver import ResourceResolver  # noqa: E402

ARC_PATH = REPO_ROOT / "nightcap" / "couch-race.arc.json"

SESSION_ID = UUID("00000000-0000-0000-0000-0000000000f0")
BEAT_ID = "dig"

PRIYA_ID = UUID("00000000-0000-0000-0000-000000000010")
MARCUS_ID = UUID("00000000-0000-0000-0000-000000000020")
JORDAN_ID = UUID("00000000-0000-0000-0000-000000000030")
ZOE_ID = UUID("00000000-0000-0000-0000-000000000040")

PLAYER_LABELS = {
    str(PRIYA_ID): "Priya",
    str(MARCUS_ID): "Marcus",
    str(JORDAN_ID): "Jordan",
    str(ZOE_ID): "Zoe",
}

STARTING_BALANCES = {
    str(PRIYA_ID): 12,
    str(MARCUS_ID): 4,
    str(JORDAN_ID): 2,
    str(ZOE_ID): 7,
}

BASE_TIME = datetime(2026, 7, 19, 20, 0, 0, tzinfo=timezone.utc)


def _tick(offset_seconds: int) -> datetime:
    return BASE_TIME + timedelta(seconds=offset_seconds)


def _label(player_id: str | None) -> str:
    if player_id is None:
        return "(whole table)"
    return PLAYER_LABELS.get(player_id, player_id)


def _print_header(step_number: int, title: str) -> None:
    print()
    print(f"--- Step {step_number}: {title} ---")


def _print_balance_change(
    resolver: ResourceResolver, player_id: str, before: int
) -> int:
    after = resolver.get_balance(player_id).current_amount
    print(f"    balance: {_label(player_id)} {before} -> {after}")
    return after


def _print_event(label: str, event: ContentEvent) -> None:
    recipient = _label(str(event.target_player_id) if event.target_player_id else None)
    print(
        f"    event[{label}]: type={event.event_type} "
        f"audience={event.target_audience.value} recipient={recipient}"
    )
    print(f"        payload={event.payload}")


def main() -> None:
    arc = ArcDefinition.model_validate_json(ARC_PATH.read_text("utf-8"))
    effects_by_key = {effect.effect_key: effect for effect in arc.resource_effects}
    print(f"Loaded {len(effects_by_key)} resource effects from {ARC_PATH}")

    resolver = ResourceResolver()
    for player_id, starting_amount in STARTING_BALANCES.items():
        resolver.set_balance(
            ResourceBalance(
                player_id=player_id,
                session_id=str(SESSION_ID),
                current_amount=0,
                bank_cap=20,
                protected_floor=0,
            )
        )
        resolver.grant(
            player_id=player_id,
            amount=starting_amount,
            source="scenario_opening_balance",
            beat_id=BEAT_ID,
            now=_tick(0),
        )

    print("Opening balances (Beat 3, The Dig):")
    for player_id in (PRIYA_ID, MARCUS_ID, JORDAN_ID, ZOE_ID):
        print(
            f"    {_label(str(player_id))}: {resolver.get_balance(str(player_id)).current_amount}"
        )

    # ------------------------------------------------------------------
    # Step 1: Priya spends her advantage effect on her own upcoming question.
    # ------------------------------------------------------------------
    _print_header(1, "Priya spends her advantage effect on her own question")
    step1_effect = effects_by_key["advantage.deep_read"]
    before = resolver.get_balance(str(PRIYA_ID)).current_amount
    resolver.activate(
        effect=step1_effect,
        activator_id=str(PRIYA_ID),
        target_id=None,
        window_id="w1-priya-question",
        beat_id=BEAT_ID,
        now=_tick(10),
    )
    _print_balance_change(resolver, str(PRIYA_ID), before)
    step1_balance_event = build_balance_changed_event(
        session_id=SESSION_ID,
        player_id=PRIYA_ID,
        new_amount=resolver.get_balance(str(PRIYA_ID)).current_amount,
        timestamp=_tick(10),
    )
    _print_event("balance-changed (public)", step1_balance_event)

    resolver.resolve_activation(window_id="w1-priya-question", now=_tick(11))
    step1_outcome_event = build_effect_outcome_event(
        session_id=SESSION_ID,
        effect_key=step1_effect.effect_key,
        outcome_payload={"detail": "sharpened private observation"},
        audience=AudienceTarget.specific_player,
        recipient_id=PRIYA_ID,
        category=EventCategory.private_delivery,
        timestamp=_tick(11),
    )
    _print_event("effect-outcome (private to Priya)", step1_outcome_event)

    resolver.open_new_window()

    # ------------------------------------------------------------------
    # Step 2: Marcus spends a witness-pressure sabotage targeting Jordan's
    # next question.
    # ------------------------------------------------------------------
    _print_header(2, "Marcus spends a witness-pressure sabotage targeting Jordan")
    step2_effect = effects_by_key["sabotage.rattle_the_witness"]
    before = resolver.get_balance(str(MARCUS_ID)).current_amount
    resolver.activate(
        effect=step2_effect,
        activator_id=str(MARCUS_ID),
        target_id=str(JORDAN_ID),
        window_id="w2-jordan-question",
        beat_id=BEAT_ID,
        now=_tick(20),
    )
    _print_balance_change(resolver, str(MARCUS_ID), before)
    step2_balance_event = build_balance_changed_event(
        session_id=SESSION_ID,
        player_id=MARCUS_ID,
        new_amount=resolver.get_balance(str(MARCUS_ID)).current_amount,
        timestamp=_tick(20),
    )
    _print_event("balance-changed (public)", step2_balance_event)
    print(
        "    (saboteur identity withheld from Jordan and the table until "
        "Jordan's question resolves)"
    )

    # ------------------------------------------------------------------
    # Step 3: Jordan's question resolves (source reveal fires on resolution),
    # and a second sabotage attempt against Jordan is rejected by the
    # post-target protection window.
    # ------------------------------------------------------------------
    _print_header(3, "Jordan's question resolves; post-target protection guards him")
    resolved = resolver.resolve_activation(
        window_id="w2-jordan-question", now=_tick(21)
    )

    step3_outcome_event = build_effect_outcome_event(
        session_id=SESSION_ID,
        effect_key=step2_effect.effect_key,
        outcome_payload={
            "suspect_state": "guarded",
            "answer": "a hedged, evasive answer",
        },
        audience=AudienceTarget.all,
        recipient_id=None,
        category=EventCategory.character_dialogue,
        timestamp=_tick(21),
    )
    _print_event(
        "effect-outcome (public: table hears the guarded answer)", step3_outcome_event
    )

    resolved_activation = resolved[0]
    step3_reveal_event = build_source_reveal_event(
        session_id=SESSION_ID,
        revealed_source_id=UUID(resolved_activation.activator_id),
        recipient_id=UUID(resolved_activation.target_id),
        timestamp=_tick(21),
    )
    _print_event("source-reveal (private to Jordan only)", step3_reveal_event)

    print(
        "    Attempting a second sabotage against Jordan right now (should be rejected)..."
    )
    rejected_attempt_effect = effects_by_key["sabotage.listen_in"]
    try:
        resolver.activate(
            effect=rejected_attempt_effect,
            activator_id=str(MARCUS_ID),
            target_id=str(JORDAN_ID),
            window_id="w2b-second-attempt-on-jordan",
            beat_id=BEAT_ID,
            now=_tick(22),
        )
        print("    UNEXPECTED: second sabotage against Jordan was NOT rejected")
    except TargetIneligibleError as error:
        print(f"    REJECTED as expected: {error}")
        print(
            f"    balance check: {_label(str(MARCUS_ID))} still "
            f"{resolver.get_balance(str(MARCUS_ID)).current_amount} "
            "(rejected attempt did not deduct cost)"
        )

    resolver.open_new_window()

    # ------------------------------------------------------------------
    # Step 4: Zoe activates a counterplay effect in anticipation, before
    # anyone targets her.
    # ------------------------------------------------------------------
    _print_header(4, "Zoe activates a counterplay effect in anticipation")
    step4_effect = effects_by_key["advantage.sting_operation"]
    before = resolver.get_balance(str(ZOE_ID)).current_amount
    resolver.activate(
        effect=step4_effect,
        activator_id=str(ZOE_ID),
        target_id=None,
        window_id="w3-zoe-arms-counterplay",
        beat_id=BEAT_ID,
        now=_tick(30),
    )
    _print_balance_change(resolver, str(ZOE_ID), before)
    step4_balance_event = build_balance_changed_event(
        session_id=SESSION_ID,
        player_id=ZOE_ID,
        new_amount=resolver.get_balance(str(ZOE_ID)).current_amount,
        timestamp=_tick(30),
    )
    _print_event("balance-changed (public)", step4_balance_event)
    print("    (armed, not resolved: nothing else visible yet)")

    resolver.open_new_window()

    # ------------------------------------------------------------------
    # Step 5: Priya spends an information-control sabotage targeting Zoe's
    # next private observation, but Zoe's counterplay effect is armed.
    # ------------------------------------------------------------------
    _print_header(
        5,
        "Priya targets Zoe with information-control sabotage - Zoe's counterplay is armed",
    )
    step5_effect = effects_by_key["sabotage.listen_in"]
    before = resolver.get_balance(str(PRIYA_ID)).current_amount
    resolver.activate(
        effect=step5_effect,
        activator_id=str(PRIYA_ID),
        target_id=str(ZOE_ID),
        window_id="w4-priya-targets-zoe",
        beat_id=BEAT_ID,
        now=_tick(40),
    )
    _print_balance_change(resolver, str(PRIYA_ID), before)
    step5_balance_event = build_balance_changed_event(
        session_id=SESSION_ID,
        player_id=PRIYA_ID,
        new_amount=resolver.get_balance(str(PRIYA_ID)).current_amount,
        timestamp=_tick(40),
    )
    _print_event("balance-changed (public)", step5_balance_event)

    countered = resolver.counter_and_reveal_source(
        countering_activator_id=str(ZOE_ID),
        countered_window_id="w4-priya-targets-zoe",
        now=_tick(40),
    )
    step5_reveal_event = build_source_reveal_event(
        session_id=SESSION_ID,
        revealed_source_id=UUID(countered.activator_id),
        recipient_id=ZOE_ID,
        timestamp=_tick(40),
    )
    print(
        "    Zoe's counterplay fires: Priya's sabotage lands weakened "
        "(partial copy only), and Priya's identity is exposed IMMEDIATELY "
        "(not waiting for question resolution) - private to Zoe only:"
    )
    _print_event(
        "source-reveal (immediate, private to Zoe only - never table-wide)",
        step5_reveal_event,
    )
    assert step5_reveal_event.target_audience is not AudienceTarget.all, (
        "counterplay reveal must never be broadcast table-wide"
    )

    # ------------------------------------------------------------------
    # Step 6: Beat 3 ends, Beat 4 begins - balances persist unchanged.
    # ------------------------------------------------------------------
    _print_header(6, "Beat 3 ends, Beat 4 begins - balances persist, no reset fires")
    print("    (no grant/activate/reset call made here - balances simply carry over)")
    for player_id in (PRIYA_ID, MARCUS_ID, JORDAN_ID, ZOE_ID):
        print(
            f"    {_label(str(player_id))}: {resolver.get_balance(str(player_id)).current_amount}"
        )

    expected_final = {
        str(PRIYA_ID): 8,
        str(MARCUS_ID): 2,
        str(JORDAN_ID): 2,
        str(ZOE_ID): 4,
    }
    for player_id, expected_amount in expected_final.items():
        actual_amount = resolver.get_balance(player_id).current_amount
        assert actual_amount == expected_amount, (
            f"{_label(player_id)}: expected {expected_amount}, got {actual_amount}"
        )
    print()
    print(
        "All six walkthrough steps replayed successfully; final balances match the approved scenario."
    )


if __name__ == "__main__":
    main()
