> Current version: v0.1
> Last updated: 2026-08-05
> Status: Awaiting founder approval (spec 0087 phase gate 2)
> Canonical path: docs/specs/0087-appendix-a-case-persistence-migration-design.md

# Appendix A — Case Persistence Migration Design

This is the phase gate 2 artifact required by
`docs/specs/0087-aw-290-narrator-slot-schema-and-wrapper-dressing.md` and by
`docs/decisions/0022-resolved-case-persistence.md`, which states: "This decision
approves persistence in principle only. The concrete table design, foreign key
layout, indexes, and downgrade path require separate founder approval before the
migration is written, per the `AGENTS.md` schema and migration Hard Rules."

**No migration file has been written. Nothing in this document is implemented.**

---

# Blocking finding: there is no production caller that can satisfy the FK

Verified 2026-08-05 by reading source, not by inference.

Q1 was answered `cases.session_id NOT NULL` referencing `sessions.session_id`.
Writing such a row requires a caller holding three things at once: a real
`sessions` row, a `ResolvedCase`, and an `AsyncSession`. **No production code
path holds all three.**

| Fact | Evidence |
|---|---|
| `engine/case/` has zero DB coupling | Full import inventory of all 7 modules; only outward dependency is `engine.arc.models` (`engine/case/resolver.py:44`) |
| The only production caller of `resolve()` is the harness | `engine/harness/runner.py:240`. No caller in `api/`, `nightcap/`, or `scripts/` |
| The harness has no DB access whatsoever | `grep -rn "sqlalchemy\|AsyncSession\|engine.db" engine/harness/` → no matches |
| The harness `session_id` is synthetic | `engine/harness/runner.py:196-197` mints it from the seeded RNG; **no corresponding `sessions` row is ever inserted** |
| The other `ResolvedCase` consumer has no production caller | `AccusationResolver` (`engine/scoring/resolver.py:55`) is referenced only from `engine/tests/` |
| All three coexist only in test code | `engine/tests/test_scoring_integration.py:233-235` bridges them by hand |

**Consequence.** The tables, ORM models, and a `persist_case` / `load_case`
round-trip can be built and fully tested against the SQLite test harness. They
**cannot be exercised by production code** until something calls them from a
context that owns a real session row.

**Recommendation: do not try to fix that inside this migration.** The natural
home is `engine/session/service.py`'s `start_session`, which already owns a real
`sessions` row and a `db` session and already calls into a sibling persister the
same way (`engine/session/service.py:157-163` → `engine/session/obligations.py`).
Wiring it there touches `engine/case`, `engine/session`, and `engine/db`
together, which is a **cross-module change and an `AGENTS.md` Hard Rule
requiring its own design review**. It is carved out as its own task and its own
approval, not folded in here.

---

# Where the persistence code lives

`engine/case/` stays pure. It gains no `engine/db` import.

The house pattern for "pure engine module plus separate persister" already
exists: `engine/resources/` holds no DB coupling and
`engine/telemetry/resources.py:115-205` persists its objects. Case persistence
follows the same shape, in **`engine/session/case_store.py`**, which sits
alongside `engine/session/obligations.py` — the closest structural precedent, a
session-scoped persister called from `start_session`.

Write pattern follows the house standard exactly, confirmed across `claims`,
`accusations`, `suspect_locks`, and `obligations`: construct ORM objects inline,
`db.add(row)`, `await db.flush()`, **never `commit()` inside engine code**. The
`AsyncSession` is an explicit parameter. There is no repository or DAO layer in
this codebase and this introduces none.

---

# The six tables

Migration `0008_add_case_tables.py`, `down_revision = "0007_add_accusations_table"`.

Every primary key is `PGUUID(as_uuid=True)` with
`server_default=text("gen_random_uuid()")`, matching all 22 existing tables in
`engine/db/orm.py`. There are no string or integer primary keys anywhere in this
codebase and this adds none.

## Why every id appears twice

`ResolvedCase` identifiers are **strings scoped to one case**:
`evidence_id="e1"`, `member_id="s1"`, `fact_id="fact_motive"`,
`case_id="{arc_id}::case::{seed}"` (`engine/case/resolver.py:443`). They are not
globally unique and must not be primary keys. Each table therefore carries a
`PGUUID` surrogate PK **and** the original string as a `*_ref` column, unique
within the case. This is what lets `ResolvedCase` round-trip without loss.

## 1. `cases`

| Column | Type | Null | Note |
|---|---|---|---|
| `case_pk` | PGUUID PK, `gen_random_uuid()` | no | surrogate |
| `session_id` | PGUUID FK → `sessions.session_id` | **no** | the Q1 decision |
| `case_ref` | Text | no | `ResolvedCase.case_id`, the deterministic string |
| `arc_id` | Text | no | |
| `seed` | BigInteger | no | `ResolvedCase.seed` is a Python `int`; `BigInteger` avoids an int32 ceiling |
| `skeleton_id` | Text | no | |
| `culprit_ref` | Text | no | `CastMember.member_id`; see note below |
| `reveal_shape` | JSONB, default `'{}'::jsonb` | no | opaque `dict[str, Any]` on the model |
| `created_at` | timestamptz, default `now()` | no | house standard |

- `UNIQUE (session_id)` — enforces "one case row per session" from Q1 in the
  database rather than by convention. Postgres backs a unique constraint with an
  index, so no separate `session_id` index is created.
- `INDEX ix_cases_case_ref (case_ref)` — lookup by deterministic identity across
  sessions, for debugging and replay comparison. Deliberately **not** unique:
  under Q1 the same arc and seed can legitimately recur in two sessions.

**`culprit_ref` is Text with no foreign key, deliberately.** A composite FK to
`case_cast (case_pk, member_ref)` would be stronger, but `cases` must be
inserted before `case_cast` rows exist, so the FK would have to be `DEFERRABLE
INITIALLY DEFERRED` — a construct used nowhere else in this schema. The house
precedent is plain Text for exactly this shape:
`Accusation.accused_cast_member_id` (`engine/db/orm.py:877`) and
`SuspectLock.suspect_cast_member_id` (`orm.py:927`). Integrity is enforced by a
round-trip test instead. **Flagging the trade rather than hiding it.**

## 2. `case_anchors`

Inserted second, immediately after `cases`, because three other tables reference it.

| Column | Type | Null | Note |
|---|---|---|---|
| `anchor_pk` | PGUUID PK | no | |
| `case_pk` | PGUUID FK → `cases.case_pk` | no | |
| `anchor_ref` | Text | no | `CaseAnchor.anchor_id` |
| `location_ref` | Text | no | reference into the per-case location set |
| `location_label` | Text | no | display label |
| `time_ordinal` | Integer | no | orders anchors within the case; no global clock |
| `time_label` | Text | no | display label |

- `UNIQUE (case_pk, anchor_ref)` — satisfies the spec's "per-case uniqueness of
  anchor ids" test criterion at the database level.
- `INDEX ix_case_anchors_case_pk_location_time (case_pk, location_ref, time_ordinal)`
  — **non-unique.** This resolves an Unknown the spec left open, and the answer
  is load-bearing:

> **Duplicate `(location_ref, time_ordinal)` pairs must be legal.** Two suspects
> placed in the same room at the same hour is not a data error — it is the
> single most interesting configuration the alibi mechanic can produce, and the
> case for it is exactly the scenario the contradiction test is meant to detect.
> A unique constraint here would forbid the best cases the generator can make.
> The index exists for join speed only.

## 3. `case_cast`

| Column | Type | Null | Note |
|---|---|---|---|
| `cast_pk` | PGUUID PK | no | |
| `case_pk` | PGUUID FK → `cases.case_pk` | no | |
| `member_ref` | Text | no | `CastMember.member_id` |
| `display_name` | Text | no | |
| `role` | Text | no | `"suspect"` / `"victim"` |
| `is_culprit` | Boolean, default `false` | no | |
| `tags` | JSONB, default `'[]'::jsonb` | no | |

- `UNIQUE (case_pk, member_ref)`
- `INDEX ix_case_cast_case_pk_role (case_pk, role)` — backs
  `ResolvedCase.members_by_role()` (`engine/case/models.py:165`), called on every
  case load.

## 4. `case_evidence`

| Column | Type | Null | Note |
|---|---|---|---|
| `evidence_pk` | PGUUID PK | no | |
| `case_pk` | PGUUID FK → `cases.case_pk` | no | |
| `evidence_ref` | Text | no | `EvidenceEntry.evidence_id` |
| `anchor_pk` | PGUUID FK → `case_anchors.anchor_pk` | **yes** | the ADR-0022 anchor FK |
| `evidence_type` | Text | no | |
| `body_text` | Text | no | `EvidenceEntry.text`; renamed, see below |
| `short_label` | Text | no | the new generated short form |
| `points_toward` | JSONB, default `'[]'::jsonb` | no | |
| `points_away_from` | JSONB, default `'[]'::jsonb` | no | |
| `delivery` | Text | no | |
| `delivery_target` | Text | yes | |
| `truth_value` | Text, default `'genuine'` | no | |

- `UNIQUE (case_pk, evidence_ref)`
- `INDEX ix_case_evidence_anchor_pk (anchor_pk)` — backs the contradiction join.
- `anchor_pk` is **nullable**: the spec says each of these models carries an
  *optional* anchor reference, and not all evidence is anchored to a place and time.

**Naming gotcha, flagged so it is not discovered at debug time.** The Pydantic
field is `EvidenceEntry.text`. `engine/db/orm.py` imports `text` from SQLAlchemy
and uses it in nearly every `server_default`. Inside a class body, an attribute
named `text` shadows that import for every line after it. The column is
therefore named **`body_text`** in the database and mapped explicitly, using the
same override idiom already used for the reserved word `metadata` at
`engine/db/orm.py:299-304`:

```python
body_text: Mapped[str] = mapped_column("body_text", Text, nullable=False)
```

The Pydantic model keeps `text` unchanged. Only the database column differs.

## 5. `case_facts`

| Column | Type | Null | Note |
|---|---|---|---|
| `fact_pk` | PGUUID PK | no | |
| `case_pk` | PGUUID FK → `cases.case_pk` | no | |
| `fact_ref` | Text | no | `CaseFact.fact_id` |
| `anchor_pk` | PGUUID FK → `case_anchors.anchor_pk` | yes | |
| `predicate` | Text | no | |
| `subject_ref` | Text | no | |
| `object_ref` | Text, default `''` | no | |
| `value` | Text | no | |
| `known_by` | JSONB, default `'[]'::jsonb` | no | |

- `UNIQUE (case_pk, fact_ref)`
- `INDEX ix_case_facts_case_pk_predicate (case_pk, predicate)` — backs
  `ResolvedCase.facts_by_predicate()` (`engine/case/models.py:173`).

## 6. `case_falsehoods`

| Column | Type | Null | Note |
|---|---|---|---|
| `falsehood_pk` | PGUUID PK | no | |
| `case_pk` | PGUUID FK → `cases.case_pk` | no | |
| `falsehood_ref` | Text | no | `AuthorizedFalsehood.falsehood_id` |
| `anchor_pk` | PGUUID FK → `case_anchors.anchor_pk` | yes | |
| `speaker_ref` | Text | no | |
| `topic` | Text | no | |
| `claim_text` | Text | no | |
| `contradicted_by` | JSONB, default `'[]'::jsonb` | no | list of evidence refs |

- `UNIQUE (case_pk, falsehood_ref)`
- `INDEX ix_case_falsehoods_case_pk_topic (case_pk, topic)` — the alibi query
  filters `topic == "location"`; every culprit is forced to that topic at
  `engine/case/resolver.py:395-397`, so this index is on the hot path.

---

# The alibi contradiction becomes one join

This is the whole point of the normalized shape, per ADR-0022. With the above:

```sql
SELECT f.falsehood_ref, e.evidence_ref
FROM case_falsehoods f
JOIN case_anchors fa ON fa.anchor_pk = f.anchor_pk
JOIN case_evidence  e ON e.case_pk    = f.case_pk
JOIN case_anchors ea ON ea.anchor_pk = e.anchor_pk
WHERE f.case_pk = :case_pk
  AND f.topic   = 'location'
  AND ea.time_ordinal  = fa.time_ordinal
  AND ea.location_ref <> fa.location_ref;
```

No string matching anywhere. This satisfies the spec acceptance criterion "a
test proves a contradiction is detected by comparison alone."

---

# Order of operations

**Upgrade:** `cases` → `case_anchors` → `case_cast` → `case_evidence` →
`case_facts` → `case_falsehoods`. Anchors must precede the three tables that
reference them.

**Downgrade:** exact reverse — `case_falsehoods` → `case_facts` →
`case_evidence` → `case_cast` → `case_anchors` → `cases`, dropping each index
before its table, matching the style of
`migrations/versions/0007_add_accusations_table.py`.

The downgrade is a clean drop of six new tables. It alters no existing table, so
there is no data-loss path on an existing database and no backfill to reverse.
**`sessions` is not modified** — that was the cost of the standalone option in
Q1, and Q1 chose the option that avoids it.

---

# Honest limits of the verification

Flagged because the spec's acceptance criteria assume more than CI currently delivers.

1. **`alembic upgrade head` / `downgrade -1` is effectively untested in CI.** The
   only migration up/down test in the repo is
   `engine/tests/test_mini_game_runtime.py:798-832`. It shells out to `alembic`
   but **skips unless `DATABASE_URL` is set** (`:808-810`), so it does not run in
   the default suite. Its `@pytest.mark.integration` marker is also unregistered
   in `pyproject.toml`, which lists only `slow` at lines 23-25. The acceptance
   criterion "applies cleanly to an empty schema and to a populated one" cannot be
   met by CI as configured. Either a Postgres service gets added to CI, or the
   criterion is honestly downgraded to "verified locally against Postgres, with
   the command and output recorded in the PR."

2. **Table-level tests run on SQLite, not Postgres.** `engine/db/testing.py:34-69`
   rewrites `JSONB → JSON`, `gen_random_uuid() → uuid4`, and `now() →
   CURRENT_TIMESTAMP` so the ORM works in-memory. Round-trip tests are therefore
   real but do not exercise Postgres-specific behavior.

3. **There is no `conftest.py` in this repo.** Every DB-touching test module
   defines its own `db_session` fixture, duplicated per file (for example
   `engine/tests/test_claims_resolver.py:24-36`). New test files pay that cost
   again. This is pre-existing and is not being fixed here.

---

# What is being asked

Approve, or send back with changes:

1. The six tables and their columns as specified above.
2. `cases.session_id NOT NULL` with `UNIQUE (session_id)`.
3. `culprit_ref` as plain Text with no foreign key, following the
   `Accusation.accused_cast_member_id` precedent.
4. Nullable `anchor_pk` foreign keys on `case_evidence`, `case_facts`, and
   `case_falsehoods`.
5. **`(case_pk, location_ref, time_ordinal)` non-unique** — duplicate
   place-and-time anchors are legal.
6. The `body_text` column name for `EvidenceEntry.text`.
7. Persistence code in `engine/session/case_store.py`, leaving `engine/case/` pure.
8. Acknowledgement that no production caller writes these tables in this task,
   and that wiring `start_session` is a separate cross-module change needing its
   own review.
