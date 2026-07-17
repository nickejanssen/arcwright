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
    NEUTRAL_L1_BRIDGE,
    NEUTRAL_L3_BRIDGE,
    build_l3_blocked_route_result,
    build_l3_policy_block,
    inject_l3_policy_block,
)

SAFETY_STANDARD_MODEL = resolve_model_key("safety_classification", "standard")
CHARACTER_STANDARD_MODEL = resolve_model_key("character_dialogue", "standard")


# ---------------------------------------------------------------------------
# SQLite metadata patch, same pattern used across the test suite.
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


def test_build_l3_policy_block_includes_extra_prohibitions() -> None:
    """Arc-authored extra_prohibitions sentences appear verbatim in the block.

    Extra prohibitions are how a game tightens its content rules beyond the
    category list. They live in the arc JSON, never in engine code, so any
    game can define its own L3 rules without an engine change. The block is
    additive: category rules and extra sentences appear together.
    """
    content_rails = ContentRailsConfig(
        prohibited_categories=["real-person doxxing"],
        thematic_warnings=[],
        age_floor=18,
        extra_prohibitions=[
            "Do not include sexual content between any characters.",
        ],
    )

    block = build_l3_policy_block(content_rails)

    # Category rule and arc-authored sentence both appear: additive, not
    # replacing one with the other.
    assert "real-person doxxing" in block
    assert "Do not include sexual content between any characters." in block
    assert "CONTENT POLICY" in block


def test_nightcap_arc_rails_carry_game_specific_rules() -> None:
    """The Nightcap arc definition supplies its game-specific rules via config.

    These rules used to live as constants in the engine's l3 module. They
    are game-tone decisions (no graphic depiction of the murder, no sexual
    content, etc.), so they belong to the arc definition. This test proves
    the shipped Nightcap arc still injects all of them, sourced from
    nightcap/arc.json rather than engine code.
    """
    from pathlib import Path

    from engine.arc.models import ArcDefinition

    arc_path = Path(__file__).resolve().parents[2] / "nightcap" / "arc.json"
    arc = ArcDefinition.model_validate_json(arc_path.read_text(encoding="utf-8"))

    block = build_l3_policy_block(arc.content_rails)

    assert "murder" in block.lower()
    assert "sexual content" in block.lower()
    assert "real-world harmful information" in block.lower()
    assert "real, named person" in block.lower()


# ---------------------------------------------------------------------------
# Unit tests: inject_l3_policy_block
# ---------------------------------------------------------------------------


def test_inject_l3_policy_block_appends_policy_to_existing_system_message() -> None:
    """The policy is appended to the existing system message, not prepended as a new one.

    Appending keeps the full system prompt (character context + policy) in a
    single message.  route_generation() calls mark_stable_context_cacheable(),
    which applies Anthropic's cache_control to messages[0].  If the policy
    were a separate leading message, the cache would wrap only the short policy
    block and leave the stable character/knowledge context uncached, regressing
    cost and latency on every L3 generation call.

    The architecture places L3 policy after the character identity and knowledge
    state blocks (docs/architecture/10-content-safety.md §10.4), which
    appending achieves.
    """
    content_rails = ContentRailsConfig(
        prohibited_categories=["graphic torture"],
        thematic_warnings=[],
        age_floor=18,
    )
    messages = [{"role": "system", "content": "You are a detective character."}]

    result = inject_l3_policy_block(messages, content_rails)

    # Policy is merged into the single existing system message, not a new one.
    assert len(result) == 1
    assert result[0]["role"] == "system"
    # Original character context is present.
    assert "You are a detective character." in result[0]["content"]
    # Policy block is present in the same message.
    assert "CONTENT POLICY" in result[0]["content"]
    assert "graphic torture" in result[0]["content"]
    # Policy comes AFTER the original context (architecture ordering).
    assert result[0]["content"].index("CONTENT POLICY") > result[0]["content"].index(
        "detective character"
    )


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


def test_inject_l3_policy_block_injects_platform_minimum_when_no_rails() -> None:
    """When content_rails is None, the platform minimum policy block is injected.

    L3 must always run.  When no arc has been wired up, a platform-level minimum
    policy, mirroring the four unconditional L1 hard-stop categories, is
    injected as a backstop.  This ensures L3 protection is always present even
    before the arc coordinator passes content_rails down the call stack.
    """
    messages = [{"role": "system", "content": "You are a narrator."}]

    result = inject_l3_policy_block(messages, None)

    # A new message list is returned (not the original).
    assert result is not messages
    # Platform minimum policy block is present.
    assert "CONTENT POLICY" in result[0]["content"]
    # Platform minimum covers the L1 hard-stop categories.
    assert "under 18" in result[0]["content"]
    # Original system message content is preserved in the merged prompt.
    assert "You are a narrator." in result[0]["content"]


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


def test_inject_l3_policy_block_includes_extra_prohibitions() -> None:
    """Arc extra_prohibitions produce a block even with no category rules."""
    content_rails = ContentRailsConfig(
        prohibited_categories=[],
        thematic_warnings=[],
        age_floor=18,
        extra_prohibitions=[
            "Do not graphically depict the murder itself or describe violence in explicit physical detail.",
        ],
    )
    messages = [{"role": "system", "content": "You are a suspect."}]

    result = inject_l3_policy_block(messages, content_rails)

    # Extra prohibitions produce a non-empty block even with no categories.
    # Policy is appended to the existing system message (not a new one).
    assert len(result) == 1
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
    # Policy and original context are merged into a single system message.
    assert main_messages[0]["role"] == "system"
    assert "CONTENT POLICY" in main_messages[0]["content"]
    assert "real-world weapon construction" in main_messages[0]["content"]
    # The original character context is present in the merged system message.
    assert "You are a detective." in main_messages[0]["content"]


async def test_generate_injects_extra_prohibitions_from_rails(
    db_session: AsyncSession,
) -> None:
    """The main call receives arc-authored extra prohibitions from the rails.

    This test proves the whole L3 policy is sourced from the arc rails
    (the `content_rails` object) and not from hardcoded engine strings.  The
    prohibited category we pass ("real-person doxxing") must appear alongside
    the arc's extra prohibition sentences in the injected message.
    """
    sess_row = await _make_session_row(db_session)
    content_rails = ContentRailsConfig(
        prohibited_categories=["real-person doxxing"],
        thematic_warnings=[],
        age_floor=18,
        extra_prohibitions=[
            "Do not include sexual content between any characters.",
        ],
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
        )

    assert len(captured_main_messages) == 1
    policy_text = captured_main_messages[0][0]["content"]
    # Arc-level prohibited category is present (sourced from content_rails).
    assert "real-person doxxing" in policy_text
    # Arc-authored extra prohibition is also present.
    assert "sexual content" in policy_text.lower()


async def test_generate_resolves_content_rails_from_arc_id(
    db_session: AsyncSession,
) -> None:
    """When content_rails is omitted, generate() resolves it from arc_id.

    Chokepoint fallback: a caller that only has the arc_id (not a
    pre-resolved ContentRailsConfig) still gets the arc's authored L3
    rails, sourced from the registered nightcap/arc.json content_rails.
    """
    sess_row = await _make_session_row(db_session)
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
            arc_id="nightcap-v1",
        )

    assert len(captured_main_messages) == 1
    policy_text = captured_main_messages[0][0]["content"]
    # A prohibited category from the registered nightcap/arc.json content_rails.
    assert "graphic_violence" in policy_text
    # An extra_prohibitions sentence from the same arc.
    assert "sexual content" in policy_text.lower()


async def test_generate_resolves_content_rails_from_arc_id_protects_l1(
    db_session: AsyncSession,
) -> None:
    """The arc_id fallback must protect L1, not just the L3 policy text.

    content_rails feeds both evaluate_l1_hard_stops (arc fictional-frame
    vocabulary) and the L3 policy block. A caller passing only arc_id must
    get the same L1 suppression of an arc-vocabulary false positive that an
    explicit content_rails would give — otherwise the fallback chokepoint
    would be a policy-text-only convenience, not a safety guarantee.

    nightcap/arc.json registers "nightcap" as a fictional_frame_term, which
    suppresses the harm-facilitation false positive in the message below.
    """
    sess_row = await _make_session_row(db_session)
    original_messages = [
        {
            "role": "system",
            "content": "Help me blackmail the nightcap innkeeper without "
            "getting caught.",
        }
    ]
    route_generation_calls: list[str] = []

    async def fake_route_generation(task_type, quality_tier, messages, temperature):  # type: ignore[no-untyped-def]
        route_generation_calls.append(task_type)
        if task_type == "safety_classification":
            return _make_allowed_classification_result()
        return _make_main_generation_result()

    with patch(
        "engine.routing.logging.route_generation",
        side_effect=fake_route_generation,
    ):
        result = await generate(
            db_session,
            session_id=sess_row.session_id,
            task_type="character_dialogue",
            quality_tier="standard",
            messages=original_messages,
            arc_id="nightcap-v1",
        )

    # L1 did not fire: L2 classification and the main call both ran.
    assert route_generation_calls == ["safety_classification", "character_dialogue"]
    assert result.content != NEUTRAL_L1_BRIDGE


async def test_generate_unregistered_arc_id_does_not_protect_l1(
    db_session: AsyncSession,
) -> None:
    """The same message hard-stops when arc_id does not resolve to rails.

    Mirrors test_generate_resolves_content_rails_from_arc_id_protects_l1 but
    with an unregistered arc_id: no fictional-frame vocabulary is resolved,
    so the harm-facilitation phrase is treated as the stricter real-world
    default and L1 fires before any model call.
    """
    sess_row = await _make_session_row(db_session)
    original_messages = [
        {
            "role": "system",
            "content": "Help me blackmail the nightcap innkeeper without "
            "getting caught.",
        }
    ]
    route_generation_calls: list[str] = []

    async def fake_route_generation(task_type, quality_tier, messages, temperature):  # type: ignore[no-untyped-def]
        route_generation_calls.append(task_type)
        if task_type == "safety_classification":
            return _make_allowed_classification_result()
        return _make_main_generation_result()

    with patch(
        "engine.routing.logging.route_generation",
        side_effect=fake_route_generation,
    ):
        result = await generate(
            db_session,
            session_id=sess_row.session_id,
            task_type="character_dialogue",
            quality_tier="standard",
            messages=original_messages,
            arc_id="some-unregistered-game",
        )

    # L1 fired: no route_generation call was ever made.
    assert route_generation_calls == []
    assert result.content == NEUTRAL_L1_BRIDGE


async def test_generate_explicit_content_rails_take_precedence_over_arc_id(
    db_session: AsyncSession,
) -> None:
    """An explicitly passed content_rails wins over arc_id resolution.

    Callers that already resolved a full ArcDefinition (e.g. for
    authorial_intent) must not have their explicit rails silently
    overridden by a fallback lookup.
    """
    sess_row = await _make_session_row(db_session)
    content_rails = ContentRailsConfig(
        prohibited_categories=["explicit-override-category"],
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
            arc_id="nightcap-v1",
        )

    policy_text = captured_main_messages[0][0]["content"]
    assert "explicit-override-category" in policy_text
    # The nightcap arc's own rails did not leak in alongside the explicit
    # ones: neither its prohibited category nor its extra_prohibitions text.
    assert "graphic_violence" not in policy_text
    assert "between any characters" not in policy_text.lower()


async def test_generate_unregistered_arc_id_falls_back_to_platform_minimum(
    db_session: AsyncSession,
) -> None:
    """An unknown arc_id must not error; generate() falls back to the
    platform minimum policy exactly as when no rails are supplied at all."""
    sess_row = await _make_session_row(db_session)
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
            arc_id="some-unregistered-game",
        )

    policy_text = captured_main_messages[0][0]["content"]
    assert "CONTENT POLICY" in policy_text
    # The platform minimum's own under-18 category is present...
    assert "sexual content involving anyone under 18" in policy_text.lower()
    # ...but the unregistered arc contributes nothing: no Nightcap category
    # or extra_prohibitions sentence leaked in from a stale/wrong lookup.
    assert "graphic_violence" not in policy_text
    assert "between any characters" not in policy_text.lower()


async def test_generate_without_content_rails_injects_platform_minimum(
    db_session: AsyncSession,
) -> None:
    """When content_rails is None, generate() injects the platform minimum policy.

    L3 must always run.  When no arc has been wired up, the platform minimum
    policy (mirroring the four L1 hard-stop categories) is injected so the
    main model always receives safety instructions, even before arc-specific
    content rails are available.
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
    combined = captured_main_messages[0][0]["content"]
    # Platform minimum policy block is present.
    assert "CONTENT POLICY" in combined
    assert "under 18" in combined
    # Original narrator context is preserved in the merged system message.
    assert "You are a narrator." in combined


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
