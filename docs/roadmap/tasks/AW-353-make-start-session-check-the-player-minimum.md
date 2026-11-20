---
id: productroadmap.roadmap.tasks.aw-353-make-start-session-check-the-player-minimum
namespace: product-roadmap
title: "AW-353: Make Start Session Check The Player Minimum"
owner: Nico Janssen
status: active
review_by: "2027-02-19"
sensitivity: internal
source: authored
x-scope-evidence: none
tags: []
supersedes: []
---

# AW-353: Make Start Session Check The Player Minimum

**Milestone / Epic:** M7 / M7-B  
**Size:** S  
**Product:** Shared (Arcwright and Nightcap)  
**Owner:** One AI build session (Claude or Codex)  
**Target date:** 2026-12-01

## Plain-English Summary

The phone's Start button stays off until enough players have joined, but the engine itself will start a game with any number of players, even one. Make the engine refuse to start with fewer human seats than the game's minimum, with a named reason a screen can show, so the rule lives in one place and no screen bug can start a broken game.

## Why This Matters

- Found while planning AW-331 (verified: `SessionService.start_session` has no `min_players` check; the lobby read reports `min_players` from the arc, `api/routers/lobby.py`). Only the screen enforces it today.
- A game started with one player cannot run its rounds as designed (rounds wait for everyone; the mini-games need at least two).

## Technical Scope

- `engine/session/service.py` `start_session`: count human seats and refuse below the arc's `min_players` with a stable code (`not_enough_players`) as a `SessionStateError` subclass, like `SeatClosedError`; map it to 409 with `{code, message}` in `api/routers/sessions.py`.
- Decide in the plan how existing callers that start with fewer seats (tests, the rehearsal script, the operator host key) are handled: for example a clearly named way to start anyway for the operator key, or fixtures that seat enough players. Recommend one.
- Tests first: refused below the minimum with the code and no state change; works at the minimum; AI seats do not count as players; the route answers 409 with the code.

## Human Collaboration Contract

**Interaction profile:** Independent execution. Needs a decision on the operator and test-start path, so the plan must recommend one and the founder's merge is the approval (D-118, small-fix lane). If the plan touches sign-in or crosses engine modules, say so and ask for explicit approval.

## Acceptance Criteria

- [ ] `start_session` refuses with fewer human seats than the arc's `min_players`, with the code `not_enough_players`, and changes nothing.
- [ ] It starts at the minimum and above.
- [ ] The route returns 409 with `{code, message}`.
- [ ] Every existing test, script and the AW-301 walkthrough still pass or are updated with a stated reason.
- [ ] No game word is added to `engine/`.

## Tests/Verification

- `python -m pytest tests engine/tests api/tests -q`, ruff check and format.
- Merged and verified in CI.

## Dependencies

- AW-331 merged (it changes `start_session`'s lock; this task edits the same function).

## Must Not Do

- Do not open any real case file under `nightcap/cases/`.
- Do not weaken the lock AW-331 added.

## Kickoff Prompt

> Run `/implement AW-353`. Read `AGENTS.md`, `HANDOVER.md` and this task. Write the plan with a recommendation for the operator and test-start path, post it on the issue, then build tests first. Wait for CI `verify`. Do not merge.
