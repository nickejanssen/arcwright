---
id: productroadmap.roadmap.tasks.aw-354-add-per-mini-game-rating-and-version-tags-to-the-survey
namespace: product-roadmap
title: "AW-354: Add A Per-Mini-Game Rating, A Version Tag And The Extra Survey Questions"
owner: Nico Janssen
status: active
review_by: "2027-02-20"
sensitivity: internal
source: authored
x-scope-evidence: D-146
tags: []
supersedes: []
---

# AW-354: Add A Per-Mini-Game Rating, A Version Tag And The Extra Survey Questions

**Milestone / Epic:** M7 / M7-C  
**Size:** M  
**Product:** Nightcap (screens and play record), with one game-agnostic engine read  
**Owner:** One AI build session (Claude or Codex)  
**Target date:** 2026-12-05, so the first beta sessions can compare versions

## Plain-English Summary

The version sheets (AW-346) compare four versions of Nightcap. The approved survey has three taps per player (fun, felt like a detective, play again) plus a comment. To tell the versions apart the survey also needs a two-tap rating after each mini-game, a few extra questions, and every answer tagged with the version, the case and the group.

## Why This Matters

- Founder direction on issue #429: vary mini-games by cohort with common control games. Version sheets: `docs/design/session-1-variants/README.md`, section "Survey".
- It extends spec 0095 decision 7 (the survey is three taps), which the founder approved in D-139. Extending an approved decision needs his approval, and the survey and the play record (D-115) are on AGENTS.md's hard-rule list for telemetry signals.
- A zero-build fallback exists: the founder reads out a printed card after each playthrough. This task replaces the card with saved data.

## Technical Scope

- Plan first, with the questions and the saved shape in the plan, then stop for approval.
- After each mini-game, each phone asks for a rating (loved, fine, skip) and "play this one again?" (yes or no). Saved per player as events, as the survey answers are (spec 0095 decision 7, AW-331), with no table change if that holds.
- Extra questions: the version question from each version sheet, "did you need to ask the host a question", "I enjoyed this case (1 to 5)", and, at the end of a group's second playthrough, "which of the two did you prefer, and why".
- Tag every saved answer with the version name, the case and the group, taken from the arc setup (D-115 play record; the version name is game configuration, not an engine term).
- No arc logic in TypeScript; screens ask and send, the engine saves.

## Human Collaboration Contract

**Interaction profile:** Independent execution after plan approval; the question wording is the founder's.

**Required founder inputs:** approval of the plan, and of the question wording. The extension of the survey itself was approved by the founder on 2026-11-20 ("Approve (Recommended)", issue #429).

**Current phase and next gate:** filed; next gate is the plan.

**Outstanding owner actions:** none.

## Acceptance Criteria

- [ ] After a mini-game each phone shows the two-tap rating, and the answer is saved with the run it belongs to.
- [ ] The extra survey questions are asked and saved per player.
- [ ] Every saved answer carries the version name, the case and the group.
- [ ] A scripted run shows the answers read back by version and by mini-game.
- [ ] The privacy test still shows no private answer on the shared screen.
- [ ] `verify` and the other checks pass.

## Tests/Verification

- `python -m pytest engine/tests api/tests -q`; `npm test --prefix dashboard`; ruff and typecheck.

## Dependencies

- AW-331 (survey answers route), AW-304 (play record), AW-346 (the sheets), AW-332 and AW-333 (screens).
