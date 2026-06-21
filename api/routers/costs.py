"""Cost and usage summary endpoints.

Architecture: docs/architecture/13-cost-model.md §13.4.
Route handlers are thin: validate input, call engine function, return response.
No query logic here — aggregation lives in engine/telemetry/costs.py.

Endpoint summary:
  GET /v1/sessions/{session_id}/cost-summary   API key   Per-session totals
  GET /v1/cost-summary?arc_id=                 API key   Arc-level or global totals
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth import ApiCaller, require_api_key
from api.schemas import CostSummaryResponse, PlayerCountCostRow, TaskTypeCostRow
from engine.db import get_async_session
from engine.telemetry.costs import CostSummaryData, get_cost_summary

router = APIRouter(tags=["costs"])


def _to_response(
    data: CostSummaryData,
    *,
    session_id: UUID | None = None,
    arc_id: str | None = None,
) -> CostSummaryResponse:
    return CostSummaryResponse(
        total_cost_usd=data.total_cost_usd,
        total_input_tokens=data.total_input_tokens,
        total_output_tokens=data.total_output_tokens,
        total_generation_count=data.total_generation_count,
        session_id=session_id,
        arc_id=arc_id,
        by_task_type=[
            TaskTypeCostRow(
                task_type=r.task_type,
                generation_count=r.generation_count,
                input_tokens=r.input_tokens,
                output_tokens=r.output_tokens,
                cost_usd=r.cost_usd,
            )
            for r in data.by_task_type
        ],
        by_player_count=[
            PlayerCountCostRow(
                player_count=r.player_count,
                session_count=r.session_count,
                generation_count=r.generation_count,
                cost_usd=r.cost_usd,
            )
            for r in data.by_player_count
        ],
    )


@router.get("/sessions/{session_id}/cost-summary", response_model=CostSummaryResponse)
async def get_session_cost_summary(
    session_id: UUID,
    caller: ApiCaller = Depends(require_api_key),
    db: AsyncSession = Depends(get_async_session),
) -> CostSummaryResponse:
    """Return cost and usage totals for a single session."""
    data = await get_cost_summary(db, session_id=session_id)
    return _to_response(data, session_id=session_id)


@router.get("/cost-summary", response_model=CostSummaryResponse)
async def get_arc_or_global_cost_summary(
    arc_id: str | None = Query(
        default=None, description="Filter to sessions with this arc definition"
    ),
    caller: ApiCaller = Depends(require_api_key),
    db: AsyncSession = Depends(get_async_session),
) -> CostSummaryResponse:
    """Return cost and usage totals grouped by arc or globally.

    Pass ?arc_id= to filter to sessions sharing that arc definition.
    Omit arc_id for a global aggregate over all sessions.
    """
    data = await get_cost_summary(db, arc_id=arc_id)
    return _to_response(data, arc_id=arc_id)
