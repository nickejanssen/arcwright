---
id: productroadmap.roadmap.tasks.aw-305-load-the-first-case-pass-the-fairness-check-and-report-readiness-without-spoilers
namespace: product-roadmap
title: "AW-305: Load The First Case, Pass The Fairness Check, And Report Readiness Without Spoilers"
owner: Nico Janssen
status: active
review_by: "2027-02-15"
sensitivity: internal
source: authored
x-scope-evidence: D-112
tags: []
supersedes: []
---

# AW-305: Load The First Case, Pass The Fairness Check, And Report Readiness Without Spoilers

**Milestone / Epic:** M7 / M7-B  
**Size:** M  
**Product:** Nightcap  
**Owner:** The case-writing session, plus a separate reviewer session  
**Target date:** 2026-11-28

## Plain-English Summary

Get the first hand-written case into the engine's format, prove it is fair by rule, and tell the founder whether it is ready without revealing anything about the solution.

## Why This Matters

Case 1 gates the founder's first end-to-end 1a run. The founder hosts and tests under D-153. Independent blind participants need only player-facing material. Public records stay spoiler-free.

## Technical Scope

- **D-138 (2026-11-19):** write a short account of what happened with one blank per solution slot, in the slots' order, as the text the player fills at Last Call. Keep it in the spoiler file with the solution.
- The case exists in the authored case format from the engine-spine spec.
- It passes the case-graph invariants named in spec 0092.
- A reviewer session that did not write the case reports pass or fail per invariant, using counts only.
- The real session 1 arc file sets `release_content: false` on its mini-game bindings, so a mini-game hands out no case information (AW-328, D-126; spec 0093, Q1 Answered). The setting and its test exist; this task only turns it on.
- Before engine conversion, validate the physical staging and paper difficulty gates below. Coordinate the approved round layout and Last Call transition with AW-356. Keep the private case in an approved private handoff.

## Human Collaboration Contract

**Interaction profile:** Creative collaboration and facilitated live operation. The founder reviews the case under D-153 and approves the preflight before the cold run and the runtime plan before integration. Current phase: paper preflight. A local four-round draft and one-off facilitator sheet are prepared. An AI blind run gives directional evidence only. The next human gate is confirmation of the sightlines and drainage timeline, followed by the host's approval to run a fresh blind session. Record approvals and results without publishing case truth.

## Acceptance Criteria

- [ ] Stage the witness positions, check when observations become possible, and reconcile drainage and event timing before inviting a fresh solver.
- [ ] Run a cold human paper test on the revised draft and a separate attempt to make a credible alternative fit. Record each round's leading suspect, runner-up and decisive observation. Allow six investigations without coaching or competitive rewards. A defensible proof should first become available in Round 4, with an evidence-backed rival theory still plausible at the end of Round 3.
- [ ] Recheck all active seats at two, three and four players, including one recoverable wrong turn and independent evidence paths. Resolve any blocker and rerun the affected gate before beginning engine conversion.

- [ ] The case loads and a headless session completes on it at two and at four players.
- [ ] The reviewer's report contains no culprit, method, truth or route.
- [ ] Founder approvals at premise, design and full-prose stages are recorded on the issue.

## Tests/Verification

- Run the spec 0093 Part A checks A1 to A6 against the actual 1a choice windows. Verify private brief and finding delivery, shared-only quiz evidence, private lock and the full closing sequence.
- Run the founder's timed TV-and-phone rehearsal after the engine and screen checks. Record what was merged, deployed and observed in play separately.

## Dependencies

- AW-302: spec 0093 approved. The format is Part A of `docs/specs/0093-engine-spine-for-the-thin-version.md`.
- AW-324, which builds the loader and the fairness check the case must pass.
- Findings and evidence: `docs/product/2026-11-15-reset-audit.md`

## Must Not Do

- Keep the culprit, method, essential truths and routes out of commit messages, pull requests, issues, public files and player-facing materials before the reveal. D-153 governs private founder access.
- Do not move solution material out of the file marked as spoilers.
