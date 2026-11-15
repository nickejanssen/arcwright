---
id: productroadmap.roadmap.tasks.aw-313-fix-or-drop-the-orphaned-document-freshness-number
namespace: product-roadmap
title: "AW-313: Fix Or Drop The Orphaned-Document Freshness Number"
owner: Nico Janssen
status: active
review_by: "2027-02-15"
sensitivity: internal
source: authored
x-scope-evidence: none
tags: []
supersedes: []
---

# AW-313: Fix Or Drop The Orphaned-Document Freshness Number

**Milestone / Epic:** M6 / M6-D  
**Size:** S  
**Product:** Shared (Arcwright and Nightcap)  
**Owner:** One AI build session (Claude or Codex)  
**Target date:** 2027-01-30

## Plain-English Summary

The session-start message reports an "orphaned" count. At baseline it counted 438 of 449 documents, so it says nothing. Make it mean something or remove it.

## Why This Matters

A number that is always alarming teaches every session to ignore the freshness report.

## Technical Scope

- "Orphaned" currently means "not referenced by any document".
- Options: count only documents past `review_by`, or drop the number.

## Human Collaboration Contract

**Interaction profile:** Independent execution. Blocked until the tooling freeze ends at the rebuild's first TV session (D-111), because it changes tooling behaviour.

## Acceptance Criteria

- [ ] The session-start report shows only numbers a session can act on.

## Tests/Verification

- `python -m pytest scripts/hooks/tests scripts/tests -q`

## Dependencies

- None
- Findings and evidence: `docs/product/2026-11-15-reset-audit.md`

## Must Not Do

- Do not start before the freeze ends.
