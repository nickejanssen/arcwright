"""Tests for ContentEvent schema, the in-memory SessionEventBus, and the SSE fanout layer."""

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
    SessionConnectionRegistry,
    SessionEventBus,
    SSEConnection,
    run_fanout,
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


# ---------------------------------------------------------------------------
# AW-216: SessionConnectionRegistry routing
# ---------------------------------------------------------------------------


class TestSessionConnectionRegistry:
    def test_specific_player_event_routes_only_to_matching_player(self) -> None:
        registry = SessionConnectionRegistry()
        player_a = uuid4()
        player_b = uuid4()
        conn_a = registry.register_player(player_a)
        conn_b = registry.register_player(player_b)

        event = make_event(
            session_id=uuid4(),
            target_audience=AudienceTarget.specific_player,
            target_player_id=player_a,
            category=EventCategory.private_delivery,
            event_type="clue_delivery",
        )
        result = registry.route(event)

        assert conn_a in result
        assert conn_b not in result

    def test_all_event_routes_to_all_players_and_displays_but_not_hosts(self) -> None:
        registry = SessionConnectionRegistry()
        conn_player = registry.register_player(uuid4())
        conn_display = registry.register_display()
        conn_host = registry.register_host(uuid4())

        event = make_event(session_id=uuid4(), target_audience=AudienceTarget.all)
        result = registry.route(event)

        assert conn_player in result
        assert conn_display in result
        assert conn_host not in result

    def test_host_only_event_routes_only_to_host_connections(self) -> None:
        registry = SessionConnectionRegistry()
        conn_host = registry.register_host(uuid4())
        conn_player = registry.register_player(uuid4())
        conn_display = registry.register_display()

        event = make_event(session_id=uuid4(), target_audience=AudienceTarget.host_only)
        result = registry.route(event)

        assert conn_host in result
        assert conn_player not in result
        assert conn_display not in result

    def test_shared_display_event_routes_only_to_display_connections(self) -> None:
        registry = SessionConnectionRegistry()
        conn_display = registry.register_display()
        conn_player = registry.register_player(uuid4())
        conn_host = registry.register_host(uuid4())

        event = make_event(
            session_id=uuid4(), target_audience=AudienceTarget.shared_display
        )
        result = registry.route(event)

        assert conn_display in result
        assert conn_player not in result
        assert conn_host not in result

    def test_specific_player_missing_from_registry_returns_empty(self) -> None:
        registry = SessionConnectionRegistry()
        unknown = uuid4()

        event = make_event(
            session_id=uuid4(),
            target_audience=AudienceTarget.specific_player,
            target_player_id=unknown,
            category=EventCategory.private_delivery,
            event_type="clue_delivery",
        )
        assert registry.route(event) == []

    def test_deregister_player_removes_connection_from_subsequent_routing(self) -> None:
        registry = SessionConnectionRegistry()
        player_id = uuid4()
        conn = registry.register_player(player_id)
        registry.deregister(conn)

        event = make_event(
            session_id=uuid4(),
            target_audience=AudienceTarget.specific_player,
            target_player_id=player_id,
            category=EventCategory.private_delivery,
            event_type="clue_delivery",
        )
        assert registry.route(event) == []

    def test_deregister_host_removes_connection_from_subsequent_routing(self) -> None:
        registry = SessionConnectionRegistry()
        host_id = uuid4()
        conn = registry.register_host(host_id)
        registry.deregister(conn)

        event = make_event(session_id=uuid4(), target_audience=AudienceTarget.host_only)
        assert registry.route(event) == []

    def test_deregister_display_removes_connection_from_subsequent_routing(
        self,
    ) -> None:
        registry = SessionConnectionRegistry()
        conn = registry.register_display()
        registry.deregister(conn)

        event = make_event(
            session_id=uuid4(), target_audience=AudienceTarget.shared_display
        )
        assert registry.route(event) == []

    def test_deregister_is_idempotent(self) -> None:
        registry = SessionConnectionRegistry()
        conn = registry.register_player(uuid4())
        registry.deregister(conn)
        registry.deregister(conn)  # second call must not raise

    def test_multiple_players_all_receive_all_event(self) -> None:
        registry = SessionConnectionRegistry()
        conns = [registry.register_player(uuid4()) for _ in range(3)]

        event = make_event(session_id=uuid4(), target_audience=AudienceTarget.all)
        result = registry.route(event)

        for conn in conns:
            assert conn in result


# ---------------------------------------------------------------------------
# AW-216: run_fanout integration tests (AC1, AC2, AC3)
# ---------------------------------------------------------------------------


async def _cancel_task(task: asyncio.Task) -> None:  # type: ignore[type-arg]
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


class TestFanoutRouter:
    async def test_fanout_delivers_specific_player_event_only_to_matching_connection(
        self,
    ) -> None:
        bus = SessionEventBus()
        registry = SessionConnectionRegistry()
        player_a = uuid4()
        player_b = uuid4()
        conn_a = registry.register_player(player_a)
        conn_b = registry.register_player(player_b)

        task = asyncio.create_task(run_fanout(bus, registry))
        # Yield so the fanout task runs up to its first await (queue.get),
        # establishing its bus subscription before we publish.
        await asyncio.sleep(0)
        try:
            event = await bus.publish(
                make_event(
                    session_id=uuid4(),
                    target_audience=AudienceTarget.specific_player,
                    target_player_id=player_a,
                    category=EventCategory.private_delivery,
                    event_type="clue_delivery",
                )
            )
            received = await asyncio.wait_for(conn_a._queue.get(), timeout=1.0)
            assert received.event_id == event.event_id
            assert conn_b._queue.empty()
        finally:
            await _cancel_task(task)

    async def test_fanout_delivers_all_event_to_players_and_display_not_host(
        self,
    ) -> None:
        bus = SessionEventBus()
        registry = SessionConnectionRegistry()
        conn_player = registry.register_player(uuid4())
        conn_display = registry.register_display()
        conn_host = registry.register_host(uuid4())

        task = asyncio.create_task(run_fanout(bus, registry))
        await asyncio.sleep(0)
        try:
            event = await bus.publish(
                make_event(session_id=uuid4(), target_audience=AudienceTarget.all)
            )
            received_player = await asyncio.wait_for(
                conn_player._queue.get(), timeout=1.0
            )
            received_display = await asyncio.wait_for(
                conn_display._queue.get(), timeout=1.0
            )
            assert received_player.event_id == event.event_id
            assert received_display.event_id == event.event_id
            assert conn_host._queue.empty()
        finally:
            await _cancel_task(task)

    async def test_replay_missed_events_and_live_events_are_disjoint(self) -> None:
        """AC3: reconnect replay uses sequence numbers; no duplicates.

        Approach: publish 5 events before the connection, register it with
        since=3, capture cutoff = bus.last_sequence_number, get replay events,
        then publish 2 more. Verify replay covers only seqs 4-5, live covers
        6-7, and the two sets are disjoint.
        """
        bus = SessionEventBus()
        registry = SessionConnectionRegistry()
        session_id = uuid4()

        for _ in range(5):
            await bus.publish(make_event(session_id=session_id))

        player_id = uuid4()
        conn = registry.register_player(player_id)
        task = asyncio.create_task(run_fanout(bus, registry))
        await asyncio.sleep(0)

        try:
            # Atomic capture — no await between these three lines.
            cutoff = bus.last_sequence_number  # 5
            missed = bus.replay_since(3)  # seqs 4, 5

            await bus.publish(make_event(session_id=session_id))  # seq 6
            await bus.publish(make_event(session_id=session_id))  # seq 7

            live_event_a = await asyncio.wait_for(conn._queue.get(), timeout=1.0)
            live_event_b = await asyncio.wait_for(conn._queue.get(), timeout=1.0)

            missed_seqs = {e.sequence_number for e in missed}
            live_seqs_raw = {live_event_a.sequence_number, live_event_b.sequence_number}
            live_seqs_filtered = {s for s in live_seqs_raw if s > cutoff}

            assert missed_seqs == {4, 5}
            assert live_seqs_filtered == {6, 7}
            assert missed_seqs.isdisjoint(live_seqs_filtered)
        finally:
            await _cancel_task(task)

    async def test_sse_connection_close_ends_async_iteration(self) -> None:
        conn = SSEConnection(player_id=uuid4())
        conn.send(make_event(session_id=uuid4()))
        conn.close()

        received = []
        async for event in conn:
            received.append(event)

        assert len(received) == 1

    def test_replay_privacy_specific_player_events_filtered_for_wrong_player(
        self,
    ) -> None:
        """Replay must apply the same registry.route() filter as the live fanout.

        A player reconnecting with since=0 should not receive specific_player
        events from history that were addressed to a different player.
        """
        registry = SessionConnectionRegistry()
        session_id = uuid4()
        player_a = uuid4()
        player_b = uuid4()
        conn_a = registry.register_player(player_a)
        registry.register_player(player_b)

        event_for_a = ContentEvent(
            session_id=session_id,
            timestamp=datetime.now(tz=timezone.utc),
            category=EventCategory.private_delivery,
            event_type="clue_delivery",
            target_audience=AudienceTarget.specific_player,
            target_player_id=player_a,
        )
        event_for_b = ContentEvent(
            session_id=session_id,
            timestamp=datetime.now(tz=timezone.utc),
            category=EventCategory.private_delivery,
            event_type="clue_delivery",
            target_audience=AudienceTarget.specific_player,
            target_player_id=player_b,
        )

        # Simulate what the SSE endpoint does when filtering replay events.
        replay_history = [event_for_a, event_for_b]
        visible_to_conn_a = [e for e in replay_history if conn_a in registry.route(e)]

        assert event_for_a in visible_to_conn_a
        assert event_for_b not in visible_to_conn_a

    def test_replay_privacy_host_only_events_hidden_from_player(self) -> None:
        """A player reconnecting should not receive host_only events from history."""
        registry = SessionConnectionRegistry()
        session_id = uuid4()
        player_conn = registry.register_player(uuid4())

        host_event = ContentEvent(
            session_id=session_id,
            timestamp=datetime.now(tz=timezone.utc),
            category=EventCategory.acknowledgement,
            event_type="clue_acknowledged",
            target_audience=AudienceTarget.host_only,
        )
        all_event = make_event(
            session_id=session_id, target_audience=AudienceTarget.all
        )

        replay_history = [host_event, all_event]
        visible = [e for e in replay_history if player_conn in registry.route(e)]

        assert host_event not in visible
        assert all_event in visible
