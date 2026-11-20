---
id: productroadmap.roadmap.tasks.aw-350-make-the-two-timing-sensitive-tests-reliable
namespace: product-roadmap
title: "AW-350: Make The Two Timing-Sensitive Tests Reliable On A Busy Machine"
owner: Nico Janssen
status: active
review_by: "2027-02-19"
sensitivity: internal
source: authored
x-scope-evidence: none
tags: []
supersedes: []
---

# AW-350: Make The Two Timing-Sensitive Tests Reliable On A Busy Machine

**Milestone / Epic:** M7 / M7-A  
**Size:** S  
**Product:** Shared (Arcwright and Nightcap)  
**Owner:** One AI build session (Claude or Codex)  
**Target date:** 2026-12-05

## Plain-English Summary

Two engine tests fail now and then because they measure how fast the code runs, not whether it is right. On a busy computer they run slower and fail, then pass when run again. Keep the speed checks useful without letting them fail at random.

## Why This Matters

- `engine/tests/test_spine_headless.py::test_twenty_sessions_tick_in_under_two_hundred_milliseconds` failed on untouched main during AW-303 (HANDOVER, 2026-11-18) and again in the AW-326 build session's full run on head `7813a59` (2026-11-19); both times it passed when rerun alone.
- `engine/tests/test_case_property_sweep.py::test_sweep_invariants_hold_for_exactly_1000_seeds[alibi_collapse]` failed once in the orchestrator's combined run of main plus pull requests #446 and #445 on 2026-11-19 (1485 passed, 1 skipped, 1 failed), while other test runs shared the machine. Rerun alone, the file passed in 35.8 seconds for three case types, about 12 seconds each against a 15-second limit (inferred from the total). Its content checks are seeded and deterministic, so the failure was the time limit (inferred; the failure text was not captured).
- Random failures waste reruns and teach people to ignore a red check, the same reason as AW-342 (D-119 capture).

## Technical Scope

- For both tests, keep the correctness assertions exactly as they are.
- Choose, in the plan, one of: move the speed check behind a marker that the normal run skips and CI runs alone; measure with a margin tied to a quick calibration on the same machine; or raise the limit with a recorded reason. Recommend one.
- Do not change engine code to make a test faster.

## Human Collaboration Contract

**Interaction profile:** Independent execution. Small test-only fix; the founder's merge is the approval (D-118, small-fix lane). If the fix needs a CI workflow change, say so in the plan.

## Acceptance Criteria

- [ ] Neither test can fail only because the machine is busy; each correctness assertion is unchanged. Both tests measure CPU time (`time.process_time()`), not the wall clock, because a busy machine makes code wait for a processor.
- [ ] The 20-session tick test also counts the database statements one tick runs and fails above a fixed budget (81 measured, budget 93), so extra queries fail whatever the machine is doing. Founder decision, 2026-11-20, relayed on pull request #455: "tell the AW-350 session to add the query count to #455, and file one task for the later monitoring and load test".
- [ ] A real slowdown (for example, ten times slower) still fails a check somewhere that runs in CI; one extra query per session fails the query budget.
- [ ] `verify` passes.

## Tests/Verification

- `python -m pytest engine/tests/test_spine_headless.py engine/tests/test_case_property_sweep.py -q`, then the full `python -m pytest tests engine/tests api/tests -q` while another test run shares the machine.
- Merged and verified in CI only.

## Dependencies

- None. Can run beside AW-342 (different files).

## Must Not Do

- Do not delete either test or weaken a correctness assertion.
- Do not hide failures with automatic retries.
- Do not open any real case file under `nightcap/cases/`.

## Kickoff Prompt

> Run `/implement AW-350`. Read `AGENTS.md`, `HANDOVER.md` and this task. Write the plan with a recommendation, post it on the issue, then make the smallest test-only change. Wait for CI `verify` before reporting done. Do not merge.
