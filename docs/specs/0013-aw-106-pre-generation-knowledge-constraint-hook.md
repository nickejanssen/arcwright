# AW-106 Pre-generation Knowledge Constraint Hook

**Status**: Draft

**Author**: Codex | **Date**: 2026-05-31

---

# References

- Architecture sections: `docs/architecture/04-knowledge-graph.md` (§4.2, §4.3), `docs/architecture/07-character-behavior.md` (§7.3), `docs/architecture/11-telemetry.md` (§11.3)
- Related specs: `docs/specs/0011-aw-103-sqlalchemy-orm-models.md`, `docs/specs/0012-aw-104-first-full-alembic-migration.md`
- PRD sections: `docs/prd/02-requirements.md` (Principle 5, Character management, Knowledge graph)
- Roadmap task: `docs/roadmap/tasks/AW-106-pre-generation-knowledge-constraint-hook.md`

---

# Overview

Define the single engine hook that assembles prompt-facing knowledge constraints for AI character generation. The hook is session-scoped, queries the active knowledge state for one character, derives both permitted and blocked facts for that session, and returns them in a stable deterministic order.

---

# In Scope

- Add one sanctioned function for generation-time knowledge constraint assembly
- Return a structured generation-context object rather than raw ORM rows
- Include both "knows" and "does not know" fact sets for the current session scope
- Include confidence and provenance-chain length for known facts
- Enforce stable ordering for cache-friendly prompt assembly
- Add unit tests for scoping, exclusion, and ordering behavior

---

# Out of Scope

- Full character behavior pipeline implementation from architecture §7.3
- Prompt templating or model invocation changes
- Telemetry emission plumbing beyond returning data needed by later telemetry work
- Relationship graph, social pressure, or safety-layer integration
- Schema or migration changes

---

# Proposed Interface

`build_character_generation_context(session, *, session_id, character_id) -> CharacterGenerationContext`

Notes:

- `session_id` and `character_id` are both mandatory. `character_id` alone is not sufficient to scope knowledge safely.
- The function is the sanctioned generation-facing chokepoint. Raw knowledge graph queries remain internal building blocks, not prompt-context APIs.
- The return value is a structured object suitable for direct prompt assembly later.

---

# Return Shape

`CharacterGenerationContext` should contain:

- `session_id`
- `character_id`
- `known_facts`: ordered structured items for facts currently known by the character
- `unknown_facts`: ordered structured items for facts in the same session not currently known by the character

Each `known_facts` item should contain:

- `fact_id`
- `fact_type`
- `fact_content`
- `confidence`
- `provenance_chain`
- `provenance_chain_length`

Each `unknown_facts` item should contain:

- `fact_id`
- `fact_type`
- `fact_content`

Ordering must be deterministic so repeated calls over unchanged data produce byte-stable prompt inputs.

---

# Ordering Rules

To satisfy cache friendliness and avoid caller divergence, the hook owns ordering:

- `known_facts` ordered by `asserted_at`, then `fact_id`
- `unknown_facts` ordered by `fact_id`

If implementation constraints require a different deterministic tie-breaker discovered in code review, it must remain fully stable and be covered by tests.

---

# Acceptance Criteria

- [ ] A single sanctioned function accepts `session_id` and `character_id` and returns that character's complete current generation-time knowledge context
- [ ] The returned context includes only facts currently known by that character in that session, plus the session-scoped facts the character does not know
- [ ] The sanctioned interface is the only generation-context assembly path exposed for character generation work
- [ ] Returned known and unknown fact lists are stable and ordered deterministically
- [ ] Unit tests prove the hook never returns a known fact outside the character's active state

---

# Test Plan

- Unit tests: character scoping within a session
- Unit tests: session scoping across identical character IDs in different sessions
- Unit tests: superseded knowledge records excluded from known facts
- Unit tests: session facts absent from a character's knowledge appear in unknown facts
- Unit tests: repeated calls return the same ordered fact IDs for unchanged fixtures

---

# Risks and Unknowns

**Risks**:
- Exposing raw `KnowledgeState` rows as the public return type would push prompt-shaping and ordering logic into callers, undermining the chokepoint requirement.
- Forgetting session-wide fact enumeration would make the negative constraint block impossible to build later without bypass logic.

**Unknowns**:
- None within AW-106 scope after contract clarification on 2026-05-31.

---

# Open Questions

- None. Contract clarified with user before implementation.
