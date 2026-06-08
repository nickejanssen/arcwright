# AW-201: M2-M6 Roadmap And Tracker Bootstrap

**Status**: Approved

**Author**: Codex | **Date**: 2026-06-08

---

# References

- Related ADRs: `docs/decisions/0001-scaffolding-audit.md`, `docs/02-Decisions-Log-Additions-May2026.md`
- Architecture sections: `docs/architecture/01-overview.md` through `docs/architecture/15-development-guide.md`, plus `docs/architecture/supplemental-schemas.md`
- Related specs: `docs/specs/0006-roadmap-organization.md`, `docs/specs/0007-roadmap-tracker-alignment.md`, `docs/specs/0008-github-tracker-reproducibility.md`
- PRD sections: `docs/prd/01-overview.md`, `docs/prd/02-requirements.md`, `docs/prd/03-scope.md`, `docs/prd/04-non-goals.md`

---

# Overview

This spec defines the documentation and GitHub tracker bootstrap required to move Arcwright from M1 complete to M6 first qualifying Nightcap playtests. It creates the roadmap, task, spec, manifest, tracker config, and live GitHub issue structure only. It does not implement product code.

---

# In Scope

- Create M2-M6 epic documentation under `docs/roadmap/epics/`
- Create AW-201 through AW-244 task documentation under `docs/roadmap/tasks/`
- Update `docs/roadmap/index.json` after docs exist
- Update roadmap operational docs and tracker config for M2-M6
- Create or update GitHub milestones and labels required by M2-M6
- Create GitHub epic and task issues with novice-readable, technically actionable bodies
- Record live GitHub issue numbers and URLs back into `docs/roadmap/index.json`

---

# Out Of Scope

- Product code in `engine/`, `api/`, `sdk/`, `dashboard/`, `nightcap/`, or `migrations/`
- Dependency changes
- Schema or migration implementation
- Prompt, routing, safety, or eval behavior changes
- Modifying or reopening closed M1 issues
- Implementing M4 Nightcap web experience runtime code before AW-202 records the runtime contract

---

# Acceptance Criteria

- [ ] Roadmap docs exist for every planned M2-M6 epic and every AW-201 through AW-244 task
- [ ] Every task doc and GitHub issue includes Plain-English Summary, Why This Matters, Player Impact, Business Value, Technical Scope, Acceptance Criteria, Tests/Verification, Dependencies, Must Not Do, Architecture References, and Playtest Relevance
- [ ] `docs/roadmap/index.json` validates as JSON and contains all new milestones, epics, tasks, dependencies, paths, and live GitHub references
- [ ] GitHub labels `M2`, `M3`, `M4`, `M5`, and `M6` exist
- [ ] GitHub milestone `M6: First Qualifying Sessions` exists, and M2-M5 milestone titles/descriptions match the roadmap
- [ ] GitHub epic and task issues are created for every new roadmap item without duplicating or modifying closed M1 issues
- [ ] M4 implementation tasks are explicitly dependent on AW-202 and tied to the Nightcap web experience runtime decision

---

# Test Plan

- Validate JSON files with a parser
- Inspect generated roadmap docs for required sections and references
- Confirm live GitHub milestones, labels, and issues exist
- Confirm `git status` contains only intended documentation and tracker config changes
- Run repository docs or lightweight checks that apply to non-code changes

---

# Risks And Unknowns

**Risks**:
- GitHub tracker creation can drift from docs if live issue numbers are not written back into the manifest
- M4 implementation detail can become speculative if AW-202 is not treated as a blocker
- M6 can be misread as a formality instead of a product proof gate

**Unknowns**:
- The Nightcap web experience runtime is resolved by AW-202
- Nightcap trademark clearance remains outside this product-code tracker unless separately requested
- Pricing remains a product decision, so gross-margin tasks must separate actual logged cost from open revenue assumptions

---

# Open Questions

- None for AW-201 implementation. Later tasks carry their own open decisions where the repo docs mark them unresolved.
