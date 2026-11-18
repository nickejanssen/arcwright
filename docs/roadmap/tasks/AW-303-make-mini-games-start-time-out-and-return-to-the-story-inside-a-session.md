---
id: productroadmap.roadmap.tasks.aw-303-make-mini-games-start-time-out-and-return-to-the-story-inside-a-session
namespace: product-roadmap
title: "AW-303: Make Mini-Games Start, Time Out And Return To The Story Inside A Session"
owner: Nico Janssen
status: active
review_by: "2027-02-15"
sensitivity: internal
source: authored
x-scope-evidence: D-113
tags: []
supersedes: []
---

# AW-303: Make Mini-Games Start, Time Out And Return To The Story Inside A Session

**Milestone / Epic:** M7 / M7-B  
**Size:** M  
**Product:** Shared (Arcwright and Nightcap)  
**Owner:** One AI build session (Claude or Codex)  
**Target date:** 2026-11-28

## Plain-English Summary

The mini-game runtime is built and tested, but nothing in the product starts one. Wire it into session flow so a beat's mini-game starts when the beat reaches it, ends on the engine's clock, and lets the beat end.

## Why This Matters

Verified in code on 14 November 2026: outside tests, nothing calls `create_run`, `start_run` or `check_timeout` in `engine/mini_games/runtime.py`; only `resolve_run` is reachable, through a host command. Nothing links a finished run to the beat ending. "A mini-game after every beat" (D-113) cannot happen until this exists.

## Technical Scope

- Start a bound mini-game when its beat is reached.
- Fire the deadline from the engine's clock, with no submission needed.
- Let the finished result satisfy the beat's exit condition. AW-325 left the hook: call `finish_mini_game_phase(db, session_id, now, publish)` in `engine/session/phases.py` when a run reaches any end state.
- Pausing the session also pauses the active run and keeps its time left; resuming restarts it (spec 0093, Part C). AW-325 kept only the phase clock: `freeze_phase` and `thaw_phase` do not touch a run. Found by the review of pull request #397 on 2026-11-17 and carried here under D-119.
- All timing, validation and scoring stay in Python.

## Human Collaboration Contract

**Interaction profile:** Independent execution after plan approval. The change crosses engine modules, which is a hard rule in `AGENTS.md` and needs design review.

## Acceptance Criteria

- [x] Headless test: entering a beat with a bound mini-game creates and starts a run.
- [x] With no submissions at all, the run ends when its deadline passes.
- [x] Duplicate and late submissions behave as the existing tests require.
- [x] When the run ends, the beat can end.
- [x] Pausing during a run stops the run's clock; resuming keeps the time that was left.
- [x] Passes at two and at four players with no AI call.
- [ ] Seen once on a real TV and two phones, recorded on the issue.

## Tests/Verification

- `python -m pytest engine/tests -q`

## Dependencies

- AW-302: spec 0093 approved. This task is Part E of `docs/specs/0093-engine-spine-for-the-thin-version.md`.
- AW-325, which builds the phases and the clock this task connects the run to. Merged 2026-11-17 (pull request #397); read its task file's "What Was Built" section first.
- Findings and evidence: `docs/product/2026-11-15-reset-audit.md`

## Must Not Do

- Add no game-specific word to `engine/`.
- No new mini-games, no package platform work, no reward redesign. The reward for winning is AW-328 (D-126).

## Kickoff Prompt

> Read `AGENTS.md`, `HANDOVER.md`, the approved engine-spine spec and `engine/mini_games/runtime.py`. Confirm the spec is approved; if not, stop. Task AW-303: wire the existing mini-game runtime into session flow. Write tests first, including a run that times out with zero submissions. Write a plan and stop for founder approval, because this crosses engine modules.

## What Was Built

Built on 2026-11-18 under spec 0093, Part E. The founder approved the plan on 2026-11-17 (issue #356).

- **Where.** New `engine/session/mini_game_phase.py` (begin, advance, stop, pause, resume), called from `engine/session/phases.py`. `engine/mini_games/resolver.py` gained `RunBinding` (beat, binding, phase visit) on the snapshot; `engine/arc/models.py` gained the optional `mini_game_root` on the arc. `engine/mini_games/runtime.py` is unchanged.
- **Rules.** The tick asks the run whether its time is up and reads its state back. Any end state ends the phase (`mini_game_ended`). The phase's `seconds` is a hard cap (`time`) that cancels a run still going. A phase ended any other way (host move-on) cancels the open run. No binding: the phase is skipped (`mini_game_skipped`). A binding that cannot run (`no_root`, `package_missing`, `version_mismatch`, `unknown_mechanic`, `invalid_definition`, `resolution_failed`, `run_not_started`) or a missing run (`run_missing`), or a game rule that raises while starting or ending the run (`run_not_started`, `run_failed`): the phase ends with `mini_game_error:<code>` and a host-only `mini_game_unavailable` event, so the round never hangs. A phase whose limit is not longer than the game's length sends a host-only `mini_game_warning`. The arc file refuses a phased beat that binds a mini-game but has no `mini_game` phase. Database errors are not turned into game errors. Pause and resume keep the run's time left to the second.
- **The hook.** The tick reaches the end rule from inside the session lock. `finish_mini_game_phase` is the same rule for a caller outside the tick (a route could call it to avoid up to one second of wait); it changes nothing while the run is still going.
- **Tests.** `engine/tests/test_mini_game_phase.py`, and real runs in `test_spine_headless.py` at 2 and 4 players. A test-only package and game rule stand in for a game that allows 2 or 3 players; no shipped game changed.
- **Not changed.** No table, migration, dependency or model call; nothing under `api/` (except one test fixture), `sdk/`, `dashboard/`, `nightcap-web/` or `nightcap/`.
- **Left open.** Criterion 7, the TV and two phones. The round view's countdown shows the phase's time, not the run's. The resume event is not delivered to screens. A hybrid or generative game calls the model when its phase starts, inside the session lock, so it can briefly block that session's other writers (resolving before the lock is a follow-up for when the first real game is wired). Only the first binding on a beat is used. A game's own length must be shorter than its phase's `seconds`. Player counts are not checked (AW-337).
