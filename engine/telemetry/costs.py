"""Cost and usage aggregation queries over generation_logs.

Architecture: docs/architecture/13-cost-model.md §13.4.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from uuid import UUID

from sqlalchemy import distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from engine.db.orm import GenerationLog
from engine.db.orm import Session as OrmSession


@dataclass
class TaskTypeCostData:
    task_type: str
    generation_count: int
    input_tokens: int
    output_tokens: int
    cost_usd: Decimal


@dataclass
class PlayerCountCostData:
    player_count: int
    session_count: int
    generation_count: int
    cost_usd: Decimal


@dataclass
class CostSummaryData:
    total_cost_usd: Decimal
    total_input_tokens: int
    total_output_tokens: int
    total_generation_count: int
    by_task_type: list[TaskTypeCostData] = field(default_factory=list)
    by_player_count: list[PlayerCountCostData] = field(default_factory=list)


async def get_cost_summary(
    db: AsyncSession,
    *,
    session_id: UUID | None = None,
    arc_id: str | None = None,
) -> CostSummaryData:
    """Return aggregated cost and usage totals from generation_logs.

    Filters by session_id when provided, by arc_id when provided (joining to
    sessions), or aggregates globally when neither is supplied.
    """
    totals_q = select(
        func.sum(GenerationLog.cost_usd).label("total_cost_usd"),
        func.sum(GenerationLog.input_tokens).label("total_input_tokens"),
        func.sum(GenerationLog.output_tokens).label("total_output_tokens"),
        func.count().label("total_generation_count"),
    )
    task_q = select(
        GenerationLog.task_type,
        func.count().label("generation_count"),
        func.sum(GenerationLog.input_tokens).label("input_tokens"),
        func.sum(GenerationLog.output_tokens).label("output_tokens"),
        func.sum(GenerationLog.cost_usd).label("cost_usd"),
    ).group_by(GenerationLog.task_type)
    player_q = (
        select(
            OrmSession.player_count,
            func.count(distinct(GenerationLog.session_id)).label("session_count"),
            func.count().label("generation_count"),
            func.sum(GenerationLog.cost_usd).label("cost_usd"),
        )
        .join(OrmSession, GenerationLog.session_id == OrmSession.session_id)
        .group_by(OrmSession.player_count)
    )

    if session_id is not None:
        totals_q = totals_q.where(GenerationLog.session_id == session_id)
        task_q = task_q.where(GenerationLog.session_id == session_id)
        player_q = player_q.where(GenerationLog.session_id == session_id)
    elif arc_id is not None:
        totals_q = totals_q.join(
            OrmSession, GenerationLog.session_id == OrmSession.session_id
        ).where(OrmSession.arc_id == arc_id)
        task_q = task_q.join(
            OrmSession, GenerationLog.session_id == OrmSession.session_id
        ).where(OrmSession.arc_id == arc_id)
        player_q = player_q.where(OrmSession.arc_id == arc_id)

    totals_row = (await db.execute(totals_q)).one()
    task_rows = (await db.execute(task_q)).all()
    player_rows = (await db.execute(player_q)).all()

    return CostSummaryData(
        total_cost_usd=totals_row.total_cost_usd or Decimal("0"),
        total_input_tokens=totals_row.total_input_tokens or 0,
        total_output_tokens=totals_row.total_output_tokens or 0,
        total_generation_count=totals_row.total_generation_count or 0,
        by_task_type=[
            TaskTypeCostData(
                task_type=r.task_type,
                generation_count=r.generation_count,
                input_tokens=r.input_tokens,
                output_tokens=r.output_tokens,
                cost_usd=r.cost_usd,
            )
            for r in task_rows
        ],
        by_player_count=[
            PlayerCountCostData(
                player_count=r.player_count,
                session_count=r.session_count,
                generation_count=r.generation_count,
                cost_usd=r.cost_usd,
            )
            for r in player_rows
        ],
    )
