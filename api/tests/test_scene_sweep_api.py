from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Iterator
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from starlette.testclient import TestClient

from api.auth import (
    JwtClaims,
    require_host_jwt,
    require_player_jwt,
    require_player_or_host_jwt,
)
from api.main import app
from api.schemas import SceneSweepBoardPhaseState
from engine.db import get_async_session
from engine.db.orm import (
    Account,
    Base,
    Character,
    MiniGameRun,
    MiniGameSubmission,
    Session,
    SessionParticipant,
)
from engine.db.testing import patch_metadata_for_sqlite
from engine.mini_games.loader import load_mini_game_package
from engine.mini_games.models import ContentMode
from engine.mini_games.resolver import ResolvedMiniGameSnapshot

patch_metadata_for_sqlite()

_SESSION_ID = uuid4()
_PART_ID = uuid4()
_CHAR_ID = uuid4()
_OTHER_PART_ID = uuid4()
_OTHER_CHAR_ID = uuid4()
_HOST_PART_ID = uuid4()


def _player_claims(
    session_id: UUID = _SESSION_ID, player_id: UUID = _PART_ID
) -> JwtClaims:
    return JwtClaims(
        uid="player-uid", session_id=session_id, player_id=player_id, role="player"
    )


def _host_claims(session_id: UUID = _SESSION_ID) -> JwtClaims:
    return JwtClaims(
        uid="host-uid", session_id=session_id, player_id=_HOST_PART_ID, role="host"
    )


@pytest_asyncio.fixture()
async def db_factory() -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        yield factory
    finally:
        await engine.dispose()


@pytest.fixture()
def client(db_factory: async_sessionmaker[AsyncSession]) -> Iterator[TestClient]:
    async def _override_db() -> AsyncIterator[AsyncSession]:
        async with db_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[require_player_jwt] = lambda: _player_claims()
    app.dependency_overrides[require_player_or_host_jwt] = lambda: _player_claims()
    app.dependency_overrides[require_host_jwt] = lambda: _host_claims()
    app.dependency_overrides[get_async_session] = _override_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


def _scene_sweep_snapshot_dict(*, run_seed: str) -> dict[str, Any]:
    from pathlib import Path

    package_path = (
        Path(__file__).resolve().parents[2] / "nightcap" / "mini_games" / "scene-sweep"
    )
    loaded = load_mini_game_package(package_path)
    definition = loaded.definition
    resolved_content = dict(definition.authored_content or {})
    resolved_content["run_seed"] = run_seed
    snap = ResolvedMiniGameSnapshot(
        game_id=definition.game_id,
        definition_version=definition.version,
        source_content_mode=ContentMode.hybrid,
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
    return snap.model_dump(mode="json")


async def _seed_scene_sweep_session_and_run(
    factory: async_sessionmaker[AsyncSession],
    *,
    status: str,
    active_object_ids: list[str],
    claimed_object_ids: list[str],
    submissions: list[dict[str, Any]] | None = None,
) -> tuple[UUID, UUID]:
    async with factory() as db:
        account_id = uuid4()
        db.add(Account(account_id=account_id, firebase_uid="host-firebase-uid"))
        await db.flush()

        db.add(
            Session(
                session_id=_SESSION_ID,
                arc_id="nightcap-v1",
                status="active",
                host_account_id=account_id,
                current_beat_id="beat-1",
                quality_tier="standard",
                player_count=4,
            )
        )
        db.add(Character(character_id=_CHAR_ID, behavior_profile={}))
        db.add(Character(character_id=_OTHER_CHAR_ID, behavior_profile={}))
        await db.flush()

        db.add(
            SessionParticipant(
                participant_id=_PART_ID,
                session_id=_SESSION_ID,
                character_id=_CHAR_ID,
                join_token="tok-player",
                surface_type="phone",
                is_ai_controlled=False,
            )
        )
        db.add(
            SessionParticipant(
                participant_id=_OTHER_PART_ID,
                session_id=_SESSION_ID,
                character_id=_OTHER_CHAR_ID,
                join_token="tok-other",
                surface_type="phone",
                is_ai_controlled=False,
            )
        )
        await db.flush()

        run_id = uuid4()
        db.add(
            MiniGameRun(
                run_id=run_id,
                session_id=_SESSION_ID,
                game_id="scene-sweep",
                definition_version="0.1.0",
                definition_snapshot=_scene_sweep_snapshot_dict(
                    run_seed="api-test-seed"
                ),
                status=status,
                revision=0,
                started_at=datetime.now(tz=timezone.utc),
                deadline=datetime(2026, 8, 2, 21, 0, tzinfo=timezone.utc),
                clue_unlock_record={
                    "runtime_state": {
                        "active_object_ids": active_object_ids,
                        "claimed_object_ids": claimed_object_ids,
                    }
                },
            )
        )
        if submissions:
            for submission in submissions:
                db.add(
                    MiniGameSubmission(
                        run_id=run_id,
                        submission_id=submission["submission_id"],
                        character_id=submission["character_id"],
                        submitted_at=submission.get(
                            "submitted_at", datetime.now(tz=timezone.utc)
                        ),
                        payload=submission["payload"],
                        is_accepted=submission.get("is_accepted", True),
                        rejection_reason=submission.get("rejection_reason"),
                    )
                )
        await db.commit()

    return _SESSION_ID, run_id


class TestSceneSweepPhaseState:
    def test_active_phase_state_never_reveals_real_object(
        self,
        client: TestClient,
        db_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        """The /active response for an in-progress run must not contain any
        field naming which object is real — the API-layer lock on top of the
        plugin-level withholding already proven in Task 3.
        """
        session_id, _run_id = asyncio.run(
            _seed_scene_sweep_session_and_run(
                db_factory,
                status="active",
                active_object_ids=["slot-1", "slot-2", "slot-3", "slot-4", "slot-5"],
                claimed_object_ids=["slot-2"],
            )
        )

        resp = client.get(f"/v1/sessions/{session_id}/mini-games/active")

        assert resp.status_code == 200
        body = resp.json()
        raw_text = resp.text
        assert "real_object_id" not in raw_text
        assert "is_real" not in raw_text

        phase_state = SceneSweepBoardPhaseState.model_validate(body["phase_state"])
        assert phase_state.phase == "active"
        assert phase_state.claimed_object_ids == ["slot-2"]
        assert len(phase_state.objects) == 5
        for obj in phase_state.objects:
            assert obj.archetype
            assert set(obj.position.keys()) == {"x", "y"}

    def test_shared_display_view_also_withholds_real_object(
        self,
        client: TestClient,
        db_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        """Same withholding guarantee via the unauthenticated display path
        (GET /active/display), which the TV surface will actually call.
        """
        session_id, _run_id = asyncio.run(
            _seed_scene_sweep_session_and_run(
                db_factory,
                status="active",
                active_object_ids=["slot-1", "slot-2", "slot-3", "slot-4", "slot-5"],
                claimed_object_ids=[],
            )
        )

        resp = client.get(f"/v1/sessions/{session_id}/mini-games/active/display")

        assert resp.status_code == 200
        assert "real_object_id" not in resp.text
        assert "is_real" not in resp.text
        phase_state = SceneSweepBoardPhaseState.model_validate(
            resp.json()["phase_state"]
        )
        assert phase_state.phase == "active"
        assert phase_state.claimed_object_ids == []
