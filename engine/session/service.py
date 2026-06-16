"""Session lifecycle service — in-memory store for single-process MVP.

Architecture: docs/architecture/09-developer-api.md §9.2.
Persistence (Postgres) is a later M3 task; swap this module then.
"""

from __future__ import annotations

import secrets
from datetime import datetime, timezone
from uuid import UUID, uuid4

from engine.session.models import (
    QualityTier,
    Session,
    SessionParticipant,
    SessionStatus,
)


class SessionNotFoundError(Exception):
    pass


class SessionStateError(Exception):
    pass


class SessionCapacityError(Exception):
    pass


class SessionService:
    """In-process session registry for single-process MVP deployment."""

    def __init__(self) -> None:
        self._sessions: dict[UUID, Session] = {}
        self._participants: dict[UUID, list[SessionParticipant]] = {}
        # join_token → (session_id, participant_id)
        self._join_token_index: dict[str, tuple[UUID, UUID]] = {}

    def create_session(
        self,
        arc_id: str,
        host_account_id: UUID,
        quality_tier: QualityTier = QualityTier.standard,
    ) -> tuple[Session, str]:
        """Create a new session and return (session, host_join_token).

        The host_join_token is passed to GET /sessions/{id}/join to obtain
        a Firebase custom token for the host surface.
        """
        session_id = uuid4()
        host_join_token = secrets.token_urlsafe(32)
        session = Session(
            session_id=session_id,
            arc_id=arc_id,
            status=SessionStatus.created,
            host_account_id=host_account_id,
            created_at=datetime.now(tz=timezone.utc),
            current_beat_id="arrival",
            quality_tier=quality_tier,
            player_count=0,
        )
        self._sessions[session_id] = session
        self._participants[session_id] = []
        host_participant = SessionParticipant(
            participant_id=uuid4(),
            session_id=session_id,
            character_id=uuid4(),  # placeholder; real assignment is arc execution scope
            account_id=host_account_id,
            join_token=host_join_token,
            surface_type="host",
            is_ai_controlled=False,
        )
        self._participants[session_id].append(host_participant)
        self._join_token_index[host_join_token] = (
            session_id,
            host_participant.participant_id,
        )
        return session, host_join_token

    def get_session(self, session_id: UUID) -> Session | None:
        return self._sessions.get(session_id)

    def start_session(self, session_id: UUID, host_account_id: UUID) -> Session:
        session = self._require_session(session_id)
        if session.status is not SessionStatus.created:
            raise SessionStateError(
                f"Cannot start session in status {session.status!r}"
            )
        session.status = SessionStatus.active
        session.started_at = datetime.now(tz=timezone.utc)
        return session

    def pause_session(self, session_id: UUID, host_account_id: UUID) -> Session:
        session = self._require_session(session_id)
        if session.status is not SessionStatus.active:
            raise SessionStateError(
                f"Cannot pause session in status {session.status!r}"
            )
        session.status = SessionStatus.paused
        return session

    def resume_session(self, session_id: UUID, host_account_id: UUID) -> Session:
        session = self._require_session(session_id)
        if session.status is not SessionStatus.paused:
            raise SessionStateError(
                f"Cannot resume session in status {session.status!r}"
            )
        session.status = SessionStatus.active
        return session

    def end_session(self, session_id: UUID, host_account_id: UUID) -> Session:
        session = self._require_session(session_id)
        if session.status in (SessionStatus.completed, SessionStatus.abandoned):
            raise SessionStateError(
                f"Session already ended with status {session.status!r}"
            )
        session.status = SessionStatus.completed
        session.completed_at = datetime.now(tz=timezone.utc)
        return session

    def add_player(
        self,
        session_id: UUID,
        max_players: int = 10,
        surface_type: str = "player",
    ) -> tuple[SessionParticipant, str]:
        """Create a player participant slot and return (participant, join_token).

        The caller distributes ``join_token`` to the player out of band.
        The player presents it to GET /sessions/{id}/join to receive a Firebase token.
        """
        session = self._require_session(session_id)
        if session.status in (SessionStatus.completed, SessionStatus.abandoned):
            raise SessionStateError(
                f"Cannot add player to session in status {session.status!r}"
            )
        if session.player_count >= max_players:
            raise SessionCapacityError(
                f"Session is at capacity ({max_players} players)"
            )
        join_token = secrets.token_urlsafe(32)
        participant = SessionParticipant(
            participant_id=uuid4(),
            session_id=session_id,
            character_id=uuid4(),  # placeholder; real assignment is arc execution scope
            join_token=join_token,
            surface_type=surface_type,
            is_ai_controlled=False,
        )
        self._participants[session_id].append(participant)
        self._join_token_index[join_token] = (session_id, participant.participant_id)
        session.player_count += 1
        return participant, join_token

    def validate_join_token(
        self, session_id: UUID, join_token: str
    ) -> SessionParticipant | None:
        """Return the participant matching ``join_token`` for this session, or None."""
        entry = self._join_token_index.get(join_token)
        if entry is None:
            return None
        token_session_id, participant_id = entry
        if token_session_id != session_id:
            return None
        for p in self._participants.get(session_id, []):
            if p.participant_id == participant_id:
                return p
        return None

    def _require_session(self, session_id: UUID) -> Session:
        session = self._sessions.get(session_id)
        if session is None:
            raise SessionNotFoundError(session_id)
        return session


_session_service = SessionService()
