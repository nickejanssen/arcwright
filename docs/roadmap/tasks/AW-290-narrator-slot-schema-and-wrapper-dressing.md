# AW-290: Narrator Slot Schema — Structured Location/Time And Wrapper Dressing Pack

**Milestone / Epic:** M5 / M5-I
**Size:** M
**Status:** Planned

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
