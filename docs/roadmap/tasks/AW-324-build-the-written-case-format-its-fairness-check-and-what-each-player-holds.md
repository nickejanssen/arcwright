---
id: productroadmap.roadmap.tasks.aw-324-build-the-written-case-format-its-fairness-check-and-what-each-player-holds
namespace: product-roadmap
title: "AW-324: Build The Written Case Format, Its Fairness Check, And What Each Player Holds"
owner: Nico Janssen
status: active
review_by: "2027-02-16"
sensitivity: internal
source: authored
x-scope-evidence: D-112, D-118, D-123
tags: []
supersedes: []
---

# AW-324: Build The Written Case Format, Its Fairness Check, And What Each Player Holds

**Milestone / Epic:** M7 / M7-B  
**Size:** M  
**Product:** Shared (Arcwright and Nightcap)  
**Owner:** One AI build session (Claude or Codex)  
**Target date:** 2026-11-22

## Plain-English Summary

Give the engine one file format for a case written by a person, a loader that refuses an unfair case with a named reason, and a saved record of what each player found themselves. It is Parts A and B of spec 0093 and the first build task of the rebuild.

## Why This Matters

- The first case (AW-305) and the story-tool importer (AW-306) both need a format to aim at. Today the engine only knows cases it generates from a skeleton.
- The founder plays the first case unspoiled, so fairness has to be proven by rule and reported without revealing anything.
- The final theory may only count what a player found themselves. That needs a record that keeps "found" apart from "heard".
- Filed under D-119 when spec 0093 was drafted on 2026-11-16: the spec needed build work that no existing task covered.

## Technical Scope

- The case file fields in spec 0093, Part A, as typed models beside the existing code in `engine/case/`. The existing generated-case resolver is not changed.
- The six refusal rules A1 to A6, each with a named reason.
- Two reports: a full one for the case's author, and a summary of rule names, pass or fail, and counts that prints nothing from the case file.
- One function that answers "which concepts does this participant hold", built on the knowledge graph (spec 0093, Part B).
- At session start, each cast character's knowledge is saved into the knowledge graph.
- A small made-up case and arc in the test fixtures. No real case content.

## Human Collaboration Contract

**Interaction profile:** Independent execution after plan approval. The change crosses engine modules (`case`, `knowledge`, `session`), which is a hard rule in `AGENTS.md`.

- Blocked until the founder approves spec 0093 (issue #355).
- The build session writes a plan and stops for the founder's approval before code.

## Acceptance Criteria

- [ ] The "Part A" and "Part B" acceptance criteria of spec 0093 pass.
- [ ] No table change and no new dependency. If one is needed, the session stops and asks.
- [ ] No murder-mystery word is added to `engine/`.

## Tests/Verification

- `python -m pytest engine/tests/test_authored_case.py -q`
- `python -m pytest engine/tests -q`
- `python -m ruff check engine api`

## Dependencies

- AW-302: spec 0093 approved (issue #355).
- Spec: `docs/specs/0093-engine-spine-for-the-thin-version.md`

## Must Not Do

- Do not open, read or quote any real case file. Use the test fixture only.
- Do not judge a submitted final theory. That belongs to the endgame spec.
- Do not change the generated-case resolver or the old arc files.

## Kickoff Prompt

> Read `AGENTS.md`, `HANDOVER.md` and `docs/specs/0093-engine-spine-for-the-thin-version.md`. Confirm on issue #355 that the spec is approved; if not, stop. Task AW-324: build Parts A and B. Write the tests first from the spec's acceptance criteria. Write a plan and stop for founder approval, because this crosses engine modules. Never open a real case file.
