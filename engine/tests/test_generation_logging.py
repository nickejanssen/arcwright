"""Tests for engine/routing/logging.py."""

from __future__ import annotations

import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, patch
from uuid import UUID, uuid4

import pytest
from sqlalchemy import JSON, Text, select, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.schema import ColumnDefault, DefaultClause

from engine.db.orm import Base, Event, GenerationLog, Session
from engine.routing import generate, log_generation, mark_stable_context_cacheable
from engine.routing.router import (
    RouteResult,
    resolve_fallback_model_key,
    resolve_model_key,
)

CHARACTER_STANDARD_MODEL = resolve_model_key("character_dialogue", "standard")
CHARACTER_PREMIUM_MODEL = resolve_model_key("character_dialogue", "premium")
SAFETY_STANDARD_FALLBACK_MODEL = resolve_fallback_model_key(
    "safety_classification", "standard"
)
NARRATIVE_STANDARD_FALLBACK_MODEL = resolve_fallback_model_key(
    "narrative_generation", "standard"
)

assert SAFETY_STANDARD_FALLBACK_MODEL is not None
assert NARRATIVE_STANDARD_FALLBACK_MODEL is not None

# ---------------------------------------------------------------------------
# SQLite metadata patch — same pattern as test_knowledge_graph.py
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Async session fixture
# ---------------------------------------------------------------------------


@pytest.fixture
async def session() -> AsyncSession:  # type: ignore[override]
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as sess:  # type: ignore[attr-defined]
        yield sess  # type: ignore[misc]

    await engine.dispose()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _make_session_row(
    db: AsyncSession, *, session_id: UUID | None = None
) -> Session:
    s = Session(
        session_id=session_id or uuid4(),
        arc_id="arc-test",
        status="active",
        host_account_id=uuid4(),
        current_beat_id="beat-1",
        quality_tier="standard",
        player_count=4,
    )
    db.add(s)
    await db.flush()
    return s


def _make_route_result(
    *,
    model_used: str = CHARACTER_STANDARD_MODEL,
    input_tokens: int = 100,
    output_tokens: int = 50,
    latency_ms: int = 250,
    used_fallback: bool = False,
    content: str = "Hello from model",
) -> RouteResult:
    return RouteResult(
        content=content,
        model_used=model_used,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        latency_ms=latency_ms,
        used_fallback=used_fallback,
    )


# ---------------------------------------------------------------------------
# log_generation tests
# ---------------------------------------------------------------------------


async def test_log_generation_writes_correct_fields(session: AsyncSession) -> None:
    sess_row = await _make_session_row(session)
    result = _make_route_result(latency_ms=300, input_tokens=200, output_tokens=80)

    log = await log_generation(
        session,
        session_id=sess_row.session_id,
        task_type="character_dialogue",
        quality_tier="standard",
        result=result,
        tension_score=0.75,
    )

    assert log.log_id is not None
    fetched = await session.scalar(
        select(GenerationLog).where(GenerationLog.log_id == log.log_id)
    )
    assert fetched is not None
    assert fetched.session_id == sess_row.session_id
    assert fetched.task_type == "character_dialogue"
    assert fetched.quality_tier == "standard"
    assert fetched.model_used == CHARACTER_STANDARD_MODEL
    assert fetched.latency_ms == 300
    assert fetched.input_tokens == 200
    assert fetched.output_tokens == 80
    assert fetched.cost_usd > Decimal("0")
    assert abs((fetched.tension_score or 0) - 0.75) < 1e-9


async def test_log_generation_cost_nonzero_for_known_model(
    session: AsyncSession,
) -> None:
    sess_row = await _make_session_row(session)
    result = _make_route_result(
        model_used=CHARACTER_PREMIUM_MODEL,
        input_tokens=1000,
        output_tokens=500,
    )

    log = await log_generation(
        session,
        session_id=sess_row.session_id,
        task_type="narration",
        quality_tier="premium",
        result=result,
    )

    assert log.cost_usd > Decimal("0")


async def test_log_generation_raises_for_unknown_model(session: AsyncSession) -> None:
    sess_row = await _make_session_row(session)
    result = _make_route_result(
        model_used="unknown/model-xyz",
        input_tokens=500,
        output_tokens=200,
    )

    with pytest.raises(ValueError, match="unknown model cost"):
        await log_generation(
            session,
            session_id=sess_row.session_id,
            task_type="narration",
            quality_tier="standard",
            result=result,
        )


async def test_log_generation_omits_content_when_flag_off(
    session: AsyncSession, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("CONTENT_LOGGING_ENABLED", raising=False)
    sess_row = await _make_session_row(session)
    result = _make_route_result()
    messages = [{"role": "system", "content": "You are a character."}]

    log = await log_generation(
        session,
        session_id=sess_row.session_id,
        task_type="character_dialogue",
        quality_tier="standard",
        result=result,
        messages=messages,
    )

    assert log.prompt_text is None
    assert log.output_text is None


async def test_log_generation_writes_content_when_flag_on(
    session: AsyncSession, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("CONTENT_LOGGING_ENABLED", "true")
    sess_row = await _make_session_row(session)
    result = _make_route_result(content="Character speaks.")
    messages = [{"role": "system", "content": "You are a character."}]

    log = await log_generation(
        session,
        session_id=sess_row.session_id,
        task_type="character_dialogue",
        quality_tier="standard",
        result=result,
        messages=messages,
    )

    assert log.prompt_text is not None
    assert log.output_text == "Character speaks."
    import json as _json

    assert _json.loads(log.prompt_text) == messages


async def test_log_generation_writes_fallback_event(session: AsyncSession) -> None:
    sess_row = await _make_session_row(session)
    result = _make_route_result(
        model_used=SAFETY_STANDARD_FALLBACK_MODEL,
        used_fallback=True,
    )

    await log_generation(
        session,
        session_id=sess_row.session_id,
        task_type="safety_check",
        quality_tier="standard",
        result=result,
    )

    events = (
        await session.scalars(
            select(Event).where(
                Event.session_id == sess_row.session_id,
                Event.event_type == "routing_fallback",
            )
        )
    ).all()
    assert len(events) == 1
    assert events[0].event_type == "routing_fallback"
    assert events[0].session_id == sess_row.session_id
    assert events[0].actor_char_id is None
    payload = events[0].payload
    assert payload["task_type"] == "safety_check"
    assert payload["model_used"] == SAFETY_STANDARD_FALLBACK_MODEL


async def test_log_generation_no_fallback_event_on_clean_call(
    session: AsyncSession,
) -> None:
    sess_row = await _make_session_row(session)
    result = _make_route_result(used_fallback=False)

    await log_generation(
        session,
        session_id=sess_row.session_id,
        task_type="character_dialogue",
        quality_tier="standard",
        result=result,
    )

    events = (
        await session.scalars(
            select(Event).where(
                Event.session_id == sess_row.session_id,
                Event.event_type == "routing_fallback",
            )
        )
    ).all()
    assert len(events) == 0


# ---------------------------------------------------------------------------
# generate() wrapper tests
# ---------------------------------------------------------------------------


async def test_generate_writes_generation_log(session: AsyncSession) -> None:
    sess_row = await _make_session_row(session)
    mock_result = _make_route_result(
        model_used=CHARACTER_STANDARD_MODEL,
        input_tokens=120,
        output_tokens=60,
        content="generated output",
    )

    with patch(
        "engine.routing.logging.route_generation",
        new_callable=AsyncMock,
        return_value=mock_result,
    ):
        result = await generate(
            session,
            session_id=sess_row.session_id,
            task_type="character_dialogue",
            quality_tier="standard",
            messages=[{"role": "system", "content": "arc context"}],
            tension_score=0.5,
        )

    assert result is mock_result

    logs = (
        await session.scalars(
            select(GenerationLog).where(GenerationLog.session_id == sess_row.session_id)
        )
    ).all()
    assert len(logs) == 1
    log = logs[0]
    assert log.task_type == "character_dialogue"
    assert log.quality_tier == "standard"
    assert log.model_used == CHARACTER_STANDARD_MODEL
    assert log.input_tokens == 120
    assert log.output_tokens == 60
    assert log.cost_usd > Decimal("0")
    assert abs((log.tension_score or 0) - 0.5) < 1e-9


async def test_generate_writes_fallback_event(session: AsyncSession) -> None:
    sess_row = await _make_session_row(session)
    mock_result = _make_route_result(
        model_used=NARRATIVE_STANDARD_FALLBACK_MODEL,
        used_fallback=True,
    )

    with patch(
        "engine.routing.logging.route_generation",
        new_callable=AsyncMock,
        return_value=mock_result,
    ):
        await generate(
            session,
            session_id=sess_row.session_id,
            task_type="character_dialogue",
            quality_tier="standard",
            messages=[{"role": "user", "content": "hi"}],
        )

    events = (
        await session.scalars(
            select(Event).where(
                Event.session_id == sess_row.session_id,
                Event.event_type == "routing_fallback",
            )
        )
    ).all()
    assert len(events) == 1
    assert events[0].payload["model_used"] == NARRATIVE_STANDARD_FALLBACK_MODEL


# ---------------------------------------------------------------------------
# mark_stable_context_cacheable tests
# ---------------------------------------------------------------------------


def test_mark_cacheable_wraps_system_message() -> None:
    messages = [
        {"role": "system", "content": "You are a narrator."},
        {"role": "user", "content": "What happens next?"},
    ]
    result = mark_stable_context_cacheable(messages)

    first = result[0]
    assert first["role"] == "system"
    content = first["content"]
    assert isinstance(content, list)
    assert len(content) == 1
    block = content[0]
    assert block["type"] == "text"
    assert block["text"] == "You are a narrator."
    assert block["cache_control"] == {"type": "ephemeral"}


def test_mark_cacheable_ignores_non_system_messages() -> None:
    messages = [
        {"role": "system", "content": "You are a narrator."},
        {"role": "user", "content": "What happens next?"},
        {"role": "assistant", "content": "The story continues."},
    ]
    result = mark_stable_context_cacheable(messages)

    assert len(result) == 3
    assert result[1] == {"role": "user", "content": "What happens next?"}
    assert result[2] == {"role": "assistant", "content": "The story continues."}


def test_mark_cacheable_no_op_on_no_system_message() -> None:
    messages = [
        {"role": "user", "content": "What happens next?"},
        {"role": "assistant", "content": "The story continues."},
    ]
    result = mark_stable_context_cacheable(messages)
    assert result == messages


def test_mark_cacheable_does_not_mutate_input() -> None:
    original_content = "You are a narrator."
    messages = [
        {"role": "system", "content": original_content},
        {"role": "user", "content": "What happens next?"},
    ]
    original_first = dict(messages[0])

    mark_stable_context_cacheable(messages)

    assert messages[0]["content"] == original_content
    assert messages[0] == original_first
    assert len(messages) == 2
