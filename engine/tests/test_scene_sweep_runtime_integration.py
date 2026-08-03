from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import UUID, uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from engine.db.orm import (
    Account,
    Character,
    Fact,
    KnowledgeState,
    Session,
    SessionParticipant,
)
from engine.db.testing import make_sqlite_session_factory, patch_metadata_for_sqlite
from engine.events.bus import SessionEventBus
from engine.mini_games.loader import load_mini_game_package
from engine.mini_games.plugins import default_registry
from engine.mini_games.resolver import ResolvedMiniGameSnapshot
from engine.mini_games.runtime import MiniGameRuntime

patch_metadata_for_sqlite()

T0 = datetime(2026, 8, 2, 20, 0, 0, tzinfo=timezone.utc)
PACKAGE_PATH = (
    Path(__file__).resolve().parents[2] / "nightcap" / "mini_games" / "scene-sweep"
)


def load_snapshot(*, run_seed: str) -> ResolvedMiniGameSnapshot:
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


@pytest.fixture
async def db() -> AsyncSession:
    _, factory = await make_sqlite_session_factory()
    async with factory() as sess:
        yield sess


async def _setup_session_with_participants(
    db: AsyncSession,
    count: int,
) -> tuple[UUID, list[UUID]]:
    account_id = uuid4()
    session_id = uuid4()
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
            player_count=count,
        )
    )
    char_ids: list[UUID] = []
    for _ in range(count):
        char_id = uuid4()
        char_ids.append(char_id)
        db.add(Character(character_id=char_id, behavior_profile={}))
    await db.flush()
    for char_id in char_ids:
        db.add(
            SessionParticipant(
                session_id=session_id,
                character_id=char_id,
                join_token=f"tok-{char_id}",
                surface_type="phone",
                is_ai_controlled=False,
            )
        )
    await db.flush()
    return session_id, char_ids


def make_runtime(db: AsyncSession, *, clock_time: datetime = T0) -> MiniGameRuntime:
    return MiniGameRuntime(
        db,
        SessionEventBus(),
        default_registry(),
        clock=lambda: clock_time,
    )


@pytest.mark.parametrize("participant_count", [4, 8])
async def test_full_success_path_asserts_knowledge_for_every_participant(
    db: AsyncSession,
    participant_count: int,
) -> None:
    session_id, char_ids = await _setup_session_with_participants(db, participant_count)
    snapshot = load_snapshot(run_seed=f"seed-success-{participant_count}")
    runtime = make_runtime(db)

    run = await runtime.create_run(session_id, snapshot)
    run = await runtime.start_run(run.run_id)
    run_id = run.run_id

    # Discover the round's active object ids from the plugin directly, since
    # the runtime doesn't expose them on the ORM row except via clue_unlock_record.
    active_ids = list(run.clue_unlock_record["runtime_state"]["active_object_ids"])

    # `run_id` (not `run`) drives the loop below, and every submission is
    # kept referenced. SQLAlchemy's identity map holds ORM objects via weak
    # references: if the loop instead reassigned `run` to each
    # `submit_action()` return value, the `MiniGameRun` object would lose
    # its only strong reference and get evicted the moment CPython reclaims
    # it. `MiniGameRuntime.submit_action` (engine/mini_games/runtime.py)
    # reloads the run internally on every call and checks
    # `if run.deadline and now > run.deadline`; once the run has been
    # evicted, that reload comes back from SQLite with a naive `deadline`
    # (SQLite has no timezone-aware storage), while the injected clock's
    # `now` is tz-aware, so the comparison raises "can't compare
    # offset-naive and offset-aware datetimes" inside that deadline check —
    # not inside the plugin's scoring/sort logic. Holding strong references
    # to the submissions guards against the same class of bug if anything
    # here later needed to compare their timestamps; production Postgres
    # preserves tzinfo through any reload either way.
    submissions = []
    for index, object_id in enumerate(active_ids):
        submitter = char_ids[index % len(char_ids)]
        submissions.append(
            await runtime.submit_action(
                run_id,
                f"sub-{index}",
                submitter,
                {"action": "claim", "object_id": object_id},
            )
        )

    active_run = await runtime.get_active_run(session_id)
    assert active_run is None  # terminal runs are excluded from get_active_run

    from engine.db.orm import MiniGameRun as MiniGameRunOrm

    result = await db.execute(
        select(MiniGameRunOrm).where(MiniGameRunOrm.session_id == session_id)
    )
    finished = result.scalar_one()
    assert finished.status == "completed"
    assert finished.behavioral_outputs["real-object-claimed"] is True

    # Knowledge is split across two tables: Fact (session-scoped, shared
    # across whoever knows it) and KnowledgeState (the character-to-fact
    # link `assert_knowledge` creates one row of per eligible character).
    # Success delivers both clue entries (full-mode returns every entry in
    # the authored clues list), so expect exactly 2 distinct Facts.
    facts_result = await db.execute(select(Fact).where(Fact.session_id == session_id))
    facts = list(facts_result.scalars().all())
    assert len(facts) == 2

    states_result = await db.execute(
        select(KnowledgeState).where(KnowledgeState.session_id == session_id)
    )
    states = list(states_result.scalars().all())
    assert len(states) == 2 * participant_count

    characters_per_fact: dict[UUID, set[UUID]] = {}
    for state in states:
        characters_per_fact.setdefault(state.fact_id, set()).add(state.character_id)
    for fact_id, known_by in characters_per_fact.items():
        assert known_by == set(char_ids)


@pytest.mark.parametrize("participant_count", [4, 8])
async def test_fallback_path_delivers_only_reduced_clue(
    db: AsyncSession,
    participant_count: int,
) -> None:
    session_id, char_ids = await _setup_session_with_participants(db, participant_count)
    snapshot = load_snapshot(run_seed=f"seed-fallback-{participant_count}")
    runtime = make_runtime(db, clock_time=T0)

    run = await runtime.create_run(session_id, snapshot)
    run = await runtime.start_run(run.run_id)

    # No submissions; advance the clock past the deadline and check timeout.
    late_runtime = make_runtime(db, clock_time=run.deadline + timedelta(seconds=1))
    await late_runtime.check_timeout(run.run_id)

    from engine.db.orm import MiniGameRun as MiniGameRunOrm

    result = await db.execute(
        select(MiniGameRunOrm).where(MiniGameRunOrm.session_id == session_id)
    )
    finished = result.scalar_one()
    assert finished.status == "timed_out"
    assert finished.behavioral_outputs["real-object-claimed"] is False

    # Fallback (ClueVariant.reduced) returns only entries tagged "reduced" —
    # exactly one Fact, shared across every eligible participant's
    # KnowledgeState row.
    facts_result = await db.execute(select(Fact).where(Fact.session_id == session_id))
    facts = list(facts_result.scalars().all())
    assert len(facts) == 1
    assert facts[0].fact_content["variant"] == "reduced"

    states_result = await db.execute(
        select(KnowledgeState).where(KnowledgeState.session_id == session_id)
    )
    states = list(states_result.scalars().all())
    assert len(states) == participant_count
    assert {state.character_id for state in states} == set(char_ids)


async def test_concurrent_double_claim_accepts_exactly_one(
    db: AsyncSession,
) -> None:
    """Proves the mechanic's authoritative state — not raw submission-row
    is_accepted flags — reflects exactly one true claim per object.

    Note on a platform-wide quirk this test deliberately works around: when
    a StatefulMechanicPlugin's on_submission raises ValueError for a
    conflict (here, claiming an already-claimed object), the runtime has
    already flushed the submission row with is_accepted=True (payload shape
    was valid) *before* on_submission runs — the ValueError becomes a
    RunStateError raised to the caller, not a rejection recorded on the row.
    Tell Me Something True's own conflict paths (double-input, wrong-phase
    vote) already behave identically. So the correct assertion is: the
    second call raises, and the mechanic's own claimed_object_ids state
    (not the DB row's is_accepted flag) contains the object exactly once.
    """
    session_id, char_ids = await _setup_session_with_participants(db, 4)
    snapshot = load_snapshot(run_seed="seed-concurrent")
    runtime = make_runtime(db)

    run = await runtime.create_run(session_id, snapshot)
    run = await runtime.start_run(run.run_id)
    active_ids = list(run.clue_unlock_record["runtime_state"]["active_object_ids"])
    target_object_id = active_ids[0]

    first = await runtime.submit_action(
        run.run_id,
        "sub-a",
        char_ids[0],
        {"action": "claim", "object_id": target_object_id},
    )
    assert first.is_accepted is True

    from engine.mini_games.runtime import RunStateError

    with pytest.raises(RunStateError):
        await runtime.submit_action(
            run.run_id,
            "sub-b",
            char_ids[1],
            {"action": "claim", "object_id": target_object_id},
        )

    from engine.db.orm import MiniGameRun as MiniGameRunOrm

    result = await db.execute(
        select(MiniGameRunOrm).where(MiniGameRunOrm.run_id == run.run_id)
    )
    reloaded = result.scalar_one()
    claimed_ids = reloaded.clue_unlock_record["runtime_state"]["claimed_object_ids"]
    assert claimed_ids.count(target_object_id) == 1
