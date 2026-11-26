"""Exercise the standalone HTTP room with the real package and a fixed clock."""

import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from shutil import copytree
from time import monotonic

import httpx
import pytest

from scripts.play_battle_of_wits import PACKAGE, create_app


@dataclass
class Clock:
    now: datetime = datetime(2026, 11, 26, tzinfo=timezone.utc)

    def __call__(self):
        return self.now


def headers(seat):
    return {"Authorization": f"Bearer {seat['token']}"}


async def join(client, name):
    response = await client.post("/api/join", json={"name": name})
    assert response.status_code == 201
    return response.json()


async def status(client, seat):
    response = await client.get("/api/room", headers=headers(seat))
    assert response.status_code == 200
    assert response.headers["cache-control"] == "private, no-store"
    return response.json()


async def start(client, seat, previous_run=None):
    response = await client.post(
        "/api/start", json={"previous_run": previous_run}, headers=headers(seat)
    )
    assert response.status_code == 200
    return response.json()["game"]


def answer(game, submission_id, option_id):
    return {
        "run_id": game["runId"],
        "submission_id": submission_id,
        "payload": {"action": "choice", "question_index": 0, "option_id": option_id},
    }


@pytest.mark.asyncio
async def test_two_seats_reconnect_score_and_replay(tmp_path):
    fixture = tmp_path / "package"
    copytree(PACKAGE, fixture)
    definition_path = fixture / "definitions/0.1.0.json"
    package_definition = json.loads(definition_path.read_text(encoding="utf-8"))
    package_definition["authored_content"]["server_content_path"] = "server/test.json"
    definition_path.write_text(json.dumps(package_definition), encoding="utf-8")
    bank = fixture / "server/test.json"
    options = [{"id": x, "label": x} for x in "ABCD"]
    original = {
        "questions": [
            {"kind": "choice", "prompt": "Pick A", "options": options, "answer": ["A"]},
            {
                "kind": "sort",
                "prompt": "Sort A to D",
                "options": options,
                "answer": list("ABCD"),
            },
        ]
    }
    bank.write_text(json.dumps(original), encoding="utf-8")
    assets = tmp_path / "site"
    (assets / "assets").mkdir(parents=True)
    (assets / "index.html").write_text("<h1>Battle of Wits</h1>", encoding="utf-8")
    clock = Clock()
    app = create_app(assets, package=fixture, clock=clock)
    transport = httpx.ASGITransport(app=app)
    async with app.router.lifespan_context(app):
        async with (
            httpx.AsyncClient(transport=transport, base_url="http://test") as one,
            httpx.AsyncClient(transport=transport, base_url="http://test") as two,
        ):
            assert (await one.get("/")).status_code == 200
            assert (await one.get("/api/room")).status_code == 401
            assert (await one.get("/@fs/" + bank.as_posix())).status_code == 404
            assert (await one.get("/server/" + bank.name)).status_code == 404
            first = await join(one, "River")
            second = await join(two, "Kit")
            game = await start(one, first)
            assert "answer" not in game["runtimeState"]["stage"]
            assert "questions" not in game and "resolved_content" not in game
            stage = game["runtimeState"]["stage"]
            definition = (await status(one, first))["definition"]
            assert definition["authored_content"] is None
            assert definition["generation_constraints"] is None
            assert stage["prompt"] == "Pick A"
            correct, wrong = "A", "B"
            first_answer = answer(game, "first-answer", correct)
            received = await one.post(
                "/api/answer", headers=headers(first), json=first_answer
            )
            assert received.json()["isAccepted"] is True
            duplicate = await one.post(
                "/api/answer",
                headers=headers(first),
                json=answer(game, "first-answer", wrong),
            )
            assert duplicate.json() == received.json()
            stolen_id = await two.post(
                "/api/answer", headers=headers(second), json=first_answer
            )
            assert stolen_id.status_code == 409
            received = await two.post(
                "/api/answer",
                headers=headers(second),
                json=answer(game, "second-answer", wrong),
            )
            assert received.json()["isAccepted"] is True
            first_view = (await status(one, first))["game"]["runtimeState"]["player"]
            second_view = (await status(two, second))["game"]["runtimeState"]["player"]
            assert set(first_view) == {first["character_id"]}
            assert set(second_view) == {second["character_id"]}
            async with httpx.AsyncClient(
                transport=transport, base_url="http://test"
            ) as refreshed:
                assert (await status(refreshed, first))["game"]["runtimeState"][
                    "player"
                ] == first_view
            clock.now += timedelta(seconds=13)
            assert (
                await one.post(
                    "/api/answer",
                    headers=headers(first),
                    json=answer(game, "late", correct),
                )
            ).status_code == 409
            assert (await status(one, first))["game"]["runtimeState"]["stage"][
                "phase"
            ] == "reveal"
            clock.now += timedelta(seconds=6)
            leading = (await status(one, first))["game"]["runtimeState"]
            trailing = (await status(two, second))["game"]["runtimeState"]
            assert leading["stage"] == trailing["stage"]
            assert leading["player"] == {first["character_id"]: {"locked": False}}
            assert set(trailing["player"]) == {second["character_id"]}
            assert "pinned" in trailing["player"][second["character_id"]]
            for _ in range(8):
                current = await status(one, first)
                if current["game"].get("resultHold"):
                    break
                clock.now += timedelta(seconds=22)
            assert current["game"]["resultHold"]["standing"] == [
                [first["participant_id"]],
                [second["participant_id"]],
            ]
            assert (await status(two, second))["game"]["resultHold"] == current["game"][
                "resultHold"
            ]

            for question in original["questions"]:
                question["prompt"] = "New standalone bank " + question["prompt"]
            next_bank = fixture / "server/updated.json"
            next_bank.write_text(json.dumps(original), encoding="utf-8")
            package_definition["authored_content"]["server_content_path"] = (
                "server/updated.json"
            )
            package_definition["rules"]["choice_seconds"] = 11
            edited_at = monotonic()
            definition_path.write_text(json.dumps(package_definition), encoding="utf-8")
            replay = await start(two, second, game["runId"])
            print(f"Package rule edit to next round: {monotonic() - edited_at:.2f}s")
            assert replay["runId"] != game["runId"]
            assert datetime.fromisoformat(
                replay["deadlineAt"]
            ) - clock.now == timedelta(seconds=11)
            assert replay["runtimeState"]["stage"]["prompt"].startswith(
                "New standalone bank"
            )
            assert (
                await start(one, first, game["runId"])
                == (await status(one, first))["game"]
            )
            assert (
                await one.post("/api/answer", headers=headers(first), json=first_answer)
            ).status_code == 409


@pytest.mark.asyncio
@pytest.mark.parametrize("count", [1, 8])
async def test_supported_room_sizes(count, tmp_path):
    app = create_app(tmp_path, clock=Clock())
    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            seats = [
                await join(client, f"Player {index + 1}") for index in range(count)
            ]
            if count == 8:
                assert (
                    await client.post("/api/join", json={"name": "Overflow"})
                ).status_code == 409
            assert (await start(client, seats[0]))["status"] == "active"


@pytest.mark.asyncio
async def test_answer_body_is_bounded_and_names_reject_controls(tmp_path):
    app = create_app(tmp_path, clock=Clock())
    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            for name in ("Ada\n", "A\x00da", "A\x85da"):
                response = await client.post("/api/join", json={"name": name})
                assert response.status_code == 422
            player = await join(client, "Ada")
            game = await start(client, player)
            oversized = answer(game, "large", "x" * 8192)
            response = await client.post(
                "/api/answer", headers=headers(player), json=oversized
            )
            assert response.status_code == 413

            async def chunks():
                body = json.dumps(oversized).encode()
                for offset in range(0, len(body), 1024):
                    yield body[offset : offset + 1024]

            response = await client.post(
                "/api/answer",
                headers={**headers(player), "Content-Type": "application/json"},
                content=chunks(),
            )
            assert response.status_code == 413
            response = await client.post(
                "/api/answer",
                headers={**headers(player), "Content-Type": "application/json"},
                content=b"{",
            )
            assert response.status_code == 422


@pytest.mark.asyncio
async def test_asset_mount_cannot_return_bank_via_parent_paths(tmp_path):
    assets = tmp_path / "assets"
    assets.mkdir()
    (assets / "public.js").write_text("console.log('public')", encoding="utf-8")
    server = tmp_path / "server"
    server.mkdir()
    bank = server / "bank.json"
    private = '{"questions": ["private bank marker"]}'
    bank.write_text(private, encoding="utf-8")
    app = create_app(tmp_path, clock=Clock())
    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            assert (await client.get("/assets/public.js")).status_code == 200
            # HTTPX normalizes literal parent segments. Encoded requests also
            # exercise the decoded parent path inside the asset mount.
            for path in (
                "/assets/../server/bank.json",
                "/assets/%2e%2e/server/bank.json",
                "/assets/..%2fserver%2fbank.json",
                "/assets/%2e%2e%5cserver%5cbank.json",
            ):
                response = await client.get(path)
                assert response.status_code == 404
                assert private not in response.text
