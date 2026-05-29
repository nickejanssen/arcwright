# AW-102: Local Postgres 15 + pgvector + Alembic init

**Milestone / Epic:** M1 / A  
**Size:** S  
**Implements:** Arch S2.2, S2.4  
**Depends on:** AW-101

## Build

Provide a docker-compose configuration running Postgres 15 with pgvector for local development, mirroring the Cloud SQL instance that will run in production. Initialize Alembic with async engine configuration. Write the first migration: `CREATE EXTENSION IF NOT EXISTS vector` and nothing else.

## Acceptance Criteria

- [ ] `docker compose up` brings up Postgres 15 with pgvector available
- [ ] Alembic is configured for SQLAlchemy 2.0 async (`asyncpg` driver)
- [ ] `alembic upgrade head` enables the vector extension with zero errors
- [ ] `alembic downgrade base` reverses cleanly
- [ ] No connection strings hardcoded; all config via environment variables
- [ ] README documents the `docker compose up` and migration steps

## Do NOT

- Apply any schema changes directly to any database outside Alembic
- Hardcode connection strings or credentials anywhere in the codebase
- Create any application tables in this migration

## Testing

Manual upgrade and downgrade cycle against the docker database.

## Agent Notes

Cloud SQL provisioning is a founder action. Agent work here is local development parity only.
