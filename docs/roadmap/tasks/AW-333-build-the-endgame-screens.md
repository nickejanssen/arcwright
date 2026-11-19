---
id: productroadmap.roadmap.tasks.aw-333-build-the-endgame-screens
namespace: product-roadmap
title: "AW-333: Build The Endgame Screens: Last Call, Your Theory, The Accused, The Verdict, The Postmortem, The Survey"
owner: Nico Janssen
status: active
review_by: "2027-02-19"
sensitivity: internal
source: authored
x-scope-evidence: D-139
tags: []
supersedes: []
---

# AW-333: Build The Endgame Screens: Last Call, Your Theory, The Accused, The Verdict, The Postmortem, The Survey

**Milestone / Epic:** M7 / M7-B  
**Size:** M  
**Product:** Nightcap  
**Owner:** One AI build session  
**Target date:** 2026-12-03

## Plain-English Summary

Build screens 13 to 22 of spec 0095: Last Call on the TV, the phone's theory as a short story to fill plus one proof, the accused revealed one at a time, the Verdict with the winner's proof, each player's own result, the Postmortem lines and the survey.

## Why This Matters

- Spec 0095 Part L screens 13 to 22, approved 2026-11-19 (D-139).
- D-135: the accused are shown one at a time; staging, hold and order belong to Nightcap and never depend on who is right. D-138: the theory is a short written account filled with the player's own pieces plus one proof; the winner's proof is shown at the Verdict.

## Technical Scope

- Screens 13 to 22. Screen 14 is the account with blanks and a Proof field (D-138). Screen 16 stages the reveal from Nightcap's settings (D-135). Screen 17 adds the winner's proof. Screen 18 appears only after the TV's Verdict.
- The theory form lists pieces in the exact order the route returns.
- Owns (spec 0095): `dashboard/src/screens/endgame/`, `dashboard/src/screens/survey/`.

## Human Collaboration Contract

**Interaction profile:** Independent execution after plan approval; the screen copy follows the approved sample. The founder approves the plan in the build session himself, or by his own comment on this task's issue. A build session must not act on an approval relayed or posted for him by another session.

## Acceptance Criteria

- [ ] Each of screens 13 to 22 has a component test.
- [ ] The theory form keeps the route's order (test with two orders) and shows the account text with blanks and a proof field.
- [ ] The reveal order comes from Nightcap's settings and never from right or wrong.
- [ ] The phone's private result appears only after the TV's Verdict in the recorded run.

## Tests/Verification

- `npm test --prefix dashboard`, typecheck and build.
- Merged, deployed and seen in play are separate; seen in play is the founder TV run.

## Dependencies

- AW-330 and AW-331 merged; AW-326 and AW-327 merged (with D-138's account text and proof).
- Decisions: D-128, D-135, D-138, D-139.

## Must Not Do

- No game rule in TypeScript: no budget arithmetic, no right-or-wrong, no deciding what is on a menu or a theory list (spec 0095 Part L; AGENTS.md).
- No internal ID on any screen. Nothing private on the TV.
- Do not change `nightcap-web/`, `sdk/` or `nightcap/mini_games/` (spec 0095 Part K).
- Do not open any real case file.

## Kickoff Prompt

> Read `AGENTS.md`, `HANDOVER.md`, this task and `docs/specs/0095-screens-for-the-thin-version.md` (the parts named above and every "Answered" section). Confirm the dependencies are merged. Write a plan with the exact file list and the tests you will write first, post it on this task's issue, and stop for the founder's approval.
