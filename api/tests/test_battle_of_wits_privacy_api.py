"""Verify real Battle of Wits HTTP projections before and after reveal."""

from collections.abc import AsyncIterator
from datetime import timedelta
from functools import partial
from pathlib import Path
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api import auth
from api.main import app
from api.routers import events, mini_games
from engine.db import get_async_session
from engine.db.orm import SessionParticipant
from engine.db.testing import make_sqlite_session_factory
from engine.events.bus import SessionEventBus
from engine.events.fanout import SessionConnectionRegistry
from engine.mini_games.plugins import default_registry
from engine.mini_games.resolver import resolve_mini_game_package_snapshot
from engine.mini_games.runtime import MiniGameRuntime
from engine.tests.rounds_support import (
    at,
    fixture_arc_registered,
    phased_arc,
    seat_session,
)


@pytest.mark.asyncio
async def test_battle_of_wits_routes_keep_answers_and_catch_up_private(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine, sessions = await make_sqlite_session_factory()
    package = Path(__file__).resolve().parents[2] / "nightcap/mini_games/battle-of-wits"
    arc = phased_arc(case_path=None)
    bus = SessionEventBus()
    now = at(100)
    make_runtime = partial(MiniGameRuntime, clock=lambda: now)

    async def request_session() -> AsyncIterator[AsyncSession]:
        async with sessions() as db, db.begin():
            yield db

    monkeypatch.setitem(app.dependency_overrides, get_async_session, request_session)
    monkeypatch.setattr(mini_games, "MiniGameRuntime", make_runtime)
    try:
        async with sessions() as db, db.begin():
            with fixture_arc_registered(arc):
                seated = await seat_session(db, arc, players=2, start=False)
            host = await db.scalar(
                select(SessionParticipant.participant_id).where(
                    SessionParticipant.session_id == seated.session_id,
                    SessionParticipant.surface_type == "host",
                )
            )
            assert host is not None
            snapshot = await resolve_mini_game_package_snapshot(
                db,
                session_id=seated.session_id,
                package_path=package,
                quality_tier="low",
            )
            runtime = make_runtime(db, bus, default_registry())
            run = await runtime.create_run(seated.session_id, snapshot)
            await runtime.start_run(run.run_id)
            assert run.deadline is not None
            deadline = run.deadline

        monkeypatch.setitem(events._buses, seated.session_id, bus)
        monkeypatch.setitem(
            events._registries, seated.session_id, SessionConnectionRegistry()
        )
        callers = {
            name: {
                "uid": name,
                "arcwright_session_id": str(seated.session_id),
                "arcwright_player_id": str(participant),
                "arcwright_role": "host" if name == "host" else "player",
            }
            for name, participant in zip(
                ("host", "leader", "catch-up"), (host, *seated.participants)
            )
        }
        monkeypatch.setattr(auth, "_decode_bearer", callers.__getitem__)
        leader, catch_up = map(str, seated.characters)
        questions = snapshot.resolved_content["questions"]
        base = f"/v1/sessions/{seated.session_id}/mini-games"

        async def advance() -> None:
            nonlocal now, deadline
            now = deadline + timedelta(seconds=1)
            async with sessions() as db, db.begin():
                runtime = make_runtime(db, bus, default_registry())
                updated = await runtime.check_timeout(run.run_id)
                assert updated is not None and updated.deadline is not None
                deadline = updated.deadline

        def receipt(submission_id: str) -> dict[str, Any]:
            return {
                "submission_id": submission_id,
                "is_accepted": True,
                "rejection_reason": None,
            }

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:

            async def submit(
                viewer: str, submission_id: str, payload: dict[str, Any]
            ) -> None:
                response = await client.post(
                    f"{base}/{run.run_id}/submissions",
                    headers={"Authorization": f"Bearer {viewer}"},
                    json={"submission_id": submission_id, "payload": payload},
                )
                assert response.status_code == 200, response.text
                assert response.json() == receipt(submission_id)

            await submit(
                "leader",
                "choice-one",
                {
                    "action": "choice",
                    "question_index": 0,
                    "option_id": questions[0]["answer"][0],
                },
            )
            await advance()
            await advance()
            question = questions[1]
            first, second, third, fourth = question["answer"]
            await submit(
                "catch-up",
                "sort-two",
                {
                    "action": "sort",
                    "question_index": 1,
                    "order": [first, third, second, fourth],
                },
            )

            question_view = {
                "phase": "question",
                "index": 1,
                "total": len(questions),
                "kind": "sort",
                "prompt": question["prompt"],
                "options": question["options"],
            }
            reveal_view = {
                **question_view,
                "phase": "reveal",
                "answer": question["answer"],
                "correct": [],
                "scores": {leader: 4, catch_up: 2},
                "standing": [[leader], [catch_up]],
            }
            private = {
                "leader": {leader: {"locked": False}},
                "catch-up": {
                    catch_up: {"locked": True, "pinned": {"id": first, "position": 0}}
                },
            }
            receipts = {
                "tv": [],
                "host": [receipt("choice-one"), receipt("sort-two")],
                "leader": [receipt("choice-one")],
                "catch-up": [receipt("sort-two")],
            }
            for stage in (question_view, reveal_view):
                if stage is reveal_view:
                    await advance()
                for viewer, submissions in receipts.items():
                    display = viewer == "tv"
                    response = await client.get(
                        f"{base}/active/display" if display else f"{base}/active",
                        headers={}
                        if display
                        else {"Authorization": f"Bearer {viewer}"},
                    )
                    assert response.status_code == 200, (viewer, response.text)
                    body = response.json()
                    body["my_submissions"].sort(key=lambda item: item["submission_id"])
                    state = {"stage": stage}
                    if stage is question_view and viewer in private:
                        state["player"] = private[viewer]
                    assert body == {
                        "run_id": str(run.run_id),
                        "game_id": "battle-of-wits",
                        "mechanic_type": "battle-of-wits",
                        "definition_version": "0.1.0",
                        "status": "active",
                        "deadline_at": deadline.isoformat().replace("+00:00", "Z"),
                        "phase_state": None,
                        "runtime_state": state,
                        "presentation": {},
                        "my_submissions": submissions,
                    }, viewer
    finally:
        await engine.dispose()
