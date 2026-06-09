# AW-203: ArcDefinition Schema And Validation Core

**Status**: Approved

**Author**: Codex | **Date**: 2026-06-09

---

# References

- Related ADRs: `docs/decisions/0001-scaffolding-audit.md`
- Architecture sections: `docs/architecture/09-developer-api.md`, `docs/architecture/15-development-guide.md`
- Related specs: `docs/specs/0005-scaffolding-remediation.md`
- PRD sections: `docs/prd/02-requirements.md`
- Roadmap task: `docs/roadmap/tasks/AW-203-arcdefinition-schema-and-validation-core.md`

---

# Overview

This spec defines the AW-203 implementation of the Pydantic arc definition schema and validation behavior. It tightens the existing scaffold models so invalid arc definitions fail before runtime execution.

---

# In Scope

- Tighten `engine/arc/models.py` Pydantic models for `ArcDefinition` and nested schema pieces
- Validate required fields through Pydantic model requirements
- Validate beat graph references against declared beat IDs
- Validate player count bounds and imposter minimum player count
- Validate top-level pacing weights sum to `1.0`
- Validate narrator behavior triggers against the documented trigger set
- Validate generative element keys against the documented allowed set
- Validate authored character mode requires authored characters
- Add focused unit tests for one valid arc and at least five invalid arc fixtures

---

# Out Of Scope

- Dynamic StateChart generation from arbitrary beat graphs
- Rewriting the full canonical Nightcap arc content
- Implementing API route handlers for `/v1/arcs/validate`
- Adding database schema, migrations, prompts, routing, safety, or telemetry behavior
- Adding dependencies

---

# Acceptance Criteria

- [ ] `ArcDefinition` and nested models cover the fields documented for AW-203
- [ ] Validation rejects missing required fields
- [ ] Validation rejects invalid beat graph references
- [ ] Validation rejects invalid player counts
- [ ] Validation rejects invalid pacing weight sums
- [ ] Validation rejects invalid narrator triggers
- [ ] Validation rejects invalid generative element keys
- [ ] Validation rejects authored character mode with no characters
- [ ] Validation rejects imposter mode with fewer than 3 players
- [ ] Tests include at least one valid arc fixture and at least five invalid arc fixtures tied to documented validation rules

---

# Test Plan

- Run `pytest engine/tests/test_arc_models.py engine/tests/test_arc_state.py -q`
- Run `pytest engine/tests/ -q` when a Python 3.11+ test environment with pytest is available
- Run `python -m ruff check engine/arc/models.py engine/tests/test_arc_models.py engine/tests/test_arc_state.py`

---

# Risks And Unknowns

**Risks**:
- `docs/architecture/15-development-guide.md` S15.4 still lists `aesthetic_mode`, while `docs/architecture/09-developer-api.md` and the decisions log say `aesthetic_mode` was replaced by `aesthetic_config`. The implementation treats `aesthetic_config` as canonical and keeps narrow compatibility for existing minimal fixtures that still use `aesthetic_mode`.
- Tightening validation can expose existing placeholder arc fixture gaps.

**Unknowns**:
- The full production Nightcap arc remains AW-205 scope.
- The API route implementation for `/v1/arcs/validate` belongs to later API work unless a task explicitly pulls it forward.

---

# Open Questions

- None for AW-203 implementation.
