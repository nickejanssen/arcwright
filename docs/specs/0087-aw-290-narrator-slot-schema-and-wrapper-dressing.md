> Current version: v0.1
> Last updated: 2026-08-05
> Status: Draft
> Canonical path: docs/specs/0087-aw-290-narrator-slot-schema-and-wrapper-dressing.md

# AW-290 Narrator Slot Schema: Structured Location and Time, Case Persistence, and Wrapper Dressing Pack

**Status**: Draft

**Author**: Claude Opus 5 (Spec Author role), from a founder decision interview | **Date**: 2026-08-05

---

# References

- Related ADRs: `docs/decisions/0017-narrator-slot-resolution-and-wrapper-dressing.md` (Accepted, the charter);
  `docs/decisions/0022-resolved-case-persistence.md` (the persistence extension this spec depends on);
  `docs/decisions/0016-aw283-claim-ledger-schema.md` (dedicated-table precedent)
- Decision records: D-089 (ADR-0017 approval), D-103 (case persistence, this spec's interview)
- Task: `docs/roadmap/tasks/AW-290-narrator-slot-schema-and-wrapper-dressing.md`
- Grounding: `docs/design/authoring/couch-race-systems-map.md` sections 2, 8, 9;
  `docs/design/authoring/schema-fit-audit.md`
- Canonical slot registry: `docs/product/2026-07-19-creative-session-master-plan.md` section 5
- Code: `engine/case/models.py`, `engine/case/resolver.py`, `engine/db/orm.py`,
  `nightcap/couch-race.arc.json`
- Authoring source: `docs/design/moodboards/`, `docs/design/line-libraries/`
- Architecture: `AGENTS.md` Hard Rules (schema, migration, cross-module)

---

# Overview

AW-290 gives narrator refrain slots real data to resolve from. It promotes
location and time out of generated prose into typed case truth, adds a short
reference for evidence, persists the resolved case, and adds a per-wrapper
dressing pack for aesthetic slots. It builds sources only. AW-291 owns entry
selection, slot filling, and event emission.

---

# Founder decisions recorded in this spec

Resolved in a decision interview on 2026-08-05. ADR-0017 section "Open
Implementation Questions" delegated the first three to the migration PR; the
fourth and fifth are new.

| # | Question | Decision | Note |
|---|---|---|---|
| 1 | Alembic migration, when the models appear unpersisted | **Add case persistence as part of AW-290** | Chosen against the Spec Author's recommendation to correct the acceptance criterion instead. See Risks. |
| 2 | Anchor placement: `EvidenceEntry` vs `CaseFact` vs shared value object | **Shared value object, referenced by id** | Makes the alibi contradiction a real join rather than prose comparison. |
| 3 | Persistence shape | **Fully normalized tables** | Follows the ADR-0016 precedent for hot-path gameplay data. |
| 4 | Anchor type: enum into per-case set vs free label | **Typed id plus ordered time**, with display labels | Founder asked for the engineering-best answer rather than selecting an option. Rationale below. |
| 5 | `{{evidence}}` short form | **Add `EvidenceEntry.short_label`** | Matches the ADR-0017 recommendation. |
| 6 | Dressing pack ownership | **Founder-reviewed content**, seeded from moodboards | Creates a content approval gate inside this task. |

**Rationale for decision 4**, since it was delegated rather than selected.
Deterministic contradiction detection is the reason. Nightcap's core loop is
interrogation to contradiction to accusation, and `claims` and
`contradiction_flags` already exist for it. A free-label time forces the
comparison "you said the study at nine, the glass was in the conservatory at
nine" into either a model call or nothing. A model call violates platform
principle 2, which forbids the LLM deciding what happened, and costs tokens per
interrogation turn per player against principle 6. A typed comparison is exact
and free. Typed values also index, deduplicate, and generalize across arcs.
Display labels are carried alongside so player-facing text is unaffected.

---

# In Scope

**Typed anchors**

- A `CaseAnchor` value object carrying an anchor id, a location reference into
  the per-case location set, a location display label, a time ordinal, and a
  time display label.
- The time ordinal indexes into a per-case ordered list of time anchors. It is
  self-describing within the case. There is no global clock.
- `ResolvedCase` declares the per-case anchor set once.
- `EvidenceEntry`, `CaseFact`, and `AuthorizedFalsehood` each carry an optional
  anchor reference.
- The resolver populates anchors at case generation, and generates prose **from**
  the anchor. Prose is never parsed back into an anchor.

**Evidence short form**

- `EvidenceEntry.short_label`, generated alongside `text` at case generation.

**Case persistence (new scope, see ADR-0022)**

- Normalized tables: a `cases` root plus `case_cast`, `case_evidence`,
  `case_falsehoods`, `case_facts`, and `case_anchors`.
- Foreign keys from `case_evidence`, `case_facts`, and `case_falsehoods` to
  `case_anchors`.
- One Alembic migration with a working downgrade path.
- SQLAlchemy models in `engine/db/orm.py` and a read/write path for the
  resolved case.

**Wrapper dressing pack**

- A per-wrapper dressing config selected at session start alongside `era` and
  `occasion` in `aesthetic_config.selection_model`.
- Content for the two Rehearsal 1 wrappers only, per D-088: Séance 1928 and
  Big Top 1899.
- Field set sufficient for those two wrappers: drinks, and Big Top stage-name
  templates.
- Content is founder-reviewed before it ships.

**Slot coverage**

- Every slot in the canonical registry maps to a named source: case field,
  dressing pack, session or timer, or scoring. Unmapped slots fail.

---

# Out of Scope

- **Everything AW-291 owns**: reading the line libraries, converting them to a
  runtime format, entry selection, slot filling, wink budget, the Beat 6
  `{{killer}}` gate, and ContentEvent emission.
- **Editing any Vesper refrain line.** Slots stay verbatim. ADR-0017 preserves
  the master plan's Risk 5 verbatim-conversion rule.
- `{{detective}}`, `{{detective_name}}`, `{{flavor}}`, `{{habit}}`: AW-279 owns
  detective identity and it is not built.
- `{{minutes}}`, `{{seconds}}`, `{{count}}`: timer and AW-284 scoring surfaces.
  This spec maps them to their source, it does not build them.
- Dressing content for the four wrappers outside the Rehearsal 1 pair.
- Daily Case slots and the three sample-doc-only slots the registry says must
  not be whitelisted.
- Game-specific vocabulary as schema field names anywhere in `engine/case`.

---

# Human Collaboration Contract

**Interaction profiles:** Decision interview (complete), creative collaboration
(dressing pack content), independent execution (schema, migration, resolver).

**Classification rationale:** The schema shape questions were founder calls and
are now answered. The dressing pack is player-facing voice, so decision 6 makes
it creative collaboration with a content gate. The remaining implementation is
independent execution against this spec.

**Required founder inputs:**

- Approval of this spec.
- Approval of the concrete migration design before it is written, per the
  `AGENTS.md` schema and migration Hard Rules. Decision 1 approves persistence
  in principle; it does not approve a specific table design.
- Approval of the dressing pack vocabulary before it ships, per decision 6.

**Phase gates:**

1. Spec approval. No implementation begins first.
2. Migration design review. The table design, FK layout, and downgrade path are
   presented and approved before any migration file is written.
3. Dressing pack content review. The Séance 1928 and Big Top 1899 vocabulary is
   presented and approved before it is loaded.

**Review package:** This spec, then a migration design note, then the dressing
pack content as a readable list rather than raw JSON.

**Approval evidence:** D-103 records the interview. Spec approval, migration
design approval, and dressing content approval are three separate records and
none may be inferred from another.

**Owner actions:** None external.

---

# Acceptance Criteria

- [ ] `{{location}}` and `{{time}}` resolve from typed anchor fields, not from
      substrings of `EvidenceEntry.text` or `CaseFact.value`.
- [ ] A `CaseAnchor` value object exists, is declared once per case on
      `ResolvedCase`, and is referenced by id from `EvidenceEntry`, `CaseFact`,
      and `AuthorizedFalsehood`.
- [ ] Time anchors carry an ordinal that orders them within the case, and a
      display label. Location anchors carry a reference into the per-case
      location set, and a display label.
- [ ] An `AuthorizedFalsehood` with `topic == "location"` and its contradicting
      evidence reference anchors that can be compared without string matching,
      and a test proves a contradiction is detected by comparison alone.
- [ ] `EvidenceEntry.short_label` is populated at generation for every evidence
      entry, and is not a truncation of `text`.
- [ ] Six normalized tables exist with the FK layout above, and `ResolvedCase`
      round-trips through them without loss.
- [ ] `alembic upgrade head` applies cleanly to an empty schema and to a
      populated one; `alembic downgrade -1` reverses it cleanly.
- [ ] A dressing pack exists for Séance 1928 and Big Top 1899 with drink
      coverage and Big Top stage-name templates, selected at session start
      alongside `era` and `occasion`.
- [ ] Every slot in the canonical registry maps to a named source, and a test
      fails the build if any registry slot is unmapped.
- [ ] The `engine/case` field-name policy is preserved: no game-specific
      vocabulary appears as a schema field name.
- [ ] No Vesper refrain line is edited. A diff check proves
      `docs/design/line-libraries/` is untouched.
- [ ] Founder approval recorded for the migration design and for the dressing
      pack content, as separate records.

---

# Test Plan

**Unit**

- Anchor construction and per-case uniqueness of anchor ids.
- Time ordinal ordering within a case.
- Resolver populates anchors for a seeded case, and the generated prose is
  consistent with the anchor it was generated from.
- `short_label` populated for every evidence entry and distinct from a prefix
  of `text`.
- Dressing pack selection returns the right vocabulary per wrapper, and fails
  loudly on an unknown wrapper.

**Integration**

- Deterministic replay: the same seed produces the same anchor set.
- `ResolvedCase` round-trips through the six tables unchanged.
- Alibi contradiction: a `location` falsehood and its contradicting evidence
  are detected as contradictory by anchor comparison, with no string matching.
- Migration up and down against an empty and a populated schema.

**Registry coverage**

- A test enumerating the canonical registry, asserting each slot has a named
  source, and failing on any unmapped slot. The three sample-doc-only slots
  must be absent from the whitelist.

**Manual**

- Founder review of the dressing pack vocabulary.

---

# Risks and Unknowns

**Risks**

- **Scope. Decision 1 materially grew this task.** AW-290 is recorded as Size
  `M` and now carries six tables, a migration, ORM models, a read/write path,
  typed anchors, resolver changes, a dressing pack, and a content gate. It is
  at least L, plausibly XL. This reinforces the Planner handoff already opened
  by D-101 on the AW-286 record and applies equally here: **AW-290 should be
  re-estimated and probably split before scheduling.** A natural seam is
  anchors and `short_label` in one task, persistence in a second, dressing pack
  in a third.
- **Persistence was not required by the narrator slot problem.** The Spec
  Author recommended correcting the acceptance criterion instead, on the
  evidence that `ResolvedCase` carries a `seed` and is deterministically
  regenerated, so persisting it stores something already reproducible. The
  founder chose persistence. Recorded so the trade is visible, not to reopen it.
- **Rehearsal 1 timing.** D-102 redirected capacity to this content path
  specifically to unblock the rehearsal. A larger AW-290 delays AW-291, which
  is what actually makes Vesper speak. If schedule pressure appears, ADR-0017
  keeps Option C available as a fallback.
- **Anchor and prose drift.** If any code path writes prose without an anchor,
  the typed fields silently diverge from what players read. Mitigated by
  generating prose from the anchor and by the consistency test above.

**Unknowns**

- Whether the case should be written at generation or lazily on first read.
- Whether `case_anchors` needs a uniqueness constraint on
  `(case_id, location_id, time_ordinal)` or whether duplicate anchors are
  legitimate.
- How the dressing pack interacts with `era`, which is currently host-selected
  and independent of wrapper.

---

# Open Questions

- Q1: Does the persisted case need a `session_id` foreign key, or is `case_id`
  standalone with the session referencing it? Affects whether a case can be
  reused across sessions.
- Q2: Do the four non-Rehearsal-1 wrappers get empty dressing packs that fail
  loudly, or no pack at all until authored?
- Q3: Should the registry coverage test live in `engine/tests` or as a build
  step, given AW-291 is the consumer that actually needs the guarantee?
