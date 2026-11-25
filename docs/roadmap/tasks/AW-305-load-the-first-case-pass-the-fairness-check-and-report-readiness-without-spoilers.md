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
- Convert the revised draft (Codex worktree, 22 November) to the spec 0093 Part A format now, with no paper gates first (D-156). Change the story only where a check forces it. Coordinate the approved round layout and Last Call transition with AW-356. Keep the private case in an approved private handoff and a private backup outside every repo.

## Human Collaboration Contract

**Interaction profile:** Creative collaboration and facilitated live operation. The founder reviews the case under D-153 and approves the preflight before the cold run and the runtime plan before integration. Current phase: engine conversion (D-156). A local four-round draft and one-off facilitator sheet are prepared; an AI blind run and an adversarial review gave directional evidence only. The sightline and timing check and the human blind test are no longer gates: the founder's 1 December run tests the technology, and the 5 December beta with friends is the story's blind test. Record approvals and results without publishing case truth.

## Acceptance Criteria

- [ ] The revised draft is backed up outside every repo before conversion starts.
- [ ] The converted case passes A0 to A6 at two, three and four players.
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

## Later, after playtesting starts (not gates for this task)

- Witness sightlines and timing, and a story-quality blind read, move to story iteration once playtests run (D-156). Record what the 5 December beta shows per round: leading suspect, runner-up, what changed their mind.

## Must Not Do

- Keep the culprit, method, essential truths and routes out of commit messages, pull requests, issues, public files and player-facing materials before the reveal. D-153 governs private founder access.
- Do not move solution material out of the file marked as spoilers.
