"""Tests for AW-223: Cost and Usage Summary.

Uses real SQLite in-memory DB via engine.db.testing.make_sqlite_session_factory.
Inserts Session and GenerationLog rows directly — no routing layer dependency.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from engine.db.orm import GenerationLog
from engine.db.orm import Session as OrmSession
from engine.db.testing import make_sqlite_session_factory
from engine.telemetry.costs import get_cost_summary

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture()
async def db_engine_factory() -> AsyncIterator[
    tuple[AsyncEngine, async_sessionmaker[AsyncSession]]
]:
    engine, factory = await make_sqlite_session_factory()
    try:
        yield engine, factory
    finally:
        await engine.dispose()


@pytest_asyncio.fixture()
async def db(
    db_engine_factory: tuple[AsyncEngine, async_sessionmaker[AsyncSession]],
) -> AsyncIterator[AsyncSession]:
    _, factory = db_engine_factory
    async with factory() as session:
        try:
            yield session
        finally:
            await session.rollback()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_session(arc_id: str = "test-arc", player_count: int = 4) -> OrmSession:
    return OrmSession(
        session_id=uuid4(),
        arc_id=arc_id,
        status="created",
        host_account_id=uuid4(),
        created_at=datetime.now(tz=timezone.utc),
        current_beat_id="arrival",
        quality_tier="standard",
        player_count=player_count,
    )


def _make_log(
    session_id: object,
    *,
    task_type: str = "character_dialogue",
    cost_usd: Decimal = Decimal("0.001"),
    input_tokens: int = 100,
    output_tokens: int = 50,
) -> GenerationLog:
    return GenerationLog(
        session_id=session_id,
        timestamp=datetime.now(tz=timezone.utc),
        task_type=task_type,
        quality_tier="standard",
        model_used="test-model",
        latency_ms=200,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cost_usd=cost_usd,
    )


# ---------------------------------------------------------------------------
# AC1: per-session total cost
# ---------------------------------------------------------------------------


class TestAC1SessionTotal:
    @pytest.mark.asyncio
    async def test_total_cost_equals_sum_of_inserted_rows(
        self, db: AsyncSession
    ) -> None:
        session = _make_session()
        db.add(session)
        await db.flush()

        db.add(_make_log(session.session_id, cost_usd=Decimal("0.003")))
        db.add(_make_log(session.session_id, cost_usd=Decimal("0.007")))
        await db.flush()

        summary = await get_cost_summary(db, session_id=session.session_id)

        assert float(summary.total_cost_usd) == pytest.approx(0.010)
        assert summary.total_generation_count == 2
        assert summary.total_input_tokens == 200
        assert summary.total_output_tokens == 100

    @pytest.mark.asyncio
    async def test_empty_session_returns_zero_totals(self, db: AsyncSession) -> None:
        session = _make_session()
        db.add(session)
        await db.flush()

        summary = await get_cost_summary(db, session_id=session.session_id)

        assert float(summary.total_cost_usd) == pytest.approx(0.0)
        assert summary.total_generation_count == 0
        assert summary.by_task_type == []
        assert summary.by_player_count == []


# ---------------------------------------------------------------------------
# AC2: grouping by task_type
# ---------------------------------------------------------------------------


class TestAC2TaskTypeGrouping:
    @pytest.mark.asyncio
    async def test_by_task_type_splits_rows_correctly(self, db: AsyncSession) -> None:
        session = _make_session()
        db.add(session)
        await db.flush()

        db.add(
            _make_log(
                session.session_id,
                task_type="character_dialogue",
                cost_usd=Decimal("0.004"),
            )
        )
        db.add(
            _make_log(
                session.session_id,
                task_type="character_dialogue",
                cost_usd=Decimal("0.006"),
            )
        )
        db.add(
            _make_log(
                session.session_id,
                task_type="safety_classification",
                cost_usd=Decimal("0.002"),
            )
        )
        await db.flush()

        summary = await get_cost_summary(db, session_id=session.session_id)
        by_type = {r.task_type: r for r in summary.by_task_type}

        assert set(by_type.keys()) == {"character_dialogue", "safety_classification"}
        assert float(by_type["character_dialogue"].cost_usd) == pytest.approx(0.010)
        assert by_type["character_dialogue"].generation_count == 2
        assert by_type["character_dialogue"].input_tokens == 200
        assert by_type["character_dialogue"].output_tokens == 100
        assert float(by_type["safety_classification"].cost_usd) == pytest.approx(0.002)
        assert by_type["safety_classification"].generation_count == 1


# ---------------------------------------------------------------------------
# AC2: grouping by player_count
# ---------------------------------------------------------------------------


class TestAC2PlayerCountGrouping:
    @pytest.mark.asyncio
    async def test_by_player_count_splits_across_sessions(
        self, db: AsyncSession
    ) -> None:
        s4 = _make_session(player_count=4)
        s8 = _make_session(player_count=8)
        db.add(s4)
        db.add(s8)
        await db.flush()

        db.add(_make_log(s4.session_id, cost_usd=Decimal("0.005")))
        db.add(_make_log(s8.session_id, cost_usd=Decimal("0.010")))
        await db.flush()

        summary = await get_cost_summary(db)
        by_pc = {r.player_count: r for r in summary.by_player_count}

        assert set(by_pc.keys()) == {4, 8}
        assert float(by_pc[4].cost_usd) == pytest.approx(0.005)
        assert float(by_pc[8].cost_usd) == pytest.approx(0.010)
        assert by_pc[4].session_count == 1
        assert by_pc[8].session_count == 1
        assert by_pc[4].generation_count == 1
        assert by_pc[8].generation_count == 1


# ---------------------------------------------------------------------------
# AC2: filtering by arc_id
# ---------------------------------------------------------------------------


class TestAC2ArcIdFilter:
    @pytest.mark.asyncio
    async def test_arc_filter_excludes_other_arc_logs(self, db: AsyncSession) -> None:
        s_alpha = _make_session(arc_id="arc-alpha")
        s_beta = _make_session(arc_id="arc-beta")
        db.add(s_alpha)
        db.add(s_beta)
        await db.flush()

        db.add(_make_log(s_alpha.session_id, cost_usd=Decimal("0.005")))
        db.add(_make_log(s_beta.session_id, cost_usd=Decimal("0.009")))
        await db.flush()

        summary = await get_cost_summary(db, arc_id="arc-alpha")

        assert float(summary.total_cost_usd) == pytest.approx(0.005)
        assert summary.total_generation_count == 1

    @pytest.mark.asyncio
    async def test_arc_filter_aggregates_multiple_sessions(
        self, db: AsyncSession
    ) -> None:
        s1 = _make_session(arc_id="arc-alpha")
        s2 = _make_session(arc_id="arc-alpha")
        db.add(s1)
        db.add(s2)
        await db.flush()

        db.add(_make_log(s1.session_id, cost_usd=Decimal("0.003")))
        db.add(_make_log(s2.session_id, cost_usd=Decimal("0.007")))
        await db.flush()

        summary = await get_cost_summary(db, arc_id="arc-alpha")

        assert float(summary.total_cost_usd) == pytest.approx(0.010)
        assert summary.total_generation_count == 2


# ---------------------------------------------------------------------------
# AC3: no pricing fields in CostSummaryResponse schema
# ---------------------------------------------------------------------------


class TestAC3NoPricingFields:
    def test_cost_summary_response_has_no_pricing_fields(self) -> None:
        from api.schemas import CostSummaryResponse

        banned = {"revenue", "margin", "price", "profit"}
        schema_fields = set(CostSummaryResponse.model_fields.keys())
        pricing_fields_present = banned & schema_fields
        assert not pricing_fields_present, (
            f"CostSummaryResponse must not contain pricing fields: {pricing_fields_present}"
        )
