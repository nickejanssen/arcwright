"""Closing routes: the public reveal, result and recap, and each player's own
part of the result (AW-327, spec 0094 Part J).

Each route's happy path, wrong role, wrong session and the privacy rule. The
rules are tested in ``engine/tests``; the handlers only call one engine read.
Auth dependencies are overridden so no GCP credentials are needed. Made-up case,
arc and lines only.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from starlette.testclient import TestClient

from api.auth import (
    JwtClaims,
    optional_player_or_host_jwt,
    require_host_jwt,
    require_player_jwt,
)
from api.main import app
from api.tests.test_rounds_api import Who, _now, url
from engine.db import get_async_session
from engine.db.testing import make_sqlite_session_factory
from engine.knowledge.holdings import grant_concept
from engine.session.phases import (
    current_phase,
    host_move_on,
    lock_theory,
    save_theory_draft,
    tick,
)
from engine.session.service import SessionService
from engine.tests.rounds_support import closing_arc, timer_race_registry

RIGHT = {"slot_who": "marlowe", "slot_how": "c_how_true"}
WRONG = {"slot_who": "pinecone", "slot_how": "c_how_true"}


@pytest_asyncio.fixture()
async def db_factory() -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    engine, factory = await make_sqlite_session_factory()
    try:
        yield factory
    finally:
        await engine.dispose()


@pytest.fixture()
def who() -> Who:
    return Who()


@pytest.fixture()
def client(
    db_factory: async_sessionmaker[AsyncSession],
    who: Who,
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[TestClient]:
    arc = closing_arc()
    for target in (
        "engine.session.service.load_arc_definition",
        "engine.session.phases.load_arc_definition",
        "engine.session.choices.load_arc_definition",
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

    app.dependency_overrides[require_player_jwt] = lambda: JwtClaims(
        uid="p", session_id=who.session_id, player_id=who.player_id, role="player"
    )
    app.dependency_overrides[require_host_jwt] = lambda: JwtClaims(
        uid="h", session_id=who.session_id, player_id=who.host_id, role="host"
    )
    app.dependency_overrides[optional_player_or_host_jwt] = lambda: None
    app.dependency_overrides[get_async_session] = _override_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


async def seed(
    factory: async_sessionmaker[AsyncSession], who: Who
) -> tuple[list[UUID], list[UUID]]:
    """A started two-player session at the start of Last Call. The overridden
    auth speaks for the first player. Returns participant and character IDs."""
    arc = closing_arc()
    svc = SessionService()
    async with factory() as db:
        created, _ = await svc.create_session(
            db, arc_id=arc.arc_id, host_account_id=uuid4()
        )
        ids: list[UUID] = []
        characters: list[UUID] = []
        for _ in range(2):
            participant, _ = await svc.add_player(db, created.session_id)
            ids.append(participant.participant_id)
            characters.append(participant.character_id)
        await svc.start_session(db, created.session_id)
        await tick(db, created.session_id, _now())
        for _ in range(40):
            state = await current_phase(db, created.session_id)
            assert state is not None
            if state.phase == "commit":
                break
            await host_move_on(db, created.session_id, _now())
        for character in characters:
            await grant_concept(
                db,
                session_id=created.session_id,
                character_id=character,
                concept_id="c_how_true",
                text="made up",
            )
        await db.commit()
    who.session_id = created.session_id
    who.player_id = ids[0]
    return ids, characters


async def lock_both(
    factory: async_sessionmaker[AsyncSession], who: Who, ids: list[UUID]
) -> None:
    """Player one is right, player two is wrong; both lock. Last Call ends and
    the session is at the reveal."""
    async with factory() as db:
        for participant, theory in zip(ids, (RIGHT, WRONG), strict=True):
            await save_theory_draft(
                db, who.session_id, participant, theory, "c_how_true", _now()
            )
            await lock_theory(db, who.session_id, participant, _now())
        await db.commit()


async def move_on(factory: async_sessionmaker[AsyncSession], who: Who) -> str:
    async with factory() as db:
        state = await host_move_on(db, who.session_id, _now())
        await db.commit()
        return state.phase


class TestBeforeTheResult:
    @pytest.mark.asyncio
    async def test_nothing_is_reached_while_players_are_still_building_theories(
        self, client: TestClient, db_factory: async_sessionmaker[AsyncSession], who: Who
    ) -> None:
        await seed(db_factory, who)
        response = client.get(url(who, "/closing"))
        assert response.status_code == 200
        assert response.json() == {"reveal": None, "result": None, "recap": None}
        mine = client.get(url(who, "/me/result"))
        assert mine.status_code == 409
        assert mine.json()["detail"]["code"] == "result_not_ready"

    @pytest.mark.asyncio
    async def test_the_reveal_is_readable_but_holds_no_right_or_wrong(
        self, client: TestClient, db_factory: async_sessionmaker[AsyncSession], who: Who
    ) -> None:
        ids, _ = await seed(db_factory, who)
        await lock_both(db_factory, who, ids)
        response = client.get(url(who, "/closing"))
        body = response.json()
        assert body["result"] is None and body["recap"] is None
        assert [p["participant_id"] for p in body["reveal"]["players"]] == sorted(
            str(i) for i in ids
        )
        text = response.text.casefold()
        for word in ("solved", "winners", "decided_by", "right"):
            assert word not in text
        assert client.get(url(who, "/me/result")).status_code == 409


class TestTheResultRoutes:
    @pytest.mark.asyncio
    async def test_the_public_result_and_each_players_own_part(
        self, client: TestClient, db_factory: async_sessionmaker[AsyncSession], who: Who
    ) -> None:
        ids, _ = await seed(db_factory, who)
        await lock_both(db_factory, who, ids)
        assert await move_on(db_factory, who) == "scene"
        assert await move_on(db_factory, who) == "result"

        public = client.get(url(who, "/closing")).json()["result"]
        assert public["decided_by"] == "only_solver"
        assert [w["participant_id"] for w in public["winners"]] == [str(ids[0])]
        assert {p["participant_id"]: p["solved"] for p in public["players"]} == {
            str(ids[0]): True,
            str(ids[1]): False,
        }
        assert "slots" not in client.get(url(who, "/closing")).text

        mine = client.get(url(who, "/me/result"))
        assert mine.status_code == 200
        assert mine.json()["participant_id"] == str(ids[0])
        assert [s["right"] for s in mine.json()["slots"]] == [True, True]

        who.player_id = ids[1]
        theirs = client.get(url(who, "/me/result")).json()
        assert theirs["participant_id"] == str(ids[1])
        assert [s["right"] for s in theirs["slots"]] == [False, True]

    @pytest.mark.asyncio
    async def test_the_recap_appears_once_its_phase_begins(
        self, client: TestClient, db_factory: async_sessionmaker[AsyncSession], who: Who
    ) -> None:
        ids, _ = await seed(db_factory, who)
        await lock_both(db_factory, who, ids)
        for _ in range(3):
            await move_on(db_factory, who)
        body = client.get(url(who, "/closing")).json()
        assert [line["participant_id"] for line in body["recap"]["lines"]] == sorted(
            str(i) for i in ids
        )
        assert all(line["text"] for line in body["recap"]["lines"])

    @pytest.mark.asyncio
    async def test_the_host_cannot_read_a_players_result(
        self, client: TestClient, db_factory: async_sessionmaker[AsyncSession], who: Who
    ) -> None:
        ids, _ = await seed(db_factory, who)
        await lock_both(db_factory, who, ids)
        for _ in range(2):
            await move_on(db_factory, who)
        who.player_id = who.host_id
        assert client.get(url(who, "/me/result")).status_code == 403

    @pytest.mark.asyncio
    async def test_someone_who_is_not_in_the_session_is_403(
        self, client: TestClient, db_factory: async_sessionmaker[AsyncSession], who: Who
    ) -> None:
        ids, _ = await seed(db_factory, who)
        await lock_both(db_factory, who, ids)
        for _ in range(2):
            await move_on(db_factory, who)
        who.player_id = uuid4()
        assert client.get(url(who, "/me/result")).status_code == 403

    @pytest.mark.asyncio
    async def test_a_token_for_another_session_is_403_on_both_routes(
        self, client: TestClient, db_factory: async_sessionmaker[AsyncSession], who: Who
    ) -> None:
        await seed(db_factory, who)
        app.dependency_overrides[require_player_jwt] = lambda: JwtClaims(
            uid="p", session_id=uuid4(), player_id=who.player_id, role="player"
        )
        assert client.get(url(who, "/me/result")).status_code == 403
        app.dependency_overrides[optional_player_or_host_jwt] = lambda: JwtClaims(
            uid="p", session_id=uuid4(), player_id=who.player_id, role="player"
        )
        assert client.get(url(who, "/closing")).status_code == 403

    @pytest.mark.asyncio
    async def test_an_unknown_session_is_404_on_the_public_route(
        self, client: TestClient, who: Who
    ) -> None:
        assert client.get(url(who, "/closing")).status_code == 404
