"""Integration tests for the cost and usage REST API endpoints (AW-223).

Exercises routes at the HTTP level via starlette.testclient.TestClient
against an in-memory SQLite-backed AsyncSession.

Covers: route registration, API-key auth guard, 404 for unknown session,
response schema shape, and AC3 (no pricing fields in response).
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from starlette.testclient import TestClient

from api.auth import ApiCaller, require_api_key
from api.main import app
from engine.db import get_async_session
from engine.db.testing import patch_metadata_for_sqlite

patch_metadata_for_sqlite()

from engine.db.orm import Base  # noqa: E402 -- must follow patch call


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
    """TestClient with auth overridden and DB wired to in-memory SQLite."""

    async def _override_db() -> AsyncIterator[AsyncSession]:
        async with db_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    from unittest.mock import patch

    with (
        patch("api.routers.sessions._ensure_firebase_app"),
        patch("firebase_admin.auth.create_custom_token", return_value=b"fake-token"),
    ):
        app.dependency_overrides[require_api_key] = lambda: ApiCaller(
            api_key="test-key"
        )
        app.dependency_overrides[get_async_session] = _override_db
        with TestClient(app) as c:
            yield c
        app.dependency_overrides.clear()


def _create_session_id(client: TestClient) -> str:
    resp = client.post("/v1/sessions", json={"arc_id": "test-arc"})
    assert resp.status_code == 201, resp.text
    return resp.json()["session_id"]


class TestGetSessionCostSummary:
    def test_known_session_returns_200(self, client: TestClient) -> None:
        session_id = _create_session_id(client)
        resp = client.get(f"/v1/sessions/{session_id}/cost-summary")
        assert resp.status_code == 200

    def test_unknown_session_returns_404(self, client: TestClient) -> None:
        resp = client.get(f"/v1/sessions/{uuid4()}/cost-summary")
        assert resp.status_code == 404

    def test_response_has_required_fields(self, client: TestClient) -> None:
        session_id = _create_session_id(client)
        body = client.get(f"/v1/sessions/{session_id}/cost-summary").json()

        assert "total_cost_usd" in body
        assert "total_input_tokens" in body
        assert "total_output_tokens" in body
        assert "total_generation_count" in body
        assert "by_task_type" in body
        assert "by_player_count" in body

    def test_response_has_no_pricing_fields(self, client: TestClient) -> None:
        session_id = _create_session_id(client)
        body = client.get(f"/v1/sessions/{session_id}/cost-summary").json()

        banned = {"revenue", "margin", "price", "profit"}
        assert not banned & set(body.keys()), (
            f"Response must not contain pricing fields: {banned & set(body.keys())}"
        )

    def test_session_id_echoed_in_response(self, client: TestClient) -> None:
        session_id = _create_session_id(client)
        body = client.get(f"/v1/sessions/{session_id}/cost-summary").json()
        assert body["session_id"] == session_id

    def test_empty_session_returns_zero_totals(self, client: TestClient) -> None:
        session_id = _create_session_id(client)
        body = client.get(f"/v1/sessions/{session_id}/cost-summary").json()
        assert body["total_generation_count"] == 0
        assert body["by_task_type"] == []
        assert body["by_player_count"] == []


class TestGetUsage:
    def test_global_returns_200(self, client: TestClient) -> None:
        resp = client.get("/v1/usage")
        assert resp.status_code == 200

    def test_arc_id_filter_returns_200(self, client: TestClient) -> None:
        resp = client.get("/v1/usage?arc_id=test-arc")
        assert resp.status_code == 200

    def test_response_has_required_fields(self, client: TestClient) -> None:
        body = client.get("/v1/usage").json()

        assert "total_cost_usd" in body
        assert "total_input_tokens" in body
        assert "total_output_tokens" in body
        assert "total_generation_count" in body
        assert "by_task_type" in body
        assert "by_player_count" in body

    def test_response_has_no_pricing_fields(self, client: TestClient) -> None:
        body = client.get("/v1/usage").json()
        banned = {"revenue", "margin", "price", "profit"}
        assert not banned & set(body.keys())
