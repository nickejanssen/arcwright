# AW-289: Couch Race Trivia Mini-Game

**Milestone / Epic:** M5 / M5-I
**Size:** L
**Status:** Planned

## Plain-English Summary

Design and build a net-new trivia-style mini-game package for Couch Race, a
fourth mini-game alongside Crime Scene Smash, Evidence Locker, and Tell Me
Something True (AW-288), per the founder's direction in D-079.

## Why This Matters

D-079 records the founder's explicit choice to add mini-game variety beyond
what D-062/D-064 had already scoped, specifically naming a trivia-type game.
Unlike AW-288 (which integrates an already-approved package), this is
genuinely new content with no existing spec, design, or package -- it needs
its own founder discovery cycle, the same weight AW-281/AW-283/AW-287
received, not a shortcut.

## Player Impact

A fourth distinct mini-game beat, adding pacing variety and a different kind
of challenge (recall/speed under a case-relevant trivia frame) to the
investigation loop.

## Business Value

Further closes the gap between the shipped session and the founder's stated
"Mario Party" bar, and adds a second production-lifecycle mechanic type
beyond match-3/social-bluff, testing the mini-game runtime's extensibility
(D-059) a third way.

## Technical Scope

*Not yet resolved -- this section is intentionally thin pending discovery.*
Known constraints only: must reuse the existing `engine/mini_games/`
package/runtime boundary (D-059, AW-249/AW-250) rather than a bespoke
system; must define an authored delayed-clue fallback so failure cannot make
the case unsolvable (same invariant every existing mini-game package
follows); must not let AI grade or judge trivia answers in a way that
mutates case truth or scoring outside deterministic rules.

## Human Collaboration Contract

**Interaction profile:** Creative collaboration.

**Founder input:** Trivia format and question source (case-specific facts
vs. general trivia vs. both), difficulty/pacing target, scoring integration
with AW-284, target beat placement, and success definition.

**Required phases:** Begin with focused discovery before authoring. Confirm
a short design brief, then present a small representative question set and
scoring-integration example before building the full package. Offer bounded
options and a recommendation, then ask one interactive question at a time,
matching the AW-281/AW-283/AW-287 discovery pattern.

**Gates:** Pause for explicit direction after discovery, the design brief,
the representative sample, and the implemented thin slice. Research and
reversible preparation may continue while the founder is unavailable, but no
creative choice or full implementation may proceed.

**Evidence:** Preserve discovery answers, the design brief, sample review
and founder feedback, explicit checkpoint approvals, dates, and owner
actions.

## Acceptance Criteria

*To be finalized after discovery; placeholder criteria pending the design
brief:*

- [ ] A trivia mini-game package validates against the AW-249 schema and
  loader.
- [ ] The package defines an authored delayed-clue fallback per D-059.
- [ ] Scoring/reward integration with AW-284's race-scoring model is
  deterministic and documented.
- [ ] Package passes AW-250 content and safety review.

## Tests/Verification

- AW-249 schema validator against the new package.
- AW-250 safety review.
- Headless harness run with the package bound into the Couch Race arc.

## Dependencies

- D-079 (founder direction creating this task)
- AW-249/AW-250 mini-game authoring and safety foundation (complete)
- AW-284 (race scoring) for reward-integration shape
- AW-288 (sibling task; both gate AW-286's Rehearsal 1 readiness)

## Must Not Do

- Do not invent or ship trivia content without founder approval (same rule
  as AW-257).
- Do not let a model call decide correctness of a subjective trivia answer
  in a way that isn't deterministic and reproducible.
- Do not skip the discovery/sample-review gates to hit a rehearsal date --
  if discovery cannot complete in time, report that as a real blocker to
  AW-286's readiness, not something to route around.

## Architecture References

- `docs/decisions/0009-mini-game-runtime-boundary.md`
- `docs/product/decisions-log.csv` (D-059, D-079)
- `docs/story-bibles/nightcap-couch-race.md`

## Playtest Relevance

Direct: a new mechanic type is exactly the kind of thing Rehearsal 1 exists
to pressure-test.
