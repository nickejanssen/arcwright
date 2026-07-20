# AW-289: Couch Race Trivia Mini-Game

> Current version: v0.2
> Last updated: 2026-07-20
> Status: Planned; design brief drafted and awaiting founder approval
> Canonical path: docs/roadmap/tasks/AW-289-couch-race-trivia-mini-game.md

**GitHub:** [#258](https://github.com/nickejanssen/arcwright/issues/258)

**Selected Rehearsal 1 game:** The Interrogation Room

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
of challenge (case recall under interrogation pressure) to the investigation
loop. The selected game must feel like Murder Mystery Trivia rather than a
detached general-knowledge quiz.

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

The proposed design is recorded in `docs/specs/0076-aw-289-interrogation-room.md`.
It remains a draft until the founder approves the design brief and
representative question/scoring sample.

The proposed content direction is per-session generated, setting- and
genre-matched trivia with occasional case callbacks. The proposed adaptive
runtime concept is platform-neutral **adaptive room momentum**. Immersion is
treated as a playtest outcome, not an opaque runtime score. The first slice
uses resolved narrative pacing context plus observable participation,
response pace, challenge fit, player count, format variety, spotlight balance,
session tone, and content readiness signals.

## Human Collaboration Contract

**Interaction profile:** Creative collaboration.

**Founder input:** Confirm or revise the proposed hybrid question source,
case-relevant question framing, difficulty/pacing target, individual answer
model, scoring integration with AW-284, Beat 3 placement, and success
definition.

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
- [ ] The Interrogation Room is the only new trivia game included in the
  Rehearsal 1 build.
- [ ] Questions are generated per session within authored tone, safety,
  structure, answer, and solvability constraints.
- [ ] Generated content validates its evidence basis and current narrative
  grounding before delivery; unestablished or future clues cannot leak.
- [ ] Adaptive selection uses platform-neutral room-momentum signals and
  bounded deterministic policy rules.
- [ ] Correct, incorrect, late, duplicate, invalid, and timeout submissions
  resolve deterministically.
- [ ] Private answers and clue payloads respect the two-surface privacy
  contract.
- [ ] Existing Crime Scene Smash, Evidence Locker, and Tell Me Something
  True packages remain unaffected.

## Tests/Verification

- AW-249 schema validator against the new package.
- AW-250 safety review.
- Headless harness run with the package bound into the Couch Race arc.

## Dependencies

- D-079 (founder direction creating this task)
- AW-249/AW-250 mini-game authoring and safety foundation (complete)
- AW-284 (race scoring) for reward-integration shape
- AW-288 (sibling task; both gate AW-286's Rehearsal 1 readiness)
- AW-286 (rehearsal readiness; must not close until this task and AW-288 are
  ready)

## Must Not Do

- Do not invent or ship trivia content without founder approval (same rule
  as AW-257).
- Do not let a model call decide correctness of a subjective trivia answer
  in a way that isn't deterministic and reproducible.
- Do not skip the discovery/sample-review gates to hit a rehearsal date --
  if discovery cannot complete in time, report that as a real blocker to
  AW-286's readiness, not something to route around.
- Do not build or schedule Contradiction Trap, Planted Evidence, Alibi
  Auction, or Chain of Custody before Rehearsal 1.
- Do not introduce player-killer or informant roles into Couch Race.
- Do not add client-side authority for timers, validation, scoring, outcomes,
  persistence, or clue unlocking.

## Architecture References

- `docs/decisions/0009-mini-game-runtime-boundary.md`
- `docs/product/decisions-log.csv` (D-059, D-079)
- `docs/story-bibles/nightcap-couch-race.md`

## Playtest Relevance

Direct: a new mechanic type is exactly the kind of thing Rehearsal 1 exists
to pressure-test.
