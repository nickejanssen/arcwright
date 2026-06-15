"""Tests for ContentEvent schema and the in-memory SessionEventBus."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from engine.events import (
    AudienceTarget,
    ContentEvent,
    EventCategory,
    PresentationHints,
    SessionEventBus,
)


def make_event(
    *,
    session_id: UUID,
    target_audience: AudienceTarget = AudienceTarget.all,
    target_player_id: UUID | None = None,
    category: EventCategory = EventCategory.narrative,
    event_type: str = "narrator_line",
    payload: dict | None = None,
    presentation_hints: PresentationHints | None = None,
) -> ContentEvent:
    return ContentEvent(
        session_id=session_id,
        timestamp=datetime.now(tz=timezone.utc),
        category=category,
        event_type=event_type,
        target_audience=target_audience,
        target_player_id=target_player_id,
        payload=payload or {},
        presentation_hints=presentation_hints or PresentationHints(),
    )


class TestContentEventSchema:
    def test_round_trips_all_documented_fields(self) -> None:
        session_id = uuid4()
        actor_id = uuid4()
        target_player_id = uuid4()
        hints = PresentationHints(
            emotion="tense",
            urgency="high",
            voice_hint="raspy",
            animation_hint="zoom_in",
            lighting_hint="dim_red",
            pause_before_ms=1500,
        )
        event = ContentEvent(
            session_id=session_id,
            timestamp=datetime(2026, 6, 14, 12, 0, tzinfo=timezone.utc),
            category=EventCategory.private_delivery,
            event_type="clue_delivery",
            actor_id=actor_id,
            target_audience=AudienceTarget.specific_player,
            target_player_id=target_player_id,
            payload={"clue_id": "library_note"},
            presentation_hints=hints,
        )

        assert event.session_id == session_id
        assert event.actor_id == actor_id
        assert event.category is EventCategory.private_delivery
        assert event.event_type == "clue_delivery"
        assert event.target_audience is AudienceTarget.specific_player
        assert event.target_player_id == target_player_id
        assert event.payload == {"clue_id": "library_note"}
        assert event.presentation_hints.pause_before_ms == 1500
        assert event.sequence_number == 0  # un-published, the bus stamps this

    def test_presentation_hints_defaults_pause_before_ms_to_zero(self) -> None:
        hints = PresentationHints()
        assert hints.pause_before_ms == 0
        assert hints.emotion is None

    def test_specific_player_target_requires_target_player_id(self) -> None:
        with pytest.raises(ValidationError):
            ContentEvent(
                session_id=uuid4(),
                timestamp=datetime.now(tz=timezone.utc),
                category=EventCategory.private_delivery,
                event_type="clue_delivery",
                target_audience=AudienceTarget.specific_player,
                target_player_id=None,
            )

    def test_target_player_id_rejected_for_non_specific_audience(self) -> None:
        with pytest.raises(ValidationError):
            ContentEvent(
                session_id=uuid4(),
                timestamp=datetime.now(tz=timezone.utc),
                category=EventCategory.narrative,
                event_type="narrator_line",
                target_audience=AudienceTarget.all,
                target_player_id=uuid4(),
            )

    def test_event_type_must_be_non_empty(self) -> None:
        with pytest.raises(ValidationError):
            ContentEvent(
                session_id=uuid4(),
                timestamp=datetime.now(tz=timezone.utc),
                category=EventCategory.system,
                event_type="",
                target_audience=AudienceTarget.host_only,
            )

    def test_event_type_is_arbitrary_string_owned_by_arc(self) -> None:
        # ADR-0008: game/arc owns the open string. Platform does not validate.
        event = make_event(
            session_id=uuid4(),
            category=EventCategory.state_transition,
            event_type="monster_rpg.world_state_tick",
        )
        assert event.event_type == "monster_rpg.world_state_tick"


class TestSessionEventBus:
    async def test_publish_assigns_monotonic_sequence_starting_at_one(self) -> None:
        session_id = uuid4()
        bus = SessionEventBus()

        first = await bus.publish(make_event(session_id=session_id))
        second = await bus.publish(make_event(session_id=session_id))
        third = await bus.publish(make_event(session_id=session_id))

        assert first.sequence_number == 1
        assert second.sequence_number == 2
        assert third.sequence_number == 3
        assert bus.last_sequence_number == 3

    async def test_single_subscriber_receives_events_in_publish_order(self) -> None:
        session_id = uuid4()
        bus = SessionEventBus()
        received: list[int] = []

        async with bus.subscribe() as sub:

            async def consume() -> None:
                async for event in sub:
                    received.append(event.sequence_number)
                    if len(received) == 3:
                        return

            consumer = asyncio.create_task(consume())
            await bus.publish(make_event(session_id=session_id))
            await bus.publish(make_event(session_id=session_id))
            await bus.publish(make_event(session_id=session_id))
            await asyncio.wait_for(consumer, timeout=1.0)

        assert received == [1, 2, 3]

    async def test_multiple_subscribers_each_receive_every_event(self) -> None:
        session_id = uuid4()
        bus = SessionEventBus()

        async def collect(sub) -> list[int]:
            received: list[int] = []
            async for event in sub:
                received.append(event.sequence_number)
                if len(received) == 2:
                    return received
            return received

        async with bus.subscribe() as sub_a, bus.subscribe() as sub_b:
            task_a = asyncio.create_task(collect(sub_a))
            task_b = asyncio.create_task(collect(sub_b))

            await bus.publish(make_event(session_id=session_id))
            await bus.publish(make_event(session_id=session_id))

            received_a, received_b = await asyncio.wait_for(
                asyncio.gather(task_a, task_b), timeout=1.0
            )

        assert received_a == [1, 2]
        assert received_b == [1, 2]

    async def test_late_subscriber_does_not_get_past_events_on_live_channel(
        self,
    ) -> None:
        session_id = uuid4()
        bus = SessionEventBus()

        await bus.publish(make_event(session_id=session_id))
        await bus.publish(make_event(session_id=session_id))

        received: list[int] = []
        async with bus.subscribe() as sub:

            async def consume() -> None:
                async for event in sub:
                    received.append(event.sequence_number)
                    if received:
                        return

            consumer = asyncio.create_task(consume())
            await bus.publish(make_event(session_id=session_id))
            await asyncio.wait_for(consumer, timeout=1.0)

        assert received == [3]

    async def test_replay_since_returns_only_events_after_given_sequence(self) -> None:
        session_id = uuid4()
        bus = SessionEventBus()

        for _ in range(5):
            await bus.publish(make_event(session_id=session_id))

        replay = bus.replay_since(2)
        assert [e.sequence_number for e in replay] == [3, 4, 5]

        assert bus.replay_since(5) == []
        assert [e.sequence_number for e in bus.replay_since(0)] == [1, 2, 3, 4, 5]

    async def test_history_buffer_evicts_oldest_when_capped(self) -> None:
        session_id = uuid4()
        bus = SessionEventBus(history_cap=3)

        for _ in range(5):
            await bus.publish(make_event(session_id=session_id))

        history_sequences = [e.sequence_number for e in bus.replay_since(0)]
        assert history_sequences == [3, 4, 5]
        assert bus.history_cap == 3
        assert bus.last_sequence_number == 5

    def test_history_cap_must_be_positive(self) -> None:
        with pytest.raises(ValueError):
            SessionEventBus(history_cap=0)

    async def test_unsubscribe_does_not_block_future_publishes(self) -> None:
        session_id = uuid4()
        bus = SessionEventBus()

        survivor_received: list[int] = []

        async with bus.subscribe() as survivor:

            async def consume() -> None:
                async for event in survivor:
                    survivor_received.append(event.sequence_number)
                    if len(survivor_received) == 2:
                        return

            consumer = asyncio.create_task(consume())

            # Subscribe and immediately unsubscribe a transient subscriber.
            transient = bus.subscribe()
            await transient.aclose()
            # Idempotent close is safe.
            await transient.aclose()

            await bus.publish(make_event(session_id=session_id))
            await bus.publish(make_event(session_id=session_id))
            await asyncio.wait_for(consumer, timeout=1.0)

        assert survivor_received == [1, 2]

    async def test_publish_returns_the_stamped_event(self) -> None:
        bus = SessionEventBus()
        event = make_event(session_id=uuid4())
        stamped = await bus.publish(event)
        assert stamped is event
        assert event.sequence_number == 1
