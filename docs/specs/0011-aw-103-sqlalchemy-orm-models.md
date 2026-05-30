# SQLAlchemy ORM Models for All Platform Tables

**Status**: Planned

**Author**: Claude | **Date**: 2026-05-29

---

# References

- Architecture sections: `docs/architecture/04-knowledge-graph.md` (§4.2), `docs/architecture/05-session-persistence.md` (§5.2), `docs/architecture/15-development-guide.md` (§15.3, §15.9 #1)
- Related specs: `docs/specs/0010-aw-102-local-postgres-pgvector-alembic-init.md`
- PRD sections: `docs/prd/02-requirements.md`
- Roadmap task: `docs/roadmap/tasks/AW-103-sqlalchemy-models-for-all-platform-tables.md`

---

# Overview

Implement SQLAlchemy 2.0 async ORM models for all platform database tables, as enumerated in architecture §15.3. This is the persistence layer — separate from the Pydantic domain models that already exist in `engine/session/models.py` and `engine/arc/models.py`. The ORM models live in a new `engine/db/` module and are the sole source of truth for Alembic autogenerate. Wire the ORM metadata into `migrations/env.py` so AW-104 can autogenerate the full migration.

---

# Context From Epic A

Two things from Epic A affect this task directly:

1. **Pydantic models already exist.** `engine/session/models.py` has `Session`, `SessionParticipant`, `ArcBeat`. `engine/arc/models.py` has the arc-definition schema. These are domain models used by the engine layer — do not replace or merge them. The ORM models are a separate concern.
2. **`migrations/env.py` has `target_metadata = None`.** Alembic autogenerate will produce an empty migration until `target_metadata` is pointed at the new ORM `Base.metadata`. Updating this import is part of AW-103's scope.

---

# In Scope

- Create `engine/db/__init__.py` and `engine/db/orm.py`
- Define a `Base` (SQLAlchemy `DeclarativeBase` or `DeclarativeBaseNoMeta`) in `engine/db/orm.py`
- Implement ORM models for all 15 platform tables (see Table List below), in dependency order
- Include `VECTOR(1536) NULL` columns on `characters`, `facts`, `events`, `generation_logs` using the `pgvector.sqlalchemy` `Vector` type
- Include `JSONB` column on `characters.behavior_profile`
- Include `JSONB` `statemachine_config` or equivalent on `arc_beat_states`
- Mark `events` table as append-only via a table comment; enforce at engine layer not DB layer
- Update `migrations/env.py` to import `Base.metadata` and assign it to `target_metadata`
- Smoke test: all 15 models importable; relationship foreign keys resolve without error

---

# Table List

Implement in dependency order (matches §15.3):

| # | Table | Notable columns |
|---|-------|----------------|
| 1 | `accounts` | `account_id UUID PK`, `email TEXT`, `created_at TIMESTAMPTZ` |
| 2 | `consent_records` | `consent_id UUID PK`, `account_id UUID FK→accounts`, `created_at TIMESTAMPTZ` |
| 3 | `characters` | `character_id UUID PK`, `behavior_profile JSONB`, `embedding VECTOR(1536) NULL` |
| 4 | `facts` | `fact_id UUID PK`, `fact_type TEXT`, `fact_content JSONB`, `embedding VECTOR(1536) NULL` |
| 5 | `knowledge_states` | `ks_id UUID PK`, `session_id UUID FK→sessions`, `character_id UUID FK→characters`, `fact_id UUID FK→facts`, `provenance_chain JSONB`, `confidence FLOAT`, `asserted_at TIMESTAMPTZ`, `expires_at TIMESTAMPTZ NULL` |
| 6 | `relationships` | `relationship_id UUID PK`, `session_id UUID FK→sessions`, `character_a UUID FK→characters`, `character_b UUID FK→characters`, `trust_level FLOAT`, `disposition JSONB` |
| 7 | `locations` | `location_id UUID PK`, `arc_id TEXT`, `name TEXT`, `properties JSONB` |
| 8 | `objects` | `object_id UUID PK`, `arc_id TEXT`, `name TEXT`, `properties JSONB` |
| 9 | `decisions` | `decision_id UUID PK`, `session_id UUID FK→sessions`, `decision_type TEXT`, `payload JSONB`, `decided_at TIMESTAMPTZ` |
| 10 | `events` | `event_id UUID PK`, `session_id UUID FK→sessions`, `event_type TEXT`, `actor_id UUID NULL`, `target_audience TEXT`, `target_player_id UUID NULL`, `payload JSONB`, `timestamp TIMESTAMPTZ`, `embedding VECTOR(1536) NULL` |
| 11 | `sessions` | `session_id UUID PK`, `arc_id TEXT`, `status TEXT`, `host_account_id UUID FK→accounts`, `current_beat_id TEXT`, `quality_tier TEXT`, `player_count INT`, `created_at TIMESTAMPTZ`, `started_at TIMESTAMPTZ NULL`, `completed_at TIMESTAMPTZ NULL` |
| 12 | `session_participants` | `participant_id UUID PK`, `session_id UUID FK→sessions`, `character_id UUID FK→characters`, `account_id UUID NULL FK→accounts`, `join_token TEXT`, `surface_type TEXT`, `is_ai_controlled BOOL` |
| 13 | `arc_beat_states` | `abs_id UUID PK`, `session_id UUID FK→sessions`, `beat_id TEXT`, `statemachine_config JSONB`, `snapshot_at TIMESTAMPTZ` |
| 14 | `generation_logs` | `log_id UUID PK`, `session_id UUID FK→sessions`, `task_type TEXT`, `quality_tier TEXT`, `model_key TEXT`, `prompt_tokens INT NULL`, `completion_tokens INT NULL`, `latency_ms INT NULL`, `prompt_text TEXT NULL`, `output_text TEXT NULL`, `prompt_embedding VECTOR(1536) NULL`, `created_at TIMESTAMPTZ` |
| 15 | `decision_logs` | `dlog_id UUID PK`, `session_id UUID FK→sessions`, `decision_id UUID NULL FK→decisions`, `trigger TEXT`, `payload JSONB`, `logged_at TIMESTAMPTZ` |

> **Note on table count:** §15.9 references "16 tables" while §15.3 lists 15. If a 16th table is identified in any architecture section during implementation, add it and flag it in a PR comment. Do not invent a table to reach 16.

---

# Out of Scope

- Changes to existing Pydantic models in `engine/session/models.py` or `engine/arc/models.py`
- Writing the Alembic migration (that is AW-104)
- Adding Nightcap-specific columns to any platform table
- Database indexes beyond primary keys (Alembic autogenerate handles indexes in AW-104; flag any index requirements as a PR comment)
- SQLAlchemy event listeners or hybrid properties

---

# Acceptance Criteria

- [ ] `engine/db/orm.py` exists with a `Base` and ORM models for all platform tables
- [ ] All ORM models importable from `engine.db.orm` with no import errors
- [ ] `VECTOR(1536)` columns present and nullable on `characters`, `facts`, `events`, `generation_logs`
- [ ] `behavior_profile JSONB` present on `characters`
- [ ] `statemachine_config JSONB` present on `arc_beat_states`
- [ ] No Nightcap-specific column names on any platform table
- [ ] `migrations/env.py` imports `Base.metadata` and assigns it to `target_metadata`
- [ ] All model relationship foreign keys resolve (smoke test: `from engine.db.orm import *` succeeds in isolation)
- [ ] `make type` passes clean

---

# Test Plan

- Import smoke test: `python -c "from engine.db.orm import Base; print(list(Base.metadata.tables.keys()))"` — verify all expected table names present
- Relationship integrity check: instantiate representative ORM objects and confirm FK references resolve at import time
- `make type` / `make lint` pass

---

# Risks and Unknowns

**Risks**:
- `pgvector.sqlalchemy` `Vector` type requires the `pgvector` Python package installed. Confirm it is in `requirements.txt` / `pyproject.toml` from AW-101 before writing imports.
- `knowledge_states` has a circular dependency: it references both `sessions` and `characters`, and `sessions` is created after `characters` in §15.3. Ensure FK declarations use `relationship()` with string references to avoid Python import-order issues.

**Unknowns**:
- Whether `accounts` needs a `firebase_uid TEXT` column for Firebase Auth linkage. Architecture §15.3 does not specify. If unclear, stop and flag; do not invent columns.
- Whether `CONTENT_LOGGING_ENABLED` feature flag affects ORM model definition (it does not — nullable columns are always present in schema; the flag controls write behavior at the engine layer).

---

# Open Questions

- Arch §15.9 says "16 tables" while §15.3 lists 15 explicitly. If one table is missing from the §15.3 list, which is it? Flagging here so the implementing agent does not silently drop it.
