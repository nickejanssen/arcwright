"""Serve the standalone Battle of Wits playtest on a local Wi-Fi network."""

from __future__ import annotations

import argparse
import asyncio
import os
import shutil
import socket
import subprocess
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager, suppress
from datetime import datetime, timezone
from pathlib import Path
from secrets import token_urlsafe
from tempfile import TemporaryDirectory
from typing import Any
from unicodedata import category
from uuid import UUID, uuid4

# The launcher uses an authored package and can run without internet access.
if __name__ == "__main__":
    os.environ.setdefault("LITELLM_LOCAL_MODEL_COST_MAP", "True")

import uvicorn
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from engine.db.orm import Account, Character, MiniGameRun, Session, SessionParticipant
from engine.db.testing import make_sqlite_session_factory
from engine.events.bus import SessionEventBus
from engine.mini_games.audience_view import Audience, Viewer, build_run_view
from engine.mini_games.loader import load_mini_game_package
from engine.mini_games.models import ContentMode
from engine.mini_games.plugins import default_registry
from engine.mini_games.resolver import (
    RunBinding,
    resolve_loaded_mini_game_snapshot,
)
from engine.mini_games.runtime import MiniGameRuntime, RunStateError

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "nightcap/mini_games/battle-of-wits"
GAME_ID = "battle-of-wits"
VERSION = "0.1.0"
MAX_PLAYERS = 8
MAX_ANSWER_BYTES = 4096
FINAL = {"completed", "timed_out"}


class Join(BaseModel):
    name: str = Field(max_length=40)


class Start(BaseModel):
    previous_run: UUID | None = None


class Answer(BaseModel):
    run_id: UUID
    submission_id: str = Field(min_length=1, max_length=100)
    payload: dict[str, Any]


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def create_app(
    assets: Path,
    *,
    package: Path = PACKAGE,
    clock: Callable[[], datetime] = _utc_now,
) -> FastAPI:
    # The standalone lab uses the existing test database adapter. Its rows and
    # mini-game events live only for this process.
    registry = default_registry()
    room_id = uuid4()
    lock = asyncio.Lock()
    active_run: UUID | None = None
    public_definition: dict[str, Any] | None = None

    def runtime(db: AsyncSession) -> MiniGameRuntime:
        return MiniGameRuntime(db, SessionEventBus(), registry, clock=clock)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        engine, factory = await make_sqlite_session_factory()
        app.state.factory = factory
        async with factory.begin() as db:
            account_id = uuid4()
            db.add(Account(account_id=account_id, firebase_uid=str(account_id)))
            await db.flush()
            db.add(
                Session(
                    session_id=room_id,
                    arc_id="standalone",
                    current_beat_id="standalone",
                    status="active",
                    host_account_id=account_id,
                    quality_tier="low",
                    player_count=0,
                )
            )

        async def tick() -> None:
            while True:
                await asyncio.sleep(0.25)
                async with lock, factory.begin() as db:
                    await advance(db)

        ticker = asyncio.create_task(tick())
        try:
            yield
        finally:
            ticker.cancel()
            with suppress(asyncio.CancelledError):
                await ticker
            await engine.dispose()

    app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)

    @app.middleware("http")
    async def protect_seat_state(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        response = await call_next(request)
        if request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "private, no-store"
        return response

    async def advance(db: AsyncSession) -> MiniGameRun | None:
        if active_run is None:
            return None
        run = await db.get(MiniGameRun, active_run)
        if run is not None and run.status == "active":
            await runtime(db).check_timeout(run.run_id)
        return run

    async def roster(db: AsyncSession) -> list[SessionParticipant]:
        rows = await db.scalars(
            select(SessionParticipant).where(SessionParticipant.session_id == room_id)
        )
        return list(rows)

    async def seat(db: AsyncSession, authorization: str | None) -> SessionParticipant:
        scheme, _, token = (authorization or "").partition(" ")
        if scheme.lower() == "bearer" and token:
            player = await db.scalar(
                select(SessionParticipant).where(
                    SessionParticipant.session_id == room_id,
                    SessionParticipant.join_token == token,
                )
            )
            if player is not None:
                return player
        raise HTTPException(401, "Join this room to play.")

    async def room(
        db: AsyncSession,
        player: SessionParticipant,
        run: MiniGameRun | None,
        definition: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        players = await roster(db)
        names = {
            str(key): p.display_name
            for p in players
            for key in (p.character_id, p.participant_id)
        }
        state: dict[str, Any] | None = None
        if run is not None:
            view = build_run_view(
                registry, run, Viewer(Audience.player, str(player.character_id))
            )
            deadline = (
                run.deadline.replace(tzinfo=timezone.utc) if run.deadline else None
            )
            state = {
                "runId": str(run.run_id),
                "gameId": GAME_ID,
                "definitionVersion": VERSION,
                "status": run.status,
                "deadlineAt": deadline.isoformat() if deadline else None,
                "runtimeState": view.runtime_state,
                "playerNames": names,
                "mySubmissions": [],
            }
            if run.status in FINAL:
                state["resultHold"] = {
                    "phaseEntry": 0,
                    "standing": (run.outcome or {}).get("standing", []),
                }
        return {
            "players": [p.display_name for p in players],
            "game": state,
            "definition": definition if definition is not None else public_definition,
        }

    @app.get("/")
    async def index() -> FileResponse:
        return FileResponse(
            assets / "index.html", headers={"Cache-Control": "no-store"}
        )

    # This directory contains just the standalone build, never the package tree.
    app.mount("/assets", StaticFiles(directory=assets / "assets", check_dir=False))

    @app.post("/api/join", status_code=201)
    async def join(request: Join) -> dict[str, str]:
        if any(category(char) == "Cc" for char in request.name):
            raise HTTPException(422, "Names cannot contain control characters.")
        name = request.name.strip()
        if not name:
            raise HTTPException(422, "Enter a name to join.")
        async with lock, app.state.factory.begin() as db:
            if active_run is not None:
                raise HTTPException(409, "This room has already started.")
            players = await roster(db)
            if len(players) == MAX_PLAYERS:
                raise HTTPException(409, "The room is full.")
            if any(
                (p.display_name or "").casefold() == name.casefold() for p in players
            ):
                raise HTTPException(409, "That name is taken in this room.")
            character_id = uuid4()
            participant_id = uuid4()
            token = token_urlsafe(32)
            db.add(Character(character_id=character_id))
            await db.flush()
            db.add(
                SessionParticipant(
                    session_id=room_id,
                    participant_id=participant_id,
                    character_id=character_id,
                    join_token=token,
                    surface_type="phone",
                    is_ai_controlled=False,
                    display_name=name,
                )
            )
            return {
                "token": token,
                "character_id": str(character_id),
                "participant_id": str(participant_id),
            }

    @app.get("/api/room")
    async def read_room(
        authorization: str | None = Header(default=None),
    ) -> dict[str, Any]:
        async with lock, app.state.factory.begin() as db:
            player = await seat(db, authorization)
            return await room(db, player, await advance(db))

    @app.post("/api/start")
    async def start(
        request: Start, authorization: str | None = Header(default=None)
    ) -> dict[str, Any]:
        nonlocal active_run, public_definition
        async with lock:
            async with app.state.factory.begin() as db:
                player = await seat(db, authorization)
                run = await advance(db)
                if run is not None and (
                    run.status not in FINAL or request.previous_run != run.run_id
                ):
                    return await room(db, player, run)
                try:
                    loaded = load_mini_game_package(package)
                    definition = loaded.definition
                    if (
                        definition.game_id,
                        definition.version,
                        definition.content_mode,
                    ) != (GAME_ID, VERSION, ContentMode.authored):
                        raise ValueError(
                            "expected the authored Battle of Wits 0.1.0 package"
                        )
                    snapshot = await resolve_loaded_mini_game_snapshot(
                        db, session_id=room_id, loaded_game=loaded, quality_tier="low"
                    )
                    snapshot = snapshot.model_copy(
                        update={
                            "binding": RunBinding(
                                beat_id="standalone",
                                binding_id=GAME_ID,
                                phase_entry=0,
                                release_content=False,
                            )
                        }
                    )
                    game = runtime(db)
                    run = await game.create_run(room_id, snapshot)
                    run = await game.start_run(run.run_id)
                except ValueError:
                    raise HTTPException(
                        503,
                        "The server could not load the Battle of Wits question bank.",
                    ) from None
                safe_definition = definition.model_dump(
                    mode="json", exclude={"authored_content", "generation_constraints"}
                )
                safe_definition.update(
                    authored_content=None, generation_constraints=None
                )
                reply = await room(db, player, run, safe_definition)
            active_run = run.run_id
            public_definition = safe_definition
            return reply

    @app.post("/api/answer")
    async def answer(
        request: Request, authorization: str | None = Header(default=None)
    ) -> dict[str, Any]:
        body = bytearray()
        async for chunk in request.stream():
            if len(body) + len(chunk) > MAX_ANSWER_BYTES:
                raise HTTPException(413, "The answer is too large.")
            body.extend(chunk)
        try:
            submitted = Answer.model_validate_json(body)
        except ValidationError:
            raise HTTPException(422, "Enter a valid answer.") from None
        async with lock, app.state.factory.begin() as db:
            player = await seat(db, authorization)
            if submitted.run_id != active_run:
                raise HTTPException(409, "That round has ended.")
            try:
                response = await runtime(db).submit_action(
                    submitted.run_id,
                    submitted.submission_id,
                    player.character_id,
                    submitted.payload,
                    participant_id=player.participant_id,
                )
            except (RunStateError, ValueError):
                raise HTTPException(409, "This answer is unavailable.") from None
            return {
                "submissionId": response.submission_id,
                "isAccepted": response.is_accepted,
            }

    return app


def _lan_ip() -> str:
    # Connecting a UDP socket selects the local interface without sending data.
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
        try:
            probe.connect(("192.0.2.1", 1))
            return str(probe.getsockname()[0])
        except OSError:
            return socket.gethostbyname(socket.gethostname())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    node = shutil.which("node")
    vite = ROOT / "dashboard/node_modules/vite/bin/vite.js"
    if node is None or not vite.is_file():
        parser.exit(1, "Install Node and run npm ci --prefix dashboard first.\n")
    with TemporaryDirectory(prefix="battle-of-wits-") as build:
        subprocess.run(
            [
                node,
                str(vite),
                "build",
                "--config",
                "dashboard/standalone/vite.config.ts",
                "--outDir",
                build,
            ],
            cwd=ROOT,
            check=True,
        )
        address = _lan_ip()
        print(f"On this PC: http://localhost:{args.port}", flush=True)
        print(f"On the same Wi-Fi: http://{address}:{args.port}", flush=True)
        uvicorn.run(create_app(Path(build)), host="0.0.0.0", port=args.port)


if __name__ == "__main__":
    main()
