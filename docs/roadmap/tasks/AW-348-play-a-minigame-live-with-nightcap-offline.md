---
id: productroadmap.roadmap.tasks.aw-348-play-a-minigame-live-with-nightcap-offline
namespace: product-roadmap
title: "AW-348: Play a minigame live with Nightcap offline"
owner: Nico Janssen
status: active
review_by: "2027-02-16"
sensitivity: internal
source: authored
x-scope-evidence: D-119
tags: []
supersedes: []
---

# AW-348: Play a minigame live with Nightcap offline

**Milestone / Epic:** M7 / M7-B  
**Size:** M  
**Product:** Shared  
**Owner:** One implementation session and founder playtest  
**Target date:** Unscheduled; founder to prioritize after dependency review.

## Plain-English Summary

Make one existing versioned package playable directly in a mobile or desktop browser. Two people can join, make choices, finish and replay while all Nightcap services are stopped. A local network link is sufficient for the first proof.

## Why This Matters

AW-322 verified that the existing preview replays fixed states. Its served evidence page cannot exercise authoritative scoring with real players. The founder wants fast live iteration and independent play on mobile or desktop.

## Technical Scope

- Review [AW-322](https://github.com/nickejanssen/arcwright/issues/382), specs 0078 and 0080, ADR 0018, the existing runtime/loader, browser kit and preview script. Check current work for AW-329 and AW-347 before defining new interfaces.
- Extend the smallest game-independent launch path. Accept an explicit package and fixture. Provide a direct URL, an independent join flow for multiplayer, reset/replay, and instructions for opening the LAN URL from a phone. A shared engine/library or game-independent service is acceptable. No Nightcap lobby, login, case, arc, TV or running application is required.
- Prefer Tell Me Something True as the existing example; confirm the version supports the chosen count before the run. Use the actual rules and each participant's authorized state. Retain the preview for visual checks.

## Human Collaboration Contract

**Interaction profile:** Independent execution after plan approval, then facilitated live operation. Current phase is scope capture. Next gate is founder review of the smallest implementation plan and any hard-rule changes. Bring a launch walkthrough; founder and a second player try it, then debrief. Scheduling remains open.

## Acceptance Criteria

- [ ] From a clean checkout, the documented command starts the standalone game. Supply package/version, fixture and exact prerequisites. With Nightcap stopped, a desktop and phone join via a reachable URL, submit distinct choices, see a rules-derived result, refresh/reconnect and replay cleanly.
- [ ] Automate two isolated browser seats and check private data in responses, duplicate or late input, timeout and stable results on replay. Run deterministic rule tests against fixed inputs.
- [ ] Record separately the automated run, devices/browsers actually observed, time to first playable link and time from a rule edit to the next round. Document standalone limitations and any optional remote-hosting follow-up.

## Tests/Verification

Record commands and pass/fail evidence in the issue. Report merge, deployment and observed play separately. An evidence page, simulation or screenshot alone cannot demonstrate the live path.

## Dependencies

AW-322 owns discovery and gap sizing. Reconcile the resulting slice with spec 0080 before build. Coordinate audience projections with AW-347 (#440) and renderer work with AW-329 (#432).

## Must Not Do

Keep Nightcap rewards and case evidence outside the standalone loop. Public hosting and a complete creator studio are outside this first proof.
