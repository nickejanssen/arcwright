# AW-103: SQLAlchemy models for all platform tables

**Milestone / Epic:** M1 / B  
**Size:** L  
**Implements:** Arch S4, S5, S2.10  
**Depends on:** AW-102

## Build

Implement SQLAlchemy 2.0 async models for the full platform data model as enumerated in the architecture data-model sections. Use platform-clean schema names and include nullable `VECTOR(1536)` columns on the specified tables.

## Acceptance Criteria

- [ ] Every table in the architecture data-model section has a corresponding model
- [ ] Schema names are platform-clean; no game-specific semantics in column names
- [ ] pgvector columns present and nullable on the specified tables
- [ ] No Nightcap-specific columns on platform tables

## Do NOT

- Add Nightcap-only columns to platform tables
- Invent table or column names
- Use SQLAlchemy 1.x legacy style

## Testing

Model import smoke tests and relationship integrity checks.

## Agent Notes

If the data-model section is ambiguous on a table or column, stop and flag it rather than guessing.
