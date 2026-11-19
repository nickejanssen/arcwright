---
id: productroadmap.roadmap.tasks.aw-330-build-the-screen-shell-sign-in-storage-room-and-join-screens-and-the-start-menu
namespace: product-roadmap
title: "AW-330: Build The Screen Shell, Sign-In Storage, Room And Join Screens, And The Phone Start Menu"
owner: Nico Janssen
status: active
review_by: "2027-02-19"
sensitivity: internal
source: authored
x-scope-evidence: D-139
tags: []
supersedes: []
---

# AW-330: Build The Screen Shell, Sign-In Storage, Room And Join Screens, And The Phone Start Menu

**Milestone / Epic:** M7 / M7-B  
**Size:** M  
**Product:** Nightcap  
**Owner:** One AI build session  
**Target date:** 2026-11-26

## Plain-English Summary

Build the dashboard's pages for the TV, joining and the phone; the table that picks a screen from the phase the engine reports; reading state from routes on load and after a reconnect; a phone that remembers its seat; the room, join, seated and paused screens; and the phone Start menu with the host's controls.

## Why This Matters

- Spec 0095 Parts K, L and N and decisions 3 and 5, approved 2026-11-19 (D-139).
- D-133: every phone has a Start menu (Pause, Resume, Settings); the host's adds Start game, Move on, mini-game Resolve and Cancel, End game and handing the role on. The TV has no controls.

## Technical Scope

- Pages for TV, join and phone; the phase-to-screen table with empty slots for the round and endgame screens.
- Sign-in kept per session in long-lived storage, so reopening the join link returns a player to their seat (decision 3; a sign-in change, hard rule).
- Screens 1, 2, 3 and 23; the Start menu (D-133) with the controls whose routes exist today. What Settings holds is proposed in the plan (text size, reduced motion, room code and rejoin link, leave game) and shown in the screen-copy sample.
- Screen copy: one sample of about twenty lines shown to the founder before code (spec 0095 Part L).
- Owns (spec 0095): `dashboard/src/App.tsx`, `dashboard/src/main.tsx`, `dashboard/src/index.css`, `dashboard/src/api/`, `dashboard/src/shell/` (new), `dashboard/src/screens/DisplayScreen.tsx`, `JoinScreen.tsx`, `WaitingScreen.tsx`, and empty `screens/round/index.tsx` and `screens/endgame/index.tsx`.

## Human Collaboration Contract

**Interaction profile:** Creative collaboration for the screen copy sample, then independent execution after plan approval. Touches sign-in storage (hard rule). The founder approves the plan in the build session himself, or by his own comment on this task's issue. A build session must not act on an approval relayed or posted for him by another session.

## Acceptance Criteria

- [ ] A phone whose tab closed and reopened on the join link resumes its own seat (test with a fake storage).
- [ ] Each Start menu control calls its route; Move on in Last Call and End game confirm first; a player's menu offers only Pause, Resume and Settings.
- [ ] After a simulated API restart the screens reread their routes.
- [ ] The founder approved the screen-copy sample before code.

## Tests/Verification

- `npm test --prefix dashboard`, typecheck and build.
- Merged, deployed and seen in play are separate; seen in play is the founder TV run.

## Dependencies

- AW-329 merged; the phase-aware parts need AW-325 (merged). Player pause and the host role on a seat need AW-331's engine side.
- Decisions: D-133, D-139.

## Must Not Do

- No game rule in TypeScript: no budget arithmetic, no right-or-wrong, no deciding what is on a menu or a theory list (spec 0095 Part L; AGENTS.md).
- No internal ID on any screen. Nothing private on the TV.
- Do not change `nightcap-web/`, `sdk/` or `nightcap/mini_games/` (spec 0095 Part K).
- Do not open any real case file.

## Kickoff Prompt

> Read `AGENTS.md`, `HANDOVER.md`, this task and `docs/specs/0095-screens-for-the-thin-version.md` (the parts named above and every "Answered" section). Confirm the dependencies are merged. Write a plan with the exact file list and the tests you will write first, post it on this task's issue, and stop for the founder's approval.
