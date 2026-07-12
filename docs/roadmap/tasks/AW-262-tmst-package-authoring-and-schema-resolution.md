# AW-262: TMST Package Authoring and Schema Resolution

**Milestone / Epic:** M5 / M5-F
**Size:** M
**Status:** Complete

## Plain-English Summary

Author the Tell Me Something True (TMST) mini-game package on disk and
resolve the open `deflection_tendency` structured-output schema question
raised in spec 0061, so the rest of the M5-F implementation chain can begin.

## Why This Matters

Spec 0061 (AW-258) approved the TMST design and game ID but did not produce
the on-disk package or close the behavioral-output schema question. Without
that resolution, the runtime (AW-263), API and SDK (AW-264), and web
rendering (AW-265) work cannot proceed.

## Player Impact

Indirect. This task produces the authored content (prompts, narrator copy
for High Society, Corporate, Sci-Fi wrappers, authored delayed-clue
fallback) real humans will encounter in Rehearsal 2.

## Business Value

Closes the last design-side ambiguity in the TMST workstream and produces
the founder-approved content that AW-266 will rehearse.

## Technical Scope

- Author `nightcap/mini_games/tell-me-something-true/` package per spec 0061:
  manifest, definition, content, narrator copy across all three diegetic
  wrappers (High Society, Corporate, Sci-Fi).
- Resolve `deflection_tendency` open question: either extend the AW-249
  schema to support map-shaped behavioral outputs, or formalize the
  "scalar declaration plus event-payload-only" workaround. Record the
  resolution in the package definition and in a short decision note linked
  from the spec.
- Produce the authored delayed-clue fallback even though TMST is
  non-clue-gating per spec 0061's fallback contract.
- Founder content sign-off required before lifecycle leaves `draft`.

## Acceptance Criteria

- [ ] Package validates against the AW-249 schema and loader.
- [ ] Package passes the AW-250 content and safety review.
- [ ] `deflection_tendency` schema resolution is recorded and consistent
  across the package definition and spec 0061 follow-up note.
- [ ] All three diegetic wrappers (High Society, Corporate, Sci-Fi) have
  authored narrator copy.
- [ ] Authored delayed-clue fallback is present and documented.
- [ ] Founder content sign-off recorded.

## Tests/Verification

- Run AW-249 schema validator against the package.
- Run AW-250 safety review on the package.
- Manually walk through each diegetic wrapper's narrator script.

## Dependencies

- AW-249 mini-game authoring foundation (complete)
- AW-250 mini-game content resolution and safety (complete)
- AW-258 spec 0061 approved
- D-063 founder approval of TMST as social-opener design candidate

## Must Not Do

- Do not ship runtime, API, SDK, or rendering code in this task.
- Do not bypass founder content sign-off.
- Do not wire behavioral signals into killer assignment or cross-session
  behavior (v1.1 scope per spec 0061).

## Architecture References

- `docs/specs/0061-aw-258-tell-me-something-true.md`
- `docs/specs/0046-aw-249-nightcap-mini-game-authoring-foundation.md`
- `docs/specs/0047-aw-250-mini-game-content-resolution-and-safety.md`
- `docs/decisions/0009-mini-game-runtime-boundary.md`
- `docs/story-bibles/nightcap-murder-mystery.md`

## Playtest Relevance

Produces the authored package AW-266 will rehearse with real humans.
