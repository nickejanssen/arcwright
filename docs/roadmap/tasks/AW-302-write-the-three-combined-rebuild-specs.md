---
id: productroadmap.roadmap.tasks.aw-302-write-the-three-combined-rebuild-specs
namespace: product-roadmap
title: "AW-302: Write The Three Combined Rebuild Specs"
owner: Nico Janssen
status: active
review_by: "2027-02-15"
sensitivity: internal
source: authored
x-scope-evidence: D-118
tags: []
supersedes: []
---

# AW-302: Write The Three Combined Rebuild Specs

**Milestone / Epic:** M7 / M7-B  
**Size:** L  
**Product:** Shared (Arcwright and Nightcap)  
**Owner:** One spec-author session; founder approves each spec  
**Target date:** 2026-11-25

## Plain-English Summary

Replace about twelve separate spec approvals with three: the engine spine, the screens, and the endgame. Each has acceptance criteria and a headless proof.

## Why This Matters

Spec 0092 asks for an approved spec per work package. On 10 to 15 founder hours a week that alone could take the month. The founder accepted three combined specs on 15 November 2026 (D-118).

## Technical Scope

- Engine spine: authored case format, loader and fairness check; per-player proof tracking; beats as rounds; the investigation budget; mini-game start, clock and return; game-agnostic play records.
- Screens: one client, TV and phone, for the thin version; the build-versus-adopt choices from AW-309.
- Endgame: Last Call, the final theory (culprit plus a short causal chain), the rule-based theory checker, the accused reveal, the Truth, the Verdict and a short Postmortem.
- Each spec lists which hard rules it touches (cross-module engine change, schema or migration, new dependency, prompts) so approvals are asked once.

## Human Collaboration Contract

**Interaction profile:** Decision interview. Each of the three specs needs its own founder approval before building starts.

## Progress

- **Engine spine: approved 2026-11-16** (D-124, issue #355). `docs/specs/0093-engine-spine-for-the-thin-version.md`. It needed two build tasks that did not exist: AW-324 and AW-325.
- **Screens: drafted 2026-11-16, not approved.** `docs/specs/0095-screens-for-the-thin-version.md`, merged to main as a draft in pull request #393. It follows D-128 (the screens protect "I outsmarted you" first). Five open questions for the founder. Proposed build tasks AW-329 to AW-334, not yet created. The walkthrough (AW-301) checks the twelve claims the spec lists under "What the walkthrough must confirm".
- **Endgame: approved 2026-11-16** (D-125, issue #355). `docs/specs/0094-endgame-for-the-thin-version.md`. Build tasks: AW-326 and AW-327.
- **Mini-game reward (spec 0093, Q1): answered 2026-11-16** (D-126). The top-ranked get one extra investigation. Build task: AW-328.

## Acceptance Criteria

- [ ] Three specs in `docs/specs/` from the template, each with acceptance criteria and a named headless test.
- [ ] Each spec states merged, deployed and verified-in-play separately.
- [ ] The founder's approval of each is recorded on its issue before any build task starts.

## Tests/Verification

- `python scripts/checks/scope_evidence_check.py`

## Dependencies

- AW-300, AW-309
- Findings and evidence: `docs/product/2026-11-15-reset-audit.md`

## Must Not Do

- Do not start implementation.
- Do not add scope beyond the thin version in `docs/product/nightcap-status.md` without a founder decision.
