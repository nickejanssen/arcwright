# Repository Structure and Python Project Setup

**Status**: Done

**Author**: Codex | **Date**: 2026-05-29

---

# References

- Related ADRs: `docs/decisions/0001-scaffolding-audit.md`
- Architecture sections: `docs/architecture/02-technology-stack.md`, `docs/07-Technical-Architecture-v1 3 35db7de354a881618e59e65c8e12caf6.md` Sections 2.3 and 2.4
- Related specs: `docs/specs/0000-template.md`, `docs/specs/0005-scaffolding-remediation.md`
- PRD sections: `docs/prd/02-requirements.md`, `docs/prd/03-scope.md`

---

# Overview

Add the missing Python workspace scaffolding for AW-101 without replacing the existing engine and API spine that is already present in the repository.

---

# In Scope

- Add a root `pyproject.toml` for pinned Python dependency groups and shared tooling config
- Add a task runner interface for `lint`, `type`, `test`, and `migrate`
- Scaffold the four top-level locked test directories from Architecture S2.9
- Preserve the current `engine/` and `api/` package layout if it already satisfies the issue

---

# Out of Scope

- Changes to arc execution behavior or existing engine module implementations
- New application logic in `api/`
- Database schema changes or migration contents
- Replacing the existing `engine/tests/` suite

---

# Acceptance Criteria

- [x] `engine/` and `api/` packages exist with `__init__.py` and clear module boundaries
- [x] `pyproject.toml` pins Python 3.11+, SQLAlchemy 2.0, asyncpg, alembic, FastAPI 0.111+, python-statemachine 3.0+, and LiteLLM 1.30+
- [x] `make lint` runs ruff and passes clean
- [x] `make type` runs mypy strict and passes clean
- [x] `make test` runs pytest on an empty test suite and passes clean
- [x] `tests/knowledge_graph/`, `tests/arc/`, `tests/safety/`, and `tests/routing/` exist as scaffolded directories

---

# Test Plan

- Run `make lint`
- Run `make type`
- Run `make test`
- Manually confirm the existing `engine/` and `api/` package spine was preserved

---

# Risks and Unknowns

**Risks**:
- Windows environments may not have GNU Make installed, so a local command shim is needed for validation parity
- The default local `python` interpreter may not satisfy the repo's Python 3.11+ requirement

**Unknowns**:
- Whether future tasks will split this workspace manifest into separate distributable Python packages

---

# Open Questions

- None for AW-101 after plan approval
