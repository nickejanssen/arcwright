# AW-295: Resolved Case Persistence (Six Normalized Tables)

**Milestone / Epic:** M5 / M5-I
**Size:** L
**Status:** Planned — **not on the Rehearsal 1 critical path**

> **Split from AW-290**, approved by the founder 2026-08-05.
>
> **Charter:** `docs/decisions/0022-resolved-case-persistence.md` (Accepted),
> D-103 decisions 1 and 3. **Spec:**
> `docs/specs/0087-aw-290-narrator-slot-schema-and-wrapper-dressing.md`
> (Approved). **Migration design:**
> `docs/specs/0087-appendix-a-case-persistence-migration-design.md`.
> **Plan:** `docs/superpowers/plans/2026-08-05-aw-290-narrator-slot-schema.md`,
> Tasks 11-14.

## Plain-English Summary

Persist the resolved case — cast, evidence, facts, falsehoods, and anchors — to
six normalized tables so case truth is queryable and survives a process restart,
instead of being held only in memory.

## Why This Matters And Why It Is Sequenced Last

ADR-0022 gives the rationale: queryable case truth with referential integrity
supports the AW-272 continuity evals and AW-278 reveal accounting, and the alibi
contradiction becomes an indexed join.

**It supplies no narrator slot.** `{{location}}` and `{{time}}` resolve from
`CaseAnchor`, `{{evidence}}` from `EvidenceEntry.short_label`, and the aesthetic
slots from the dressing pack. Nothing resolves from a database row. AW-291 and
Rehearsal 1 do not depend on this task. ADR-0022 lines 104-106 predicted exactly
this delay risk; the split answers it.

## Player Impact

None at Rehearsal 1. Later: a session resuming mid-play does not depend on
regenerating an identical case from seed.

## Business Value

Case truth becomes queryable ground truth for evals and reveal fairness
accounting, consistent with the ADR-0016 dedicated-table precedent.

## Technical Scope

- Six tables: `cases`, `case_anchors`, `case_cast`, `case_evidence`,
  `case_facts`, `case_falsehoods`, with real foreign keys including anchor
  references from evidence, facts, and falsehoods.
- `cases.session_id` FK to `sessions.session_id`, NOT NULL, `UNIQUE(session_id)`
  — one case row per session, per the founder's Q1 answer.
- SQLAlchemy models in `engine/db/orm.py`; Alembic migration `0008` with a
  working downgrade.
- Read/write path in `engine/session/case_store.py`. **`engine/case/` stays
  pure** and gains no `engine/db` import — the precedent is `engine/resources/`
  persisted by `engine/telemetry/resources.py`.

## Blocking finding: no production caller exists

Verified 2026-08-05 by reading source. Writing a `cases` row needs a real
`sessions` row, a `ResolvedCase`, and a DB session held together. Nothing in
production holds all three:

- `engine/case/` has zero DB coupling; its only outward dependency is
  `engine.arc.models` (`engine/case/resolver.py:44`).
- Its sole production caller is `engine/harness/runner.py:240`, an in-memory
  harness with no DB access at all.
- That harness mints its `session_id` from the seeded RNG
  (`engine/harness/runner.py:196-197`). **No `sessions` row is ever inserted**,
  so a FK insert from there fails.
- `AccusationResolver` has no production caller either.
- All three coexist only in `engine/tests/test_scoring_integration.py:233-235`,
  which bridges them by hand in test code.

The tables and round-trip can be built and fully tested. **Nothing in production
writes them until `engine/session/service.py:start_session` is wired to call
them** — which touches `engine/case`, `engine/session`, and `engine/db`
together, an `AGENTS.md` cross-module Hard Rule. That wiring is deliberately
**not** in this task and needs its own design review.

## Human Collaboration Contract

**Interaction profile:** Independent execution, gated on one approval.

**Migration design gate.** ADR-0022 lines 74-77 approve persistence in principle
only. The concrete table design, FK layout, indexes, and downgrade path require
separate founder approval before the migration file is written, per `AGENTS.md`
Hard Rules. The design is written and awaiting that approval in
`docs/specs/0087-appendix-a-case-persistence-migration-design.md`.

## Acceptance Criteria

- [ ] Six normalized tables exist with the approved FK layout, and
      `ResolvedCase` round-trips through them without loss.
- [ ] `alembic upgrade head` applies cleanly; `alembic downgrade -1` reverses it
      cleanly. **See the verification caveat below.**
- [ ] Anchor references survive the round trip as real foreign keys.
- [ ] `engine/case/` still imports nothing from `engine/db/` or `sqlalchemy`.
- [ ] Founder approval of the migration design recorded as its own row.

## Verification caveat, open for founder decision

The repo's only migration up/down test,
`engine/tests/test_mini_game_runtime.py:798-832`, **skips unless `DATABASE_URL`
is set** (`:808-810`), and its `integration` marker is not registered in
`pyproject.toml` (which lists only `slow` at lines 23-25). The upgrade/downgrade
criterion **cannot be met by CI as configured.** Either CI gains a Postgres
service, or the criterion is honestly restated as "verified locally against
Postgres, with command output recorded in the PR." This is a founder call and is
unresolved.

## Dependencies

- AW-290 (`CaseAnchor` defines the `case_anchors` column shape)
- ADR-0022 / D-103 (the charter)

## Must Not Do

- Do not write the migration before the design-approval record exists.
- Do not add an `engine/db` import to `engine/case/`.
- Do not introduce a repository or DAO layer; this codebase has none.
- Do not wire `start_session` here — separate cross-module review.
- Do not claim CI verified the migration up/down path.
