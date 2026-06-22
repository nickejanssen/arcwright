# AW-255: REST-Backed Nightcap Session Loop

**Current version:** v0.1
**Last updated:** 2026-06-21
**Status:** Draft
**Canonical path:** docs/specs/0054-aw-255-rest-backed-nightcap-session-loop.md

**Author**: Codex

---

# References

- Architecture: `docs/architecture/09-developer-api.md` §9.2
- Architecture: `docs/architecture/11-telemetry.md` §11.3 and §11.7
- Architecture: `docs/architecture/12-build-plan.md` §12.2, §12.3, §12.4
- Architecture: `docs/architecture/15-development-guide.md` §15.5, §15.6, §15.9
- Related spec: `docs/specs/0042-aw-220-session-persistence-snapshots-and-resume.md`
- Related spec: `docs/specs/0045-aw-222-five-mvp-telemetry-signals.md`
- Related spec: `docs/specs/0053-aw-224-full-api-batch-harness.md`
- Existing API routes: `api/routers/characters.py`, `api/routers/sessions.py`
- Existing telemetry write sites: `engine/session/service.py`, `engine/telemetry/pacing.py`, `engine/knowledge/graph.py`
- Existing batch harness: `api/tests/test_batch_harness.py`
- Test-only harness to retire from this proof path: `engine/harness/runner.py`

---

# Overview

This is the missing follow-up to the M3 exit-gate audit. It closes the gap between the current REST API surface and a real Nightcap proof path by moving beat progression, live telemetry emission, and replay-intent collection onto the production session flow. The harness proof must use the same REST-backed path as live sessions, not a detached `HarnessRunner` that advances Nightcap outside the API.

---

# Existing State

- Session lifecycle, pause/resume snapshots, knowledge queries, and telemetry write helpers already exist.
- `SessionService.record_beat_transition()` and `SessionService.write_replay_intent()` already exist as write sites.
- `api/tests/test_batch_harness.py` currently still uses a detached `HarnessRunner` to force Nightcap beat progression in the proof path.
- There is no production REST flow yet that proves beat advancement, live pacing telemetry, and replay-intent capture together.

---

# In Scope

- A production session progression path that consumes validated REST player input and advances Nightcap beat state when the authored conditions are satisfied.
- Live telemetry emission from that same production path for `beat_transition`, `tension_update`, `pacing_intervention`, and `pacing_intervention_outcome` when applicable.
- A host-facing `POST /v1/sessions/{session_id}/replay-intent` endpoint backed by `SessionService.write_replay_intent()`.
- Batch harness updates so the 10-session proof runs through the same REST-backed progression path used by live sessions.

---

# Out of Scope

- New telemetry payload shapes or schema changes.
- New provider or model strings outside `config/routing_table.json` and `engine/routing/router.py`.
- Test-only `host_bypass` data becoming part of the production API schema.
- Any Nightcap content changes or arc-definition changes.
- Any new database migrations.

---

# Acceptance Criteria

- [ ] **AC1**: Submitting Nightcap player input through the REST API can advance the session to the next beat through production code, and the persisted `sessions.current_beat_id` reflects the new beat.
- [ ] **AC2**: The live progression path writes `beat_transition` Event rows from the production session flow without using `engine.harness.HarnessRunner` to move Nightcap beats.
- [ ] **AC3**: When the live pacing path triggers during a real session, it writes `tension_update`, `pacing_intervention`, and `pacing_intervention_outcome` Event rows as applicable.
- [ ] **AC4**: `POST /v1/sessions/{session_id}/replay-intent` persists a `replay_intent` Event row through `SessionService.write_replay_intent()` and remains separate from `end_session()`.
- [ ] **AC5**: `api/tests/test_batch_harness.py` runs 10 seeded Nightcap sessions through the same REST-backed progression path used by live sessions, records seed and pass/fail status, and no longer depends on a detached `HarnessRunner` to force the truth beat.
- [ ] **AC6**: The batch harness still uses mocked generation and consumes no real provider tokens.
- [ ] **AC7**: `host_bypass` remains local test metadata only and is never added to the API request or response schemas.

---

# Test Plan

**API integration tests**

- Extend or add HTTP-level tests that drive a Nightcap session through the REST input path and verify persisted beat advancement and telemetry writes.
- Add a replay-intent endpoint test that verifies the `replay_intent` Event row is written through the dedicated API path.

**Batch harness test**

- Update `api/tests/test_batch_harness.py` so the 10 seeded cases execute through the REST-backed progression path and assert `session_completed` plus telemetry presence without forcing beat state through `HarnessRunner`.

**Regression coverage**

- Keep the existing telemetry and cost tests intact.
- Keep `host_bypass` constrained to test metadata.

---

# Risks and Unknowns

- The live progression path is cross-cutting: route handler, session service, and telemetry writes must stay thin and deterministic.
- The batch harness currently proves the wrong thing; this spec exists so the repository has a durable record of the remaining proof gap.
- Replay-intent is intentionally separate from session end, so the API must not collapse those two steps together.

---

# Open Questions

None. The remaining work is a tracked implementation gap, not a design ambiguity.

