"""Arc state snapshot persistence — interruption and resume.

Architecture: docs/architecture/05-session-persistence.md §5.2, §5.3, §5.4.

The engine writes a full snapshot row to ``arc_beat_states`` at the
nearest completed beat boundary when a session is paused. On resume the
most recent ``is_current`` row carries the python-statemachine
configuration the engine deserializes back into a fresh
``GeneratedArcStateChart``.

Append-only invariant (§5.2): snapshot rows are never updated in place
once written — the row's ``statemachine_config``, ``transition_history``
and ``snapshot_at`` are write-once. The ``is_current`` flag is a separate
indexed marker explicitly defined by the supplemental schema as
toggled-on-insert: when a newer snapshot is written, the prior row's
``is_current`` is flipped to ``False`` so the active-snapshot lookup
remains a single-row indexed query.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from engine.db.orm import ArcBeatState

if TYPE_CHECKING:
    from engine.arc.arc_state import GeneratedArcStateChart
    from engine.arc.models import ArcDefinition


def capture_chart_config(chart: "GeneratedArcStateChart") -> dict[str, Any]:
    """Return the JSON-serializable snapshot of a chart's runtime state.

    Captures the active configuration (the set of currently-active state
    values per python-statemachine, §5.2) and the chart's ``session_context``
    dict. ``beat_id`` is the single-active beat when present — it is the
    primary key the resume path consults when the chart configuration set
    has exactly one entry (the common Nightcap shape).
    """
    configuration_values = sorted(chart.configuration_values)
    beat_id = configuration_values[0] if len(configuration_values) == 1 else None
    return {
        "beat_id": beat_id,
        "configuration_values": configuration_values,
        "session_context": dict(chart.session_context),
    }


async def write_snapshot(
    db: AsyncSession,
    *,
    session_id: UUID,
    beat_id: str,
    statemachine_config: dict[str, Any],
    transition_history: list[Any] | None = None,
) -> ArcBeatState:
    """Insert a new snapshot at the given beat boundary and demote prior rows.

    Per the supplemental schema, the prior ``is_current`` row(s) have
    their flag flipped to ``False`` so the indexed lookup
    ``(session_id, is_current=True)`` returns exactly one row.
    """
    await db.execute(
        update(ArcBeatState)
        .where(
            ArcBeatState.session_id == session_id,
            ArcBeatState.is_current.is_(True),
        )
        .values(is_current=False)
    )
    snapshot = ArcBeatState(
        session_id=session_id,
        beat_id=beat_id,
        statemachine_config=statemachine_config,
        transition_history=list(transition_history or []),
        is_current=True,
    )
    db.add(snapshot)
    await db.flush()
    return snapshot


async def load_current_snapshot(
    db: AsyncSession, *, session_id: UUID
) -> ArcBeatState | None:
    """Return the active snapshot for ``session_id`` or ``None`` if none exists.

    Backs the resume path. Absence is the documented AC3 exception case
    (§5.3): a paused session with no prior snapshot falls back to starting
    from the arc's first beat.
    """
    result = await db.execute(
        select(ArcBeatState)
        .where(
            ArcBeatState.session_id == session_id,
            ArcBeatState.is_current.is_(True),
        )
        .order_by(ArcBeatState.snapshot_at.desc())
        .limit(1)
    )
    return result.scalars().first()


def restore_chart_from_snapshot(
    arc_definition: "ArcDefinition", snapshot: ArcBeatState
) -> "GeneratedArcStateChart":
    """Rebuild a ``GeneratedArcStateChart`` from a persisted snapshot.

    The chart is constructed with ``start_value`` pointing at the recorded
    beat so python-statemachine's StateChart enters that beat directly
    rather than the arc's initial state. ``session_context`` is restored
    after construction so guard predicates evaluate against the same
    conditions the prior process had accumulated.

    Imported lazily to avoid an ``engine.arc <-> engine.session`` cycle —
    ``engine.arc.models`` already imports from ``engine.session.models``.
    """
    from engine.arc.arc_state import ArcStateChart

    config = dict(snapshot.statemachine_config or {})
    beat_id = config.get("beat_id") or snapshot.beat_id
    chart = ArcStateChart(arc_definition, start_value=beat_id)
    saved_context = config.get("session_context") or {}
    if isinstance(saved_context, dict):
        chart.session_context = dict(saved_context)
    return chart
