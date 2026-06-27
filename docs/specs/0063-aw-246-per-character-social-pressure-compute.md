# AW-246: Per-Character Social Pressure Compute

**Status**: Done

**Author**: Nicolas Janssen | **Date**: 2026-06-27

---

# References

- Architecture: `docs/architecture/07-character-behavior.md §7.3, §7.4`
- Roadmap task: `docs/roadmap/tasks/AW-246-per-character-social-pressure-compute.md`
- Depends on: AW-211 (`behavior_profile` with `crumble_threshold`), AW-213 (`InitiativeScheduler`), AW-207 (`dramatic_tension_score` pattern)
- Implemented in: PR #193

---

# Overview

Adds a per-character `social_pressure` score — distinct from the session-level `dramatic_tension_score` — computed as the §7.4 weighted sum of recent accusations, directed questions, and alliance isolation. Wires the score into initiative threshold modulation and prompt assembly so killer behavior shifts under suspicion without confessing.

---

# In Scope

- `engine/characters/pressure.py`: `SocialPressureSignals`, `SocialPressureWeights`, `compute_social_pressure(signals, weights) -> float`
- `BehaviorProfileContext.crumble_threshold` field extracted from `behavior_profile.secrets` (minimum across secrets that declare it; default 1.0)
- `build_dialogue_messages` and `build_npc_npc_messages`: `[SOCIAL PRESSURE]` block injected between relationship context and scene block when `social_pressure >= crumble_threshold`
- `InitiativeScheduler.evaluate`: `social_pressure_by_character` parameter; `modulate_threshold_for_pressure` function
- Propagation through `generate_character_dialogue`, `generate_npc_npc_exchange`, `schedule_initiative_tasks`, `_run_initiative_action`
- Gaze-signal slot (zero-weighted at v1)

---

# Out of Scope

- Gaze-signal collection: slot exists in `SocialPressureSignals` but is zero-weighted until a surface emits it.
- Caller-side computation of `accusation_weight`, `question_intensity`, `alliance_isolation` from session events — those are session coordinator responsibilities.
- Changes to `crumble_threshold` semantics or the `behavior_profile` JSON schema.
- New routing-table entries or model strings.
- Schema migrations.

---

# Acceptance Criteria

- [x] `compute_social_pressure` returns a float 0.0–1.0 as a weighted sum aligned with §7.4 inputs (accusations×0.5, directed_questions×0.3, alliance_isolation×0.2, gaze×0.0).
- [x] Initiative scheduling accepts per-character social-pressure input and modulates effective threshold via `base × (1 − pressure)`.
- [x] Generation prompt assembly includes an explicit `[SOCIAL PRESSURE]` block when `social_pressure >= crumble_threshold`.
- [x] Tests prove pressure crossing `crumble_threshold` changes the assembled prompt; sub-threshold pressure leaves it unchanged.
- [x] No regression on AW-213 tests; callers that pass no pressure argument see identical behavior.

---

# Test Plan

- **Unit tests** (`engine/tests/test_social_pressure.py`, 22 tests): weighted-sum compute, clamping, gaze zero-weight, custom weights, threshold modulation formula, scheduler wiring (enable/disable by pressure), `crumble_threshold` extraction from secrets, prompt block inclusion/exclusion at/above/below threshold for both `build_dialogue_messages` and `build_npc_npc_messages`, block ordering.
- **End-to-end tests** (`engine/tests/test_initiative.py`, 2 tests): `generate_npc_npc_exchange` with mocked `generate` — verifies `[SOCIAL PRESSURE]` block appears in the assembled prompt when initiator is above threshold, and is absent when below.
- **AW-213 regression**: existing initiative test suite passes with no modifications.
- **Full suite**: 403 passed, 1 pre-existing skip, 0 failures.

---

# Risks and Unknowns

**Risks**:
- Misconfigured arc JSON with non-numeric `crumble_threshold` silently falls back to 1.0 (character never shows pressure). Mitigated by `logger.warning` in `_build_behavior_profile_context` when a non-numeric value is detected.

**Unknowns**:
- Caller-side computation of pressure signals from session event history is not yet implemented. The compute function is ready; callers will integrate it when the session coordinator is built.
