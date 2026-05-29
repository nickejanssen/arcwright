# AW-104: First full Alembic migration

**Milestone / Epic:** M1 / B  
**Size:** M  
**Implements:** Arch S2.4, S15.9 #1  
**Depends on:** AW-103

## Build

Generate and hand-verify the Alembic migration that creates all platform tables, indexes, and foreign keys. Confirm pgvector extension ordering.

## Acceptance Criteria

- [ ] `alembic upgrade head` creates all tables with zero errors
- [ ] pgvector extension created before vector columns
- [ ] `alembic downgrade base` drops everything cleanly
- [ ] Migration is deterministic and re-runnable on a fresh DB

## Do NOT

- Edit a generated migration to include manual schema drift not reflected in models

## Testing

Fresh-database upgrade and downgrade cycle in CI and locally.

## Agent Notes

Autogenerate, then review by hand. Alembic autogenerate misses some pgvector and index details.
