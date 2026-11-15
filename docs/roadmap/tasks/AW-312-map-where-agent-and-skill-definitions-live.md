---
id: productroadmap.roadmap.tasks.aw-312-map-where-agent-and-skill-definitions-live
namespace: product-roadmap
title: "AW-312: Map Where Agent And Skill Definitions Live"
owner: Nico Janssen
status: active
review_by: "2027-02-15"
sensitivity: internal
source: authored
x-scope-evidence: none
tags: []
supersedes: []
---

# AW-312: Map Where Agent And Skill Definitions Live

**Milestone / Epic:** M6 / M6-D  
**Size:** S  
**Product:** Shared (Arcwright and Nightcap)  
**Owner:** One AI build session (Claude or Codex)  
**Target date:** 2027-01-16

## Plain-English Summary

Agent and skill definitions live in at least seven places. Write down which is the source and which are generated or mirrored, so nobody edits the wrong one.

## Why This Matters

Verified on 15 November 2026: `.agents/`, `.claude/agents/`, `.codex/`, `.github/agents/`, `docs/agents/`, `docs/skills/` and `team-ai/agents/` all exist. `AGENTS.md` explains some of them and not others.

## Technical Scope

- One table: location, what reads it, source or generated, how to regenerate.
- Put it in `docs/agents/README.md`.

## Human Collaboration Contract

**Interaction profile:** Independent execution. Documentation only; allowed under the tooling freeze because it adds no capability.

## Acceptance Criteria

- [ ] Every location has a row.
- [ ] Each generated location names its command.

## Tests/Verification

- A reviewer regenerates one generated location from the table's command and gets no diff.

## Dependencies

- None
- Findings and evidence: `docs/product/2026-11-15-reset-audit.md`

## Must Not Do

- Do not move, merge or delete any definition in this task.
