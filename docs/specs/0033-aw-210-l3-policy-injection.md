# AW-210 L3 Policy Injection And Neutral Bridge

**Status**: Approved

**Author**: Claude Sonnet 4.6 | **Date**: 2026-06-14

---

# References

- Architecture sections: `docs/architecture/10-content-safety.md S10.4`
- Related specs: `docs/specs/0032-aw-209-l2-pre-generation-classification.md`, `docs/specs/0028-aw-208-l1-hard-stops.md`
- PRD sections: `docs/prd/01-overview.md`
- GitHub issue: `https://github.com/nickejanssen/arcwright/issues/63`

---

# Overview

This spec defines Layer 3 in-generation policy injection for the Arcwright content safety system. L3 inserts a plain-language rules block into every main AI generation prompt, telling the model what it must not write based on the arc's `content_rails` configuration. A neutral bridge sentinel is provided for callers that need to signal an L3-level block.

---

# In Scope

- Add `engine/safety/l3.py` with `build_l3_policy_block`, `build_nightcap_l3_policy_block`, `inject_l3_policy_block`, and the `NEUTRAL_L3_BRIDGE` / `L3_BLOCK_SENTINEL` sentinel values.
- Export new L3 symbols from `engine/safety/__init__.py`.
- Integrate `inject_l3_policy_block` into `engine.routing.logging.generate` so the policy block is injected after L2 approval and before the main generation call.
- Add `content_rails` and `nightcap_mode` parameters to `generate()` so callers can supply arc-specific rails.
- Tests proving that the Nightcap L3 policy is sourced from arc content rails (not hardcoded), that the policy block appears in the main generation messages, and that the neutral bridge sentinel is correct.

---

# Out of Scope

- Dashboard safety visibility (AW-10.5, future work).
- Post-generation L4 filtering (deferred per architecture decision).
- New provider, model, dependency, schema, or migration changes.
- Arc coordinator wiring that passes `content_rails` from a running session (future integration task).

---

# Design

`inject_l3_policy_block` is called inside `generate()` after L2 classification approves the prompt and before `route_generation` is called for the main task. It prepends a new system message containing the policy block text. The original messages list is never mutated.

`build_nightcap_l3_policy_block(content_rails)` combines arc-level `prohibited_categories` with Nightcap-specific extra prohibitions. This two-level design ensures:
- Arc designers control their custom prohibitions via `content_rails`.
- Nightcap-specific rules (no graphic murder depiction, no sexual content, etc.) are always present for Nightcap sessions without the designer having to enumerate them.

`safety_classification` tasks are exempt from L3 injection (same exemption as L2 classification) to avoid corrupting the classifier prompt.

---

# Acceptance Criteria

- [x] Every main generation prompt includes an L3 policy block derived from arc content rails (when `content_rails` is supplied).
- [x] Blocked generation emits a neutral bridge event so the session can continue (sentinel `NEUTRAL_L3_BRIDGE` and `L3_BLOCK_SENTINEL` provided).
- [x] Tests prove Nightcap-specific L3 policy is sourced from arc rails rather than hardcoded platform policy.

---

# Test Plan

- Unit tests: `build_l3_policy_block` contains arc prohibited categories.
- Unit tests: `build_nightcap_l3_policy_block` contains arc categories AND Nightcap-specific rules.
- Unit tests: `inject_l3_policy_block` prepends policy, does not mutate originals, no-ops on None or empty rails.
- Unit tests: `build_l3_blocked_route_result` sentinel values are correct.
- Integration tests: `generate()` with `content_rails` passes policy block to main route call.
- Integration tests: `generate()` in Nightcap mode passes Nightcap-specific policy.
- Integration tests: `generate()` without `content_rails` passes messages unmodified.
- Integration tests: `safety_classification` task type skips L3 injection.
- Commands:
  - `python -m pytest engine/tests/test_safety_l3.py -q`
  - `python -m pytest engine/tests/ -q`
  - `python -m ruff check engine/safety engine/routing engine/tests`
  - `python -m ruff format --check engine/safety engine/routing engine/tests`

---

# Risks and Unknowns

**Risks**:
- The arc coordinator is not yet wired to pass `content_rails` into `generate()`. Until it is, L3 injection is a no-op at runtime. Tests cover the injection path via direct parameter passing.

**Unknowns**:
- None blocking AW-210 implementation.

---

# Open Questions

- None blocking implementation.
