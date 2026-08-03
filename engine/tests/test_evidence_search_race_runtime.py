from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import UUID

import pytest

from engine.mini_games.loader import load_mini_game_package
from engine.mini_games.plugins._evidence_search_race import EvidenceSearchRacePlugin
from engine.mini_games.resolver import ResolvedMiniGameSnapshot

T0 = datetime(2026, 8, 2, 20, 0, 0, tzinfo=timezone.utc)
PACKAGE_PATH = (
    Path(__file__).resolve().parents[2] / "nightcap" / "mini_games" / "scene-sweep"
)
PARTICIPANTS_4 = [
    (UUID(int=1), UUID(int=101)),
    (UUID(int=2), UUID(int=102)),
    (UUID(int=3), UUID(int=103)),
    (UUID(int=4), UUID(int=104)),
]


def load_snapshot(*, run_seed: str = "fixture-seed") -> ResolvedMiniGameSnapshot:
    loaded = load_mini_game_package(PACKAGE_PATH)
    definition = loaded.definition
    resolved_content = dict(definition.authored_content or {})
    resolved_content["run_seed"] = run_seed
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
        resolved_content=resolved_content,
    )


def make_submission(
    *,
    submission_id: str,
    character_id: UUID,
    object_id: str,
    submitted_at: datetime,
) -> "FakeSubmission":
    return FakeSubmission(
        submission_id=submission_id,
        character_id=character_id,
        payload={"action": "claim", "object_id": object_id},
        submitted_at=submitted_at,
    )


class FakeSubmission:
    """Minimal stand-in for engine.db.orm.MiniGameSubmission's read surface."""

    def __init__(
        self,
        *,
        submission_id: str,
        character_id: UUID,
        payload: dict,
        submitted_at: datetime,
    ) -> None:
        self.submission_id = submission_id
        self.character_id = character_id
        self.payload = payload
        self.submitted_at = submitted_at


def test_scene_sweep_registered_and_package_passes_strict_validation() -> None:
    loaded = load_mini_game_package(PACKAGE_PATH)
    assert loaded.definition.mechanic_type == EvidenceSearchRacePlugin.mechanic_type


def test_validate_payload_accepts_valid_claim() -> None:
    plugin = EvidenceSearchRacePlugin()
    plugin.validate_payload({"action": "claim", "object_id": "slot-1"})


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"action": "vote"},
        {"action": "claim"},
        {"action": "claim", "object_id": ""},
        {"action": "claim", "object_id": 5},
    ],
)
def test_validate_payload_rejects_invalid_shapes(payload: dict) -> None:
    plugin = EvidenceSearchRacePlugin()
    with pytest.raises(ValueError):
        plugin.validate_payload(payload)


def test_real_object_id_uses_generation_supplied_value_when_present() -> None:
    """Proves the case-grounded path: when content resolution (AW-250) has
    written real_object_id into resolved_content, the plugin must use that
    exact value rather than its own seeded-hash fallback — this is what
    makes "which archetype is real" mean something in the actual case,
    per the design doc's non-negotiable that the mini-game never invents
    this independently of resolved session state.
    """
    plugin = EvidenceSearchRacePlugin()
    snapshot = load_snapshot(run_seed="seed-generation-supplied")
    valid_slot_ids = [slot["slot_id"] for slot in plugin._object_slots(snapshot)]
    # Deliberately pick whichever slot the hash fallback would NOT pick, so
    # a test that accidentally ignored the supplied value would fail loudly.
    fallback_pick = plugin._real_object_id(
        load_snapshot(run_seed="seed-generation-supplied")
    )
    forced_choice = next(
        slot_id for slot_id in valid_slot_ids if slot_id != fallback_pick
    )
    resolved_content = dict(snapshot.resolved_content)
    resolved_content["real_object_id"] = forced_choice
    snapshot_with_generation = snapshot.model_copy(
        update={"resolved_content": resolved_content}
    )

    assert plugin._real_object_id(snapshot_with_generation) == forced_choice


def test_real_object_id_falls_back_to_hash_when_not_supplied() -> None:
    plugin = EvidenceSearchRacePlugin()
    snapshot = load_snapshot(run_seed="seed-no-generation")
    assert "real_object_id" not in snapshot.resolved_content
    real_id = plugin._real_object_id(snapshot)
    assert real_id in {slot["slot_id"] for slot in plugin._object_slots(snapshot)}


def test_real_object_id_is_deterministic_across_calls() -> None:
    plugin = EvidenceSearchRacePlugin()
    snapshot = load_snapshot(run_seed="seed-a")
    first = plugin._real_object_id(snapshot)
    second = plugin._real_object_id(snapshot)
    assert first is not None
    assert first == second


def test_real_object_id_changes_with_seed() -> None:
    plugin = EvidenceSearchRacePlugin()
    seeds_and_results = {
        seed: plugin._real_object_id(load_snapshot(run_seed=seed))
        for seed in ("seed-a", "seed-b", "seed-c", "seed-d", "seed-e")
    }
    # Not asserting a specific distribution, just that seed changes the pick
    # for at least one pair (guards against an accidental constant return).
    assert len(set(seeds_and_results.values())) > 1


def test_initialize_state_includes_real_object_in_active_set() -> None:
    plugin = EvidenceSearchRacePlugin()
    snapshot = load_snapshot(run_seed="seed-init")
    real_id = plugin._real_object_id(snapshot)

    progress = plugin.initialize_state(snapshot, participants=PARTICIPANTS_4, now=T0)

    active_ids = progress.state["active_object_ids"]
    assert len(active_ids) == 5  # 4 players -> 5 objects per rules table
    assert real_id in active_ids
    assert len(progress.events) == 1
    assert progress.events[0].event_type == "scene_sweep_board_started"
    for obj in progress.events[0].payload["objects"]:
        assert "archetype" in obj and "position" in obj


def test_on_submission_rejects_object_not_on_board() -> None:
    plugin = EvidenceSearchRacePlugin()
    snapshot = load_snapshot(run_seed="seed-reject")
    progress = plugin.initialize_state(snapshot, participants=PARTICIPANTS_4, now=T0)
    off_board = next(
        slot["slot_id"]
        for slot in plugin._object_slots(snapshot)
        if slot["slot_id"] not in progress.state["active_object_ids"]
    )
    submission = make_submission(
        submission_id="s1",
        character_id=PARTICIPANTS_4[0][0],
        object_id=off_board,
        submitted_at=T0,
    )
    with pytest.raises(ValueError, match="not on this round's board"):
        plugin.on_submission(
            snapshot,
            state=progress.state,
            participants=PARTICIPANTS_4,
            submission=submission,  # type: ignore[arg-type]
            accepted_submissions=[submission],  # type: ignore[list-item]
            now=T0,
        )


def test_on_submission_rejects_double_claim() -> None:
    plugin = EvidenceSearchRacePlugin()
    snapshot = load_snapshot(run_seed="seed-double")
    progress = plugin.initialize_state(snapshot, participants=PARTICIPANTS_4, now=T0)
    object_id = progress.state["active_object_ids"][0]
    first = make_submission(
        submission_id="s1",
        character_id=PARTICIPANTS_4[0][0],
        object_id=object_id,
        submitted_at=T0,
    )
    first_progress = plugin.on_submission(
        snapshot,
        state=progress.state,
        participants=PARTICIPANTS_4,
        submission=first,  # type: ignore[arg-type]
        accepted_submissions=[first],  # type: ignore[list-item]
        now=T0,
    )
    second = make_submission(
        submission_id="s2",
        character_id=PARTICIPANTS_4[1][0],
        object_id=object_id,
        submitted_at=T0 + timedelta(seconds=1),
    )
    with pytest.raises(ValueError, match="already been claimed"):
        plugin.on_submission(
            snapshot,
            state=first_progress.state,
            participants=PARTICIPANTS_4,
            submission=second,  # type: ignore[arg-type]
            accepted_submissions=[first, second],  # type: ignore[list-item]
            now=T0,
        )


def test_board_exhaustion_sets_finalize_status_completed() -> None:
    plugin = EvidenceSearchRacePlugin()
    snapshot = load_snapshot(run_seed="seed-exhaust")
    progress = plugin.initialize_state(snapshot, participants=PARTICIPANTS_4, now=T0)
    active_ids = list(progress.state["active_object_ids"])
    state = dict(progress.state)
    accepted: list[FakeSubmission] = []
    last_progress = None
    for index, object_id in enumerate(active_ids):
        submission = make_submission(
            submission_id=f"s{index}",
            character_id=PARTICIPANTS_4[index % len(PARTICIPANTS_4)][0],
            object_id=object_id,
            submitted_at=T0 + timedelta(seconds=index),
        )
        accepted.append(submission)
        last_progress = plugin.on_submission(
            snapshot,
            state=state,
            participants=PARTICIPANTS_4,
            submission=submission,  # type: ignore[arg-type]
            accepted_submissions=list(accepted),  # type: ignore[list-item]
            now=T0 + timedelta(seconds=index),
        )
        state = dict(last_progress.state)

    assert last_progress is not None
    assert last_progress.finalize_status == "completed"


def test_claiming_real_object_alone_does_not_finalize_early() -> None:
    plugin = EvidenceSearchRacePlugin()
    snapshot = load_snapshot(run_seed="seed-no-early-exit")
    real_id = plugin._real_object_id(snapshot)
    progress = plugin.initialize_state(snapshot, participants=PARTICIPANTS_4, now=T0)
    submission = make_submission(
        submission_id="s1",
        character_id=PARTICIPANTS_4[0][0],
        object_id=real_id,
        submitted_at=T0,
    )
    result = plugin.on_submission(
        snapshot,
        state=progress.state,
        participants=PARTICIPANTS_4,
        submission=submission,  # type: ignore[arg-type]
        accepted_submissions=[submission],  # type: ignore[list-item]
        now=T0,
    )
    assert result.finalize_status is None


def test_on_deadline_expired_always_times_out() -> None:
    plugin = EvidenceSearchRacePlugin()
    snapshot = load_snapshot(run_seed="seed-deadline")
    progress = plugin.initialize_state(snapshot, participants=PARTICIPANTS_4, now=T0)
    result = plugin.on_deadline_expired(
        snapshot,
        state=progress.state,
        participants=PARTICIPANTS_4,
        accepted_submissions=[],
        now=T0 + timedelta(seconds=105),
    )
    assert result.finalize_status == "timed_out"


def test_score_reports_success_when_real_object_claimed() -> None:
    plugin = EvidenceSearchRacePlugin()
    snapshot = load_snapshot(run_seed="seed-score-success")
    real_id = plugin._real_object_id(snapshot)
    finder = PARTICIPANTS_4[2][0]
    submission = make_submission(
        submission_id="s1",
        character_id=finder,
        object_id=real_id,
        submitted_at=T0 + timedelta(seconds=10),
    )
    outcome = plugin.score(snapshot, [submission])  # type: ignore[list-item]
    assert outcome["real-object-claimed"] is True
    assert outcome["finder-character-id"] == str(finder)


def test_score_reports_fallback_when_real_object_never_claimed() -> None:
    plugin = EvidenceSearchRacePlugin()
    snapshot = load_snapshot(run_seed="seed-score-fallback")
    progress = plugin.initialize_state(snapshot, participants=PARTICIPANTS_4, now=T0)
    decoy_id = next(
        object_id
        for object_id in progress.state["active_object_ids"]
        if object_id != plugin._real_object_id(snapshot)
    )
    submission = make_submission(
        submission_id="s1",
        character_id=PARTICIPANTS_4[0][0],
        object_id=decoy_id,
        submitted_at=T0 + timedelta(seconds=5),
    )
    outcome = plugin.score(snapshot, [submission])  # type: ignore[list-item]
    assert outcome["real-object-claimed"] is False
    assert outcome["finder-character-id"] is None
    assert outcome["decoys-claimed"][str(PARTICIPANTS_4[0][0])] == 1
