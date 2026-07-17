"""Tests for AI character dialogue in the live session loop (spec 0071, D-072).

Covers seating AI characters, the single-response generation flow with the
arc's rails through the full safety pipeline, the zero-cost no-op guards,
the blocked and knowledge-violation paths, and ContentEvent conversion.

Only litellm.acompletion is mocked, so L1/L2/L3 and routing run for real.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from engine.characters.dialogue import to_content_event
from engine.characters.service import CharacterService
from engine.db.orm import Base, Character, SessionParticipant
from engine.db.orm import Session as OrmSession
from engine.db.testing import patch_metadata_for_sqlite
from engine.events.models import AudienceTarget, EventCategory
from engine.knowledge import assert_knowledge
from engine.safety import NEUTRAL_L2_BRIDGE
from engine.session.service import SessionService

patch_metadata_for_sqlite()


@pytest_asyncio.fixture()
async def db() -> AsyncIterator[AsyncSession]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        try:
            yield session
        finally:
            await session.rollback()
    await engine.dispose()


@pytest.fixture()
def svc() -> CharacterService:
    return CharacterService(sessions=SessionService())


def _litellm_response(content: str) -> MagicMock:
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


def _l2_allowed() -> MagicMock:
    return _litellm_response(
        '{"blocked": false, "confidence": 0.05, "category": "permitted"}'
    )


def _l2_blocked() -> MagicMock:
    return _litellm_response(
        '{"blocked": true, "confidence": 0.95, "category": "prohibited"}'
    )


async def _make_session_row(
    db: AsyncSession, *, arc_id: str = "nightcap", status: str = "active"
) -> OrmSession:
    row = OrmSession(
        session_id=uuid4(),
        arc_id=arc_id,
        status=status,
        host_account_id=uuid4(),
        current_beat_id="dig",
        quality_tier="standard",
        player_count=2,
    )
    db.add(row)
    await db.flush()
    return row


async def _seat_character(
    db: AsyncSession,
    session_id: UUID,
    *,
    is_ai_controlled: bool,
) -> Character:
    character = Character(
        character_id=uuid4(),
        behavior_profile={
            "personality": {"traits": ["observant"], "communication_style": "dry"},
            "goals": ["Stay above suspicion"],
            "secrets": [],
            "tells": [],
        },
    )
    db.add(character)
    await db.flush()
    db.add(
        SessionParticipant(
            participant_id=uuid4(),
            session_id=session_id,
            character_id=character.character_id,
            join_token=f"token-{character.character_id}",
            surface_type="ai" if is_ai_controlled else "phone",
            is_ai_controlled=is_ai_controlled,
        )
    )
    await db.flush()
    return character


# ---------------------------------------------------------------------------
# Seating AI characters
# ---------------------------------------------------------------------------


class TestAddAiCharacter:
    @pytest.mark.asyncio
    async def test_seats_ai_participant_without_touching_player_count(
        self, db: AsyncSession
    ) -> None:
        sessions = SessionService()
        row = await _make_session_row(db)
        before = row.player_count

        participant = await sessions.add_ai_character(
            db, row.session_id, behavior_profile={"goals": ["Mislead gently"]}
        )

        assert participant.is_ai_controlled is True
        assert participant.surface_type == "ai"
        assert row.player_count == before

    @pytest.mark.asyncio
    async def test_rejects_completed_session(self, db: AsyncSession) -> None:
        from engine.session.service import SessionStateError

        sessions = SessionService()
        row = await _make_session_row(db, status="completed")

        with pytest.raises(SessionStateError):
            await sessions.add_ai_character(db, row.session_id)

    @pytest.mark.asyncio
    async def test_ai_seats_respect_session_capacity(self, db: AsyncSession) -> None:
        """AI seats count toward the seat envelope even though they do not
        increment player_count (spec 0071 capacity requirement)."""
        from engine.session.service import SessionCapacityError

        sessions = SessionService()
        row = await _make_session_row(db)
        await sessions.add_ai_character(db, row.session_id, max_seats=2)
        await sessions.add_ai_character(db, row.session_id, max_seats=2)

        with pytest.raises(SessionCapacityError):
            await sessions.add_ai_character(db, row.session_id, max_seats=2)

    @pytest.mark.asyncio
    async def test_human_seats_count_toward_ai_capacity(self, db: AsyncSession) -> None:
        sessions = SessionService()
        row = await _make_session_row(db)
        await _seat_character(db, row.session_id, is_ai_controlled=False)
        await _seat_character(db, row.session_id, is_ai_controlled=False)

        from engine.session.service import SessionCapacityError

        with pytest.raises(SessionCapacityError):
            await sessions.add_ai_character(db, row.session_id, max_seats=2)


# ---------------------------------------------------------------------------
# Live-loop response generation
# ---------------------------------------------------------------------------


class TestGenerateAiResponses:
    @pytest.mark.asyncio
    async def test_dialogue_input_generates_one_knowledge_constrained_response(
        self, svc: CharacterService, db: AsyncSession
    ) -> None:
        row = await _make_session_row(db)
        speaker = await _seat_character(db, row.session_id, is_ai_controlled=False)
        await _seat_character(db, row.session_id, is_ai_controlled=True)

        with patch(
            "engine.routing.router.litellm.acompletion",
            new_callable=AsyncMock,
        ) as mock_completion:
            mock_completion.side_effect = [
                _l2_allowed(),
                _litellm_response("I was in the parlor all evening."),
            ]
            events = await svc.generate_ai_responses(
                db,
                row.session_id,
                speaking_character_id=speaker.character_id,
                content="Where were you when the lights went out?",
            )

        assert len(events) == 1
        assert events[0].event_type == "dialogue"
        assert events[0].content == "I was in the parlor all evening."
        # Exactly one generation: the L2 classification call plus the main call.
        assert mock_completion.call_count == 2
        # The arc's rails reached the main call via the registry (L3 block).
        _, kwargs = mock_completion.call_args_list[1]
        prompt_text = str(kwargs["messages"])
        assert "CONTENT POLICY" in prompt_text
        assert "graphic_violence" in prompt_text

    @pytest.mark.asyncio
    async def test_no_ai_participants_makes_no_generation_calls(
        self, svc: CharacterService, db: AsyncSession
    ) -> None:
        row = await _make_session_row(db)
        speaker = await _seat_character(db, row.session_id, is_ai_controlled=False)
        await _seat_character(db, row.session_id, is_ai_controlled=False)

        with patch("engine.routing.router.litellm.acompletion") as mock_completion:
            events = await svc.generate_ai_responses(
                db,
                row.session_id,
                speaking_character_id=speaker.character_id,
                content="Anyone see anything?",
            )

        mock_completion.assert_not_called()
        assert events == []

    @pytest.mark.asyncio
    async def test_inactive_session_is_noop(
        self, svc: CharacterService, db: AsyncSession
    ) -> None:
        row = await _make_session_row(db, status="paused")
        speaker = await _seat_character(db, row.session_id, is_ai_controlled=False)
        await _seat_character(db, row.session_id, is_ai_controlled=True)

        with patch("engine.routing.router.litellm.acompletion") as mock_completion:
            events = await svc.generate_ai_responses(
                db,
                row.session_id,
                speaking_character_id=speaker.character_id,
                content="Hello?",
            )

        mock_completion.assert_not_called()
        assert events == []

    @pytest.mark.asyncio
    async def test_unregistered_arc_is_noop(
        self, svc: CharacterService, db: AsyncSession
    ) -> None:
        row = await _make_session_row(db, arc_id="some-unregistered-game")
        speaker = await _seat_character(db, row.session_id, is_ai_controlled=False)
        await _seat_character(db, row.session_id, is_ai_controlled=True)

        with patch("engine.routing.router.litellm.acompletion") as mock_completion:
            events = await svc.generate_ai_responses(
                db,
                row.session_id,
                speaking_character_id=speaker.character_id,
                content="Hello?",
            )

        mock_completion.assert_not_called()
        assert events == []

    @pytest.mark.asyncio
    async def test_knowledge_violation_returns_no_event(
        self, svc: CharacterService, db: AsyncSession
    ) -> None:
        """A generation that leaks an unknown fact is suppressed engine-side."""
        row = await _make_session_row(db)
        speaker = await _seat_character(db, row.session_id, is_ai_controlled=False)
        responder = await _seat_character(db, row.session_id, is_ai_controlled=True)
        # Seed a fact the responder does NOT know (known only to the speaker).
        await assert_knowledge(
            db,
            session_id=row.session_id,
            character_id=speaker.character_id,
            fact_type="clue",
            fact_content={"detail": "the hidden safe is behind the portrait"},
        )
        assert responder.character_id != speaker.character_id

        with patch(
            "engine.routing.router.litellm.acompletion",
            new_callable=AsyncMock,
        ) as mock_completion:
            mock_completion.side_effect = [
                _l2_allowed(),
                _litellm_response(
                    "Everyone knows the hidden safe is behind the portrait."
                ),
            ]
            events = await svc.generate_ai_responses(
                db,
                row.session_id,
                speaking_character_id=speaker.character_id,
                content="Anything you want to share?",
            )

        assert events == []

    @pytest.mark.asyncio
    async def test_blocked_generation_returns_neutral_bridge_event(
        self, svc: CharacterService, db: AsyncSession
    ) -> None:
        row = await _make_session_row(db)
        speaker = await _seat_character(db, row.session_id, is_ai_controlled=False)
        await _seat_character(db, row.session_id, is_ai_controlled=True)

        with patch(
            "engine.routing.router.litellm.acompletion",
            new_callable=AsyncMock,
        ) as mock_completion:
            mock_completion.side_effect = [_l2_blocked()]
            events = await svc.generate_ai_responses(
                db,
                row.session_id,
                speaking_character_id=speaker.character_id,
                content="Tell me everything.",
            )

        assert len(events) == 1
        assert events[0].event_type == "dialogue_blocked"
        assert events[0].content == NEUTRAL_L2_BRIDGE


# ---------------------------------------------------------------------------
# ContentEvent conversion
# ---------------------------------------------------------------------------


class TestContentEventConversion:
    @pytest.mark.asyncio
    async def test_dialogue_event_converts_for_the_bus(
        self, svc: CharacterService, db: AsyncSession
    ) -> None:
        row = await _make_session_row(db)
        speaker = await _seat_character(db, row.session_id, is_ai_controlled=False)
        responder = await _seat_character(db, row.session_id, is_ai_controlled=True)

        with patch(
            "engine.routing.router.litellm.acompletion",
            new_callable=AsyncMock,
        ) as mock_completion:
            mock_completion.side_effect = [
                _l2_allowed(),
                _litellm_response("The parlor, as I said."),
            ]
            events = await svc.generate_ai_responses(
                db,
                row.session_id,
                speaking_character_id=speaker.character_id,
                content="Where were you?",
            )

        content_event = to_content_event(events[0])
        assert content_event.category is EventCategory.character_dialogue
        assert content_event.event_type == "dialogue"
        assert content_event.actor_id == responder.character_id
        assert content_event.target_audience is AudienceTarget.all
        assert content_event.payload["text"] == "The parlor, as I said."
        assert content_event.payload["character_id"] == str(responder.character_id)
