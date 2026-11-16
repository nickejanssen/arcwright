---
id: productroadmap.roadmap.epics.m7-a-development-harness-and-tracker-readiness
namespace: product-roadmap
title: "M7-A: Development Harness And Tracker Readiness"
owner: Nico Janssen
status: active
review_by: "2027-02-15"
sensitivity: internal
source: authored
tags: []
supersedes: []
x-scope-evidence: none
---

# M7-A: Development Harness And Tracker Readiness

**Milestone:** M7  

## Plain-English Summary

Make the tools the work depends on trustworthy: the specialist agents answer, the knowledge base is current, merges are guarded, and GitHub describes the game being built.

## Why This Matters

The founder's requirement of 14 and 15 November 2026: the harness and the knowledge base must work so building is quick, safe and accurate, and every piece of work must be captured in one standard format instead of in chat.

## Tasks

- [AW-296: Fix The Knowledge-Base Agent Guard In Worktree Sessions](../tasks/AW-296-fix-the-knowledge-base-agent-guard-in-worktree-sessions.md)
- [AW-297: Rebuild The Knowledge-Base Index And Run The Ten-Question Accuracy Check](../tasks/AW-297-rebuild-the-knowledge-base-index-and-run-the-ten-question-accuracy-check.md)
- [AW-298: Require The CI And Knowledge-Base Checks Before Merging To Main](../tasks/AW-298-require-the-ci-and-knowledge-base-checks-before-merging-to-main.md)
- [AW-299: Reconcile The Tracker With The Rebuild](../tasks/AW-299-reconcile-the-tracker-with-the-rebuild.md)
- [AW-318: Rerun The Roadmap Questions In A Fresh Session And Close The Citation Misses](../tasks/AW-318-rerun-the-roadmap-questions-in-a-fresh-session-and-close-the-citation-misses.md)

## Acceptance Criteria

- All child tasks satisfy their acceptance criteria.
- Any open decision is recorded before dependent work starts.

## Dependencies

- Parent milestone: M7
- Findings and evidence: `docs/product/2026-11-15-reset-audit.md`

## Must Not Do

- Do not bypass the architecture principles in `AGENTS.md`.
- Do not turn Nightcap-specific requirements into platform assumptions.
