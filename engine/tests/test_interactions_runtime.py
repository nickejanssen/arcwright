from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

from engine.arc.models import ArcDefinition
from engine.events.fanout import SessionConnectionRegistry
from engine.events.models import AudienceTarget
from engine.interactions.models import InteractionTarget
from engine.interactions.runtime import InteractionRuntime

REPO_ROOT = Path(__file__).resolve().parents[2]
ARC_PATH = REPO_ROOT / "nightcap" / "couch-race.arc.json"
SESSION_ID = UUID("00000000-0000-0000-0000-000000000201")
P1 = UUID("00000000-0000-0000-0000-000000000202")
P2 = UUID("00000000-0000-0000-0000-000000000203")


def test_arc_backed_runtime_resolves_and_routes_public_and_private_events() -> None:
    arc = ArcDefinition.model_validate_json(ARC_PATH.read_text("utf-8"))
    runtime = InteractionRuntime(arc_definition=arc, session_id=SESSION_ID, seed=7)
    window = runtime.open_window(
        beat_id="grill",
        window_id="runtime-window",
        round_index=0,
        participant_ids=[P1, P2],
        eligible_targets=[InteractionTarget(target_id="suspect")],
        held_evidence_by_participant={P1: set(), P2: {"evidence.behavioral_baseline"}},
        authorized_knowledge_context_ref="knowledge:runtime",
        claim_reference_ids=["claim:1"],
        evidence_reference_ids=["evidence:1"],
    )
    runtime.submit_selection(
        window_id=window.window_id,
        participant_id=P1,
        target_id="suspect",
        option_id="observe_behavior",
    )
    runtime.submit_selection(
        window_id=window.window_id,
        participant_id=P2,
        target_id="suspect",
        option_id="read_reaction",
    )

    resolution = runtime.lock_window(window_id=window.window_id)
    assert resolution.authorized_knowledge_context_ref == "knowledge:runtime"
    assert resolution.claim_reference_ids == ("claim:1",)
    assert resolution.evidence_reference_ids == ("evidence:1",)

    events = runtime.resolve_window(
        window_id=window.window_id,
        timestamp=datetime(2026, 7, 18, tzinfo=timezone.utc),
        answer_payload_by_group={
            "runtime-window:suspect:observe_behavior": {"text": "The room tightens."},
            "runtime-window:suspect:read_reaction": {"text": "The witness looks away."},
        },
    )

    public_events = [
        event for event in events if event.target_audience is AudienceTarget.all
    ]
    private_events = [
        event
        for event in events
        if event.target_audience is AudienceTarget.specific_player
    ]
    assert len(public_events) == 2
    assert len(private_events) == 2

    registry = SessionConnectionRegistry()
    p1_connection = registry.register_player(P1)
    p2_connection = registry.register_player(P2)
    display_connection = registry.register_display()
    assert set(registry.route(public_events[0])) == {
        p1_connection,
        p2_connection,
        display_connection,
    }
    assert registry.route(
        next(event for event in private_events if event.target_player_id == P1)
    ) == [p1_connection]
    assert registry.route(
        next(event for event in private_events if event.target_player_id == P2)
    ) == [p2_connection]
