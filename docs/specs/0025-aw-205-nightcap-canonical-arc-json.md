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

This spec defines the AW-205 canonical Nightcap arc JSON. The goal is to make `nightcap/arc.json` the schema-valid reference arc described by the Developer API architecture while using the canonical eight Nightcap Story Circle beats from `docs/story-bibles/nightcap-murder-mystery.md` Section 4.

---

# In Scope

- Canonicalize values in `nightcap/arc.json` against `docs/architecture/09-developer-api.md` Section 9.3
- Encode the eight Nightcap Story Circle beats: `arrival`, `body`, `opening_move`, `dig`, `thread`, `reckoning`, `close`, and `truth`
- Encode the v1 four-human-player floor and larger supported human player counts
- Explicitly record the M6 first-proof target range of 4 to 6 human players in schema-safe metadata
- Explicitly record that 2-3 player support requires v1.1 interrogatable AI participants
- Preserve Nightcap content rails and knowledge rules
- Add focused tests that prove the canonical arc properties

---

# Out Of Scope

- Changing the `ArcDefinition` schema
- Adding nested Nightcap sub-beats beyond the eight canonical Story Circle beats
- Changing the generated StateChart behavior from AW-204
- Implementing killer assignment runtime behavior
- Implementing pacing engine behavior
- Implementing safety pipeline behavior
- Adding prompts, routing changes, dependencies, database migrations, or API routes

---

# Acceptance Criteria

- [ ] `nightcap/arc.json` exists and validates against `ArcDefinition`
- [ ] `nightcap/arc.json` defines exactly the eight canonical Nightcap Story Circle beats
- [ ] The beat graph follows the Story Circle sequence through `truth`
- [ ] Nightcap content rails include prohibited categories, thematic warnings, and age floor
- [ ] Nightcap knowledge rules enable killer self-knowledge, narrator omniscience, and private clues until shared
- [ ] The arc supports the v1 four-human-player floor through `min_players`
- [ ] The arc explicitly records the M6 first-proof target range of 4 to 6 human players
- [ ] The arc records that 2-3 player support is deferred to v1.1 interrogatable AI participants
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
- Encoding Nightcap's eight-beat Story Circle as a platform-wide beat-count assumption would violate D-053. Keep the eight-beat graph Nightcap-specific.

**Unknowns**:
- Later Nightcap runtime tasks may need a separate internal phase model. That should be added through a future task rather than folded into AW-205.

---

# Open Questions

- None for AW-205 implementation.
