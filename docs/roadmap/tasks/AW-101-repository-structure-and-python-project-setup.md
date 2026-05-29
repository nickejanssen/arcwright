# AW-101: Repository structure and Python project setup

**Milestone / Epic:** M1 / A  
**Size:** S  
**Implements:** Arch S2.3, S2.4  
**Depends on:** none

## Build

Establish the Python package layout for the `arcwright-engine` library and a separate `arcwright-api` package. Configure `pyproject.toml` with locked dependency versions, ruff for lint, mypy strict for type checking, and pytest. Add a Makefile or task runner with `lint`, `type`, `test`, and `migrate` commands.

## Acceptance Criteria

- [ ] `engine/` and `api/` packages exist with `__init__.py` and clear module boundaries
- [ ] `pyproject.toml` pins Python 3.11+, SQLAlchemy 2.0, asyncpg, alembic, fastapi 0.111+, python-statemachine 3.0+, litellm 1.30+
- [ ] `make lint` runs ruff and passes clean
- [ ] `make type` runs mypy strict and passes clean
- [ ] `make test` runs pytest on an empty test suite and passes clean
- [ ] Four test directories scaffolded empty: `tests/knowledge_graph/`, `tests/arc/`, `tests/safety/`, `tests/routing/`

## Do NOT

- Put any arc execution or game logic in the `api` package
- Mix engine and api dependencies into one package
- Use Python below 3.11 anywhere in the codebase

## Testing

Test directories scaffolded per Arch S2.9 four locked test areas.

## Agent Notes

First action before creating anything: inspect the current repo state and reconcile what already exists before creating or replacing files. Do not clobber existing work.
