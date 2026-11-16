---
id: productroadmap.roadmap.tasks.aw-319-try-the-detective-agency-framing-as-a-wrapper-on-the-first-case
namespace: product-roadmap
title: "AW-319: Try The Detective Agency Framing As A Wrapper On The First Case"
owner: Nico Janssen
status: active
review_by: "2027-02-15"
sensitivity: internal
source: authored
x-scope-evidence: D-119
tags: []
supersedes: []
---

# AW-319: Try The Detective Agency Framing As A Wrapper On The First Case

**Milestone / Epic:** M7 / M7-B  
**Size:** S  
**Product:** Nightcap  
**Owner:** The case-writing session drafts; the founder chooses  
**Target date:** 2026-11-28

## Plain-English Summary

The founder's idea, 16 November 2026: every Nightcap case starts with the group being hired to solve a mystery. The players are a slightly dysfunctional detective agency that always turns the case into a contest. Write this as a wrapper (intro, narrator voice, end-of-case banter) and compare it with the current invitation framing before session 1.

## Why This Matters

- The founder thinks it could give Nightcap more identity and wants to compare framings ("a/b test stories").
- The current design has rival detectives racing each other with no in-fiction reason. The agency gives one.
- Being hired works for any setting, so a case needs no invented reason for the group to be there.
- This is an idea under test, not approved scope. The approved framing is still the invitation framing and restrained voice direction of 1 October 2026 (see `docs/gdd/nightcap/00-governance/`). Captured under D-119.

## Technical Scope

- Wrapper only. No change to mechanics, case structure, scoring, the engine or the case graph.
- Draft two short intro texts for the first case (AW-305): the current invitation framing and the agency framing. Each is the opening the TV would show, plus two or three sample narrator lines and one end-of-case line.
- Content lives in `nightcap/` with the first case. Nothing in `engine/` changes.
- Tone, set by the founder on 16 November 2026: "Dysfunctional should be comedic, but can still have depth when appropriate." The drafts may draw on his recorded inspirations (`docs/product/2026-11-15-reset-audit.md`, section 3). The drafting session proposes which ones fit, for example Dungeon Crawler Carl for comedy that still carries weight and Jackbox for party humour; those two are the session's suggestion, not the founder's pick.
- Open question for the founder: how to compare. Session 1 is one group on one night, so it cannot be a true A/B test. Options: the founder picks from the two drafts; a few outside readers react to both intros; or different framings run in different sessions after session 1. The online paper test stays paused (D-111).

## Human Collaboration Contract

**Interaction profile:** Creative collaboration, then a decision interview.

- Founder inputs: the comparison method, and the choice of framing for session 1. Tone is answered (see Technical Scope); the drafts show how comedy sits beside the "cinematic" promise.
- Next gate: the founder reviews the two intro drafts side by side.
- Approval: the founder's written choice on the issue. If the agency framing replaces the invitation framing, that is a product decision and goes in `docs/product/decisions-log.csv` before any canonical GDD page changes.

## Acceptance Criteria

- [ ] Two intro drafts for the first case exist, free of spoilers, and the founder has seen both.
- [ ] The comparison method is chosen and recorded on the issue.
- [ ] The framing for session 1 is chosen and recorded; a decision row is added if the premise changes.

## Tests/Verification

- The founder's recorded choice on the issue. Session 1 feedback on the chosen framing is noted in the GDD validation pages.

## Dependencies

- AW-305 (the first case, whose premise and tone approvals this feeds)

## Must Not Do

- Do not change mechanics or add a persistent agency that carries over between sessions; that touches Continuity, which is v1.1 scope (D-051).
- Do not edit the authoritative GDD or the approved creative samples before the founder decides.
- Do not restart the paused online paper test (D-111).
- Do not reveal anything about the first case's solution in the drafts.
