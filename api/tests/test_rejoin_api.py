"""A phone drops mid-round and rejoins as the same player (AW-308).

The whole path runs through the real API routes: join by room code, start,
investigate, drop, come back. "Drop" means the client is closed; "rejoin" means
a new client that holds only the sign-in the phone kept (spec 0095 decision 3).
Only the Firebase signing and checking calls are replaced, so a token carries
exactly the claims ``/lobby-join`` signed into it. Every role and seat check
runs for real. Made-up arc and case only.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import AbstractContextManager
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

import pytest
from firebase_admin import auth as firebase_auth
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from api import auth
from api.main import app
from api.routers import events, lobby
from engine.db import get_async_session
from engine.db.testing import make_sqlite_session_factory
from engine.events.bus import SessionEventBus
from engine.events.fanout import SessionConnectionRegistry
from engine.session.phases import current_phase, host_move_on, tick
from engine.session.service import SessionService
from engine.tests.rounds_support import fixture_arc_registered, phased_arc


def _now() -> datetime:
    return datetime.now(tz=timezone.utc)


class SignIns:
    """Stands in for Firebase: a signed token maps back to its own claims."""

    def __init__(self) -> None:
        self._claims: dict[str, dict[str, Any]] = {}

    def create_custom_token(self, uid: str, claims: dict[str, Any]) -> bytes:
        token = f"token-{len(self._claims)}"
        self._claims[token] = {"uid": uid, **claims}
        return token.encode("utf-8")

    def decode(self, token: str) -> dict[str, Any]:
        return self._claims[token]


@pytest.mark.asyncio
async def test_a_dropped_phone_rejoins_with_its_own_holdings_and_findings(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine, sessions = await make_sqlite_session_factory()
    arc = phased_arc()
    sign_ins = SignIns()

    async def request_session() -> AsyncIterator[AsyncSession]:
        async with sessions() as db, db.begin():
            yield db

    overrides: dict[Any, Any] = app.dependency_overrides
    monkeypatch.setitem(overrides, get_async_session, request_session)
    monkeypatch.setattr(lobby, "_ensure_firebase_app", lambda: None)
    monkeypatch.setattr(
        firebase_auth, "create_custom_token", sign_ins.create_custom_token
    )
    monkeypatch.setattr(auth, "_decode_bearer", sign_ins.decode)
    registered: AbstractContextManager[None] = fixture_arc_registered(arc)
    try:
        with registered:
            monkeypatch.setattr(lobby, "load_arc_definition", lambda _: arc)
            async with sessions() as db, db.begin():
                created, _ = await SessionService().create_session(
                    db, arc_id=arc.arc_id, host_account_id=uuid4()
                )
            session_id = created.session_id
            monkeypatch.setitem(events._buses, session_id, SessionEventBus())
            monkeypatch.setitem(
                events._registries, session_id, SessionConnectionRegistry()
            )
            base = f"/v1/sessions/{session_id}"

            def phone() -> AsyncClient:
                return AsyncClient(
                    transport=ASGITransport(app=app), base_url="http://test"
                )

            async def get(client: AsyncClient, token: str, path: str) -> Any:
                response = await client.get(
                    f"{base}{path}", headers={"Authorization": f"Bearer {token}"}
                )
                assert response.status_code == 200, (path, response.text)
                return response.json()

            async def own_view(client: AsyncClient, token: str) -> dict[str, Any]:
                return {
                    path: await get(client, token, path)
                    for path in ("/me/seat", "/me/holdings", "/me/menu")
                }

            async def join(client: AsyncClient, name: str) -> dict[str, Any]:
                response = await client.post(
                    "/v1/lobby-join",
                    json={"name": name, "join_code": created.join_code},
                )
                assert response.status_code == 201, response.text
                body: dict[str, Any] = response.json()
                return body

            async def choose(
                client: AsyncClient, token: str, opportunity_id: str
            ) -> str:
                response = await client.post(
                    f"{base}/me/choices",
                    headers={"Authorization": f"Bearer {token}"},
                    json={
                        "choice_id": str(uuid4()),
                        "opportunity_id": opportunity_id,
                    },
                )
                assert response.status_code == 200, response.text
                content: str = response.json()["content"]
                return content

            async with phone() as first, phone() as second:
                ada = await join(first, "Ada")
                bo = await join(second, "Bo")
                ada_token, bo_token = ada["player_token"], bo["player_token"]

                started = await first.post(
                    f"{base}/start", headers={"Authorization": f"Bearer {ada_token}"}
                )
                assert started.status_code == 200, started.text
                async with sessions() as db, db.begin():
                    await tick(db, session_id, _now())
                    for _ in range(40):
                        state = await current_phase(db, session_id)
                        assert state is not None
                        if state.phase == "choices":
                            break
                        await host_move_on(db, session_id, _now())
                    reached = await current_phase(db, session_id)
                    assert reached is not None and reached.phase == "choices"

                # Each player looks into something different.
                ada_menu = await get(first, ada_token, "/me/menu")
                assert len(ada_menu["items"]) >= 2
                ada_pick = ada_menu["items"][0]["opportunity_id"]
                bo_pick = ada_menu["items"][1]["opportunity_id"]
                ada_found = await choose(first, ada_token, ada_pick)
                bo_found = await choose(second, bo_token, bo_pick)
                assert ada_found != bo_found

                ada_before = await own_view(first, ada_token)
                bo_before = await own_view(second, bo_token)

            # Both sets are private and different, so a mix-up would show.
            assert ada_before != bo_before
            assert ada_before["/me/holdings"] != bo_before["/me/holdings"]

            # Ada's browser is closed. A new one opens the join link with the
            # sign-in it kept: it reads the lobby and never joins again.
            async with phone() as reopened:
                room_state = await reopened.get(f"{base}/lobby")
                assert room_state.json()["status"] == "active"
                ada_after = await own_view(reopened, ada_token)

                assert ada_after == ada_before
                assert ada_after["/me/seat"]["participant_id"] == ada["participant_id"]
                taken = {
                    item["opportunity_id"]
                    for item in ada_after["/me/menu"]["items"]
                    if item["taken"]
                }
                assert taken == {ada_pick}

                # Her own finding can be reread, at no further cost.
                assert await choose(reopened, ada_token, ada_pick) == ada_found
                reread = await get(reopened, ada_token, "/me/menu")
                assert (
                    reread["remaining_budget"]
                    == ada_before["/me/menu"]["remaining_budget"]
                )

                # Nothing Bo found reaches Ada, on her reads or the public ones.
                assert bo_found not in str(ada_after)
                for public in ("/room", "/lobby", "/round", "/closing"):
                    shown = await reopened.get(f"{base}{public}")
                    assert shown.status_code == 200, (public, shown.text)
                    assert ada_found not in shown.text, public
                    assert bo_found not in shown.text, public

                # The other player's view is untouched by the rejoin.
                assert await own_view(reopened, bo_token) == bo_before

                # A second seat cannot be taken once the game has started.
                again = await reopened.post(
                    "/v1/lobby-join",
                    json={"name": "Ada", "join_code": created.join_code},
                )
                assert again.status_code == 409, again.text
                assert again.json()["detail"]["code"] == "game_started"
                seats = (await reopened.get(f"{base}/lobby")).json()["players"]
                assert {UUID(p["participant_id"]) for p in seats} == {
                    UUID(ada["participant_id"]),
                    UUID(bo["participant_id"]),
                }
    finally:
        await engine.dispose()
