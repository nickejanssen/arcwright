---
id: productroadmap.roadmap.tasks.aw-331-add-the-room-view-seat-rule-survey-answers-signed-in-mini-game-view-and-start-menu-sign-in
namespace: product-roadmap
title: "AW-331: Add The Room View, Seat Rule, Survey Answers, Signed-In Mini-Game View And Start Menu Sign-In"
owner: Nico Janssen
status: active
review_by: "2027-02-19"
sensitivity: internal
source: authored
x-scope-evidence: D-139
tags: []
supersedes: []
---

# AW-331: Add The Room View, Seat Rule, Survey Answers, Signed-In Mini-Game View And Start Menu Sign-In

**Milestone / Epic:** M7 / M7-B  
**Size:** M  
**Product:** Shared (Arcwright and Nightcap)  
**Owner:** One AI build session  
**Target date:** 2026-11-28

## Plain-English Summary

Add the few engine reads and rules the screens need (spec 0095 Part M): a room view the TV can read without signing in, no new seat after the game starts, per-player survey answers, a private mini-game view that needs the player's sign-in, and the sign-in changes the phone Start menu needs.

## Why This Matters

- Spec 0095 Part M rows M1 to M6, approved 2026-11-19 (D-139). Row M6 comes from D-133.
- D-130 already lets the TV read the round without signing in; M1 extends that room-safe read.

## Technical Scope

- M1 room view, M2 no new seat after start, M3 survey answers as events, M4 the display mini-game address returns a player's view only to that player's sign-in, M5 notebook fields if missing.
- M6 (D-133): pause and resume accept a player's sign-in; the host role belongs to a player's seat (the first to join); a route lets the host hand it to another seated player; the host controls accept that seat's sign-in.
- Owns (spec 0095): `engine/session/room_view.py` (new), `engine/session/survey.py` (new), `engine/session/service.py` (join rule), `api/routers/room.py` (new), `api/schemas/room.py` (new), `api/main.py` (one line), `api/routers/mini_games.py` (display address), `api/routers/lobby.py`, tests; plus, for M6, the sign-in and route files the plan lists (expected: `api/auth/`, `api/routers/sessions.py`, `api/routers/rounds.py`).
- Saving and sending follows AW-338: hold `delivery_lock`, pass an `Outbox`, commit, then flush.

## Human Collaboration Contract

**Interaction profile:** Independent execution after plan approval. Crosses engine modules and changes sign-in (two AGENTS.md hard rules): the founder approves the plan explicitly, including the M6 sign-in design. The founder approves the plan in the build session himself, or by his own comment on this task's issue. A build session must not act on an approval relayed or posted for him by another session.

## Acceptance Criteria

- [ ] The room view, read with no sign-in, returns everything in M1 and no private marker at any phase of a full fixture run.
- [ ] `lobby-join` after start is refused with a named reason.
- [ ] Survey answers save per player, a repeat replaces, and no other reader sees them.
- [ ] The display mini-game address with a character ID and no sign-in returns the shared view.
- [ ] A player's sign-in can pause and resume; only the host seat can use host controls; the host can hand the role on; tests for each.
- [ ] Route handlers contain no rule; no game word added to `engine/`.

## Tests/Verification

- `python -m pytest tests engine/tests api/tests -q`, ruff check and format.
- Merged, deployed and seen in play are separate; seen in play is the founder TV run.

## Dependencies

- AW-327 merged (the engine tasks before it change `engine/session/` and `api/main.py`).
- Decisions: D-130, D-133, D-139.

## Must Not Do

- No game rule in TypeScript: no budget arithmetic, no right-or-wrong, no deciding what is on a menu or a theory list (spec 0095 Part L; AGENTS.md).
- No internal ID on any screen. Nothing private on the TV.
- Do not change `nightcap-web/`, `sdk/` or `nightcap/mini_games/` (spec 0095 Part K).
- Do not open any real case file.

## Kickoff Prompt

> Read `AGENTS.md`, `HANDOVER.md`, this task and `docs/specs/0095-screens-for-the-thin-version.md` (the parts named above and every "Answered" section). Confirm the dependencies are merged. Write a plan with the exact file list and the tests you will write first, post it on this task's issue, and stop for the founder's approval.
