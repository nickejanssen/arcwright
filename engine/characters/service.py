"""Character service — DB-backed participant lookups, in-memory input log.

Architecture: docs/architecture/09-developer-api.md §9.2.

Participant existence and ownership are resolved against
``session_participants`` (the same source of truth used by
``SessionService``) so the service stays consistent across cold process
restarts. Player-submitted ``action`` / ``dialogue`` inputs are still
held in-memory — that surface has no AC2 resume requirement and a
dedicated events-table representation is the AW-222 telemetry scope.

LLM dispatch is intentionally out of scope here — this layer captures
the authored, deterministic side of the unified character model.
Generation is called separately by the arc execution layer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from engine.session.service import SessionService, _session_service


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


_character_service = CharacterService(sessions=_session_service)
