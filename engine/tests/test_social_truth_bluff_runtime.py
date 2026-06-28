from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import UUID

from api.schemas import (
    TmstPhaseStartedPayload,
    TmstPrivatePromptReadyPayload,
    TmstRevealResolvedPayload,
    TmstScoreboardReadyPayload,
    TmstSpotlightSkippedPayload,
    TmstSpotlightStartedPayload,
)
from engine.mini_games.loader import load_mini_game_package
from engine.mini_games.models import ClueVariant
from engine.mini_games.plugins import default_registry
from engine.mini_games.plugins._social_truth_bluff import SocialTruthBluffPlugin
from engine.mini_games.resolver import ResolvedMiniGameSnapshot
from engine.mini_games.runtime import (
    MechanicRegistry,
    MiniGameRuntime,
    _extract_authored_clues,
)

T0 = datetime(2026, 6, 28, 12, 0, 0, tzinfo=timezone.utc)
TMST_PATH = (
    Path(__file__).resolve().parents[2]
    / "nightcap"
    / "mini_games"
    / "tell-me-something-true"
)
PARTICIPANTS = [
    (UUID(int=1), UUID(int=101)),
    (UUID(int=2), UUID(int=102)),
    (UUID(int=3), UUID(int=103)),
    (UUID(int=4), UUID(int=104)),
]


class FakeDb:
    def __init__(self) -> None:
        self.added: list[object] = []

    def add(self, obj: object) -> None:
        self.added.append(obj)

    async def flush(self) -> None:
        return None


def load_tmst_snapshot(*, run_seed: str = "fixture-seed") -> ResolvedMiniGameSnapshot:
    loaded = load_mini_game_package(TMST_PATH)
    definition = loaded.definition
    return ResolvedMiniGameSnapshot(
        game_id=definition.game_id,
        definition_version=definition.version,
        source_content_mode=definition.content_mode,
        mechanic_type=definition.mechanic_type,
        participation_mode=definition.participation_mode.value,
        min_players=definition.min_players,
        max_players=definition.max_players,
        duration_seconds=definition.duration_seconds,
        rules=definition.rules,
        behavioral_outputs=tuple(definition.behavioral_outputs),
        clue_fallback=definition.clue_fallback,
        resolved_content={"run_seed": run_seed},
    )


def make_input_submission(
    plugin: SocialTruthBluffPlugin,
    character_id: UUID,
    *,
    statement_text: str,
    declared_truth: bool,
):
    return plugin._synthetic_submission(
        character_id,
        {
            "action": "input",
            "statement_text": statement_text,
            "declared_truth": declared_truth,
        },
    )


def make_vote_submission(
    plugin: SocialTruthBluffPlugin,
    character_id: UUID,
    *,
    target_character_id: UUID,
    vote: str,
):
    return plugin._synthetic_submission(
        character_id,
        {
            "action": "vote",
            "target_character_id": str(target_character_id),
            "vote": vote,
        },
    )


def test_tmst_registered_and_package_passes_strict_aw251_validation() -> None:
    registry = default_registry()
    plugin = registry.get("social-truth-bluff")

    assert plugin.mechanic_type == "social-truth-bluff"

    runtime = MiniGameRuntime(FakeDb(), object(), MechanicRegistry([plugin]))
    run = asyncio.run(runtime.create_run(UUID(int=999), load_tmst_snapshot()))

    assert run.game_id == "tell-me-something-true"


def test_input_deadline_auto_truth_starts_spotlight_deterministically() -> None:
    plugin = SocialTruthBluffPlugin()
    snapshot = load_tmst_snapshot(run_seed="auto-truth-seed")
    progress = plugin.initialize_state(snapshot, participants=PARTICIPANTS, now=T0)

    accepted = [
        make_input_submission(
            plugin, PARTICIPANTS[0][0], statement_text="A", declared_truth=True
        ),
        make_input_submission(
            plugin, PARTICIPANTS[1][0], statement_text="B", declared_truth=False
        ),
        make_input_submission(
            plugin, PARTICIPANTS[2][0], statement_text="C", declared_truth=True
        ),
    ]

    timed = plugin.on_deadline_expired(
        snapshot,
        state=progress.state or {},
        participants=PARTICIPANTS,
        accepted_submissions=accepted,
        now=T0 + timedelta(seconds=46),
    )

    assert timed.state is not None
    assert timed.state["phase"] == "spotlight"
    assert len(timed.synthetic_submissions) == 1
    assert timed.synthetic_submissions[0].payload["declared_truth"] is True
    assert timed.synthetic_submissions[0].payload["auto_submitted"] is True
    assert len(timed.state["spotlight_order"]) == 4
    assert any(event.event_type == "tmst_spotlight_started" for event in timed.events)


def test_disconnect_skip_advances_past_disconnected_spotlight() -> None:
    plugin = SocialTruthBluffPlugin()
    snapshot = load_tmst_snapshot(run_seed="skip-seed")
    state = (
        plugin.initialize_state(snapshot, participants=PARTICIPANTS, now=T0).state or {}
    )
    accepted = [
        make_input_submission(
            plugin, character_id, statement_text=str(index), declared_truth=True
        )
        for index, (character_id, _participant_id) in enumerate(PARTICIPANTS, start=1)
    ]
    spotlight = plugin.on_deadline_expired(
        snapshot,
        state=state,
        participants=PARTICIPANTS,
        accepted_submissions=accepted,
        now=T0 + timedelta(seconds=46),
    )
    spotlight_state = spotlight.state or {}
    first_target = UUID(spotlight_state["spotlight_order"][0])
    presence_submission = plugin._synthetic_submission(
        first_target,
        {"action": "presence", "connected": False},
    )

    skipped = plugin.on_submission(
        snapshot,
        state=spotlight_state,
        participants=PARTICIPANTS,
        submission=presence_submission,
        accepted_submissions=[*accepted, presence_submission],
        now=T0 + timedelta(seconds=47),
    )

    assert skipped.state is not None
    assert skipped.state["current_spotlight_index"] == 1
    skip_events = [
        event
        for event in skipped.events
        if event.event_type == "tmst_spotlight_skipped"
    ]
    assert len(skip_events) == 1
    assert skip_events[0].payload["target_character_id"] == str(first_target)


def test_vote_abstention_reveal_is_deterministic() -> None:
    plugin = SocialTruthBluffPlugin()
    snapshot = load_tmst_snapshot(run_seed="abstain-seed")
    state = (
        plugin.initialize_state(snapshot, participants=PARTICIPANTS, now=T0).state or {}
    )
    accepted = [
        make_input_submission(
            plugin, PARTICIPANTS[0][0], statement_text="A", declared_truth=False
        ),
        make_input_submission(
            plugin, PARTICIPANTS[1][0], statement_text="B", declared_truth=True
        ),
        make_input_submission(
            plugin, PARTICIPANTS[2][0], statement_text="C", declared_truth=True
        ),
        make_input_submission(
            plugin, PARTICIPANTS[3][0], statement_text="D", declared_truth=True
        ),
    ]
    spotlight = plugin.on_deadline_expired(
        snapshot,
        state=state,
        participants=PARTICIPANTS,
        accepted_submissions=accepted,
        now=T0 + timedelta(seconds=46),
    )
    spotlight_state = spotlight.state or {}
    target = UUID(spotlight_state["spotlight_order"][0])
    single_vote = make_vote_submission(
        plugin,
        PARTICIPANTS[1][0],
        target_character_id=target,
        vote="truth",
    )

    reveal = plugin.on_deadline_expired(
        snapshot,
        state=spotlight_state,
        participants=PARTICIPANTS,
        accepted_submissions=[*accepted, single_vote],
        now=T0 + timedelta(seconds=62),
    )

    reveal_events = [
        event for event in reveal.events if event.event_type == "tmst_reveal_resolved"
    ]
    assert len(reveal_events) == 1
    assert reveal_events[0].payload["vote_breakdown"]["abstain"] == 2


def test_score_output_is_identical_for_identical_fixture_and_has_no_clue_release() -> (
    None
):
    plugin = SocialTruthBluffPlugin()
    snapshot = load_tmst_snapshot(run_seed="deterministic-seed")
    submissions = [
        make_input_submission(
            plugin, PARTICIPANTS[0][0], statement_text="A", declared_truth=False
        ),
        make_input_submission(
            plugin, PARTICIPANTS[1][0], statement_text="B", declared_truth=True
        ),
        make_input_submission(
            plugin, PARTICIPANTS[2][0], statement_text="C", declared_truth=True
        ),
        make_input_submission(
            plugin, PARTICIPANTS[3][0], statement_text="D", declared_truth=True
        ),
        make_vote_submission(
            plugin,
            PARTICIPANTS[2][0],
            target_character_id=PARTICIPANTS[0][0],
            vote="truth",
        ),
        make_vote_submission(
            plugin,
            PARTICIPANTS[3][0],
            target_character_id=PARTICIPANTS[0][0],
            vote="truth",
        ),
        make_vote_submission(
            plugin,
            PARTICIPANTS[0][0],
            target_character_id=PARTICIPANTS[1][0],
            vote="truth",
        ),
    ]

    first = plugin.score(snapshot, submissions)
    second = plugin.score(snapshot, submissions)

    assert first == second
    assert first["round-resolved"] is True
    assert _extract_authored_clues(snapshot, ClueVariant.full) == []


def test_tmst_input_phase_events_validate_against_api_schema() -> None:
    plugin = SocialTruthBluffPlugin()
    snapshot = load_tmst_snapshot()
    progress = plugin.initialize_state(snapshot, participants=PARTICIPANTS, now=T0)

    phase_started = next(
        event for event in progress.events if event.event_type == "tmst_phase_started"
    )
    private_prompt_ready = next(
        event
        for event in progress.events
        if event.event_type == "tmst_private_prompt_ready"
    )

    assert phase_started.target_audience.value == "all"
    assert private_prompt_ready.target_audience.value == "specific_player"
    assert all(
        event.target_audience.value != "shared_display"
        for event in progress.events
        if event.event_type == "tmst_private_prompt_ready"
    )
    TmstPhaseStartedPayload.model_validate(phase_started.payload)
    TmstPrivatePromptReadyPayload.model_validate(private_prompt_ready.payload)


def test_tmst_spotlight_and_reveal_events_validate_against_api_schema() -> None:
    plugin = SocialTruthBluffPlugin()
    snapshot = load_tmst_snapshot(run_seed="schema-seed")
    state = (
        plugin.initialize_state(snapshot, participants=PARTICIPANTS, now=T0).state or {}
    )
    accepted = [
        make_input_submission(
            plugin, PARTICIPANTS[0][0], statement_text="A", declared_truth=False
        ),
        make_input_submission(
            plugin, PARTICIPANTS[1][0], statement_text="B", declared_truth=True
        ),
        make_input_submission(
            plugin, PARTICIPANTS[2][0], statement_text="C", declared_truth=True
        ),
        make_input_submission(
            plugin, PARTICIPANTS[3][0], statement_text="D", declared_truth=True
        ),
    ]
    spotlight = plugin.on_deadline_expired(
        snapshot,
        state=state,
        participants=PARTICIPANTS,
        accepted_submissions=accepted,
        now=T0 + timedelta(seconds=46),
    )
    spotlight_started = next(
        event
        for event in spotlight.events
        if event.event_type == "tmst_spotlight_started"
    )
    TmstSpotlightStartedPayload.model_validate(spotlight_started.payload)

    spotlight_state = spotlight.state or {}
    target = UUID(spotlight_state["spotlight_order"][0])
    reveal = plugin.on_deadline_expired(
        snapshot,
        state=spotlight_state,
        participants=PARTICIPANTS,
        accepted_submissions=[
            *accepted,
            make_vote_submission(
                plugin,
                PARTICIPANTS[1][0],
                target_character_id=target,
                vote="truth",
            ),
        ],
        now=T0 + timedelta(seconds=62),
    )
    reveal_resolved = next(
        event for event in reveal.events if event.event_type == "tmst_reveal_resolved"
    )
    TmstRevealResolvedPayload.model_validate(reveal_resolved.payload)


def test_tmst_skip_and_scoreboard_events_validate_against_api_schema() -> None:
    plugin = SocialTruthBluffPlugin()
    snapshot = load_tmst_snapshot(run_seed="skip-schema-seed")
    state = (
        plugin.initialize_state(snapshot, participants=PARTICIPANTS, now=T0).state or {}
    )
    accepted = [
        make_input_submission(
            plugin, character_id, statement_text=str(index), declared_truth=True
        )
        for index, (character_id, _participant_id) in enumerate(PARTICIPANTS, start=1)
    ]
    spotlight = plugin.on_deadline_expired(
        snapshot,
        state=state,
        participants=PARTICIPANTS,
        accepted_submissions=accepted,
        now=T0 + timedelta(seconds=46),
    )
    spotlight_state = spotlight.state or {}
    first_target = UUID(spotlight_state["spotlight_order"][0])
    skipped = plugin.on_submission(
        snapshot,
        state=spotlight_state,
        participants=PARTICIPANTS,
        submission=plugin._synthetic_submission(
            first_target, {"action": "presence", "connected": False}
        ),
        accepted_submissions=accepted,
        now=T0 + timedelta(seconds=47),
    )
    skip_event = next(
        event
        for event in skipped.events
        if event.event_type == "tmst_spotlight_skipped"
    )
    TmstSpotlightSkippedPayload.model_validate(skip_event.payload)

    scoreboard = plugin._scoreboard_progress(
        snapshot,
        accepted,
        T0 + timedelta(seconds=90),
        [],
        {"phase": "spotlight"},
    )
    scoreboard_ready = next(
        event
        for event in scoreboard.events
        if event.event_type == "tmst_scoreboard_ready"
    )
    TmstScoreboardReadyPayload.model_validate(scoreboard_ready.payload)
