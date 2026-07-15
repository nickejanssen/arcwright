"""Character service — DB-backed participant lookups, in-memory input log.

Architecture: docs/architecture/09-developer-api.md §9.2.

Participant existence and ownership are resolved against
``session_participants`` (the same source of truth used by
``SessionService``) so the service stays consistent across cold process
restarts. Player-submitted ``action`` / ``dialogue`` inputs are still
held in-memory — that surface has no AC2 resume requirement and a
dedicated events-table representation is the AW-222 telemetry scope.

This layer captures the authored, deterministic side of the unified
character model first. Since spec 0071 (D-072) it also owns the live-loop
AI response dispatch: after an input is recorded and arc state has
advanced deterministically, ``generate_ai_responses`` composes at most one
AI character reply from the resolved state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Literal
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from engine.session.service import SessionService, _session_service

if TYPE_CHECKING:
    from engine.characters.dialogue import CharacterDialogueEvent


class CharacterNotFoundError(Exception):
    pass


class CharacterAccessError(Exception):
    """Raised when a caller asks for a character they do not own."""


@dataclass(frozen=True)
class CharacterSummary:
    character_id: UUID
    participant_id: UUID
    surface_type: str
    is_ai_controlled: bool


@dataclass(frozen=True)
class CharacterDetail:
    character_id: UUID
    participant_id: UUID
    surface_type: str
    is_ai_controlled: bool


InputKind = Literal["action", "dialogue"]


@dataclass(frozen=True)
class PlayerInputRecord:
    input_id: UUID
    session_id: UUID
    character_id: UUID
    participant_id: UUID
    kind: InputKind
    content: str
    submitted_at: datetime


@dataclass
class CharacterService:
    """Character + player-input service backed by ``session_participants``."""

    sessions: SessionService
    _inputs: dict[UUID, list[PlayerInputRecord]] = field(default_factory=dict)

    async def list_characters(
        self, db: AsyncSession, session_id: UUID
    ) -> list[CharacterSummary]:
        """Return every non-host character participant in ``session_id``."""
        participants = await self.sessions.list_participants(db, session_id)
        return [
            CharacterSummary(
                character_id=p.character_id,
                participant_id=p.participant_id,
                surface_type=p.surface_type,
                is_ai_controlled=p.is_ai_controlled,
            )
            for p in participants
            if p.surface_type != "host"
        ]

    async def get_character_for_player(
        self,
        db: AsyncSession,
        session_id: UUID,
        character_id: UUID,
        requesting_participant_id: UUID,
    ) -> CharacterDetail:
        """Return the character detail for the player who owns it."""
        participant = await self.sessions.find_participant_by_character(
            db, session_id, character_id
        )
        if participant is None:
            raise CharacterNotFoundError(character_id)
        if participant.participant_id != requesting_participant_id:
            raise CharacterAccessError("Player may only access their own character")
        return CharacterDetail(
            character_id=participant.character_id,
            participant_id=participant.participant_id,
            surface_type=participant.surface_type,
            is_ai_controlled=participant.is_ai_controlled,
        )

    async def submit_input(
        self,
        db: AsyncSession,
        session_id: UUID,
        character_id: UUID,
        requesting_participant_id: UUID,
        kind: InputKind,
        content: str,
    ) -> PlayerInputRecord:
        """Record a typed action or dialogue input as the named character."""
        participant = await self.sessions.find_participant_by_character(
            db, session_id, character_id
        )
        if participant is None:
            raise CharacterNotFoundError(character_id)
        if participant.participant_id != requesting_participant_id:
            raise CharacterAccessError(
                "Player may only submit input as their own character"
            )
        record = PlayerInputRecord(
            input_id=uuid4(),
            session_id=session_id,
            character_id=character_id,
            participant_id=participant.participant_id,
            kind=kind,
            content=content,
            submitted_at=datetime.now(tz=timezone.utc),
        )
        self._inputs.setdefault(session_id, []).append(record)
        await self.sessions.advance_live_session_on_input(
            db,
            session_id,
            player_action_count=len(self._inputs[session_id]),
        )
        return record

    def get_inputs(self, session_id: UUID) -> list[PlayerInputRecord]:
        """Return every submitted input for ``session_id`` in arrival order."""
        return list(self._inputs.get(session_id, []))

    async def generate_ai_responses(
        self,
        db: AsyncSession,
        session_id: UUID,
        *,
        speaking_character_id: UUID,
        content: str,
    ) -> list["CharacterDialogueEvent"]:
        """Generate at most one AI character response to a dialogue input.

        Live-loop wiring per spec 0071 (D-072). Deterministic-first: the
        caller has already recorded the input and advanced arc state; this
        composes from resolved state only. Returns [] with zero generation
        calls when the session is not active, the arc is unregistered, or
        no AI-controlled participant other than the speaker exists.

        A KnowledgeConstraintViolation stays engine-internal: the guard did
        its job and no event is returned. Safety-blocked generations return
        the existing neutral-bridge event so the experience is preserved.
        """
        from engine.arc.registry import load_arc_definition
        from engine.characters.dialogue import (
            KnowledgeConstraintViolation,
            generate_character_dialogue,
        )
        from engine.characters.initiative import select_initiative_target
        from engine.session.models import SessionStatus

        session = await self.sessions.get_session(db, session_id)
        if session is None or session.status is not SessionStatus.active:
            return []
        arc_definition = load_arc_definition(session.arc_id)
        if arc_definition is None:
            return []

        participants = await self.sessions.list_participants(db, session_id)
        ai_character_ids = [
            p.character_id
            for p in participants
            if p.is_ai_controlled and p.character_id != speaking_character_id
        ]
        responder_id = select_initiative_target(
            initiating_character_id=speaking_character_id,
            eligible_target_ids=ai_character_ids,
            beat_character_emphasis=None,
            relationships=[],
        )
        if responder_id is None:
            return []

        try:
            event = await generate_character_dialogue(
                db,
                session_id=session_id,
                character_id=responder_id,
                player_input=content,
                quality_tier=session.quality_tier.value,
                current_beat_id=session.current_beat_id,
                content_rails=arc_definition.content_rails,
                authorial_intent=arc_definition.authorial_intent,
            )
        except KnowledgeConstraintViolation:
            return []
        return [event]


_character_service = CharacterService(sessions=_session_service)
