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


def test_score_credits_the_winner_not_the_loser_of_a_claim_race() -> None:
    """Reproduces the runtime quirk documented in
    _accepted_claims_by_object: submit_action (engine/mini_games/runtime.py)
    flushes a submission row with is_accepted=True before on_submission's
    claim arbitration runs, so a losing race for an already-claimed
    object_id can still land in `submissions` with is_accepted=True even
    though on_submission rejected it. score() must credit the earlier
    (winning) claim, not whichever submission happens to sort last.
    """
    plugin = EvidenceSearchRacePlugin()
    snapshot = load_snapshot(run_seed="seed-race-credit")
    real_id = plugin._real_object_id(snapshot)
    winner = PARTICIPANTS_4[0][0]
    loser = PARTICIPANTS_4[1][0]
    winning_submission = make_submission(
        submission_id="s1",
        character_id=winner,
        object_id=real_id,
        submitted_at=T0,
    )
    losing_submission = make_submission(
        submission_id="s2",
        character_id=loser,
        object_id=real_id,
        submitted_at=T0 + timedelta(seconds=1),
    )
    # Both submissions are "accepted" in the DB sense (the runtime's own
    # is_accepted=True-before-on_submission-runs quirk), even though the
    # loser was actually rejected by on_submission's claim arbitration.
    outcome = plugin.score(snapshot, [winning_submission, losing_submission])  # type: ignore[list-item]
    assert outcome["finder-character-id"] == str(winner)
    assert outcome["real-object-claimed"] is True
    assert outcome["claimed-object-ids"] == [real_id]


def test_score_does_not_double_count_a_duplicate_decoy_claim() -> None:
    """Same runtime quirk as the winner/loser race, but for a decoy object:
    a rejected duplicate claim on the same decoy object_id must not inflate
    decoys-claimed beyond the single accepted (earliest) claim.
    """
    plugin = EvidenceSearchRacePlugin()
    snapshot = load_snapshot(run_seed="seed-race-decoy")
    progress = plugin.initialize_state(snapshot, participants=PARTICIPANTS_4, now=T0)
    real_id = plugin._real_object_id(snapshot)
    decoy_id = next(
        object_id
        for object_id in progress.state["active_object_ids"]
        if object_id != real_id
    )
    first_claimant = PARTICIPANTS_4[0][0]
    second_claimant = PARTICIPANTS_4[1][0]
    first_submission = make_submission(
        submission_id="s1",
        character_id=first_claimant,
        object_id=decoy_id,
        submitted_at=T0,
    )
    duplicate_submission = make_submission(
        submission_id="s2",
        character_id=second_claimant,
        object_id=decoy_id,
        submitted_at=T0 + timedelta(seconds=1),
    )
    outcome = plugin.score(snapshot, [first_submission, duplicate_submission])  # type: ignore[list-item]
    assert outcome["decoys-claimed"] == {str(first_claimant): 1}
    assert str(second_claimant) not in outcome["decoys-claimed"]
    assert outcome["claimed-object-ids"] == [decoy_id]


def test_real_object_id_falls_back_when_generation_supplies_invalid_slot() -> None:
    """A generation-supplied real_object_id that doesn't match any authored
    slot_id (e.g. a stale or malformed generation result) must not be
    trusted; the plugin should fall back to the deterministic seeded-hash
    pick exactly as if no real_object_id had been supplied at all.
    """
    plugin = EvidenceSearchRacePlugin()
    snapshot = load_snapshot(run_seed="seed-invalid-generated")
    resolved_content = dict(snapshot.resolved_content)
    resolved_content["real_object_id"] = "not-a-real-slot-id"
    tampered = snapshot.model_copy(update={"resolved_content": resolved_content})
    fallback_expected = plugin._real_object_id(
        snapshot
    )  # no real_object_id present -> hash fallback
    assert plugin._real_object_id(tampered) == fallback_expected


@pytest.mark.parametrize("participant_count", [0, 1, 3, 9, 20])
def test_select_active_object_ids_clamps_out_of_range_participant_counts(
    participant_count: int,
) -> None:
    plugin = EvidenceSearchRacePlugin()
    snapshot = load_snapshot(run_seed="seed-clamp")
    active_ids = plugin._select_active_object_ids(snapshot, participant_count)
    assert len(active_ids) > 0
    assert len(active_ids) == len(set(active_ids))  # no duplicates
    real_id = plugin._real_object_id(snapshot)
    assert real_id in active_ids
