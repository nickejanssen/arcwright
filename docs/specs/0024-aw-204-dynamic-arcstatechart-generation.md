# AW-204: Dynamic ArcStateChart Generation

**Status**: Approved

**Author**: Codex | **Date**: 2026-06-09

---

# References

- Related ADRs: `docs/decisions/0001-scaffolding-audit.md`
- Architecture sections: `docs/architecture/03-arc-execution.md`, `docs/architecture/15-development-guide.md`
- Related specs: `docs/specs/0023-aw-203-arcdefinition-schema-validation-core.md`
- PRD sections: `docs/prd/02-requirements.md`
- Roadmap task: `docs/roadmap/tasks/AW-204-dynamic-arcstatechart-generation.md`

---

# Overview

This spec defines dynamic `ArcStateChart` generation from validated `ArcDefinition.beat_graph` data. It replaces the remaining static Nightcap-only chart shape with a generated `python-statemachine` StateChart while keeping authored beat transitions deterministic and engine-owned.

---

# In Scope

- Generate a `python-statemachine` `StateChart` subclass from an `ArcDefinition`
- Create one top-level state per beat definition
- Create deterministic transition events for every beat graph edge
- Support linear, branching, convergence, and loop graph patterns
- Enforce source beat `exit_conditions` and target beat `entry_conditions` through StateChart transition guards
- Preserve runtime context helpers used by the harness and later coordinator work
- Update the harness to resolve generated chart events without a hardcoded Nightcap event allowlist
- Add focused tests for graph patterns, guard blocking, guard acceptance, and no LLM involvement

---

# Out Of Scope

- Nested Nightcap sub-beats, compound states, or parallel investigation internals
- Pacing engine behavior
- Killer assignment or reveal state mutation
- API route handlers
- Database schema, migrations, prompts, routing, safety, or telemetry behavior
- New dependencies

---

# Acceptance Criteria

- [ ] Generated StateCharts support linear beat graphs from `ArcDefinition` data
- [ ] Generated StateCharts support branching beat graphs from `ArcDefinition` data
- [ ] Generated StateCharts support convergence beat graphs from `ArcDefinition` data
- [ ] Generated StateCharts support loop beat graphs from `ArcDefinition` data
- [ ] Generated transition guards enforce authored source `exit_conditions`
- [ ] Generated transition guards enforce authored target `entry_conditions`
- [ ] Tests prove canonical state transitions are StateChart events, not custom graph traversal
- [ ] Tests prove canonical state transitions do not call LLM routing or generation
- [ ] Nightcap harness still reaches `reveal` through the generated top-level beat graph

---

# Test Plan

- Run `pytest engine/tests/test_arc_state.py engine/tests/test_harness_runner.py -q`
- Run `pytest engine/tests/ -q`
- Run `python -m ruff check engine/arc/arc_state.py engine/harness/runner.py engine/tests/test_arc_state.py engine/tests/test_harness_runner.py`
- Run `git diff --check`

---

# Risks And Unknowns

**Risks**:
- Existing M1 harness fixtures used the handcrafted Nightcap sub-beat event names. AW-204 intentionally shifts the canonical harness path to generated top-level beat transitions.
- Guard condition semantics are still minimal because condition evaluation sources beyond chart context are future session coordinator work.

**Unknowns**:
- Whether a later Nightcap-specific implementation will model nested sub-beats as authored beat IDs or add a separate sub-beat schema.

---

# Open Questions

- None for AW-204 implementation.
