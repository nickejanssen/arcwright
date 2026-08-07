# AW-294: Machine-Readable Slot Registry And Coverage Test

**Milestone / Epic:** M5 / M5-I
**Size:** S
**Status:** Planned

> **Split from AW-290**, approved by the founder 2026-08-05.
>
> **Spec:** `docs/specs/0087-aw-290-narrator-slot-schema-and-wrapper-dressing.md`
> (Approved). **Plan:** `docs/superpowers/plans/2026-08-05-aw-290-narrator-slot-schema.md`,
> Tasks 8-10. Placement resolved by the founder's Q3 answer: pytest in
> `engine/tests` reading a data file under `nightcap/`.

## Plain-English Summary

Turn the canonical slot registry from prose in a planning doc into a checked-in
data file, and add a test that fails the build if any slot has no source.

## Why This Matters

The registry lives only as markdown at
`docs/product/2026-07-19-creative-session-master-plan.md` section 5. AW-291
cannot validate its conversion against prose, and spec 0087 requires a test that
fails on any unmapped slot. Making the registry data is the prerequisite for
both.

## Player Impact

None directly. This prevents a slot silently rendering as literal `{{drink}}`
text in front of players.

## Business Value

Machine-checkable authoring contract; the conversion in AW-291 gets a real gate
instead of a manual read-through.

## Technical Scope

- `nightcap/content/slot_registry.json` — every slot with a named source:
  `case_anchor`, `case_field`, `dressing_pack`, `session_timer`, `scoring`, or
  `identity_aw279`.
- `engine/tests/test_slot_registry.py` — every registry slot has a source; the
  source actually exists (checked against `CaseAnchor.model_fields` and
  `DressingPack.model_fields`); slots from unbuilt systems are asserted as an
  exact expected set rather than skipped.
- The registry file lives under `nightcap/` and the test enumerates whatever it
  declares, so no Nightcap slot vocabulary enters engine code.

**Note for AW-291, which is the production consumer.** A test under
`engine/tests/` may name a `nightcap/` path directly —
`engine/tests/test_case_resolver.py` is the existing precedent. **Production
code under `engine/` may not.** When AW-291 reads this registry at runtime it
must resolve the path by generic `arc_id` prefix match against a registry file
in `config/`, the way `resolve_case_resolution_config_path`
(`engine/case/loader.py:95`) and `engine/arc/registry.py` already do. AW-293
establishes exactly this pattern for the dressing pack in
`config/dressing_registry.json`; follow it rather than hardcoding a path.

## Two registry errors to correct

Verified 2026-08-05 by grepping `docs/design/line-libraries/`:

1. Master plan line 259 claims `{{tier}}` "appears in both sci-fi wrappers —
   shared sci-fi slot". It does not. All 9 occurrences are in `sim-reunion.md`;
   `orbital-gala-2087.md` has **zero**. `docs/design/authoring/schema-fit-audit.md`
   inherited the error.
2. Master plan line 270 lists `{{complication_object}}` as existing "in
   discovery samples". It appears nowhere in `docs/design/line-libraries/`; its
   only repo occurrence is `docs/design/authoring/story-to-arc-exemplar.md:126`.

Correct both with a dated note recording what changed and why. Do not silently
rewrite. Without this the coverage test asserts a false mapping from its first
commit.

## Acceptance Criteria

- [ ] Every slot in the registry maps to a named source, and a test fails the
      build if any registry slot is unmapped.
- [ ] The three sample-doc-only slots (`{{time_1..3}}`, `{{suspect_3}}`,
      `{{complication_object}}`) are absent from the whitelist.
- [ ] `{{tier}}` is recorded against Sim Reunion only.
- [ ] The registry set matches the tokens actually present in the line
      libraries, minus documented exclusions.
- [ ] No Vesper refrain line is edited. A diff check proves
      `docs/design/line-libraries/` is untouched.

## Tests/Verification

- Registry coverage test as above.
- Committed diff guard on `docs/design/line-libraries/`.

## Dependencies

- AW-290 (`CaseAnchor` must exist for anchor-sourced slots to verify)
- AW-293 (`DressingPack` must exist for dressing-sourced slots to verify)

## Must Not Do

- Do not edit narrator refrain text. Correcting the master-plan registry
  section is a different file and is explicitly permitted.
- Do not whitelist the sample-doc-only slots.
