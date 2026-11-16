---
id: productroadmap.roadmap.tasks.aw-325-make-rounds-move-by-rule-with-a-saved-investigation-budget
namespace: product-roadmap
title: "AW-325: Make Rounds Move By Rule, With A Saved Investigation Budget"
owner: Nico Janssen
status: active
review_by: "2027-02-16"
sensitivity: internal
source: authored
x-scope-evidence: D-112, D-113, D-118, D-123
tags: []
supersedes: []
---

# AW-325: Make Rounds Move By Rule, With A Saved Investigation Budget

**Milestone / Epic:** M7 / M7-B  
**Size:** L  
**Product:** Shared (Arcwright and Nightcap)  
**Owner:** One AI build session (Claude or Codex)  
**Target date:** 2026-11-26

## Plain-English Summary

Make a round run by itself: show its written scene, open the investigation menu, count each player's choices against a saved budget of six, and move on by rule or by a clock. It is Parts C and D of spec 0093.

## Why This Matters

- Today a live game moves on only when every player has typed once, and every condition the arc author wrote is treated as met.
- Nothing sends a beat's written scene to the screens (found on 2026-11-16 while writing spec 0093).
- The investigation limit that exists is per beat, held in memory, and has no route, so a phone cannot use it and a restart loses it.
- Filed under D-119 when spec 0093 was drafted on 2026-11-16: the spec needed build work that no existing task covered.

## Technical Scope

- Ordered phases on a beat (`scene`, `choices`, `mini_game`, `bridge`), each ending by the rules in spec 0093, Part C. Arc files without phases behave exactly as today.
- One engine function, the tick, that applies every deadline that is due, and a loop in the API that calls it once a second. Pause and resume keep the time left.
- Sending a beat's written scene and bridge lines as events.
- The investigation menu, the budget across the whole game, free review, repeat-safe choices, and readiness (Part D).
- Routes with thin handlers: read my menu, choose, mark ready, read what I hold, host move-on, and the current beat, phase and deadline.
- The `mini_game` phase is entered and left by this task with a stand-in; AW-303 connects the real run.

## Human Collaboration Contract

**Interaction profile:** Independent execution after plan approval. The change crosses engine modules (`arc`, `session`, `interactions`, `characters`, `events`) and adds API routes, which is a hard rule in `AGENTS.md`.

- Spec 0093 was approved on 2026-11-16 (D-124, issue #355). Still blocked until AW-324 is merged.
- The build session writes a plan and stops for the founder's approval before code.

## Acceptance Criteria

- [ ] The "Part C" and "Part D" acceptance criteria of spec 0093 pass.
- [ ] Both registered arc files load and run unchanged; no existing test is edited to make it pass.
- [ ] No table change, no new dependency, and no change under `sdk/`, `dashboard/` or `nightcap-web/`.
- [ ] No murder-mystery word is added to `engine/`.

## Tests/Verification

- `python -m pytest engine/tests -q`
- `python -m pytest api/tests -q`
- `python -m ruff check engine api`

## Dependencies

- AW-324
- AW-302: spec 0093 approved (issue #355).
- Spec: `docs/specs/0093-engine-spine-for-the-thin-version.md`

## Must Not Do

- Do not let typed input or a model call decide when a round moves on.
- Do not send the content of a choice to the shared screen or to another player.
- Do not change the old questioning code in `engine/interactions/` or the old arc files.
- Do not build Last Call or anything after it.

## Kickoff Prompt

> Read `AGENTS.md`, `HANDOVER.md` and `docs/specs/0093-engine-spine-for-the-thin-version.md`. Confirm on issue #355 that the spec is approved and that AW-324 is merged; if not, stop. Task AW-325: build Parts C and D. Write the tests first from the spec's acceptance criteria, with a controlled clock. After every transition read the state back, because a refused transition does not raise. Write a plan and stop for founder approval, because this crosses engine modules.
