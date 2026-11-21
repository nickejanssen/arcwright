---
id: productroadmap.roadmap.tasks.aw-358-fix-the-two-findings-left-open-by-aw-351
namespace: product-roadmap
title: "AW-358: Fix The Two Review Findings Left Open When AW-351 Merged"
owner: Nico Janssen
status: draft
review_by: "2027-02-21"
sensitivity: internal
source: authored
x-scope-evidence: none
tags: []
supersedes: []
---

# AW-358: Fix The Two Review Findings Left Open When AW-351 Merged

**Milestone / Epic:** M7 / M7-B  
**Size:** M  
**Product:** Nightcap, with one shared dashboard file  
**Owner:** One AI build session, after founder approval of its plan  
**GitHub issue:** [#475](https://github.com/nickejanssen/arcwright/issues/475)  
**Target date:** before the founder's end-to-end test on 1 December 2026 (D-149)

## Plain-English Summary

Tell Me Something True merged with two known problems. After a reconnect, the TV cannot rebuild the final scoreboard. If the lobby takes longer than half a second to answer, the TV can show a generic player label for a whole spotlight. This task fixes both.

## Why This Matters

- The founder chose to merge pull request #472 with these findings open ("Merge anyway", 2026-11-21, recorded on the pull request). Merged is not fixed.
- The founder's test will reach this scoreboard, and a TV or phone reload during a party is normal.

## Technical Scope

1. **P1, scoreboard after a reconnect** (`nightcap/mini_games/tell-me-something-true/client/renderer.ts:443`). The engine marks the run finished as it produces the scoreboard step, and `get_active_run` excludes finished runs, so the active route returns 404 after a reload. Verify the finished-run path and give the screen a tested route to the correct result, or name the missing prerequisite.
2. **P2, lobby name lookup** (`dashboard/src/mini-games/client.ts:250`). A healthy lobby slower than 500 ms is aborted and its names are discarded. If the first lookup and the stream-start refresh both time out, nothing retries. Keep mounting bounded, but finish or retry the lookup in the background, with guards for a stale run and an unmounted screen.

The approved result-hold design (D-155) includes a privacy-safe result read that may also close finding 1. The plan must say whether to build them together. That design's implementation plan is not approved, and this task does not approve it.

## Human Collaboration Contract

**Interaction profile:** Independent execution after plan approval.

- The founder approves the plan in his own words, in the builder's session or in his own issue comment.
- Finding 1 may cross engine, API and package code, which is an AGENTS.md hard rule. The plan must name any hard rule it hits.
- The plan names who takes finding 2, because `dashboard/` is the screens lane. Two builders must not edit `client.ts` at once.

## Acceptance Criteria

1. After a TV or phone reload at the scoreboard step of a real finished run, the screen shows the correct result or a deliberate, tested fallback.
2. The scoreboard read exposes no private player data to the unsigned shared display.
3. A lobby reply slower than 500 ms still replaces the generic label during the same spotlight, with no stream reconnect.
4. A delayed reply from an earlier run cannot change names in the current run, and a reply after unmount does nothing.
5. Mounting never waits on the lobby lookup.

## Tests/Verification

- A test that runs the real engine transition to a finished run, then reads the result as a reconnecting screen. The recorded fixture alone is not proof.
- Dashboard tests for delayed success, stale reply and unmount.
- All six pull request checks pass.

## Dependencies

- AW-351 (#457, pull request #472, merged as `fdd0c77`).
- D-155, if the plan builds finding 1 on its result read.

## Must Not Do

- Do not treat the fixture as proof of the live step.
- Do not send private entries to the shared display.
- Do not build the rest of D-155 under this task.
- Do not put Nightcap or game-specific assumptions in `engine/`.

## Kickoff Prompt

> Implement AW-358 (#475). Read `AGENTS.md`, `HANDOVER.md`, this task and the two deferred threads on pull request #472. Write the plan with recommendations, name any hard rule it hits, post it on the issue, and wait for the founder's own approval. Do not merge.
