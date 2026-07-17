"""Tests for generate_narrator_bridge (AW-221).

The function under test is generate_narrator_bridge. The only mock used is
at the litellm.acompletion boundary so we avoid real LLM calls while still
exercising the full L1/L2/L3/route_generation pipeline.

SQLite in-memory DB via engine.db.testing.make_sqlite_session_factory.
A Session row is required because generate() writes Event and GenerationLog
rows that carry a session_id FK.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from engine.db.orm import ArcBeatState
from engine.db.orm import Session as OrmSession
from engine.db.testing import make_sqlite_session_factory
from engine.events.models import AudienceTarget, EventCategory
from engine.narrator.bridge import generate_narrator_bridge
from engine.routing.router import resolve_model_key
from engine.safety import NEUTRAL_L1_BRIDGE, NEUTRAL_L2_BRIDGE

_NARRATOR_BRIDGE_STANDARD_MODEL = resolve_model_key("narrator_bridge", "standard")


def _litellm_response(content: str) -> MagicMock:
    """Build a mock litellm completion response with the given content."""
    msg = MagicMock()
    msg.content = content
    choice = MagicMock()
    choice.message = msg
    usage = MagicMock()
    usage.prompt_tokens = 80
    usage.completion_tokens = 40
    resp = MagicMock()
    resp.choices = [choice]
    resp.usage = usage
    return resp


def _l2_allowed_response() -> MagicMock:
    return _litellm_response(
        '{"blocked": false, "confidence": 0.05, "category": "permitted"}'
    )


def _l2_blocked_response() -> MagicMock:
    return _litellm_response(
        '{"blocked": true, "confidence": 0.95, "category": "prohibited"}'
    )


@pytest_asyncio.fixture()
async def db_engine_factory():
    engine, factory = await make_sqlite_session_factory()
    yield factory
    await engine.dispose()


@pytest_asyncio.fixture()
async def db(db_engine_factory: async_sessionmaker[AsyncSession]):
    async with db_engine_factory() as session:
        yield session


async def _make_session_row(db: AsyncSession, session_id: UUID) -> OrmSession:
    row = OrmSession(
        session_id=session_id,
        arc_id="nightcap",
        status="active",
        host_account_id=uuid4(),
        current_beat_id="dig",
        quality_tier="standard",
        player_count=4,
    )
    db.add(row)
    await db.flush()
    return row


def _make_snapshot(session_id: UUID, beat_id: str = "dig") -> ArcBeatState:
    snap = ArcBeatState(
        state_id=uuid4(),
        session_id=session_id,
        beat_id=beat_id,
        statemachine_config={
            "beat_id": beat_id,
            "configuration_values": [beat_id],
            "session_context": {"victim_revealed": True, "body_discovered": True},
        },
        transition_history=["arrival", "body", beat_id],
        is_current=True,
    )
    return snap


class TestNarratorBridgeGeneration:
    async def test_emits_content_event_with_narrator_bridge_type(
        self, db: AsyncSession
    ) -> None:
        session_id = uuid4()
        await _make_session_row(db, session_id)
        snapshot = _make_snapshot(session_id)

        with patch(
            "engine.routing.router.litellm.acompletion",
            new_callable=AsyncMock,
        ) as mock_completion:
            mock_completion.side_effect = [
                _l2_allowed_response(),
                _litellm_response("The investigation resumes at the manor."),
            ]
            event = await generate_narrator_bridge(db, session_id, snapshot, "standard")

        assert event.event_type == "narrator_bridge"
        assert event.category == EventCategory.narrative
        assert event.target_audience == AudienceTarget.all
        assert event.session_id == session_id
        assert event.presentation_hints.emotion == "warm"
        assert event.presentation_hints.urgency == "low"
        assert event.presentation_hints.pause_before_ms == 1500

    async def test_uses_narrator_bridge_task_type(self, db: AsyncSession) -> None:
        session_id = uuid4()
        await _make_session_row(db, session_id)
        snapshot = _make_snapshot(session_id)

        with patch(
            "engine.routing.router.litellm.acompletion",
            new_callable=AsyncMock,
        ) as mock_completion:
            mock_completion.side_effect = [
                _l2_allowed_response(),
                _litellm_response("The evening continues."),
            ]
            await generate_narrator_bridge(db, session_id, snapshot, "standard")

        assert mock_completion.call_count == 2
        # Second call (index 1) is the narrator_bridge generation call
        _, kwargs = mock_completion.call_args_list[1]
        assert kwargs.get("model") == _NARRATOR_BRIDGE_STANDARD_MODEL

    async def test_l1_hard_stop_replaces_content(self, db: AsyncSession) -> None:
        session_id = uuid4()
        await _make_session_row(db, session_id)

        # L1 triggers on "how to build bomb" in the session_context
        snapshot = ArcBeatState(
            state_id=uuid4(),
            session_id=session_id,
            beat_id="dig",
            statemachine_config={
                "beat_id": "dig",
                "configuration_values": ["dig"],
                "session_context": {"note": "how to build bomb"},
            },
            transition_history=[],
            is_current=True,
        )

        with patch("engine.routing.router.litellm.acompletion") as mock_completion:
            event = await generate_narrator_bridge(db, session_id, snapshot, "standard")

        # L1 fires before any LLM call
        mock_completion.assert_not_called()
        assert event.payload["text"] == NEUTRAL_L1_BRIDGE
        assert event.event_type == "narrator_bridge"

    async def test_l2_block_replaces_content(self, db: AsyncSession) -> None:
        session_id = uuid4()
        await _make_session_row(db, session_id)
        snapshot = _make_snapshot(session_id)

        # L2 classifier returns blocked; no narrator_bridge LLM call should follow
        with patch(
            "engine.routing.router.litellm.acompletion",
            new_callable=AsyncMock,
        ) as mock_completion:
            mock_completion.side_effect = [_l2_blocked_response()]
            event = await generate_narrator_bridge(db, session_id, snapshot, "standard")

        # Only the L2 classification call was made, not the narrator_bridge call
        assert mock_completion.call_count == 1
        assert event.payload["text"] == NEUTRAL_L2_BRIDGE
        assert event.event_type == "narrator_bridge"

    async def test_no_snapshot_emits_authored_event_without_llm_call(
        self, db: AsyncSession
    ) -> None:
        session_id = uuid4()

        with patch("engine.routing.router.litellm.acompletion") as mock_completion:
            event = await generate_narrator_bridge(db, session_id, None, "standard")

        mock_completion.assert_not_called()
        assert event.event_type == "narrator_bridge"
        assert event.category == EventCategory.narrative
        assert event.target_audience == AudienceTarget.all
        assert event.payload["text"] == "The session begins."

    async def test_prompt_contains_no_arc_specific_genre_text(
        self, db: AsyncSession
    ) -> None:
        """Regression guard: system prompt must not embed arc-specific genre labels.

        Uses a non-Nightcap arc shape to confirm the engine-level prompt stays
        neutral regardless of arc_id or session_context contents.
        """
        session_id = uuid4()
        row = OrmSession(
            session_id=session_id,
            arc_id="monster_rpg",
            status="active",
            host_account_id=uuid4(),
            current_beat_id="dungeon_entrance",
            quality_tier="standard",
            player_count=4,
        )
        db.add(row)
        await db.flush()

        snapshot = ArcBeatState(
            state_id=uuid4(),
            session_id=session_id,
            beat_id="dungeon_entrance",
            statemachine_config={
                "beat_id": "dungeon_entrance",
                "configuration_values": ["dungeon_entrance"],
                "session_context": {"encounter": "dragon_lair", "players_alive": True},
            },
            transition_history=["tavern", "dungeon_entrance"],
            is_current=True,
        )

        with patch(
            "engine.routing.router.litellm.acompletion",
            new_callable=AsyncMock,
        ) as mock_completion:
            mock_completion.side_effect = [
                _l2_allowed_response(),
                _litellm_response("The dungeon entrance looms before you."),
            ]
            await generate_narrator_bridge(db, session_id, snapshot, "standard")

        # Second call is the narrator_bridge generation call; inspect its messages
        assert mock_completion.call_count == 2
        _, kwargs = mock_completion.call_args_list[1]
        messages_text = str(kwargs["messages"])
        assert "murder mystery" not in messages_text.lower()
        assert "nightcap" not in messages_text.lower()

    async def test_arc_id_injects_registered_arc_content_rails(
        self, db: AsyncSession
    ) -> None:
        """With arc_id supplied, the arc's authored L3 rails reach the prompt.

        The registered arc's content_rails (including extra_prohibitions)
        must appear in the main generation call, not just the platform
        minimum block.
        """
        session_id = uuid4()
        await _make_session_row(db, session_id)
        snapshot = _make_snapshot(session_id)

        with patch(
            "engine.routing.router.litellm.acompletion",
            new_callable=AsyncMock,
        ) as mock_completion:
            mock_completion.side_effect = [
                _l2_allowed_response(),
                _litellm_response("The investigation resumes."),
            ]
            await generate_narrator_bridge(
                db, session_id, snapshot, "standard", arc_id="nightcap-v1"
            )

        assert mock_completion.call_count == 2
        _, kwargs = mock_completion.call_args_list[1]
        messages_text = str(kwargs["messages"])
        # A prohibited category from nightcap/arc.json content_rails.
        assert "graphic_violence" in messages_text
        # An extra_prohibitions sentence from nightcap/arc.json.
        assert "sexual content" in messages_text.lower()

    async def test_arc_id_injects_voice_block(self, db: AsyncSession) -> None:
        """With arc_id supplied, the arc's [VOICE] block reaches the system
        prompt (AW-276, finding F1)."""
        session_id = uuid4()
        await _make_session_row(db, session_id)
        snapshot = _make_snapshot(session_id)

        with patch(
            "engine.routing.router.litellm.acompletion",
            new_callable=AsyncMock,
        ) as mock_completion:
            mock_completion.side_effect = [
                _l2_allowed_response(),
                _litellm_response("The investigation resumes."),
            ]
            await generate_narrator_bridge(
                db, session_id, snapshot, "standard", arc_id="nightcap-v1"
            )

        _, kwargs = mock_completion.call_args_list[1]
        system_content = str(kwargs["messages"][0]["content"])
        assert "[VOICE]" in system_content
        # The voice directive from nightcap/arc.json tone_config.
        assert "Wit-first ensemble mystery." in system_content
        # Stable region: voice precedes the narrator task instruction.
        assert system_content.index("[VOICE]") < system_content.index(
            "You are the narrator"
        )

    async def test_unregistered_arc_id_falls_back_to_platform_minimum(
        self, db: AsyncSession
    ) -> None:
        """An unknown arc_id must not break the bridge; the platform-minimum
        L3 policy is injected instead."""
        session_id = uuid4()
        await _make_session_row(db, session_id)
        snapshot = _make_snapshot(session_id)

        with patch(
            "engine.routing.router.litellm.acompletion",
            new_callable=AsyncMock,
        ) as mock_completion:
            mock_completion.side_effect = [
                _l2_allowed_response(),
                _litellm_response("The evening continues."),
            ]
            event = await generate_narrator_bridge(
                db, session_id, snapshot, "standard", arc_id="some-unregistered-game"
            )

        assert event.event_type == "narrator_bridge"
        _, kwargs = mock_completion.call_args_list[1]
        messages_text = str(kwargs["messages"])
        # Platform minimum policy block is present as the backstop.
        assert "CONTENT POLICY" in messages_text
