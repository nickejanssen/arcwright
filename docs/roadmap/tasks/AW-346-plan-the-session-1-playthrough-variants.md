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

## Acceptance Criteria

- [ ] Each variant (1a to 1d) is written down with its arc setup and what it tests, and the founder has approved the list.
- [ ] The replay-spoiler approach is decided and recorded.
- [ ] The survey or debrief can tell the variants apart.
- [ ] The core variant is named and is what the founder TV run plays.

## Tests/Verification

- The variant list and the approval on this task's issue.
- `python scripts/checks/scope_evidence_check.py`

## Dependencies

- AW-344, AW-345, AW-337 for the structures being compared; AW-305 for the case; AW-308 for preflight.
- Decisions: D-112, D-136, D-137.

## Must Not Do

- Do not let the extra variants delay the core variant past the founder TV run (5 December).
- Do not open any real case file or reveal the solution to the founder.

## Kickoff Prompt

> Read `AGENTS.md`, `HANDOVER.md`, this task, D-136 and D-137. Ask the founder one question at a time, with options and a recommendation, starting with how to avoid spoiling the case across variants. Record each answer on this task's issue.
