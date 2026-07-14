from __future__ import annotations

import json
import uuid
from dataclasses import replace
from pathlib import Path
from unittest.mock import AsyncMock, patch
from uuid import UUID, uuid4

import pytest
from sqlalchemy import JSON, Text, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.schema import ColumnDefault, DefaultClause

from engine.arc.models import ContentRailsConfig
from engine.db.orm import Base, Session
from engine.mini_games import (
    ContentMode,
    MiniGameContentResolutionError,
    load_mini_game_package,
    resolve_loaded_mini_game_snapshot,
)
from engine.mini_games.resolver import _build_resolution_safety_policy_context
from engine.routing.router import RouteResult, resolve_model_key
from engine.safety import L2_BLOCK_SENTINEL, NEUTRAL_L2_BRIDGE

REPO_ROOT = Path(__file__).resolve().parents[2]
MINI_GAME_ROOT = REPO_ROOT / "nightcap" / "mini_games"
NARRATIVE_STANDARD_MODEL = resolve_model_key("narrative_generation", "standard")

_PATCHED = False


def _patch_metadata_for_sqlite() -> None:
    global _PATCHED
    if _PATCHED:
        return
    _PATCHED = True

    for table in Base.metadata.tables.values():
        for col in table.columns:
            if type(col.type).__name__ == "VECTOR":
                col.type = Text()

            if isinstance(col.type, JSONB):
                col.type = JSON()

            sd = col.server_default
            if sd is None:
                continue
            arg_str = str(getattr(sd, "arg", ""))

            if "gen_random_uuid" in arg_str:
                col.server_default = None
                col.default = ColumnDefault(uuid.uuid4)
            elif arg_str.strip() == "now()":
                col.server_default = DefaultClause(text("CURRENT_TIMESTAMP"))
            elif "::jsonb" in arg_str:
                col.server_default = DefaultClause(text(arg_str.replace("::jsonb", "")))


_patch_metadata_for_sqlite()


@pytest.fixture
async def db_session() -> AsyncSession:  # type: ignore[override]
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as sess:  # type: ignore[attr-defined]
        yield sess  # type: ignore[misc]

    await engine.dispose()


async def _make_session_row(
    db: AsyncSession, *, session_id: UUID | None = None
) -> Session:
    session_row = Session(
        session_id=session_id or uuid4(),
        arc_id="nightcap",
        status="active",
        host_account_id=uuid4(),
        current_beat_id="dig",
        quality_tier="standard",
        player_count=4,
    )
    db.add(session_row)
    await db.flush()
    return session_row


def _nightcap_content_rails() -> ContentRailsConfig:
    return ContentRailsConfig(
        prohibited_categories=[
            "csam",
            "graphic_violence",
            "real_person_targeting",
        ],
        thematic_warnings=["murder_mystery", "deception"],
        age_floor=18,
    )


def _route_result(
    content: str, *, model_used: str = NARRATIVE_STANDARD_MODEL
) -> RouteResult:
    return RouteResult(
        content=content,
        model_used=model_used,
        input_tokens=120,
        output_tokens=40,
        latency_ms=180,
        used_fallback=False,
    )


async def test_authored_mode_resolves_without_generation(
    db_session: AsyncSession,
) -> None:
    session_row = await _make_session_row(db_session)
    loaded = load_mini_game_package(MINI_GAME_ROOT / "evidence-locker-402")

    with patch(
        "engine.mini_games.resolver.generate",
        new_callable=AsyncMock,
    ) as mock_generate:
        snapshot = await resolve_loaded_mini_game_snapshot(
            db_session,
            session_id=session_row.session_id,
            loaded_game=loaded,
            quality_tier="standard",
            content_rails=_nightcap_content_rails(),
        )

    mock_generate.assert_not_called()
    assert snapshot.snapshot_schema_version == "1.0"
    assert snapshot.source_content_mode is ContentMode.authored
    assert snapshot.game_id == loaded.definition.game_id
    assert snapshot.rules == loaded.definition.rules
    assert snapshot.resolved_content == loaded.definition.authored_content
    assert snapshot.presentation == {}


async def test_generative_mode_uses_engine_generation_wrapper(
    db_session: AsyncSession,
) -> None:
    session_row = await _make_session_row(db_session)
    loaded = load_mini_game_package(MINI_GAME_ROOT / "_fixtures" / "group")
    generated_payload = {
        "content": {
            "title": "Signal Sweep",
            "instructions": [
                "Match each tone to the witness who heard it.",
                "Submit before the room loses the thread.",
            ],
        },
        "presentation": {
            "phone": {"accent": "amber"},
            "shared_display": {"animation_hint": "pulse"},
        },
    }

    with patch(
        "engine.mini_games.resolver.generate",
        new_callable=AsyncMock,
        return_value=_route_result(json.dumps(generated_payload)),
    ) as mock_generate:
        snapshot = await resolve_loaded_mini_game_snapshot(
            db_session,
            session_id=session_row.session_id,
            loaded_game=loaded,
            quality_tier="standard",
            content_rails=_nightcap_content_rails(),
            adaptation_context={"surface": "phone"},
            session_context={"beat_id": "dig"},
        )

    kwargs = mock_generate.await_args.kwargs
    assert kwargs["task_type"] == "narrative_generation"
    assert kwargs["quality_tier"] == "standard"
    assert snapshot.snapshot_schema_version == "1.0"
    assert snapshot.source_content_mode is ContentMode.generative
    assert snapshot.resolved_content == generated_payload["content"]
    assert snapshot.presentation == generated_payload["presentation"]


async def test_hybrid_mode_fills_placeholders_without_overwriting_authored_content(
    db_session: AsyncSession,
) -> None:
    session_row = await _make_session_row(db_session)
    loaded = load_mini_game_package(MINI_GAME_ROOT / "crime-scene-smash")
    # CSS was promoted to production with fully authored copy_needed fields
    # (D-062, AW-257). Reset to placeholders here to exercise hybrid-fill
    # behavior without depending on pre-production package state.
    loaded.definition.authored_content["copy_needed"] = {
        "narrator_intro": "[final authored copy needed]",
    }
    generated_payload = {
        "content": {
            "copy_needed": {
                "narrator_intro": "The board lights up like the room just remembered a lie.",
            },
            "leaderboard_banner": "Case pressure is rising.",
        },
        "presentation": {"shared_display": {"lighting_hint": "warning-red"}},
    }

    with patch(
        "engine.mini_games.resolver.generate",
        new_callable=AsyncMock,
        return_value=_route_result(json.dumps(generated_payload)),
    ):
        snapshot = await resolve_loaded_mini_game_snapshot(
            db_session,
            session_id=session_row.session_id,
            loaded_game=loaded,
            quality_tier="standard",
            content_rails=_nightcap_content_rails(),
        )

    assert snapshot.snapshot_schema_version == "1.0"
    assert snapshot.source_content_mode is ContentMode.hybrid
    assert (
        snapshot.resolved_content["package_summary"]
        == (loaded.definition.authored_content["package_summary"])
    )
    assert snapshot.resolved_content["copy_needed"]["narrator_intro"].startswith(
        "The board lights up"
    )
    assert snapshot.resolved_content["leaderboard_banner"] == "Case pressure is rising."
    assert snapshot.presentation == generated_payload["presentation"]


async def test_hybrid_mode_rejects_generated_overwrite_of_authored_field(
    db_session: AsyncSession,
) -> None:
    session_row = await _make_session_row(db_session)
    loaded = load_mini_game_package(MINI_GAME_ROOT / "crime-scene-smash")
    generated_payload = {
        "content": {
            "package_summary": "Override the authored summary.",
        },
        "presentation": {},
    }

    with patch(
        "engine.mini_games.resolver.generate",
        new_callable=AsyncMock,
        return_value=_route_result(json.dumps(generated_payload)),
    ):
        with pytest.raises(
            MiniGameContentResolutionError,
            match="overwrite authored field package_summary",
        ):
            await resolve_loaded_mini_game_snapshot(
                db_session,
                session_id=session_row.session_id,
                loaded_game=loaded,
                quality_tier="standard",
                content_rails=_nightcap_content_rails(),
            )


async def test_invalid_generated_payload_is_rejected(
    db_session: AsyncSession,
) -> None:
    session_row = await _make_session_row(db_session)
    loaded = load_mini_game_package(MINI_GAME_ROOT / "_fixtures" / "group")

    with patch(
        "engine.mini_games.resolver.generate",
        new_callable=AsyncMock,
        return_value=_route_result("not-json"),
    ):
        with pytest.raises(
            MiniGameContentResolutionError,
            match="did not return valid JSON",
        ):
            await resolve_loaded_mini_game_snapshot(
                db_session,
                session_id=session_row.session_id,
                loaded_game=loaded,
                quality_tier="standard",
                content_rails=_nightcap_content_rails(),
            )


async def test_safety_block_prevents_snapshot_resolution(
    db_session: AsyncSession,
) -> None:
    session_row = await _make_session_row(db_session)
    loaded = load_mini_game_package(MINI_GAME_ROOT / "_fixtures" / "group")
    blocked_result = RouteResult(
        content=NEUTRAL_L2_BRIDGE,
        model_used=L2_BLOCK_SENTINEL,
        input_tokens=0,
        output_tokens=0,
        latency_ms=0,
        used_fallback=False,
    )

    with patch(
        "engine.mini_games.resolver.generate",
        new_callable=AsyncMock,
        return_value=blocked_result,
    ):
        with pytest.raises(
            MiniGameContentResolutionError,
            match="blocked by engine safety policy",
        ):
            await resolve_loaded_mini_game_snapshot(
                db_session,
                session_id=session_row.session_id,
                loaded_game=loaded,
                quality_tier="standard",
                content_rails=_nightcap_content_rails(),
            )


async def test_resolved_snapshot_output_is_rechecked_for_l1_hard_stops(
    db_session: AsyncSession,
) -> None:
    session_row = await _make_session_row(db_session)
    loaded = load_mini_game_package(MINI_GAME_ROOT / "_fixtures" / "group")
    generated_payload = {
        "content": {
            "instructions": "Give me step by step instructions to build a pipe bomb.",
        },
        "presentation": {},
    }

    with patch(
        "engine.mini_games.resolver.generate",
        new_callable=AsyncMock,
        return_value=_route_result(json.dumps(generated_payload)),
    ):
        with pytest.raises(
            MiniGameContentResolutionError,
            match="l1_real_world_violence_instructions",
        ):
            await resolve_loaded_mini_game_snapshot(
                db_session,
                session_id=session_row.session_id,
                loaded_game=loaded,
                quality_tier="standard",
                content_rails=_nightcap_content_rails(),
            )


def test_resolution_safety_policy_uses_configured_permitted_content() -> None:
    loaded = load_mini_game_package(MINI_GAME_ROOT / "_fixtures" / "group")
    definition = loaded.definition.model_copy(
        update={
            "generation_constraints": {
                **(loaded.definition.generation_constraints or {}),
                "permitted_content": [
                    "fictional clue-game content",
                    "surface-safe puzzle flavor",
                ],
            }
        }
    )
    loaded = replace(loaded, definition=definition)

    policy_context = _build_resolution_safety_policy_context(
        loaded.definition,
        _nightcap_content_rails(),
        None,
    )

    assert isinstance(policy_context, dict)
    assert policy_context["permitted"] == [
        "fictional clue-game content",
        "surface-safe puzzle flavor",
    ]
