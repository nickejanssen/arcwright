# AW-216: SSE Fanout Filtering And Replay

**Status**: Approved

**Author**: Claude (Arcwright SME) | **Date**: 2026-06-15

---

# References

- Architecture: [`docs/architecture/08-event-system.md`](../architecture/08-event-system.md) S8.4–S8.6
- ADR: [`docs/decisions/0008-content-event-type-layering.md`](../decisions/0008-content-event-type-layering.md)
- Predecessor spec: [`docs/specs/0038-aw-215-contentevent-model-and-in-memory-bus.md`](0038-aw-215-contentevent-model-and-in-memory-bus.md)
- Roadmap epic: [`docs/roadmap/epics/M3-A-content-event-system.md`](../roadmap/epics/M3-A-content-event-system.md)
- Roadmap task: [`docs/roadmap/tasks/AW-216-sse-fanout-filtering-and-replay.md`](../roadmap/tasks/AW-216-sse-fanout-filtering-and-replay.md)
- GitHub issue: [#69](https://github.com/nickejanssen/arcwright/issues/69)

---

# Overview

AW-216 is the second half of Epic M3-A. It builds the SSE delivery layer on top of the `SessionEventBus` from AW-215, adding:

1. **`SessionConnectionRegistry`** — the structural privacy enforcer. Maintains three typed connection buckets (player, host, shared display) and a `route(event)` method that resolves `AudienceTarget` to concrete connections. No code path through which a `specific_player` event reaches the wrong participant.

2. **`run_fanout`** — a background coroutine that subscribes to a `SessionEventBus` and dispatches each event to the connections returned by `registry.route(event)`.

3. **SSE endpoint** (`GET /sessions/{session_id}/events`) — a FastAPI endpoint using `sse-starlette` that registers a connection, issues a replay of missed events, then streams live events from the connection queue.

Routing dispatches on `EventCategory` for audience resolution (per ADR-0008). It never reads `event_type`.

---

# In Scope

- `engine/events/fanout.py`:
  - `SSEConnection`: asyncio.Queue wrapper with `send()`, `close()`, and async-iterator support.
  - `SessionConnectionRegistry`: `register_player`, `register_host`, `register_display`, `deregister`, `all_player_connections`, `route(event)`.
  - `run_fanout(bus, registry)`: background coroutine subscribing to the bus and dispatching via `registry.route`.
- `engine/events/__init__.py`: export new public names.
- `api/routers/events.py`:
  - `GET /sessions/{session_id}/events` SSE endpoint.
  - Query params: `since` (int, default 0), `player_id` (UUID | None), `connection_type` ("player" | "host" | "display", default "player").
  - Replay: atomically captures `cutoff = bus.last_sequence_number`, fetches `bus.replay_since(since)`, streams replay first, then streams live events with `sequence_number > cutoff`.
  - Deregisters connection on disconnect (via `try/finally`).
  - Module-level in-process session state (bus + registry + fanout task per session_id) for single-process MVP.
- `requirements.txt`: add `sse-starlette>=1.6`.
- `api/pyproject.toml`: add `sse-starlette>=1.6`.
- `engine/tests/test_events.py`: tests for `SessionConnectionRegistry.route()` and the full fanout + replay flow.

---

# Out of Scope

- JWT auth on SSE connections (M3-B).
- Persistent event storage (M3-D).
- Distributed fanout / Redis Pub/Sub (H2).
- TypeScript SDK EventSource wrapper (M3-B).
- Arc engine wiring to publish events (downstream tasks).

---

# Key Design Decisions

## Replay without duplication

Between subscribing to the live bus and fetching replay history, no `await` is interleaved. In asyncio's cooperative model, this block runs atomically:

```python
cutoff = bus.last_sequence_number   # no await
missed  = bus.replay_since(since)   # no await
```

Replay events have `sequence_number <= cutoff`. Live events from the connection queue have `sequence_number > cutoff`. The two sets are disjoint. The endpoint filters live events by `event.sequence_number > cutoff` to enforce this.

## Fanout via connection queue, not per-subscriber bus subscription

Each `SSEConnection` holds a private `asyncio.Queue`. The single `run_fanout` background coroutine subscribes to the bus and calls `conn.send(event)` for each connection returned by `registry.route(event)`. SSE endpoint generators read from their connection queue, not from the bus directly. This is the structural privacy guarantee: the routing decision is made once in the fan-out router, not replicated in every SSE handler.

## AudienceTarget.ALL does not include host connections

Per S8.4: `ALL` routes to `all_player_connections() + display_connections`. Hosts receive events via explicit `HOST_ONLY` events, not via `ALL`. This preserves the pattern from the Nightcap two-surface example (S8.5).

---

# Acceptance Criteria

- [ ] Specific-player events are delivered only to the matching player connection.
- [ ] Host-only, shared-display, and all-player events route to the documented connection sets.
- [ ] Reconnect replay uses sequence numbers to deliver missed events without duplicating already-seen events.

---

# Tests/Verification

- `TestSessionConnectionRegistry`: unit tests for `route()` across all four `AudienceTarget` values and for `deregister`.
- `TestFanoutRouter`: async tests verifying that `run_fanout` delivers specific-player events only to the correct connection queue, and that replay + live events are disjoint.
- All tests pass under `pytest engine/tests/`.
- `python -m ruff check engine api` and `python -m ruff format --check engine api` clean.

---

# Playtest Relevance

This task completes Epic M3-A and unlocks the M3 milestone exit gate: "events routed by target audience with no leakage." Without audience filtering, private clues could leak to other players' SSE streams, which would be a session-breaking privacy failure for any Nightcap playtest.
