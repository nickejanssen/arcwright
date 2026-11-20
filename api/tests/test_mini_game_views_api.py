"""AW-347: the mini-game reply carries live state and presentation, per audience.

The reads go through the real routes. The privacy tests use a test-only
mechanic whose saved state holds every player's private marker, so a leak shows
up as another player's marker appearing anywhere in a reply body.
"""

from __future__ import annotations

import asyncio
import json
import os
from collections.abc import AsyncIterator, Iterator
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import UUID

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
from engine.mini_games.audience_view import AudienceRule
from engine.mini_games.plugins import (
    EvidenceLockerBreachPlugin,
    EvidenceSearchRacePlugin,
    Match3ClueRacePlugin,
    SocialTruthBluffPlugin,
)
from engine.mini_games.runtime import MechanicRegistry

patch_metadata_for_sqlite()

FIXTURE_PATH = (
    Path(__file__).resolve().parents[2]
    / "dashboard"
    / "tests"
    / "fixtures"
    / "mini-game-live-replies.json"
)

SESSION_ID = UUID("a0000000-0000-4000-8000-000000000001")
HOST_PART_ID = UUID("a0000000-0000-4000-8000-0000000000f0")
PLAYERS = {
    "a": (
        UUID("a0000000-0000-4000-8000-0000000000a1"),
        UUID("a0000000-0000-4000-8000-0000000000c1"),
    ),
    "b": (
        UUID("a0000000-0000-4000-8000-0000000000a2"),
        UUID("a0000000-0000-4000-8000-0000000000c2"),
    ),
    "c": (
        UUID("a0000000-0000-4000-8000-0000000000a3"),
        UUID("a0000000-0000-4000-8000-0000000000c3"),
    ),
}
MARKERS = {key: f"PRIVATE-MARKER-{key.upper()}-{key * 6}" for key in PLAYERS}
RUN_ID = UUID("a0000000-0000-4000-8000-000000000099")
DEADLINE = datetime(2026, 12, 12, 20, 0, tzinfo=timezone.utc)


class _PrivateNotesMechanic:
    """Test-only mechanic: each player's note sits in the saved state."""

    mechanic_type = "test-private-notes"
    audience_rule = AudienceRule(
        public_state=("step",),
        own_state=("notes",),
        withheld_presentation=("phone_prompt",),
    )


def _registry() -> MechanicRegistry:
    return MechanicRegistry(
        [
            Match3ClueRacePlugin(),
            EvidenceLockerBreachPlugin(),
            SocialTruthBluffPlugin(),
            EvidenceSearchRacePlugin(),
            _PrivateNotesMechanic(),  # type: ignore[list-item]
        ]
    )


@pytest.fixture(autouse=True)
def _use_test_registry(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("api.routers.mini_games.default_registry", _registry)


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


class _Who:
    """Which signed-in caller the next request is made as."""

    claims: JwtClaims | None = None


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

    def _claims() -> JwtClaims:
        assert _Who.claims is not None
        return _Who.claims

    app.dependency_overrides[require_player_jwt] = _claims
    app.dependency_overrides[require_player_or_host_jwt] = _claims
    app.dependency_overrides[require_host_jwt] = _claims
    app.dependency_overrides[get_async_session] = _override_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
    _Who.claims = None


def _player(key: str) -> JwtClaims:
    return JwtClaims(
        uid=f"uid-{key}",
        session_id=SESSION_ID,
        player_id=PLAYERS[key][0],
        role="player",
    )


def _host() -> JwtClaims:
    return JwtClaims(
        uid="uid-host", session_id=SESSION_ID, player_id=HOST_PART_ID, role="host"
    )


async def _seed(
    factory: async_sessionmaker[AsyncSession],
    *,
    game_id: str,
    mechanic_type: str,
    runtime_state: dict[str, Any],
    presentation: dict[str, Any],
    submissions: list[dict[str, Any]] | None = None,
) -> None:
    async with factory() as db:
        account_id = UUID("a0000000-0000-4000-8000-0000000000e1")
        db.add(Account(account_id=account_id, firebase_uid="host-firebase-uid"))
        await db.flush()
        db.add(
            Session(
                session_id=SESSION_ID,
                arc_id="test-arc",
                status="active",
                host_account_id=account_id,
                current_beat_id="beat-1",
                quality_tier="standard",
                player_count=3,
            )
        )
        for _key, (_part, char) in PLAYERS.items():
            db.add(Character(character_id=char, behavior_profile={}))
        await db.flush()
        for _key, (part, char) in PLAYERS.items():
            db.add(
                SessionParticipant(
                    participant_id=part,
                    session_id=SESSION_ID,
                    character_id=char,
                    join_token=f"tok-{part}",
                    surface_type="phone",
                    is_ai_controlled=False,
                )
            )
        await db.flush()
        db.add(
            MiniGameRun(
                run_id=RUN_ID,
                session_id=SESSION_ID,
                game_id=game_id,
                definition_version="0.1.0",
                definition_snapshot={
                    "mechanic_type": mechanic_type,
                    "presentation": presentation,
                },
                status="active",
                revision=0,
                started_at=datetime(2026, 12, 12, 19, 59, tzinfo=timezone.utc),
                deadline=DEADLINE,
                clue_unlock_record={"runtime_state": runtime_state},
            )
        )
        for submission in submissions or []:
            db.add(
                MiniGameSubmission(
                    run_id=RUN_ID,
                    submission_id=submission["submission_id"],
                    character_id=submission["character_id"],
                    submitted_at=datetime(
                        2026, 12, 12, 19, 59, 30, tzinfo=timezone.utc
                    ),
                    payload=submission["payload"],
                    is_accepted=True,
                    rejection_reason=None,
                )
            )
        await db.commit()


def _private_state() -> dict[str, Any]:
    return {
        "step": "input",
        "notes": {str(PLAYERS[key][1]): MARKERS[key] for key in PLAYERS},
        "internal_only": "INTERNAL-ONLY-VALUE",
    }


def _private_presentation() -> dict[str, Any]:
    return {"title": "Shared title", "phone_prompt": "PHONE-ONLY-PROMPT"}


def _read_active(client: TestClient, claims: JwtClaims) -> Any:
    _Who.claims = claims
    return client.get(f"/v1/sessions/{SESSION_ID}/mini-games/active")


def _read_display(client: TestClient, character_id: UUID | None = None) -> Any:
    suffix = f"?character_id={character_id}" if character_id else ""
    return client.get(f"/v1/sessions/{SESSION_ID}/mini-games/active/display{suffix}")


async def _seed_private(factory: async_sessionmaker[AsyncSession]) -> None:
    await _seed(
        factory,
        game_id="test-game",
        mechanic_type="test-private-notes",
        runtime_state=_private_state(),
        presentation=_private_presentation(),
    )


def _assert_no_marker_of(body_text: str, owners: list[str]) -> None:
    for key in owners:
        assert MARKERS[key] not in body_text, f"player {key}'s marker leaked"
    assert "INTERNAL-ONLY-VALUE" not in body_text


class TestPrivacyPerAudience:
    def test_shared_screen_gets_no_player_marker(
        self, client: TestClient, db_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        asyncio.run(_seed_private(db_factory))
        res = _read_display(client)
        assert res.status_code == 200
        _assert_no_marker_of(res.text, ["a", "b", "c"])
        assert res.json()["runtime_state"] == {"step": "input"}
        assert "PHONE-ONLY-PROMPT" not in res.text
        assert res.json()["presentation"] == {"title": "Shared title"}

    def test_shared_screen_with_another_players_id_still_gets_no_marker(
        self, client: TestClient, db_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        asyncio.run(_seed_private(db_factory))
        for key in PLAYERS:
            res = _read_display(client, PLAYERS[key][1])
            assert res.status_code == 200
            _assert_no_marker_of(res.text, ["a", "b", "c"])
            assert res.json()["runtime_state"] == {"step": "input"}

    def test_each_player_gets_only_their_own_marker(
        self, client: TestClient, db_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        asyncio.run(_seed_private(db_factory))
        for key in PLAYERS:
            res = _read_active(client, _player(key))
            assert res.status_code == 200
            others = [k for k in PLAYERS if k != key]
            _assert_no_marker_of(res.text, others)
            body = res.json()
            assert body["runtime_state"]["notes"] == {
                str(PLAYERS[key][1]): MARKERS[key]
            }
            assert body["runtime_state"]["step"] == "input"
            assert body["presentation"]["phone_prompt"] == "PHONE-ONLY-PROMPT"

    def test_host_gets_no_player_marker(
        self, client: TestClient, db_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        asyncio.run(_seed_private(db_factory))
        res = _read_active(client, _host())
        assert res.status_code == 200
        _assert_no_marker_of(res.text, ["a", "b", "c"])
        assert res.json()["runtime_state"] == {"step": "input"}
        assert "PHONE-ONLY-PROMPT" not in res.text

    def test_signed_in_player_with_no_seat_gets_the_shared_view(
        self, client: TestClient, db_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        asyncio.run(_seed_private(db_factory))
        stranger = JwtClaims(
            uid="uid-x",
            session_id=SESSION_ID,
            player_id=UUID("a0000000-0000-4000-8000-0000000000ff"),
            role="player",
        )
        res = _read_active(client, stranger)
        assert res.status_code == 200
        _assert_no_marker_of(res.text, ["a", "b", "c"])
        assert res.json()["runtime_state"] == {"step": "input"}
        assert "PHONE-ONLY-PROMPT" not in res.text

    def test_run_of_a_game_with_no_rule_sends_empty_state(
        self, client: TestClient, db_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        asyncio.run(
            _seed(
                db_factory,
                game_id="scene-sweep",
                mechanic_type="evidence-search-race",
                runtime_state=_private_state(),
                presentation={"title": "T"},
            )
        )
        res = _read_active(client, _player("a"))
        assert res.status_code == 200
        _assert_no_marker_of(res.text, ["a", "b", "c"])
        assert res.json()["runtime_state"] == {}


class TestOldFieldsUnchanged:
    def test_old_fields_keep_their_values_and_new_fields_default_empty(
        self, client: TestClient, db_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        asyncio.run(
            _seed(
                db_factory,
                game_id="unknown-game",
                mechanic_type="no-such-mechanic",
                runtime_state={"step": "x"},
                presentation={},
                submissions=[
                    {
                        "submission_id": "s-a",
                        "character_id": PLAYERS["a"][1],
                        "payload": {"action": "any"},
                    }
                ],
            )
        )
        body = _read_active(client, _player("a")).json()
        assert body["run_id"] == str(RUN_ID)
        assert body["game_id"] == "unknown-game"
        assert body["status"] == "active"
        assert body["mechanic_type"] == "no-such-mechanic"
        assert body["phase_state"] is None
        assert body["my_submissions"] == [
            {"submission_id": "s-a", "is_accepted": True, "rejection_reason": None}
        ]
        assert body["runtime_state"] == {}
        assert body["presentation"] == {}


_TMST_PRESENTATION = {
    "title": "Tell Me Something True: Late Night",
    "prompt": "Finish the sentence, then choose: truth or lie.",
    "true_label": "Tell the truth",
    "lie_label": "Sell the lie",
}


def _tmst_state(phase: str) -> dict[str, Any]:
    order = [str(PLAYERS[key][1]) for key in ("a", "b", "c")]
    return {
        "phase": phase,
        "presence": {cid: True for cid in order},
        "input_closed": phase != "input",
        "current_spotlight_index": 1 if phase == "spotlight" else 0,
        "spotlight_order": [] if phase == "input" else order,
    }


class TestRecordedRepliesForTheTellMeSomethingTruePackageScreen:
    """The replies a real route sends at each step, kept in a committed file.

    The dashboard's Node test feeds this file through the real loader to the
    real package screen. Set ``AW347_REWRITE_FIXTURE=1`` to rewrite the file
    after a deliberate change to the reply shape.
    """

    @pytest.mark.parametrize("phase", ["input", "spotlight", "scoreboard"])
    def test_route_replies_match_the_committed_recording(
        self,
        phase: str,
        client: TestClient,
        db_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        asyncio.run(
            _seed(
                db_factory,
                game_id="tell-me-something-true",
                mechanic_type="social-truth-bluff",
                runtime_state=_tmst_state(phase),
                presentation=_TMST_PRESENTATION,
            )
        )
        replies = {
            "shared_display": _read_display(client).json(),
            "player": _read_active(client, _player("b")).json(),
        }
        for reply in replies.values():
            assert reply["runtime_state"]["phase"] == phase
            assert (
                reply["presentation"]["title"] == "Tell Me Something True: Late Night"
            )
        assert "prompt" not in replies["shared_display"]["presentation"]
        assert replies["player"]["presentation"]["prompt"]

        existing: dict[str, Any] = (
            json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
            if FIXTURE_PATH.exists()
            else {}
        )
        if os.environ.get("AW347_REWRITE_FIXTURE") == "1":
            existing[phase] = replies
            FIXTURE_PATH.parent.mkdir(parents=True, exist_ok=True)
            FIXTURE_PATH.write_text(
                json.dumps(existing, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
        assert existing.get(phase) == replies, (
            "the recorded replies are out of date; run with AW347_REWRITE_FIXTURE=1"
        )
