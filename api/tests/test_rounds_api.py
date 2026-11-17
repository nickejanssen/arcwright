"""Round endpoints: the current phase, menu, choices, readiness, holdings and
the host's move-on (AW-325, spec 0093 Parts C and D).

Each route's happy path, wrong role, wrong session and repeat request. The
engine rules themselves are tested in ``engine/tests``; here the handlers only
have to be thin. Auth dependencies are overridden so no GCP credentials are
needed. Uses only the made-up fixture case and arc.
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Iterator
from datetime import datetime, timezone
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from starlette.testclient import TestClient

from api import main as api_main
from api.auth import (
    JwtClaims,
    optional_player_or_host_jwt,
    require_host_jwt,
    require_player_jwt,
)
from api.main import app
from engine.db import get_async_session
from engine.db.testing import make_sqlite_session_factory
from engine.session.phases import host_move_on, tick
from engine.session.service import SessionService
from engine.tests.rounds_support import phased_arc

LEDGER_CONTENT = "You read the ledger closely."


def _now() -> datetime:
    return datetime.now(tz=timezone.utc)


class Who:
    """Which player or host the overridden auth dependencies speak for."""

    def __init__(self) -> None:
        self.session_id: UUID = uuid4()
        self.player_id: UUID = uuid4()
        self.host_id: UUID = uuid4()


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
    arc = phased_arc()
    for target in (
        "engine.session.service.load_arc_definition",
        "engine.session.phases.load_arc_definition",
        "engine.session.choices.load_arc_definition",
    ):
        monkeypatch.setattr(target, lambda _id, _arc=arc: _arc)

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
    factory: async_sessionmaker[AsyncSession],
    who: Who,
    *,
    players: int = 2,
    phase: str | None = None,
    beat: str = "beat_one",
) -> list[UUID]:
    """A started session with its first phase entered; optionally moved on by
    the host to ``beat``/``phase``. Returns the participant IDs and points the
    overridden auth at the first player."""
    arc = phased_arc()
    svc = SessionService()
    async with factory() as db:
        created, _ = await svc.create_session(
            db, arc_id=arc.arc_id, host_account_id=uuid4()
        )
        ids: list[UUID] = []
        for _ in range(players):
            participant, _ = await svc.add_player(db, created.session_id)
            ids.append(participant.participant_id)
        await svc.start_session(db, created.session_id)
        await tick(db, created.session_id, _now())
        if phase is not None:
            for _ in range(40):
                from engine.session.phases import current_phase

                state = await current_phase(db, created.session_id)
                assert state is not None
                if (state.beat_id, state.phase) == (beat, phase):
                    break
                await host_move_on(db, created.session_id, _now())
        await db.commit()
    who.session_id = created.session_id
    who.player_id = ids[0]
    return ids


def url(who: Who, path: str) -> str:
    return f"/v1/sessions/{who.session_id}{path}"


class TestRoundState:
    @pytest.mark.asyncio
    async def test_the_round_route_names_beat_phase_deadline_and_lines(
        self, client: TestClient, db_factory: async_sessionmaker[AsyncSession], who: Who
    ) -> None:
        await seed(db_factory, who)
        response = client.get(url(who, "/round"))
        assert response.status_code == 200
        body = response.json()
        assert (body["beat_id"], body["phase"], body["status"]) == (
            "opening",
            "scene",
            "running",
        )
        assert body["deadline_at"] and 0 < body["seconds_left"] <= 20
        assert [line["text"] for line in body["lines"]] == ["Welcome to the house."]
        assert body["player_count"] == 2 and body["ready_count"] == 0

    @pytest.mark.asyncio
    async def test_the_round_route_for_an_unknown_session_is_404(
        self, client: TestClient, who: Who
    ) -> None:
        assert client.get(url(who, "/round")).status_code == 404

    @pytest.mark.asyncio
    async def test_a_token_for_another_session_is_refused_on_the_round_route(
        self, client: TestClient, db_factory: async_sessionmaker[AsyncSession], who: Who
    ) -> None:
        await seed(db_factory, who)
        app.dependency_overrides[optional_player_or_host_jwt] = lambda: JwtClaims(
            uid="x", session_id=uuid4(), player_id=uuid4(), role="player"
        )
        assert client.get(url(who, "/round")).status_code == 403


class TestMenuAndChoices:
    @pytest.mark.asyncio
    async def test_the_menu_route_lists_the_choices_and_the_budget(
        self, client: TestClient, db_factory: async_sessionmaker[AsyncSession], who: Who
    ) -> None:
        await seed(db_factory, who, phase="choices")
        response = client.get(url(who, "/me/menu"))
        assert response.status_code == 200
        body = response.json()
        assert body["open"] and body["remaining_budget"] == 6
        assert {i["opportunity_id"] for i in body["items"]} == {
            "o_ledger",
            "o_shed",
            "o_porter",
        }
        assert LEDGER_CONTENT not in response.text

    @pytest.mark.asyncio
    async def test_a_choice_returns_its_content_and_a_repeat_returns_the_same(
        self, client: TestClient, db_factory: async_sessionmaker[AsyncSession], who: Who
    ) -> None:
        await seed(db_factory, who, phase="choices")
        body = {"choice_id": "tap-1", "opportunity_id": "o_ledger"}
        first = client.post(url(who, "/me/choices"), json=body)
        again = client.post(url(who, "/me/choices"), json=body)
        assert first.status_code == again.status_code == 200
        assert first.json()["content"] == LEDGER_CONTENT
        assert first.json()["remaining_budget"] == 5
        assert not first.json()["replayed"] and again.json()["replayed"]
        assert {k: v for k, v in again.json().items() if k != "replayed"} == {
            k: v for k, v in first.json().items() if k != "replayed"
        }
        assert client.get(url(who, "/me/menu")).json()["remaining_budget"] == 5

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("body", "code"),
        [
            ({"choice_id": "x", "opportunity_id": "o_attic"}, "not_on_menu"),
            ({"choice_id": "y", "opportunity_id": "nope"}, "not_on_menu"),
        ],
    )
    async def test_a_choice_not_on_the_menu_is_409_with_a_code(
        self,
        client: TestClient,
        db_factory: async_sessionmaker[AsyncSession],
        who: Who,
        body: dict[str, str],
        code: str,
    ) -> None:
        await seed(db_factory, who, phase="choices")
        response = client.post(url(who, "/me/choices"), json=body)
        assert response.status_code == 409
        assert response.json()["detail"]["code"] == code

    @pytest.mark.asyncio
    async def test_a_choice_outside_a_choices_phase_is_409(
        self, client: TestClient, db_factory: async_sessionmaker[AsyncSession], who: Who
    ) -> None:
        await seed(db_factory, who)
        response = client.post(
            url(who, "/me/choices"),
            json={"choice_id": "x", "opportunity_id": "o_ledger"},
        )
        assert response.status_code == 409
        assert response.json()["detail"]["code"] == "not_in_choices_phase"

    @pytest.mark.asyncio
    async def test_a_bad_body_is_422(
        self, client: TestClient, db_factory: async_sessionmaker[AsyncSession], who: Who
    ) -> None:
        await seed(db_factory, who, phase="choices")
        assert client.post(url(who, "/me/choices"), json={}).status_code == 422

    @pytest.mark.asyncio
    async def test_the_seventh_paid_choice_is_refused_by_the_route(
        self, client: TestClient, db_factory: async_sessionmaker[AsyncSession], who: Who
    ) -> None:
        ids = await seed(db_factory, who, phase="choices")
        # Spend through the engine to reach a spent budget quickly.
        from engine.db.orm import Decision

        async with db_factory() as db:
            for _ in range(6):
                db.add(
                    Decision(
                        session_id=who.session_id,
                        decision_type="choice",
                        context={
                            "choice_id": str(uuid4()),
                            "participant_id": str(ids[0]),
                            "opportunity_id": f"gone-{uuid4()}",
                        },
                        outcome={"cost": 1, "gave": [], "first_time": True},
                    )
                )
            await db.commit()
        response = client.post(
            url(who, "/me/choices"),
            json={"choice_id": "late", "opportunity_id": "o_ledger"},
        )
        assert response.status_code == 409
        assert response.json()["detail"]["code"] == "budget_exhausted"


class TestReadyAndMoveOn:
    @pytest.mark.asyncio
    async def test_everyone_marking_ready_moves_the_phase_on(
        self, client: TestClient, db_factory: async_sessionmaker[AsyncSession], who: Who
    ) -> None:
        ids = await seed(db_factory, who)
        first = client.post(url(who, "/me/ready"))
        assert first.status_code == 200 and first.json()["phase"] == "scene"
        who.player_id = ids[1]
        second = client.post(url(who, "/me/ready"))
        assert second.status_code == 200
        assert (second.json()["beat_id"], second.json()["phase"]) == (
            "opening",
            "bridge",
        )
        assert client.get(url(who, "/round")).json()["phase"] == "bridge"

    @pytest.mark.asyncio
    async def test_marking_ready_twice_is_harmless(
        self, client: TestClient, db_factory: async_sessionmaker[AsyncSession], who: Who
    ) -> None:
        await seed(db_factory, who)
        assert client.post(url(who, "/me/ready")).status_code == 200
        assert client.post(url(who, "/me/ready")).status_code == 200
        assert client.get(url(who, "/round")).json()["ready_count"] == 1

    @pytest.mark.asyncio
    async def test_the_host_move_on_route_ends_the_phase(
        self, client: TestClient, db_factory: async_sessionmaker[AsyncSession], who: Who
    ) -> None:
        await seed(db_factory, who)
        response = client.post(url(who, "/round/move-on"))
        assert response.status_code == 200
        assert response.json()["phase"] == "bridge"

    @pytest.mark.asyncio
    async def test_move_on_needs_the_host_token(
        self, client: TestClient, db_factory: async_sessionmaker[AsyncSession], who: Who
    ) -> None:
        await seed(db_factory, who)
        app.dependency_overrides.pop(require_host_jwt)
        assert client.post(url(who, "/round/move-on")).status_code == 401
        assert client.get(url(who, "/round")).json()["phase"] == "scene"

    @pytest.mark.asyncio
    async def test_a_host_token_for_another_session_is_refused(
        self, client: TestClient, db_factory: async_sessionmaker[AsyncSession], who: Who
    ) -> None:
        await seed(db_factory, who)
        app.dependency_overrides[require_host_jwt] = lambda: JwtClaims(
            uid="h", session_id=uuid4(), player_id=uuid4(), role="host"
        )
        assert client.post(url(who, "/round/move-on")).status_code == 403

    @pytest.mark.asyncio
    async def test_the_ready_route_in_the_mini_game_phase_is_409(
        self, client: TestClient, db_factory: async_sessionmaker[AsyncSession], who: Who
    ) -> None:
        await seed(db_factory, who, phase="mini_game")
        response = client.post(url(who, "/me/ready"))
        assert response.status_code == 409
        assert response.json()["detail"]["code"] == "phase_not_ready_able"


class TestHoldings:
    @pytest.mark.asyncio
    async def test_holdings_list_what_the_player_found_with_its_text(
        self, client: TestClient, db_factory: async_sessionmaker[AsyncSession], who: Who
    ) -> None:
        await seed(db_factory, who, phase="choices")
        client.post(
            url(who, "/me/choices"),
            json={"choice_id": "a", "opportunity_id": "o_ledger"},
        )
        response = client.get(url(who, "/me/holdings"))
        assert response.status_code == 200
        ids = {c["concept_id"] for c in response.json()["concepts"]}
        assert ids == {"c_open_a", "c_open_b", "c_ledger"}
        assert "standing" not in response.text and "misleading" not in response.text


class TestWhoMayCall:
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("method", "path"),
        [
            ("get", "/me/menu"),
            ("post", "/me/choices"),
            ("post", "/me/ready"),
            ("get", "/me/holdings"),
        ],
    )
    async def test_a_player_token_for_another_session_is_403(
        self,
        client: TestClient,
        db_factory: async_sessionmaker[AsyncSession],
        who: Who,
        method: str,
        path: str,
    ) -> None:
        await seed(db_factory, who)
        app.dependency_overrides[require_player_jwt] = lambda: JwtClaims(
            uid="p", session_id=uuid4(), player_id=who.player_id, role="player"
        )
        kwargs = {"json": {"choice_id": "a", "opportunity_id": "o_ledger"}}
        response = getattr(client, method)(
            url(who, path), **(kwargs if method == "post" else {})
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("method", "path"),
        [
            ("get", "/me/menu"),
            ("post", "/me/choices"),
            ("post", "/me/ready"),
            ("get", "/me/holdings"),
        ],
    )
    async def test_someone_who_is_not_in_the_session_is_403(
        self,
        client: TestClient,
        db_factory: async_sessionmaker[AsyncSession],
        who: Who,
        method: str,
        path: str,
    ) -> None:
        await seed(db_factory, who)
        who.player_id = uuid4()
        kwargs = {"json": {"choice_id": "a", "opportunity_id": "o_ledger"}}
        response = getattr(client, method)(
            url(who, path), **(kwargs if method == "post" else {})
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("method", "path"),
        [
            ("get", "/me/menu"),
            ("post", "/me/choices"),
            ("post", "/me/ready"),
            ("get", "/me/holdings"),
            ("post", "/round/move-on"),
        ],
    )
    async def test_no_token_is_401(
        self,
        client: TestClient,
        db_factory: async_sessionmaker[AsyncSession],
        who: Who,
        method: str,
        path: str,
    ) -> None:
        await seed(db_factory, who)
        app.dependency_overrides.pop(require_player_jwt)
        app.dependency_overrides.pop(require_host_jwt)
        kwargs = {"json": {"choice_id": "a", "opportunity_id": "o_ledger"}}
        response = getattr(client, method)(
            url(who, path), **(kwargs if method == "post" else {})
        )
        assert response.status_code == 401


class TestTheClockLoopIsWired:
    def test_the_app_starts_and_stops_the_tick_loop(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        events: list[str] = []

        async def fake_loop() -> None:
            events.append("started")
            try:
                await asyncio.sleep(3600)
            except asyncio.CancelledError:
                events.append("cancelled")
                raise

        monkeypatch.setattr(api_main, "run_tick_loop", fake_loop)
        with TestClient(app):
            pass
        assert events == ["started", "cancelled"]
