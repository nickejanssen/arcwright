# AW-211 Behavior Profile Assembly

**Status**: Approved

**Author**: Codex
**Date**: 2026-06-14

---

# References

- Related roadmap task: `docs/roadmap/tasks/AW-211-behavior-profile-assembly.md`
- Architecture sections: `docs/architecture/07-character-behavior.md` S7.2, `docs/architecture/15-development-guide.md` S15.9
- Related specs: `docs/specs/0025-aw-205-nightcap-canonical-arc-json.md`, `docs/specs/0026-aw-206-killer-assignment-and-reveal-state.md`
- PRD sections: `docs/prd/01-overview.md`

---

# Overview

Define the runtime character context assembly needed for AW-211. The character behavior engine must expose behavior profile data and live relationship dispositions without creating separate human and AI character models.

---

# In Scope

- Extend generation-time character context assembly in `engine/characters`.
- Include personality, goals, secrets, tells, and live relationship dispositions.
- Preserve the existing pre-generation knowledge context in the same runtime context.
- Surface participant control mode from session participation without changing the platform `Character` object model.
- Add focused tests for killer and non-killer character context assembly.

---

# Out of Scope

- Behavior profile generation or augmentation.
- AI dialogue generation.
- Knowledge-constrained dialogue pipeline work reserved for AW-212.
- Schema or migration changes.
- Model routing, provider selection, prompt, or safety pipeline changes.
- Nightcap-specific rendering, API, dashboard, or SDK changes.

---

# Acceptance Criteria

- [ ] Runtime character context includes personality, goals, secrets, tells, and relationship dispositions.
- [ ] Human-controlled and AI-driven characters use the same platform character object model.
- [ ] Tests cover context assembly for killer and non-killer characters.

---

# Test Plan

- Unit tests cover behavior profile context assembly for a killer character.
- Unit tests cover behavior profile context assembly for a non-killer AI character.
- Existing knowledge-context tests continue to pass.
- Run `python -m pytest engine/tests/test_character_generation_context.py -q`.
- Run `pytest engine/tests/ -q` with a Python 3.11+ runtime.
- Run `python -m ruff check engine/characters engine/tests`.
- Run `python -m ruff format --check engine/characters engine/tests`.

---

# Risks and Unknowns

**Risks**:
- Relationship data could be mistaken for static behavior profile data. The implementation must read live `relationships` rows.
- Participant control mode could be misused as a separate character model. It must remain context about control source only.

**Unknowns**:
- None for AW-211.

---

# Open Questions

- None.
