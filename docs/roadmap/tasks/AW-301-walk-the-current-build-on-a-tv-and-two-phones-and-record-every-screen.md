---
id: productroadmap.roadmap.tasks.aw-301-walk-the-current-build-on-a-tv-and-two-phones-and-record-every-screen
namespace: product-roadmap
title: "AW-301: Walk The Current Build On A TV And Two Phones And Record Every Screen"
owner: Nico Janssen
status: active
review_by: "2027-02-15"
sensitivity: internal
source: authored
x-scope-evidence: none
tags: []
supersedes: []
---

# AW-301: Walk The Current Build On A TV And Two Phones And Record Every Screen

**Milestone / Epic:** M7 / M7-B  
**Size:** S  
**Product:** Nightcap  
**Owner:** One AI build session (Claude or Codex); founder starts Docker Desktop  
**Target date:** 2026-11-21

## Plain-English Summary

Start the playable build, step through it at TV size and phone size, and save what each screen shows. This was skipped during the reset audit because Docker was not running.

## Why This Matters

Nobody has looked at the running build since the 1 August rehearsal. The inventory and the screens spec both need to know what the screens do today, and the practice "inspect visual changes before showing the founder" needs a first worked example.

## Technical Scope

- Start the build with `make rehearsal`.
- Capture each screen at 1920 by 1080 (TV) and 375 by 812 (phone) for the host, one player and a second player, from join to the end of the session.
- Do the same for the `nightcap-web/` client if it can be started.
- Before the TV check, run the Postgres-only checks that SQLite skips (spec 0093, Risks): two simultaneous choices by one player cannot both spend budget, and two simultaneous ends of one mini-game give its reward once (AW-325, AW-328).
- For each screen record: what it shows, what a player can do, what is broken, and whether private information appears on the TV.

## Human Collaboration Contract

**Interaction profile:** Independent execution with one founder prerequisite: Docker Desktop must be running on the founder's PC.

## Acceptance Criteria

- [ ] A dated record with one row per screen and a saved capture for each.
- [ ] A plain list of what did not work.
- [ ] The record is linked from the AW-300 inventory.

## Tests/Verification

- Captures are viewable from the committed record.

## Dependencies

- None
- Findings and evidence: `docs/product/2026-11-15-reset-audit.md`

## Must Not Do

- Do not fix anything in this task.
- Do not restart the paused online playtest (D-111).
