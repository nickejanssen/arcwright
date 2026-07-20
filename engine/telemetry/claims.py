"""Telemetry payloads and event recorders for claim resolution."""

from __future__ import annotations

from collections.abc import Sequence
from math import ceil
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from engine.claims.models import ClaimRecord, FlagResult
from engine.db.orm import Event


def build_claim_recorded_payload(claim: ClaimRecord) -> dict[str, Any]:
    """Build safe claim telemetry without exposing lie classification."""
    return {
        "claim_id": claim.claim_id,
        "speaker_id": claim.speaker_id,
        "asker_id": claim.asker_id,
        "round_index": claim.round_index,
        "beat_id": claim.beat_id,
        "interaction_window_id": claim.interaction_window_id,
        "claim_text": claim.claim_text,
        "referenced_fact_ids": list(claim.referenced_fact_ids),
    }


def build_contradiction_outcome_payload(result: FlagResult) -> dict[str, Any]:
    return {
        "claim_id": result.claim_id,
        "outcome": result.outcome.value,
        "evidence_id_used": result.evidence_id_used,
    }


def build_answer_latency_payload(
    *, latency_ms: float, quality_tier: str
) -> dict[str, Any]:
    return {"latency_ms": latency_ms, "quality_tier": quality_tier}


def compute_answer_latency_p95(latencies_ms: Sequence[float]) -> float:
    """Return the nearest-rank p95 from recorded latency values."""
    if not latencies_ms:
        raise ValueError("at least one latency value is required")
    ordered = sorted(latencies_ms)
    return ordered[max(0, ceil(0.95 * len(ordered)) - 1)]


async def record_claim_recorded(
    db: AsyncSession, session_id: UUID, claim: ClaimRecord
) -> None:
    db.add(
        Event(
            session_id=session_id,
            event_type="claim_recorded",
            payload=build_claim_recorded_payload(claim),
        )
    )
    await db.flush()


async def record_contradiction_outcome(
    db: AsyncSession, session_id: UUID, result: FlagResult
) -> None:
    db.add(
        Event(
            session_id=session_id,
            event_type=f"contradiction_{result.outcome.value}",
            payload=build_contradiction_outcome_payload(result),
        )
    )
    await db.flush()


async def record_answer_latency(
    db: AsyncSession,
    session_id: UUID,
    *,
    latency_ms: float,
    quality_tier: str,
) -> None:
    db.add(
        Event(
            session_id=session_id,
            event_type="answer_generation_latency",
            payload=build_answer_latency_payload(
                latency_ms=latency_ms,
                quality_tier=quality_tier,
            ),
        )
    )
    await db.flush()
