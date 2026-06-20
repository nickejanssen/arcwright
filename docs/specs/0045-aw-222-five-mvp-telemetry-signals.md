# AW-222: Five MVP Telemetry Signals

**Status**: Approved — all four decisions signed off. Implementation complete.

**Author**: Nicolas Janssen | **Date**: 2026-06-19

---

# References

- Architecture: `docs/architecture/11-telemetry.md` §11.3 — event_type strings and payload shapes (source of truth)
- Architecture: `docs/architecture/11-telemetry.md` §11.4 — `CONTENT_LOGGING_ENABLED` semantics
- ADR: `docs/decisions/0004-pacing-telemetry-outcome-events.md` — two-event append-only model for Signal 2
- ORM: `engine/db/orm.py` — `Event` model (session_id, event_type, payload JSONB, actor_char_id nullable)
- Existing builders: `engine/telemetry/pacing.py` — Signal 2 builders (do not rewrite)
- Signal 4+5 write site: `engine/session/service.py` — `SessionService` (has AsyncSession)
- Signal 3 write site: `engine/knowledge/graph.py` — `get_character_knowledge()` (has AsyncSession)
- Signal 2 pacing function: `engine/arc/pacing.py` — `evaluate_pacing_interventions()` (pure, no DB)
- Signal 1 state machine: `engine/arc/arc_state.py` — `GeneratedArcStateChart` (pure, no DB)
- Test helper: `engine/db/testing.py` — `make_sqlite_session_factory()`
- Prior spec (structure reference): `docs/specs/0044-aw-219-typescript-sdk-client.md`
- GitHub issue: #75

---

# Overview

Wires all five MVP telemetry signals — `beat_transition`, `tension_update` / `pacing_intervention` / `pacing_intervention_outcome`, `knowledge_constraint_activated`, `session_completed`, and `replay_intent` — so that every production session emits structured Event rows from the first run. Signal 2 payload builders already exist in `engine/telemetry/pacing.py`; every other signal needs a builder. No Alembic migration is required; the `events` table already has all needed columns.

---

# Existing State (Do Not Undo)

- Signal 2 builders are complete and tested in `engine/telemetry/pacing.py`. Do not rewrite them.
- `engine/harness/runner.py` has no DB session. Do not add one.
- `engine/session/service.py::SessionService.end_session()` writes no `session_completed` Event today.
- `engine/session/service.py::SessionService.pause_session()` writes a `session_interrupted` Event. This is NOT a telemetry signal. Do not confuse it with Signal 4.

---

# Signal Write Sites and Session State

This section names the exact write site for each signal, whether AsyncSession is present, and the verbatim payload shape from §11.3.

## Signal 1 — `beat_transition`

**Write site:** new method `SessionService.record_beat_transition()` in `engine/session/service.py`

**Has AsyncSession:** YES — follows existing `SessionService` parameter pattern (`db: AsyncSession` passed by caller)

**Why `SessionService`:** `GeneratedArcStateChart` (`engine/arc/arc_state.py`) is a pure synchronous state machine with no DB session. `HarnessRunner` (`engine/harness/runner.py`) has no DB session and must not receive one. No existing production caller of `ArcStateChart` transitions holds AsyncSession today. `SessionService` is the established home for session-scoped Event writes (Signal 4, Signal 5, and the existing `session_interrupted` write all live here).

**Builder:** new pure function `build_beat_transition_payload()` in new file `engine/telemetry/beats.py`

**Payload (verbatim from §11.3):**
```python
{
    "from_beat": str,
    "to_beat": str,
    "duration_seconds": int,
    "player_action_count": int,
}
```

**`actor_char_id`:** NULL — system event

---

## Signal 2 — `tension_update` / `pacing_intervention` / `pacing_intervention_outcome`

**Write site:** new async write functions appended to `engine/telemetry/pacing.py`:
- `record_tension_update(db: AsyncSession, session_id: UUID, score: float, beat_id: str) -> None`
- `record_pacing_intervention(db: AsyncSession, session_id: UUID, intervention: PacingIntervention) -> None`
- `record_pacing_intervention_outcome(db: AsyncSession, session_id: UUID, intervention: PacingIntervention, *, outcome_resumed_within_60s: bool) -> None`

**Has AsyncSession:** YES — taken as parameter by each write function

**Design choice (Decision B):** Option (b) — caller writes. `evaluate_pacing_interventions()` in `engine/arc/pacing.py` stays a pure function. The write functions live alongside the builders in `engine/telemetry/pacing.py`. The future async pacing loop calls them after evaluating interventions.

**Builders:** already exist — `build_tension_update_payload`, `build_pacing_intervention_payload`, `build_pacing_intervention_outcome_payload`. Do not rewrite.

**ADR constraint:** `pacing_intervention_outcome` is a separate append-only event; the trigger-time event is never updated. AW-222 adds the write function; the 60-second wait logic belongs to the future async pacing loop. Tests call the write function directly with a known `outcome_resumed_within_60s` value.

**quality_upgrade** produces no `pacing_intervention` or `pacing_intervention_outcome` Event. `build_pacing_intervention_payload` already returns `None` for non-player-facing interventions; `record_pacing_intervention` will early-return in that case.

**Payloads (verbatim from §11.3):**
```python
# tension_update
{"score": float, "beat_id": str}

# pacing_intervention
{"trigger_type": "stall" | "misdirection", "tension_score_at_trigger": float, "beat_id": str}

# pacing_intervention_outcome
{"trigger_type": "stall" | "misdirection", "tension_score_at_trigger": float, "beat_id": str, "outcome_resumed_within_60s": bool}
```

**`actor_char_id`:** NULL on all three — system events

---

## Signal 3 — `knowledge_constraint_activated`

**Write site:** `get_character_knowledge()` in `engine/knowledge/graph.py` — MODIFIED to write the Event after the query executes

**Has AsyncSession:** YES — `get_character_knowledge(session: AsyncSession, ...)` already takes it

**Builder:** new pure function `build_knowledge_constraint_payload()` in new file `engine/telemetry/knowledge.py`

**Scope (Decision C):** Both "blocked" and "permitted" directions are logged on every `get_character_knowledge()` call.
- "blocked" = the query returns zero active knowledge states. `fact_type = ""`, `provenance_chain_length = 0`.
- "permitted" = the query returns one or more active knowledge states. `fact_type = result[0].fact.fact_type`, `provenance_chain_length = max(len(ks.provenance_chain) for ks in result)`.
- One Event row per call. `character_id` in the payload is the queried `character_id` parameter (string form).

**Payload (verbatim from §11.3):**
```python
{
    "character_id": str,
    "fact_type": str,
    "constraint_direction": "blocked" | "permitted",
    "provenance_chain_length": int,
}
```

**`actor_char_id`:** set to the queried `character_id` — the only signal that sets this column

---

## Signal 4 — `session_completed`

**Write site:** `SessionService.end_session()` in `engine/session/service.py` — MODIFIED

**Has AsyncSession:** YES — `end_session(self, db: AsyncSession, session_id: UUID)` already takes it

**Signature change:** `end_session()` gains two new keyword-only parameters:
```python
async def end_session(
    self,
    db: AsyncSession,
    session_id: UUID,
    *,
    completion_type: str = "full_arc",
    killer_identified: bool = False,
) -> Session:
```
`total_duration_seconds`, `final_beat_reached`, and `player_count` are derived from the ORM session (`orm.started_at`, `orm.current_beat_id`, `orm.player_count`). The `end_session` route handler in `api/routers/sessions.py` passes `completion_type` and `killer_identified` from the (new) request body; MVP defaults are `"full_arc"` and `False`.

**Builder:** new pure function `build_session_completed_payload()` in new file `engine/telemetry/session.py`

**`CONTENT_LOGGING_ENABLED` gate:** Signal 4 is NEVER gated behind this flag. The Event row is written unconditionally. `content_text` and `embedding` are always `None`.

**Payload (verbatim from §11.3):**
```python
{
    "completion_type": "full_arc" | "interrupted" | "abandoned",
    "final_beat_reached": str,
    "killer_identified": bool,
    "total_duration_seconds": int,
    "player_count": int,
}
```

**`actor_char_id`:** NULL — system event

---

## Signal 5 — `replay_intent`

**Write site:** new method `SessionService.write_replay_intent()` in `engine/session/service.py`

**Has AsyncSession:** YES — follows existing `SessionService` pattern

**Design choice (Decision D):** Standalone `SessionService.write_replay_intent(db, session_id, intent, collection_method)`. Not a parameter to `end_session()`. The host ends the session and then separately calls this endpoint. This gives AW-224 flexibility to collect intent at different times (immediately after end, or from a separate host prompt).

**Builder:** new pure function `build_replay_intent_payload()` in `engine/telemetry/session.py` (alongside Signal 4 builder)

**Payload (verbatim from §11.3):**
```python
{
    "intent": "yes" | "no" | "maybe" | "not_asked",
    "collection_method": "host_report" | "in_app_prompt",
}
```

**`actor_char_id`:** NULL — system event

---

# In Scope

- New file `engine/telemetry/beats.py`: `build_beat_transition_payload()` builder + `record_beat_transition()` write function
- New file `engine/telemetry/knowledge.py`: `build_knowledge_constraint_payload()` builder
- New file `engine/telemetry/session.py`: `build_session_completed_payload()` and `build_replay_intent_payload()` builders
- Append to `engine/telemetry/pacing.py`: `record_tension_update()`, `record_pacing_intervention()`, `record_pacing_intervention_outcome()` write functions
- Modify `engine/session/service.py`: add `record_beat_transition()` and `write_replay_intent()` methods; modify `end_session()` to write `session_completed` Event and accept `completion_type` + `killer_identified` kwargs; modify `get_character_knowledge()` to write `knowledge_constraint_activated` Event
- Modify `engine/knowledge/graph.py`: write Signal 3 Event inside `get_character_knowledge()` after query executes
- New test file `engine/tests/test_telemetry_signals.py`: all test cases listed in Test Plan
- Minimal update to `api/routers/sessions.py` end_session handler: accept optional `EndSessionRequest` body and pass `completion_type` / `killer_identified` to `end_session()`

---

# Out of Scope

- Async 60-second pacing loop that emits `pacing_intervention_outcome` after observing resumed activity (future task)
- Beat-advance API endpoint (not yet built; Signal 1 write function is added now for testing, wiring to a route is deferred)
- Any new Alembic migration (`events` table already has all columns)
- `CONTENT_LOGGING_ENABLED` flag (Signal writes are unconditional; content_text and embedding are always None)
- Populating `embedding` on any Event row
- `decision_logs` writes for pacing (separate concern; ADR 0004 notes this separately)
- Signal 2 quality_upgrade pathway through `pacing_intervention` events

---

# Acceptance Criteria

- [ ] AC1: `beat_transition` Event row is written with `from_beat`, `to_beat`, `duration_seconds`, and `player_action_count` in payload when `SessionService.record_beat_transition()` is called. `actor_char_id` is NULL.
- [ ] AC2: `tension_update` Event row is written with `score` and `beat_id` when `record_tension_update()` is called. `actor_char_id` is NULL.
- [ ] AC2b: `pacing_intervention` Event row is written with `trigger_type`, `tension_score_at_trigger`, `beat_id` for `stall` and `misdirection` interventions. No row is written for `quality_upgrade`.
- [ ] AC2c: `pacing_intervention_outcome` Event row is written with all Signal 2 trigger fields plus `outcome_resumed_within_60s` when `record_pacing_intervention_outcome()` is called for a player-facing intervention.
- [ ] AC3: `knowledge_constraint_activated` Event row is written on every `get_character_knowledge()` call. `constraint_direction` is `"blocked"` when result is empty; `"permitted"` when result is non-empty. `actor_char_id` is set to the queried character_id.
- [ ] AC4: `session_completed` Event row is written inside `end_session()` with all five payload fields. Written unconditionally regardless of `CONTENT_LOGGING_ENABLED`.
- [ ] AC5: `replay_intent` Event row is written with `intent` and `collection_method` when `SessionService.write_replay_intent()` is called.
- [ ] AC6: `content_text` and `embedding` are `None` on all five signal Event rows.
- [ ] AC7: `pytest engine/tests/ -q`, `python -m ruff check engine api`, and `python -m ruff format --check engine api` all pass with no errors.

---

# Test Plan

**File:** `engine/tests/test_telemetry_signals.py`

**DB setup:** `engine.db.testing.make_sqlite_session_factory` — real in-memory SQLite. Assert actual Event rows committed to DB. Do not mock the Event write itself. Mock only `litellm.acompletion` if any generation path is invoked.

**Required cases:**

**Signal 1:**
- Call `record_beat_transition(db, session_id, from_beat="arrival", to_beat="investigation", duration_seconds=120, player_action_count=4)`. Assert one `beat_transition` Event row in DB with matching payload keys and values.

**Signal 2:**
- Call `record_tension_update(db, session_id, score=0.42, beat_id="investigation")`. Assert `tension_update` row with `{"score": 0.42, "beat_id": "investigation"}`.
- Build a stall `PacingIntervention`, call `record_pacing_intervention()`. Assert `pacing_intervention` row with `trigger_type`, `tension_score_at_trigger`, `beat_id`.
- Call `record_pacing_intervention_outcome()` with `outcome_resumed_within_60s=True`. Assert `pacing_intervention_outcome` row includes that field.
- Build a `quality_upgrade` `PacingIntervention`, call `record_pacing_intervention()`. Assert NO `pacing_intervention` row is written.

**Signal 3:**
- Seed a fact and `assert_knowledge` for a character, then call `get_character_knowledge()`. Assert `knowledge_constraint_activated` row with `constraint_direction="permitted"` and `provenance_chain_length >= 0`.
- Call `get_character_knowledge()` for a character with no knowledge states. Assert `knowledge_constraint_activated` row with `constraint_direction="blocked"`, `fact_type=""`, `provenance_chain_length=0`.

**Signal 4:**
- Call `end_session()` with `CONTENT_LOGGING_ENABLED` unset in environment. Assert `session_completed` Event row with all five payload fields. Assert `content_text` is `None`. This is direct AC3 validation.

**Signal 5:**
- Call `write_replay_intent(db, session_id, intent="yes", collection_method="host_report")`. Assert `replay_intent` row with matching payload.

---

# Risks and Unknowns

**Risks:**
- `get_character_knowledge()` is called in the pre-generation chokepoint for every AI character response. Adding an Event write here adds one DB insert per generation call. At MVP session volume this is acceptable; at scale it should be batched. This is a known trade-off for MVP.
- Modifying `end_session()` signature requires updating `api/routers/sessions.py` and its test in `api/tests/test_sessions_api.py`. Scope is narrow but touches two files.

**Unknowns:**
- None open. All four decisions are proposed in the section below and require sign-off before implementation.

---

# Four Decisions Requiring Sign-Off

> **Decision A — Signal 1 write site (beat_transition):**
> `GeneratedArcStateChart` has no DB session. No existing production caller with AsyncSession fires beat transitions today (`HarnessRunner` is test-only and must not receive a DB session). Proposed: new `SessionService.record_beat_transition(db, session_id, from_beat, to_beat, duration_seconds, player_action_count)` method in `engine/session/service.py`. The future beat-advance API endpoint will call this after the StateChart transition fires.
> | Rationale: `SessionService` is the established location for session-scoped Event writes.
> | Downside: The method exists before any production caller does; it is exercised only by tests until a beat-advance route is built.

> **Decision B — Signal 2 wiring approach:**
> Proposed: Option (b) — caller writes. `evaluate_pacing_interventions()` stays a pure function. New async write functions `record_tension_update()`, `record_pacing_intervention()`, `record_pacing_intervention_outcome()` are appended to `engine/telemetry/pacing.py` and take `AsyncSession` as a parameter. The future pacing loop will call them.
> | Rationale: Keeps the pure pacing engine free of DB concerns; write functions live beside their builders.
> | Downside: The write functions exist before the pacing loop that will call them; tests call them directly.

> **Decision C — Signal 3 scope (both directions logged):**
> Proposed: Both "blocked" (zero results) and "permitted" (one or more results) directions are logged on every `get_character_knowledge()` call. "blocked": `fact_type=""`, `provenance_chain_length=0`. "permitted": `fact_type=result[0].fact.fact_type`, `provenance_chain_length=max(len(ks.provenance_chain) for ks in result)`.
> | Rationale: Both directions are analytically useful; the payload schema already carries `constraint_direction: "blocked" | "permitted"` to distinguish them.
> | Downside: `fact_type=""` for "blocked" is a sentinel rather than a real fact type; analytics consumers must handle it.

> **Decision D — Signal 5 trigger (standalone function):**
> Proposed: new `SessionService.write_replay_intent(db, session_id, intent, collection_method)` standalone method, NOT a parameter to `end_session()`. Host ends the session and then separately calls a dedicated endpoint backed by this method.
> | Rationale: Decouples session termination from intent collection; AW-224 can collect intent at any point after session end.
> | Downside: Requires a new API endpoint (a `/replay-intent` route) in AW-224's scope; it is not implicit in `end_session()`.
