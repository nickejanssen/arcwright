---
id: productroadmap.roadmap.tasks.aw-310-triage-remote-branches-and-worktrees
namespace: product-roadmap
title: "AW-310: Triage Remote Branches And Worktrees"
owner: Nico Janssen
status: active
review_by: "2027-02-15"
sensitivity: internal
source: authored
x-scope-evidence: none
tags: []
supersedes: []
---

# AW-310: Triage Remote Branches And Worktrees

**Milestone / Epic:** M6 / M6-D  
**Size:** S  
**Product:** Shared (Arcwright and Nightcap)  
**Owner:** One AI build session (Claude or Codex); founder approves any deletion  
**Target date:** 2027-01-16

## Plain-English Summary

There were 27 remote branches and 14 worktrees on 15 November 2026. List each, say whether it holds unsaved or unmerged work, and propose keep, merge or delete.

## Why This Matters

Stale branches and worktrees are where unsaved work hides. On 15 November another session's spec edit and case folder had sat uncommitted for two days.

## Technical Scope

- Repeat the September branch triage.
- For each branch and worktree: last commit, whether it is merged, whether it has uncommitted files.
- A proposal table for the founder.

## Human Collaboration Contract

**Interaction profile:** Decision interview. Nothing is deleted without the founder's approval of the list.

## Acceptance Criteria

- [ ] Every branch and worktree has a row.
- [ ] No unmerged work is deleted.
- [ ] The founder's approval of the list is recorded before anything is removed.

## Tests/Verification

- `git branch -r` and `git worktree list` after the cleanup match the approved list.

## Dependencies

- None
- Findings and evidence: `docs/product/2026-11-15-reset-audit.md`

## Must Not Do

- Do not delete anything before approval.
- Do not touch another running session's worktree.
