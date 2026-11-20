"""Who may use which control (AW-331, spec 0095 Q1 and M6, D-133).

A seated player's sign-in may pause and resume. Only the host seat's sign-in
(or the session creator's host token) may start, end, move on, send mini-game
host commands and hand the role on. The seat check runs for real; only the
token's own verification is replaced. Made-up arc and case only.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from starlette.testclient import TestClient

from api.auth import JwtClaims, require_player_jwt, require_player_or_host_jwt
from api.main import app
from engine.db import get_async_session
from engine.db.testing import make_sqlite_session_factory
from engine.session.phases import tick
from engine.session.service import SessionService
from engine.tests.rounds_support import closing_arc, timer_race_registry


def _now() -> datetime:
    return datetime.now(tz=timezone.utc)


class Signed:
    def __init__(self) -> None:
        self.session_id: UUID = uuid4()
        self.participant_id: UUID | None = None
        self.role: str = "player"

    def claims(self) -> JwtClaims:
        return JwtClaims(
            uid="u",
            session_id=self.session_id,
            player_id=self.participant_id,
            role=self.role,
        )


@pytest_asyncio.fixture()
async def db_factory() -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    engine, factory = await make_sqlite_session_factory()
    try:
        yield factory
    finally:
        await engine.dispose()


@pytest.fixture()
def signed() -> Signed:
    return Signed()


@pytest.fixture()
def client(
    db_factory: async_sessionmaker[AsyncSession],
    signed: Signed,
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[TestClient]:
    arc = closing_arc()
    for target in (
        "engine.session.service.load_arc_definition",
        "engine.session.phases.load_arc_definition",
        "engine.session.choices.load_arc_definition",
        "engine.session.closing.load_arc_definition",
    ):
        monkeypatch.setattr(target, lambda _id, _arc=arc: _arc)
    monkeypatch.setattr(
        "engine.session.mini_game_phase.build_registry", timer_race_registry
    )

    async def _override_db() -> AsyncIterator[AsyncSession]:
        async with db_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[require_player_jwt] = signed.claims
    app.dependency_overrides[require_player_or_host_jwt] = signed.claims
    app.dependency_overrides[get_async_session] = _override_db
    # Resuming asks the narrator for a bridge line; here it is a fixed stub.
    with (
        patch(
            "api.routers.sessions.generate_narrator_bridge",
            new=AsyncMock(side_effect=lambda *a, **k: _bridge(signed.session_id)),
        ),
        TestClient(app) as c,
    ):
        yield c
    app.dependency_overrides.clear()


def _bridge(session_id: UUID):  # type: ignore[no-untyped-def]
    from engine.events.models import (
        AudienceTarget,
        ContentEvent,
        EventCategory,
        PresentationHints,
    )

    return ContentEvent(
        session_id=session_id,
        timestamp=_now(),
        category=EventCategory.narrative,
        event_type="narrator_bridge",
        target_audience=AudienceTarget.all,
        payload={"text": "stub"},
        presentation_hints=PresentationHints(),
    )


async def seed(
    factory: async_sessionmaker[AsyncSession], signed: Signed, *, start: bool = True
) -> list[UUID]:
    """Three seated players; the first is the host seat. The sign-in speaks for
    the first player."""
    arc = closing_arc()
    svc = SessionService()
    async with factory() as db:
        created, _ = await svc.create_session(
            db, arc_id=arc.arc_id, host_account_id=uuid4()
        )
        ids = [
            (
                await svc.lobby_join(
                    db, join_code=str(created.join_code), display_name=name
                )
            ).participant_id
            for name in ("Ada", "Bo", "Cy")
        ]
        if start:
            await svc.start_session(db, created.session_id)
            await tick(db, created.session_id, _now())
        await db.commit()
    signed.session_id = created.session_id
    signed.participant_id = ids[0]
    return ids


def url(signed: Signed, path: str) -> str:
    return f"/v1/sessions/{signed.session_id}{path}"


HOST_ONLY = ["/start", "/end", "/round/move-on"]


class TestAPlayerSignIn:
    @pytest.mark.asyncio
    async def test_a_seated_player_can_pause_and_resume(
        self,
        client: TestClient,
        db_factory: async_sessionmaker[AsyncSession],
        signed: Signed,
    ) -> None:
        ids = await seed(db_factory, signed)
        signed.participant_id = ids[1]
        paused = client.post(url(signed, "/pause"))
        assert paused.status_code == 200, paused.text
        assert paused.json()["status"] == "paused"
        room = client.get(url(signed, "/room")).json()
        assert room["paused"] is True and room["paused_by"] == "Bo"
        resumed = client.post(url(signed, "/resume"))
        assert resumed.status_code == 200, resumed.text
        assert resumed.json()["status"] == "active"
        assert client.get(url(signed, "/room")).json()["paused"] is False

    @pytest.mark.asyncio
    @pytest.mark.parametrize("path", HOST_ONLY)
    async def test_a_plain_player_is_refused_on_each_host_control(
        self,
        client: TestClient,
        db_factory: async_sessionmaker[AsyncSession],
        signed: Signed,
        path: str,
    ) -> None:
        ids = await seed(db_factory, signed)
        signed.participant_id = ids[2]
        refused = client.post(url(signed, path))
        assert refused.status_code == 403
        assert client.get(url(signed, "/room")).json()["phase"] == "scene"

    @pytest.mark.asyncio
    async def test_a_plain_player_is_refused_on_host_commands_and_hand_over(
        self,
        client: TestClient,
        db_factory: async_sessionmaker[AsyncSession],
        signed: Signed,
    ) -> None:
        ids = await seed(db_factory, signed)
        signed.participant_id = ids[2]
        commands = client.post(
            url(signed, f"/mini-games/{uuid4()}/host-commands"),
            json={"command": "cancel", "params": {}},
        )
        assert commands.status_code == 403
        handed = client.post(
            url(signed, "/host/hand-over"), json={"to_participant_id": str(ids[2])}
        )
        assert handed.status_code == 403

    @pytest.mark.asyncio
    async def test_a_player_who_is_not_seated_is_refused_even_on_pause(
        self,
        client: TestClient,
        db_factory: async_sessionmaker[AsyncSession],
        signed: Signed,
    ) -> None:
        await seed(db_factory, signed)
        signed.participant_id = uuid4()
        assert client.post(url(signed, "/pause")).status_code == 403

    @pytest.mark.asyncio
    async def test_a_display_token_is_refused_everywhere(
        self,
        client: TestClient,
        db_factory: async_sessionmaker[AsyncSession],
        signed: Signed,
    ) -> None:
        await seed(db_factory, signed)
        signed.role = "display"
        for path in ["/pause", "/resume", *HOST_ONLY]:
            assert client.post(url(signed, path)).status_code == 403, path

    @pytest.mark.asyncio
    async def test_a_token_for_another_session_is_refused(
        self,
        client: TestClient,
        db_factory: async_sessionmaker[AsyncSession],
        signed: Signed,
    ) -> None:
        await seed(db_factory, signed)
        real = signed.session_id
        signed.session_id = uuid4()
        for path in ["/pause", "/resume", *HOST_ONLY]:
            refused = client.post(f"/v1/sessions/{real}{path}")
            assert refused.status_code == 403, path


class TestTheHostSeat:
    @pytest.mark.asyncio
    async def test_the_host_seat_starts_the_game_and_moves_on(
        self,
        client: TestClient,
        db_factory: async_sessionmaker[AsyncSession],
        signed: Signed,
    ) -> None:
        await seed(db_factory, signed, start=False)
        started = client.post(url(signed, "/start"))
        assert started.status_code == 200, started.text
        assert started.json()["status"] == "active"
        assert client.post(url(signed, "/round/move-on")).status_code in (200, 409)

    @pytest.mark.asyncio
    async def test_the_host_seat_can_end_the_game(
        self,
        client: TestClient,
        db_factory: async_sessionmaker[AsyncSession],
        signed: Signed,
    ) -> None:
        await seed(db_factory, signed)
        ended = client.post(url(signed, "/end"))
        assert ended.status_code == 200, ended.text
        assert client.get(url(signed, "/room")).json()["over"] is True

    @pytest.mark.asyncio
    async def test_the_host_seat_reaches_host_commands(
        self,
        client: TestClient,
        db_factory: async_sessionmaker[AsyncSession],
        signed: Signed,
    ) -> None:
        await seed(db_factory, signed)
        response = client.post(
            url(signed, f"/mini-games/{uuid4()}/host-commands"),
            json={"command": "cancel", "params": {}},
        )
        # Past the seat check: the run does not exist, so the engine says so.
        assert response.status_code in (404, 409), response.text


class TestTheOperatorKey:
    @pytest.mark.asyncio
    async def test_the_session_creators_host_token_does_every_control(
        self,
        client: TestClient,
        db_factory: async_sessionmaker[AsyncSession],
        signed: Signed,
    ) -> None:
        await seed(db_factory, signed, start=False)
        signed.role = "host"
        signed.participant_id = uuid4()
        assert client.post(url(signed, "/start")).status_code == 200
        assert client.post(url(signed, "/pause")).status_code == 200
        assert client.post(url(signed, "/resume")).status_code == 200
        assert client.post(url(signed, "/round/move-on")).status_code in (200, 409)
        assert client.post(url(signed, "/end")).status_code == 200


class TestAfterAHandOver:
    @pytest.mark.asyncio
    async def test_the_menus_swap_at_once_without_a_new_sign_in(
        self,
        client: TestClient,
        db_factory: async_sessionmaker[AsyncSession],
        signed: Signed,
    ) -> None:
        ids = await seed(db_factory, signed)
        handed = client.post(
            url(signed, "/host/hand-over"), json={"to_participant_id": str(ids[1])}
        )
        assert handed.status_code == 200
        # The old host holds the same sign-in and is now a plain player.
        assert client.post(url(signed, "/round/move-on")).status_code == 403
        assert client.post(url(signed, "/pause")).status_code == 200
        client.post(url(signed, "/resume"))
        # The new host holds a sign-in minted before the hand-over.
        signed.participant_id = ids[1]
        assert client.post(url(signed, "/round/move-on")).status_code in (200, 409)
        back = client.post(
            url(signed, "/host/hand-over"), json={"to_participant_id": str(ids[0])}
        )
        assert back.status_code == 200
        assert client.post(url(signed, "/round/move-on")).status_code == 403
