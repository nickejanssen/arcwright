---
id: productroadmap.roadmap.tasks.aw-336-run-the-api-tests-in-ci-and-fix-the-one-failing-on-main
namespace: product-roadmap
title: "AW-336: Run The API Tests In CI And Fix The One Failing On Main"
owner: Nico Janssen
status: active
review_by: "2027-02-16"
sensitivity: internal
source: authored
x-scope-evidence: none
tags: []
supersedes: []
---

# AW-336: Run The API Tests In CI And Fix The One Failing On Main

**Milestone / Epic:** M7 / M7-A  
**Size:** S  
**Product:** Shared (Arcwright and Nightcap)  
**Owner:** One AI build session (Claude or Codex)  
**Target date:** 2026-11-20

## Plain-English Summary

The automatic checks on a pull request never run the server's own tests. Make them run, and fix the one that fails today, so a broken server route cannot merge unseen.

## Why This Matters

- Verified on 2026-11-16 at commit `83795a5`: no workflow runs `api/tests`. `.github/workflows/ci.yml` runs `pytest engine/tests` only. The required check `verify` runs `make test`, which looks in a top-level `tests` folder and counts "no tests found" as a pass.
- Verified on 2026-11-16 on the founder's machine (Python 3.14.6): `python -m pytest api/tests -q` gives 114 passed and 1 failed. The failure is `api/tests/test_batch_harness.py::test_batch_session_completes`, at the line `assert all(record["passed"] is True for record in records)`. Unknown: whether it also fails on the Python version CI uses, and when it started failing.
- AW-325 adds server routes and tests for them under `api/tests`. Until this task is done, those tests protect nothing at merge time.
- Filed under D-119. Reported by the AW-325 build session and the screens spec session on 2026-11-16, then checked by the parent session.

## Technical Scope

- Add `api/tests` to a CI job that runs on every pull request. Prefer the job behind the required check `verify`, so the result blocks a merge.
- Find why `test_batch_session_completes` fails and fix the cause. If the test itself is wrong, say why in the pull request before changing it.
- Decide whether `make test` should keep treating "no tests found" as a pass. Recommended: point it at `engine/tests` and `api/tests` and drop the exception.

## Human Collaboration Contract

**Interaction profile:** Independent execution after plan approval. Changing which checks gate a merge is a founder decision; the session proposes and the founder approves.

- Making a new check required on `main` needs the founder's GitHub admin rights. That step belongs with AW-298.

## Acceptance Criteria

- [ ] A pull request that breaks a test under `api/tests` shows a failed check.
- [ ] `python -m pytest api/tests -q` passes on `main` in CI.
- [ ] The cause of the failing test is written in the pull request, with the commit that introduced it if it can be found.
- [ ] No test is deleted or skipped to make the run pass.

## Tests/Verification

- `python -m pytest api/tests -q`
- `python -m pytest engine/tests -q`
- `python -m ruff check engine api`

## Dependencies

- None. Related: AW-298 (which checks are required before merging), AW-325 (adds tests under `api/tests`).

## Must Not Do

- Do not skip, delete or mark as expected-to-fail any test to get a green run.
- Do not change branch protection; that is the founder's step in AW-298.
- Do not edit files AW-325 is changing (`engine/` and `api/` product code) while that task is open, beyond the single fix this task needs. If the fix lands in the same file, wait for AW-325 to merge.

## Kickoff Prompt

> Read `AGENTS.md`, `HANDOVER.md` and this task. Task AW-336: make CI run `api/tests` and fix `test_batch_session_completes`. First reproduce the failure and find its cause. Write a plan and stop for founder approval, because this changes what gates a merge. Check whether AW-325 has merged; if it has not, touch only CI files and the one fix.
