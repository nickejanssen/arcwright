---
id: productroadmap.roadmap.tasks.aw-304-make-play-records-game-agnostic
namespace: product-roadmap
title: "AW-304: Make Play Records Game-Agnostic"
owner: Nico Janssen
status: active
review_by: "2027-02-15"
sensitivity: internal
source: authored
x-scope-evidence: D-115
tags: []
supersedes: []
---

# AW-304: Make Play Records Game-Agnostic

**Milestone / Epic:** M7 / M7-B  
**Size:** M  
**Product:** Arcwright  
**Owner:** One AI build session (Claude or Codex)  
**Target date:** 2026-12-05

## Plain-English Summary

Make sure every session, for any game, saves the same six generic facts, and that the records do not use one game's vocabulary.

## Why This Matters

The founder's direction is that play data is captured at engine level so any game can learn from it (D-115). The engine already records events, decisions, generated lines, beat states, mini-game runs and consent, but some records use Nightcap words such as accusation and contradiction.

## Technical Scope

- The six facts: story units entered and left, with times; who learned what, and from whom; what each participant chose from what was offered; what each character said; tension against the author's target; cost.
- Find every game-specific word in record and table names and either make it game configuration or list it with a follow-up.
- A short query pack that answers: where did players stall, what content did nobody see, which characters drew attention, was the mini-game reward used.

## Human Collaboration Contract

**Interaction profile:** Independent execution after plan approval. A rename that touches a database table needs a migration and founder approval (hard rule).

## Acceptance Criteria

- [ ] After one headless session, one query per fact returns rows.
- [ ] The four questions above are answerable from the record without reading game content files.
- [ ] No new game-specific word enters `engine/`; remaining ones are listed with an issue.

## Tests/Verification

- `python -m pytest engine/tests -q`

## Dependencies

- AW-302: spec 0093 approved. This task is Part F of `docs/specs/0093-engine-spine-for-the-thin-version.md`.
- AW-325, which saves the choices and phase changes these records read.
- Findings and evidence: `docs/product/2026-11-15-reset-audit.md`

## Must Not Do

- No graph database, dashboard or model training in this task.
- No analysis tooling beyond plain queries.
