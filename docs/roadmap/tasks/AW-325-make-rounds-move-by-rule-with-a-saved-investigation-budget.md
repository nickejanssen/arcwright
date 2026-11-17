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

## What Was Built (for AW-303 and AW-328)

Built on 2026-11-16 under spec 0093, Parts C and D. The founder approved the plan the same day.

- **Phases.** `engine/arc/models.py`: `PhaseDefinition` on a beat (`scene`, `choices`, `mini_game`, `bridge`, in that order, each at most once, each with required `seconds`), `ChoiceConfig.budget` (default 6) on the arc. Phases on every beat or on none. The old arc files have none and run as before.
- **The rules and the tick.** `engine/session/phases.py`. Saved state is one `phase_state` event per change; readiness is a `decisions` row of type `ready`. `tick`, `mark_ready`, `host_move_on`, `freeze_phase`, `thaw_phase`, `round_view`, `tick_active_sessions`. The API loop is `api/tick_loop.py`, started by the app's lifespan.
- **Choices.** `engine/session/choices.py`. A choice is a `decisions` row of type `choice`. The budget is worked out only in `remaining_budget` / `budget_allowance`.
- **For AW-303.** Call `finish_mini_game_phase(db, session_id, now, publish)` when a run reaches any end state. It ends the phase, or changes nothing if the phase is not a running `mini_game`. The phase's `seconds` is the outer time limit until a run's own deadline replaces it. Pausing the run is not done here: `freeze_phase` and `thaw_phase` only keep the phase clock.
- **For AW-328.** Save a `decisions` row with `decision_type = "budget_grant"`, `context = {"participant_id": "<id>"}` and `outcome = {"amount": n}`. It is added to that participant's allowance. Nothing else changes.
- **Checked at session start.** The fairness check now takes the budget from the arc file, and an arc whose case offers choices in a beat with no `choices` phase is refused.
- **Not changed.** No table, no migration, no dependency, no model call, nothing under `engine/interactions/`, `sdk/`, `dashboard/` or `nightcap-web/`.
