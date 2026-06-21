# AW-223: Cost and Usage Summary

**Status**: Approved

**Author**: Claude Code | **Date**: 2026-06-21

---

# References

- Architecture: `docs/architecture/13-cost-model.md` §13.4 (three levels of cost visibility)
- Architecture: `docs/architecture/09-developer-api.md` §9.2 (thin-route pattern)
- ORM: `engine/db/orm.py` — `GenerationLog` (line 547), `Session` (line 414)
- Logging: `engine/routing/logging.py` — `log_generation` (always writes cost_usd and tokens)
- ADR: `docs/decisions/0001-scaffolding-audit.md`
- Related spec: `docs/specs/0045-aw-222-five-mvp-telemetry-signals.md`
- GitHub issue: #76

---

# Overview

Add a cost and usage summary query layer (`engine/telemetry/costs.py`) and a thin API
endpoint (`GET /v1/cost-summary`) that exposes aggregated values from `generation_logs`.
Supports grouping by session, arc, task type, and player count. No pricing-model fields
are returned — only actual values logged at generation time.

---

# In Scope

- `engine/telemetry/costs.py`: pure async SQLAlchemy query functions
- `api/schemas/__init__.py`: `TaskTypeCostRow`, `PlayerCountCostRow`, `CostSummaryResponse`
- `api/routers/costs.py`: thin `GET /v1/cost-summary` endpoint
- `api/main.py`: register the new `costs` router
- `engine/tests/test_cost_summary.py`: unit tests using `make_sqlite_session_factory`

---

# Out of Scope

- Revenue, margin, or pricing fields of any kind
- Routing-table efficiency analysis (§13.4 level 3 — no spec for it yet)
- New database schema or migrations
- Changes to `generation_logs` or `sessions` table structure
- Per-beat or per-character cost breakdown

---

# Query Signatures

All functions live in `engine/telemetry/costs.py` and accept an `AsyncSession` as their
first argument. No route logic, no HTTP types.

```python
from decimal import Decimal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession


async def get_cost_summary(
    db: AsyncSession,
    *,
    session_id: UUID | None = None,
    arc_id: str | None = None,
) -> "CostSummaryData":
    """Return aggregated cost and usage totals from generation_logs.

    Filters by session_id if provided, by arc_id if provided (joining to sessions),
    or returns a global aggregate if neither is supplied.
    Always includes a by_task_type breakdown.
    Includes a by_player_count breakdown when arc_id is provided or neither filter
    is provided (because player_count requires joining to sessions).
    """
```

Internal dataclass returned by the engine function (not a Pydantic model — that lives
in `api/schemas/__init__.py`):

```python
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
    by_task_type: list[TaskTypeCostData]
    by_player_count: list[PlayerCountCostData]
```

---

# API Endpoints

Two routes in a single new file `api/routers/costs.py`, registered with prefix `/v1` in
`api/main.py`. Both use `require_api_key` auth.

## Route 1 — per-session (nested sub-resource)

**Path:** `GET /v1/sessions/{session_id}/cost-summary`
**Auth:** API key
**Path parameters:** `session_id: UUID`

Returns cost and usage for that session only. `session_id` is echoed in the response;
`arc_id` is null.

## Route 2 — arc-level or global

**Path:** `GET /v1/usage`
**Auth:** API key
**Query parameters:**
- `arc_id: str | None = None` — when provided, aggregates across all sessions with
  this arc definition; when omitted, returns a global aggregate over all sessions.

This path aligns with `docs/architecture/09-developer-api.md §9.2` which defines
`GET /v1/usage` as the canonical AI credit consumption endpoint.

`session_id` is null in the response; `arc_id` is echoed when provided.

## Shared response schema (`api/schemas/__init__.py`)

```python
class TaskTypeCostRow(BaseModel):
    task_type: str
    generation_count: int
    input_tokens: int
    output_tokens: int
    cost_usd: Decimal

class PlayerCountCostRow(BaseModel):
    player_count: int
    session_count: int
    generation_count: int
    cost_usd: Decimal

class CostSummaryResponse(BaseModel):
    # AC3: only actual logged values from generation_logs.
    # Pricing fields (revenue, margin, price_per_session, profit) are absent because
    # pricing design is deferred — see docs/architecture/13-cost-model.md §13.5.
    total_cost_usd: Decimal
    total_input_tokens: int
    total_output_tokens: int
    total_generation_count: int
    session_id: UUID | None = None
    arc_id: str | None = None
    by_task_type: list[TaskTypeCostRow]
    by_player_count: list[PlayerCountCostRow]
```

Both breakdowns are always present (never gated behind a query param). At MVP session
sizes (7 task types max) the extra rows are negligible.

**Example response** (Route 1 -- single session):

```json
{
  "total_cost_usd": "0.015400",
  "total_input_tokens": 12000,
  "total_output_tokens": 3000,
  "total_generation_count": 8,
  "session_id": "a1b2c3d4-...",
  "arc_id": null,
  "by_task_type": [
    {
      "task_type": "character_dialogue",
      "generation_count": 5,
      "input_tokens": 8000,
      "output_tokens": 2000,
      "cost_usd": "0.010200"
    },
    {
      "task_type": "safety_classification",
      "generation_count": 3,
      "input_tokens": 4000,
      "output_tokens": 1000,
      "cost_usd": "0.005200"
    }
  ],
  "by_player_count": [
    {
      "player_count": 8,
      "session_count": 1,
      "generation_count": 8,
      "cost_usd": "0.015400"
    }
  ]
}
```

**Grouping logic:**
- `by_task_type`: `GROUP BY generation_logs.task_type`. Applied after any session/arc filter.
- `by_player_count`: `JOIN sessions ON generation_logs.session_id = sessions.session_id`,
  then `GROUP BY sessions.player_count`. Applied after any session/arc filter.

---

# AC3 Constraint (Concrete)

The `CostSummaryResponse` schema must NOT contain any field named:
`revenue`, `margin`, `price`, `profit`, or any derivative of these.

The response reflects only what `log_generation` writes: `cost_usd`, `input_tokens`,
`output_tokens`, and `COUNT(*)` as `generation_count`. The docstring in the schema
class explains why pricing fields are absent (pricing is a deferred product decision
per `docs/architecture/13-cost-model.md §13.5`).

---

# Write Sites

| Concern | File |
|---|---|
| SQL aggregation functions | `engine/telemetry/costs.py` (new) |
| Pydantic response schemas | `api/schemas/__init__.py` (append) |
| HTTP GET endpoints (both routes) | `api/routers/costs.py` (new) |
| Router registration | `api/main.py` |
| Unit tests | `engine/tests/test_cost_summary.py` (new) |

---

# Acceptance Criteria

- [ ] **AC1**: `GET /v1/sessions/{session_id}/cost-summary` returns `total_cost_usd` equal to
  the sum of `cost_usd` across all `generation_logs` rows for that session.
- [ ] **AC2**: The response includes `by_task_type` (grouped by `task_type`) and
  `by_player_count` (grouped by `sessions.player_count`). Filtering by `arc_id`
  aggregates across all sessions that share that `arc_id`.
- [ ] **AC3**: `CostSummaryResponse` contains no field named `revenue`, `margin`,
  `price`, or `profit`. The schema comment documents why pricing fields are absent.

---

# Test Plan

File: `engine/tests/test_cost_summary.py`

Uses `make_sqlite_session_factory()` (same pattern as `test_telemetry_signals.py`).
Direct ORM inserts of `Session` and `GenerationLog` rows — does not call
`log_generation` (avoids routing layer dependency in unit tests).

Test cases:
1. **AC1 total cost:** Insert two `GenerationLog` rows with known `cost_usd`. Assert
   `get_cost_summary(db, session_id=...)` returns `total_cost_usd == sum`.
2. **AC2 task-type grouping:** Insert rows with two different `task_type` values. Assert
   `by_task_type` splits them correctly with correct per-type sums.
3. **AC2 player-count grouping:** Insert two sessions with different `player_count`
   values, each with one log row. Assert `by_player_count` has two rows with the
   correct sums.
4. **AC2 arc-id filter:** Insert sessions with two different `arc_id` values. Assert
   filtering by one `arc_id` excludes the other's logs.
5. **AC3 schema guard:** Assert that `CostSummaryResponse.model_fields` contains none
   of `{"revenue", "margin", "price", "profit"}`.

Numerical comparisons use `pytest.approx()`. All async tests use `@pytest.mark.asyncio`.

---

# Risks and Unknowns

**Risks:**
- SQLite stores `Numeric(10,6)` as float, so `pytest.approx()` is required for all
  `cost_usd` assertions (same issue as AW-222).
- `player_count` join requires `Session` rows to exist; FK is not enforced in SQLite by
  default, but we insert real `Session` rows to avoid that ambiguity.

**Unknowns:**
- None. All required columns exist in the current schema.

---

# Open Questions

None — all decisions resolved from ORM + architecture docs before writing this spec.
