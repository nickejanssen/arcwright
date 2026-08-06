# 0022 - Resolved Case Is Persisted in Normalized Tables

**Date:** 2026-08-05
**Status:** Accepted
**Decision authority:** Founder decision interview recorded 2026-08-05 (D-103)
**Extends:** `docs/decisions/0017-narrator-slot-resolution-and-wrapper-dressing.md`
**Implemented by:** `docs/specs/0087-aw-290-narrator-slot-schema-and-wrapper-dressing.md`
**Roadmap references:** AW-290, M5-I

---

# Status

**Accepted**

---

# Context

ADR-0017 authorized the AW-290 migration PR to design one thing: the shape and
placement of typed location and time anchors on the case-resolution surface. It
did not authorize persisting the resolved case, and it did not discuss
persistence at all.

AW-290's task file nevertheless carries acceptance criteria requiring an Alembic
migration with a downgrade path and `alembic upgrade head` verification. Review
on 2026-08-05 found nothing to migrate:

- `ResolvedCase`, `EvidenceEntry`, `CaseFact`, `CastMember`, and
  `AuthorizedFalsehood` in `engine/case/models.py` are Pydantic models with
  `extra="forbid"`. None has a persistence layer.
- `engine/db/orm.py` contains no reference to any of them.
- The `sessions` table has no column that could hold a case.
- The case is produced at `engine/harness/runner.py:240` and consumed at
  `engine/scoring/resolver.py:61`. It is never written.
- Alembic revisions stop at `migrations/versions/0007_add_accusations_table.py`.
- `ResolvedCase` carries a `seed` field and is regenerated deterministically.

Two readings were possible: the acceptance criterion is stale copy, or it
records an intent to persist that was never separately decided. The founder was
asked which, and chose persistence.

The recommendation put to the founder was the opposite: correct the acceptance
criterion, add the typed fields to the Pydantic models, and ship no migration,
on the grounds that a deterministically regenerated artifact does not need
storing. That recommendation was not taken. This record exists so the decision
is durable and the trade-off is visible, per the `AGENTS.md` rule that new
scope needs approval evidence in canonical docs.

---

# Decision

**The resolved case is persisted.** `ResolvedCase` and its constituent objects
are written to the database rather than held only in memory.

**Persistence is fully normalized**, not a JSONB document. A `cases` root table
plus `case_cast`, `case_evidence`, `case_falsehoods`, `case_facts`, and
`case_anchors`, with real foreign keys, including references from
`case_evidence`, `case_facts`, and `case_falsehoods` to `case_anchors`.

This follows the precedent in `docs/decisions/0016-aw283-claim-ledger-schema.md`,
which gave the claim ledger dedicated tables rather than the generic events
table because it is hot-path gameplay data rather than incidental telemetry.
Case truth is read throughout a session by evidence delivery, interrogation,
contradiction detection, and reveal accounting, and qualifies on the same test.

Normalization is also what makes the paired anchor decision meaningful. The
anchors were chosen as a shared value object referenced by id specifically so
that an alibi contradiction becomes a join with database-enforced referential
integrity. A JSONB document would have left anchor references unconstrained and
reduced the value object to a code-hygiene measure.

**This decision approves persistence in principle only.** The concrete table
design, foreign key layout, indexes, and downgrade path require separate founder
approval before the migration is written, per the `AGENTS.md` schema and
migration Hard Rules. Spec 0087 records that as its phase gate 2.

---

# Consequences

## Positive consequences

- Case truth becomes queryable rather than ephemeral, which supports the AW-272
  continuity and coherence evals and the AW-278 reveal fairness accounting.
- The alibi contradiction between an `AuthorizedFalsehood` with
  `topic == "location"` and its contradicting evidence becomes an indexed
  comparison with FK integrity, rather than prose against prose.
- Case state survives process restart, so a session resuming mid-play does not
  depend on regenerating from seed and getting an identical result.
- Consistent with the ADR-0016 precedent, so the codebase has one story about
  when gameplay data earns dedicated tables.

## Negative consequences

- **AW-290 grows well beyond its recorded Size `M`.** Six tables, a migration,
  ORM models, and a read/write path are added to work that was already
  substantial. Re-estimation and a probable split are required before
  scheduling, reinforcing the Planner handoff opened by D-101.
- The Pydantic models and the ORM models must be kept in sync, a duplication
  that did not previously exist in this part of the codebase.
- Storage and write cost for an artifact reproducible from `seed`.
- AW-291, the task that actually makes Vesper speak, is delayed by however much
  AW-290 grows. D-102 redirected capacity here specifically to unblock
  Rehearsal 1.

## Trade-offs

Gained: queryable, integrity-enforced case truth and a durable session state.
Lost: the smaller, faster AW-290 that would have shipped typed anchors with no
migration at all, and some of the schedule margin ahead of Rehearsal 1.

---

# References

- `docs/decisions/0017-narrator-slot-resolution-and-wrapper-dressing.md`
- `docs/decisions/0016-aw283-claim-ledger-schema.md`
- `docs/specs/0087-aw-290-narrator-slot-schema-and-wrapper-dressing.md`
- `docs/product/decisions-log.csv`, D-089 and D-103
- `docs/roadmap/tasks/AW-290-narrator-slot-schema-and-wrapper-dressing.md`
- `engine/case/models.py`, `engine/db/orm.py`, `engine/harness/runner.py`
- `AGENTS.md` Hard Rules

## Open questions this decision does not resolve

- The concrete table design, indexes, and downgrade path. Gated on separate
  founder approval.
- Whether the case is written at generation or lazily on first read.
- Whether a persisted case carries a `session_id` foreign key or is standalone
  and referenced by the session.
- AW-290 re-estimation and split, routed to the Planner.
