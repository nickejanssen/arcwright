---
id: productroadmap.roadmap.tasks.aw-306-connect-one-story-writing-tool-through-an-importer
namespace: product-roadmap
title: "AW-306: Connect One Story-Writing Tool Through An Importer"
owner: Nico Janssen
status: active
review_by: "2027-02-15"
sensitivity: internal
source: authored
x-scope-evidence: D-117
tags: []
supersedes: []
---

# AW-306: Connect One Story-Writing Tool Through An Importer

**Milestone / Epic:** M7 / M7-B  
**Size:** M  
**Product:** Arcwright  
**Owner:** One AI build session (Claude or Codex); founder picks the tool  
**Target date:** 2026-12-05

## Plain-English Summary

Let the founder write the second case in an existing story tool, and import it into Arcwright's format. Session 1 uses the hand-built case; session 2 uses a case written in the tool; the two are compared.

## Why This Matters

Founder decision D-117. Writing tools already exist and are free; Arcwright should not build one (D-114). None of them models who knows what or fair routes to a truth, so the work is an importer, not a replacement.

## Technical Scope

- Founder requirement, 16 November 2026: he must be able to read and manipulate a story graphically in the tool. Viewing, editing and building a story are one tool, adopted first to save time and built only if adoption falls short. The comparison must say, for each candidate, whether it has a graph view the founder can edit.
- A one-page comparison for the founder's choice. Candidates with licences checked on 14 November 2026: Ink (MIT), Yarn Spinner (MIT), Twine (GPL-3.0), Arcweave (free plan: 3 projects, 200 items, JSON export). articy:draft has a free version whose limits were not verified.
- An importer from the chosen tool's export into the authored case and arc format.
- Who knows what, and the fairness check, stay in Arcwright and run on the imported case.
- A one-page writing guide for the founder.

## Human Collaboration Contract

**Interaction profile:** Decision interview for the tool choice, then independent execution. A new dependency is a hard rule and needs founder approval.

## Acceptance Criteria

- [ ] A sample story written in the tool imports and runs headless.
- [ ] The fairness check runs on the imported case and reports failures in the author's terms.
- [ ] The founder writes one scene in the tool from the guide alone.

## Tests/Verification

- `python -m pytest engine/tests -q`

## Dependencies

- AW-302
- Findings and evidence: `docs/product/2026-11-15-reset-audit.md`

## Must Not Do

- Do not convert the first case mid-flight.
- Do not let the tool's runtime decide session state; the engine decides, by rule.
