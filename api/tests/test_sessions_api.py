"""Integration tests for the session lifecycle REST API endpoints
(AW-217 + AW-220).

Exercises routes at the HTTP level via starlette.testclient.TestClient
against an in-memory SQLite-backed AsyncSession. The ``_session_service``
singleton is preserved (it is now stateless); the DB owns all state.

Firebase is mocked so tests run without GCP credentials.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from datetime import datetime, timezone
from decimal import Decimal
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
)
from api.main import app
from engine.db import get_async_session
from engine.db.orm import ArcBeatState, Base, Event, GenerationLog
from engine.db.orm import Session as OrmSession
from engine.db.testing import patch_metadata_for_sqlite
from engine.session.models import SessionStatus
from engine.session.service import _session_service

_FAKE_TOKEN = b"fake-firebase-custom-token"


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
def client(
    db_factory: async_sessionmaker[AsyncSession],
) -> Iterator[TestClient]:
    """TestClient with auth dependencies overridden, Firebase mocked, DB shared."""

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
        app.dependency_overrides[require_host_jwt] = lambda: JwtClaims(
            uid="host-uid", session_id=None, player_id=uuid4(), role="host"
        )
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


class TestCreateSession:
    def test_returns_201_with_required_fields(self, client: TestClient) -> None:
        resp = client.post("/v1/sessions", json={"arc_id": "nightcap-v1"})

        assert resp.status_code == 201
        body = resp.json()
        assert "session_id" in body
        assert "host_token" in body
        assert "host_join_token" in body
        assert "join_url" in body

    def test_missing_arc_id_returns_422(self, client: TestClient) -> None:
        resp = client.post("/v1/sessions", json={})
        assert resp.status_code == 422


class TestGetSession:
    def test_known_session_returns_200(self, client: TestClient) -> None:
        session_id = _create_session(client)
        resp = client.get(f"/v1/sessions/{session_id}")

        assert resp.status_code == 200
        assert resp.json()["session_id"] == str(session_id)

    def test_known_session_reports_logged_cost(
        self,
        client: TestClient,
        db_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        session_id = _create_session(client)

        async def _seed_generation_log() -> None:
            async with db_factory() as db:
                db.add(
                    GenerationLog(
                        session_id=session_id,
                        timestamp=datetime.now(tz=timezone.utc),
                        task_type="character_dialogue",
                        quality_tier="standard",
                        model_used="test-model",
                        latency_ms=120,
                        input_tokens=100,
                        output_tokens=40,
                        cost_usd=Decimal("0.125"),
                    )
                )
                await db.commit()

        import asyncio

        asyncio.get_event_loop().run_until_complete(_seed_generation_log())

        resp = client.get(f"/v1/sessions/{session_id}")

        assert resp.status_code == 200
        assert resp.json()["cost_consumed_usd"] == pytest.approx(0.125)

    def test_unknown_session_returns_404(self, client: TestClient) -> None:
        resp = client.get(f"/v1/sessions/{uuid4()}")
        assert resp.status_code == 404


class TestStartSession:
    def test_start_returns_active_status(self, client: TestClient) -> None:
        session_id = _create_session(client)
        resp = client.post(f"/v1/sessions/{session_id}/start")

        assert resp.status_code == 200
        assert resp.json()["status"] == "active"

    def test_unknown_session_returns_404(self, client: TestClient) -> None:
        resp = client.post(f"/v1/sessions/{uuid4()}/start")
        assert resp.status_code == 404

    def test_double_start_returns_409(self, client: TestClient) -> None:
        session_id = _create_session(client)
        client.post(f"/v1/sessions/{session_id}/start")
        resp = client.post(f"/v1/sessions/{session_id}/start")
        assert resp.status_code == 409


class TestPauseResumeSession:
    def test_resume_emits_narrator_bridge_event(self, client: TestClient) -> None:
        """AW-221 AC1: resume publishes a narrator_bridge ContentEvent to the bus."""
        from unittest.mock import AsyncMock, MagicMock, patch

        from engine.events.bus import SessionEventBus
        from engine.events.models import AudienceTarget, ContentEvent, EventCategory

        session_id = _create_session(client)
        client.post(f"/v1/sessions/{session_id}/start")
        client.post(f"/v1/sessions/{session_id}/pause")

        mock_bus = MagicMock(spec=SessionEventBus)
        mock_bus.publish = AsyncMock()

        def _l2_allowed() -> MagicMock:
            msg = MagicMock()
            msg.content = (
                '{"blocked": false, "confidence": 0.05, "category": "permitted"}'
            )
            choice = MagicMock()
            choice.message = msg
            usage = MagicMock()
            usage.prompt_tokens = 10
            usage.completion_tokens = 5
            resp = MagicMock()
            resp.choices = [choice]
            resp.usage = usage
            return resp

        def _narrator_response() -> MagicMock:
            msg = MagicMock()
            msg.content = "The investigation continues."
            choice = MagicMock()
            choice.message = msg
            usage = MagicMock()
            usage.prompt_tokens = 80
            usage.completion_tokens = 30
            resp = MagicMock()
            resp.choices = [choice]
            resp.usage = usage
            return resp

        with (
            patch(
                "api.routers.sessions._get_or_create_session_state",
                return_value=(mock_bus, MagicMock()),
            ),
            patch(
                "engine.routing.router.litellm.acompletion",
                new_callable=AsyncMock,
            ) as mock_completion,
        ):
            mock_completion.side_effect = [_l2_allowed(), _narrator_response()]
            resp = client.post(f"/v1/sessions/{session_id}/resume")

        assert resp.status_code == 200
        mock_bus.publish.assert_awaited_once()
        published: ContentEvent = mock_bus.publish.call_args[0][0]
        assert published.event_type == "narrator_bridge"
        assert published.category == EventCategory.narrative
        assert published.target_audience == AudienceTarget.all

    def test_pause_returns_paused_status(self, client: TestClient) -> None:
        session_id = _create_session(client)
        client.post(f"/v1/sessions/{session_id}/start")
        resp = client.post(f"/v1/sessions/{session_id}/pause")

        assert resp.status_code == 200
        assert resp.json()["status"] == "paused"

    def test_resume_returns_active_status(self, client: TestClient) -> None:
        from unittest.mock import AsyncMock, MagicMock, patch

        from engine.events.bus import SessionEventBus

        session_id = _create_session(client)
        client.post(f"/v1/sessions/{session_id}/start")
        client.post(f"/v1/sessions/{session_id}/pause")

        mock_bus = MagicMock(spec=SessionEventBus)
        mock_bus.publish = AsyncMock()
        with (
            patch(
                "api.routers.sessions._get_or_create_session_state",
                return_value=(mock_bus, MagicMock()),
            ),
            patch(
                "api.routers.sessions.generate_narrator_bridge",
                new_callable=AsyncMock,
                return_value=MagicMock(),
            ),
        ):
            resp = client.post(f"/v1/sessions/{session_id}/resume")

        assert resp.status_code == 200
        assert resp.json()["status"] == "active"

    def test_pause_writes_snapshot_and_interruption_event(
        self,
        client: TestClient,
        db_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        """AW-220 AC1 at the HTTP layer: pause persists arc_beat_states +
        session_interrupted event without any in-process state."""
        session_id = _create_session(client)
        client.post(f"/v1/sessions/{session_id}/start")
        resp = client.post(f"/v1/sessions/{session_id}/pause")
        assert resp.status_code == 200

        async def _read() -> tuple[int, int]:
            async with db_factory() as db:
                snaps = (
                    (
                        await db.execute(
                            select(ArcBeatState).where(
                                ArcBeatState.session_id == session_id
                            )
                        )
                    )
                    .scalars()
                    .all()
                )
                events = (
                    (
                        await db.execute(
                            select(Event).where(
                                Event.session_id == session_id,
                                Event.event_type == "session_interrupted",
                            )
                        )
                    )
                    .scalars()
                    .all()
                )
                return len(snaps), len(events)

        import asyncio

        snap_count, event_count = asyncio.get_event_loop().run_until_complete(_read())
        assert snap_count == 1
        assert event_count == 1

    def test_resume_via_http_restores_status_from_db_only(
        self,
        client: TestClient,
        db_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        """AW-220 AC2 at the HTTP layer: resume reads status + beat from
        the DB (the service holds no in-process session state)."""
        from unittest.mock import AsyncMock, MagicMock, patch

        from engine.events.bus import SessionEventBus

        session_id = _create_session(client)
        client.post(f"/v1/sessions/{session_id}/start")

        async def _set_beat() -> None:
            async with db_factory() as db:
                orm = await db.get(OrmSession, session_id)
                assert orm is not None
                orm.current_beat_id = "dig"
                await db.commit()

        import asyncio

        asyncio.get_event_loop().run_until_complete(_set_beat())

        client.post(f"/v1/sessions/{session_id}/pause")

        mock_bus = MagicMock(spec=SessionEventBus)
        mock_bus.publish = AsyncMock()
        with (
            patch(
                "api.routers.sessions._get_or_create_session_state",
                return_value=(mock_bus, MagicMock()),
            ),
            patch(
                "api.routers.sessions.generate_narrator_bridge",
                new_callable=AsyncMock,
                return_value=MagicMock(),
            ),
        ):
            resp = client.post(f"/v1/sessions/{session_id}/resume")

        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "active"
        assert body["current_beat_id"] == "dig"


class TestEndSession:
    def test_end_returns_completed_status(self, client: TestClient) -> None:
        session_id = _create_session(client)
        client.post(f"/v1/sessions/{session_id}/start")
        resp = client.post(f"/v1/sessions/{session_id}/end")

        assert resp.status_code == 200
        assert resp.json()["status"] == "completed"

    def test_unknown_session_returns_404(self, client: TestClient) -> None:
        resp = client.post(f"/v1/sessions/{uuid4()}/end")
        assert resp.status_code == 404

    def test_end_with_body_writes_completion_type_and_killer_flag(
        self,
        client: TestClient,
        db_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        import asyncio

        session_id = _create_session(client)
        client.post(f"/v1/sessions/{session_id}/start")
        resp = client.post(
            f"/v1/sessions/{session_id}/end",
            json={"completion_type": "interrupted", "killer_identified": True},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "completed"

        async def _check_event() -> None:
            async with db_factory() as db:
                result = await db.execute(
                    select(Event).where(
                        Event.session_id == session_id,
                        Event.event_type == "session_completed",
                    )
                )
                event = result.scalars().first()
                assert event is not None
                assert event.payload["completion_type"] == "interrupted"
                assert event.payload["killer_identified"] is True

        asyncio.get_event_loop().run_until_complete(_check_event())

    def test_end_with_invalid_completion_type_returns_422(
        self, client: TestClient
    ) -> None:
        session_id = _create_session(client)
        resp = client.post(
            f"/v1/sessions/{session_id}/end",
            json={"completion_type": "nonsense"},
        )
        assert resp.status_code == 422


class TestAddPlayer:
    def test_returns_201_with_join_token(self, client: TestClient) -> None:
        session_id = _create_session(client)
        resp = client.post(f"/v1/sessions/{session_id}/players")

        assert resp.status_code == 201
        body = resp.json()
        assert "participant_id" in body
        assert "join_token" in body
        assert "join_url" in body

    def test_unknown_session_returns_404(self, client: TestClient) -> None:
        resp = client.post(f"/v1/sessions/{uuid4()}/players")
        assert resp.status_code == 404


class TestJoinSession:
    def test_valid_token_returns_player_token(self, client: TestClient) -> None:
        session_id = _create_session(client)
        add = client.post(f"/v1/sessions/{session_id}/players")
        join_token = add.json()["join_token"]
        resp = client.get(f"/v1/sessions/{session_id}/join?token={join_token}")

        assert resp.status_code == 200
        assert "player_token" in resp.json()

    def test_invalid_token_returns_403(self, client: TestClient) -> None:
        session_id = _create_session(client)
        resp = client.get(f"/v1/sessions/{session_id}/join?token=not-a-real-token")
        assert resp.status_code == 403


# Reference the singleton so test imports are checked even though state
# lives in the DB.
assert _session_service is not None
assert SessionStatus is not None
