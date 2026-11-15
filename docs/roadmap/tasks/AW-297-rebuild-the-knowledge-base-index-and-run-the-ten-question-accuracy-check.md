---
id: productroadmap.roadmap.tasks.aw-297-rebuild-the-knowledge-base-index-and-run-the-ten-question-accuracy-check
namespace: product-roadmap
title: "AW-297: Rebuild The Knowledge-Base Index And Run The Ten-Question Accuracy Check"
owner: Nico Janssen
status: active
review_by: "2027-02-15"
sensitivity: internal
source: authored
x-scope-evidence: none
tags: []
supersedes: []
---

# AW-297: Rebuild The Knowledge-Base Index And Run The Ten-Question Accuracy Check

**Milestone / Epic:** M7 / M7-A  
**Size:** S  
**Product:** Shared (Arcwright and Nightcap)  
**Owner:** One AI build session (Claude or Codex)  
**Target date:** 2026-11-21

## Plain-English Summary

Bring the knowledge-base search index up to date with main, then measure whether the specialist agents answer correctly, using ten questions whose answers are already verified.

## Why This Matters

The committed index dates from 21 September 2026, before the freeze and rebuild decisions were written. One ranked-search query about the tooling freeze returned three unrelated documents. Nobody has measured whether the agents give right answers with the right citations.

## Technical Scope

- Run the existing `team-ai reindex` and commit the refreshed index files under `team-ai/`.
- Run the ten questions in `docs/conventions/knowledge-base-upkeep.md` against the owning agents.
- Score each answer on four things: answered, correct, cited the right file, flagged a known conflict.
- Record the scores and the date in that same document.

## Human Collaboration Contract

**Interaction profile:** Independent execution. Running the existing reindex command is upkeep, not new tooling.

## Acceptance Criteria

- [ ] The index on main includes documents merged after 21 September 2026.
- [ ] Ranked search from a worktree session returns results, or states clearly that it is falling back to plain search.
- [ ] All ten questions are scored and the table is committed.
- [ ] Every wrong or uncited answer has a GitHub issue naming the document or agent to fix.

## Tests/Verification

- The `team-ai` check passes on the pull request.
- The score table in `docs/conventions/knowledge-base-upkeep.md`.

## Dependencies

- AW-296
- Findings and evidence: `docs/product/2026-11-15-reset-audit.md`

## Must Not Do

- Do not change how the index is built or ranked; that is new capability and frozen.
- Do not edit generated agent files by hand.
