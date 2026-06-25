"""Arcwright REST API — FastAPI application entry point.

Architecture: docs/architecture/09-developer-api.md §9.2.
"""

from __future__ import annotations

from fastapi import FastAPI

from api.routers import characters, costs, events, knowledge, mini_games, sessions


def create_app() -> FastAPI:
    application = FastAPI(title="Arcwright API", version="0.1.0")
    application.include_router(sessions.router, prefix="/v1")
    application.include_router(events.router, prefix="/v1")
    application.include_router(characters.router, prefix="/v1")
    application.include_router(knowledge.router, prefix="/v1")
    application.include_router(costs.router, prefix="/v1")
    application.include_router(mini_games.router, prefix="/v1")
    return application


app = create_app()
