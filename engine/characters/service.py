"""Character service — in-memory store for single-process MVP.

Architecture: docs/architecture/09-developer-api.md §9.2.

Mirrors the in-memory pattern of ``engine.session.service`` (AW-217).
Postgres persistence is a later M3 task; swap this module then.

The service answers three classes of question against the SessionService
participant store:
  - list every character in a session (no private knowledge state)
  - return the character detail a single player is authorised to see
  - record a typed player action or dialogue input against a character

LLM dispatch is intentionally out of scope here — this layer captures the
authored, deterministic side of the unified character model. Generation is
called separately by the arc execution layer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal
from uuid import UUID, uuid4

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
    """In-process character + player-input registry."""

    sessions: SessionService
    _inputs: dict[UUID, list[PlayerInputRecord]] = field(default_factory=dict)

    def list_characters(self, session_id: UUID) -> list[CharacterSummary]:
        """Return every non-host character participant in ``session_id``.

        Host participants are excluded — §9.2 describes this list as
        "characters in session," and the host is not a character.
        """
        participants = self.sessions._participants.get(session_id, [])
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

    def get_character_for_player(
        self,
        session_id: UUID,
        character_id: UUID,
        requesting_participant_id: UUID,
    ) -> CharacterDetail:
        """Return the character detail for the player who owns it.

        Raises ``CharacterNotFoundError`` if the character is not in the session.
        Raises ``CharacterAccessError`` if the requesting participant does not
        own that character.
        """
        participant = self._find_participant_by_character(session_id, character_id)
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

    def submit_input(
        self,
        session_id: UUID,
        character_id: UUID,
        requesting_participant_id: UUID,
        kind: InputKind,
        content: str,
    ) -> PlayerInputRecord:
        """Record a typed action or dialogue input as the named character."""
        participant = self._find_participant_by_character(session_id, character_id)
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
        return record

    def get_inputs(self, session_id: UUID) -> list[PlayerInputRecord]:
        """Return every submitted input for ``session_id`` in arrival order."""
        return list(self._inputs.get(session_id, []))

    def _find_participant_by_character(self, session_id: UUID, character_id: UUID):  # type: ignore[no-untyped-def]
        for p in self.sessions._participants.get(session_id, []):
            if p.character_id == character_id:
                return p
        return None


_character_service = CharacterService(sessions=_session_service)
