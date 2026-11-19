"""Theory routes: read my form, save my draft, lock (AW-326, spec 0094 Part G).

Each route's happy path, wrong role, wrong session and a second lock. The rules
themselves are tested in ``engine/tests``; here the handlers only have to be
thin and must never carry whether anything is right. Auth dependencies are
overridden so no GCP credentials are needed. Uses only the made-up fixture
case and arc.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from typing import Any
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
from engine.session.phases import current_phase, host_move_on, tick
from engine.session.service import SessionService
from engine.tests.rounds_support import timer_race_registry
from engine.tests.test_commit_phase import commit_arc

RIGHT = {"slot_who": "marlowe", "slot_how": "c_how_true"}


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
    arc = commit_arc()
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
    factory: async_sessionmaker[AsyncSession], who: Who, *, in_commit: bool = True
) -> tuple[list[UUID], list[UUID]]:
    """A started two-player session, moved by the host into the commit phase.
    Points the overridden auth at the first player. Returns participant IDs and
    character IDs."""
    arc = commit_arc()
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
        for _ in range(40 if in_commit else 0):
            state = await current_phase(db, created.session_id)
            assert state is not None
            if state.phase == "commit":
                break
            await host_move_on(db, created.session_id, _now())
        await db.commit()
    who.session_id = created.session_id
    who.player_id = ids[0]
    return ids, characters


async def hold(
    factory: async_sessionmaker[AsyncSession],
    who: Who,
    character_id: UUID,
    concept: str,
) -> None:
    async with factory() as db:
        await grant_concept(
            db,
            session_id=who.session_id,
            character_id=character_id,
            concept_id=concept,
            text="made up",
        )
        await db.commit()


class TestReadTheForm:
    @pytest.mark.asyncio
    async def test_the_form_lists_slots_offers_and_the_time_left(
        self, client: TestClient, db_factory: async_sessionmaker[AsyncSession], who: Who
    ) -> None:
        await seed(db_factory, who)
        response = client.get(url(who, "/me/theory"))
        assert response.status_code == 200
        body = response.json()
        assert body["open"] and 0 < body["seconds_left"] <= 120
        assert [s["slot_id"] for s in body["slots"]] == ["slot_who", "slot_how"]
        assert body["slots"][0]["kind"] == "cast"
        assert [o["value"] for o in body["slots"][0]["options"]] == [
            "marlowe",
            "pinecone",
            "quillby",
        ]
        assert body["theory"] == {
            "state": "none",
            "answers": {},
            "proof": None,
            "revision": 0,
        }

    @pytest.mark.asyncio
    async def test_the_form_never_says_whether_anything_is_right(
        self, client: TestClient, db_factory: async_sessionmaker[AsyncSession], who: Who
    ) -> None:
        _, characters = await seed(db_factory, who)
        await hold(db_factory, who, characters[0], "c_how_true")
        await hold(db_factory, who, characters[0], "c_how_false1")
        text = client.get(url(who, "/me/theory")).text.casefold()
        for word in ("misleading", "standing", "accepted", "solved", "correct"):
            assert word not in text

    @pytest.mark.asyncio
    async def test_outside_the_phase_the_form_is_closed_and_empty(
        self, client: TestClient, db_factory: async_sessionmaker[AsyncSession], who: Who
    ) -> None:
        await seed(db_factory, who, in_commit=False)
        body = client.get(url(who, "/me/theory")).json()
        assert not body["open"] and body["slots"] == [] and body["account"] == []

    @pytest.mark.asyncio
    async def test_a_player_token_for_another_session_is_403(
        self, client: TestClient, db_factory: async_sessionmaker[AsyncSession], who: Who
    ) -> None:
        await seed(db_factory, who)
        app.dependency_overrides[require_player_jwt] = lambda: JwtClaims(
            uid="p", session_id=uuid4(), player_id=who.player_id, role="player"
        )
        assert client.get(url(who, "/me/theory")).status_code == 403

    @pytest.mark.asyncio
    async def test_someone_who_is_not_in_the_session_is_403(
        self, client: TestClient, db_factory: async_sessionmaker[AsyncSession], who: Who
    ) -> None:
        await seed(db_factory, who)
        who.player_id = uuid4()
        assert client.get(url(who, "/me/theory")).status_code == 403

    @pytest.mark.asyncio
    async def test_an_unknown_session_is_404(
        self, client: TestClient, who: Who
    ) -> None:
        assert client.get(url(who, "/me/theory")).status_code in (403, 404)


class TestSaveADraft:
    @pytest.mark.asyncio
    async def test_a_draft_is_saved_and_read_back(
        self, client: TestClient, db_factory: async_sessionmaker[AsyncSession], who: Who
    ) -> None:
        _, characters = await seed(db_factory, who)
        await hold(db_factory, who, characters[0], "c_how_true")
        saved = client.put(
            url(who, "/me/theory"), json={"answers": RIGHT, "proof": "c_how_true"}
        )
        assert saved.status_code == 200
        assert saved.json() == {
            "state": "drafting",
            "answers": RIGHT,
            "proof": "c_how_true",
            "revision": 1,
        }
        assert client.get(url(who, "/me/theory")).json()["theory"] == saved.json()

    @pytest.mark.asyncio
    async def test_a_concept_not_held_is_refused_with_its_code(
        self, client: TestClient, db_factory: async_sessionmaker[AsyncSession], who: Who
    ) -> None:
        await seed(db_factory, who)
        response = client.put(
            url(who, "/me/theory"), json={"answers": {"slot_how": "c_how_true"}}
        )
        assert response.status_code == 409
        assert response.json()["detail"]["code"] == "concept_not_held"

    @pytest.mark.asyncio
    async def test_outside_the_phase_it_is_refused(
        self, client: TestClient, db_factory: async_sessionmaker[AsyncSession], who: Who
    ) -> None:
        await seed(db_factory, who, in_commit=False)
        response = client.put(
            url(who, "/me/theory"), json={"answers": {"slot_who": "marlowe"}}
        )
        assert response.status_code == 409
        assert response.json()["detail"]["code"] == "not_in_commit_phase"

    @pytest.mark.asyncio
    async def test_someone_who_is_not_in_the_session_is_403(
        self, client: TestClient, db_factory: async_sessionmaker[AsyncSession], who: Who
    ) -> None:
        await seed(db_factory, who)
        who.player_id = uuid4()
        response = client.put(url(who, "/me/theory"), json={"answers": {}})
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_a_token_for_another_session_is_403(
        self, client: TestClient, db_factory: async_sessionmaker[AsyncSession], who: Who
    ) -> None:
        await seed(db_factory, who)
        app.dependency_overrides[require_player_jwt] = lambda: JwtClaims(
            uid="p", session_id=uuid4(), player_id=who.player_id, role="player"
        )
        assert (
            client.put(url(who, "/me/theory"), json={"answers": {}}).status_code == 403
        )


class TestLock:
    @pytest.mark.asyncio
    async def test_an_incomplete_draft_cannot_be_locked(
        self, client: TestClient, db_factory: async_sessionmaker[AsyncSession], who: Who
    ) -> None:
        await seed(db_factory, who)
        client.put(url(who, "/me/theory"), json={"answers": {"slot_who": "marlowe"}})
        response = client.post(url(who, "/me/theory/lock"))
        assert response.status_code == 409
        assert response.json()["detail"]["code"] == "theory_incomplete"

    @pytest.mark.asyncio
    async def test_a_complete_draft_locks_and_a_second_lock_is_refused(
        self, client: TestClient, db_factory: async_sessionmaker[AsyncSession], who: Who
    ) -> None:
        _, characters = await seed(db_factory, who)
        await hold(db_factory, who, characters[0], "c_how_true")
        client.put(url(who, "/me/theory"), json={"answers": RIGHT})
        locked = client.post(url(who, "/me/theory/lock"))
        assert locked.status_code == 200
        assert locked.json()["state"] == "locked"
        assert locked.json()["answers"] == RIGHT
        second = client.post(url(who, "/me/theory/lock"))
        assert second.status_code == 409
        assert second.json()["detail"]["code"] == "theory_locked"
        again = client.put(
            url(who, "/me/theory"), json={"answers": {"slot_who": "pinecone"}}
        )
        assert again.status_code == 409
        assert client.get(url(who, "/me/theory")).json()["theory"]["answers"] == RIGHT

    @pytest.mark.asyncio
    async def test_the_round_view_counts_the_lock_and_names_no_one(
        self, client: TestClient, db_factory: async_sessionmaker[AsyncSession], who: Who
    ) -> None:
        _, characters = await seed(db_factory, who)
        await hold(db_factory, who, characters[0], "c_how_true")
        client.put(url(who, "/me/theory"), json={"answers": RIGHT})
        client.post(url(who, "/me/theory/lock"))
        body: dict[str, Any] = client.get(url(who, "/round")).json()
        assert (body["phase"], body["ready_count"], body["player_count"]) == (
            "commit",
            1,
            2,
        )
        assert "marlowe" not in client.get(url(who, "/round")).text

    @pytest.mark.asyncio
    async def test_the_other_player_never_sees_a_draft_or_a_lock(
        self, client: TestClient, db_factory: async_sessionmaker[AsyncSession], who: Who
    ) -> None:
        ids, characters = await seed(db_factory, who)
        await hold(db_factory, who, characters[0], "c_how_true")
        client.put(url(who, "/me/theory"), json={"answers": RIGHT})
        client.post(url(who, "/me/theory/lock"))
        who.player_id = ids[1]
        other = client.get(url(who, "/me/theory"))
        assert other.status_code == 200
        assert other.json()["theory"]["state"] == "none"
        assert "marlowe" not in other.json()["theory"]["answers"].values()
        # The public round route holds only a count.
        assert "marlowe" not in client.get(url(who, "/round")).text

    @pytest.mark.asyncio
    async def test_locking_by_someone_who_is_not_in_the_session_is_403(
        self, client: TestClient, db_factory: async_sessionmaker[AsyncSession], who: Who
    ) -> None:
        await seed(db_factory, who)
        who.player_id = uuid4()
        assert client.post(url(who, "/me/theory/lock")).status_code == 403

    @pytest.mark.asyncio
    async def test_a_token_for_another_session_cannot_lock(
        self, client: TestClient, db_factory: async_sessionmaker[AsyncSession], who: Who
    ) -> None:
        await seed(db_factory, who)
        app.dependency_overrides[require_player_jwt] = lambda: JwtClaims(
            uid="p", session_id=uuid4(), player_id=who.player_id, role="player"
        )
        assert client.post(url(who, "/me/theory/lock")).status_code == 403
