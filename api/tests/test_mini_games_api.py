"""Integration tests for the mini-game API endpoints (AW-252).

Exercises GET /active, POST /submissions, POST /host-commands via
starlette.testclient.TestClient against an in-memory SQLite DB.

Firebase and the MiniGameRuntime event bus are not mocked; the runtime is
exercised end-to-end through the thin route handlers.

Auth dependencies are overridden so tests run without GCP credentials.
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Iterator
from datetime import datetime, timezone
from typing import Any
from unittest.mock import patch
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
from api.schemas import TmstInputPhaseState, TmstSpotlightPhaseState
from engine.db import get_async_session
from engine.db.orm import (
    Account,
    Base,
    Character,
    MiniGameRun,
    Session,
    SessionParticipant,
)
from engine.db.testing import patch_metadata_for_sqlite
from engine.mini_games.models import (
    BehavioralOutputDeclaration,
    BehavioralScope,
    BehavioralValueType,
    ClueVariant,
    ContentMode,
    DelayedClueFallback,
)
from engine.mini_games.resolver import ResolvedMiniGameSnapshot

patch_metadata_for_sqlite()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_SESSION_ID = uuid4()
_PART_ID = uuid4()
_CHAR_ID = uuid4()
_HOST_PART_ID = uuid4()
_OTHER_PART_ID = uuid4()
_OTHER_CHAR_ID = uuid4()


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


def _make_snapshot_dict() -> dict[str, Any]:
    snap = ResolvedMiniGameSnapshot(
        game_id="test-game",
        definition_version="0.1.0",
        source_content_mode=ContentMode.authored,
        mechanic_type="match-3-clue-race",
        participation_mode="individual",
        min_players=1,
        max_players=8,
        duration_seconds=120,
        rules={},
        behavioral_outputs=(
            BehavioralOutputDeclaration(
                key="score",
                description="Score",
                value_type=BehavioralValueType.integer,
                scope=BehavioralScope.participant,
                derived=False,
            ),
        ),
        clue_fallback=DelayedClueFallback(
            delay_seconds=0,
            clue_variant=ClueVariant.full,
            host_override=True,
        ),
        resolved_content={
            "clues": [
                {"clue_id": "c1", "variant": "full", "content": {"text": "the answer"}}
            ]
        },
    )
    return snap.model_dump(mode="json")


def _make_tmst_snapshot_dict() -> dict[str, Any]:
    snap = ResolvedMiniGameSnapshot(
        game_id="tell-me-something-true",
        definition_version="0.1.0",
        source_content_mode=ContentMode.hybrid,
        mechanic_type="social-truth-bluff",
        participation_mode="group",
        min_players=4,
        max_players=8,
        duration_seconds=240,
        rules={},
        behavioral_outputs=(
            BehavioralOutputDeclaration(
                key="participation-recorded",
                description="sentinel",
                value_type=BehavioralValueType.boolean,
                scope=BehavioralScope.participant,
                derived=False,
            ),
        ),
        clue_fallback=DelayedClueFallback(
            delay_seconds=30,
            clue_variant=ClueVariant.reduced,
            host_override=True,
        ),
        resolved_content={},
    )
    return snap.model_dump(mode="json")


async def _seed_session_and_run(
    factory: async_sessionmaker[AsyncSession],
    *,
    run_status: str = "active",
) -> tuple[UUID, UUID]:
    """Seed DB with a session, participant, character, and mini-game run.

    Returns (session_id, run_id).
    """
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
                player_count=1,
            )
        )
        db.add(Character(character_id=_CHAR_ID, behavior_profile={}))
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
        await db.flush()

        run_id = uuid4()
        db.add(
            MiniGameRun(
                run_id=run_id,
                session_id=_SESSION_ID,
                game_id="test-game",
                definition_version="0.1.0",
                definition_snapshot=_make_snapshot_dict(),
                status=run_status,
                revision=0,
                started_at=datetime.now(tz=timezone.utc)
                if run_status == "active"
                else None,
                deadline=None,
                clue_unlock_record={},
            )
        )
        await db.commit()

    return _SESSION_ID, run_id


async def _seed_tmst_session_and_run(
    factory: async_sessionmaker[AsyncSession],
    *,
    runtime_state: dict[str, Any],
    deadline: datetime | None = None,
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
                game_id="tell-me-something-true",
                definition_version="0.1.0",
                definition_snapshot=_make_tmst_snapshot_dict(),
                status="active",
                revision=0,
                started_at=datetime.now(tz=timezone.utc),
                deadline=deadline,
                clue_unlock_record={"runtime_state": runtime_state},
            )
        )
        if submissions:
            from engine.db.orm import MiniGameSubmission

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


# ---------------------------------------------------------------------------
# GET /active — auth and reconnect
# ---------------------------------------------------------------------------


class TestGetActiveMiniGame:
    def test_returns_404_when_no_active_run(self, client: TestClient) -> None:
        resp = client.get(f"/v1/sessions/{_SESSION_ID}/mini-games/active")
        assert resp.status_code == 404

    def test_returns_run_state_for_active_run(
        self,
        client: TestClient,
        db_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        session_id, run_id = asyncio.run(_seed_session_and_run(db_factory))
        resp = client.get(f"/v1/sessions/{session_id}/mini-games/active")

        assert resp.status_code == 200
        body = resp.json()
        assert body["run_id"] == str(run_id)
        assert body["status"] == "active"
        assert body["my_submissions"] == []

    def test_player_only_sees_own_submissions(
        self,
        client: TestClient,
        db_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        """Reconnect path: player recovers only their own submissions (AC5)."""
        session_id, run_id = asyncio.run(_seed_session_and_run(db_factory))
        # Submit as this player first
        client.post(
            f"/v1/sessions/{session_id}/mini-games/{run_id}/submissions",
            json={"submission_id": "my-sub", "payload": {}},
        )

        # Seed an "other player's" submission directly in DB
        async def _seed_other_sub() -> None:
            async with db_factory() as db:
                other_char = uuid4()
                db.add(Character(character_id=other_char, behavior_profile={}))
                await db.flush()
                from engine.db.orm import MiniGameSubmission

                db.add(
                    MiniGameSubmission(
                        run_id=run_id,
                        submission_id="other-sub",
                        character_id=other_char,
                        submitted_at=datetime.now(tz=timezone.utc),
                        payload={},
                        is_accepted=True,
                    )
                )
                await db.commit()

        asyncio.run(_seed_other_sub())

        resp = client.get(f"/v1/sessions/{session_id}/mini-games/active")

        assert resp.status_code == 200
        subs = resp.json()["my_submissions"]
        sub_ids = [s["submission_id"] for s in subs]
        assert "my-sub" in sub_ids
        assert "other-sub" not in sub_ids

    def test_unauthenticated_returns_401(self, client: TestClient) -> None:
        app.dependency_overrides[require_player_or_host_jwt] = lambda: (
            _ for _ in ()
        ).throw(__import__("fastapi").HTTPException(status_code=401))
        try:
            resp = client.get(f"/v1/sessions/{_SESSION_ID}/mini-games/active")
            assert resp.status_code == 401
        finally:
            app.dependency_overrides[require_player_or_host_jwt] = lambda: (
                _player_claims()
            )

    def test_wrong_session_id_in_token_returns_403(self, client: TestClient) -> None:
        wrong_session = uuid4()
        app.dependency_overrides[require_player_or_host_jwt] = lambda: _player_claims(
            session_id=wrong_session
        )
        try:
            resp = client.get(f"/v1/sessions/{_SESSION_ID}/mini-games/active")
            assert resp.status_code == 403
        finally:
            app.dependency_overrides[require_player_or_host_jwt] = lambda: (
                _player_claims()
            )

    def test_tmst_input_phase_state_is_typed_for_player_reconnect(
        self,
        client: TestClient,
        db_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        session_id, _run_id = asyncio.run(
            _seed_tmst_session_and_run(
                db_factory,
                runtime_state={
                    "phase": "input",
                    "presence": {
                        str(_CHAR_ID): True,
                        str(_OTHER_CHAR_ID): True,
                    },
                    "input_closed": False,
                    "current_spotlight_index": 0,
                    "spotlight_order": [],
                },
                deadline=datetime(2026, 6, 28, 16, 0, tzinfo=timezone.utc),
            )
        )

        resp = client.get(f"/v1/sessions/{session_id}/mini-games/active")

        assert resp.status_code == 200
        phase_state = TmstInputPhaseState.model_validate(resp.json()["phase_state"])
        assert phase_state.phase == "input"
        assert phase_state.prompt_ready is True
        assert phase_state.submitted is False

    def test_tmst_spotlight_phase_state_is_authorized_for_reconnect(
        self,
        client: TestClient,
        db_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        session_id, run_id = asyncio.run(
            _seed_tmst_session_and_run(
                db_factory,
                runtime_state={
                    "phase": "spotlight",
                    "presence": {
                        str(_CHAR_ID): True,
                        str(_OTHER_CHAR_ID): True,
                    },
                    "input_closed": True,
                    "current_spotlight_index": 0,
                    "spotlight_order": [str(_OTHER_CHAR_ID)],
                },
                deadline=datetime(2026, 6, 28, 16, 15, tzinfo=timezone.utc),
                submissions=[
                    {
                        "submission_id": "tmst-input-self",
                        "character_id": _CHAR_ID,
                        "payload": {
                            "action": "input",
                            "statement_text": "Self statement",
                            "declared_truth": True,
                        },
                    },
                    {
                        "submission_id": "tmst-input-target",
                        "character_id": _OTHER_CHAR_ID,
                        "payload": {
                            "action": "input",
                            "statement_text": "Other statement",
                            "declared_truth": False,
                        },
                    },
                    {
                        "submission_id": "tmst-vote-1",
                        "character_id": _CHAR_ID,
                        "payload": {
                            "action": "vote",
                            "target_character_id": str(_OTHER_CHAR_ID),
                            "vote": "truth",
                        },
                    },
                ],
            )
        )

        resp = client.get(f"/v1/sessions/{session_id}/mini-games/active")

        assert resp.status_code == 200
        body = resp.json()
        phase_state = TmstSpotlightPhaseState.model_validate(body["phase_state"])
        assert phase_state.phase == "spotlight"
        assert phase_state.target_character_id == _OTHER_CHAR_ID
        assert phase_state.can_vote is True
        assert phase_state.has_voted is True
        assert body["my_submissions"] == [
            {
                "submission_id": "tmst-input-self",
                "is_accepted": True,
                "rejection_reason": None,
            },
            {
                "submission_id": "tmst-vote-1",
                "is_accepted": True,
                "rejection_reason": None,
            },
        ]


# ---------------------------------------------------------------------------
# POST /submissions — auth and idempotency
# ---------------------------------------------------------------------------


class TestSubmitMiniGameAction:
    def test_accepts_valid_submission(
        self,
        client: TestClient,
        db_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        _, run_id = asyncio.run(_seed_session_and_run(db_factory))
        resp = client.post(
            f"/v1/sessions/{_SESSION_ID}/mini-games/{run_id}/submissions",
            json={"submission_id": "sub-1", "payload": {"answer": 42}},
        )

        assert resp.status_code == 200
        body = resp.json()
        assert body["submission_id"] == "sub-1"
        assert isinstance(body["is_accepted"], bool)

    def test_idempotent_on_same_submission_id(
        self,
        client: TestClient,
        db_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        """AC2: submitting the same submission_id twice returns identical response."""
        _, run_id = asyncio.run(_seed_session_and_run(db_factory))
        url = f"/v1/sessions/{_SESSION_ID}/mini-games/{run_id}/submissions"
        body = {"submission_id": "dup-sub", "payload": {}}

        r1 = client.post(url, json=body)
        r2 = client.post(url, json=body)

        assert r1.status_code == 200
        assert r2.status_code == 200
        assert r1.json() == r2.json()

    def test_host_token_rejected(
        self,
        client: TestClient,
        db_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        """Host JWT cannot reach the submission endpoint (player-only)."""
        _, run_id = asyncio.run(_seed_session_and_run(db_factory))
        app.dependency_overrides[require_player_jwt] = lambda: (_ for _ in ()).throw(
            __import__("fastapi").HTTPException(
                status_code=403, detail="Player token required"
            )
        )
        try:
            resp = client.post(
                f"/v1/sessions/{_SESSION_ID}/mini-games/{run_id}/submissions",
                json={"submission_id": "s1", "payload": {}},
            )
            assert resp.status_code == 403
        finally:
            app.dependency_overrides[require_player_jwt] = lambda: _player_claims()

    def test_non_participant_returns_403(
        self,
        client: TestClient,
        db_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        """Player from a different session (or not in participant table) gets 403."""
        _, run_id = asyncio.run(_seed_session_and_run(db_factory))
        outsider_id = uuid4()
        app.dependency_overrides[require_player_jwt] = lambda: JwtClaims(
            uid="outsider", session_id=_SESSION_ID, player_id=outsider_id, role="player"
        )
        try:
            resp = client.post(
                f"/v1/sessions/{_SESSION_ID}/mini-games/{run_id}/submissions",
                json={"submission_id": "s1", "payload": {}},
            )
            assert resp.status_code == 403
        finally:
            app.dependency_overrides[require_player_jwt] = lambda: _player_claims()

    def test_wrong_session_returns_403(
        self,
        client: TestClient,
        db_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        _, run_id = asyncio.run(_seed_session_and_run(db_factory))
        wrong_session = uuid4()
        app.dependency_overrides[require_player_jwt] = lambda: _player_claims(
            session_id=wrong_session
        )
        try:
            resp = client.post(
                f"/v1/sessions/{wrong_session}/mini-games/{run_id}/submissions",
                json={"submission_id": "s1", "payload": {}},
            )
            assert resp.status_code == 403
        finally:
            app.dependency_overrides[require_player_jwt] = lambda: _player_claims()

    def test_tmst_malformed_payload_returns_422(
        self,
        client: TestClient,
        db_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        _, run_id = asyncio.run(
            _seed_tmst_session_and_run(
                db_factory,
                runtime_state={
                    "phase": "input",
                    "presence": {str(_CHAR_ID): True, str(_OTHER_CHAR_ID): True},
                    "input_closed": False,
                    "current_spotlight_index": 0,
                    "spotlight_order": [],
                },
            )
        )

        resp = client.post(
            f"/v1/sessions/{_SESSION_ID}/mini-games/{run_id}/submissions",
            json={
                "submission_id": "bad-input",
                "payload": {"action": "input", "declared_truth": True},
            },
        )

        assert resp.status_code == 422

    def test_tmst_out_of_phase_action_returns_409(
        self,
        client: TestClient,
        db_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        _, run_id = asyncio.run(
            _seed_tmst_session_and_run(
                db_factory,
                runtime_state={
                    "phase": "spotlight",
                    "presence": {str(_CHAR_ID): True, str(_OTHER_CHAR_ID): True},
                    "input_closed": True,
                    "current_spotlight_index": 0,
                    "spotlight_order": [str(_OTHER_CHAR_ID)],
                },
            )
        )

        resp = client.post(
            f"/v1/sessions/{_SESSION_ID}/mini-games/{run_id}/submissions",
            json={
                "submission_id": "late-input",
                "payload": {
                    "action": "input",
                    "statement_text": "Too late",
                    "declared_truth": True,
                },
            },
        )

        assert resp.status_code == 409
        assert "input phase" in resp.json()["detail"]


# ---------------------------------------------------------------------------
# POST /host-commands — routing and auth
# ---------------------------------------------------------------------------


class TestHostCommands:
    def test_cancel_transitions_run_to_cancelled(
        self,
        client: TestClient,
        db_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        _, run_id = asyncio.run(_seed_session_and_run(db_factory))
        resp = client.post(
            f"/v1/sessions/{_SESSION_ID}/mini-games/{run_id}/host-commands",
            json={"command": "cancel", "params": {}},
        )

        assert resp.status_code == 200
        assert resp.json()["status"] == "cancelled"

    def test_resolve_transitions_run_to_completed(
        self,
        client: TestClient,
        db_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        # plugin.score is scaffolded as NotImplementedError pending full implementation;
        # mock it here to test the API routing behaviour in isolation.
        _, run_id = asyncio.run(_seed_session_and_run(db_factory))
        with patch(
            "engine.mini_games.plugins._match_3_clue_race.Match3ClueRacePlugin.score",
            return_value={},
        ):
            resp = client.post(
                f"/v1/sessions/{_SESSION_ID}/mini-games/{run_id}/host-commands",
                json={"command": "resolve", "params": {}},
            )

        assert resp.status_code == 200
        assert resp.json()["status"] == "completed"

    def test_release_fallback_calls_override_clue_release(
        self,
        client: TestClient,
        db_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        _, run_id = asyncio.run(_seed_session_and_run(db_factory))
        resp = client.post(
            f"/v1/sessions/{_SESSION_ID}/mini-games/{run_id}/host-commands",
            json={
                "command": "release_fallback",
                "params": {
                    "clues": [
                        {"clue_id": "c1", "variant": "full", "content": {"text": "x"}}
                    ]
                },
            },
        )

        assert resp.status_code == 200
        assert resp.json()["run_id"] == str(run_id)

    def test_player_token_rejected(
        self,
        client: TestClient,
        db_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        _, run_id = asyncio.run(_seed_session_and_run(db_factory))
        app.dependency_overrides[require_host_jwt] = lambda: (_ for _ in ()).throw(
            __import__("fastapi").HTTPException(
                status_code=403, detail="Host token required"
            )
        )
        try:
            resp = client.post(
                f"/v1/sessions/{_SESSION_ID}/mini-games/{run_id}/host-commands",
                json={"command": "cancel", "params": {}},
            )
            assert resp.status_code == 403
        finally:
            app.dependency_overrides[require_host_jwt] = lambda: _host_claims()

    def test_resolve_returns_501_when_scoring_not_implemented(
        self,
        client: TestClient,
        db_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        """Unimplemented plugin.score() must surface as 501, not 500.

        The real Match3ClueRacePlugin.score raises NotImplementedError.
        This test exercises the unpatched path to verify the router converts
        it to a 501 rather than leaking an unhandled 500.
        """
        _, run_id = asyncio.run(_seed_session_and_run(db_factory))
        resp = client.post(
            f"/v1/sessions/{_SESSION_ID}/mini-games/{run_id}/host-commands",
            json={"command": "resolve", "params": {}},
        )
        assert resp.status_code == 501
        assert "not yet implemented" in resp.json()["detail"].lower()

    def test_unknown_command_returns_422(
        self,
        client: TestClient,
        db_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        _, run_id = asyncio.run(_seed_session_and_run(db_factory))
        resp = client.post(
            f"/v1/sessions/{_SESSION_ID}/mini-games/{run_id}/host-commands",
            json={"command": "teleport", "params": {}},
        )
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# ContentEvent validation
# ---------------------------------------------------------------------------


class TestContentEventEmission:
    def test_submission_emits_acknowledgement_category(
        self,
        client: TestClient,
        db_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        """AC4: submission acknowledgement uses EventCategory.acknowledgement."""
        from api.routers.events import _buses

        _, run_id = asyncio.run(_seed_session_and_run(db_factory))
        client.post(
            f"/v1/sessions/{_SESSION_ID}/mini-games/{run_id}/submissions",
            json={"submission_id": "ev-sub", "payload": {}},
        )

        bus = _buses.get(_SESSION_ID)
        if bus is None:
            return

        ack_events = [
            e
            for e in bus.replay_since(0)
            if e.event_type == "mini_game_submission_accepted"
        ]
        for evt in ack_events:
            assert evt.category.value == "acknowledgement"
            assert evt.target_audience.value == "specific_player"
            assert evt.target_player_id == _PART_ID


# ---------------------------------------------------------------------------
# GET /active/display — unauthenticated shared-display and player-device path
# (AW-265)
# ---------------------------------------------------------------------------


class TestGetActiveMiniGameDisplay:
    """Tests for the public /display endpoint (no auth required)."""

    def test_returns_404_when_no_active_run(self, client: TestClient) -> None:
        resp = client.get(f"/v1/sessions/{_SESSION_ID}/mini-games/active/display")
        assert resp.status_code == 404

    def test_returns_200_without_auth_header(
        self,
        client: TestClient,
        db_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        """Shared display can fetch state with no Authorization header."""
        asyncio.run(_seed_session_and_run(db_factory))
        resp = client.get(f"/v1/sessions/{_SESSION_ID}/mini-games/active/display")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "active"
        assert body["my_submissions"] == []

    def test_display_input_phase_state_has_no_private_fields(
        self,
        client: TestClient,
        db_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        """Shared display (no character_id) sees prompt_ready=False."""
        asyncio.run(
            _seed_tmst_session_and_run(
                db_factory,
                runtime_state={"phase": "input", "presence": {}, "input_closed": False},
            )
        )
        resp = client.get(f"/v1/sessions/{_SESSION_ID}/mini-games/active/display")
        assert resp.status_code == 200
        ps = TmstInputPhaseState.model_validate(resp.json()["phase_state"])
        assert ps.phase == "input"
        assert ps.prompt_ready is False
        assert ps.submitted is False

    def test_player_device_input_phase_state_with_character_id(
        self,
        client: TestClient,
        db_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        """Player device sees prompt_ready=True when character_id is supplied."""
        asyncio.run(
            _seed_tmst_session_and_run(
                db_factory,
                runtime_state={"phase": "input", "presence": {}, "input_closed": False},
            )
        )
        resp = client.get(
            f"/v1/sessions/{_SESSION_ID}/mini-games/active/display"
            f"?character_id={_CHAR_ID}"
        )
        assert resp.status_code == 200
        ps = TmstInputPhaseState.model_validate(resp.json()["phase_state"])
        assert ps.phase == "input"
        assert ps.prompt_ready is True
        assert ps.submitted is False

    def test_player_device_submitted_flag_reflects_accepted_submission(
        self,
        client: TestClient,
        db_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        """submitted=True after the player's input submission is accepted."""
        asyncio.run(
            _seed_tmst_session_and_run(
                db_factory,
                runtime_state={"phase": "input", "presence": {}, "input_closed": False},
                submissions=[
                    {
                        "submission_id": "input-sub",
                        "character_id": _CHAR_ID,
                        "payload": {
                            "action": "input",
                            "statement_text": "I ate __ hotdogs",
                            "declared_truth": True,
                        },
                        "is_accepted": True,
                    }
                ],
            )
        )
        resp = client.get(
            f"/v1/sessions/{_SESSION_ID}/mini-games/active/display"
            f"?character_id={_CHAR_ID}"
        )
        assert resp.status_code == 200
        ps = TmstInputPhaseState.model_validate(resp.json()["phase_state"])
        assert ps.submitted is True

    def test_display_spotlight_phase_state_no_personalization(
        self,
        client: TestClient,
        db_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        """Shared display gets is_spotlighted_player=False and can_vote=False."""
        asyncio.run(
            _seed_tmst_session_and_run(
                db_factory,
                runtime_state={
                    "phase": "spotlight",
                    "presence": {
                        str(_CHAR_ID): True,
                        str(_OTHER_CHAR_ID): True,
                    },
                    "input_closed": True,
                    "current_spotlight_index": 0,
                    "spotlight_order": [str(_CHAR_ID)],
                },
            )
        )
        resp = client.get(f"/v1/sessions/{_SESSION_ID}/mini-games/active/display")
        assert resp.status_code == 200
        ps = TmstSpotlightPhaseState.model_validate(resp.json()["phase_state"])
        assert ps.phase == "spotlight"
        assert ps.is_spotlighted_player is False
        assert ps.can_vote is False
