---
id: productroadmap.roadmap.tasks.aw-339-remove-duplicate-python-ci-checks
namespace: product-roadmap
title: "AW-339: Remove Duplicate Python CI Checks"
owner: Nico Janssen
status: active
review_by: "2027-02-17"
sensitivity: internal
source: authored
x-scope-evidence: none
tags: []
supersedes: []
---

# AW-339: Remove Duplicate Python CI Checks

**Milestone / Epic:** M7 / M7-A
**Size:** S
**Product:** Shared
**Owner:** One AI build session
**Target date:** 2026-11-24

## Plain-English Summary

Run Python lint and tests once on each pull request while keeping both required GitHub checks. Reduce repeated installs and preserve existing coverage.

## Why This Matters

PR #401 identified repeated Python lint and engine tests across CI and verify. AW-298 made both checks required.

## Technical Scope

Remove duplicated lint and engine tests from ci.yml. Keep formatting, frontend checks, secret scanning, job names and triggers. Install pinned Ruff for formatting. Keep verify's lint, type checking, and tests of tests, engine/tests and api/tests.

## Human Collaboration Contract

**Interaction profile:** Independent execution. The founder approved execution of the merged infrastructure plan in PR #401.

## Acceptance Criteria

- [ ] Python lint and all three Python test directories run in verify.
- [ ] CI keeps Python formatting, frontend checks, builds and secret scanning.
- [ ] The three existing required checks pass on this PR.
- [ ] Compare CI duration with the PR #401 baseline.

## Tests/Verification

Inspect workflow commands and run Ruff format check. Review GitHub Actions results for CI, verify and team-ai.

## Dependencies

- AW-298, PR #401.

## Must Not Do

- Do not remove tests or alter branch protection.

## Kickoff Prompt

Read this task and the implementation plan in PR #401. Preserve check names and verify all three jobs.
