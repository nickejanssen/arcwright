---
id: productroadmap.roadmap.tasks.aw-308-session-1-preflight-reconnect-private-information-and-the-host-cheat-sheet
namespace: product-roadmap
title: "AW-308: Session 1 Preflight: Reconnect, Private Information And The Host Cheat Sheet"
owner: Nico Janssen
status: active
review_by: "2027-02-15"
sensitivity: internal
source: authored
x-scope-evidence: D-112
tags: []
supersedes: []
---

# AW-308: Session 1 Preflight: Reconnect, Private Information And The Host Cheat Sheet

**Milestone / Epic:** M7 / M7-C  
**Size:** S  
**Product:** Nightcap  
**Owner:** One AI build session (Claude or Codex), then the founder on real devices  
**Target date:** 2026-12-10

## Plain-English Summary

Before friends arrive, prove three things on real devices: a dropped phone can rejoin and keeps its private notes, the TV never shows private information, and there is one page telling the host what to do when something breaks.

## Why This Matters

These were listed as requirements for session 1 in the reset roadmap but were not verified in code during the audit. They fail in ways automated tests do not catch.

## Technical Scope

- Rejoin: close the browser on one phone mid-beat and rejoin with the same identity.
- Private information: step through every screen and look at the TV, not only the tests.
- A one-page host cheat sheet, modelled on `docs/roadmap/operations/rehearsal-1-failure-cheat-sheet.md`.
- The debrief survey is ready and the play record is being saved (AW-304).

## Human Collaboration Contract

**Interaction profile:** Facilitated live operation. The founder runs the checks on a real TV and two phones.

## Acceptance Criteria

- [ ] A dated record of the rejoin and private-information checks, with what was seen.
- [ ] The cheat sheet exists and the founder has read it.
- [ ] Any failure has an issue before session 1 is scheduled.

## Tests/Verification

- The founder's recorded run on a real TV and two phones.

## Dependencies

- AW-303
- Findings and evidence: `docs/product/2026-11-15-reset-audit.md`

## Must Not Do

- Do not schedule session 1 on a failed preflight.
