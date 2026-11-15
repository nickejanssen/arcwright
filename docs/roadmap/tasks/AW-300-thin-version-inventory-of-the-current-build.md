---
id: productroadmap.roadmap.tasks.aw-300-thin-version-inventory-of-the-current-build
namespace: product-roadmap
title: "AW-300: Thin-Version Inventory Of The Current Build"
owner: Nico Janssen
status: active
review_by: "2027-02-15"
sensitivity: internal
source: authored
x-scope-evidence: D-112
tags: []
supersedes: []
---

# AW-300: Thin-Version Inventory Of The Current Build

**Milestone / Epic:** M7 / M7-B  
**Size:** M  
**Product:** Shared (Arcwright and Nightcap)  
**Owner:** One AI build session (Claude or Codex)  
**Target date:** 2026-11-21

## Plain-English Summary

An inventory is a line-by-line list of what exists today, each line marked keep, change or retire. It is work package 0 of spec 0092, limited to what the thin first version needs, and it stops anyone rebuilding something that already exists.

## Why This Matters

Spec 0092's own gap table is a first pass built on keyword scans and is already known to be wrong in two places (see the corrections section of the spec). Every later task depends on this list being right.

## Technical Scope

- Every arc field, engine function, API route and screen file the thin version touches, marked keep, change or retire, with a file path. Example row: `engine/scoring` - points scoring - retire; the thin version has no points.
- Choose one set of screen code. `scripts/rehearsal.py` launches `dashboard/`; the mini-game kit lives in `nightcap-web/`. Give reasons.
- Confirm or correct each row of spec 0092's reconciliation table against code, not keywords.
- State what the mini-game wiring needs (start, clock, return to the story) as input to AW-303.
- List every game-specific word found in `engine/`, as input to AW-274.
- Use the walkthrough from AW-301 as evidence for the screen rows.

## Human Collaboration Contract

**Interaction profile:** Independent execution, then a founder review of the inventory before any spec is written from it. Blocked until the founder approves spec 0092 for the thin version (#303).

## Acceptance Criteria

- [ ] One document with a file path for every claim.
- [ ] Each row of the spec 0092 reconciliation table is marked confirmed or corrected.
- [ ] One screen codebase is named, with the disposition of the other.
- [ ] The founder has reviewed it and the review is recorded on the issue.

## Tests/Verification

- Reviewer session checks ten sampled rows against the code.

## Dependencies

- None
- Findings and evidence: `docs/product/2026-11-15-reset-audit.md`

## Must Not Do

- No code changes. Do not delete or unregister any old file.
- Do not open or read case solution files; the founder plays the first case unspoiled.

## Kickoff Prompt

> Read `AGENTS.md`, `HANDOVER.md` and `docs/specs/0092-nightcap-gdd-rebuild.md`, including its corrections section. Confirm the founder's approval of spec 0092 for the thin version is recorded on issue #303; if not, stop. Task AW-300: produce the work package 0 inventory limited to the thin first version (three beats as rounds, six investigations per player, simple notebook, a mini-game per beat, Last Call, final theory, ending). Check code, not keywords. Output one document with file paths for every claim. No code changes.
