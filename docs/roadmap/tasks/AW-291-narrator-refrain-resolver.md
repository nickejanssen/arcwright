# AW-291: Narrator Refrain Resolver

**Milestone / Epic:** M5 / M5-I
**Size:** M
**Status:** Planned

## Plain-English Summary

Build the runtime component that turns an authored Vesper refrain
library into a rendered narrator line: select the right entry for the
current beat, mood, and wrapper; fill its slots from resolved state;
and emit a ContentEvent with D-070 presentation hints. This is the
consumer the arc already declares but that does not yet exist.

## Why This Matters

`nightcap/couch-race.arc.json` declares
`asset_generation.narrator_dialogue =
"authored_refrain_library_plus_generative_specifics"`, but the
schema-fit audit confirmed no component reads `host_lines` — the
pipeline is specified and unbuilt. Without this task, the authored
libraries (6 wrappers, 468 lines) cannot reach a screen, and Rehearsal
1 has no narrator.

## Player Impact

Vesper speaks: the authored voice, the shift, and the roast reach the
TV in the right beat with case-correct specifics.

## Business Value

This is the runtime half of the platform's headline anti-slop lever
(authored refrains + generated specifics). It is arc-neutral — Daily
Case and every future arc reuse the same resolver — so it directly
advances the platform-reuse thesis.

## Technical Scope

- Consume an authored refrain library (converted from the
  `docs/design/line-libraries/` markdown into an engine-consumable
  content format under `nightcap/content/host_lines/`; conversion is
  verbatim text plus metadata — beat, mood, shift target, slots).
- Select an entry deterministically for the current beat, mood, and
  wrapper, honoring the once-per-session budget for wink entries and
  the Beat-6-only gate on `{{killer}}`.
- Fill slots from the AW-290 resolvable sources (case fields, dressing
  pack, session/timer, scoring). Never invent slot values; a missing
  required source is an error, not a guess.
- Enforce the-host.md hard rules at resolution: never expose the killer
  before The Truth; never reveal which statements were lies.
- Emit a ContentEvent through the existing session event bus and fanout
  router (surface-agnostic; carries D-070 presentation hints; TV
  target for Vesper per §7, with the nudge escalation ladder from D-087
  choosing TV-room / TV-named / silent-UI-phone).
- No model call for Vesper text (the-host.md §5: Vesper speaks only from
  the library). Generation is limited to slot specifics already
  resolved deterministically.

## Human Collaboration Contract

**Interaction profile:** Independent execution against a locked spec,
with a founder checkpoint on the markdown-to-runtime conversion format
(verbatim-text rule: any wording change returns to the founder).

## Acceptance Criteria

- [ ] A converted Séance 1928 + Big Top 1899 library loads and a full
  six-beat session emits a narrator line per beat, slots filled from
  resolved state.
- [ ] Selection is deterministic given a seed; wink budget and
  Beat-6 killer gate are enforced.
- [ ] No Vesper text is model-generated; only slot specifics are
  filled.
- [ ] the-host.md hard rules hold under test (no early killer, no lie
  disclosure).
- [ ] Converted text is byte-verbatim against the approved libraries
  (metadata added, wording unchanged).
- [ ] ContentEvents carry D-070 hints and route to the TV surface;
  nudge ladder resolves per D-087.

## Tests/Verification

- Deterministic-selection test (same seed → same lines).
- Verbatim-conversion test (converted text == library text).
- Hard-rule tests: killer never surfaces before Beat 6; lie-status
  never disclosed.
- Slot-fill test against seeded case + dressing pack.
- Nudge-ladder escalation test (room → named → silent UI).

## Dependencies

- AW-290 (slot sources must exist to fill from)
- AW-279 (detective identity — source for `{{detective}}`)
- AW-276 (arc voice block injection — existing narrator-prompt lineage)
- Live-loop event system (PR #225 lineage) and D-070 presentation hints
- `docs/design/the-host.md` v1.2; `docs/design/line-libraries/`

## Must Not Do

- Do not generate Vesper text from a model (library-only per §5).
- Do not edit refrain wording during conversion (verbatim rule, Risk 5).
- Do not put Vesper on the phone (§7); the nudge floor is UI-voice, not
  Vesper.
- Do not expose case truth (killer, lie-status) ahead of its beat gate.
