---
id: productroadmap.roadmap.tasks.aw-362-give-each-player-private-starting-information-in-a-written-case
namespace: product-roadmap
title: "AW-362: Give Each Player Private Starting Information In A Written Case"
owner: Nico Janssen
status: draft
review_by: "2027-02-25"
sensitivity: internal
source: authored
x-scope-evidence: none
tags: []
supersedes: []
---

# AW-362: Give Each Player Private Starting Information In A Written Case

**Milestone / Epic:** M7 / M7-B  
**Size:** M  
**Product:** Arcwright engine (story-writing technology)  
**Owner:** One build session, after a spec change and the founder's plan approval  
**GitHub issue:** [#497](https://github.com/nickejanssen/arcwright/issues/497)  
**Target date:** after playtesting starts (D-156)

## Plain-English Summary

The written-case format (spec 0093 Part A, format version 1) gives every player the same starting information; players differ only by what they choose to investigate. Writers want each seat to start with its own private information. This task adds that to the format, the loader, the fairness check and what each player holds.

## Why This Matters

D-156: get to playtesting, then improve the story technologies (creating, calibrating and running a story), then iterate on the story. Case 1 folds its private starting information into investigations for 1 December, because format version 1 cannot express it. This restores it as engine capability.

## Technical Scope

- Format version 2: optional per-seat starting information by seat slot, for each supported player count.
- The loader and checks A1 to A6 handle it; A3's search runs per seat.
- At session start each player's character holds its own seat's starting information, through the one held-concepts function (spec 0093 Part B).
- Generic names only; nothing in `engine/` names a game.

## Acceptance Criteria

- [ ] A fixture case with per-seat starting information loads, passes A0 to A6, and each seat holds only its own information at session start.
- [ ] A fixture broken per rule is refused with that rule's name.
- [ ] Format version 1 cases load and check unchanged.

## Dependencies

- AW-324 (merged): the loader and fairness check.
- A spec 0093 change approved by the founder (cross-module hard rule).

## Must Not Do

- Do not use a real case's content in tests or PRs; fixtures are made up.
