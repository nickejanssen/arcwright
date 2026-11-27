---
id: productroadmap.roadmap.tasks.aw-368-close-two-ways-a-live-game-can-get-stuck
namespace: product-roadmap
title: "AW-368: Close Two Ways A Live Game Can Get Stuck: Half-Made Seats And Resume"
owner: Nico Janssen
status: draft
review_by: "2027-02-26"
sensitivity: internal
source: authored
x-scope-evidence: none
tags: []
supersedes: []
---

# AW-368: Close Two Ways A Live Game Can Get Stuck: Half-Made Seats And Resume

**Milestone / Epic:** M7 / M7-C
**Size:** S
**Product:** Arcwright
**Owner:** One build session, after founder approval of its plan
**GitHub issue:** [#512](https://github.com/nickejanssen/arcwright/issues/512)  
**Target date:** 2026-12-05

## Plain-English Summary

First, if a phone joins but its sign-in step then fails, the seat stays in the game with nobody in it, and trying again adds another. Second, resuming a paused game needs a call to the writing model; if that call fails the game stays paused.

## Why This Matters

- Found during AW-308 (#362) by reading the code. **Neither has been seen happen.**
- `dashboard/src/screens/JoinScreen.tsx` joins first and exchanges the sign-in second; a retry joins again. If the empty seat is first, it holds the host role (`engine/session/host_seat.py`).
- `lobby_join` in `engine/session/service.py` has no player maximum.
- `resume_session` in `api/routers/sessions.py` awaits `generate_narrator_bridge` inside the same request, so a failure rolls the resume back.

## Technical Scope

1. Retrying a join after a failed sign-in reuses the seat, or the seat is removed.
2. Refuse a join above the arc's maximum players.
3. Resume succeeds with a written fallback line when the model call fails.

## Human Collaboration Contract

**Interaction profile:** Decision interview, then independent execution. The founder approves the plan in their own words before any code.

## Acceptance Criteria

1. Tests show one seat after a failed sign-in and a retry.
2. A test shows a fifth join refused on a four-player arc.
3. A test shows resume succeeding when the model call raises.

## Tests/Verification

- `pytest engine/tests/ api/tests/` and `npm test --prefix dashboard`.

## Dependencies

- Founder plan approval: it touches sign-in handling and more than one engine module (hard rules).

## Must Not Do

- Do not open or quote files in `nightcap/cases/`.
- Do not add a dependency without approval.
