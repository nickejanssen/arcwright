from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from engine.arc.arc_state import transition_name_for
from engine.case.models import ResolvedCase
from engine.db.orm import Base, Character, Session, SessionParticipant
from engine.db.testing import patch_metadata_for_sqlite
from engine.harness.models import HarnessAction
from engine.harness.runner import HarnessRunner
from engine.scoring.resolver import (
    AccusationResolver,
    accusations_locked_or_countdown_expired,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
ARC_PATH = REPO_ROOT / "nightcap" / "couch-race.arc.json"

patch_metadata_for_sqlite()


@pytest_asyncio.fixture()
async def db_session() -> AsyncIterator[AsyncSession]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        yield session
    await engine.dispose()


def _to_grill(
    runner: HarnessRunner, participants: list[str] | None = None
) -> None:
    runner.start()
    runner.set_participants(participants or ["p1", "p2"])
    for source, target, conditions in (
        (
            "pour",
            "scene",
            {"case_resolution_complete": True, "all_players_ready": True},
        ),
        ("scene", "grill", {"evidence_wave_delivered": True}),
    ):
        runner.apply_action(
            HarnessAction(
                transition_name=transition_name_for(source, target),
                payload={"context": conditions},
            )
        )


async def _make_db_session(
    db: AsyncSession, *, session_id: UUID, participant_ids: list[str]
) -> None:
    db.add(
        Session(
            session_id=session_id,
            arc_id="nightcap-couch-race-v1",
            status="active",
            host_account_id=uuid4(),
            current_beat_id="pour",
            quality_tier="standard",
            player_count=len(participant_ids),
        )
    )
    for index, participant_id in enumerate(participant_ids):
        character_id = uuid4()
        db.add(Character(character_id=character_id, behavior_profile={}))
        db.add(
            SessionParticipant(
                participant_id=_participant_uuid(participant_id),
                session_id=session_id,
                character_id=character_id,
                join_token=participant_id,
                surface_type="phone",
                is_ai_controlled=False,
            )
        )
    await db.flush()


def _participant_uuid(participant_id: str) -> UUID:
    """Return a SQLite-safe UUID for a harness participant identifier."""
    ordinal = int(participant_id.removeprefix("p"))
    return UUID(f"00000000-0000-0000-0000-a{ordinal:011d}")


def _case() -> ResolvedCase:
    return ResolvedCase(
        case_id="case-1",
        arc_id="nightcap-couch-race-v1",
        seed=284,
        skeleton_id="skeleton-1",
        cast=[],
        culprit_id="culprit-1",
        evidence=[],
        falsehoods=[],
        facts=[],
        reveal_shape={},
    )


def _clock() -> datetime:
    return datetime(2026, 7, 19, 12, 0, tzinfo=timezone.utc)


def _resolver(
    session_id: UUID, context: dict[str, object]
) -> AccusationResolver:
    return AccusationResolver(
        session_id=session_id,
        resolved_case=_case(),
        session_context=context,
        clock=_clock,
        round_duration_seconds=60,
        last_call_duration_seconds=100,
    )


async def _accuse(
    resolver: AccusationResolver,
    db: AsyncSession,
    session_id: UUID,
    participant_id: str,
    *,
    beat_id: str,
    accused_cast_member_id: str,
) -> None:
    await resolver.submit_accusation(
        db,
        session_id=session_id,
        accuser_participant_id=_participant_uuid(participant_id),
        beat_id=beat_id,
        beat_progress_fraction=0.5,
        accused_cast_member_id=accused_cast_member_id,
        motive_correct=False,
        method_correct=False,
    )


def test_normal_grill_completion_invokes_twist_transition():
    runner = HarnessRunner(arc_path=ARC_PATH, seed=284)
    _to_grill(runner)

    entry = runner.advance_current_beat(cause="normal_completion")

    assert entry.transition_name == "advance_grill_to_twist"
    assert runner.snapshot().configuration == ["twist"]
    assert runner.transition_causes == {"grill": "normal_completion"}


def test_first_correct_accusation_invokes_grill_to_last_call_transition():
    runner = HarnessRunner(arc_path=ARC_PATH, seed=284)
    _to_grill(runner)

    entry = runner.advance_current_beat(cause="first_correct_accusation")

    assert entry.transition_name == "advance_grill_to_last_call"
    assert runner.snapshot().configuration == ["last_call"]
    assert "twist" not in runner.snapshot().configuration
    assert runner.transition_causes == {"grill": "first_correct_accusation"}


def test_orchestrator_rejects_wrong_target_for_normal_cause():
    runner = HarnessRunner(arc_path=ARC_PATH, seed=284)
    _to_grill(runner)

    with pytest.raises(ValueError, match="does not match cause"):
        runner.advance_current_beat(
            cause="normal_completion", target_beat_id="last_call"
        )

    assert runner.snapshot().configuration == ["grill"]
    assert runner.trace()[-1].transition_name == "advance_scene_to_grill"


def test_twist_exit_ready_uses_existing_last_call_edge_for_early_accusation():
    runner = HarnessRunner(arc_path=ARC_PATH, seed=284)
    _to_grill(runner)
    runner.advance_current_beat(cause="normal_completion")

    entry = runner.advance_current_beat(cause="first_correct_accusation")

    assert entry.transition_name == "advance_twist_to_last_call"
    assert runner.snapshot().configuration == ["last_call"]
    assert runner.transition_causes == {
        "grill": "normal_completion",
        "twist": "first_correct_accusation",
    }


def test_last_call_condition_becomes_true_on_natural_expiry():
    assert accusations_locked_or_countdown_expired(
        0,
        eligible_participant_ids={"p1", "p2"},
        locked_out_participant_ids=set(),
    )


def test_last_call_condition_becomes_true_when_all_active_players_locked_early():
    assert accusations_locked_or_countdown_expired(
        42,
        eligible_participant_ids={"p1", "p2"},
        locked_out_participant_ids={"p1", "p2"},
    )


def test_passive_participant_does_not_block_all_locked_condition():
    assert accusations_locked_or_countdown_expired(
        42,
        eligible_participant_ids={"p1", "p2"},
        locked_out_participant_ids={"p1", "p2"},
    )
    assert not accusations_locked_or_countdown_expired(
        42,
        eligible_participant_ids={"p1", "p2"},
        locked_out_participant_ids={"p1"},
    )


@pytest.mark.asyncio
async def test_path_one_first_correct_then_chain_reaction_and_truth(
    db_session: AsyncSession,
):
    participants = ["p1", "p2", "p3"]
    runner = HarnessRunner(arc_path=ARC_PATH, seed=284)
    _to_grill(runner, participants)
    session_id = runner.current_run().session_id
    await _make_db_session(
        db_session, session_id=session_id, participant_ids=participants
    )
    context: dict[str, object] = {"last_call_remaining_seconds": 100.0}
    resolver = _resolver(session_id, context)

    await _accuse(
        resolver,
        db_session,
        session_id,
        "p1",
        beat_id="grill",
        accused_cast_member_id="culprit-1",
    )
    runner.advance_current_beat(cause="first_correct_accusation")
    assert runner.snapshot().configuration == ["last_call"]

    await _accuse(
        resolver,
        db_session,
        session_id,
        "p2",
        beat_id="last_call",
        accused_cast_member_id="culprit-1",
    )
    assert context["last_call_remaining_seconds"] == 80.0
    assert accusations_locked_or_countdown_expired(
        0,
        eligible_participant_ids={"p1", "p2"},
        locked_out_participant_ids=set(),
    )
    runner.advance_current_beat(cause="normal_completion")
    assert runner.snapshot().configuration == ["truth"]
    assert "p3" not in context


@pytest.mark.asyncio
async def test_path_two_countdown_expiry_with_passive_player(
    db_session: AsyncSession,
):
    participants = ["p1", "p2", "p3"]
    runner = HarnessRunner(arc_path=ARC_PATH, seed=285)
    _to_grill(runner, participants)
    session_id = runner.current_run().session_id
    await _make_db_session(
        db_session, session_id=session_id, participant_ids=participants
    )
    context: dict[str, object] = {"last_call_remaining_seconds": 100.0}
    resolver = _resolver(session_id, context)

    for participant_id in ("p1", "p2"):
        await _accuse(
            resolver,
            db_session,
            session_id,
            participant_id,
            beat_id="grill",
            accused_cast_member_id="wrong-1",
        )
    runner.advance_current_beat(cause="normal_completion")
    runner.advance_current_beat(cause="normal_completion")
    assert runner.snapshot().configuration == ["last_call"]
    assert context["last_call_remaining_seconds"] == 100.0

    assert accusations_locked_or_countdown_expired(
        0,
        eligible_participant_ids={"p1", "p2"},
        locked_out_participant_ids={"p1", "p2"},
    )
    runner.advance_current_beat(cause="normal_completion")
    assert runner.snapshot().configuration == ["truth"]
    assert "advance_grill_to_last_call" not in [
        entry.transition_name for entry in runner.trace()
    ]


@pytest.mark.asyncio
async def test_path_three_all_active_players_locked_before_countdown_expiry(
    db_session: AsyncSession,
):
    participants = ["p1", "p2", "p3"]
    runner = HarnessRunner(arc_path=ARC_PATH, seed=286)
    _to_grill(runner, participants)
    session_id = runner.current_run().session_id
    await _make_db_session(
        db_session, session_id=session_id, participant_ids=participants
    )
    runner.advance_current_beat(cause="normal_completion")
    runner.advance_current_beat(cause="normal_completion")
    assert runner.snapshot().configuration == ["last_call"]
    context: dict[str, object] = {"last_call_remaining_seconds": 100.0}
    resolver = _resolver(session_id, context)

    for participant_id in ("p1", "p2"):
        await _accuse(
            resolver,
            db_session,
            session_id,
            participant_id,
            beat_id="last_call",
            accused_cast_member_id="wrong-1",
        )
    assert accusations_locked_or_countdown_expired(
        42,
        eligible_participant_ids={"p1", "p2"},
        locked_out_participant_ids={"p1", "p2"},
    )
    assert not accusations_locked_or_countdown_expired(
        42,
        eligible_participant_ids=set(participants),
        locked_out_participant_ids={"p1", "p2"},
    )
    runner.advance_current_beat(cause="normal_completion")
    assert runner.snapshot().configuration == ["truth"]
