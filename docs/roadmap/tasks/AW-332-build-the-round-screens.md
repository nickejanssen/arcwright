---
id: productroadmap.roadmap.tasks.aw-332-build-the-round-screens
namespace: product-roadmap
title: "AW-332: Build The Round Screens: Story, Thinking Time, Investigate, Finding, Notebook, Mini-Game And Its Result"
owner: Nico Janssen
status: active
review_by: "2027-02-19"
sensitivity: internal
source: authored
x-scope-evidence: D-139
tags: []
supersedes: []
---

# AW-332: Build The Round Screens: Story, Thinking Time, Investigate, Finding, Notebook, Mini-Game And Its Result

**Milestone / Epic:** M7 / M7-B  
**Size:** L  
**Product:** Nightcap  
**Owner:** One AI build session  
**Target date:** 2026-12-02

## Plain-English Summary

Build screens 4 to 12 of spec 0095: the story on the TV, the quiet TV during thinking time, the phone's investigate menu, findings and notebook, and the mini-game shared view, phone view and result, including several mini-games in a round and solo mini-games.

## Why This Matters

- Spec 0095 Part L screens 4 to 12, approved 2026-11-19 (D-139).
- D-134: the TV stays quiet during thinking time. D-136: a round may run several mini-games, and a solo mini-game runs on one phone only. AW-343: the phone shows rewards from the menu read, not only the live message.

## Technical Scope

- Screens 4 to 12, chosen by the phase the engine reports.
- Mini-game result (screen 12) reads the player's rewards from the menu read (`rewards`, matched by `grant_id`), so a missed live message still shows.
- Handle several mini-games in a round (AW-344) and a solo mini-game on one phone (AW-345) as those land; what the TV and other phones show during a solo mini-game is settled in AW-345's design.
- Owns (spec 0095): `dashboard/src/screens/round/`, `dashboard/src/screens/notebook/`.

## Human Collaboration Contract

**Interaction profile:** Independent execution after plan approval; the screen copy follows the approved sample. The founder approves the plan in the build session himself, or by his own comment on this task's issue. A build session must not act on an approval relayed or posted for him by another session.

## Acceptance Criteria

- [ ] Each of screens 4 to 12 has a component test with fixture data.
- [ ] The TV during thinking time shows only the round title, clock and who is ready (D-134).
- [ ] The phone's investigations-left number equals the route's number in every step.
- [ ] A reward shows on the result screen from the menu read when no live message arrived.

## Tests/Verification

- `npm test --prefix dashboard`, typecheck and build.
- Merged, deployed and seen in play are separate; seen in play is the founder TV run.

## Dependencies

- AW-330, AW-331, AW-303, AW-328 merged; AW-343 merged. AW-344 and AW-345 for their parts.
- Decisions: D-128, D-134, D-136, D-139.

## Must Not Do

- No game rule in TypeScript: no budget arithmetic, no right-or-wrong, no deciding what is on a menu or a theory list (spec 0095 Part L; AGENTS.md).
- No internal ID on any screen. Nothing private on the TV.
- Do not change `nightcap-web/`, `sdk/` or `nightcap/mini_games/` (spec 0095 Part K).
- Do not open any real case file.

## Kickoff Prompt

> Read `AGENTS.md`, `HANDOVER.md`, this task and `docs/specs/0095-screens-for-the-thin-version.md` (the parts named above and every "Answered" section). Confirm the dependencies are merged. Write a plan with the exact file list and the tests you will write first, post it on this task's issue, and stop for the founder's approval.
