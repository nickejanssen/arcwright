# Mini-game Platform and Nightcap Readiness Program Plan

> **For Codex:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to execute
> this plan task by task. Do not execute any task until the founder separately
> approves implementation.

**Goal:** Make every existing Nightcap mini-game game-ready, give Couch Race a
valid mini-game opportunity in every beat, and prove that the same Arcwright
contracts work for a non-Nightcap game using its own engine.

**Architecture:** Games register versioned mini-game packages. Human-authored
arcs define story opportunities, eligible candidates, repetition, fallback,
and consequence mappings. Arcwright deterministically schedules invocations
and owns canonical narrative consequences. Arcwright-hosted games reuse the
Python runtime; external games may use a host-authoritative adapter.

**Tech stack:** Python 3.11, Pydantic, SQLAlchemy and Alembic, FastAPI,
TypeScript SDK, Nightcap web, JSON arc and package definitions, pytest,
node:test, Ruff, and existing roadmap and GitHub tooling.

**Design input:**
docs/superpowers/specs/2026-08-02-mini-game-platform-orchestration-design.md

**Proposed ADR:**
docs/decisions/0018-mini-game-orchestration-and-execution-adapters.md

---

## Execution Gate

This document authorizes planning only.

Before Task 1 begins, the founder must explicitly approve:

1. the architecture artifact version;
2. ADR 0018;
3. the canonical implementation specs created from this program;
4. the selected first implementation plan; and
5. implementation itself.

Approval of a plan, branch, PR, issue update, or prior direction does not imply
implementation approval.

## Program Order

| Order | Plan or workstream | Why it comes here | Completion gate |
| --- | --- | --- | --- |
| 0 | Mainline and tracker preflight | Prevent planning from building on stale or partial merges | Clean worktree at current origin/main, overlap report, founder go |
| 1 | Canonical reconciliation | Repair false and stale status before creating new work | Local and GitHub records agree |
| 2 | Contracts and adapters | Every game depends on invocation and consequence orchestration | Hosted and host-authoritative contract tests pass |
| 3 | Onboarding and certification | Reuse existing skill, script, template, and validators | Synthetic developer can reach a readiness report |
| 4 | Nightcap opportunity foundation | Connect generic contracts to Couch Race, Leverage, scoring, and theme | Six opportunities validate without package-specific engine logic |
| 5 | Tell Me Something True | Most complete mechanic, best migration canary | Game-ready report passes |
| 6 | Crime Scene Smash | Proves competitive real-time hosted mechanics | Game-ready report passes |
| 7 | Evidence Locker 402 | Proves individual selection and puzzle flow | Game-ready report passes |
| 8 | The Grill | Proves story-native, repeatable interrogation gameplay | Automatic Beat 3 path passes |
| 9 | Interrogation Room trivia | New content and adaptive mechanic after separate creative approval | Game-ready report passes |
| 10 | Couch Race end to end | Proves phones, TV, beats, multiplayer, reconnect, and story consequences | AW-286 rehearsal gates pass |
| 11 | Program closeout | Prevent stale plans, specs, epics, and issues | All status surfaces reconciled |

The final sixth-beat package placement is a creative decision. Six
opportunities do not require six unique packages.

## Task 0: Refresh Mainline and Verify Safety

**Files:** None.

**Step 1: Fetch current refs**

Run:

    git fetch origin --prune

**Step 2: Inspect merged work since this plan baseline**

Use GitHub and local Git to list every PR merged after commit
52562723d5dd6374817e1299f8faf98ecd5dd120. Inspect titles, base and head refs,
merge timestamps, changed files, and overlap with the selected plan.

**Step 3: Verify branch ancestry**

Run:

    git rev-parse HEAD
    git rev-parse origin/main
    git merge-base --is-ancestor origin/main HEAD
    git status --short --branch

Expected: the execution worktree is clean and based on the current origin/main.
If main advanced, rebase a clean plan branch or recreate the worktree. Never
overwrite or clean another agent's local changes.

**Step 4: Run baseline checks**

Run the focused suites named by the selected subsystem plan. Separate genuine
baseline failures from sandbox, database, or missing-dependency setup errors.

**Step 5: Report and pause**

Report merged PRs, head SHA, overlap, baseline results, and changed assumptions.
Pause for explicit founder implementation approval.

## Task 1: Reconcile Canonical and GitHub Status

**Files:**

- Modify: docs/product/aw285-discovery-and-checkpoints.md
- Modify: docs/roadmap/tasks/AW-285-couch-race-tv-and-phone-rendering.md
- Modify: docs/roadmap/tasks/AW-288-couch-race-mini-game-beat-coverage-and-tmst-acceleration.md
- Modify: docs/roadmap/tasks/AW-286-couch-race-rehearsal-slice-and-rehearsal-1-retarget.md
- Modify: docs/roadmap/epics/M4-E-nightcap-mini-game-interaction-layer.md
- Modify: docs/roadmap/epics/M5-F-tell-me-something-true-social-opener.md
- Modify: docs/roadmap/epics/M5-I-nightcap-couch-race-arc-and-interrogation.md
- Modify: docs/roadmap/index.json
- Modify or supersede: docs/specs/0051-aw-254-first-production-nightcap-mini-game.md
- Modify or supersede: docs/specs/0067-development-survey-and-path-to-first-playtest.md
- Modify: docs/specs/0072-nightcap-couch-race-v1.md
- Modify or supersede: docs/specs/0073-m5-canonical-reconciliation.md
- Modify: docs/roadmap/operations/human-collaboration-open-work.md
- Modify: docs/roadmap/milestones/M6-first-qualifying-sessions.md

**Step 1: Write failing consistency checks**

Add or extend roadmap validation so stale parent status, missing epic children,
missing GitHub mapping, and an issue marked complete while required criteria
remain open are reported.

**Step 2: Reconcile completed foundations**

- Mark M4-E complete with evidence for AW-249 through AW-253.
- Mark AW-287 complete with PR and verification evidence.
- Mark AW-262 through AW-265 complete consistently.
- Supersede obsolete AW-254 and spec 0051 scope while carrying its unproven
  real-device gate into AW-285 and AW-286.

**Step 3: Repair AW-285 status**

- Record PR #269 as Phase 1 structural completion only.
- Record that PR #271 was reverted by PR #272 and its CI protection is absent.
- Reopen GitHub issue #239.
- Update #239 and the canonical task so Phase 2 phone, audiovisual, room-watch,
  privacy, real-device, and integration criteria remain open.
- Create a canonical docs/specs AW-285 contract from the approved design
  evidence before Phase 2 implementation.

**Step 4: Resolve AW-288 and AW-266 authority conflict**

Present one focused founder decision before mutation:

- recommended: D-079 controls, AW-266 is superseded by integrated Couch Race
  rehearsal evidence;
- alternative: preserve a separate TMST-focused human session as a later
  evidence task.

After confirmation:

- reduce AW-288 to TMST activation, placement, and pacing integration;
- remove beat coverage moved by D-095;
- create the missing AW-288 GitHub issue;
- close or rescope AW-266 and issue #183 exactly as approved.

**Step 5: Synchronize M5-I and AW-286**

Give the epic, parent spec, roadmap manifest, and GitHub issue #234 one
authoritative child list. Make AW-286 the integrated rehearsal gate for all
required minigame, narrative, visual, and device work.

**Step 6: Reconcile M5-G and M6**

- Add AW-275 to M5-G and issue #187.
- Keep AW-268 as asset and motion execution against spec 0069.
- Correct obsolete M6 pivot and player-count references.
- Add explicit Couch Race readiness before the final rehearsal.

**Step 7: Verify**

Run:

    python -m json.tool docs/roadmap/index.json
    git diff --check

Run the repository's roadmap validation command if present. Fetch every mutated
GitHub issue and compare title, state, body, labels, dependencies, and local
status.

**Step 8: Commit**

    git add docs/product docs/roadmap docs/specs
    git commit -m "docs(nightcap): reconcile minigame program status"

## Task 2: Approve Canonical Contract Specs

**Files:**

- Create: docs/specs/0077-mini-game-registration-and-story-opportunities.md
- Create: docs/specs/0078-mini-game-invocation-and-execution-adapters.md
- Create: docs/specs/0079-mini-game-result-consequences-and-theme.md
- Create: docs/specs/0080-mini-game-onboarding-preview-and-certification.md
- Modify: docs/decisions/0018-mini-game-orchestration-and-execution-adapters.md
- Modify: docs/decisions/0009-mini-game-runtime-boundary.md
- Modify: docs/decisions/README.md
- Modify: docs/architecture/03-arc-execution.md
- Modify: docs/architecture/09-developer-api.md
- Modify: docs/architecture/14-architecture-validation.md

**Step 1: Split the approved design into four implementation contracts**

Each spec must define ownership, schemas, invariants, compatibility, API or SDK
surfaces, tests, migration impact, telemetry, error behavior, and explicit
non-goals.

**Step 2: Preserve hosted compatibility**

Specs 0046 through 0050 remain historical foundations for arcwright_hosted.
Add references without rewriting their original acceptance history.

**Step 3: Validate future engines**

Every contract must be walked against:

- Nightcap hosted web;
- a synthetic non-Nightcap host-authoritative game;
- Unity-style launch and result handoff;
- an emergent arc with no fixed beat count.

**Step 4: Founder review**

Present schemas, example flows, failure scenarios, and compatibility impact.
Obtain separate explicit approval for each spec and ADR 0018.

**Step 5: Commit**

    git add docs/specs docs/decisions docs/architecture
    git commit -m "docs(arc): specify minigame orchestration contracts"

## Task 3: Execute the Contract and Adapter Plan

Use the separate detailed plan:

    docs/superpowers/plans/2026-08-02-mini-game-contracts-and-adapters.md

Required outcome:

- registration and opportunity models;
- deterministic selection;
- shared invocation lifecycle;
- arcwright_hosted compatibility adapter;
- host_authoritative adapter;
- result validation;
- declarative consequence mapping;
- API and SDK transport;
- migration and replay compatibility;
- synthetic non-Nightcap proof.

Pause after contract-only tests before Nightcap integration.

## Task 4: Execute the Onboarding and Certification Plan

Use the separate detailed plan:

    docs/superpowers/plans/2026-08-02-mini-game-onboarding-and-certification.md

Required outcome:

- existing skill and script updated, not duplicated;
- package, registration, and opportunity scaffolding;
- import and compatibility diagnostics;
- deterministic preview and simulation;
- theme and privacy validation;
- machine-readable readiness report;
- promotion blocked until required evidence passes.

## Task 5: Execute the Nightcap Foundation Plan

Use the separate detailed plan:

    docs/superpowers/plans/2026-08-02-nightcap-mini-game-foundation.md

Required outcome:

- six Couch Race opportunities;
- generic Leverage and race-score consequence mappings;
- Nightcap semantic theme contract;
- invocation launch from arc progression;
- timeout driver;
- player-count eligibility;
- phone, shared-display, and host stage bootstrap;
- no currency-funded optional Grill behavior.

## Task 6: Execute Individual Game-ready Plans

Write and approve one canonical game spec and one implementation plan per game
before changing its gameplay or presentation.

Execute in this order:

1. Tell Me Something True.
2. Crime Scene Smash.
3. Evidence Locker 402.
4. The Grill.
5. Interrogation Room trivia.

Each plan must include:

- mechanic tests first;
- package schema and lifecycle correction;
- renderer and theme implementation;
- privacy and reconnect;
- player-count behavior;
- deterministic consequence mapping;
- performance and accessibility;
- gameplay artifact review;
- real-device walkthrough;
- real-human rehearsal;
- readiness report;
- issue and local status reconciliation.

Do not promote a package merely because automated checks pass. Subjective
gameplay, visual, animation, graphics, and session-fit gates require founder
review.

## Task 7: Run End-to-end Certification

**Files:**

- Modify: engine/tests/test_couch_race_harness.py
- Modify: engine/tests/test_couch_race_arc_json.py
- Modify: api/tests/test_mini_games_api.py
- Modify: nightcap-web/tests/mini-game-privacy-matrix.test.ts
- Modify: nightcap-web/tests/mini-game-stage.test.ts
- Modify: docs/roadmap/operations/rehearsal-1-runbook.md
- Modify: docs/roadmap/operations/rehearsal-1-blocker-log.md
- Create: docs/roadmap/operations/minigame-readiness-report.json

**Step 1: Headless deterministic session**

Run 2-player and 8-player Couch Race sessions through all six opportunities.
Verify selection, invocation, consequences, fallback, repeat policy,
pause/resume, reconnect, and deterministic replay.

**Step 2: Host-authoritative synthetic session**

Run a non-Nightcap experience through registration, opportunity selection,
launch, result receipt, consequence application, and replay without importing
host gameplay code.

**Step 3: Real-device preflight**

Verify phone, shared display, host controls, privacy, stage bootstrap,
disconnect, refresh, and timeout recovery.

**Step 4: Founder walkthrough**

Pause for artifact and readiness approval before a real-player session.

**Step 5: Real-player rehearsal**

Run AW-286 using the collaboration contract. Record game-specific fun,
seamlessness, story enhancement, competition, style, motion, and confusion
findings.

**Step 6: Remediation**

Open or update only evidence-backed issues. Do not close AW-286 or promote
games while blocking findings remain.

## Task 8: Reconcile Every Status Surface

**Files:** All related plan, spec, roadmap, operations, and decision artifacts.

**Step 1: Build the closeout matrix**

For every affected artifact record:

- intended final status;
- evidence;
- local path or GitHub URL;
- owner;
- close, update, supersede, or leave-open action.

**Step 2: Update local records**

Update all completed plan tasks, canonical spec status, roadmap task and epic
status, roadmap index entries, milestone gates, decision indexes, discovery
logs, and rehearsal evidence.

**Step 3: Update GitHub**

Update issue bodies and checklists, dependencies, labels, epic issue, and
milestone only where evidence supports it. Close a game issue only after its
game-ready report and required human gates pass.

**Step 4: Verify bidirectionally**

Fetch the mutated GitHub records and compare them with local canonical truth.
Run:

    git diff --check
    git status --short

Run all focused and full checks required by the completed subsystem plans.

**Step 5: Commit**

    git add docs
    git commit -m "docs(nightcap): close minigame readiness program"

**Step 6: Final founder sign-off**

Present:

- active game inventory;
- six-beat opportunity coverage;
- test and rehearsal evidence;
- remaining non-blocking issues;
- all closed, updated, superseded, and still-open artifacts.

Only after this sign-off may the program be called complete. D-097's optional
currency-funded Grill mechanic becomes eligible for a new design interview,
not automatic implementation.
