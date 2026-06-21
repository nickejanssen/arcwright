# AW-251: Mini-game Runtime, Persistence, And Clue Gating

**Status**: Draft

**Author**: Codex | **Date**: 2026-06-20

---

# References

- Related ADRs: `docs/decisions/0009-mini-game-runtime-boundary.md`
- Related specs: `docs/specs/0047-aw-250-mini-game-content-resolution-and-safety.md`
- Architecture: `docs/architecture/03-arc-execution.md`, `docs/architecture/05-session-persistence.md`
- GitHub issue: #145

---

# Overview

Implement deterministic mini-game runs with authoritative timing, idempotent
submissions, scoring, clue gating, behavioral outputs, and pause/resume support.

---

# In Scope

- Run states: pending, active, completed, timed out, and cancelled
- Server-authored deadlines and an injected clock for tests
- Optimistic revision checks and idempotent submission IDs
- `mini_game_runs` canonical state with an immutable definition snapshot
- Append-only `mini_game_submissions` participant actions
- Neutral metrics and deterministic game-scoped observations
- Knowledge assertion after deterministic clue-unlock resolution
- Delayed full or reduced clue fallback plus logged host override

---

# Out Of Scope

- Content generation, API, SDK, rendering, or cross-session behavior analysis
- Killer assignment input in v1

---

# Acceptance Criteria

- [ ] Python exclusively decides lifecycle, validity, scoring, outcome, and clue
  release.
- [ ] Duplicate and concurrent submissions cannot corrupt run state.
- [ ] Pause/resume restores the definition snapshot, revision, deadline, and
  accepted submissions.
- [ ] Timeout follows the authored fallback and preserves a solvable clue path.
- [ ] v1 behavioral output is not read by killer assignment or another session.
- [ ] The migration applies and rolls back in supported test environments.
- [ ] Unknown `mechanic_type` values are rejected at runtime resolution before
  any run is created. Dispatch is keyed on a closed registry of approved
  mechanic implementations.
- [ ] A `derived` behavioral output is rejected if no non-derived sibling in the
  same scope can express it. Derivation is validated against the resolved
  definition snapshot, not at authoring time.

---

# Test Plan

- Unit tests use an injected clock for all lifecycle transitions.
- Integration tests cover persistence, concurrency, idempotency, knowledge
  assertion, pause/resume, timeout, and host override.
- Migration review and full engine/API suites are required.

---

# Risks and Unknowns

**Risks**: This task changes database schema and multiple engine modules, so it
requires the repository's explicit migration and design review.

**Unknowns**: Mechanic-specific scoring implementations remain separate plugins.

---

# Open Questions

- None for the generic runtime contract.
