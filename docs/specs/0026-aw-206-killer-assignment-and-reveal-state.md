# AW-206: Killer Assignment And Reveal State

**Status**: Approved

**Author**: Codex | **Date**: 2026-06-10

---

# References

- Related ADRs: `docs/decisions/0001-scaffolding-audit.md`
- Architecture sections: `docs/architecture/03-arc-execution.md`, `docs/architecture/05-session-persistence.md`, `docs/architecture/15-development-guide.md`
- Related specs: `docs/specs/0024-aw-204-dynamic-arcstatechart-generation.md`, `docs/specs/0025-aw-205-nightcap-canonical-arc-json.md`
- PRD sections: `docs/prd/02-requirements.md`
- Roadmap task: `docs/roadmap/tasks/AW-206-killer-assignment-and-reveal-state.md`

---

# Overview

This spec defines the first runtime state support for Nightcap killer assignment and reveal constraints. The implementation keeps the platform state shape generic: Nightcap's killer is represented as a role assignment resolved from deterministic engine state, not as a Nightcap-specific field on the core `Session` model.

---

# In Scope

- Generic session runtime state for seeded generative resolution, role assignments, reveal state, and transition bypass logs
- Deterministic killer role assignment during the introduction setup path
- Harness-visible runtime state so seeded replay can compare killer assignment and reveal state
- Reveal transition enforcement through authored conditions
- Explicit host-privileged reveal bypass logging without mutating authored reveal conditions
- Focused unit tests for AW-206 acceptance criteria

---

# Out Of Scope

- Database schema changes or Alembic migrations
- API route changes
- Content event emission
- Persistent event-table writes
- Knowledge graph assertions for the killer fact
- Character behavior profile generation or augmentation
- LLM calls, prompts, routing, safety, telemetry, or cost-accounting changes
- UI or Nightcap web experience changes

---

# Acceptance Criteria

- [ ] Killer assignment occurs during the introduction setup path and stores the assigned killer in generic session runtime state.
- [ ] Killer assignment uses a seeded deterministic draw over the session participants.
- [ ] A seeded replay with the same participants produces the same killer assignment and reveal state.
- [ ] Normal reveal transition remains blocked until authored reveal conditions are satisfied.
- [ ] Reveal can fire through authored reveal conditions without a bypass log.
- [ ] Reveal can fire through a host-privileged bypass only when actor and reason metadata are present.
- [ ] Host bypass records source transition, target beat, bypassed authored conditions, reason, actor id, and deterministic sequence number.
- [ ] Host bypass does not silently set authored reveal conditions such as `core_clues_revealed`.
- [ ] Non-host or incomplete bypass payloads fail before reveal.

---

# Test Plan

- Unit tests: harness start assigns the killer in introduction setup and stores runtime state.
- Unit tests: same seed and same participants produce identical killer assignment and reveal state.
- Unit tests: reveal is blocked without authored reveal conditions.
- Unit tests: reveal succeeds with authored reveal condition and no bypass log.
- Unit tests: reveal succeeds with logged host bypass.
- Unit tests: non-host and missing-reason bypass payloads fail.
- Regression tests: existing harness scenario, batch, and arc state tests still pass.

Run:

- `python -m pytest engine/tests/test_harness_runner.py engine/tests/test_harness_scenarios.py engine/tests/test_harness_batch.py engine/tests/test_arc_state.py -q`
- `python -m pytest engine/tests/ -q`
- `python -m ruff check engine/session engine/harness engine/tests`
- `python -m ruff format --check engine/session engine/harness engine/tests`
- `git diff --check`

---

# Risks And Unknowns

**Risks**:
- If role assignment is modeled as a Nightcap-only `Session` field, future arcs inherit a murder-mystery assumption that should remain game-specific.
- If host bypass mutates authored conditions, later replay cannot distinguish a legitimate clue-complete reveal from an intervention.

**Unknowns**:
- The durable persistence shape for runtime state is deferred to M3. `docs/architecture/05-session-persistence.md` says durable arc position and session history will live through `arc_beat_states` and `events`, but AW-206 records runtime and harness state only.

---

# Open Questions

- None for AW-206 implementation.
