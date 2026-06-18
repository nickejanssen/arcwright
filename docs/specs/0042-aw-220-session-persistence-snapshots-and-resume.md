# AW-220: Session Persistence Snapshots And Resume

**Status**: Done

**Author**: Nicolas Janssen | **Date**: 2026-06-18

---

# References

- Architecture: `docs/architecture/05-session-persistence.md` §5.2, §5.3, §5.4
- Supplemental schemas: `docs/architecture/supplemental-schemas.md` (`arc_beat_states`)
- Related specs: `0041-aw-217-session-lifecycle-api-and-auth.md`, `0013-aw-106-pre-generation-knowledge-constraint-hook.md`
- GitHub issue: #73
- PR: #136

---

# Overview

Moves `SessionService` from in-memory to DB-backed, adds snapshot-on-pause at the nearest completed beat boundary, and adds cold-resume from DB so a session survives total process loss. Retires the `_ensure_session_row_for_knowledge` bridge introduced by AW-248.

---

# In Scope

- DB-backed `SessionService` (all methods take `AsyncSession`; no in-process state)
- `engine/session/snapshots.py`: `capture_chart_config`, `write_snapshot`, `load_current_snapshot`, `restore_chart_from_snapshot`
- `pause_session` writes an `arc_beat_states` row and a `session_interrupted` event log entry
- `resume_session` reads the `is_current` snapshot and rebuilds `current_beat_id`; returns the snapshot ORM row so the caller can reconstruct the live chart
- Retire `_ensure_session_row_for_knowledge` from `api/routers/knowledge.py`
- `GeneratedArcStateChart.__init__` and `ArcStateChart()` factory accept `start_value` for beat-position resume
- Async rewrites of `api/routers/sessions.py`, `api/routers/knowledge.py`, `api/routers/characters.py`, `engine/characters/service.py`
- Integration test suite in `engine/tests/test_session_resume.py` covering all three ACs with cold-resume pattern (no in-process cache)

---

# Out of Scope

- Narrator bridge on resume (AW-221)
- TypeScript SDK changes (AW-219)
- Full telemetry beyond `session_interrupted` event (AW-222)
- Single-player drop to AI takeover (§5.5 — separate ticket)
- New Alembic migration (`arc_beat_states` already exists in `migrations/versions/0002`)

---

# Acceptance Criteria

- [x] AC1: Interruption writes an `arc_beat_states` snapshot at the nearest completed beat boundary (`is_current = True`; prior row demoted to `is_current = False`)
- [x] AC2: Resume restores statemachine configuration, knowledge state, relationship state, and session status from the DB row; verified by tests that discard all in-process objects after pause and resume from a fresh `AsyncSession`
- [x] AC3: A resumed session never restarts from the beginning unless no valid prior `arc_beat_states` row exists; when no snapshot exists, the session falls back to the arc's initial beat (documented exception in `docs/architecture/05-session-persistence.md` §5.3)

---

# Test Plan

All tests in `engine/tests/test_session_resume.py` are integration tests against a SQLite in-memory DB. Each AC is exercised by a cold-resume test: create → pause → `del` all in-process objects → new `AsyncSession` → resume → assert.

- `TestSnapshotOnPause` (3 tests): snapshot row content, demote-prior-snapshot, `session_interrupted` event
- `TestResumeRestoresState` (3 tests): chart beat + context, knowledge state, relationship state
- `TestAc3NoSnapshotException` (2 tests): fallback to initial beat, negative test (snapshot present must not revert)
- `TestSnapshotHelpers` (1 test): `load_current_snapshot` returns the `is_current=True` row after two pauses

API-layer coverage in `api/tests/test_sessions_api.py`: `test_pause_writes_snapshot_and_interruption_event`, `test_resume_via_http_restores_status_from_db_only`.

---

# Risks and Unknowns

**Risks**:
- `_DEFAULT_INITIAL_BEAT_ID = "arrival"` is hardcoded in `engine/session/service.py:64`. Correct for Nightcap; incorrect for any second arc whose first beat has a different ID. Follow-up ticket created to derive it from `arc_definition.beats[0].beat_id`.

**Unknowns**:
- None open at ship time.

---

# Open Questions

- None. All questions resolved during implementation. See follow-up issue for the `_DEFAULT_INITIAL_BEAT_ID` fix.
