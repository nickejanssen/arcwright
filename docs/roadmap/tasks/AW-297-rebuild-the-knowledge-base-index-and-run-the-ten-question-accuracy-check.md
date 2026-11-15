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

The local index in the main checkout dated from 21 September 2026, before the freeze and rebuild decisions were written. One ranked-search query about the tooling freeze returned three unrelated documents. The live check measures whether agents give right answers with the right citations.

## Technical Scope

- Run `python scripts/team_ai_cli.py reindex --root team-ai` from the checkout being indexed. Keep each generated database gitignored, as required by spec 0089. Give unindexed worktrees an explicit Grep/Glob and Read fallback within the specialist's namespace.
- Use the existing CLI with 64 candidates before namespace filtering and at most eight returned results. Keep its index, scoring and namespace restrictions.
- Run the ten questions in `docs/conventions/knowledge-base-upkeep.md` against the owning agents.
- Score each answer on four things: answered, correct, cited the right file, flagged a known conflict.
- Record the scores and the date in that same document.

## Human Collaboration Contract

**Interaction profile:** Independent execution. On 2026-11-15 the founder explicitly approved local ignored indexes, worktree fallback, and committed live scores in PR #352. The founder subsequently approved measured retrieval, routing and handoff repairs using the existing architecture, including the candidate-window adjustment. Approval and measured evidence are recorded in PR #352 and GitHub issue #349.

## Acceptance Criteria

- [ ] The local index in the main checkout includes documents merged after 21 September 2026.
- [ ] Ranked search from a worktree returns results after reindexing and clearly gives a plain-search fallback when the index is missing.
- [ ] All ten questions are scored and the table is committed.
- [ ] Every wrong or uncited answer has a GitHub issue naming the document or agent to fix.

## Tests/Verification

- The `team-ai` check passes on the pull request.
- The score table in `docs/conventions/knowledge-base-upkeep.md`.

## Dependencies

- AW-296
- Findings and evidence: `docs/product/2026-11-15-reset-audit.md`

## Must Not Do

- Do not replace index construction or ranking. The approved candidate-window adjustment above is the only retrieval expansion.
- Do not edit generated agent files by hand.
