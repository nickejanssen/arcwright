# Local Postgres 15 + pgvector + Alembic Init

**Status**: Done

**Author**: Codex | **Date**: 2026-05-29

---

# References

- Related ADRs: `docs/decisions/0001-scaffolding-audit.md`
- Architecture sections: `docs/architecture/02-technology-stack.md`
- Related specs: `docs/specs/0009-aw-101-repository-structure-and-python-project-setup.md`
- PRD sections: `docs/prd/01-overview.md`
- Roadmap task: `docs/roadmap/tasks/AW-102-local-postgres-pgvector-alembic-init.md`

---

# Overview

Set up the local PostgreSQL development baseline for Arcwright with Postgres 15, pgvector, and Alembic configured for SQLAlchemy 2.0 async usage. The first migration enables the `vector` extension and does nothing else.

---

# In Scope

- Root `docker-compose.yml` for local Postgres 15 with pgvector
- Environment-variable-driven database configuration for local development
- Alembic async configuration using the `asyncpg` driver
- Initial Alembic migration that creates and drops the `vector` extension only
- README instructions for bringing up the local database and running migrations

---

# Out of Scope

- Cloud SQL provisioning or any non-local infrastructure work
- Application table creation or any schema beyond the `vector` extension
- Changes to engine, API, routing, safety, or knowledge graph logic
- Direct schema changes outside Alembic

---

# Acceptance Criteria

- [x] `docker compose up` brings up Postgres 15 with pgvector available
- [x] Alembic is configured for SQLAlchemy 2.0 async (`asyncpg` driver)
- [x] `alembic upgrade head` enables the vector extension with zero errors
- [x] `alembic downgrade base` reverses cleanly
- [x] No connection strings hardcoded; all config via environment variables
- [x] README documents the `docker compose up` and migration steps

---

# Test Plan

- Manual testing: run `docker compose up`
- Manual testing: run `alembic upgrade head`
- Manual testing: verify `vector` extension availability in the local database
- Manual testing: run `alembic downgrade base`

---

# Risks and Unknowns

**Risks**:
- Local Docker availability may differ by developer machine
- Alembic async configuration can fail if env var loading is inconsistent between shells

**Unknowns**:
- None within AW-102 scope after plan approval

---

# Open Questions

- None within AW-102 scope after plan approval
