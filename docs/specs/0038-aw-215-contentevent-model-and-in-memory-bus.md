# AW-215: ContentEvent Model And In-Memory Bus

**Status**: Approved

**Author**: Claude (Arcwright SME) | **Date**: 2026-06-14

---

# References

- Related ADRs: [`docs/decisions/0008-content-event-type-layering.md`](../decisions/0008-content-event-type-layering.md)
- Architecture sections: [`docs/architecture/08-event-system.md`](../architecture/08-event-system.md) S8.2 and S8.3, [`docs/architecture/15-development-guide.md`](../architecture/15-development-guide.md)
- Roadmap epic: [`docs/roadmap/epics/M3-A-content-event-system.md`](../roadmap/epics/M3-A-content-event-system.md)
- Roadmap task: [`docs/roadmap/tasks/AW-215-contentevent-model-and-in-memory-bus.md`](../roadmap/tasks/AW-215-contentevent-model-and-in-memory-bus.md)
- GitHub issues: epic [#40](https://github.com/nickejanssen/arcwright/issues/40), task [#68](https://github.com/nickejanssen/arcwright/issues/68)
- Product decisions: D-32 (Jackbox-style multi-surface routing), D-45 (structured semantic content events), D-50 (SSE + POST transport adapter pattern)

---

# Overview

AW-215 is the first half of Epic M3-A. It introduces the `ContentEvent` schema and an in-memory per-session async event bus inside `engine/events/`. The bus is the engine-side delivery point that S8.3 names: arc execution publishes to it; AW-216's SSE fan-out will subscribe to it.

The schema is implemented per ADR-0008's layered classification: a closed `EventCategory` enum owned by the platform plus an open `event_type` string owned by the arc/game.

---

# In Scope

- `engine/events/models.py`:
  - `AudienceTarget` enum (`all`, `host_only`, `specific_player`, `shared_display`).
  - `EventCategory` enum (`narrative`, `character_dialogue`, `private_delivery`, `acknowledgement`, `state_transition`, `input_request`, `system`).
  - `PresentationHints` model matching S8.2 exactly.
  - `ContentEvent` model matching S8.2 (layered category + event_type per ADR-0008).
- `engine/events/bus.py`:
  - `SessionEventBus`, a per-session async pub/sub bus.
  - Monotonic `sequence_number` assignment on `publish`, owned by the bus, starting at 1.
  - Multi-subscriber fan-out: each `subscribe()` call returns an independent async iterator that receives every published event in order.
  - Bounded in-session history (ring buffer, default 1000 events) so AW-216 can serve reconnect replay without bolting on a separate retention layer.
  - `replay_since(sequence_number)` helper returning events with `sequence_number > N`, ordered.
  - Subscriber lifecycle handled cleanly: `unsubscribe()` is idempotent; a closed subscriber does not block future publishes.
- `engine/events/__init__.py`: public exports.
- `engine/tests/test_events.py`: unit tests covering acceptance criteria.

---

# Out of Scope

- SSE wire layer, FastAPI routes, JWT auth on connections (AW-216).
- Target-audience filtering at the connection registry (AW-216).
- Reconnect-replay endpoint and gap detection on the SDK side (AW-216).
- Telemetry persistence of events to the events table (M3-D).
- Arc engine emission wiring (downstream, after the bus exists).
- Distributed pub/sub adapters (Redis, Cloud Pub/Sub) — H2.
- Game-specific `event_type` strings beyond what the tests need as fixtures.

---

# Acceptance Criteria

- [ ] `ContentEvent` includes every field documented in `docs/architecture/08-event-system.md` S8.2 with the layered `category` + `event_type` shape per ADR-0008.
- [ ] `PresentationHints` includes every field documented in S8.2 with `pause_before_ms` defaulting to `0`.
- [ ] `SessionEventBus` assigns `sequence_number` monotonically starting at 1, increasing by 1 per published event, per session, independent of subscriber count.
- [ ] Subscribers receive every published event in publish order.
- [ ] Multiple concurrent subscribers each receive every event in order, with no cross-subscriber interference.
- [ ] A subscriber that is added after `N` events have been published does not retroactively receive those events through the live channel; replay is served via `replay_since(...)`.
- [ ] `replay_since(seq)` returns events with sequence numbers strictly greater than `seq`, in order; returns an empty list when no such events exist.
- [ ] The history buffer is bounded; oldest entries are evicted when the buffer is full.
- [ ] Unsubscribing a subscriber does not block subsequent publishes or other subscribers.

---

# Tests/Verification

- New file `engine/tests/test_events.py` with unit tests covering each acceptance-criterion behavior.
- All new tests pass under `pytest engine/tests/`.
- `python -m ruff check engine` and `python -m ruff format --check engine` are clean for the new files.

---

# Risks and Mitigations

- **Asyncio fanout pattern errors.** `asyncio.Queue` is single-consumer by design. Mitigation: bus maintains a list of per-subscriber `asyncio.Queue` instances and pushes to each on publish; subscribers consume from their own queue.
- **History buffer leaks memory over a very long session.** Mitigation: ring buffer with a configurable cap (default 1000) and a clear documented bound. Persistent storage is the M3-D telemetry table's job, not the bus's.
- **Tight coupling to AW-216.** Mitigation: AW-216 will consume the public API (`subscribe`, `unsubscribe`, `replay_since`); the bus does not import anything web-shaped.

---

# Playtest Relevance

This task unlocks the M3 milestone exit gate ("events routed by target audience with no leakage") indirectly: AW-216 cannot land without it. By itself, AW-215 is invisible to playtesters; it is platform plumbing.
