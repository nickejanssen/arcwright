# AW-221: Narrator Bridge On Resume

**Status**: Approved

**Author**: Nicolas Janssen | **Date**: 2026-06-18

---

# References

- Architecture: `docs/architecture/05-session-persistence.md` §5.3, §5.4
- Architecture: `docs/architecture/08-event-system.md` §8.2
- Architecture: `docs/architecture/10-content-safety.md`
- Related spec (immediately prior): `docs/specs/0042-aw-220-session-persistence-snapshots-and-resume.md`
- Routing table: `config/routing_table.json` (`narrator_bridge` task type)
- GitHub issue: #74

---

# Overview

Implements the narrator bridge step in the resume flow (§5.4 step 5). When a
session resumes, the engine generates a 2–3 sentence narrator recap seeded
from the ArcBeatState snapshot and emits it as a `ContentEvent` to the session
bus before normal play continues. When no snapshot exists the engine emits a
simple authored event with no LLM call.

---

# In Scope

- `engine/narrator/bridge.py` (new module): `generate_narrator_bridge(db,
  session_id, snapshot, quality_tier) → ContentEvent`
  - Builds generation messages from `snapshot.beat_id`,
    `snapshot.statemachine_config["session_context"]`, and
    `snapshot.transition_history` (human arc primacy: LLM composes language
    from structured state; it does not infer what happened).
  - Runs messages through the existing `engine.routing.logging.generate()`
    pipeline, which enforces L1 → L2 → L3 → `route_generation` in order.
  - Returns `ContentEvent(category=narrative, event_type="narrator_bridge",
    target_audience=all, payload={"text": <generated text>},
    presentation_hints=PresentationHints(emotion="warm", urgency="low",
    pause_before_ms=1500))`.
  - When `snapshot is None` (AC4 no-prior-state path): returns a simple
    authored ContentEvent with `payload={"text": "The session begins."}` and
    the same PresentationHints; no call to `generate()` is made.
- `engine/narrator/__init__.py`: exports `generate_narrator_bridge`.
- Wire into `api/routers/sessions.py:resume_session`: after
  `_session_service.resume_session`, calls `generate_narrator_bridge` and
  publishes the returned `ContentEvent` to the session bus via
  `_get_or_create_session_state(session_id)`.
  - The resume HTTP response does **not** include the ContentEvent text
    (surface agnosticism; the event is delivered via SSE, not the REST
    response body). `SessionStateResponse` is unchanged.

---

# Out of Scope

- Character-specific knowledge filtering for the narrator recap. The narrator
  bridge speaks to `all`; private-clue enforcement is delegated to L3 policy
  rails (arc `content_rails`), not a knowledge graph query.
- Full pacing engine restart (AW-222+).
- Full SSE stream reconnect logic (already handled by AW-216 replay).
- Single-player drop AI takeover (issue #138).
- Any new DB table or Alembic migration.
- New safety rules in l1.py, l2.py, or l3.py — existing pipeline used as-is.
- New fields on `PresentationHints` or `ContentEvent` — models used as-is.

---

# Acceptance Criteria

- [ ] AC1: Resuming a paused session emits a narrator bridge `ContentEvent`
  before normal play continues. `target_audience` is `all`, `category` is
  `narrative`, `event_type` is `"narrator_bridge"`.
- [ ] AC2: Narrator bridge generation uses `task_type="narrator_bridge"` in
  the routing call. No provider name or model string appears outside
  `config/routing_table.json` and `engine/routing/router.py`.
- [ ] AC3: Bridge generation runs through L1, L2, and L3 safety handling via
  `engine.routing.logging.generate()`. L1 hard stop → `NEUTRAL_L1_BRIDGE`
  replaces content (no LLM generation call made). L2 block →
  `NEUTRAL_L2_BRIDGE`. L3 policy rails injected before `route_generation`.
- [ ] AC4: When no `ArcBeatState` exists for the session, `generate_narrator_bridge`
  returns a simple authored `ContentEvent` with
  `payload={"text": "The session begins."}`. No call to `generate()` or
  `litellm.acompletion` is made.

---

# Implementation Notes

## `engine/narrator/bridge.py` design

```
generate_narrator_bridge(
    db: AsyncSession,
    session_id: UUID,
    snapshot: ArcBeatState | None,
    quality_tier: str,
) -> ContentEvent
```

No-snapshot fast path: build and return an authored ContentEvent immediately.

With-snapshot path:
1. Extract `beat_id`, `session_context` (from `snapshot.statemachine_config`),
   `transition_history` from the snapshot.
2. Build messages: system message combining beat position + session_context +
   transition_history + narrator instruction; user message `"Continue the
   session."`.
3. Call `generate(db, session_id=session_id, task_type="narrator_bridge",
   quality_tier=quality_tier, messages=messages, content_rails=None)` —
   `generate()` owns L1/L2/L3/routing. `content_rails=None` causes L3 to
   inject the platform-minimum policy (four L1 hard-stop categories).
4. Wrap `result.content` in a ContentEvent with the required fields.

## `api/routers/sessions.py` wiring

`resume_session` unpacks the snapshot from `_session_service.resume_session`,
calls `generate_narrator_bridge`, then calls
`bus.publish(event)` on the bus returned by
`_get_or_create_session_state(session_id)` (imported from
`api.routers.events`). The existing `SessionStateResponse` returned to the
HTTP caller is unchanged — narrator bridge text goes only to the SSE bus.

---

# Test Plan

## `engine/tests/test_narrator_bridge.py`

SQLite in-memory DB via `engine.db.testing.make_sqlite_session_factory`.
Patch `engine.routing.router.litellm.acompletion` at the litellm boundary
(the only acceptable mock in this suite — the function under test is
`generate_narrator_bridge`, not `route_generation`).

- `TestNarratorBridgeGeneration::test_emits_content_event_with_narrator_bridge_type`
  — happy-path call returns ContentEvent with `event_type=="narrator_bridge"`,
  `category==narrative`, `target_audience==all`.
- `TestNarratorBridgeGeneration::test_uses_narrator_bridge_task_type`
  — asserts litellm.acompletion was called with the model resolved from
  `routing_table.json` for `narrator_bridge/standard`, not a hardcoded string.
- `TestNarratorBridgeGeneration::test_l1_hard_stop_replaces_content`
  — injects L1-triggering text into the snapshot context; asserts
  ContentEvent.payload["text"] == NEUTRAL_L1_BRIDGE and no
  `litellm.acompletion` call for the narrator_bridge task type is made (L1
  fires before any LLM call).
- `TestNarratorBridgeGeneration::test_l2_block_replaces_content`
  — mock litellm returns a `{"blocked": true}` JSON for the L2 classification
  call; asserts ContentEvent.payload["text"] == NEUTRAL_L2_BRIDGE.
- `TestNarratorBridgeGeneration::test_no_snapshot_emits_authored_event_without_llm_call`
  — call with `snapshot=None`; asserts ContentEvent is emitted with
  `payload["text"] == "The session begins."` and no litellm.acompletion call
  was made.

## `api/tests/test_sessions_api.py` additions

- `TestPauseResumeSession::test_resume_emits_narrator_bridge_event`
  — create, start, pause, then resume. Patch
  `api.routers.events._get_or_create_session_state` to return a mock bus,
  and patch `engine.routing.router.litellm.acompletion` to return a valid
  narrator response. Assert the mock bus `.publish` was called with a
  ContentEvent whose `event_type == "narrator_bridge"`.

---

# Risks and Unknowns

**Risks**:
- `content_rails=None` causes L3 to inject platform-minimum policy (four L1
  hard-stop categories). This is intentional and sufficient: the narrator
  bridge speaks to `all` and private-clue enforcement is an arc-level
  concern that will be wired when arc definitions carry `content_rails`.
- `asyncio.create_task` in `_get_or_create_session_state` creates a fanout
  background task on first access. In the API test for resume, this is
  sidestepped by patching `_get_or_create_session_state` to return a mock bus.

**Unknowns**:
- None open at spec time.

---

# Open Questions

- None. All questions resolved during codebase review.
