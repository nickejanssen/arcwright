# M1-A: Scaffolding and Infrastructure

**Milestone:** M1  
**Status:** Planned

## What This Epic Covers

Establish the Python package structure, tooling configuration, local development database, and Alembic migration infrastructure. Nothing in later M1 epics should proceed until this foundation is usable.

## Tasks

- [AW-101: Repository structure and Python project setup](../tasks/AW-101-repository-structure-and-python-project-setup.md)
- [AW-102: Local Postgres 15 + pgvector + Alembic init](../tasks/AW-102-local-postgres-pgvector-alembic-init.md)

## Epic Exit Criteria

- `engine/` and `api/` package boundaries are clear
- Tooling runs clean
- Local Postgres 15 + pgvector is available
- Alembic can upgrade and downgrade cleanly
