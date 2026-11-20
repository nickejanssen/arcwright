"""The room view, seat, survey and hand-over routes (AW-331, spec 0095).

Each route's happy path, wrong role, wrong session and the privacy rule. The
rules are tested in ``engine/tests``; the handlers only call one engine
function. ``require_player_or_host_jwt`` and ``require_player_jwt`` are
overridden with whoever the test says is signed in; the host-seat check itself
runs for real. Made-up arc and case only.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from datetime import datetime, timezone
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
    """Who the overridden sign-in dependencies speak for."""

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
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


async def seed(
    factory: async_sessionmaker[AsyncSession],
    signed: Signed,
    *,
    names: tuple[str, ...] = ("Ada", "Bo", "Cy"),
    start: bool = True,
) -> list[UUID]:
    """A session with seated players (the first is the host seat). The sign-in
    speaks for the first player. Returns the participant IDs."""
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
            for name in names
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


class TestRoom:
    @pytest.mark.asyncio
    async def test_the_room_needs_no_sign_in_and_carries_the_public_facts(
        self,
        client: TestClient,
        db_factory: async_sessionmaker[AsyncSession],
        signed: Signed,
    ) -> None:
        ids = await seed(db_factory, signed)
        app.dependency_overrides.pop(require_player_or_host_jwt)
        app.dependency_overrides.pop(require_player_jwt)
        response = client.get(url(signed, "/room"))
        assert response.status_code == 200
        body = response.json()
        assert body["session_status"] == "active"
        assert body["phase"] and body["round_title"]
        assert body["paused"] is False and body["over"] is False
        assert {p["participant_id"] for p in body["players"]} == {str(i) for i in ids}
        hosts = [p for p in body["players"] if p["is_host"]]
        assert [h["participant_id"] for h in hosts] == [str(ids[0])]
        assert {"ready", "locked", "answered_survey"} <= set(body["players"][0])

    @pytest.mark.asyncio
    async def test_a_signed_in_caller_gets_the_same_answer(
        self,
        client: TestClient,
        db_factory: async_sessionmaker[AsyncSession],
        signed: Signed,
    ) -> None:
        await seed(db_factory, signed)
        signed_in = client.get(url(signed, "/room")).json()
        app.dependency_overrides.pop(require_player_or_host_jwt)
        app.dependency_overrides.pop(require_player_jwt)
        unsigned = client.get(url(signed, "/room")).json()
        # The clock moves between the two reads; everything else is identical.
        signed_in.pop("seconds_left")
        unsigned.pop("seconds_left")
        assert unsigned == signed_in

    @pytest.mark.asyncio
    async def test_an_unknown_session_is_404(self, client: TestClient) -> None:
        assert client.get(f"/v1/sessions/{uuid4()}/room").status_code == 404

    @pytest.mark.asyncio
    async def test_a_survey_answer_shows_only_as_yes_or_no(
        self,
        client: TestClient,
        db_factory: async_sessionmaker[AsyncSession],
        signed: Signed,
    ) -> None:
        ids = await seed(db_factory, signed)
        saved = client.put(
            url(signed, "/me/survey"),
            json={"answers": {"fun": 5}, "comment": "a secret opinion"},
        )
        assert saved.status_code == 200
        room = client.get(url(signed, "/room"))
        assert "secret opinion" not in room.text
        flags = {
            p["participant_id"]: p["answered_survey"] for p in room.json()["players"]
        }
        assert flags[str(ids[0])] is True
        assert list(flags.values()).count(True) == 1


class TestSeat:
    @pytest.mark.asyncio
    async def test_the_first_seat_is_host_and_the_others_are_players(
        self,
        client: TestClient,
        db_factory: async_sessionmaker[AsyncSession],
        signed: Signed,
    ) -> None:
        ids = await seed(db_factory, signed)
        first = client.get(url(signed, "/me/seat")).json()
        assert first == {
            "participant_id": str(ids[0]),
            "display_name": "Ada",
            "role": "host",
        }
        signed.participant_id = ids[1]
        second = client.get(url(signed, "/me/seat")).json()
        assert second["role"] == "player" and second["display_name"] == "Bo"

    @pytest.mark.asyncio
    async def test_someone_not_seated_here_is_403(
        self,
        client: TestClient,
        db_factory: async_sessionmaker[AsyncSession],
        signed: Signed,
    ) -> None:
        await seed(db_factory, signed)
        signed.participant_id = uuid4()
        assert client.get(url(signed, "/me/seat")).status_code == 403

    @pytest.mark.asyncio
    async def test_a_token_for_another_session_is_403(
        self,
        client: TestClient,
        db_factory: async_sessionmaker[AsyncSession],
        signed: Signed,
    ) -> None:
        await seed(db_factory, signed)
        real = signed.session_id
        signed.session_id = uuid4()
        assert client.get(f"/v1/sessions/{real}/me/seat").status_code == 403


class TestSurvey:
    @pytest.mark.asyncio
    async def test_save_read_and_replace(
        self,
        client: TestClient,
        db_factory: async_sessionmaker[AsyncSession],
        signed: Signed,
    ) -> None:
        await seed(db_factory, signed)
        assert client.get(url(signed, "/me/survey")).json() == {
            "answered": False,
            "answers": {},
            "comment": None,
        }
        first = client.put(url(signed, "/me/survey"), json={"answers": {"fun": 2}})
        assert first.status_code == 200 and first.json()["answered"] is True
        client.put(
            url(signed, "/me/survey"),
            json={"answers": {"fun": 5, "length": "long"}, "comment": "good"},
        )
        read = client.get(url(signed, "/me/survey")).json()
        assert read == {
            "answered": True,
            "answers": {"fun": 5, "length": "long"},
            "comment": "good",
        }

    @pytest.mark.asyncio
    async def test_nobody_else_can_read_it(
        self,
        client: TestClient,
        db_factory: async_sessionmaker[AsyncSession],
        signed: Signed,
    ) -> None:
        ids = await seed(db_factory, signed)
        client.put(url(signed, "/me/survey"), json={"answers": {"fun": 1}})
        signed.participant_id = ids[1]
        other = client.get(url(signed, "/me/survey")).json()
        assert other["answered"] is False and other["answers"] == {}

    @pytest.mark.asyncio
    async def test_a_bad_shape_is_422_and_a_stranger_is_403(
        self,
        client: TestClient,
        db_factory: async_sessionmaker[AsyncSession],
        signed: Signed,
    ) -> None:
        await seed(db_factory, signed)
        bad = client.put(url(signed, "/me/survey"), json={"answers": {"fun": 9}})
        assert bad.status_code == 422
        assert bad.json()["detail"]["code"] == "invalid_survey"
        signed.participant_id = uuid4()
        stranger = client.put(url(signed, "/me/survey"), json={"answers": {"fun": 3}})
        assert stranger.status_code == 403

    @pytest.mark.asyncio
    async def test_before_the_start_it_is_409(
        self,
        client: TestClient,
        db_factory: async_sessionmaker[AsyncSession],
        signed: Signed,
    ) -> None:
        await seed(db_factory, signed, start=False)
        early = client.put(url(signed, "/me/survey"), json={"answers": {"fun": 3}})
        assert early.status_code == 409
        assert early.json()["detail"]["code"] == "game_not_started"


class TestHandOver:
    @pytest.mark.asyncio
    async def test_the_host_seat_hands_the_role_on(
        self,
        client: TestClient,
        db_factory: async_sessionmaker[AsyncSession],
        signed: Signed,
    ) -> None:
        ids = await seed(db_factory, signed)
        done = client.post(
            url(signed, "/host/hand-over"), json={"to_participant_id": str(ids[1])}
        )
        assert done.status_code == 200
        assert done.json() == {"host_participant_id": str(ids[1])}
        assert client.get(url(signed, "/me/seat")).json()["role"] == "player"
        signed.participant_id = ids[1]
        assert client.get(url(signed, "/me/seat")).json()["role"] == "host"

    @pytest.mark.asyncio
    async def test_a_plain_player_cannot(
        self,
        client: TestClient,
        db_factory: async_sessionmaker[AsyncSession],
        signed: Signed,
    ) -> None:
        ids = await seed(db_factory, signed)
        signed.participant_id = ids[1]
        refused = client.post(
            url(signed, "/host/hand-over"), json={"to_participant_id": str(ids[1])}
        )
        assert refused.status_code == 403

    @pytest.mark.asyncio
    async def test_the_operator_host_token_can(
        self,
        client: TestClient,
        db_factory: async_sessionmaker[AsyncSession],
        signed: Signed,
    ) -> None:
        ids = await seed(db_factory, signed)
        signed.role = "host"
        signed.participant_id = uuid4()
        done = client.post(
            url(signed, "/host/hand-over"), json={"to_participant_id": str(ids[2])}
        )
        assert done.status_code == 200

    @pytest.mark.asyncio
    async def test_a_bad_target_is_refused_with_a_named_reason(
        self,
        client: TestClient,
        db_factory: async_sessionmaker[AsyncSession],
        signed: Signed,
    ) -> None:
        ids = await seed(db_factory, signed)
        same = client.post(
            url(signed, "/host/hand-over"), json={"to_participant_id": str(ids[0])}
        )
        assert same.status_code == 409
        assert same.json()["detail"]["code"] == "already_host"
        stranger = client.post(
            url(signed, "/host/hand-over"), json={"to_participant_id": str(uuid4())}
        )
        assert stranger.status_code == 403
        assert stranger.json()["detail"]["code"] == "not_a_participant"

    @pytest.mark.asyncio
    async def test_a_token_for_another_session_or_a_display_is_403(
        self,
        client: TestClient,
        db_factory: async_sessionmaker[AsyncSession],
        signed: Signed,
    ) -> None:
        ids = await seed(db_factory, signed)
        real = signed.session_id
        signed.session_id = uuid4()
        other = client.post(
            f"/v1/sessions/{real}/host/hand-over",
            json={"to_participant_id": str(ids[1])},
        )
        assert other.status_code == 403
        signed.session_id = real
        signed.role = "display"
        display = client.post(
            url(signed, "/host/hand-over"), json={"to_participant_id": str(ids[1])}
        )
        assert display.status_code == 403
