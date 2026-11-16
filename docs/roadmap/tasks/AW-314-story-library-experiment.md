---
id: productroadmap.roadmap.tasks.aw-314-story-library-experiment
namespace: product-roadmap
title: "AW-314: Story Library Experiment"
owner: Nico Janssen
status: active
review_by: "2027-02-15"
sensitivity: internal
source: authored
x-scope-evidence: D-115
tags: []
supersedes: []
---

# AW-314: Story Library Experiment

**Milestone / Epic:** M6 / M6-D  
**Size:** M  
**Product:** Arcwright  
**Owner:** One AI build session (Claude or Codex); founder scores blind  
**Target date:** 2027-01-30

## Plain-English Summary

Test one question after session 1: does a small library of story structures improve generated case outlines?

## Why This Matters

The founder asked whether training Arcwright on stories he wrote and on open stories would help. A library of structures is the cheap, checkable version of that idea; changing a model itself is excluded for now by the architecture principles.

## Technical Scope

- Material: the founder's own writing, his short story notes and loose ideas, plus public-domain mysteries. Check each work's status first; "open source" is not the same as public domain.
- Break each story into its structure: characters, secrets, motives, clue routes, story units.
- Baseline: generate a case outline with no library. Test: generate one with five retrieved structures. Hold out three structures to check it is not copying.
- The founder scores blind, 1 to 5, on: fair, two routes to each truth, surprising but inevitable, specific voice, no clue that hands over the conclusion.
- Limit: two build days, two founder hours, under $10 of model usage.
- Later questions, only if the library wins this test (founder, 16 November 2026): does it also improve plot progression, character interactions and procedural generation while a story runs? Each is its own small test with its own stop rule, and none is in this task.

## Human Collaboration Contract

**Interaction profile:** Creative collaboration. The founder scores the outlines blind.

## Acceptance Criteria

- [ ] A scored comparison is recorded.
- [ ] Stop rule applied: if the library does not win by at least one point on average, shelve it and record that.

## Tests/Verification

- The recorded scores.

## Dependencies

- None
- Findings and evidence: `docs/product/2026-11-15-reset-audit.md`

## Must Not Do

- The library informs writing only; it never decides what happened in a session.
- Game content stays in the game's folder.
