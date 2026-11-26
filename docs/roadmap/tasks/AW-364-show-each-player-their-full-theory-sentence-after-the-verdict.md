---
id: productroadmap.roadmap.tasks.aw-364-show-each-player-their-full-theory-sentence-after-the-verdict
namespace: product-roadmap
title: "AW-364: Show Each Player Their Full Theory Sentence After The Verdict"
owner: Nico Janssen
status: draft
review_by: "2027-02-26"
sensitivity: internal
source: authored
x-scope-evidence: none
tags: []
supersedes: []
---

# AW-364: Show Each Player Their Full Theory Sentence After The Verdict

**Milestone / Epic:** M7 / M7-B  
**Size:** S  
**Product:** Arcwright engine and API, with the Nightcap phone screen as the first user  
**Owner:** One build session, after founder approval of its plan  
**GitHub issue:** [#504](https://github.com/nickejanssen/arcwright/issues/504)  
**Target date:** after the founder's test on 1 December 2026, unless that test shows players miss it (D-149, D-156)

## Plain-English Summary

After the Verdict, each phone shows the player's own theory as a list: each blank, their answer, and Right or Wrong. Spec 0095 (Q5) asks for the theory read back as the full sentence the player filled in. The phone can't do that today because, once Last Call ends, the engine returns only the saved answers, without the sentence or the blank labels.

## Why This Matters

- Found while building AW-333 part B (pull request #503, "Gaps"). Recorded there from `engine/session/commit_phase.py`: after Last Call, `read_form` has no entry, so `GET /me/theory` returns answers only.
- The list version works for the 1 December test. The full sentence is what makes the result feel like your own account of the crime (inferred).
- An answer that is neither in the player's holdings nor publicly revealed is left out of the list today.

## Technical Scope

1. Let a player read back their own locked theory, including the account text and slot labels, from the recap phase onward. Never another player's theory.
2. Keep it game-agnostic: the engine returns the authored account and labels as data. Wording and layout stay in the surface.
3. Update the phone's result screen (screen 18) to show the sentence, falling back to today's list if it is missing.

## Human Collaboration Contract

**Interaction profile:** Independent execution after plan approval. It touches what a phone may read, so the founder approves the plan in his own words.

## Acceptance Criteria

1. From the recap phase on, a signed-in player can read their own full theory sentence. Before that, the read returns nothing new.
2. A test proves a player cannot read another player's theory through the real API route.
3. Screen 18 shows the sentence with Right or Wrong per blank.
4. `engine/` gains no reference to Nightcap, a game title or a murder mystery.

## Tests/Verification

- `pytest engine/tests/` and the API tests for the theory route.
- `npm test --prefix dashboard`.
- All six pull request checks pass, and every review thread is resolved.

## Dependencies

- AW-333 part B (pull request #503).

## Must Not Do

- Do not expose another player's theory or any unrevealed case content.
- Do not add a dependency, schema change or migration without approval.
- Do not read or quote files in `nightcap/cases/`.
