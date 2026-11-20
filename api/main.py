"""Arcwright REST API — FastAPI application entry point.

Architecture: docs/architecture/09-developer-api.md §9.2.
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.routers import (
    characters,
    costs,
    events,
    knowledge,
    lobby,
    mini_games,
    room,
    rounds,
    sessions,
)
from api.tick_loop import run_tick_loop


@asynccontextmanager
async def _lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Run the once-a-second round clock for as long as the API is up."""
    task = asyncio.create_task(run_tick_loop(), name="round-tick-loop")
    try:
        yield
    finally:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


def create_app() -> FastAPI:
    application = FastAPI(title="Arcwright API", version="0.1.0", lifespan=_lifespan)

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @application.get("/health")
    async def health() -> JSONResponse:
        return JSONResponse({"status": "ok"})

    application.include_router(sessions.router, prefix="/v1")
    application.include_router(events.router, prefix="/v1")
    application.include_router(characters.router, prefix="/v1")
    application.include_router(knowledge.router, prefix="/v1")
    application.include_router(costs.router, prefix="/v1")
    application.include_router(mini_games.router, prefix="/v1")
    application.include_router(lobby.router, prefix="/v1")
    application.include_router(rounds.router, prefix="/v1")
    application.include_router(room.router, prefix="/v1")
    return application


app = create_app()
