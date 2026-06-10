# AW-205: Nightcap Canonical Arc JSON

**Status**: Approved

**Author**: Codex | **Date**: 2026-06-10

---

# References

- Related ADRs: `docs/decisions/0001-scaffolding-audit.md`
- Architecture sections: `docs/architecture/09-developer-api.md`, `docs/architecture/15-development-guide.md`
- Related specs: `docs/specs/0023-aw-203-arcdefinition-schema-validation-core.md`, `docs/specs/0024-aw-204-dynamic-arcstatechart-generation.md`
- PRD sections: `docs/prd/02-requirements.md`
- Roadmap task: `docs/roadmap/tasks/AW-205-nightcap-canonical-arc-json.md`

---

# Overview

This spec defines the AW-205 canonical Nightcap arc JSON. The goal is to make `nightcap/arc.json` the schema-valid reference arc described by the Developer API architecture while preserving the three top-level beat graph used by AW-204.

---

# In Scope

- Canonicalize values in `nightcap/arc.json` against `docs/architecture/09-developer-api.md` Section 9.3
- Preserve the top-level beat IDs and graph shape: `introduction -> investigation -> reveal`
- Encode Nightcap support for 4 to 10 players
- Explicitly record the M6 first-proof target range of 4 to 6 players in schema-safe metadata
- Preserve Nightcap content rails and knowledge rules
- Add focused tests that prove the canonical arc properties

---

# Out Of Scope

- Changing the `ArcDefinition` schema
- Adding nested Nightcap sub-beats or an 8-beat internal phase model
- Changing the generated StateChart behavior from AW-204
- Implementing killer assignment runtime behavior
- Implementing pacing engine behavior
- Implementing safety pipeline behavior
- Adding prompts, routing changes, dependencies, database migrations, or API routes

---

# Acceptance Criteria

- [ ] `nightcap/arc.json` exists and validates against `ArcDefinition`
- [ ] `nightcap/arc.json` defines exactly the top-level beats `introduction`, `investigation`, and `reveal`
- [ ] The top-level beat graph remains `introduction -> investigation -> reveal`
- [ ] Nightcap content rails include prohibited categories, thematic warnings, and age floor
- [ ] Nightcap knowledge rules enable killer self-knowledge, narrator omniscience, and private clues until shared
- [ ] The arc supports 4 to 10 players through `min_players` and `max_players`
- [ ] The arc explicitly records the M6 first-proof target range of 4 to 6 players
- [ ] Canonicalization does not introduce schema, dependency, prompt, routing, safety, auth, or migration changes

---

# Test Plan

- Run `pytest engine/tests/test_arc_models.py engine/tests/test_arc_state.py engine/tests/test_harness_runner.py -q`
- Run `pytest engine/tests/ -q`
- Run `python -m ruff check engine/arc engine/harness engine/tests`
- Run `python -m ruff format --check engine/arc engine/harness engine/tests`
- Run `git diff --check`

---

# Risks And Unknowns

**Risks**:
- Adding too much Nightcap-specific metadata to the platform schema would blur the platform/game boundary. This implementation keeps the metadata inside existing flexible arc-level config dictionaries.
- Replacing the top-level three-beat graph with older 8-beat decision-log material would conflict with the AW-205 scope and the AW-204 generated chart path.

**Unknowns**:
- Later Nightcap runtime tasks may need a separate internal phase model. That should be added through a future task rather than folded into AW-205.

---

# Open Questions

- None for AW-205 implementation.
