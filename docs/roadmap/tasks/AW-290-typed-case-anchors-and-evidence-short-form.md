# AW-290: Typed Case Anchors And Evidence Short Form

**Milestone / Epic:** M5 / M5-I
**Size:** M
**Status:** Planned

> **Rescoped by an approved split, 2026-08-05.** This task previously carried
> anchors, case persistence, a wrapper dressing pack, and a slot registry at
> Size `M`. That was an XL task. The founder approved a four-way split; this
> file now covers the anchors and evidence short form only.
>
> - **AW-293** wrapper dressing pack (M)
> - **AW-294** slot registry and coverage test (S)
> - **AW-295** resolved case persistence (L) — **off the Rehearsal 1 critical path**
>
> **Spec:** `docs/specs/0087-aw-290-narrator-slot-schema-and-wrapper-dressing.md`
> (Approved 2026-08-05). It is the implementation contract for all four tasks
> and supersedes this file where they differ.
> **Plan:** `docs/superpowers/plans/2026-08-05-aw-290-narrator-slot-schema.md`,
> Tasks 1-4.
> **Charter:** ADR-0017 mechanism 1; D-089; D-103 decisions 2, 4, 5.

## Plain-English Summary

Promote location and time out of generated prose into typed case truth: a shared
`CaseAnchor` value object declared once per case and referenced by id from
evidence, facts, and lies. Add a generated short reference for evidence so
`{{evidence}}` resolves to a few words rather than full clue prose.

## Why This Matters

`{{location}}` and `{{time}}` appear 57 and 78 times across the six refrain
libraries. The schema-fit audit proved they are load-bearing case truth
currently buried inside generated `EvidenceEntry.text` and `CaseFact.value`
prose. An alibi is a time plus a place; without typed anchors, checking one
suspect's claim against the evidence means either a model call — which violates
platform principle 2, since the LLM must never decide what happened, and costs
tokens per interrogation turn against principle 6 — or nothing at all.

This is the highest-priority slot gap and the largest single unblocker for
AW-291.

## Player Impact

Suspect alibis and clue timing resolve consistently and fairly; the same
authored line renders correctly across cases and wrappers.

## Business Value

Structured location and time is the ground truth the AW-272 continuity evals and
the AW-278 reveal accounting need. Contradiction detection becomes exact and
free instead of approximate and metered.

## Technical Scope

- `CaseAnchor` value object in `engine/case/models.py`: `anchor_id`,
  `location_ref`, `location_label`, `time_ordinal`, `time_label`. Typed
  reference plus ordered ordinal, both carrying display labels, per D-103
  decision 4.
- `ResolvedCase.anchors` declares the per-case set once;
  `EvidenceEntry`, `CaseFact`, and `AuthorizedFalsehood` carry an optional
  `anchor_id`.
- `EvidenceEntry.short_label`, generated alongside `text` at case resolution.
  Not a truncation.
- The resolver populates anchors at generation and **generates prose from the
  anchor**. Prose is never parsed back into an anchor.
- `engine/case/contradiction.py`: `find_anchor_contradictions`, typed comparison
  only.
- `engine/tests/test_case_naming_contract.py`, the missing guard for the
  field-name policy.

## Implementation notes verified against source, 2026-08-05

- Every model in `engine/case/models.py` sets `extra="forbid"`, so no field can
  be added implicitly. `short_label` is required, which breaks every existing
  `EvidenceEntry` construction site until each is updated.
- `engine/db/orm.py` has **no case tables at all**. Nothing here touches the
  database; `engine/case/` imports nothing from `engine/db/` and must not start.
- **The new naming-contract test must not copy the sibling forbidden-word
  lists.** `engine/tests/test_claims_naming_contract.py:14-33` forbids
  `culprit`, and `engine/case/models.py` already uses `culprit_id` (line 159)
  and `is_culprit` (line 24). The module docstring at lines 3-6 defines the
  policy as game vocabulary living inside string *values*; ADR-0017 lines 70-74
  names **dressing** as the thing that must never become a schema field name.
  Scope the guard to dressing vocabulary.
- Do not touch `run_seed`. Known gap, needs cross-module approval.

## Acceptance Criteria

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
- [ ] The same seed produces the same anchor set.
- [ ] The `engine/case` field-name policy is preserved and now has a test.
- [ ] No Vesper refrain line is edited.

## Tests/Verification

- Anchor construction and per-case uniqueness of anchor ids.
- Time ordinal ordering within a case.
- Resolver populates anchors for a seeded case; generated prose is consistent
  with the anchor it was generated from.
- `short_label` populated for every entry and distinct from a prefix of `text`.
- Deterministic replay: same seed, same anchor set.
- Alibi contradiction detected by anchor comparison, with an AST guard proving
  no string matching in the implementation.

## Dependencies

- AW-281 (case resolution — the surface being extended)
- ADR-0017 / D-089, D-103

## Must Not Do

- Do not edit narrator refrain text.
- Do not introduce game-specific vocabulary into `engine/case` schema field
  names.
- Do not add an `engine/db` or `sqlalchemy` import to `engine/case/`.
- Do not touch `run_seed`.
