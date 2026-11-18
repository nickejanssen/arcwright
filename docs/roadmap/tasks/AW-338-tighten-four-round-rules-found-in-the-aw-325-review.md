---
id: productroadmap.roadmap.tasks.aw-338-tighten-four-round-rules-found-in-the-aw-325-review
namespace: product-roadmap
title: "AW-338: Tighten Four Round Rules Found In The AW-325 Review"
owner: Nico Janssen
status: active
review_by: "2027-02-17"
sensitivity: internal
source: authored
x-scope-evidence: D-124
tags: []
supersedes: []
---

# AW-338: Tighten Four Round Rules Found In The AW-325 Review

**Milestone / Epic:** M7 / M7-B
**Size:** S
**Product:** Shared (Arcwright and Nightcap)
**Owner:** One AI build session (Claude or Codex)
**Target date:** 2026-11-28

## Plain-English Summary

The review of the rounds work (AW-325) found four small gaps. None broke a test, but two could be felt at the party: a choice sent just after the timer ends still counts, and a screen can show a line the server then failed to save. Close all four.

## Why This Matters

Found by a Reviewer session on pull request #397 on 2026-11-17, rated nits (not blockers); read in the code by that session, not yet reproduced by a failing test. Filed under D-119.

1. `engine/session/choices.py`, around line 352: a choice is not compared with the phase deadline. One sent about a second late is accepted, and if the tick loop stops, choices stay open past the deadline.
2. `engine/session/choices.py`, around lines 346 to 348: repeating a `choice_id` with a different opportunity silently returns the first choice with success, and the replay reports today's remaining budget, not the original.
3. `engine/session/phases.py` (`_enter`) and `engine/session/choices.py` (`choose`): events are published before the database commit. A rollback leaves a published line with no saved state, and a rolled-back tick sends the scene lines again on the next tick.
4. `api/tick_loop.py`: it logs one error per run of failures, so later failures are silent. It also runs in one process; a second API instance would have its own event bus. Nothing is deployed, so this matters only before deploy.

## Technical Scope

- Refuse a choice whose phase deadline has passed, by the engine's clock.
- Refuse a repeated `choice_id` that names a different opportunity, and make a true replay return what it returned the first time.
- Publish events only after the commit succeeds.
- Log every tick failure, rate-limited, and write down in the code that the loop assumes one API process.

## Human Collaboration Contract

**Interaction profile:** Independent execution after plan approval. Touches `engine/session/` and `api/`, which crosses modules.

## Acceptance Criteria

- [x] A failing test for each of the four gaps, written first, then passing.
- [x] No existing test is weakened, skipped or deleted.
- [x] `verify` passes; it runs every Python test since AW-336. (Passed on head `c6b8989`; merged as `21afcf3`, pull request #419, 2026-11-18.)

## What Was Built

Plan approved by the founder on 2026-11-18 (issue #399). All four gaps were still true on `c7b4073`.

1. **Deadline:** `choose()` refuses with `phase_time_up` at or after the phase deadline, using the same comparison as the tick. A replay of an earlier choice is still answered after the deadline. The menu may still read "open" for up to a second after the deadline (approved default).
2. **Replay:** a `choice_id` reused for a different opportunity is refused with `choice_id_reused`. A true replay reports the budget as it was at the first answer, read from the saved `allowance` and `spent_after`, so it needs no schema change.
3. **Publish after commit:** a new `Outbox` in `phases.py` holds events. `tick_active_sessions` and the choice, ready and move-on routes commit first and flush after; a failed commit sends nothing. `_enter` and `choose` are unchanged. After the founder's review of #419, each session's change, commit and flush run under one in-process `delivery_lock`, so events reach the bus in the order changes were saved; an event that fails to send stays queued with everything behind it and is retried every tick pass (dropped and logged as an error after 10 failed attempts). If the database session's close fails after a commit, that session's events are still sent and the rest of the pass carries on. A replay of a row with no saved budget falls back to the current budget. `finish_mini_game_phase` has no production caller yet; its docstring says any caller must use `delivery_lock` and an `Outbox`. The mini-game submit and host-command routes also publish before commit; they are named in AW-341 (#418). The session and character routes have the same gap and moved to AW-341 (#418).
4. **Tick loop logging:** the first failure logs at once, then at most one line per 30 seconds with the count skipped, and one line on recovery. Per-session failure logging in `phases.py` stays unthrottled (approved default). The single-process assumption is written in `api/tick_loop.py` and the multi-process needs are noted in the AW-269 task. Session 1 runs one process: `scripts/rehearsal.py` starts `uvicorn` without `--workers`.

## Tests/Verification

- `python -m pytest engine/tests api/tests -q`
- `python -m ruff check engine api`

## Dependencies

- AW-325, merged 2026-11-17 (pull request #397).
- Start after AW-303 merges: both change `engine/session/phases.py`.

## Must Not Do

- No change to the phase order, the budget rules, or what the TV's round view shows (D-130).
- No game-specific word in `engine/`.
- Do not open any real case file.

## Kickoff Prompt

> Read `AGENTS.md`, `HANDOVER.md`, this task and the "What Was Built" section of the AW-325 task. Confirm AW-303 has merged; if not, stop. Task AW-338: write a failing test for each of the four gaps, then the smallest fix. Write a plan and stop for founder approval, because this crosses engine modules. Wait for CI `verify` before reporting done.
