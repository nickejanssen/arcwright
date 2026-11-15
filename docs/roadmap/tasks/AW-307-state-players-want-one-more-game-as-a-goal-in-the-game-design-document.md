---
id: productroadmap.roadmap.tasks.aw-307-state-players-want-one-more-game-as-a-goal-in-the-game-design-document
namespace: product-roadmap
title: "AW-307: State \"Players Want One More Game\" As A Goal In The Game Design Document"
owner: Nico Janssen
status: active
review_by: "2027-02-15"
sensitivity: internal
source: authored
x-scope-evidence: D-116
tags: []
supersedes: []
---

# AW-307: State "Players Want One More Game" As A Goal In The Game Design Document

**Milestone / Epic:** M7 / M7-B  
**Size:** S  
**Product:** Nightcap  
**Owner:** One Scribe session; founder approves the wording  
**Target date:** 2026-11-21

## Plain-English Summary

The founder's goal that people should want to play again after every game is recorded as a decision (D-116) but is not stated in the game design document. Add it, with how session 1 measures it.

## Why This Matters

Replay intent was weak in the v2.2 paper test and is not a stated design goal anywhere in `docs/gdd/nightcap/`. A goal that is not written down is not designed for.

## Technical Scope

- Add the goal to the owning GDD page and the decision ledger.
- Name the measure: the debrief question on playing again, and the approved pass bar of at least half answering yes.
- Separate "want to play again" (measurable in session 1) from "can play again" (needs a second case).

## Human Collaboration Contract

**Interaction profile:** Decision interview. The Master GDD is the design authority, so its wording needs the founder's approval.

## Acceptance Criteria

- [ ] The GDD states the goal and its measure.
- [ ] The founder's approval of the wording is recorded on the issue.

## Tests/Verification

- The `team-ai` check passes.

## Dependencies

- None
- Findings and evidence: `docs/product/2026-11-15-reset-audit.md`

## Must Not Do

- Do not change any other design decision in the GDD.
