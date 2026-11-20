---
id: productroadmap.roadmap.tasks.aw-357-watch-step-time-live-and-load-test-before-scaling
namespace: product-roadmap
title: "AW-357: Watch The Engine's Step Time Live, And Load-Test It Before Many Games Share A Server"
owner: Nico Janssen
status: draft
review_by: "2027-02-20"
sensitivity: internal
source: authored
x-scope-evidence: none
tags: []
supersedes: []
---

# AW-357: Watch The Engine's Step Time Live, And Load-Test It Before Many Games Share A Server

**Milestone / Epic:** M7 / M7-A (runs after session 1)  
**Size:** M  
**Product:** Shared (Arcwright and Nightcap)  
**Owner:** One AI build session (Claude or Codex), after founder approval  
**GitHub issue:** [#467](https://github.com/nickejanssen/arcwright/issues/467)  
**Target date:** after session 1 (not before 12 December 2026), and before more than a few games share one server

## Plain-English Summary

Every moment the engine moves all running games forward one step (`tick_active_sessions` in `engine/session/phases.py`): it checks timers, ends phases and starts mini-games. Spec 0093 says that step should take under 0.2 seconds with 20 games running. The unit test from AW-350 only catches code that got slower on a test machine. It cannot show how the live game behaves on a busy real server. This task adds the two checks that can: a live measure of how long each step takes, with an alarm when it breaks the budget, and a load test with simulated phones on server-like hardware.

## Why This Matters

- Founder, 2026-11-20, in the orchestrator session, on the AW-350 limit: "it sound like it does effect the game because of we get to .4s and it turns out the machine is calm, then we have almost half second lags in the game" and "there's no guarantee the game will be played live on a calm machine. I don't want to hinder development, but it doesn't sound like we have found the best solution yet."
- Founder, same session: "tell the AW-350 session to add the query count to #455, and file one task for the later monitoring and load test". This is that task.
- A slow step delays every game on that server: phase ends, mini-game starts and timers land late. Tests on a laptop or CI cannot prove live performance; only live measurement and a load test can (orchestrator, inferred from common industry practice; not checked against a source today).

## Technical Scope

Layers, in this order. The plan may drop or defer a layer with a reason.

1. **Live step time.** Record how long each `tick_active_sessions` call takes and how many games it moved, as a structured telemetry event or metric through the existing `engine/telemetry/` path (architecture section 11). Report the typical and worst values (for example p50, p95, p99) and raise a host-visible or operator alert when a step breaks the budget. No game words in `engine/`.
2. **Load test.** A repeatable script that runs N simulated games with simulated phones (join, answer, mini-game input, Pause) against a server-like deployment with Postgres, and reports step time and API response time per N. Find the N at which the 0.2-second budget breaks.
3. **Later, only if needed:** benchmarks on a fixed machine, recorded over time with change detection, if layers 1 and 2 show regressions slipping through.

## Human Collaboration Contract

**Interaction profile:** Decision interview, then independent execution.

- Adding a telemetry signal is an AGENTS.md hard rule ("prompt or eval suite changes: safety, routing, or telemetry signal changes"). The plan needs the founder's explicit approval before build.
- Running the load test against any hosted environment, or anything that costs money, needs the founder's go-ahead. The online playtest pause (D-111) still applies.

## Acceptance Criteria

- [ ] Each engine step's duration and game count are recorded live, and the typical and worst values can be read for a time window.
- [ ] A step over the budget raises an alert someone will see.
- [ ] A load-test script runs N simulated games and reports the N at which the budget breaks, on named hardware.
- [ ] Results are written into this task file and the HANDOVER log.
- [ ] `verify` passes.

## Tests/Verification

- Unit tests for the step-time recording (fake clock, deterministic).
- One recorded load-test run, with its numbers in the PR body.

## Dependencies

- AW-350 (#447, pull request #455): the unit-level guards (engine processing time at 0.2 s plus a database-query count).
- After session 1.

## Must Not Do

- Do not loosen the AW-350 unit tests to make this pass.
- Do not deploy, restart the online playtest or spend money without the founder's word.
- Do not add a provider or model name anywhere.

## Kickoff Prompt

> Run `/implement AW-357`. Read `AGENTS.md`, `HANDOVER.md`, `docs/architecture/11-telemetry.md` and this task. Write the plan with recommendations, name the hard rule it hits, post it on the issue, and wait for the founder's own approval. Do not merge.
