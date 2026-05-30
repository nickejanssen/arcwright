# Supplemental Table Schemas

> **Source:** Founder decisions recorded 2026-05-30.
> These schemas fill gaps in 07-Technical-Architecture-v1.3 for tables listed in §15.3
> but not given explicit column definitions there. When the architecture document is
> next synced from Notion, these schemas should be incorporated and this file removed.

---

## `accounts`

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

`firebase_uid` is a Firebase-issued string identifier, not a UUID. `email` and `display_name`
are nullable because anonymous players who create an account post-session may not supply them.
No payment or billing fields — those belong in the game layer.

---

## `consent_records`

```sql
CREATE TABLE consent_records (
    consent_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id      UUID REFERENCES accounts(account_id),       -- nullable
    session_id      UUID REFERENCES sessions(session_id),       -- nullable
    consent_type    TEXT NOT NULL,   -- "content_logging" | "analytics" | "terms_of_service"
    granted         BOOLEAN NOT NULL,
    granted_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    revoked_at      TIMESTAMPTZ,
    consent_version TEXT NOT NULL
);
```

Both FKs are nullable: anonymous players have no `account_id`; consent may be recorded at
the session level before an account exists. `consent_version` is required for GDPR compliance —
records which version of the policy was agreed to. The `"content_logging"` consent type is
the gate that must be checked before `CONTENT_LOGGING_ENABLED` is flipped to `true` (§11.4).

---

## `relationships`

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

**Relationship to `characters.behavior_profile`:** `behavior_profile` is the authored baseline
(initialized at session start, read-only during play). `relationships` is the live mutable
session-scoped record of how dispositions evolve during play. The behavior engine reads
`relationships`, not `behavior_profile`, when building generation prompts (§7.2). The
`UNIQUE` constraint makes this upsert-friendly.

---

## `locations`

```sql
CREATE TABLE locations (
    location_id  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id   UUID NOT NULL REFERENCES sessions(session_id),
    name         TEXT NOT NULL,
    description  TEXT,
    metadata     JSONB NOT NULL DEFAULT '{}'
);
```

Not used by Nightcap at MVP. Populated by the `world_generation` module in H2 (§14.2).
`metadata JSONB` is the extension point for monster RPG world-building properties.

---

## `objects`

```sql
CREATE TABLE objects (
    object_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id   UUID NOT NULL REFERENCES sessions(session_id),
    location_id  UUID REFERENCES locations(location_id),        -- nullable
    name         TEXT NOT NULL,
    description  TEXT,
    metadata     JSONB NOT NULL DEFAULT '{}'
);
```

Not used by Nightcap at MVP. Populated by `world_generation` in H2.

---

## `decisions`

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

The knowledge graph's operational audit trail (§4.2). Records arc execution decisions made
during a live session. **Distinct from `decision_logs` (§11.5):** `decisions` is
session-scoped and operational; `decision_logs` is cross-session analytical telemetry.

---

## `arc_beat_states`

```sql
CREATE TABLE arc_beat_states (
    state_id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id           UUID NOT NULL REFERENCES sessions(session_id),
    beat_id              TEXT NOT NULL,
    statemachine_config  JSONB NOT NULL,
    transition_history   JSONB NOT NULL DEFAULT '[]',
    snapshot_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    is_current           BOOLEAN NOT NULL DEFAULT true
);

CREATE INDEX ON arc_beat_states (session_id, is_current);
```

`statemachine_config` stores python-statemachine's `configuration` value serialized as JSONB.
On resume, this is deserialized back into the statemachine instance (§5.2, §5.4).
`transition_history` is an ordered array of beat transitions for full replay.
`is_current` enables a simple indexed query to find the active snapshot. When a new snapshot
is written, the previous row's `is_current` is set to `false`.

---

## `characters` — confirmed columns only

The architecture confirms three columns. Additional columns are not yet specified:

```sql
character_id      UUID PRIMARY KEY DEFAULT gen_random_uuid()
behavior_profile  JSONB NOT NULL DEFAULT '{}'
embedding         VECTOR(1536)   -- NULL; populated when embedding collection activates (§4.5)
```

Additional columns (name, arc_id, session_id) are not defined in any architecture document.
Do not add them until specified.
