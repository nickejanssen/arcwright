---
id: productroadmap.roadmap.tasks.aw-305-load-the-first-case-pass-the-fairness-check-and-report-readiness-without-spoilers
namespace: product-roadmap
title: "AW-305: Load The First Case, Pass The Fairness Check, And Report Readiness Without Spoilers"
owner: Nico Janssen
status: active
review_by: "2027-02-15"
sensitivity: internal
source: authored
x-scope-evidence: D-112
tags: []
supersedes: []
---

# AW-305: Load The First Case, Pass The Fairness Check, And Report Readiness Without Spoilers

**Milestone / Epic:** M7 / M7-B  
**Size:** M  
**Product:** Nightcap  
**Owner:** The case-writing session, plus a separate reviewer session  
**Target date:** 2026-11-28

## Plain-English Summary

Get the first hand-written case into the engine's format, prove it is fair by rule, and tell the founder whether it is ready without revealing anything about the solution.

## Why This Matters

The first case is the most likely thing to move the session 1 date, and the founder cannot inspect it because he plays it unspoiled. A separate reviewer has to report on it.

## Technical Scope

- The case exists in the authored case format from the engine-spine spec.
- It passes the case-graph invariants named in spec 0092.
- A reviewer session that did not write the case reports pass or fail per invariant, using counts only.
- The case-writing session commits and pushes its work; on 15 November 2026 its spec edit and case folder were still unsaved on branch `claude/lido-case-and-spec-followups`.

## Human Collaboration Contract

**Interaction profile:** Creative collaboration. The founder approves premise, cast, tone and sample scenes without the solution (spec 0092, Q7).

## Acceptance Criteria

- [ ] The case loads and a headless session completes on it at two and at four players.
- [ ] The reviewer's report contains no culprit, method, truth or route.
- [ ] Founder approvals at premise, design and full-prose stages are recorded on the issue.

## Tests/Verification

- The fairness check passes in CI on the case file.

## Dependencies

- AW-302
- Findings and evidence: `docs/product/2026-11-15-reset-audit.md`

## Must Not Do

- Never state the culprit, method, essential truths or routes in chat, commit messages, pull request text, issue text or any summary the founder reads.
- Do not move solution material out of the file marked as spoilers.
