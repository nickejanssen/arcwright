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
- Let the finished result satisfy the beat's exit condition.
- All timing, validation and scoring stay in Python.

## Human Collaboration Contract

**Interaction profile:** Independent execution after plan approval. The change crosses engine modules, which is a hard rule in `AGENTS.md` and needs design review.

## Acceptance Criteria

- [ ] Headless test: entering a beat with a bound mini-game creates and starts a run.
- [ ] With no submissions at all, the run ends when its deadline passes.
- [ ] Duplicate and late submissions behave as the existing tests require.
- [ ] When the run ends, the beat can end.
- [ ] Passes at two and at four players with no AI call.
- [ ] Seen once on a real TV and two phones, recorded on the issue.

## Tests/Verification

- `python -m pytest engine/tests -q`

## Dependencies

- AW-302: spec 0093 approved. This task is Part E of `docs/specs/0093-engine-spine-for-the-thin-version.md`.
- AW-325, which builds the phases and the clock this task connects the run to.
- Findings and evidence: `docs/product/2026-11-15-reset-audit.md`

## Must Not Do

- Add no game-specific word to `engine/`.
- No new mini-games, no package platform work, no reward redesign. The reward for winning is AW-328 (D-126).

## Kickoff Prompt

> Read `AGENTS.md`, `HANDOVER.md`, the approved engine-spine spec and `engine/mini_games/runtime.py`. Confirm the spec is approved; if not, stop. Task AW-303: wire the existing mini-game runtime into session flow. Write tests first, including a run that times out with zero submissions. Write a plan and stop for founder approval, because this crosses engine modules.
