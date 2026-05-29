# Scaffolding Remediation

**Status**: Done

**Author**: Codex | **Date**: 2026-05-21

---

# References

- Related ADRs: `docs/decisions/0001-scaffolding-audit.md`
- Architecture sections: `docs/architecture/06-model-routing.md`, `docs/architecture/15-development-guide.md`
- Related specs: `docs/specs/0000-template.md`
- PRD sections: `docs/prd/02-requirements.md`, `docs/prd/03-scope.md`, `docs/prd/04-non-goals.md`

---

# Overview

Align the current scaffold to the technical architecture by fixing the high-reversal-cost arc execution divergences first, then closing the remaining routing, repo hygiene, and agent-workflow gaps that are still active.

---

# In Scope

- Move arc execution code into `engine/arc/`
- Replace scaffold arc dataclasses with architecture-aligned Pydantic models
- Remove the parallel manual `ArcStateMachine` wrapper and keep a single `StateChart`-based implementation
- Add `engine/session/models.py`
- Fill routing-table task and fallback gaps and update eval coverage
- Add standard Python gitignore exclusions and remove tracked Python cache artifacts
- Add minimal `nightcap/arc.json` and Alembic scaffolding
- Align agent instruction files with the current repo layout and toolchain

---

# Out of Scope

- Full production implementation of dynamic arc-chart generation from arbitrary arc definitions
- Full database schema implementation or first migration contents
- Merge-blocking behavior for the eval workflow

---

# Acceptance Criteria

- [x] Arc execution code lives under `engine/arc/` and tests import from the new module path
- [x] `ArcDefinition` and `BeatDefinition` are Pydantic models with the required architecture-facing fields
- [x] The manual `ArcStateMachine` wrapper is removed and tests target the single `StateChart`-based implementation
- [x] `engine/session/models.py` exists with Session-facing Pydantic models
- [x] `config/routing_table.json` includes `killer_assignment`, `narrator_bridge`, and fallback entries
- [x] Eval cases enforce the expanded routing table
- [x] `.gitignore` excludes standard Python cache artifacts and tracked `.pyc` files are removed
- [x] `nightcap/arc.json` and baseline Alembic scaffolding exist
- [x] `AGENTS.md` and `CLAUDE.md` no longer instruct contributors to use missing or incorrect paths/commands
- [x] Engine tests and routing evals pass locally

---

# Test Plan

- Run `pytest engine/tests`
- Run `pytest evals/runners/test_routing_evals.py -q`
- Validate updated workflow/config files as needed with lightweight local checks
- Manually verify the audit’s active findings against the resulting repo state

---

# Risks and Unknowns

**Risks**:
- Refactoring imports from `engine.arc_state` to `engine.arc.arc_state` may expose any hidden downstream dependency on the old path
- The architecture references some nested arc-schema components without fully defining every sub-schema in the checked-in docs, so some placeholder-typed fields may still be intentionally broad

**Unknowns**:
- Whether the future dynamic chart-generation implementation will keep the placeholder `StateChart` shape intact or replace it entirely once arbitrary arc loading is implemented

---

# Open Questions

- None after user approval of the remediation order
