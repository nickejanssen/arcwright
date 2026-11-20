---
id: productroadmap.roadmap.tasks.aw-355-write-the-battle-of-wits-questions-and-version-host-lines
namespace: product-roadmap
title: "AW-355: Write The Battle Of Wits Questions And The Host Lines For Versions 1a And 1b"
owner: Nico Janssen
status: active
review_by: "2027-02-20"
sensitivity: internal
source: authored
x-scope-evidence: D-146
tags: []
supersedes: []
---

# AW-355: Write The Battle Of Wits Questions And The Host Lines For Versions 1a And 1b

**Milestone / Epic:** M7 / M7-C  
**Size:** M  
**Product:** Nightcap (writing)  
**Owner:** The founder with a writing session  
**Target date:** 2026-11-30, for the 1 December end-to-end test

## Plain-English Summary

The agency race (1a) is trivia mixed with case questions, and the Newcomers version (1b) uses easy questions and extra host explanation. Someone has to write the questions and the host's words. Questions written by a person need no approval; questions written by a model would need a prompt, which is a hard rule.

## Why This Matters

- Founder's words (D-146): "It could be a mix of trivia and caSE QUESTIONS." He chose the agency race as the core version.
- Version sheets: `docs/design/session-1-variants/1a-agency-race.md` and `1b-newcomers.md`.
- Case questions must answer from facts players can see and must never give away the solution, in both cases.

## Technical Scope

- Question banks written by a person: easy trivia, mixed trivia, and logic and mental math (for 1a, 1b and, logic only, 1d), large enough that no question repeats in a playthrough.
- Case questions for case 1 and case 2: each answered from facts a player can have seen, and checked so none reveals the solution. The founder is spoiled on both cases (answer 6 on issue #429), so the check is made by a person comparing against the fairness file.
- Agency host lines for 1a (a wrapper, AW-319) and plain-words explanation lines for 1b (one per phase kind).
- No prompt, model call or new dependency. A model-written bank would be a separate approval.

## Human Collaboration Contract

**Interaction profile:** Creative collaboration. The founder chooses the tone and approves samples before the full banks are written (`docs/conventions/human-collaboration.md`, low-cost intermediate artifacts).

**Required founder inputs:** the tone for the agency host lines; a sample of ten questions per bank to react to.

**Current phase and next gate:** filed; next gate is the sample.

**Outstanding owner actions:** the founder reacts to the samples.

## Acceptance Criteria

- [ ] Sample questions and sample host lines are shown to the founder and he has approved or changed them.
- [ ] Banks are written and load in the Battle of Wits package (AW-337).
- [ ] Case questions for both cases pass a "gives away nothing" check recorded on the issue.
- [ ] The 1a and 1b host lines exist as written text.

## Tests/Verification

- The banks load and validate in the package loader; the "gives away nothing" check is recorded on the issue.

## Dependencies

- AW-337 (Battle of Wits package), AW-305 (case 1), AW-319 (agency framing), and case 2 (AW-346 plan).
