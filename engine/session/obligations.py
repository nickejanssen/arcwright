"""Narrative obligations lifecycle (AW-271, spec 0065, ADR-0012).

Obligations are durable session state recording narrative debts the
session owes the players: authored setups that promise payoff, and
pacing-engine misdirection injections that must be acknowledged before
the arc's resolution beat. Only deterministic engine paths mutate
obligation state; AI output never creates or resolves one.

The reveal-readiness signal ``all_mandatory_obligations_resolved`` is a
generic session-context key. Arcs reference it in ``exit_conditions``
exactly like any other condition key (architecture 03 §3.2); the engine
computes its value but never interprets beat ids or obligation names.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from engine.db.orm import Obligation
from engine.telemetry.obligations import (
    record_obligation_created,
    record_obligation_resolved,
)

if TYPE_CHECKING:
    from engine.arc.models import ArcDefinition
    from engine.arc.pacing import PacingIntervention

REVEAL_READINESS_CONTEXT_KEY = "all_mandatory_obligations_resolved"

OBLIGATION_STATUS_OPEN = "open"
OBLIGATION_STATUS_RESOLVED = "resolved"
OBLIGATION_STATUS_EXPIRED = "expired"

SOURCE_TYPE_AUTHORED = "authored"
SOURCE_TYPE_PACING_MISDIRECTION = "pacing_misdirection"


async def register_authored_obligations(
    db: AsyncSession,
    session_id: UUID,
    arc_definition: "ArcDefinition",
    *,
    created_beat: str,
) -> list[Obligation]:
    """Create one obligation row per authored ``obligations`` config entry.

    Called once at session start. Idempotent per session: if authored
    obligations already exist for the session, nothing new is created.
    """
    if not arc_definition.obligations:
        return []

    existing = await db.execute(
        select(Obligation.source_ref).where(
            Obligation.session_id == session_id,
            Obligation.source_type == SOURCE_TYPE_AUTHORED,
        )
    )
    existing_keys = {ref.get("obligation_key") for (ref,) in existing.all()}

    created: list[Obligation] = []
    for config in arc_definition.obligations:
        if config.obligation_key in existing_keys:
            continue
        obligation = Obligation(
            obligation_id=uuid4(),
            session_id=session_id,
            source_type=SOURCE_TYPE_AUTHORED,
            source_ref={
                "obligation_key": config.obligation_key,
                "resolve_on_beat_entry": config.resolve_on_beat_entry,
            },
            description=config.description,
            mandatory=config.mandatory,
            status=OBLIGATION_STATUS_OPEN,
            created_beat=created_beat,
            created_at=datetime.now(tz=timezone.utc),
        )
        db.add(obligation)
        await db.flush()
        await record_obligation_created(db, session_id, obligation)
        created.append(obligation)
    return created


async def create_misdirection_obligation(
    db: AsyncSession,
    session_id: UUID,
    intervention: "PacingIntervention",
    *,
    mandatory: bool,
) -> Obligation:
    """Record the narrative debt created by a pacing misdirection injection.

    ADR-0012: every generative red herring must exist as deterministic
    state so it can be acknowledged or resolved before the resolution
    beat instead of dangling.
    """
    obligation = Obligation(
        obligation_id=uuid4(),
        session_id=session_id,
        source_type=SOURCE_TYPE_PACING_MISDIRECTION,
        source_ref={
            "beat_id": intervention.beat_id,
            "tension_score_at_trigger": intervention.tension_score_at_trigger,
        },
        description=(
            "Pacing-injected misdirection requires acknowledgement or "
            "resolution before the arc resolution beat."
        ),
        mandatory=mandatory,
        status=OBLIGATION_STATUS_OPEN,
        created_beat=intervention.beat_id,
        created_at=datetime.now(tz=timezone.utc),
    )
    db.add(obligation)
    await db.flush()
    await record_obligation_created(db, session_id, obligation)
    return obligation


async def resolve_obligation(
    db: AsyncSession,
    obligation: Obligation,
    *,
    resolved_beat: str,
) -> Obligation:
    """Mark one open obligation resolved and emit its telemetry event."""
    if obligation.status != OBLIGATION_STATUS_OPEN:
        return obligation
    now = datetime.now(tz=timezone.utc)
    obligation.status = OBLIGATION_STATUS_RESOLVED
    obligation.resolved_beat = resolved_beat
    obligation.resolved_at = now
    await db.flush()
    created_at = obligation.created_at
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    await record_obligation_resolved(
        db,
        obligation.session_id,
        obligation,
        open_duration_seconds=max(0.0, (now - created_at).total_seconds()),
    )
    return obligation


async def resolve_obligations_on_beat_entry(
    db: AsyncSession,
    session_id: UUID,
    *,
    entered_beat_id: str,
) -> list[Obligation]:
    """Fire the deterministic beat-entry resolution trigger.

    Resolves every open authored obligation whose configured
    ``resolve_on_beat_entry`` matches the beat the session just entered.
    """
    result = await db.execute(
        select(Obligation).where(
            Obligation.session_id == session_id,
            Obligation.status == OBLIGATION_STATUS_OPEN,
            Obligation.source_type == SOURCE_TYPE_AUTHORED,
        )
    )
    resolved: list[Obligation] = []
    for obligation in result.scalars().all():
        if obligation.source_ref.get("resolve_on_beat_entry") == entered_beat_id:
            await resolve_obligation(db, obligation, resolved_beat=entered_beat_id)
            resolved.append(obligation)
    return resolved


async def expire_open_obligations(
    db: AsyncSession, session_id: UUID
) -> list[Obligation]:
    """Expire every remaining open obligation at session completion.

    Spec 0065 open-question default: unresolved obligations are marked
    ``expired`` rather than left dangling, so lifecycle telemetry can
    distinguish payoffs the session delivered from ones it dropped.
    """
    result = await db.execute(
        select(Obligation).where(
            Obligation.session_id == session_id,
            Obligation.status == OBLIGATION_STATUS_OPEN,
        )
    )
    expired: list[Obligation] = []
    for obligation in result.scalars().all():
        obligation.status = OBLIGATION_STATUS_EXPIRED
        expired.append(obligation)
    if expired:
        await db.flush()
    return expired


async def all_mandatory_obligations_resolved(
    db: AsyncSession, session_id: UUID
) -> bool:
    """Compute the reveal-readiness boolean for the session context.

    True when the session has no open mandatory obligations. Sessions
    with no obligations at all are trivially reveal-ready.
    """
    result = await db.execute(
        select(Obligation.obligation_id)
        .where(
            Obligation.session_id == session_id,
            Obligation.status == OBLIGATION_STATUS_OPEN,
            Obligation.mandatory.is_(True),
        )
        .limit(1)
    )
    return result.first() is None
