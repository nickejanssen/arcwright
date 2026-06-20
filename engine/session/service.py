"""Session lifecycle service — DB-backed.

Architecture: docs/architecture/05-session-persistence.md, §9.2.

Session state lives in Postgres (or SQLite for tests). Each call takes
an ``AsyncSession`` so transactional scope is owned by the caller — the
FastAPI dependency commits per-request, the engine's resume path can
batch multiple writes in one transaction. Nothing in this module holds
in-process session state; cold processes can resume a paused session
purely from the database, which is what AW-220 AC2 requires.

Pause writes an ``arc_beat_states`` snapshot at the current beat
boundary (§5.4 step 4) and records a ``session_interrupted`` event log
entry (§5.4 step 6). Resume reads the most recent ``is_current``
snapshot and rebuilds ``current_beat_id`` from it; the caller is
responsible for materialising the chart via
``engine.session.snapshots.restore_chart_from_snapshot``. When no
snapshot exists the resume falls back to the arc's initial beat — the
documented AC3 exception.
"""

from __future__ import annotations

import secrets
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from engine.db.orm import (
    Account,
    ArcBeatState,
    Event,
)
from engine.db.orm import (
    Session as OrmSession,
)
from engine.db.orm import (
    SessionParticipant as OrmParticipant,
)
from engine.session.models import (
    QualityTier,
    Session,
    SessionParticipant,
    SessionStatus,
)
from engine.session.snapshots import load_current_snapshot, write_snapshot
from engine.telemetry.beats import build_beat_transition_payload
from engine.telemetry.session import (
    build_replay_intent_payload,
    build_session_completed_payload,
)


class SessionNotFoundError(Exception):
    pass


class SessionStateError(Exception):
    pass


class SessionCapacityError(Exception):
    pass


_DEFAULT_INITIAL_BEAT_ID = "arrival"


class SessionService:
    """Stateless facade over the ORM session lifecycle tables.

    Methods are async and take an ``AsyncSession`` parameter; the caller
    owns commit/rollback. The class is kept as a facade (rather than
    module-level functions) so tests can monkeypatch a fresh instance
    into routers, mirroring the AW-217/AW-218 fixture pattern.
    """

    async def create_session(
        self,
        db: AsyncSession,
        *,
        arc_id: str,
        host_account_id: UUID,
        quality_tier: QualityTier = QualityTier.standard,
    ) -> tuple[Session, str]:
        """Create a new session row, a host participant slot, and the host
        ``accounts`` row if it does not already exist.

        Returns ``(session, host_join_token)``. The host token is the same
        out-of-band token format used for player joins (§9.2 GET /join).
        """
        await self._ensure_account_row(db, host_account_id)
        host_join_token = secrets.token_urlsafe(32)
        orm_session = OrmSession(
            session_id=uuid4(),
            arc_id=arc_id,
            status=SessionStatus.created.value,
            host_account_id=host_account_id,
            created_at=datetime.now(tz=timezone.utc),
            current_beat_id=_DEFAULT_INITIAL_BEAT_ID,
            quality_tier=quality_tier.value,
            player_count=0,
        )
        db.add(orm_session)
        await db.flush()
        host_participant = OrmParticipant(
            participant_id=uuid4(),
            session_id=orm_session.session_id,
            character_id=uuid4(),
            account_id=host_account_id,
            join_token=host_join_token,
            surface_type="host",
            is_ai_controlled=False,
        )
        db.add(host_participant)
        await db.flush()
        return _orm_session_to_pydantic(orm_session), host_join_token

    async def get_session(self, db: AsyncSession, session_id: UUID) -> Session | None:
        orm = await db.get(OrmSession, session_id)
        return _orm_session_to_pydantic(orm) if orm is not None else None

    async def start_session(self, db: AsyncSession, session_id: UUID) -> Session:
        orm = await self._require_session(db, session_id)
        if orm.status != SessionStatus.created.value:
            raise SessionStateError(f"Cannot start session in status {orm.status!r}")
        orm.status = SessionStatus.active.value
        orm.started_at = datetime.now(tz=timezone.utc)
        await db.flush()
        return _orm_session_to_pydantic(orm)

    async def pause_session(
        self,
        db: AsyncSession,
        session_id: UUID,
        *,
        beat_id: str | None = None,
        statemachine_config: dict[str, Any] | None = None,
        transition_history: list[Any] | None = None,
    ) -> Session:
        """Pause the arc and snapshot state at the current beat boundary.

        AC1: writes an ``arc_beat_states`` row carrying the statemachine
        configuration (the active state set + ``session_context``) so a
        cold resume can deserialize it.

        ``beat_id`` / ``statemachine_config`` / ``transition_history`` are
        optional. When omitted the session's current ``current_beat_id``
        is used and the chart's runtime context is empty — the right
        default at the HTTP layer where no live chart is held. Engine
        callers that own a live chart should pass
        ``snapshots.capture_chart_config(chart)``.
        """
        orm = await self._require_session(db, session_id)
        if orm.status != SessionStatus.active.value:
            raise SessionStateError(f"Cannot pause session in status {orm.status!r}")
        snapshot_beat = beat_id or orm.current_beat_id
        config = statemachine_config or {
            "beat_id": snapshot_beat,
            "configuration_values": [snapshot_beat],
            "session_context": {},
        }
        await write_snapshot(
            db,
            session_id=session_id,
            beat_id=snapshot_beat,
            statemachine_config=config,
            transition_history=transition_history,
        )
        orm.status = SessionStatus.paused.value
        orm.current_beat_id = snapshot_beat
        db.add(
            Event(
                session_id=session_id,
                event_type="session_interrupted",
                payload={"beat_id": snapshot_beat},
            )
        )
        await db.flush()
        return _orm_session_to_pydantic(orm)

    async def resume_session(
        self, db: AsyncSession, session_id: UUID
    ) -> tuple[Session, ArcBeatState | None]:
        """Resume the arc from the nearest beat snapshot.

        Returns ``(session, snapshot)``. ``snapshot`` is the
        ``arc_beat_states`` row used to seed the resume — the caller
        rebuilds the runtime chart via
        ``snapshots.restore_chart_from_snapshot``. When ``snapshot`` is
        ``None`` the session has no prior state and falls back to the
        arc's initial beat — the documented AC3 exception (§5.3).
        """
        orm = await self._require_session(db, session_id)
        if orm.status != SessionStatus.paused.value:
            raise SessionStateError(f"Cannot resume session in status {orm.status!r}")
        snapshot = await load_current_snapshot(db, session_id=session_id)
        if snapshot is not None:
            orm.current_beat_id = snapshot.beat_id
        # else: no snapshot — current_beat_id stays at its existing value
        # (created_at -> "arrival" default). AC3 exception.
        orm.status = SessionStatus.active.value
        await db.flush()
        return _orm_session_to_pydantic(orm), snapshot

    async def end_session(
        self,
        db: AsyncSession,
        session_id: UUID,
        *,
        completion_type: str = "full_arc",
        killer_identified: bool = False,
    ) -> Session:
        orm = await self._require_session(db, session_id)
        if orm.status in (
            SessionStatus.completed.value,
            SessionStatus.abandoned.value,
        ):
            raise SessionStateError(f"Session already ended with status {orm.status!r}")
        orm.status = SessionStatus.completed.value
        orm.completed_at = datetime.now(tz=timezone.utc)
        await db.flush()
        total_duration_seconds = 0
        if orm.started_at is not None:
            completed_at = orm.completed_at
            started_at = orm.started_at
            # SQLite strips tz info on readback; normalize both sides.
            if started_at.tzinfo is None and completed_at.tzinfo is not None:
                completed_at = completed_at.replace(tzinfo=None)
            total_duration_seconds = int((completed_at - started_at).total_seconds())
        db.add(
            Event(
                session_id=session_id,
                event_type="session_completed",
                payload=build_session_completed_payload(
                    completion_type=completion_type,
                    final_beat_reached=orm.current_beat_id,
                    killer_identified=killer_identified,
                    total_duration_seconds=total_duration_seconds,
                    player_count=orm.player_count,
                ),
            )
        )
        await db.flush()
        return _orm_session_to_pydantic(orm)

    async def record_beat_transition(
        self,
        db: AsyncSession,
        session_id: UUID,
        *,
        from_beat: str,
        to_beat: str,
        duration_seconds: int,
        player_action_count: int,
    ) -> None:
        db.add(
            Event(
                session_id=session_id,
                event_type="beat_transition",
                payload=build_beat_transition_payload(
                    from_beat=from_beat,
                    to_beat=to_beat,
                    duration_seconds=duration_seconds,
                    player_action_count=player_action_count,
                ),
            )
        )
        await db.flush()

    async def write_replay_intent(
        self,
        db: AsyncSession,
        session_id: UUID,
        *,
        intent: str,
        collection_method: str,
    ) -> None:
        db.add(
            Event(
                session_id=session_id,
                event_type="replay_intent",
                payload=build_replay_intent_payload(
                    intent=intent,
                    collection_method=collection_method,
                ),
            )
        )
        await db.flush()

    async def add_player(
        self,
        db: AsyncSession,
        session_id: UUID,
        max_players: int = 10,
        surface_type: str = "player",
    ) -> tuple[SessionParticipant, str]:
        orm = await self._require_session(db, session_id)
        if orm.status in (
            SessionStatus.completed.value,
            SessionStatus.abandoned.value,
        ):
            raise SessionStateError(
                f"Cannot add player to session in status {orm.status!r}"
            )
        if orm.player_count >= max_players:
            raise SessionCapacityError(
                f"Session is at capacity ({max_players} players)"
            )
        join_token = secrets.token_urlsafe(32)
        participant = OrmParticipant(
            participant_id=uuid4(),
            session_id=session_id,
            character_id=uuid4(),
            join_token=join_token,
            surface_type=surface_type,
            is_ai_controlled=False,
        )
        db.add(participant)
        orm.player_count += 1
        await db.flush()
        return _orm_participant_to_pydantic(participant), join_token

    async def list_participants(
        self, db: AsyncSession, session_id: UUID
    ) -> list[SessionParticipant]:
        """Return every participant in ``session_id`` in creation order.

        Backs ``CharacterService.list_characters``. The query orders by
        join token to give a stable ordering across drivers; tests rely
        only on set membership.
        """
        result = await db.execute(
            select(OrmParticipant)
            .where(OrmParticipant.session_id == session_id)
            .order_by(OrmParticipant.join_token)
        )
        return [_orm_participant_to_pydantic(p) for p in result.scalars().all()]

    async def find_participant_by_character(
        self, db: AsyncSession, session_id: UUID, character_id: UUID
    ) -> SessionParticipant | None:
        result = await db.execute(
            select(OrmParticipant).where(
                OrmParticipant.session_id == session_id,
                OrmParticipant.character_id == character_id,
            )
        )
        orm = result.scalars().first()
        return _orm_participant_to_pydantic(orm) if orm is not None else None

    async def validate_join_token(
        self, db: AsyncSession, session_id: UUID, join_token: str
    ) -> SessionParticipant | None:
        result = await db.execute(
            select(OrmParticipant).where(
                OrmParticipant.session_id == session_id,
                OrmParticipant.join_token == join_token,
            )
        )
        orm = result.scalars().first()
        return _orm_participant_to_pydantic(orm) if orm is not None else None

    async def _require_session(self, db: AsyncSession, session_id: UUID) -> OrmSession:
        orm = await db.get(OrmSession, session_id)
        if orm is None:
            raise SessionNotFoundError(session_id)
        return orm

    async def _ensure_account_row(self, db: AsyncSession, account_id: UUID) -> None:
        existing = await db.get(Account, account_id)
        if existing is not None:
            return
        db.add(
            Account(
                account_id=account_id,
                firebase_uid=f"session-host:{account_id}",
            )
        )
        await db.flush()


def _orm_session_to_pydantic(orm: OrmSession) -> Session:
    return Session(
        session_id=orm.session_id,
        arc_id=orm.arc_id,
        status=SessionStatus(orm.status),
        host_account_id=orm.host_account_id,
        created_at=orm.created_at,
        started_at=orm.started_at,
        completed_at=orm.completed_at,
        current_beat_id=orm.current_beat_id,
        quality_tier=QualityTier(orm.quality_tier),
        player_count=orm.player_count,
    )


def _orm_participant_to_pydantic(orm: OrmParticipant) -> SessionParticipant:
    return SessionParticipant(
        participant_id=orm.participant_id,
        session_id=orm.session_id,
        character_id=orm.character_id,
        account_id=orm.account_id,
        join_token=orm.join_token,
        surface_type=orm.surface_type,
        is_ai_controlled=orm.is_ai_controlled,
    )


_session_service = SessionService()
