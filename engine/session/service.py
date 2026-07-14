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

import random
import secrets
import string
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from engine.arc.registry import load_arc_definition
from engine.db.orm import (
    Account,
    ArcBeatState,
    Character,
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

if TYPE_CHECKING:
    from engine.arc.models import ArcDefinition


class SessionNotFoundError(Exception):
    pass


class SessionStateError(Exception):
    pass


class SessionCapacityError(Exception):
    pass


def _generate_join_code() -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=6))


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
        arc_def = load_arc_definition(arc_id)
        if arc_def is None:
            raise SessionStateError(f"Unknown arc: {arc_id!r}")
        initial_beat_id = arc_def.beats[0].beat_id
        await self._ensure_account_row(db, host_account_id)
        host_join_token = secrets.token_urlsafe(32)
        orm_session = OrmSession(
            session_id=uuid4(),
            arc_id=arc_id,
            status=SessionStatus.created.value,
            host_account_id=host_account_id,
            created_at=datetime.now(tz=timezone.utc),
            current_beat_id=initial_beat_id,
            quality_tier=quality_tier.value,
            player_count=0,
            join_code=_generate_join_code(),
        )
        db.add(orm_session)
        await db.flush()
        host_character = Character(behavior_profile={})
        db.add(host_character)
        await db.flush()
        host_participant = OrmParticipant(
            participant_id=uuid4(),
            session_id=orm_session.session_id,
            character_id=host_character.character_id,
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
        arc_definition = load_arc_definition(orm.arc_id)
        if arc_definition is not None:
            from engine.session.obligations import register_authored_obligations

            await register_authored_obligations(
                db,
                session_id,
                arc_definition,
                created_beat=orm.current_beat_id,
            )
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
        # (the initial beat derived from beats[0] at session creation). AC3 exception.
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
        from engine.session.obligations import expire_open_obligations

        # Spec 0065 default: unresolved obligations expire at completion so
        # lifecycle telemetry can distinguish delivered from dropped payoffs.
        await expire_open_obligations(db, session_id)
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

    async def advance_live_session_on_input(
        self,
        db: AsyncSession,
        session_id: UUID,
        *,
        player_action_count: int = 1,
    ) -> Session:
        """Advance arc beat state after validated REST player input.

        The progression is deterministic and service-owned so REST handlers
        stay thin. When the session is not active, or its arc is not in the
        arc registry, the method is a no-op and returns the current session
        state.
        """
        orm = await self._require_session(db, session_id)
        if orm.status != SessionStatus.active.value:
            return _orm_session_to_pydantic(orm)

        arc_definition = load_arc_definition(orm.arc_id)
        if arc_definition is None:
            return _orm_session_to_pydantic(orm)

        from engine.arc.arc_state import ArcStateChart, transition_name_for
        from engine.session.obligations import (
            REVEAL_READINESS_CONTEXT_KEY,
            all_mandatory_obligations_resolved,
            resolve_obligations_on_beat_entry,
        )

        current_beat_id = orm.current_beat_id
        next_beat_id = _next_beat_id(arc_definition, current_beat_id)
        if next_beat_id is None:
            return _orm_session_to_pydantic(orm)

        chart = ArcStateChart(arc_definition, start_value=current_beat_id)
        # Platform-computed context keys carry their real values into the
        # chart; every other authored condition is satisfied by the REST
        # loop's simplified deterministic progression.
        computed_conditions = {
            REVEAL_READINESS_CONTEXT_KEY: await all_mandatory_obligations_resolved(
                db, session_id
            ),
        }
        _satisfy_transition_conditions(
            chart,
            arc_definition,
            current_beat_id,
            next_beat_id,
            computed_conditions=computed_conditions,
        )

        transition_name = transition_name_for(current_beat_id, next_beat_id)
        transition = getattr(chart, transition_name, None)
        if not callable(transition):
            raise SessionStateError(
                f"Transition {transition_name!r} is not available from beat {current_beat_id!r}"
            )
        transition()
        if next_beat_id not in chart.configuration_values:
            # The StateChart ignores events whose guard fails rather than
            # raising. A platform-computed exit condition (e.g. reveal
            # readiness) is not satisfied: the gate holds and the session
            # stays at the current beat. Deterministic no-op, not an error.
            return _orm_session_to_pydantic(orm)

        # Beat exit: summarize realized-versus-intended tension for the beat
        # being left, when the arc author declared a target for it (spec 0064).
        await self._record_intent_fidelity_on_beat_exit(
            db,
            session_id,
            arc_definition=arc_definition,
            exited_beat_id=current_beat_id,
        )

        orm.current_beat_id = next_beat_id
        # Deterministic beat-entry resolution trigger for authored
        # obligations configured with resolve_on_beat_entry (spec 0065).
        await resolve_obligations_on_beat_entry(
            db, session_id, entered_beat_id=next_beat_id
        )
        await self.record_beat_transition(
            db,
            session_id,
            from_beat=current_beat_id,
            to_beat=next_beat_id,
            duration_seconds=max(1, player_action_count),
            player_action_count=player_action_count,
        )
        await self._record_live_pacing_telemetry(
            db,
            session_id,
            arc_definition=arc_definition,
            beat_id=next_beat_id,
            player_action_count=player_action_count,
            player_count=orm.player_count,
        )
        await db.flush()
        return _orm_session_to_pydantic(orm)

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
        character = Character(behavior_profile={})
        db.add(character)
        await db.flush()
        participant = OrmParticipant(
            participant_id=uuid4(),
            session_id=session_id,
            character_id=character.character_id,
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

    async def lobby_join(
        self,
        db: AsyncSession,
        *,
        join_code: str,
        display_name: str,
    ) -> SessionParticipant:
        """Find a session by join_code and add a named player.

        Raises SessionNotFoundError if no session matches the code.
        Raises SessionStateError if the session is in a terminal state.
        """
        result = await db.execute(
            select(OrmSession).where(OrmSession.join_code == join_code)
        )
        orm = result.scalars().first()
        if orm is None:
            raise SessionNotFoundError(f"No session with join_code {join_code!r}")
        if orm.status in (
            SessionStatus.completed.value,
            SessionStatus.abandoned.value,
        ):
            raise SessionStateError(f"Cannot join session in status {orm.status!r}")

        character = Character(behavior_profile={})
        db.add(character)
        await db.flush()

        participant = OrmParticipant(
            participant_id=uuid4(),
            session_id=orm.session_id,
            character_id=character.character_id,
            join_token=secrets.token_urlsafe(32),
            surface_type="player",
            is_ai_controlled=False,
            display_name=display_name,
        )
        db.add(participant)
        orm.player_count += 1
        await db.flush()
        return _orm_participant_to_pydantic(participant)

    async def ensure_account_for_firebase_uid(
        self, db: AsyncSession, *, firebase_uid: str, email: str | None = None
    ) -> UUID:
        """Look up or create the stable ``accounts`` row for a Firebase identity.

        Authenticated hosts reuse the same ``account_id`` across every
        session they create instead of minting a fresh anonymous host
        identity per session (AW-269 host identity bridge). Unlike
        ``_ensure_account_row`` (keyed by ``account_id`` for the
        developer API-key path), this looks up by the unique
        ``firebase_uid`` column first.
        """
        result = await db.execute(
            select(Account).where(Account.firebase_uid == firebase_uid)
        )
        existing = result.scalars().first()
        if existing is not None:
            return existing.account_id
        account = Account(account_id=uuid4(), firebase_uid=firebase_uid, email=email)
        db.add(account)
        await db.flush()
        return account.account_id

    async def _require_session(self, db: AsyncSession, session_id: UUID) -> OrmSession:
        orm = await db.get(OrmSession, session_id)
        if orm is None:
            raise SessionNotFoundError(session_id)
        return orm

    async def _record_intent_fidelity_on_beat_exit(
        self,
        db: AsyncSession,
        session_id: UUID,
        *,
        arc_definition: ArcDefinition,
        exited_beat_id: str,
    ) -> None:
        intent = arc_definition.authorial_intent
        if intent is None:
            return
        target_score = intent.target_tension_for(exited_beat_id)
        if target_score is None:
            return
        from engine.telemetry.pacing import record_intent_fidelity_summary

        result = await db.execute(
            select(Event).where(
                Event.session_id == session_id,
                Event.event_type == "tension_update",
            )
        )
        scores = [
            row.payload["score"]
            for row in result.scalars()
            if row.payload.get("beat_id") == exited_beat_id
        ]
        await record_intent_fidelity_summary(
            db,
            session_id,
            beat_id=exited_beat_id,
            target_score=target_score,
            scores=scores,
        )

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

    async def _record_live_pacing_telemetry(
        self,
        db: AsyncSession,
        session_id: UUID,
        *,
        arc_definition: ArcDefinition,
        beat_id: str,
        player_action_count: int,
        player_count: int,
    ) -> None:
        snapshot = _build_live_pacing_snapshot(
            arc_definition,
            beat_id=beat_id,
            player_action_count=player_action_count,
            player_count=player_count,
        )
        from engine.arc.pacing import (
            compute_dramatic_tension_score,
            evaluate_pacing_interventions,
        )
        from engine.telemetry.pacing import (
            record_pacing_intervention,
            record_pacing_intervention_outcome,
            record_tension_update,
        )

        target_score = (
            arc_definition.authorial_intent.target_tension_for(beat_id)
            if arc_definition.authorial_intent is not None
            else None
        )
        score = compute_dramatic_tension_score(snapshot, arc_definition.pacing_config)
        await record_tension_update(
            db, session_id, score=score, beat_id=beat_id, target_score=target_score
        )

        from engine.arc.pacing import PacingInterventionType
        from engine.session.obligations import create_misdirection_obligation

        interventions = evaluate_pacing_interventions(
            snapshot,
            arc_definition.pacing_config,
        )
        for intervention in interventions:
            await record_pacing_intervention(db, session_id, intervention)
            if intervention.intervention_type is PacingInterventionType.misdirection:
                # ADR-0012: every misdirection injection becomes durable
                # obligation state so it cannot dangle unacknowledged.
                await create_misdirection_obligation(
                    db,
                    session_id,
                    intervention,
                    mandatory=(
                        arc_definition.pacing_config.misdirection_obligation_mandatory
                    ),
                )
            await record_pacing_intervention_outcome(
                db,
                session_id,
                intervention,
                outcome_resumed_within_60s=True,
            )


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
        join_code=orm.join_code,
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


def _next_beat_id(arc_definition: ArcDefinition, current_beat_id: str) -> str | None:
    if current_beat_id not in arc_definition.beat_graph:
        raise SessionStateError(f"Unknown beat {current_beat_id!r}")
    targets = arc_definition.beat_graph[current_beat_id]
    if not targets:
        return None
    return targets[0]


def _satisfy_transition_conditions(
    chart: Any,
    arc_definition: ArcDefinition,
    source_beat_id: str,
    target_beat_id: str,
    *,
    computed_conditions: dict[str, bool] | None = None,
) -> None:
    """Seed chart context for the REST loop's simplified progression.

    Authored conditions are satisfied unconditionally (the REST loop owns
    deterministic advancement); platform-computed keys supplied via
    ``computed_conditions`` carry their real values so they can gate the
    transition.
    """
    computed = computed_conditions or {}
    beats_by_id = {beat.beat_id: beat for beat in arc_definition.beats}
    source_beat = beats_by_id[source_beat_id]
    target_beat = beats_by_id[target_beat_id]
    for condition in {
        *source_beat.exit_conditions,
        *target_beat.entry_conditions,
    }:
        chart.update_context(condition, computed.get(condition, True))


def _build_live_pacing_snapshot(
    arc_definition: ArcDefinition,
    *,
    beat_id: str,
    player_action_count: int,
    player_count: int,
) -> Any:
    from engine.arc.pacing import PacingSignalSnapshot

    beat_index = next(
        index
        for index, beat in enumerate(arc_definition.beats)
        if beat.beat_id == beat_id
    )
    total_beats = max(1, len(arc_definition.beats) - 1)
    time_pressure = min(1.0, beat_index / total_beats)
    action_rate = min(1.0, player_action_count / max(1, player_count))
    suspicion = min(1.0, 0.2 + (beat_index / max(1, len(arc_definition.beats))) * 0.6)
    clue_coverage = min(1.0, (beat_index + 1) / max(1, len(arc_definition.beats)))
    return PacingSignalSnapshot(
        beat_id=beat_id,
        time_pressure=time_pressure,
        action_rate=action_rate,
        suspicion=suspicion,
        clue_coverage=clue_coverage,
    )


_session_service = SessionService()
