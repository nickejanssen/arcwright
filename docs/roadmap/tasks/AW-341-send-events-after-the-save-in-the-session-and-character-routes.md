---
id: productroadmap.roadmap.tasks.aw-341-send-events-after-the-save-in-the-session-and-character-routes
namespace: product-roadmap
title: "AW-341: Send Events After The Save In The Session And Character Routes"
owner: Nico Janssen
status: active
review_by: "2027-02-17"
sensitivity: internal
source: authored
x-scope-evidence: none
tags: []
supersedes: []
---

# AW-341: Send Events After The Save In The Session And Character Routes

**Milestone / Epic:** M7 / M7-B  
**Size:** S  
**Product:** Shared (Arcwright and Nightcap)  
**Owner:** One AI build session (Claude or Codex)  
**Target date:** 2026-12-31

## Plain-English Summary

AW-338 made the round routes tell the screens about a change only after the change is saved. Other routes still do it the old way: they publish an event while their save is still open, so a failed save can leave a screen showing something the server never kept. Move them to the same save-then-tell order. Not needed for the 12 December session.

## Why This Matters

Found while planning AW-338 (D-127: a gap outside that task's finding goes to its own task, D-119). The review of pull request #397 covered the round routes only. `api/routers/sessions.py` (around line 192, the bridge event) and `api/routers/characters.py` (around line 174, the character response event) publish through the session's event bus before the request's commit. The mini-game routes in `api/routers/mini_games.py` (a player's submit, around line 523, and the host's command, around line 573) publish through `MiniGameRuntime._publish` (`engine/mini_games/runtime.py`, around line 961, `self._bus.publish`) before the request commits. They were not in the AW-325 review or the AW-338 plan and are not a regression; the review of pull request #419 named them. This is read in the code, not reproduced by a failing test.

## Technical Scope

- Use the `Outbox` and `delivery_lock` that AW-338 added in `engine/session/phases.py`, or the same lock-commit-flush order, in the two handlers above.
- Write a failing test for each route first: make the commit fail, expect no event on the bus; on success, expect the event after the commit.
- Mini-game submit and host-command routes: they publish inside the runtime, so the fix is to give the runtime an `Outbox` as its bus for those requests (or the same commit-then-flush order), under `delivery_lock`. This touches `engine/mini_games/`; AW-328 changes that folder, so build after AW-328 merges. If it needs more than passing an `Outbox`, stop and ask.
- `finish_mini_game_phase` in `engine/session/phases.py` has no production caller yet. Any caller added (by AW-326, AW-327 or this task) must use `delivery_lock` and an `Outbox`; check that when it appears.
- Check the other `bus.publish` callers in `api/` for the same order and list any found; fix them only if they are the same shape.

## Human Collaboration Contract

**Interaction profile:** Independent execution after plan approval. The session and character routes are inside `api/`; the mini-game routes also reach `engine/mini_games/`, which crosses modules, so write a plan and stop for founder approval first. If it needs more than passing an `Outbox`, stop and ask.

## Acceptance Criteria

- [ ] A failing test for each route (session, character, mini-game submit, mini-game host command), written first, then passing.
- [ ] No existing test is weakened, skipped or deleted.
- [ ] `verify` passes.

## Tests/Verification

- `python -m pytest engine/tests api/tests -q`
- `python -m ruff check engine api`

## Dependencies

- AW-338 (adds `Outbox`, `delivery_lock` and the commit-then-flush pattern).
- AW-328 merged first, for the mini-game part (it changes `engine/mini_games/`).

## Must Not Do

- No change to what an event contains, who receives it, or the route's response.
- No game-specific word in `engine/`.
- Do not open any real case file.

## Kickoff Prompt

> Read `AGENTS.md`, `HANDOVER.md`, this task and the AW-338 task. Confirm AW-338 has merged; if not, stop. Task AW-341: write a failing test for each route (session, character, mini-game submit, mini-game host command), then the smallest fix using the `Outbox` and `delivery_lock`. Wait for CI `verify` before reporting done.
