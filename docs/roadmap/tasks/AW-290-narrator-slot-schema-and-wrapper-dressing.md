# AW-290: Narrator Slot Schema — Structured Location/Time And Wrapper Dressing Pack

**Milestone / Epic:** M5 / M5-I
**Size:** M
**Status:** Planned

> **Spec:** `docs/specs/0087-aw-290-narrator-slot-schema-and-wrapper-dressing.md`
> (Draft, awaiting founder approval). It is the implementation contract for this
> task and supersedes this file where they differ.
>
> **Decision interview complete, 2026-08-05 (D-103).** The three ADR-0017 open
> questions this contract required are answered, plus two more. Anchors are a
> shared `CaseAnchor` value object referenced by id, typed location reference
> plus ordered time ordinal with display labels; `{{evidence}}` gets a generated
> `EvidenceEntry.short_label`; the dressing pack is founder-reviewed content
> capped at the D-088 Rehearsal 1 pair.
>
> **Scope grew. The migration criteria below are real, not stale.** D-103 and
> `docs/decisions/0022-resolved-case-persistence.md` add persistence of the
> resolved case in six normalized tables. ADR-0017 did not authorize that; ADR
> 0022 does. Persistence is approved in principle only. The concrete table
> design, foreign keys, indexes, and downgrade path need separate founder
> approval before the migration is written, per the `AGENTS.md` Hard Rules.
>
> **Planner handoff.** Size `M` no longer reflects this task. It now carries
> typed anchors, `short_label`, six tables, a migration, ORM models, a
> read/write path, resolver changes, a dressing pack, and a content approval
> gate. Re-estimate and consider splitting along the seam suggested in spec
> 0087 before scheduling.

## Plain-English Summary

Give the narrator refrain slots real data to resolve from: promote
location and time to structured case-resolution fields, and add a
per-wrapper dressing pack for aesthetic slots (drink, stage name, tier,
weather, and the rest). Implements ADR-0017 / D-089.

## Why This Matters

The authored Vesper refrain libraries (`docs/design/line-libraries/`)
carry `{{slot}}` variables. The schema-fit audit
(`docs/design/authoring/schema-fit-audit.md`) proved that
location/time are load-bearing case truth currently buried inside
generated prose, and that pure aesthetic dressing has no home at all.
Without this task, no launch- or rehearsal-pair line can be rendered
correctly, and the AW-278 reveal's fairness accounting cannot query a
structured time or place.

## Player Impact

Suspect alibis, clue timing, and wrapper flavor resolve consistently
and fairly; the same authored line renders correctly across cases and
wrappers.

## Business Value

Structured location/time is the ground truth the continuity/coherence
evals (AW-272) and the reveal need; the dressing pack generalizes to
every future wrapper and arc, directly serving the platform's
easy-to-create-games goal.

## Technical Scope

- Add typed location and time anchors to the case-resolution surface
  (`engine/case/models.py` — `EvidenceEntry` and/or `CaseFact`, exact
  placement per ADR-0017's open implementation questions), populated by
  the resolver at case generation. Preserve the arc-agnostic field-name
  policy: `location`/`time` are arc-neutral concepts, not game
  vocabulary.
- Migration for the new fields with a downgrade path.
- Add a per-wrapper `dressing` config selected at session start
  alongside `era`/`occasion`, seeded from the moodboards
  (`docs/design/moodboards/`): drink names, stage-name templates, tier
  labels, weather options, room/floor grammar, errata flavor.
- Add `EvidenceEntry.short_label` (or equivalent) so `{{evidence}}`
  resolves to a short reference, not full clue prose (ADR-0017 open
  question; `short_label` recommended).
- Do not put game-specific dressing vocabulary into the arc-agnostic
  case model; dressing lives in wrapper config only.

## Human Collaboration Contract

**Interaction profile:** Decision interview (schema shape) plus
independent execution (migration).

- Confirm the ADR-0017 open implementation questions with the founder
  before the migration: anchor placement (EvidenceEntry vs CaseFact vs
  shared value object), location/time type (enum-into-per-case-set vs
  free label), and whether the dressing pack is founder-reviewed
  content or engineering-owned config.

## Acceptance Criteria

- [ ] Location and time resolve from typed case fields, not from
  substrings of generated text.
- [ ] Migration applies and downgrades cleanly (`alembic upgrade head`
  / downgrade).
- [ ] A per-wrapper dressing pack exists for at least the Rehearsal 1
  pair (Séance 1928, Big Top 1899) with drink and stage-name coverage.
- [ ] Every slot in the master-plan §5 canonical registry resolves to a
  named source (case field, dressing pack, session/timer, or scoring),
  with no slot left unmapped.
- [ ] `engine/case` arc-agnostic field-name policy is preserved (no
  game-specific dressing as schema field names).
- [ ] No Vesper refrain line is edited (verbatim-conversion rule).

## Tests/Verification

- Migration up/down test.
- Resolver test: a seeded case populates location/time fields and they
  match the case's authored clue chain.
- Dressing-pack selection test across the Rehearsal 1 wrappers.
- Registry-coverage test: assert every §5 slot has a resolvable source.

## Dependencies

- ADR-0017 / D-089 (this task's charter)
- AW-281 (case resolution — the surface being extended)
- `docs/design/authoring/schema-fit-audit.md`
- `docs/design/line-libraries/00-direction.md` (slot registry)

## Must Not Do

- Do not edit narrator refrain text.
- Do not introduce game-specific vocabulary into `engine/case` schema
  field names.
- Do not bypass migration review (Hard Rule, AGENTS.md).
