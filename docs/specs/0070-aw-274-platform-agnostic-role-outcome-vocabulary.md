# Platform-Agnostic Role, Knowledge-Seeding, and Session-Outcome Vocabulary

**Status**: Draft

**Author**: Nico Janssen | **Date**: 2026-07-14

---

# References

- Related ADRs: `docs/decisions/` — a new ADR is required by this spec (schema + API + telemetry decision); see Open Questions.
- Architecture sections: `docs/architecture/03-arc-execution.md` (§3.4–3.7 role assignment), `docs/architecture/04-knowledge-graph.md` (knowledge seeding), `docs/architecture/11-telemetry.md` (§11.x `session_completed` payload)
- Related specs: `docs/specs/0065-aw-271-narrative-obligations-model.md` (generic session-context key pattern), `docs/specs/0068-game-experience-quality-bar.md`
- PRD sections: `docs/prd/` platform-agnosticism principle
- GitHub: issue #220 (this work), issue #219 (sibling: safety-layer terms), AW-206 (origin of the vocabulary), #213 (agnosticism pass that missed it)
- Guiding principles: `AGENTS.md` Architecture Principle #1 (surface/game agnosticism) and #4 (unified character/role model)

---

# Overview

Remove murder-mystery (Nightcap) narrative vocabulary that is baked into **shared platform code** — the arc schema, the session-end API contract, the `session_completed` telemetry payload, and the harness — and replace it with generic, arc-configurable mechanisms so a second game or third-party arc can express its own hidden roles, knowledge seeding, event timing, and session-resolution outcomes without editing platform code. Nightcap reproduces identical behavior via `nightcap/arc.json`.

---

# In Scope

The following game-specific identifiers on `main` (per issue #220), and their generalization:

**Arc schema — `engine/arc/models.py`**
- `GenerativeConfig.killer_assignment: bool` (L83) → generic generative role-assignment mechanism.
- `KnowledgeRuleSet.killer_knows_they_did_it: bool` (L111) → generic per-role knowledge-seeding rules.
- `ArcDefinition.murder_timing_range: List[int]` (L252) → generic timed-event config.

**Session-end outcome (API → service → telemetry)**
- `api/schemas/__init__.py` `killer_identified`, `api/routers/sessions.py`, `engine/session/service.py`, `engine/telemetry/session.py` (`session_completed` payload) → arc-declared named `resolution_outcomes`.

**Harness — `engine/harness/runner.py`, `engine/harness/scenario.py`**
- `_KILLER_ROLE`, `_KILLER_ASSIGNMENT_KEY`, `is_killer` → generic role key read from arc/runtime config.

**Config**
- `nightcap/arc.json` supplies the concrete Nightcap values so behavior is unchanged.

---

# Out of Scope

- **Safety-layer vocabulary** (`engine/safety/l1.py`, `l2.py`, `l3.py`: `"suspect"`, `"murder mystery"`, `"nightcap"`). Owned by issue #219 — changing safety heuristics is a separate hard-rule change and must not ride along here.
- `engine/mini_games/runtime.py:1133` — a comment only; cosmetic, no behavior.
- Any new gameplay capability. This is a refactor to a generic shape; it must be behavior-preserving for Nightcap.
- Migrating the web SDK's request field beyond the back-compat window (SDK follow-up tracked separately once the contract lands).

---

# Acceptance Criteria

- [ ] `git grep -iE "killer|murder" -- engine/ api/` returns nothing outside `engine/safety/` (owned by #219) and comments — no game-specific role/outcome vocabulary remains in shared schema, session lifecycle, telemetry, or harness.
- [ ] Nightcap behavior is unchanged via `nightcap/arc.json`: seeded killer assignment, reveal/knowledge seeding, event timing, and session-end outcome all reproduce today's results. A seeded harness replay yields identical role assignment and reveal state (AW-206 replay determinism preserved).
- [ ] A second arc declaring a *different* hidden role and a *different* resolution outcome validates and runs end-to-end with no platform code change (extends M5-C second-arc validation coverage).
- [ ] Session-end API accepts and the `session_completed` telemetry payload emits generic `resolution_outcomes`; the existing `killer_identified` field's back-compat is explicitly implemented and documented (dual-accept during a deprecation window, or migrated with SDK impact noted).
- [ ] Alembic/schema impact assessed: if any table column encodes the outcome, a migration is included and applies cleanly to empty and populated schemas; if it is JSON payload only, that is stated explicitly.
- [ ] An ADR captures the schema + API + telemetry decision and is referenced here before implementation begins.
- [ ] Tests updated to the generic shape; `engine/tests/test_aw256_beat_hardcode.py` (or a sibling guard test) extended to assert no role/outcome hardcodes remain in `engine/` outside `engine/safety/`.
- [ ] PR flags the schema + API + telemetry + cross-module hard rules for review; safety review not required (no safety-layer change).

---

# Test Plan

- **Unit tests**: arc schema validation for the new generic fields (valid arc, missing/duplicate role keys, unknown beat references for timed events); knowledge-seeding rule application at session start; generic outcome payload construction in telemetry.
- **Integration tests**: full seeded harness run for Nightcap producing identical role assignment + reveal state as `main` (golden/replay comparison); a synthetic second arc with a non-"killer" role assigned and a non-"killer_identified" outcome runs to session completion.
- **Contract tests**: session-end endpoint accepts both the legacy `killer_identified` field and the new `resolution_outcomes` during the deprecation window; telemetry payload asserted against the generic shape.
- **Guard test**: grep-style assertion that game vocabulary is absent from shared engine/api modules.

---

# Risks and Unknowns

**Risks**:
- **Live-path regression before Rehearsal 1 (AW-273)**: `killer_identified` is a live request/response field the web SDK sends today. A contract change on the session-end path risks breaking rehearsal. Mitigation: dual-accept back-compat, sequence relative to AW-273.
- **Behavior drift in seeded assignment**: generalizing the harness role constant could subtly change assignment or reveal state. Mitigation: golden replay comparison as an explicit AC.
- **Telemetry consumers**: any downstream reader keyed on `killer_identified` breaks if the payload key changes. Mitigation: emit both during deprecation, inventory consumers first.

**Unknowns**:
- Whether the session outcome is persisted as a typed column anywhere (drives whether a migration is needed) — resolve during design.
- Exact shape of the generic knowledge-seeding rule (list of `{role, seeded_knowledge}` vs. arc-keyed dict) — resolve in the ADR.

---

# Open Questions

- Q1: What is the canonical generic shape for `resolution_outcomes` — `Dict[str, bool]`, or a richer typed outcome object? (ADR decision.)
- Q2: Deprecation-window policy for `killer_identified` — dual-accept for how long, and who owns the SDK migration?
- Q3: Should generative role assignment be a single `role_assignment: bool` plus arc-named roles, or a list of role-assignment configs supporting multiple hidden roles? (Second-arc requirements inform this.)
- Q4: Sequencing relative to AW-273 (Rehearsal 1) — before or after the first real-human session?
