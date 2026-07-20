"""SQLAlchemy ORM models for Arcwright platform tables."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Optional
from uuid import UUID

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(AsyncAttrs, DeclarativeBase):
    """Declarative base for Arcwright ORM models."""


class Account(Base):
    __tablename__ = "accounts"

    account_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    firebase_uid: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    email: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    display_name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
    last_seen_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    hosted_sessions: Mapped[list[Session]] = relationship(
        back_populates="host_account",
        foreign_keys="Session.host_account_id",
    )
    consent_records: Mapped[list[ConsentRecord]] = relationship(
        back_populates="account"
    )
    session_participants: Mapped[list[SessionParticipant]] = relationship(
        back_populates="account"
    )


class ConsentRecord(Base):
    __tablename__ = "consent_records"

    consent_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    account_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("accounts.account_id"),
        nullable=True,
    )
    session_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("sessions.session_id"),
        nullable=True,
    )
    consent_type: Mapped[str] = mapped_column(Text, nullable=False)
    granted: Mapped[bool] = mapped_column(Boolean, nullable=False)
    granted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
    revoked_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    consent_version: Mapped[str] = mapped_column(Text, nullable=False)

    account: Mapped[Optional[Account]] = relationship(back_populates="consent_records")
    session: Mapped[Optional[Session]] = relationship(back_populates="consent_records")


class Character(Base):
    __tablename__ = "characters"

    character_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    behavior_profile: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb"),
    )
    embedding: Mapped[Optional[Any]] = mapped_column(Vector(1536), nullable=True)

    knowledge_states: Mapped[list[KnowledgeState]] = relationship(
        back_populates="character",
        foreign_keys="KnowledgeState.character_id",
    )
    sourced_knowledge_states: Mapped[list[KnowledgeState]] = relationship(
        back_populates="source_character",
        foreign_keys="KnowledgeState.source_character_id",
    )
    outgoing_relationships: Mapped[list[RelationshipState]] = relationship(
        back_populates="source_character",
        foreign_keys="RelationshipState.source_char_id",
    )
    incoming_relationships: Mapped[list[RelationshipState]] = relationship(
        back_populates="target_character",
        foreign_keys="RelationshipState.target_char_id",
    )
    session_participants: Mapped[list[SessionParticipant]] = relationship(
        back_populates="character"
    )
    events: Mapped[list[Event]] = relationship(back_populates="actor_character")


class Fact(Base):
    __tablename__ = "facts"

    fact_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    session_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("sessions.session_id"),
        nullable=False,
    )
    fact_type: Mapped[str] = mapped_column(Text, nullable=False)
    fact_content: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    embedding: Mapped[Optional[Any]] = mapped_column(Vector(1536), nullable=True)

    session: Mapped[Session] = relationship(back_populates="facts")
    knowledge_states: Mapped[list[KnowledgeState]] = relationship(back_populates="fact")


class KnowledgeState(Base):
    __tablename__ = "knowledge_states"

    ks_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    session_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("sessions.session_id"),
        nullable=False,
    )
    character_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("characters.character_id"),
        nullable=False,
    )
    fact_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("facts.fact_id"),
        nullable=False,
    )
    source_character_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("characters.character_id"),
        nullable=True,
    )
    confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        server_default=text("1.0"),
    )
    provenance_chain: Mapped[list[Any]] = mapped_column(
        JSONB,
        nullable=False,
        server_default=text("'[]'::jsonb"),
    )
    asserted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    superseded_by: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("knowledge_states.ks_id", use_alter=True),
        nullable=True,
    )

    session: Mapped[Session] = relationship(back_populates="knowledge_states")
    character: Mapped[Character] = relationship(
        back_populates="knowledge_states",
        foreign_keys=[character_id],
    )
    fact: Mapped[Fact] = relationship(back_populates="knowledge_states")
    source_character: Mapped[Optional[Character]] = relationship(
        back_populates="sourced_knowledge_states",
        foreign_keys=[source_character_id],
    )
    superseded_by_record: Mapped[Optional[KnowledgeState]] = relationship(
        back_populates="supersedes_records",
        remote_side=[ks_id],
        foreign_keys=[superseded_by],
    )
    supersedes_records: Mapped[list[KnowledgeState]] = relationship(
        back_populates="superseded_by_record"
    )


class RelationshipState(Base):
    __tablename__ = "relationships"
    __table_args__ = (
        UniqueConstraint(
            "session_id",
            "source_char_id",
            "target_char_id",
            name="uq_relationships_session_source_target",
        ),
    )

    relationship_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    session_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("sessions.session_id"),
        nullable=False,
    )
    source_char_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("characters.character_id"),
        nullable=False,
    )
    target_char_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("characters.character_id"),
        nullable=False,
    )
    trust_level: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        server_default=text("0.5"),
    )
    history_tag: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    current_affect: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    session: Mapped[Session] = relationship(back_populates="relationships")
    source_character: Mapped[Character] = relationship(
        back_populates="outgoing_relationships",
        foreign_keys=[source_char_id],
    )
    target_character: Mapped[Character] = relationship(
        back_populates="incoming_relationships",
        foreign_keys=[target_char_id],
    )


class Location(Base):
    __tablename__ = "locations"

    location_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    session_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("sessions.session_id"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb"),
    )

    session: Mapped[Session] = relationship(back_populates="locations")
    objects: Mapped[list[Object]] = relationship(back_populates="location")


class Object(Base):
    __tablename__ = "objects"

    object_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    session_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("sessions.session_id"),
        nullable=False,
    )
    location_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("locations.location_id"),
        nullable=True,
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb"),
    )

    session: Mapped[Session] = relationship(back_populates="objects")
    location: Mapped[Optional[Location]] = relationship(back_populates="objects")


class Decision(Base):
    __tablename__ = "decisions"

    decision_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    session_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("sessions.session_id"),
        nullable=False,
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
    decision_type: Mapped[str] = mapped_column(Text, nullable=False)
    context: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb"),
    )
    outcome: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb"),
    )

    session: Mapped[Session] = relationship(back_populates="decisions")


class Event(Base):
    __tablename__ = "events"
    __table_args__ = (
        Index("ix_events_session_id_timestamp", "session_id", "timestamp"),
        Index("ix_events_event_type_timestamp", "event_type", "timestamp"),
    )

    event_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    session_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("sessions.session_id"),
        nullable=False,
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
    actor_char_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("characters.character_id"),
        nullable=True,
    )
    event_type: Mapped[str] = mapped_column(Text, nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb"),
    )
    content_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    embedding: Mapped[Optional[Any]] = mapped_column(Vector(1536), nullable=True)

    session: Mapped[Session] = relationship(back_populates="events")
    actor_character: Mapped[Optional[Character]] = relationship(back_populates="events")


class Session(Base):
    __tablename__ = "sessions"

    session_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    arc_id: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    host_account_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("accounts.account_id"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    current_beat_id: Mapped[str] = mapped_column(Text, nullable=False)
    quality_tier: Mapped[str] = mapped_column(Text, nullable=False)
    player_count: Mapped[int] = mapped_column(Integer, nullable=False)
    join_code: Mapped[Optional[str]] = mapped_column(Text, nullable=True, unique=True)

    host_account: Mapped[Account] = relationship(
        back_populates="hosted_sessions",
        foreign_keys=[host_account_id],
    )
    consent_records: Mapped[list[ConsentRecord]] = relationship(
        back_populates="session"
    )
    facts: Mapped[list[Fact]] = relationship(back_populates="session")
    knowledge_states: Mapped[list[KnowledgeState]] = relationship(
        back_populates="session"
    )
    relationships: Mapped[list[RelationshipState]] = relationship(
        back_populates="session"
    )
    locations: Mapped[list[Location]] = relationship(back_populates="session")
    objects: Mapped[list[Object]] = relationship(back_populates="session")
    decisions: Mapped[list[Decision]] = relationship(back_populates="session")
    events: Mapped[list[Event]] = relationship(back_populates="session")
    session_participants: Mapped[list[SessionParticipant]] = relationship(
        back_populates="session"
    )
    arc_beat_states: Mapped[list[ArcBeatState]] = relationship(back_populates="session")
    generation_logs: Mapped[list[GenerationLog]] = relationship(
        back_populates="session"
    )
    decision_logs: Mapped[list[DecisionLog]] = relationship(back_populates="session")
    mini_game_runs: Mapped[list[MiniGameRun]] = relationship(back_populates="session")


class SessionParticipant(Base):
    __tablename__ = "session_participants"

    participant_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    session_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("sessions.session_id"),
        nullable=False,
    )
    character_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("characters.character_id"),
        nullable=False,
    )
    account_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("accounts.account_id"),
        nullable=True,
    )
    join_token: Mapped[str] = mapped_column(Text, nullable=False)
    surface_type: Mapped[str] = mapped_column(Text, nullable=False)
    is_ai_controlled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )
    display_name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    session: Mapped[Session] = relationship(back_populates="session_participants")
    character: Mapped[Character] = relationship(back_populates="session_participants")
    account: Mapped[Optional[Account]] = relationship(
        back_populates="session_participants"
    )


class ArcBeatState(Base):
    __tablename__ = "arc_beat_states"
    __table_args__ = (
        Index("ix_arc_beat_states_session_id_is_current", "session_id", "is_current"),
    )

    state_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    session_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("sessions.session_id"),
        nullable=False,
    )
    beat_id: Mapped[str] = mapped_column(Text, nullable=False)
    statemachine_config: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    transition_history: Mapped[list[Any]] = mapped_column(
        JSONB,
        nullable=False,
        server_default=text("'[]'::jsonb"),
    )
    snapshot_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
    is_current: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
    )

    session: Mapped[Session] = relationship(back_populates="arc_beat_states")


class GenerationLog(Base):
    __tablename__ = "generation_logs"

    log_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    session_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("sessions.session_id"),
        nullable=False,
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
    task_type: Mapped[str] = mapped_column(Text, nullable=False)
    quality_tier: Mapped[str] = mapped_column(Text, nullable=False)
    model_used: Mapped[str] = mapped_column(Text, nullable=False)
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    input_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    output_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    cost_usd: Mapped[Decimal] = mapped_column(Numeric(10, 6), nullable=False)
    tension_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    prompt_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    output_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    prompt_embedding: Mapped[Optional[Any]] = mapped_column(Vector(1536), nullable=True)
    output_embedding: Mapped[Optional[Any]] = mapped_column(Vector(1536), nullable=True)

    session: Mapped[Session] = relationship(back_populates="generation_logs")


class DecisionLog(Base):
    __tablename__ = "decision_logs"

    decision_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    session_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("sessions.session_id"),
        nullable=False,
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
    decision_type: Mapped[str] = mapped_column(Text, nullable=False)
    input_context: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    outcome: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)

    session: Mapped[Session] = relationship(back_populates="decision_logs")


class MiniGameRun(Base):
    __tablename__ = "mini_game_runs"
    __table_args__ = (
        Index("ix_mini_game_runs_session_id_status", "session_id", "status"),
    )

    run_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    session_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("sessions.session_id"),
        nullable=False,
    )
    game_id: Mapped[str] = mapped_column(Text, nullable=False)
    definition_version: Mapped[str] = mapped_column(Text, nullable=False)
    definition_snapshot: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    status: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        server_default=text("'pending'"),
    )
    revision: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0"),
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    deadline: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    paused_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    pause_deadline_remaining_seconds: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    outcome: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    behavioral_outputs: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB, nullable=True
    )
    clue_unlock_record: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb"),
    )

    session: Mapped[Session] = relationship(back_populates="mini_game_runs")
    submissions: Mapped[list[MiniGameSubmission]] = relationship(
        back_populates="run",
        order_by="MiniGameSubmission.submitted_at",
    )


class MiniGameSubmission(Base):
    __tablename__ = "mini_game_submissions"
    __table_args__ = (
        UniqueConstraint(
            "run_id",
            "submission_id",
            name="uq_mini_game_submissions_run_submission",
        ),
    )

    submission_pk: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    run_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("mini_game_runs.run_id"),
        nullable=False,
    )
    submission_id: Mapped[str] = mapped_column(Text, nullable=False)
    character_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("characters.character_id"),
        nullable=False,
    )
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    is_accepted: Mapped[bool] = mapped_column(Boolean, nullable=False)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    scored_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    run: Mapped[MiniGameRun] = relationship(back_populates="submissions")
    character: Mapped[Character] = relationship()


class Obligation(Base):
    """Narrative obligation tracked as durable session state (spec 0065).

    Only deterministic engine paths mutate rows: authored setups register at
    session start, pacing misdirection injection auto-creates one, resolution
    fires on deterministic triggers, and session completion expires the rest.
    """

    __tablename__ = "obligations"
    __table_args__ = (
        Index("ix_obligations_session_id_status", "session_id", "status"),
    )

    obligation_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    session_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("sessions.session_id"),
        nullable=False,
    )
    source_type: Mapped[str] = mapped_column(Text, nullable=False)
    source_ref: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb"),
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    mandatory: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    status: Mapped[str] = mapped_column(
        Text, nullable=False, server_default=text("'open'")
    )
    created_beat: Mapped[str] = mapped_column(Text, nullable=False)
    resolved_beat: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
    resolved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class Claim(Base):
    __tablename__ = "claims"
    __table_args__ = (
        Index("ix_claims_session_id_speaker", "session_id", "speaker_character_id"),
        Index("ix_claims_session_id_beat", "session_id", "beat_id"),
    )

    claim_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    session_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("sessions.session_id"),
        nullable=False,
    )
    speaker_character_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("characters.character_id"),
        nullable=False,
    )
    asker_participant_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("session_participants.participant_id"),
        nullable=True,
    )
    round_index: Mapped[int] = mapped_column(Integer, nullable=False)
    beat_id: Mapped[str] = mapped_column(Text, nullable=False)
    interaction_window_id: Mapped[str] = mapped_column(Text, nullable=False)
    claim_text: Mapped[str] = mapped_column(Text, nullable=False)
    referenced_fact_ids: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        server_default=text("'[]'::jsonb"),
    )
    is_authorized_lie: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )
    falsehood_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )


class ContradictionFlag(Base):
    __tablename__ = "contradiction_flags"
    __table_args__ = (
        Index("ix_contradiction_flags_claim_id", "claim_id"),
        Index("ix_contradiction_flags_session_id", "session_id"),
    )

    flag_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    claim_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("claims.claim_id"),
        nullable=False,
    )
    session_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("sessions.session_id"),
        nullable=False,
    )
    flagged_by_participant_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("session_participants.participant_id"),
        nullable=False,
    )
    outcome: Mapped[str] = mapped_column(Text, nullable=False)
    evidence_id_used: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )


class Accusation(Base):
    __tablename__ = "accusations"
    __table_args__ = (
        Index(
            "ix_accusations_session_id_accuser", "session_id", "accuser_participant_id"
        ),
        Index(
            "ix_accusations_session_id_outcome_submitted_at",
            "session_id",
            "outcome",
            "submitted_at",
        ),
    )

    accusation_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    session_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("sessions.session_id"),
        nullable=False,
    )
    accuser_participant_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("session_participants.participant_id"),
        nullable=False,
    )
    beat_id: Mapped[str] = mapped_column(Text, nullable=False)
    accused_cast_member_id: Mapped[str] = mapped_column(Text, nullable=False)
    motive_correct: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    method_correct: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    outcome: Mapped[str] = mapped_column(Text, nullable=False)
    catches_banked_at_submission: Mapped[int] = mapped_column(Integer, nullable=False)
    points_awarded: Mapped[int] = mapped_column(Integer, nullable=False)
    repeat_offense_count: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    lockout_until: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    used_last_word: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    triggered_last_call: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )


class SuspectLock(Base):
    __tablename__ = "suspect_locks"
    __table_args__ = (
        UniqueConstraint(
            "session_id",
            "participant_id",
            name="uq_suspect_locks_session_participant",
        ),
    )

    suspect_lock_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    session_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("sessions.session_id"),
        nullable=False,
    )
    participant_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("session_participants.participant_id"),
        nullable=False,
    )
    suspect_cast_member_id: Mapped[str] = mapped_column(Text, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
