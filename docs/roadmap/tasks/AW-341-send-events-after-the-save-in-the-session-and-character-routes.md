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

AW-338 made the round routes tell the screens about a change only after the change is saved. Two other routes still do it the old way: they publish an event while their save is still open, so a failed save can leave a screen showing something the server never kept. Move them to the same save-then-tell order. Not needed for the 12 December session.

## Why This Matters

Found while planning AW-338 (D-127: a gap outside that task's finding goes to its own task, D-119). The review of pull request #397 covered the round routes only. `api/routers/sessions.py` (around line 192, the bridge event) and `api/routers/characters.py` (around line 174, the character response event) publish through the session's event bus before the request's commit. This is read in the code, not reproduced by a failing test.

## Technical Scope

- Use the `Outbox` that AW-338 added in `engine/session/phases.py`, or the same commit-then-flush order, in the two handlers above.
- Write a failing test for each route first: make the commit fail, expect no event on the bus; on success, expect the event after the commit.
- Check the other `bus.publish` callers in `api/` for the same order and list any found; fix them only if they are the same shape.

## Human Collaboration Contract

**Interaction profile:** Independent execution. Small change inside `api/`; if it needs a change in `engine/` beyond reusing `Outbox`, stop and ask.

## Acceptance Criteria

- [ ] A failing test for each route, written first, then passing.
- [ ] No existing test is weakened, skipped or deleted.
- [ ] `verify` passes.

## Tests/Verification

- `python -m pytest engine/tests api/tests -q`
- `python -m ruff check engine api`

## Dependencies

- AW-338 (adds the `Outbox` and the commit-then-flush pattern).

## Must Not Do

- No change to what an event contains, who receives it, or the route's response.
- No game-specific word in `engine/`.
- Do not open any real case file.

## Kickoff Prompt

> Read `AGENTS.md`, `HANDOVER.md`, this task and the AW-338 task. Confirm AW-338 has merged; if not, stop. Task AW-341: write a failing test for each route, then the smallest fix using the `Outbox`. Wait for CI `verify` before reporting done.
