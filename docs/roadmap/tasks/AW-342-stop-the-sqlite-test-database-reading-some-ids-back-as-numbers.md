---
id: productroadmap.roadmap.tasks.aw-342-stop-the-sqlite-test-database-reading-some-ids-back-as-numbers
namespace: product-roadmap
title: "AW-342: Stop The SQLite Test Database Reading Some IDs Back As Numbers"
owner: Nico Janssen
status: active
review_by: "2027-02-18"
sensitivity: internal
source: authored
x-scope-evidence: none
tags: []
supersedes: []
---

# AW-342: Stop The SQLite Test Database Reading Some IDs Back As Numbers

**Milestone / Epic:** M7 / M7-A  
**Size:** S  
**Product:** Shared (Arcwright and Nightcap)  
**Owner:** One AI build session (Claude or Codex)  
**Target date:** 2026-12-05

## Plain-English Summary

About one test run in a few hundred can fail for no reason in the code under test: the in-memory test database occasionally reads a random ID back as a number instead of an ID. Fix the test helper so IDs always come back as IDs. Production (Postgres) is not affected.

## Why This Matters

- Found on 2026-11-18 by the AW-328 build session: required check `verify` failed once on pull request #417 (head `e93c35b`) with `AttributeError: 'float' object has no attribute 'replace'` in test setup (`seat_session` -> `seat_authored_case` -> `assert_knowledge`). A rerun passed. It can hit any pull request, because every engine test that saves a row uses the same helper.
- Cause, verified in code by the orchestrator: `patch_metadata_for_sqlite` in `engine/db/testing.py` swaps `JSONB` for `JSON` but keeps the Postgres `UUID(as_uuid=True)` column type. SQLite gives a column declared `UUID` numeric affinity, so a stored 32-character hex ID that happens to read as a number in scientific notation (all digits except one `e`, for example `8160107621244484000000000000e031`) is stored and read back as a float.
- Reproduced by the orchestrator with Python's `sqlite3`: a `UUID` column given `'8160107621244484000000000000e031'` returns `8.160107621244484e+58`.
- A flaky required check wastes reruns and teaches people to ignore red CI (D-119 capture).

## Technical Scope

- In `engine/db/testing.py`, `patch_metadata_for_sqlite`: when a column's type is the Postgres `UUID`, replace it with `sqlalchemy.Uuid` (which SQLite stores as text), the same way `JSONB` is replaced with `JSON`. Keep `as_uuid` behaviour, so code still gets `uuid.UUID` objects.
- Add a regression test that saves and reloads a row whose ID is a number-looking hex value, for example `UUID("81601076-2124-4484-0000-000000000e31")`, and asserts it comes back as an equal `uuid.UUID`.
- Check whether any other test helper builds its own SQLite schema without `patch_metadata_for_sqlite`; list any found.

## Human Collaboration Contract

**Interaction profile:** Independent execution. Small break-fix in the test helper only; no production code, no schema or migration change. The founder's merge is the approval (D-118, small-fix lane). If the fix needs a change outside `engine/db/testing.py` and a new test file, stop and ask.

## Acceptance Criteria

- [ ] The regression test fails on main before the fix, for the right reason, and passes after.
- [ ] `patch_metadata_for_sqlite` stays idempotent.
- [ ] No production file changes; no existing test is weakened, skipped or deleted.
- [ ] `verify` passes.

## Tests/Verification

- `python -m pytest engine/tests api/tests -q`
- `python -m ruff check engine api`
- Merged and verified in CI only; nothing is deployed or seen in play.

## Dependencies

- None.

## Must Not Do

- Do not change the Postgres column types or add a migration.
- Do not hide the failure with retries or a fixed random seed.
- Do not open any real case file.

## Kickoff Prompt

> Read `AGENTS.md`, `HANDOVER.md` and this task. Write the failing regression test first, then the smallest fix in `engine/db/testing.py`. Wait for CI `verify` before reporting done.
