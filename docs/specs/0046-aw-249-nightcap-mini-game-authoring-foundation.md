# AW-249: Nightcap Mini-game Authoring Foundation

**Status**: Approved

**Author**: Codex | **Date**: 2026-06-20

---

# References

- Related ADRs: `docs/decisions/0009-mini-game-runtime-boundary.md`
- Architecture sections: `docs/architecture/03-arc-execution.md`, `docs/architecture/08-event-system.md`, `docs/architecture/15-development-guide.md`
- PRD sections: `docs/prd/02-requirements.md`
- Product decision: `docs/product/decisions-log.csv` D-058 and D-059
- GitHub issue: #143

---

# Overview

Create a hosting-neutral authoring location, typed Python schema, package
loader, template, and non-shipping fixtures for Nightcap mini-games.

---

# In Scope

- `engine/mini_games/` manifest, definition, binding, and loader contracts
- `nightcap/mini_games/` authoring guide, template, and three fixtures
- Typed `BeatDefinition.mini_games` bindings
- Validation for IDs, semantic versions, package paths, package consistency,
  composition mode, behavioral declarations, delayed clue fallback, and
  production-catalog lifecycle filtering
- Canonical roadmap, decision, and future specification chain

---

# Out Of Scope

- Runtime execution, timers, submissions, scoring, outcomes, or clue unlocking
- Database tables or migrations
- API endpoints, ContentEvent changes, SDK methods, or browser rendering
- Cloudflare implementation or dependencies
- Shipping mini-game content or production arc bindings

---

# Acceptance Criteria

- [ ] The template and individual, collaborative, and group fixtures validate.
- [ ] Duplicate IDs, invalid versions, missing definitions, unsafe paths, and
  invalid lifecycle values fail validation.
- [ ] The canonical Nightcap arc still validates with typed mini-game bindings.
- [ ] Reserved template and fixture directories, plus non-`active`
  authoring packages, are excluded from the production catalog loader.
- [ ] No fixture or template is referenced by `nightcap/arc.json`.
- [ ] No dependencies, migrations, AI provider or model strings, secrets,
  runtime behavior, API, SDK, or Cloudflare code are added.
- [ ] Roadmap Markdown, `index.json`, specs, GitHub issues, dependencies, and
  ADRs agree.

---

# Test Plan

- Unit tests validate the template, all three fixtures, invalid inputs,
  duplicate IDs, missing files, lifecycle filtering, and reserved-directory
  exclusion.
- Arc model tests prove bindings are typed and the canonical arc remains valid.
- Run the focused tests, full engine suite, Ruff lint and format checks, and
  mypy named by GitHub issue #143.

---

# Risks and Unknowns

**Risks**:

- Future runtime requirements may require a new schema version. Semantic
  versioning and `schema_version` make that extension explicit.
- Browser prototypes may drift before AW-253. The authoring guide marks them as
  presentation-only and non-authoritative.

**Unknowns**:

- The first production mini-game is intentionally unselected and belongs to
  AW-254.

---

# Open Questions

- None for AW-249.
