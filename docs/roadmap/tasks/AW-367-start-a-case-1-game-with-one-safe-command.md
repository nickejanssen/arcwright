---
id: productroadmap.roadmap.tasks.aw-367-start-a-case-1-game-with-one-safe-command
namespace: product-roadmap
title: "AW-367: Start A Case 1 (1a) Game With One Command That Survives One Part Crashing"
owner: Nico Janssen
status: draft
review_by: "2027-02-26"
sensitivity: internal
source: authored
x-scope-evidence: none
tags: []
supersedes: []
---

# AW-367: Start A Case 1 (1a) Game With One Command That Survives One Part Crashing

**Milestone / Epic:** M7 / M7-C
**Size:** S
**Product:** Shared
**Owner:** One build session, after founder approval of its plan
**GitHub issue:** [#511](https://github.com/nickejanssen/arcwright/issues/511)  
**Target date:** 2026-11-29

## Plain-English Summary

The one-command start creates the old Couch Race game, and if any one part stops it shuts everything down. For now the host has to start case 1 by hand in three windows.

## Why This Matters

- Found during AW-308 (#362) by reading `scripts/rehearsal.py`: `DEFAULT_ARC_ID` is the Couch Race arc, and the supervisor stops every part when one exits.
- Its tunnel address changes on each start, and a phone's seat is kept per address, so a restart loses every seat.
- The manual steps in `docs/roadmap/operations/session-1-host-cheat-sheet.md` have not been run end to end.

## Technical Scope

1. Let the script create a chosen arc, including case 1 version 1a, and check the case file exists first.
2. Offer a home Wi-Fi mode that prints the phone address.
3. Restart a crashed part without stopping the others.
4. Give the host move-on, pause, resume and end commands from the PC.
5. Update the cheat sheet.

## Human Collaboration Contract

**Interaction profile:** Independent execution after plan approval. The founder approves the plan in their own words before any code.

## Acceptance Criteria

1. One command creates a `nightcap-agency-race-1a` game and prints the TV and phone addresses.
2. Stopping one part does not stop the others.
3. A missing case file is reported before any game is created.

## Tests/Verification

- Script tests under `scripts/tests/`.
- One real start on the founder's PC, reported separately from merged.

## Dependencies

- None.

## Must Not Do

- Do not open or quote files in `nightcap/cases/`.
- Do not add a dependency without approval.
