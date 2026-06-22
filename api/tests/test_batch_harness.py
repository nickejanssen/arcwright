"""API-level batch harness test for AW-255.

Runs 10 seeded Nightcap sessions through the HTTP lifecycle, proves the live
REST input path advances beat state, and records per-seed pass/fail status
without using a detached HarnessRunner.
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Iterator
from unittest.mock import patch
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from starlette.testclient import TestClient

from api.auth import (
    ApiCaller,
    JwtClaims,
    require_api_key,
    require_api_key_or_host_jwt,
    require_host_jwt,
    require_player_or_host_jwt,
)
from api.main import app
from engine.db import get_async_session
from engine.db.orm import Base, Event
from engine.db.orm import SessionParticipant as OrmParticipant
from engine.db.testing import patch_metadata_for_sqlite

_FAKE_TOKEN = b"fake-firebase-custom-token"
_BEAT_SEQUENCE = [
    "arrival",
    "body",
    "opening_move",
    "dig",
    "thread",
    "reckoning",
    "close",
    "truth",
]


patch_metadata_for_sqlite()


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
def auth_state() -> dict[str, JwtClaims]:
    return {
        "host": JwtClaims(
            uid="host-uid",
            session_id=None,
            player_id=uuid4(),
            role="host",
        ),
        "player": JwtClaims(
            uid="player-uid",
            session_id=None,
            player_id=uuid4(),
            role="player",
        ),
    }


@pytest.fixture()
def client(
    db_factory: async_sessionmaker[AsyncSession],
    auth_state: dict[str, JwtClaims],
) -> Iterator[TestClient]:
    async def _override_db() -> AsyncIterator[AsyncSession]:
        async with db_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    with (
        patch("api.routers.sessions._ensure_firebase_app"),
        patch("firebase_admin.auth.create_custom_token", return_value=_FAKE_TOKEN),
    ):
        app.dependency_overrides[require_api_key] = lambda: ApiCaller(
            api_key="test-key"
        )
        app.dependency_overrides[require_host_jwt] = lambda: auth_state["host"]
        app.dependency_overrides[require_player_or_host_jwt] = lambda: auth_state[
            "player"
        ]
        app.dependency_overrides[require_api_key_or_host_jwt] = lambda: ApiCaller(
            api_key="test-key"
        )
        app.dependency_overrides[get_async_session] = _override_db
        with TestClient(app) as c:
            yield c
        app.dependency_overrides.clear()


def _create_session(client: TestClient) -> UUID:
    resp = client.post("/v1/sessions", json={"arc_id": "nightcap-v1"})
    assert resp.status_code == 201, resp.text
    return UUID(resp.json()["session_id"])


def _add_player(client: TestClient, session_id: UUID) -> UUID:
    resp = client.post(f"/v1/sessions/{session_id}/players")
    assert resp.status_code == 201, resp.text
    return UUID(resp.json()["participant_id"])


async def _load_participant(
    db_factory: async_sessionmaker[AsyncSession],
    *,
    session_id: UUID,
    participant_id: UUID | None = None,
    surface_type: str | None = None,
) -> OrmParticipant:
    async with db_factory() as db:
        stmt = select(OrmParticipant).where(OrmParticipant.session_id == session_id)
        if participant_id is not None:
            stmt = stmt.where(OrmParticipant.participant_id == participant_id)
        if surface_type is not None:
            stmt = stmt.where(OrmParticipant.surface_type == surface_type)
        result = await db.execute(stmt)
        participant = result.scalars().first()
        assert participant is not None
        return participant


async def _count_events(
    db_factory: async_sessionmaker[AsyncSession],
    *,
    session_id: UUID,
    event_type: str,
) -> int:
    async with db_factory() as db:
        result = await db.execute(
            select(Event).where(
                Event.session_id == session_id,
                Event.event_type == event_type,
            )
        )
        return len(result.scalars().all())


def _set_host_claims(
    auth_state: dict[str, JwtClaims],
    *,
    session_id: UUID,
    participant_id: UUID,
) -> None:
    auth_state["host"] = JwtClaims(
        uid="host-uid",
        session_id=session_id,
        player_id=participant_id,
        role="host",
    )


def _set_player_claims(
    auth_state: dict[str, JwtClaims],
    *,
    session_id: UUID,
    participant_id: UUID,
) -> None:
    auth_state["player"] = JwtClaims(
        uid="player-uid",
        session_id=session_id,
        player_id=participant_id,
        role="player",
    )


def test_batch_session_completes(
    client: TestClient,
    db_factory: async_sessionmaker[AsyncSession],
    auth_state: dict[str, JwtClaims],
) -> None:
    records: list[dict[str, object]] = []
    failures: list[str] = []

    def _run_seed(seed: int) -> None:
        session_id = _create_session(client)

        host_participant = asyncio.get_event_loop().run_until_complete(
            _load_participant(
                db_factory,
                session_id=session_id,
                surface_type="host",
            )
        )
        _set_host_claims(
            auth_state,
            session_id=session_id,
            participant_id=host_participant.participant_id,
        )

        player_participant_ids = [_add_player(client, session_id) for _ in range(4)]
        player_participants = [
            asyncio.get_event_loop().run_until_complete(
                _load_participant(
                    db_factory,
                    session_id=session_id,
                    participant_id=participant_id,
                )
            )
            for participant_id in player_participant_ids
        ]

        start_resp = client.post(f"/v1/sessions/{session_id}/start")
        assert start_resp.status_code == 200, start_resp.text

        for index, source_beat in enumerate(_BEAT_SEQUENCE[:-1]):
            target_beat = _BEAT_SEQUENCE[index + 1]
            participant = player_participants[index % len(player_participants)]
            _set_player_claims(
                auth_state,
                session_id=session_id,
                participant_id=participant.participant_id,
            )
            input_resp = client.post(
                f"/v1/sessions/{session_id}/characters/{participant.character_id}/input",
                json={
                    "kind": "dialogue",
                    "content": f"seed {seed}: advance from {source_beat} to {target_beat}.",
                },
            )
            assert input_resp.status_code == 201, input_resp.text

            state_resp = client.get(f"/v1/sessions/{session_id}")
            assert state_resp.status_code == 200, state_resp.text
            assert state_resp.json()["current_beat_id"] == target_beat

        end_resp = client.post(f"/v1/sessions/{session_id}/end")
        assert end_resp.status_code == 200, end_resp.text

        beat_transition_count = asyncio.get_event_loop().run_until_complete(
            _count_events(
                db_factory,
                session_id=session_id,
                event_type="beat_transition",
            )
        )
        session_completed_count = asyncio.get_event_loop().run_until_complete(
            _count_events(
                db_factory,
                session_id=session_id,
                event_type="session_completed",
            )
        )

        assert beat_transition_count == len(_BEAT_SEQUENCE) - 1
        assert session_completed_count == 1
        records.append({"seed": seed, "passed": True})

    with patch(
        "litellm.acompletion",
        side_effect=AssertionError("provider access is forbidden in the batch harness"),
    ):
        for seed in range(10):
            try:
                _run_seed(seed)
            except Exception as exc:  # pragma: no cover - failure path
                records.append({"seed": seed, "passed": False, "error": str(exc)})
                failures.append(f"seed={seed}: {exc}")

    assert len(records) == 10
    assert all(record["passed"] is True for record in records)
    assert not failures, "\n".join(failures)
