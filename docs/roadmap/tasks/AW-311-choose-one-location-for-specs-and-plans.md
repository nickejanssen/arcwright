---
id: productroadmap.roadmap.tasks.aw-311-choose-one-location-for-specs-and-plans
namespace: product-roadmap
title: "AW-311: Choose One Location For Specs And Plans"
owner: Nico Janssen
status: active
review_by: "2027-02-15"
sensitivity: internal
source: authored
x-scope-evidence: none
tags: []
supersedes: []
---

# AW-311: Choose One Location For Specs And Plans

**Milestone / Epic:** M6 / M6-D  
**Size:** S  
**Product:** Shared (Arcwright and Nightcap)  
**Owner:** One planner session; founder decides  
**Target date:** 2027-01-16

## Plain-English Summary

Specs and plans live in two places: `docs/specs/` and `docs/superpowers/` (`specs/` and `plans/`). Pick one for new work and say so in the documentation rules.

## Why This Matters

Two locations mean a session can miss an approved spec or plan, or write a second one.

## Technical Scope

- Count what is in each location and which are still live.
- Recommend one location going forward.
- Update `docs/README.md` and the working model. Move nothing historical.

## Human Collaboration Contract

**Interaction profile:** Decision interview.

## Acceptance Criteria

- [ ] One sentence in `docs/README.md` names where new specs and plans go.
- [ ] No live spec exists in both places.

## Tests/Verification

- The `team-ai` check passes.

## Dependencies

- None
- Findings and evidence: `docs/product/2026-11-15-reset-audit.md`

## Must Not Do

- Do not move or rename historical files; links depend on them.
