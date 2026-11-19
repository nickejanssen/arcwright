---
id: productroadmap.roadmap.tasks.aw-334-prove-a-full-games-screens-without-a-tv-and-run-it-in-ci
namespace: product-roadmap
title: "AW-334: Prove A Full Game's Screens Without A TV, And Run The Proof In CI"
owner: Nico Janssen
status: active
review_by: "2027-02-19"
sensitivity: internal
source: authored
x-scope-evidence: D-139
tags: []
supersedes: []
---

# AW-334: Prove A Full Game's Screens Without A TV, And Run The Proof In CI

**Milestone / Epic:** M7 / M7-B  
**Size:** M  
**Product:** Shared (Arcwright and Nightcap)  
**Owner:** One AI build session  
**Target date:** 2026-12-04

## Plain-English Summary

Prove a full game's screens without a TV: a Python script plays a whole game through the API and records what each screen reads, and the dashboard replays that recording through its real screens, checking the screen order and that nothing private reaches the TV or another player. Both halves run in CI.

## Why This Matters

- Spec 0095 Part O, approved 2026-11-19 (D-139). It is the last check before the founder TV run.

## Technical Scope

- Python half `api/tests/test_screens_feed.py::test_full_game_screen_feeds` at 2 and 4 players, with privacy markers and a committed recording.
- TypeScript half `dashboard/tests/full-game-screens.test.tsx`, test "full game screens at 2 and 4 players".
- The rewritten role-against-audience privacy matrix; add `npm test --prefix dashboard` to CI (`api/tests` already runs in `verify` since AW-336).
- Owns (spec 0095): `api/tests/test_screens_feed.py`, `dashboard/tests/full-game/`, `dashboard/tests/fixtures/`, `dashboard/tests/privacy-matrix.test.tsx`, `.github/workflows/ci.yml`.

## Human Collaboration Contract

**Interaction profile:** Independent execution after plan approval. Changes a CI workflow. The founder approves the plan in the build session himself, or by his own comment on this task's issue. A build session must not act on an approval relayed or posted for him by another session.

## Acceptance Criteria

- [ ] Both named proofs pass at 2 and 4 players, and an idle run reaches the survey on clocks alone.
- [ ] Any privacy marker in the wrong place fails the test.
- [ ] Both halves run in CI on every pull request.
- [ ] The Python half reads each player's menu after a real mini-game run with a winner and checks the private `rewards` list matches the saved grant (`grant_id`, amount), closing the open review point from AW-343 (#430). Founder agreed 2026-11-19.

## Tests/Verification

- The two named tests; CI run on the pull request.
- Merged, deployed and seen in play are separate; seen in play is the founder TV run.

## Dependencies

- AW-332 and AW-333 merged.
- Decisions: D-139.

## Must Not Do

- No game rule in TypeScript: no budget arithmetic, no right-or-wrong, no deciding what is on a menu or a theory list (spec 0095 Part L; AGENTS.md).
- No internal ID on any screen. Nothing private on the TV.
- Do not change `nightcap-web/`, `sdk/` or `nightcap/mini_games/` (spec 0095 Part K).
- Do not open any real case file.

## Kickoff Prompt

> Read `AGENTS.md`, `HANDOVER.md`, this task and `docs/specs/0095-screens-for-the-thin-version.md` (the parts named above and every "Answered" section). Confirm the dependencies are merged. Write a plan with the exact file list and the tests you will write first, post it on this task's issue, and stop for the founder's approval.
