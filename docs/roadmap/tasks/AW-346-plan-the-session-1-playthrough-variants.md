---
id: productroadmap.roadmap.tasks.aw-346-plan-the-session-1-playthrough-variants
namespace: product-roadmap
title: "AW-346: Plan The Session 1 Playthrough Variants (1a To 1d)"
owner: Nico Janssen
status: active
review_by: "2027-02-19"
sensitivity: internal
source: authored
x-scope-evidence: D-137
tags: []
supersedes: []
---

# AW-346: Plan The Session 1 Playthrough Variants (1a To 1d)

**Milestone / Epic:** M7 / M7-C  
**Size:** S  
**Product:** Nightcap  
**Owner:** Orchestrator or playtest-ops session with the founder  
**Target date:** 2026-12-03

## Plain-English Summary

Session 1 is now several playthroughs of the same case, 1a to 1d, each set up differently, so the founder can compare mini-game structures with real players. Define each variant, the order to play them, what each one tests and how the survey tells them apart.

## Founder Direction (2026-11-19)

Founder's words: "On testable variant for our december timeline could be a detective agency version that has the building to a final race because everyone is competitive in the dysfunctional agency and they are trying to race the others to the solution. It could be a mix of trivia and caSE QUESTIONS. I like this version to test a lot! This could be the maximize fun version, then we have a maximize story + intrigue version, then we have a maximize deduction, investigation, and puzzles version, and 1 more. Each targeting a different type of player/cohort. We could learn so much from this. Please, lets make this happen!" Also: "Direction 1 with 2 as variant 1b, and merge 452 Also, it is not a strict 3 minigames per Nightcap playthrough. A game has 3 rounds isnt strict. We may playtest that, but its not strict. We should not hard code what games are played. They must be adaptive. There are anytime games, grou games, etc. End of round games can be the same as the number off rounds, but dont make it a concreate inflexible rule."

Recorded as D-144, D-145 and D-146. The variants now target kinds of players: maximize fun (a dysfunctional detective agency racing each other to the solution, building to a final race, trivia mixed with case questions; the founder's December priority), maximize story and intrigue, maximize deduction, investigation and puzzles, and a fourth not yet named. Rounds and mini-game counts are not fixed (D-145).

## Why This Matters

- Founder direction on 19 November 2026, recorded as D-137: "Both in session 1, not required to be played, but I would like to A/B test that experience. We could have Sesseion 1a, 1b, 1c, and possibly 1d to test out varied experiences."
- The status page planned one playthrough; the pass bar (fun, felt like a detective, play again) needs a way to compare variants.
- Playing the same case twice spoils its solution for the second playthrough. The plan must say how variants avoid that (for example different players, a second case, or variants that compare only the mini-game experience).

## Technical Scope

- Define each variant as an arc-file setup: which mini-games run in which round, the per-round cap (AW-344), and whether solo mini-games are on (AW-345). The core variant (1a) is the one the founder TV run proves.
- Decide the run order, how many players per variant, and how the replay-spoiler problem is handled.
- Extend the survey (spec 0095 decision 7) or the debrief so answers can be compared by variant, using the play record (D-115).
- Feed the result into AW-308 (preflight) and the host cheat sheet.

## Human Collaboration Contract

**Interaction profile:** Decision interview and facilitated live operation. The founder chooses the variants and the spoiler approach; nothing here is built without his approval.

## Interview Record And Sheets (2026-11-20)

The founder interview ran in a planning session. His answers are on issue #429, word for word. The sheets are in `docs/design/session-1-variants/` ([overview](../../design/session-1-variants/README.md)). Summary of what he said, to be confirmed when he approves the sheets:

- The fourth version is for newcomers. The agency race (1a) is the core version, and may repeat Battle of Wits; Battle of Wits is played on its own first (AW-348).
- The control mini-game is Search and Find, for now.
- A second case is written for replays. Targets: 1 December (end-to-end test of case 1), 5 December (feedback fixed, case 2 written, beta-test capable), 15 December (cases 1 and 2 with versions a to d testable). This replaces the 12 or 13 December session 1 of D-112; the orchestrator amends D-112, D-137 and the status page when he confirms.
- Version 1e, "Variety" (Direction 1, a different skill each round), is a fifth version at the founder's word: "Make it a fifth version".
- Two groups of 2 to 4 friends, each playing two versions on the two cases in a counterbalanced order.
- A solo mini-game run does not count against the no-repeat rule. The final race runs back to back with Last Call.
- The founder accepts being spoiled on both cases.

New tasks filed from this plan: AW-354 (#463, per-mini-game rating, version tags, extra survey questions), AW-355 (#464, Battle of Wits questions and host lines), AW-356 (#465, version arc setups and the group run sheet).

## Acceptance Criteria

- [x] Each version (1a to 1e) is written down with its arc setup and what it tests (`docs/design/session-1-variants/`).
- [ ] The founder has approved the list of five versions (his approval is recorded on this issue; not yet given).
- [x] The replay-spoiler approach is decided: a second case for replays, and two groups playing two versions in a counterbalanced order (founder's answers on issue #429; recorded as a decision when he approves the sheets).
- [x] The survey or debrief can tell the versions apart: the overview's survey table, with the build in AW-354 and a printed-card fallback.
- [x] The core variant is named: 1a, the agency race, played by the founder's 1 December end-to-end test (the date changed from the 5 December TV run; see above).

## Tests/Verification

- The variant list and the approval on this task's issue.
- `python scripts/checks/scope_evidence_check.py`

## Dependencies

- AW-344 (merged), AW-345, AW-337 for the structures being compared; AW-354, AW-355 and AW-356 for what the plan implies; AW-305 for the case; AW-308 for preflight.
- Decisions: D-112, D-136, D-137.

## Must Not Do

- Do not let the extra variants delay the core variant past the founder TV run (5 December).
- Do not open any real case file or reveal the solution to the founder.

## Kickoff Prompt

> Read `AGENTS.md`, `HANDOVER.md`, this task, D-136 and D-137. Ask the founder one question at a time, with options and a recommendation, starting with how to avoid spoiling the case across variants. Record each answer on this task's issue.
