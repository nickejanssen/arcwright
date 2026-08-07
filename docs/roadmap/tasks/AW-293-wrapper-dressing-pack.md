# AW-293: Wrapper Dressing Pack (Séance 1928 + Big Top 1899)

**Milestone / Epic:** M5 / M5-I
**Size:** M
**Status:** Planned

> **Split from AW-290**, approved by the founder 2026-08-05. AW-290 was
> recorded Size `M` and carried anchors, persistence, a dressing pack, and a
> registry. This task takes the dressing pack.
>
> **Spec:** `docs/specs/0087-aw-290-narrator-slot-schema-and-wrapper-dressing.md`
> (Approved). **Plan:** `docs/superpowers/plans/2026-08-05-aw-290-narrator-slot-schema.md`,
> Tasks 5-7. **Charter:** ADR-0017 mechanism 2; D-089; D-103 decision 6.

## Plain-English Summary

Give the aesthetic narrator slots — `{{drink}}`, `{{stage_name}}` — a per-wrapper
vocabulary selected at session start alongside `era` and `occasion`, so the same
authored Vesper line renders correctly in a séance parlour and under a big top.

## Why This Matters

`{{drink}}` appears 51 times across the six refrain libraries and
`{{stage_name}}` 16 times in `big-top-1899.md`. Neither has any home: the case
model deliberately holds no game-specific vocabulary, and the arc exposes only
`era` and `occasion`. Without this, no Rehearsal 1 line containing those slots
can render.

## Player Impact

Wrapper flavour resolves consistently; Vesper sounds like she belongs to the
world the players chose.

## Business Value

The pack generalises: every future wrapper, arc, and genre adds dressing as
config, not code — directly serving the easy-to-create-games goal.

## Technical Scope

- `engine/dressing/` — `models.py`, `loader.py`, `errors.py`. Arc-agnostic
  container field names only; wrapper vocabulary lives in the string values.
- `nightcap/dressing/wrappers.json` — all six wrapper ids declared, two authored.
- Two distinct errors per the founder's Q2 answer: `DressingPackNotAuthored`
  for a declared wrapper with no content, `UnknownWrapper` for an id outside
  the six. They are different bugs and must not share an error type.
- Declare `wrapper` in `nightcap/couch-race.arc.json` `selection_model`.

## Human Collaboration Contract

**Interaction profile:** Creative collaboration (content) plus independent
execution (loader).

**Content gate.** D-103 decision 6 makes the vocabulary founder-reviewed
content, not engineering config, because drinks and stage names reach players
verbatim as Vesper's voice. Present as a readable list and stop. Approval is its
own record in `docs/product/decisions-log.csv`.

**The moodboards do not contain this vocabulary.** Verified 2026-08-05:
`docs/design/moodboards/seance-1928.md` has no drink pool (only prose —
"decanter" `:33,:59,:109`, "absinthe" `:60`, "cut crystal" `:80`), and
`big-top-1899.md` has **no drink vocabulary at all** plus exactly two stage
titles at `:50-52`, with its own handoff list at `:170-171` recording stage
titles as still to author. This is original authoring with the moodboards as
tone reference, not transcription. Budget accordingly.

## Acceptance Criteria

- [ ] A dressing pack exists for Séance 1928 and Big Top 1899 with drink
      coverage and Big Top stage-name templates.
- [ ] All six wrapper ids are declared; the four unauthored ones raise
      `DressingPackNotAuthored`, and an unknown id raises `UnknownWrapper`.
- [ ] The two errors are distinct classes, neither subclassing the other.
- [ ] `wrapper` is declared in `aesthetic_config.selection_model` alongside
      `era` and `occasion`.
- [ ] No game-specific dressing vocabulary appears as a schema field name.
- [ ] Founder approval of the vocabulary recorded as its own decision row.

## Tests/Verification

- Dressing-pack selection across the Rehearsal 1 wrappers.
- Both error paths, asserted as distinct types.
- `engine/tests/test_case_naming_contract.py` still passes.

## Dependencies

- AW-290 (the naming-contract test that guards the boundary)
- D-088 (the Rehearsal 1 wrapper pair)

## Must Not Do

- Do not edit narrator refrain text.
- Do not put dressing vocabulary into `engine/case` schema field names.
- Do not author the four non-Rehearsal-1 wrappers; they are out of scope per
  spec 0087 and D-103.
- Do not ship vocabulary before the founder content gate clears.
