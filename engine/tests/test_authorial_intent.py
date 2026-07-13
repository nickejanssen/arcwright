"""Tests for the authorial_intent block and intent fidelity telemetry.

Spec 0064 (AW-270), ADR-0012. Covers the validation matrix, context-assembly
inclusion, both telemetry payloads, and an end-to-end SessionService run
showing tension_update carrying target_score and beat exits emitting
intent_fidelity_summary.
"""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from pathlib import Path
from uuid import uuid4

import pytest
import pytest_asyncio
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from engine.arc.models import ArcDefinition, AuthorialIntent
from engine.characters.context import (
    BehaviorProfileContext,
    CharacterGenerationContext,
)
from engine.characters.dialogue import build_dialogue_messages
from engine.db.orm import Base, Event
from engine.db.testing import patch_metadata_for_sqlite
from engine.session.service import SessionService
from engine.telemetry.pacing import (
    build_intent_fidelity_summary_payload,
    build_tension_update_payload,
)

patch_metadata_for_sqlite()

ARC_PATH = Path(__file__).resolve().parents[2] / "nightcap" / "arc.json"


def _arc_data() -> dict:
    return json.loads(ARC_PATH.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Schema validation matrix
# ---------------------------------------------------------------------------


def test_arc_with_intent_block_validates() -> None:
    arc = ArcDefinition.model_validate(_arc_data())

    assert arc.authorial_intent is not None
    assert arc.authorial_intent.theme
    assert arc.authorial_intent.tone
    assert arc.authorial_intent.emotional_targets


def test_arc_without_intent_block_validates_unchanged() -> None:
    data = _arc_data()
    del data["authorial_intent"]

    arc = ArcDefinition.model_validate(data)

    assert arc.authorial_intent is None


def test_intent_target_with_unknown_beat_id_is_rejected() -> None:
    data = _arc_data()
    data["authorial_intent"]["emotional_targets"].append(
        {"beat_id": "no-such-beat", "target_tension": 0.5}
    )

    with pytest.raises(ValidationError, match="no-such-beat"):
        ArcDefinition.model_validate(data)


def test_intent_target_tension_outside_range_is_rejected() -> None:
    data = _arc_data()
    data["authorial_intent"]["emotional_targets"][0]["target_tension"] = 1.5

    with pytest.raises(ValidationError):
        ArcDefinition.model_validate(data)


def test_intent_block_rejects_unknown_keys() -> None:
    data = _arc_data()
    data["authorial_intent"]["surprise_field"] = "nope"

    with pytest.raises(ValidationError):
        ArcDefinition.model_validate(data)


def test_intent_block_requires_theme_and_tone() -> None:
    data = _arc_data()
    del data["authorial_intent"]["theme"]

    with pytest.raises(ValidationError):
        ArcDefinition.model_validate(data)


def test_target_tension_for_returns_declared_target_or_none() -> None:
    intent = AuthorialIntent(
        theme="t",
        tone="t",
        emotional_targets=[{"beat_id": "opening", "target_tension": 0.4}],
    )

    assert intent.target_tension_for("opening") == 0.4
    assert intent.target_tension_for("finale") is None


# ---------------------------------------------------------------------------
# Context assembly
# ---------------------------------------------------------------------------


def _minimal_context() -> CharacterGenerationContext:
    return CharacterGenerationContext(
        session_id=uuid4(),
        character_id=uuid4(),
        behavior_profile=BehaviorProfileContext(
            personality={"warmth": 0.5},
            goals=("stay hidden",),
            secrets=(),
            tells=(),
        ),
        relationship_dispositions=(),
        is_ai_controlled=True,
        known_facts=(),
        unknown_facts=(),
    )


def test_dialogue_messages_include_intent_block_when_present() -> None:
    intent = AuthorialIntent(
        theme="Secrets under the chandelier",
        tone="Cosy but sharp",
        emotional_targets=[
            {"beat_id": "opening", "target_tension": 0.3, "note": "settling in"}
        ],
    )

    messages = build_dialogue_messages(
        _minimal_context(),
        player_input="Who saw the victim last?",
        authorial_intent=intent,
    )

    system_text = messages[0]["content"]
    assert "[AUTHORIAL INTENT]" in system_text
    assert "Secrets under the chandelier" in system_text
    assert "Cosy but sharp" in system_text
    assert "opening: 0.3 (settling in)" in system_text
    # The intent block sits in the stable region: after character identity,
    # before the per-turn scene block, so it stays inside the cacheable
    # prefix of the system prompt.
    assert system_text.index("[END CHARACTER IDENTITY AND PERSONALITY]") < (
        system_text.index("[AUTHORIAL INTENT]")
    )
    assert system_text.index("[AUTHORIAL INTENT]") < system_text.index(
        "[CURRENT SCENE]"
    )


def test_dialogue_messages_unchanged_without_intent() -> None:
    messages = build_dialogue_messages(
        _minimal_context(),
        player_input="Who saw the victim last?",
    )

    assert "[AUTHORIAL INTENT]" not in messages[0]["content"]


# ---------------------------------------------------------------------------
# Telemetry payloads
# ---------------------------------------------------------------------------


def test_tension_update_payload_includes_target_score_when_declared() -> None:
    payload = build_tension_update_payload(score=0.42, beat_id="dig", target_score=0.6)

    assert payload == {"score": 0.42, "beat_id": "dig", "target_score": 0.6}


def test_tension_update_payload_omits_target_score_when_absent() -> None:
    payload = build_tension_update_payload(score=0.42, beat_id="dig")

    assert "target_score" not in payload


def test_intent_fidelity_summary_payload_computes_mean_and_deviation() -> None:
    payload = build_intent_fidelity_summary_payload(
        beat_id="dig", target_score=0.6, scores=[0.5, 0.7, 0.9]
    )

    assert payload["beat_id"] == "dig"
    assert payload["target_score"] == 0.6
    assert payload["mean_score"] == pytest.approx(0.7)
    assert payload["mean_abs_deviation"] == pytest.approx((0.1 + 0.1 + 0.3) / 3)


def test_intent_fidelity_summary_payload_with_no_scores_reports_none() -> None:
    payload = build_intent_fidelity_summary_payload(
        beat_id="dig", target_score=0.6, scores=[]
    )

    assert payload["mean_score"] is None
    assert payload["mean_abs_deviation"] is None


# ---------------------------------------------------------------------------
# End-to-end: SessionService emits both event types (headless, SQLite)
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture()
async def db() -> AsyncIterator[AsyncSession]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        try:
            yield session
        finally:
            await session.rollback()
    await engine.dispose()


@pytest.mark.asyncio
async def test_live_session_emits_target_scores_and_fidelity_summaries(
    db: AsyncSession,
) -> None:
    svc = SessionService()
    session, _token = await svc.create_session(
        db, arc_id="nightcap-v1", host_account_id=uuid4()
    )
    await svc.start_session(db, session.session_id)

    # Two advances: the first exits the initial beat (no tension samples yet),
    # the second exits a beat that has one tension_update recorded for it.
    await svc.advance_live_session_on_input(db, session.session_id)
    await svc.advance_live_session_on_input(db, session.session_id)

    result = await db.execute(
        select(Event).where(Event.session_id == session.session_id)
    )
    events = list(result.scalars())
    tension_events = [e for e in events if e.event_type == "tension_update"]
    summaries = [e for e in events if e.event_type == "intent_fidelity_summary"]

    # Every Nightcap beat declares a target, so every tension_update carries
    # target_score.
    assert tension_events
    assert all("target_score" in e.payload for e in tension_events)

    # Both exited beats declared targets, so both exits emitted summaries.
    assert [s.payload["beat_id"] for s in summaries] == ["arrival", "body"]
    first, second = summaries
    assert first.payload["target_score"] == 0.2
    assert first.payload["mean_score"] is None  # no samples while beat active
    assert second.payload["target_score"] == 0.35
    assert second.payload["mean_score"] is not None
    assert second.payload["mean_abs_deviation"] is not None
