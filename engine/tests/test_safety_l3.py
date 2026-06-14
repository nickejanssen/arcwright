"""Tests for Layer 3 in-generation policy injection helpers.

These tests verify three things that the issue acceptance criteria require:

1. Every main generation prompt includes an L3 policy block.
2. Blocked generation emits a neutral bridge event so the session can continue.
3. The Nightcap-specific L3 policy is sourced from arc content rails rather
   than hardcoded platform policy.

The third point is the most important for auditability: if a developer
changes the Nightcap arc's content_rails, the injected policy block must
reflect that change.  A hardcoded policy block would not.
"""

from __future__ import annotations

import uuid
from unittest.mock import patch
from uuid import UUID, uuid4

import pytest
from sqlalchemy import JSON, Text, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.schema import ColumnDefault, DefaultClause

from engine.arc.models import ContentRailsConfig
from engine.db.orm import Base, Session
from engine.routing import generate
from engine.routing.router import RouteResult, resolve_model_key
from engine.safety import (
    L3_BLOCK_SENTINEL,
    NEUTRAL_L3_BRIDGE,
    build_l3_blocked_route_result,
    build_l3_policy_block,
    build_nightcap_l3_policy_block,
    inject_l3_policy_block,
)

SAFETY_STANDARD_MODEL = resolve_model_key("safety_classification", "standard")
CHARACTER_STANDARD_MODEL = resolve_model_key("character_dialogue", "standard")


# ---------------------------------------------------------------------------
# SQLite metadata patch — same pattern used across the test suite.
# This lets us run tests without a real PostgreSQL instance.
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
# Fixtures
# ---------------------------------------------------------------------------


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


def _make_allowed_classification_result() -> RouteResult:
    return RouteResult(
        content='{"blocked": false, "confidence": 0.96, "category": "permitted"}',
        model_used=SAFETY_STANDARD_MODEL,
        input_tokens=80,
        output_tokens=12,
        latency_ms=90,
        used_fallback=False,
    )


def _make_main_generation_result() -> RouteResult:
    return RouteResult(
        content="The character speaks carefully about the clue.",
        model_used=CHARACTER_STANDARD_MODEL,
        input_tokens=200,
        output_tokens=60,
        latency_ms=300,
        used_fallback=False,
    )


# ---------------------------------------------------------------------------
# Unit tests: policy block builders
# ---------------------------------------------------------------------------


def test_build_l3_policy_block_contains_arc_prohibited_categories() -> None:
    """The policy block must contain each prohibited category from the arc rails.

    This test directly proves that the text of the policy block is derived
    from `content_rails.prohibited_categories`, not from a static string.
    If a designer adds "graphic torture" to the prohibited list, it must
    appear in the injected policy.
    """
    content_rails = ContentRailsConfig(
        prohibited_categories=["graphic torture", "erotica"],
        thematic_warnings=[],
        age_floor=18,
    )

    block = build_l3_policy_block(content_rails)

    # Every designer-defined prohibited category must appear in the block.
    assert "graphic torture" in block
    assert "erotica" in block
    # The block must have a clear header so the model knows these are rules.
    assert "CONTENT POLICY" in block


def test_build_l3_policy_block_returns_empty_string_when_no_prohibitions() -> None:
    """When the arc defines no prohibited categories, the block is empty.

    An empty block means nothing is injected into the prompt, which is the
    correct behaviour for arcs that rely entirely on L1 and L2 for safety.
    """
    content_rails = ContentRailsConfig(
        prohibited_categories=[],
        thematic_warnings=[],
        age_floor=18,
    )

    block = build_l3_policy_block(content_rails)

    assert block == ""


def test_build_nightcap_l3_policy_block_includes_arc_prohibited_categories() -> None:
    """Nightcap policy block must include any categories from the arc rails.

    This is the key acceptance criterion: the Nightcap policy must be sourced
    from arc rails, not hardcoded.  If the arc designer adds a new prohibited
    category, it must appear in the injected block.
    """
    content_rails = ContentRailsConfig(
        prohibited_categories=["real-world weapon construction"],
        thematic_warnings=["graphic violence"],
        age_floor=18,
    )

    block = build_nightcap_l3_policy_block(content_rails)

    # Arc-defined prohibition must be present.
    assert "real-world weapon construction" in block
    # The block must have a policy header.
    assert "CONTENT POLICY" in block


def test_build_nightcap_l3_policy_block_includes_nightcap_specific_rules() -> None:
    """The Nightcap policy block must include the Nightcap-specific extra rules.

    These rules are defined in the l3 module rather than in the arc JSON
    because they are specific to the Nightcap game experience (no graphic
    depiction of the murder, no sexual content, etc.) and should apply to
    every Nightcap session regardless of what the arc designer puts in rails.

    This test proves those rules are present in the injected block.
    """
    content_rails = ContentRailsConfig(
        prohibited_categories=[],
        thematic_warnings=[],
        age_floor=18,
    )

    block = build_nightcap_l3_policy_block(content_rails)

    # These phrases come from the Nightcap-specific prohibitions in l3.py.
    assert "murder" in block.lower()
    assert "sexual content" in block.lower()
    assert "real-world harmful information" in block.lower()
    assert "real, named person" in block.lower()


def test_nightcap_policy_block_arc_rails_override_is_additive() -> None:
    """Arc rails and Nightcap rules both appear together in the final block.

    The Nightcap builder adds arc rules AND Nightcap-specific rules.  It
    must not replace one with the other.
    """
    content_rails = ContentRailsConfig(
        prohibited_categories=["real-person doxxing"],
        thematic_warnings=[],
        age_floor=18,
    )

    block = build_nightcap_l3_policy_block(content_rails)

    # Arc rule is present.
    assert "real-person doxxing" in block
    # At least one Nightcap-specific rule is also present.
    assert "sexual content" in block.lower()


# ---------------------------------------------------------------------------
# Unit tests: inject_l3_policy_block
# ---------------------------------------------------------------------------


def test_inject_l3_policy_block_prepends_policy_message() -> None:
    """The injected policy message must be the first message in the list.

    The model reads messages in order.  The policy must come first so the
    model knows the rules before it reads the story context and generates.
    """
    content_rails = ContentRailsConfig(
        prohibited_categories=["graphic torture"],
        thematic_warnings=[],
        age_floor=18,
    )
    messages = [{"role": "system", "content": "You are a detective character."}]

    result = inject_l3_policy_block(messages, content_rails)

    # Policy is first, original message is second.
    assert len(result) == 2
    assert result[0]["role"] == "system"
    assert "CONTENT POLICY" in result[0]["content"]
    assert "graphic torture" in result[0]["content"]
    assert result[1]["content"] == "You are a detective character."


def test_inject_l3_policy_block_does_not_mutate_original_messages() -> None:
    """The original messages list must never be changed.

    Mutating the input would be a bug: the caller may reuse the same messages
    list (e.g. for logging), and mutation would corrupt that data.
    """
    content_rails = ContentRailsConfig(
        prohibited_categories=["graphic torture"],
        thematic_warnings=[],
        age_floor=18,
    )
    messages = [{"role": "system", "content": "You are a detective character."}]
    original_length = len(messages)
    original_content = messages[0]["content"]

    inject_l3_policy_block(messages, content_rails)

    assert len(messages) == original_length
    assert messages[0]["content"] == original_content


def test_inject_l3_policy_block_returns_original_when_no_rails() -> None:
    """When content_rails is None, messages are returned unchanged.

    This handles the case where no arc has been wired up yet.  The function
    must be safe to call with None without crashing or injecting anything.
    """
    messages = [{"role": "user", "content": "Hello."}]

    result = inject_l3_policy_block(messages, None)

    assert result is messages


def test_inject_l3_policy_block_returns_original_when_no_prohibitions() -> None:
    """When prohibited_categories is empty, messages are returned unchanged.

    An arc that defines no prohibited categories should not have an empty
    policy block injected into every prompt.
    """
    content_rails = ContentRailsConfig(
        prohibited_categories=[],
        thematic_warnings=[],
        age_floor=18,
    )
    messages = [{"role": "user", "content": "Hello."}]

    result = inject_l3_policy_block(messages, content_rails)

    assert result is messages


def test_inject_l3_policy_block_nightcap_mode_includes_nightcap_rules() -> None:
    """In Nightcap mode, the injected block includes Nightcap-specific rules."""
    content_rails = ContentRailsConfig(
        prohibited_categories=[],
        thematic_warnings=[],
        age_floor=18,
    )
    messages = [{"role": "system", "content": "You are a suspect."}]

    result = inject_l3_policy_block(messages, content_rails, nightcap_mode=True)

    # Nightcap mode produces a non-empty block even with no arc prohibitions.
    assert len(result) == 2
    assert "CONTENT POLICY" in result[0]["content"]
    assert "murder" in result[0]["content"].lower()


# ---------------------------------------------------------------------------
# Unit tests: build_l3_blocked_route_result sentinel
# ---------------------------------------------------------------------------


def test_l3_blocked_route_result_is_non_provider_sentinel() -> None:
    """The L3 block sentinel must not contain a real provider or model name."""
    result = build_l3_blocked_route_result()

    assert result.content == NEUTRAL_L3_BRIDGE
    assert result.model_used == L3_BLOCK_SENTINEL
    assert result.input_tokens == 0
    assert result.output_tokens == 0
    assert result.latency_ms == 0
    assert result.used_fallback is False


# ---------------------------------------------------------------------------
# Integration tests: generate() with L3 injection
# ---------------------------------------------------------------------------


async def test_generate_injects_l3_policy_block_before_main_call(
    db_session: AsyncSession,
) -> None:
    """The main generation call must receive the L3 policy block.

    This proves that inject_l3_policy_block runs between L2 approval and
    the main route call, so the policy is part of every approved generation.
    """
    sess_row = await _make_session_row(db_session)
    content_rails = ContentRailsConfig(
        prohibited_categories=["real-world weapon construction"],
        thematic_warnings=[],
        age_floor=18,
    )
    original_messages = [{"role": "system", "content": "You are a detective."}]
    captured_main_messages: list[list[dict]] = []

    async def fake_route_generation(task_type, quality_tier, messages, temperature):  # type: ignore[no-untyped-def]
        if task_type == "safety_classification":
            return _make_allowed_classification_result()
        # Capture the messages received by the main generation call.
        captured_main_messages.append(list(messages))
        return _make_main_generation_result()

    with patch(
        "engine.routing.logging.route_generation",
        side_effect=fake_route_generation,
    ):
        await generate(
            db_session,
            session_id=sess_row.session_id,
            task_type="character_dialogue",
            quality_tier="standard",
            messages=original_messages,
            content_rails=content_rails,
        )

    assert len(captured_main_messages) == 1
    main_messages = captured_main_messages[0]
    # The policy block must be the first message.
    assert main_messages[0]["role"] == "system"
    assert "CONTENT POLICY" in main_messages[0]["content"]
    assert "real-world weapon construction" in main_messages[0]["content"]
    # The original system message must still be present.
    assert any(msg["content"] == "You are a detective." for msg in main_messages)


async def test_generate_nightcap_mode_injects_nightcap_rules(
    db_session: AsyncSession,
) -> None:
    """In Nightcap mode, the main call receives the Nightcap-specific policy.

    This test proves the Nightcap L3 policy is sourced from the arc rails
    (the `content_rails` object) and not from a hardcoded string.  The
    prohibited category we pass ("real-person doxxing") must appear alongside
    the Nightcap-specific rules in the injected message.
    """
    sess_row = await _make_session_row(db_session)
    content_rails = ContentRailsConfig(
        prohibited_categories=["real-person doxxing"],
        thematic_warnings=[],
        age_floor=18,
    )
    original_messages = [{"role": "system", "content": "You are a suspect."}]
    captured_main_messages: list[list[dict]] = []

    async def fake_route_generation(task_type, quality_tier, messages, temperature):  # type: ignore[no-untyped-def]
        if task_type == "safety_classification":
            return _make_allowed_classification_result()
        captured_main_messages.append(list(messages))
        return _make_main_generation_result()

    with patch(
        "engine.routing.logging.route_generation",
        side_effect=fake_route_generation,
    ):
        await generate(
            db_session,
            session_id=sess_row.session_id,
            task_type="character_dialogue",
            quality_tier="standard",
            messages=original_messages,
            content_rails=content_rails,
            nightcap_mode=True,
        )

    assert len(captured_main_messages) == 1
    policy_text = captured_main_messages[0][0]["content"]
    # Arc-level prohibited category is present (sourced from content_rails).
    assert "real-person doxxing" in policy_text
    # Nightcap-specific rule is also present.
    assert "sexual content" in policy_text.lower()


async def test_generate_without_content_rails_does_not_inject_policy(
    db_session: AsyncSession,
) -> None:
    """When content_rails is None, the main call receives unmodified messages.

    Callers that have not yet wired up arc content rails must not have an
    empty or accidental policy block injected into their prompts.
    """
    sess_row = await _make_session_row(db_session)
    original_messages = [{"role": "system", "content": "You are a narrator."}]
    captured_main_messages: list[list[dict]] = []

    async def fake_route_generation(task_type, quality_tier, messages, temperature):  # type: ignore[no-untyped-def]
        if task_type == "safety_classification":
            return _make_allowed_classification_result()
        captured_main_messages.append(list(messages))
        return _make_main_generation_result()

    with patch(
        "engine.routing.logging.route_generation",
        side_effect=fake_route_generation,
    ):
        await generate(
            db_session,
            session_id=sess_row.session_id,
            task_type="character_dialogue",
            quality_tier="standard",
            messages=original_messages,
            content_rails=None,
        )

    assert len(captured_main_messages) == 1
    # Without content rails, the messages are passed through unchanged.
    assert captured_main_messages[0] == original_messages


async def test_generate_safety_classification_task_skips_l3_injection(
    db_session: AsyncSession,
) -> None:
    """Safety classification tasks must not have L3 policy injected into them.

    If L3 were injected into the classification call, it would corrupt the
    classifier prompt and produce unpredictable results.  The safety
    classification task is exempt from L3 injection (and L2 classification)
    by design.
    """
    sess_row = await _make_session_row(db_session)
    content_rails = ContentRailsConfig(
        prohibited_categories=["graphic torture"],
        thematic_warnings=[],
        age_floor=18,
    )
    original_messages = [{"role": "system", "content": "Classify this content."}]
    captured_messages: list[list[dict]] = []

    async def fake_route_generation(task_type, quality_tier, messages, temperature):  # type: ignore[no-untyped-def]
        captured_messages.append(list(messages))
        return _make_main_generation_result()

    with patch(
        "engine.routing.logging.route_generation",
        side_effect=fake_route_generation,
    ):
        await generate(
            db_session,
            session_id=sess_row.session_id,
            task_type="safety_classification",
            quality_tier="standard",
            messages=original_messages,
            content_rails=content_rails,
        )

    # Only one call must have been made (no L2 classification on top of L3).
    assert len(captured_messages) == 1
    # The messages passed to the route call must be the originals, unmodified.
    assert captured_messages[0] == original_messages
