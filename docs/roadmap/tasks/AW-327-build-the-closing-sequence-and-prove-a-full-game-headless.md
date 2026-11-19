---
id: productroadmap.roadmap.tasks.aw-327-build-the-closing-sequence-and-prove-a-full-game-headless
namespace: product-roadmap
title: "AW-327: Build The Closing Sequence And Prove A Full Game Headless"
owner: Nico Janssen
status: active
review_by: "2027-02-16"
sensitivity: internal
source: authored
x-scope-evidence: D-112, D-118, D-123
tags: []
supersedes: []
---

# AW-327: Build The Closing Sequence And Prove A Full Game Headless

**Milestone / Epic:** M7 / M7-B  
**Size:** M  
**Product:** Shared (Arcwright and Nightcap)  
**Owner:** One AI build session (Claude or Codex); the founder reviews ten sample lines  
**Target date:** 2026-12-04

## Plain-English Summary

After every theory is locked, show who each player accused, then the written truth, then the result, then one written line about how each player played, chosen by rule from what they really did. Then prove in a test that a whole game runs from join to that last line. It is Part J of spec 0094.

## Why This Matters

- The thin version's must-have list ends with the accused reveal, the Truth, the Verdict and a short Postmortem. None of the last two exists.
- The status page requires a headless run at two and at four players before the founder TV run.
- Filed under D-119 when spec 0094 was drafted on 2026-11-16: no existing task covered the endgame build.

## Technical Scope

- Three phase kinds on the clock from spec 0093: `reveal`, `result`, `recap`. The written truth uses the existing `scene` phase.
- The measures of what each player did, worked out from saved records only.
- Choosing one written line per player by rule, with no repeats and a fallback.
- A route to read the result: the public part for anyone in the session, the private part for its own player.
- The named headless proof from join to the last recap line, in all three result branches.
- A made-up set of recap lines in the test fixtures. The real lines are content.

## Human Collaboration Contract

**Interaction profile:** Independent execution after plan approval, then creative collaboration for the lines.

- Blocked until AW-326 is merged. Needs AW-304 for the measures.
- The founder reviews ten sample recap lines before the full set is written (spec 0094, phase gate 3). The lines describe behaviour, not the solution, so they do not spoil the case.

## Acceptance Criteria

- [ ] The "Part J" and "Whole game" acceptance criteria of spec 0094 pass.
- [ ] No model call writes or chooses any line.
- [ ] The founder's review of ten sample lines is recorded on the issue.

## Tests/Verification

- `python -m pytest engine/tests/test_endgame_headless.py -q`
- `python -m pytest engine/tests -q`
- `python -m ruff check engine api`

## Dependencies

- AW-326, AW-304
- Spec: `docs/specs/0094-endgame-for-the-thin-version.md`

## Must Not Do

- Do not write a line that claims what a player thought. Only what the engine saw happen.
- Do not send any part of a theory to the room except the one answer the case marks as shown first.
- Do not order the players in the `reveal` event by whether they are right, or by anything derived from it; use a neutral order such as seat order. Staging and order for the room are Nightcap's, set in its files, not the engine's (D-135).
- Do not add a prompt or a model call. A generated Postmortem needs its own approval.

## Kickoff Prompt

> Read `AGENTS.md`, `HANDOVER.md` and `docs/specs/0094-endgame-for-the-thin-version.md`. Confirm that AW-326 is merged; if not, stop. Task AW-327: build Part J and the join-to-recap headless proof. Write the tests first. Write a plan and stop for founder approval. Draft ten sample recap lines for the founder to review before writing more.
