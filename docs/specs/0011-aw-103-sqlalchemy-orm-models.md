# SQLAlchemy ORM Models for All Platform Tables

**Status**: Planned

**Author**: Claude | **Date**: 2026-05-29

---

# References

- Architecture sections: `docs/architecture/04-knowledge-graph.md` (§4.2–4.3), `docs/architecture/05-session-persistence.md` (§5.2, §5.4), `docs/architecture/07-character-behavior.md` (§7.2), `docs/architecture/11-telemetry.md` (§11.2, §11.4, §11.5), `docs/architecture/15-development-guide.md` (§15.3, §15.5, §15.9 #1)
- Related specs: `docs/specs/0010-aw-102-local-postgres-pgvector-alembic-init.md`
- PRD sections: `docs/prd/02-requirements.md`
- Roadmap task: `docs/roadmap/tasks/AW-103-sqlalchemy-models-for-all-platform-tables.md`

---

# Overview

Implement SQLAlchemy 2.0 async ORM models for all 15 platform database tables. These are the persistence-layer models — separate from the Pydantic domain models already in `engine/session/models.py` and `engine/arc/models.py`. The ORM models live in a new `engine/db/` module and are the sole source of truth for Alembic autogenerate. Wire the ORM metadata into `migrations/env.py` so AW-104 can autogenerate the full migration.

---

# Context From Epic A

Two things from Epic A affect this task directly:

1. **Pydantic models already exist.** `engine/session/models.py` has `Session`, `SessionParticipant`, `ArcBeat`. `engine/arc/models.py` has the arc-definition schema. These are domain models used by the engine layer — do not replace or merge them. The ORM models are a separate concern.
2. **`migrations/env.py` has `target_metadata = None`.** Alembic autogenerate will produce an empty migration until `target_metadata` is pointed at the new ORM `Base.metadata`. Updating this import is part of AW-103's scope.

---

# In Scope

- Create `engine/db/__init__.py` and `engine/db/orm.py`
- Define a `Base` (`DeclarativeBase`) in `engine/db/orm.py`
- Implement ORM models for all 15 platform tables with exact schemas below
- Include `VECTOR(1536) NULL` columns using `pgvector.sqlalchemy.Vector` on the specified tables
- Update `migrations/env.py`: import `Base` from `engine.db.orm` and assign `target_metadata = Base.metadata`
- Import smoke test: all models importable; all FK references resolve

---

# Authoritative Table Schemas

Column definitions are the implementation contract. Use exact column names. Do not add or remove columns.

---

### `accounts`

```sql
CREATE TABLE accounts (
    account_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firebase_uid  TEXT NOT NULL UNIQUE,
    email         TEXT,
    display_name  TEXT,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_seen_at  TIMESTAMPTZ
);
```

`firebase_uid` is `TEXT NOT NULL UNIQUE` — a Firebase-issued string, not a UUID. `email` and `display_name` are nullable (anonymous players who create an account post-session may not supply them). No payment or billing fields.

---

### `consent_records`

```sql
CREATE TABLE consent_records (
    consent_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id      UUID REFERENCES accounts(account_id),
    session_id      UUID REFERENCES sessions(session_id),
    consent_type    TEXT NOT NULL,   -- "content_logging" | "analytics" | "terms_of_service"
    granted         BOOLEAN NOT NULL,
    granted_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    revoked_at      TIMESTAMPTZ,
    consent_version TEXT NOT NULL
);
```

Both `account_id` and `session_id` are nullable FKs — anonymous players have no `account_id`; consent may be recorded at the session level before an account exists. `consent_version` is non-negotiable for GDPR compliance. The `"content_logging"` consent type is the gate that must be checked before `CONTENT_LOGGING_ENABLED` is ever flipped to true (Arch §11.4).

---

### `characters`

```sql
-- Columns confirmed in architecture:
character_id      UUID PRIMARY KEY DEFAULT gen_random_uuid()
behavior_profile  JSONB NOT NULL DEFAULT '{}'
embedding         VECTOR(1536)    -- NULL; populated when embedding collection activates
```

`behavior_profile` stores the authored baseline psychology: personality, goals, secrets, tells, and starting relationship dispositions (Arch §7.2). This is initialized at session start and does not change during play. Live relationship evolution during a session is tracked in the `relationships` table, not written back here.

> **Note:** Additional columns (e.g. name, arc_id, session_id) are not yet defined in the architecture. Implement only these three columns and flag the gap in a PR comment.

---

### `facts`

```sql
CREATE TABLE facts (
    fact_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id    UUID NOT NULL REFERENCES sessions(session_id),
    fact_type     TEXT NOT NULL,   -- "clue" | "accusation" | "relationship" | "event"
    fact_content  JSONB NOT NULL,
    embedding     VECTOR(1536)     -- NULL at MVP; see Arch §4.5
);
```

Source: Arch §4.2, §4.5, §15.5 `assert_knowledge` signature.

---

### `knowledge_states`

```sql
CREATE TABLE knowledge_states (
    ks_id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id          UUID NOT NULL REFERENCES sessions(session_id),
    character_id        UUID NOT NULL REFERENCES characters(character_id),
    fact_id             UUID NOT NULL REFERENCES facts(fact_id),
    source_character_id UUID REFERENCES characters(character_id),   -- NULL = environmental
    confidence          FLOAT NOT NULL DEFAULT 1.0,
    provenance_chain    JSONB NOT NULL DEFAULT '[]',
    asserted_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at          TIMESTAMPTZ,
    superseded_by       UUID REFERENCES knowledge_states(ks_id)     -- set on revoke; see §4.3
);
```

On revoke, a new record is inserted and the old record's `superseded_by` is set — the original record is never deleted. `provenance_chain` is an ordered JSON array of character IDs from original source to current knower (Arch §4.2). `superseded_by` is a self-referential FK; declare with `use_alter=True` in SQLAlchemy to avoid circular resolution.

---

### `relationships`

```sql
CREATE TABLE relationships (
    relationship_id  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id       UUID NOT NULL REFERENCES sessions(session_id),
    source_char_id   UUID NOT NULL REFERENCES characters(character_id),
    target_char_id   UUID NOT NULL REFERENCES characters(character_id),
    trust_level      FLOAT NOT NULL DEFAULT 0.5,
    history_tag      TEXT,    -- "rivalry" | "alliance" | "acquaintance" | "strangers" | etc.
    current_affect   TEXT,    -- "warm" | "cool" | "hostile" | "cautious" | "neutral"
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (session_id, source_char_id, target_char_id)
);
```

This is the live, mutable session-scoped record of how relationship dispositions evolve during play — distinct from `characters.behavior_profile` which is the authored baseline. The behavior engine reads this table (not `behavior_profile`) when building generation prompts. The `UNIQUE` constraint makes this upsert-friendly.

---

### `locations`

```sql
CREATE TABLE locations (
    location_id  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id   UUID NOT NULL REFERENCES sessions(session_id),
    name         TEXT NOT NULL,
    description  TEXT,
    metadata     JSONB NOT NULL DEFAULT '{}'
);
```

Not used by Nightcap at MVP. Populated by the `world_generation` module in H2 (Arch §14.2). `metadata JSONB` is the extension point for monster RPG world-building properties.

---

### `objects`

```sql
CREATE TABLE objects (
    object_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id   UUID NOT NULL REFERENCES sessions(session_id),
    location_id  UUID REFERENCES locations(location_id),
    name         TEXT NOT NULL,
    description  TEXT,
    metadata     JSONB NOT NULL DEFAULT '{}'
);
```

Not used by Nightcap at MVP. Populated by `world_generation` in H2. `location_id` is a nullable FK to `locations`.

---

### `decisions`

```sql
CREATE TABLE decisions (
    decision_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id     UUID NOT NULL REFERENCES sessions(session_id),
    timestamp      TIMESTAMPTZ NOT NULL DEFAULT now(),
    decision_type  TEXT NOT NULL,   -- "beat_entry" | "generative_trigger" | "safety_rule_fired"
    context        JSONB NOT NULL DEFAULT '{}',
    outcome        JSONB NOT NULL DEFAULT '{}'
);
```

The knowledge graph's operational audit trail (Arch §4.2). Records arc execution decisions made during a live session at the knowledge-graph layer. **Distinct from `decision_logs`** (step 16): `decisions` is operational/session-scoped; `decision_logs` is analytical/cross-session telemetry.

---

### `events`

```sql
CREATE TABLE events (
    event_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id    UUID NOT NULL REFERENCES sessions(session_id),
    timestamp     TIMESTAMPTZ NOT NULL DEFAULT now(),
    actor_char_id UUID REFERENCES characters(character_id),   -- NULL for system events
    event_type    TEXT NOT NULL,
    payload       JSONB NOT NULL DEFAULT '{}',
    content_text  TEXT,       -- NULL at MVP for most event types
    embedding     VECTOR(1536)
);

CREATE INDEX ON events (session_id, timestamp);
CREATE INDEX ON events (event_type, timestamp);
```

Source: Arch §11.2 CREATE TABLE (exact). Append-only. GDPR deletion = nullify `content_text` and zero `embedding`; never delete rows.

---

### `sessions`

```sql
-- Derived from Arch §15.3 Pydantic model
session_id        UUID PRIMARY KEY DEFAULT gen_random_uuid()
arc_id            TEXT NOT NULL
status            TEXT NOT NULL    -- "created"|"active"|"paused"|"completed"|"abandoned"
host_account_id   UUID NOT NULL REFERENCES accounts(account_id)
created_at        TIMESTAMPTZ NOT NULL DEFAULT now()
started_at        TIMESTAMPTZ
completed_at      TIMESTAMPTZ
current_beat_id   TEXT NOT NULL
quality_tier      TEXT NOT NULL    -- "standard"|"premium"
player_count      INT NOT NULL
```

---

### `session_participants`

```sql
-- Derived from Arch §15.3 Pydantic model
participant_id    UUID PRIMARY KEY DEFAULT gen_random_uuid()
session_id        UUID NOT NULL REFERENCES sessions(session_id)
character_id      UUID NOT NULL REFERENCES characters(character_id)
account_id        UUID REFERENCES accounts(account_id)   -- NULL for anonymous players
join_token        TEXT NOT NULL
surface_type      TEXT NOT NULL    -- "phone"|"shared_display"|"host"
is_ai_controlled  BOOLEAN NOT NULL DEFAULT false
```

---

### `arc_beat_states`

```sql
CREATE TABLE arc_beat_states (
    state_id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id            UUID NOT NULL REFERENCES sessions(session_id),
    beat_id               TEXT NOT NULL,
    statemachine_config   JSONB NOT NULL,
    transition_history    JSONB NOT NULL DEFAULT '[]',
    snapshot_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    is_current            BOOLEAN NOT NULL DEFAULT true
);

CREATE INDEX ON arc_beat_states (session_id, is_current);
```

`statemachine_config` stores python-statemachine's `configuration` value serialized as JSONB — this is what gets deserialized back into the statemachine instance on resume (Arch §5.2, §5.4). `transition_history` is the ordered array of beat transitions for full replay. `is_current` enables a simple indexed query to find the active snapshot; set to `false` on all previous rows when a new snapshot is written.

---

### `generation_logs`

```sql
CREATE TABLE generation_logs (
    log_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id       UUID NOT NULL REFERENCES sessions(session_id),
    timestamp        TIMESTAMPTZ NOT NULL DEFAULT now(),
    task_type        TEXT NOT NULL,
    quality_tier     TEXT NOT NULL,
    model_used       TEXT NOT NULL,
    latency_ms       INTEGER NOT NULL,
    input_tokens     INTEGER NOT NULL,
    output_tokens    INTEGER NOT NULL,
    cost_usd         NUMERIC(10,6) NOT NULL,
    tension_score    FLOAT,
    -- Populated only when CONTENT_LOGGING_ENABLED=true:
    prompt_text      TEXT,
    output_text      TEXT,
    prompt_embedding VECTOR(1536),
    output_embedding VECTOR(1536)
);
```

Source: Arch §11.4 CREATE TABLE (exact). All four content columns are always nullable. Populated only when `CONTENT_LOGGING_ENABLED=true` and valid `consent_records` exist.

---

### `decision_logs`

```sql
CREATE TABLE decision_logs (
    decision_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id     UUID NOT NULL REFERENCES sessions(session_id),
    timestamp      TIMESTAMPTZ NOT NULL DEFAULT now(),
    decision_type  TEXT NOT NULL,
    input_context  JSONB NOT NULL,
    outcome        JSONB NOT NULL
);
```

Source: Arch §11.5 CREATE TABLE (exact). Cross-session analytical telemetry — distinct from `decisions` (operational audit). Use exact column names.

---

# Table Count Note

The architecture references "all 16 tables" in §15.9 but §15.3 lists 15 in the creation order. This spec implements all 15 that are defined. If a 16th table is found in any architecture document during implementation, add it and flag it in a PR comment.

---

# Out of Scope

- Changes to existing Pydantic models in `engine/session/models.py` or `engine/arc/models.py`
- Writing the Alembic migration (AW-104)
- Adding Nightcap-specific columns to any platform table
- Inventing columns not listed in this spec
- SQLAlchemy event listeners, hybrid properties, or application-layer triggers

---

# Acceptance Criteria

- [ ] `engine/db/orm.py` exists with a `Base` and ORM models for all 15 platform tables
- [ ] All models have exact column schemas matching the table definitions above
- [ ] `VECTOR(1536) NULL` on `characters.embedding`, `facts.embedding`, `events.embedding`, `generation_logs.prompt_embedding`, `generation_logs.output_embedding`
- [ ] `behavior_profile JSONB` on `characters`
- [ ] `UNIQUE (session_id, source_char_id, target_char_id)` constraint on `relationships`
- [ ] Index on `arc_beat_states (session_id, is_current)`
- [ ] No Nightcap-specific column names on any platform table
- [ ] `migrations/env.py` imports `Base` from `engine.db.orm` and assigns `target_metadata = Base.metadata`
- [ ] Import smoke test: `python -c "from engine.db.orm import Base; print(list(Base.metadata.tables.keys()))"` prints all 15 table names
- [ ] `make type` passes clean

---

# Test Plan

- Import smoke test: verify all 15 table names present in `Base.metadata.tables`
- Relationship integrity: instantiate representative ORM objects; confirm FK references resolve at import time
- `make type` / `make lint` pass

---

# Risks and Unknowns

**Risks**:
- `pgvector.sqlalchemy.Vector` requires the `pgvector` Python package. Verify it is in `pyproject.toml` before writing imports.
- `knowledge_states.superseded_by` is a self-referential FK. Declare with `use_alter=True` in SQLAlchemy to avoid circular resolution at table creation time.
- `consent_records` has two nullable FKs (`account_id`, `session_id`) — both must be declared nullable with no `NOT NULL` constraint.

**Remaining open question**:
- `characters` table: additional columns beyond `character_id`, `behavior_profile`, `embedding` are not yet defined in the architecture. Implement exactly the three confirmed columns; flag in a PR comment.

---

# Open Questions

1. **16 vs 15 tables:** Arch §15.9 references "all 16 tables" while §15.3 lists 15 in the migration order. No 16th table has been identified. Flag if found during implementation.
2. **`characters` additional columns:** Only `character_id`, `behavior_profile`, `embedding` are confirmed. Are there additional columns (name, arc_id, session_id)?
