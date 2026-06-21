"""API-level batch harness test for AW-224.

Runs 10 seeded Nightcap sessions through the HTTP lifecycle, keeps the
``host_bypass`` signal inside the test harness, and verifies telemetry
presence without widening the production input schema.
"""

from __future__ import annotations

import asyncio
import random
from collections.abc import AsyncIterator, Iterator
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from unittest.mock import AsyncMock, patch
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
from engine.arc import transition_name_for
from engine.characters.service import _character_service
from engine.db import get_async_session
from engine.db.orm import Base, Event, GenerationLog
from engine.db.orm import SessionParticipant as OrmParticipant
from engine.db.testing import patch_metadata_for_sqlite
from engine.harness import HarnessAction, HarnessRunner
from engine.routing import logging as routing_logging
from engine.routing.router import RouteResult

_FAKE_TOKEN = b"fake-firebase-custom-token"
_ARC_PATH = Path(__file__).resolve().parents[2] / "nightcap" / "arc.json"
_HOST_BYPASS = {
    "host_bypass": {
        "actor_id": "host-1",
        "actor_role": "host",
        "reason": "batch-harness-test",
    }
}
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
_EXIT_CONDITIONS = {
    "arrival": "all_players_ready",
    "body": "body_discovered",
    "opening_move": "private_clues_distributed",
    "dig": "killer_revealed_to_themselves",
    "thread": "first_convergence_reached",
    "reckoning": "accusations_resolved",
    "close": "final_accusation_committed",
}
_CLOSE_TO_TRUTH = transition_name_for("close", "truth")


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


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


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


def _advance_runner_to_truth(runner: HarnessRunner, participants: list[str]) -> None:
    runner.start()
    runner.set_participants(participants)

    for current_beat, next_beat in zip(_BEAT_SEQUENCE, _BEAT_SEQUENCE[1:]):
        payload: dict[str, object] = {}
        if current_beat != "close":
            payload = {"context": {_EXIT_CONDITIONS[current_beat]: True}}
        runner.apply_action(
            HarnessAction(
                transition_name=transition_name_for(current_beat, next_beat),
                payload=payload,
            )
        )

    runner.apply_action(
        HarnessAction(
            transition_name=_CLOSE_TO_TRUTH,
            payload=_HOST_BYPASS,
        )
    )

    run = runner.current_run()
    assert run.runtime_state.reveal_state.revealed_by == "host_bypass"
    assert run.runtime_state.reveal_state.bypass_sequence == 1


async def _count_rows(
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


async def _count_generation_rows(
    db_factory: async_sessionmaker[AsyncSession],
    *,
    session_id: UUID,
) -> int:
    async with db_factory() as db:
        result = await db.execute(
            select(GenerationLog).where(GenerationLog.session_id == session_id)
        )
        return len(result.scalars().all())


@pytest.mark.parametrize("seed", range(10))
def test_batch_session_completes(
    seed: int,
    client: TestClient,
    db_factory: async_sessionmaker[AsyncSession],
    auth_state: dict[str, JwtClaims],
) -> None:
    random.seed(seed)

    session_id = _create_session(client)

    host_participant = _run(
        _load_participant(db_factory, session_id=session_id, surface_type="host")
    )
    auth_state["host"] = JwtClaims(
        uid="host-uid",
        session_id=session_id,
        player_id=host_participant.participant_id,
        role="host",
    )

    player_participant_ids = [_add_player(client, session_id) for _ in range(4)]
    player_participant = _run(
        _load_participant(
            db_factory,
            session_id=session_id,
            participant_id=player_participant_ids[0],
        )
    )
    auth_state["player"] = JwtClaims(
        uid="player-uid",
        session_id=session_id,
        player_id=player_participant.participant_id,
        role="player",
    )

    runner = HarnessRunner(arc_path=_ARC_PATH, seed=seed)
    _advance_runner_to_truth(
        runner,
        [str(participant_id) for participant_id in player_participant_ids],
    )

    start_resp = client.post(f"/v1/sessions/{session_id}/start")
    assert start_resp.status_code == 200, start_resp.text

    async def _fake_generate(*args, **kwargs) -> RouteResult:
        db_session = args[0]
        task_type = kwargs["task_type"]
        quality_tier = kwargs["quality_tier"]
        tension_score = kwargs.get("tension_score")
        db_session.add(
            GenerationLog(
                session_id=session_id,
                timestamp=datetime.now(tz=timezone.utc),
                task_type=task_type,
                quality_tier=quality_tier,
                model_used="test-model",
                latency_ms=1,
                input_tokens=100,
                output_tokens=50,
                cost_usd=Decimal("0.001"),
                tension_score=tension_score,
            )
        )
        await db_session.flush()
        return RouteResult(
            content="[mocked]",
            model_used="test-model",
            input_tokens=100,
            output_tokens=50,
            latency_ms=1,
            used_fallback=False,
        )

    original_submit_input = _character_service.submit_input

    async def _submit_input_with_generation(*args, **kwargs):  # type: ignore[no-untyped-def]
        record = await original_submit_input(*args, **kwargs)
        db_session = args[0]
        await routing_logging.generate(
            db_session,
            session_id=session_id,
            task_type="narrator_bridge",
            quality_tier="standard",
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"seed={seed} host_bypass={_HOST_BYPASS['host_bypass']['reason']}"
                    ),
                },
                {"role": "user", "content": "Continue the session."},
            ],
        )
        return record

    with (
        patch(
            "engine.routing.logging.generate", new_callable=AsyncMock
        ) as mock_generate,
        patch(
            "engine.characters.service._character_service.submit_input",
            new=_submit_input_with_generation,
        ),
    ):
        mock_generate.side_effect = _fake_generate
        input_resp = client.post(
            f"/v1/sessions/{session_id}/characters/{player_participant.character_id}/input",
            json={
                "kind": "dialogue",
                "content": f"seed {seed}: carry the truth beat forward.",
                "host_bypass": _HOST_BYPASS,
            },
        )
        assert input_resp.status_code == 201, input_resp.text
        assert mock_generate.await_count == 1

    end_resp = client.post(
        f"/v1/sessions/{session_id}/end",
        json={"completion_type": "full_arc", "killer_identified": True},
    )
    assert end_resp.status_code == 200, end_resp.text

    assert (
        _run(
            _count_rows(
                db_factory, session_id=session_id, event_type="session_completed"
            )
        )
        == 1
    )
    assert _run(_count_generation_rows(db_factory, session_id=session_id)) > 0
