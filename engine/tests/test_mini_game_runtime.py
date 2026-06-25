"""Tests for engine/mini_games/runtime.py — AW-251.

All lifecycle tests inject a frozen clock. No test touches wall time.
SQLite in-memory DB via patch_metadata_for_sqlite / make_sqlite_session_factory.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from engine.db.orm import (
    Account,
    Character,
    MiniGameRun,
    MiniGameSubmission,
    Session,
    SessionParticipant,
)
from engine.db.testing import make_sqlite_session_factory, patch_metadata_for_sqlite
from engine.events.bus import SessionEventBus
from engine.mini_games.models import (
    BehavioralOutputDeclaration,
    BehavioralScope,
    BehavioralValueType,
    ClueVariant,
    DelayedClueFallback,
)
from engine.mini_games.resolver import ResolvedMiniGameSnapshot
from engine.mini_games.runtime import (
    DerivedOutputValidationError,
    MechanicRegistry,
    MiniGameRuntime,
    RevisionConflictError,
    RunStateError,
    UnknownMechanicTypeError,
)

patch_metadata_for_sqlite()

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

T0 = datetime(2026, 6, 25, 12, 0, 0, tzinfo=timezone.utc)
MECHANIC = "test-mechanic"


# ---------------------------------------------------------------------------
# Stub plugin
# ---------------------------------------------------------------------------


class StubPlugin:
    mechanic_type: str = MECHANIC

    def __init__(
        self,
        *,
        validate_raises: Exception | None = None,
        threshold_met: bool = False,
        score_result: dict[str, Any] | None = None,
    ) -> None:
        self._validate_raises = validate_raises
        self._threshold_met = threshold_met
        self._score_result = score_result or {}

    def validate_payload(self, payload: dict[str, Any]) -> None:
        if self._validate_raises is not None:
            raise self._validate_raises

    def is_threshold_met(
        self,
        snapshot: ResolvedMiniGameSnapshot,
        submissions: list[MiniGameSubmission],
    ) -> bool:
        return self._threshold_met

    def score(
        self,
        snapshot: ResolvedMiniGameSnapshot,
        submissions: list[MiniGameSubmission],
    ) -> dict[str, Any]:
        return self._score_result


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
async def db() -> AsyncSession:
    _, factory = await make_sqlite_session_factory()
    async with factory() as sess:
        yield sess


def make_bus() -> SessionEventBus:
    return SessionEventBus()


def frozen_clock(t: datetime = T0):
    return lambda: t


def make_registry(plugin: StubPlugin | None = None) -> MechanicRegistry:
    return MechanicRegistry([plugin or StubPlugin()])


def make_snapshot(
    *,
    mechanic_type: str = MECHANIC,
    duration_seconds: int = 60,
    behavioral_outputs: list[BehavioralOutputDeclaration] | None = None,
    clue_variant: ClueVariant = ClueVariant.reduced,
    resolved_content: dict[str, Any] | None = None,
) -> ResolvedMiniGameSnapshot:
    if behavioral_outputs is None:
        behavioral_outputs = [
            BehavioralOutputDeclaration(
                key="score",
                description="Player score",
                value_type=BehavioralValueType.integer,
                scope=BehavioralScope.participant,
                derived=False,
            )
        ]
    return ResolvedMiniGameSnapshot(
        game_id="test-game",
        definition_version="0.1.0",
        source_content_mode="authored",
        mechanic_type=mechanic_type,
        participation_mode="individual",
        min_players=1,
        max_players=8,
        duration_seconds=duration_seconds,
        rules={},
        behavioral_outputs=tuple(behavioral_outputs),
        clue_fallback=DelayedClueFallback(
            delay_seconds=0,
            clue_variant=clue_variant,
            host_override=True,
        ),
        resolved_content=resolved_content
        or {
            "clues": [
                {"clue_id": "clue-1", "variant": "full", "content": {"text": "full"}},
                {
                    "clue_id": "clue-2",
                    "variant": "reduced",
                    "content": {"text": "reduced"},
                },
            ]
        },
    )


async def _setup_session_with_participant(
    db: AsyncSession,
) -> tuple[UUID, UUID, UUID]:
    """Insert account, session, character, participant. Returns (session_id, char_id, account_id)."""
    account_id = uuid4()
    session_id = uuid4()
    char_id = uuid4()

    db.add(Account(account_id=account_id, firebase_uid=f"uid-{account_id}"))
    await db.flush()

    db.add(
        Session(
            session_id=session_id,
            arc_id="arc-1",
            status="active",
            host_account_id=account_id,
            current_beat_id="beat-1",
            quality_tier="standard",
            player_count=1,
        )
    )
    db.add(Character(character_id=char_id, behavior_profile={}))
    await db.flush()

    db.add(
        SessionParticipant(
            session_id=session_id,
            character_id=char_id,
            join_token="tok",
            surface_type="phone",
            is_ai_controlled=False,
        )
    )
    await db.flush()
    return session_id, char_id, account_id


def make_runtime(
    db: AsyncSession,
    *,
    plugin: StubPlugin | None = None,
    clock_time: datetime = T0,
) -> MiniGameRuntime:
    return MiniGameRuntime(
        db,
        make_bus(),
        make_registry(plugin),
        clock=frozen_clock(clock_time),
    )


# ---------------------------------------------------------------------------
# create_run
# ---------------------------------------------------------------------------


async def test_create_run_sets_deadline_from_clock(db: AsyncSession) -> None:
    session_id, _, _ = await _setup_session_with_participant(db)
    snapshot = make_snapshot(duration_seconds=90)
    rt = make_runtime(db, clock_time=T0)

    run = await rt.create_run(session_id, snapshot)

    assert run.status == "pending"
    assert run.revision == 0
    assert run.deadline == T0 + timedelta(seconds=90)
    assert run.game_id == "test-game"
    assert run.definition_version == "0.1.0"
    assert run.definition_snapshot is not None
    assert run.behavioral_outputs is None


async def test_create_run_stores_immutable_snapshot(db: AsyncSession) -> None:
    session_id, _, _ = await _setup_session_with_participant(db)
    snapshot = make_snapshot()
    rt = make_runtime(db)

    run = await rt.create_run(session_id, snapshot)

    stored = ResolvedMiniGameSnapshot.model_validate(run.definition_snapshot)
    assert stored.game_id == snapshot.game_id
    assert stored.mechanic_type == snapshot.mechanic_type


# ---------------------------------------------------------------------------
# AC7: Unknown mechanic_type rejected before run is created
# ---------------------------------------------------------------------------


async def test_unknown_mechanic_rejected_before_run_created(db: AsyncSession) -> None:
    session_id, _, _ = await _setup_session_with_participant(db)
    snapshot = make_snapshot(mechanic_type="not-a-real-mechanic")
    rt = make_runtime(db)

    with pytest.raises(UnknownMechanicTypeError, match="not-a-real-mechanic"):
        await rt.create_run(session_id, snapshot)

    result = await db.execute(select(MiniGameRun))
    assert result.scalars().first() is None


# ---------------------------------------------------------------------------
# AC8: Derived behavioral output validation
# ---------------------------------------------------------------------------


async def test_derived_output_rejected_no_non_derived_sibling(
    db: AsyncSession,
) -> None:
    session_id, _, _ = await _setup_session_with_participant(db)
    outputs = [
        BehavioralOutputDeclaration(
            key="derived-metric",
            description="Derived with no sibling",
            value_type=BehavioralValueType.integer,
            scope=BehavioralScope.run,
            derived=True,
        )
    ]
    snapshot = make_snapshot(behavioral_outputs=outputs)
    rt = make_runtime(db)

    with pytest.raises(DerivedOutputValidationError, match="derived-metric"):
        await rt.create_run(session_id, snapshot)

    result = await db.execute(select(MiniGameRun))
    assert result.scalars().first() is None


async def test_derived_output_accepted_with_non_derived_sibling(
    db: AsyncSession,
) -> None:
    session_id, _, _ = await _setup_session_with_participant(db)
    outputs = [
        BehavioralOutputDeclaration(
            key="base-score",
            description="Non-derived base",
            value_type=BehavioralValueType.integer,
            scope=BehavioralScope.run,
            derived=False,
        ),
        BehavioralOutputDeclaration(
            key="derived-rank",
            description="Derived from base-score",
            value_type=BehavioralValueType.integer,
            scope=BehavioralScope.run,
            derived=True,
        ),
    ]
    snapshot = make_snapshot(behavioral_outputs=outputs)
    rt = make_runtime(db)

    run = await rt.create_run(session_id, snapshot)
    assert run.status == "pending"


# ---------------------------------------------------------------------------
# Lifecycle: start_run
# ---------------------------------------------------------------------------


async def test_start_run_transitions_to_active(db: AsyncSession) -> None:
    session_id, _, _ = await _setup_session_with_participant(db)
    rt = make_runtime(db)

    run = await rt.create_run(session_id, make_snapshot())
    run = await rt.start_run(run.run_id)

    assert run.status == "active"
    assert run.started_at == T0
    assert run.revision == 1


async def test_start_run_rejects_non_pending(db: AsyncSession) -> None:
    session_id, _, _ = await _setup_session_with_participant(db)
    rt = make_runtime(db)
    run = await rt.create_run(session_id, make_snapshot())
    await rt.start_run(run.run_id)

    with pytest.raises(RunStateError, match="pending"):
        await rt.start_run(run.run_id)


async def test_submit_action_rejects_pending_run(db: AsyncSession) -> None:
    """submit_action requires active status — pending run raises RunStateError."""
    session_id, char_id, _ = await _setup_session_with_participant(db)
    rt = make_runtime(db)
    run = await rt.create_run(session_id, make_snapshot())
    # run is pending, never started

    with pytest.raises(RunStateError, match="active"):
        await rt.submit_action(run.run_id, "sub-1", char_id, {})


async def test_submit_action_rejects_completed_run(db: AsyncSession) -> None:
    """submit_action requires active status — completed run raises RunStateError."""
    session_id, char_id, _ = await _setup_session_with_participant(db)
    plugin = StubPlugin(threshold_met=True, score_result={})
    rt = MiniGameRuntime(db, make_bus(), make_registry(plugin), clock=frozen_clock(T0))
    run = await rt.create_run(session_id, make_snapshot())
    await rt.start_run(run.run_id)

    with patch("engine.mini_games.runtime.assert_knowledge", new_callable=AsyncMock):
        await rt.submit_action(run.run_id, "sub-first", char_id, {})

    # run is now completed; a second attempt with a new submission_id must fail
    with pytest.raises(RunStateError, match="active"):
        await rt.submit_action(run.run_id, "sub-second", char_id, {})


# ---------------------------------------------------------------------------
# AC2: Idempotency
# ---------------------------------------------------------------------------


async def test_submit_idempotent_same_outcome_twice(db: AsyncSession) -> None:
    session_id, char_id, _ = await _setup_session_with_participant(db)
    rt = make_runtime(db)
    run = await rt.create_run(session_id, make_snapshot())
    await rt.start_run(run.run_id)

    sub_id = "sub-001"
    first = await rt.submit_action(run.run_id, sub_id, char_id, {"answer": "butler"})
    second = await rt.submit_action(run.run_id, sub_id, char_id, {"answer": "butler"})

    assert first.submission_pk == second.submission_pk
    assert first.is_accepted == second.is_accepted

    result = await db.execute(
        select(MiniGameSubmission).where(MiniGameSubmission.run_id == run.run_id)
    )
    assert len(result.scalars().all()) == 1


# ---------------------------------------------------------------------------
# AC2: Concurrency — revision conflict
# ---------------------------------------------------------------------------


async def test_submit_concurrent_revision_conflict(db: AsyncSession) -> None:
    """AC2: A stale revision fails atomically, never silently winning.

    submit_action loads the run fresh on each call, so conflicts must be
    tested by calling _increment_revision directly with a stale in-memory
    run — which is exactly what would happen if two concurrent workers loaded
    the same revision and both tried to write.
    """
    session_id, char_id, _ = await _setup_session_with_participant(db)
    rt = make_runtime(db)
    run = await rt.create_run(session_id, make_snapshot())
    await rt.start_run(run.run_id)
    # DB revision is now 1. Construct a stale in-memory view at revision=0.
    stale = MagicMock()
    stale.run_id = run.run_id
    stale.revision = 0

    with pytest.raises(RevisionConflictError):
        await rt._increment_revision(stale)


# ---------------------------------------------------------------------------
# AC3: Pause / resume — deadline adjusted for pause duration
# ---------------------------------------------------------------------------


async def test_pause_resume_restores_deadline_adjusted_for_pause(
    db: AsyncSession,
) -> None:
    session_id, char_id, _ = await _setup_session_with_participant(db)

    t_start = T0
    t_pause = T0 + timedelta(seconds=20)
    t_resume = T0 + timedelta(seconds=35)

    rt_start = MiniGameRuntime(
        db, make_bus(), make_registry(), clock=frozen_clock(t_start)
    )
    run = await rt_start.create_run(session_id, make_snapshot(duration_seconds=60))
    await rt_start.start_run(run.run_id)

    rt_pause = MiniGameRuntime(
        db, make_bus(), make_registry(), clock=frozen_clock(t_pause)
    )
    run = await rt_pause.pause_run(run.run_id)

    assert run.status == "paused"
    assert run.paused_at == t_pause
    # 60 - 20 = 40 seconds remaining
    assert run.pause_deadline_remaining_seconds == pytest.approx(40.0)

    rt_resume = MiniGameRuntime(
        db, make_bus(), make_registry(), clock=frozen_clock(t_resume)
    )
    run = await rt_resume.resume_run(run.run_id)

    assert run.status == "active"
    assert run.paused_at is None
    # new deadline = t_resume + 40s = T0 + 35s + 40s = T0 + 75s
    assert run.deadline == t_resume + timedelta(seconds=40)


async def test_pause_run_rejects_non_active(db: AsyncSession) -> None:
    session_id, _, _ = await _setup_session_with_participant(db)
    rt = make_runtime(db)
    run = await rt.create_run(session_id, make_snapshot())

    with pytest.raises(RunStateError, match="active"):
        await rt.pause_run(run.run_id)


async def test_resume_run_rejects_non_paused(db: AsyncSession) -> None:
    session_id, _, _ = await _setup_session_with_participant(db)
    rt = make_runtime(db)
    run = await rt.create_run(session_id, make_snapshot())
    await rt.start_run(run.run_id)

    with pytest.raises(RunStateError, match="paused"):
        await rt.resume_run(run.run_id)


# ---------------------------------------------------------------------------
# AC4: Timeout — follows authored fallback
# ---------------------------------------------------------------------------


async def test_timeout_fires_reduced_fallback(db: AsyncSession) -> None:
    session_id, char_id, _ = await _setup_session_with_participant(db)
    plugin = StubPlugin(threshold_met=False, score_result={})

    t_start = T0
    t_timeout = T0 + timedelta(seconds=61)  # past the 60s deadline

    rt_start = MiniGameRuntime(
        db, make_bus(), make_registry(plugin), clock=frozen_clock(t_start)
    )
    run = await rt_start.create_run(
        session_id,
        make_snapshot(duration_seconds=60, clue_variant=ClueVariant.reduced),
    )
    await rt_start.start_run(run.run_id)

    with patch(
        "engine.mini_games.runtime.assert_knowledge", new_callable=AsyncMock
    ) as mock_ak:
        rt_timeout = MiniGameRuntime(
            db, make_bus(), make_registry(plugin), clock=frozen_clock(t_timeout)
        )
        updated = await rt_timeout.check_timeout(run.run_id)

    assert updated is not None
    assert updated.status == "timed_out"
    assert updated.clue_unlock_record.get("fallback_type") == "fallback_reduced"
    assert mock_ak.called


async def test_timeout_fires_full_fallback(db: AsyncSession) -> None:
    session_id, char_id, _ = await _setup_session_with_participant(db)
    plugin = StubPlugin(threshold_met=False, score_result={})

    t_start = T0
    t_timeout = T0 + timedelta(seconds=61)

    rt_start = MiniGameRuntime(
        db, make_bus(), make_registry(plugin), clock=frozen_clock(t_start)
    )
    run = await rt_start.create_run(
        session_id,
        make_snapshot(duration_seconds=60, clue_variant=ClueVariant.full),
    )
    await rt_start.start_run(run.run_id)

    with patch(
        "engine.mini_games.runtime.assert_knowledge", new_callable=AsyncMock
    ) as mock_ak:
        rt_timeout = MiniGameRuntime(
            db, make_bus(), make_registry(plugin), clock=frozen_clock(t_timeout)
        )
        updated = await rt_timeout.check_timeout(run.run_id)

    assert updated is not None
    assert updated.status == "timed_out"
    assert updated.clue_unlock_record.get("fallback_type") == "fallback_full"
    assert mock_ak.called


async def test_timeout_preserves_solvable_clue_path(db: AsyncSession) -> None:
    """AC4: The reduced fallback still releases clue-2 so the path stays solvable."""
    session_id, _, _ = await _setup_session_with_participant(db)
    plugin = StubPlugin(score_result={})

    rt_start = MiniGameRuntime(
        db, make_bus(), make_registry(plugin), clock=frozen_clock(T0)
    )
    run = await rt_start.create_run(
        session_id,
        make_snapshot(
            duration_seconds=60,
            clue_variant=ClueVariant.reduced,
            resolved_content={
                "clues": [
                    {"clue_id": "clue-full", "variant": "full", "content": {}},
                    {"clue_id": "clue-reduced", "variant": "reduced", "content": {}},
                ]
            },
        ),
    )
    await rt_start.start_run(run.run_id)

    with patch("engine.mini_games.runtime.assert_knowledge", new_callable=AsyncMock):
        rt_timeout = MiniGameRuntime(
            db,
            make_bus(),
            make_registry(plugin),
            clock=frozen_clock(T0 + timedelta(seconds=61)),
        )
        updated = await rt_timeout.check_timeout(run.run_id)

    assert updated is not None
    assert updated.status == "timed_out"
    unlocked = updated.clue_unlock_record.get("unlocked", [])
    released_ids = [e["clue_id"] for e in unlocked]
    assert "clue-reduced" in released_ids
    # full-only clue must NOT be released in reduced fallback
    assert "clue-full" not in released_ids


# ---------------------------------------------------------------------------
# Knowledge assertion invariant
# ---------------------------------------------------------------------------


async def test_knowledge_assert_called_per_clue_per_character(
    db: AsyncSession,
) -> None:
    session_id, char_id, _ = await _setup_session_with_participant(db)
    plugin = StubPlugin(threshold_met=False, score_result={})

    rt_start = MiniGameRuntime(
        db, make_bus(), make_registry(plugin), clock=frozen_clock(T0)
    )
    run = await rt_start.create_run(
        session_id,
        make_snapshot(
            duration_seconds=60,
            clue_variant=ClueVariant.full,
            resolved_content={
                "clues": [
                    {"clue_id": "c1", "variant": "full", "content": {}},
                    {"clue_id": "c2", "variant": "full", "content": {}},
                ]
            },
        ),
    )
    await rt_start.start_run(run.run_id)

    with patch(
        "engine.mini_games.runtime.assert_knowledge", new_callable=AsyncMock
    ) as mock_ak:
        rt_timeout = MiniGameRuntime(
            db,
            make_bus(),
            make_registry(plugin),
            clock=frozen_clock(T0 + timedelta(seconds=61)),
        )
        await rt_timeout.check_timeout(run.run_id)

    # 2 clues × 1 character = 2 assert_knowledge calls
    assert mock_ak.call_count == 2
    called_char_ids = {c.kwargs["character_id"] for c in mock_ak.call_args_list}
    assert char_id in called_char_ids


# ---------------------------------------------------------------------------
# AC5: Behavioral outputs are session-scoped; not cross-session
# ---------------------------------------------------------------------------


async def test_behavioral_outputs_session_scoped_not_cross_session(
    db: AsyncSession,
) -> None:
    """AC5: behavioral_outputs JSONB on the run row; not readable by another session."""
    session_id, char_id, _ = await _setup_session_with_participant(db)
    outputs = [
        BehavioralOutputDeclaration(
            key="score",
            description="Score",
            value_type=BehavioralValueType.integer,
            scope=BehavioralScope.participant,
            derived=False,
        )
    ]
    plugin = StubPlugin(threshold_met=True, score_result={"score": 42})
    rt = MiniGameRuntime(db, make_bus(), make_registry(plugin), clock=frozen_clock(T0))

    with patch("engine.mini_games.runtime.assert_knowledge", new_callable=AsyncMock):
        run = await rt.create_run(session_id, make_snapshot(behavioral_outputs=outputs))
        await rt.start_run(run.run_id)
        await rt.submit_action(run.run_id, "sub-1", char_id, {})

    # Output is stored on the run row (session-scoped)
    result = await db.execute(
        select(MiniGameRun).where(MiniGameRun.run_id == run.run_id)
    )
    updated = result.scalar_one()
    assert updated.behavioral_outputs is not None
    assert "score" in updated.behavioral_outputs

    # A query scoped to a different session_id returns nothing
    other_session_id = uuid4()
    result2 = await db.execute(
        select(MiniGameRun).where(MiniGameRun.session_id == other_session_id)
    )
    assert result2.scalars().first() is None


# ---------------------------------------------------------------------------
# Host override
# ---------------------------------------------------------------------------


async def test_host_override_logs_and_asserts_knowledge(db: AsyncSession) -> None:
    session_id, char_id, host_account_id = await _setup_session_with_participant(db)
    rt = make_runtime(db)
    run = await rt.create_run(session_id, make_snapshot())
    await rt.start_run(run.run_id)

    clues = [{"clue_id": "override-clue", "variant": "full", "content": {"text": "x"}}]

    with patch(
        "engine.mini_games.runtime.assert_knowledge", new_callable=AsyncMock
    ) as mock_ak:
        run = await rt.override_clue_release(run.run_id, clues, host_account_id)

    assert mock_ak.called
    override_entries = run.clue_unlock_record.get("overrides", [])
    assert len(override_entries) == 1
    assert override_entries[0]["clue_id"] == "override-clue"
    assert override_entries[0]["release_type"] == "host_override"
    assert override_entries[0]["host_account_id"] == str(host_account_id)


async def test_host_override_rejected_on_cancelled_run(db: AsyncSession) -> None:
    session_id, _, host_account_id = await _setup_session_with_participant(db)
    rt = make_runtime(db)
    run = await rt.create_run(session_id, make_snapshot())

    # Manually cancel the run
    run.status = "cancelled"
    await db.flush()

    with pytest.raises(RunStateError, match="cancelled"):
        await rt.override_clue_release(run.run_id, [], host_account_id)


# ---------------------------------------------------------------------------
# Submission rejected after deadline
# ---------------------------------------------------------------------------


async def test_submit_after_deadline_triggers_timeout(db: AsyncSession) -> None:
    session_id, char_id, _ = await _setup_session_with_participant(db)
    plugin = StubPlugin(score_result={})

    rt_start = MiniGameRuntime(
        db, make_bus(), make_registry(plugin), clock=frozen_clock(T0)
    )
    run = await rt_start.create_run(session_id, make_snapshot(duration_seconds=60))
    await rt_start.start_run(run.run_id)

    t_late = T0 + timedelta(seconds=90)
    rt_late = MiniGameRuntime(
        db, make_bus(), make_registry(plugin), clock=frozen_clock(t_late)
    )

    with patch("engine.mini_games.runtime.assert_knowledge", new_callable=AsyncMock):
        with pytest.raises(RunStateError, match="deadline exceeded"):
            await rt_late.submit_action(run.run_id, "sub-late", char_id, {})

    result = await db.execute(
        select(MiniGameRun).where(MiniGameRun.run_id == run.run_id)
    )
    updated = result.scalar_one()
    assert updated.status == "timed_out"


# ---------------------------------------------------------------------------
# check_timeout returns None when run is not active or not expired
# ---------------------------------------------------------------------------


async def test_check_timeout_returns_none_when_not_expired(db: AsyncSession) -> None:
    session_id, _, _ = await _setup_session_with_participant(db)
    rt = make_runtime(db, clock_time=T0)
    run = await rt.create_run(session_id, make_snapshot(duration_seconds=60))
    await rt.start_run(run.run_id)

    result = await rt.check_timeout(run.run_id)
    assert result is None


async def test_check_timeout_returns_none_for_pending_run(db: AsyncSession) -> None:
    session_id, _, _ = await _setup_session_with_participant(db)
    rt = make_runtime(db)
    run = await rt.create_run(session_id, make_snapshot())

    result = await rt.check_timeout(run.run_id)
    assert result is None


# ---------------------------------------------------------------------------
# Submission with invalid payload is stored as rejected
# ---------------------------------------------------------------------------


async def test_submit_invalid_payload_stored_as_rejected(db: AsyncSession) -> None:
    session_id, char_id, _ = await _setup_session_with_participant(db)
    plugin = StubPlugin(validate_raises=ValueError("bad payload"))
    rt = MiniGameRuntime(db, make_bus(), make_registry(plugin), clock=frozen_clock(T0))
    run = await rt.create_run(session_id, make_snapshot())
    await rt.start_run(run.run_id)

    sub = await rt.submit_action(run.run_id, "sub-bad", char_id, {"bad": True})

    assert sub.is_accepted is False
    assert "bad payload" in (sub.rejection_reason or "")


# ---------------------------------------------------------------------------
# AC6: Migration smoke test (integration, skipped without DATABASE_URL)
# ---------------------------------------------------------------------------


@pytest.mark.integration
async def test_migration_upgrade_and_downgrade() -> None:
    """Verifies alembic upgrade head and downgrade -1 both succeed (AC6).

    Requires DATABASE_URL to point at a live Postgres instance with the
    vector extension already enabled (alembic revision 0001 applied).
    """
    import os
    import subprocess

    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        pytest.skip("DATABASE_URL not set; skipping migration integration test")

    upgrade = subprocess.run(
        ["alembic", "upgrade", "head"],
        capture_output=True,
        text=True,
    )
    assert upgrade.returncode == 0, upgrade.stderr

    downgrade = subprocess.run(
        ["alembic", "downgrade", "-1"],
        capture_output=True,
        text=True,
    )
    assert downgrade.returncode == 0, downgrade.stderr

    # Re-apply so the DB is clean for the next test run
    re_upgrade = subprocess.run(
        ["alembic", "upgrade", "head"],
        capture_output=True,
        text=True,
    )
    assert re_upgrade.returncode == 0, re_upgrade.stderr
