# AW-250: Mini-game Content Resolution And Safety

**Status**: Approved

**Author**: Codex | **Date**: 2026-06-20 | **Last updated**: 2026-06-25
**Founder sign-off**: Approved 2026-06-25

---

# References

- Related ADRs: `docs/decisions/0009-mini-game-runtime-boundary.md`
- Related specs: `docs/specs/0046-aw-249-nightcap-mini-game-authoring-foundation.md`
- Architecture: `docs/architecture/06-model-routing.md`, `docs/architecture/10-content-safety.md`
- GitHub issue: #144

---

# Overview

Resolve authored, generative, and hybrid mini-game content into one immutable,
validated snapshot before deterministic execution.

---

# In Scope

- Content resolver selected by `content_mode`
- Existing routing abstraction for generative composition
- Content-rail and safety validation before resolved content is usable
- Aesthetic context as presentation input only
- Immutable resolved-content snapshot for AW-251

---

# Resolved Snapshot Contract

All three content modes resolve to the same runtime contract:

- `snapshot_schema_version`
- `game_id`
- `definition_version`
- `source_content_mode`
- `mechanic_type`
- `participation_mode`
- `min_players`
- `max_players`
- `duration_seconds`
- `rules`
- `behavioral_outputs`
- `clue_fallback`
- `resolved_content`
- `presentation`

`rules`, `behavioral_outputs`, and `clue_fallback` remain authored and
immutable at resolution time. Generative and hybrid resolution may populate
only `resolved_content` and `presentation`. Hybrid resolution may fill
placeholder copy or add compatible content fields, but it may not overwrite an
authored deterministic field.

---

# Out Of Scope

- Runtime state, scoring, clue unlocking, persistence, transport, or rendering
- Provider-specific code or model identifiers
- Any AI decision about canonical game state

---

# Acceptance Criteria

- [ ] All three content modes resolve to the same versioned snapshot contract.
- [ ] Generative resolution uses internal task and quality routing only.
- [ ] Invalid or unsafe resolved content cannot enter the runtime.
- [ ] Aesthetic adaptation cannot alter rules, scoring, or state transitions.
- [ ] Prompt and eval changes receive explicit approval before implementation.

---

# Test Plan

- Unit tests cover all modes and invalid resolved payloads.
- Mocked routing and safety tests spend no provider tokens.
- Approved eval cases cover schema adherence and safety regressions.
- Founder approved the AW-250 mini-game resolution prompt surface on
  2026-06-25. No eval changes are included in AW-250; eval work remains a
  separate approval-gated follow-up if this resolver contract needs dedicated
  regression coverage later.

---

# Risks and Unknowns

**Risks**: Prompt changes are product surface and require dedicated review.

**Unknowns**: Exact mechanic-specific content schemas are added only when their
mechanics are approved.

---

# Open Questions

- None at the platform-envelope level.
