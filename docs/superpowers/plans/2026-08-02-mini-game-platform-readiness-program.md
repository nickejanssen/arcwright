# Mini-game Platform and Nightcap Readiness Program Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make every known Nightcap mini-game game-ready, provide one valid mini-game opportunity per Couch Race beat, and prove the same Arcwright orchestration contracts with a synthetic non-Nightcap host.

**Architecture:** Arcwright imports or scaffolds a reusable browser mini-game,
creates non-destructive destination adaptations, and executes composable
designer-owned placement policies. Hosting, execution, result authority,
presentation, and distribution negotiate independently. The first vertical
slice proves the 10-to-15-minute browser golden path before the contracts are
generalized. This file controls sequencing and evidence gates while linked
subsystem plans contain implementation details.

**Tech Stack:** Python 3.11, Pydantic, SQLAlchemy, Alembic, FastAPI, TypeScript, Node test runner, Nightcap web, JSON, pytest, Ruff, Git, GitHub CLI.

## Global Constraints

- This plan is planning-only until the founder separately approves implementation.
- Start every executable plan from a clean worktree based on current `origin/main`.
- Inspect every pull request merged after refreshed planning baseline
  `d26d7b8dee2aafa59ef6a0fd985da5bea771dbf1` before implementation.
- Python 3.11 or newer owns deterministic arc execution and canonical state.
- TypeScript renders authorized state and submits input; it does not own arc execution.
- No provider or model name may appear outside `config/routing_table.json` and `engine/routing/router.py`.
- Knowledge queries and engine safety layers remain mandatory for AI character content.
- Do not add dependencies, migrations, cross-module changes, prompts, eval changes, secrets, or auth behavior without the approvals required by `AGENTS.md`.
- Do not implement the D-097 currency-funded player-requested Grill flow.
- Meet the first-time Playtest-ready target of 10 to 15 minutes, 20 minutes
  maximum, and returning target of 5 to 10 minutes, 15 minutes maximum.
- Managed browser hosting is the default; external browser hosting uses the
  same protocol.
- Never overwrite imported source. Generated adaptations are versioned,
  permission-first, reviewable, and reversible.
- Preview-only browser results cannot mutate production canonical state.
- Do not create a public marketplace, arbitrary code loader, Unity or Unreal SDK, billing system, or public third-party authentication in Horizon 1.
- Preserve unrelated and agent-local files. Never stage `.claude/`, `.codex/`, `.cursor/`, or equivalent local state.

---

## Program Map

| Order | Execution plan | Independently testable result |
| --- | --- | --- |
| 0 | This program, ADR 0018, specs 0076 through 0086, and the closeout matrix | Approved architecture and current-mainline scope with no duplicated Scene Sweep or AW-285 work |
| 1 | `2026-08-03-browser-minigame-golden-path.md` | Tell Me Something True reaches local Playtest-ready through the same measured destination-first browser flow offered to an external developer |
| 2 | `2026-08-03-minigame-capability-and-trust-platform.md` | Reusable packages, adaptations, placement policies, profile negotiation, authority proofs, consequences, and synthetic future-profile proof |
| 3 | `2026-08-03-minigame-creator-and-readiness-labs.md` | Permission-first adaptation, local playtest lab, visual production lab, shared Studio/CLI/SDK APIs, and independent developer usability proof |
| 4 | `2026-08-02-tell-me-something-true-game-ready.md` | Production-ready social truth/bluff Nightcap adaptation and human evidence after the canary |
| 5 | `2026-08-02-crime-scene-smash-game-ready.md` | Playtest-ready competitive match-3 adaptation and Scene rotation evidence |
| 6 | `2026-08-03-scene-sweep-game-ready.md` | Merged Scene Sweep backend gains its renderer, Nightcap adaptation, Scene rotation, and readiness evidence without backend duplication |
| 7 | `2026-08-02-evidence-locker-402-game-ready.md` | Playtest-ready selected-player puzzle adaptation and spectator evidence |
| 8 | `2026-08-02-the-grill-game-ready.md` | Playtest-ready automatic Beat 3 interrogation adaptation with deferred request seam |
| 9 | `2026-08-02-interrogation-room-trivia-game-ready.md` | Playtest-ready Last Call pressure-capstone package after creative approval |
| 10 | `2026-08-02-the-unmasking-game-ready.md` | Playtest-ready Truth reveal-reconstruction package, score animation, and podium |
| 11 | `2026-08-02-nightcap-mini-game-foundation.md` | Six composable placement policies, seven initial candidates, production bootstrap, and generic consequences |
| 12 | `2026-08-02-nightcap-existing-minigames-game-ready.md` | Production-ready adaptations, six-beat integration, device and real-player rehearsal, status reconciliation, and final sign-off |

The six Couch Race beats require six placement policies and allow additional
certified candidates to rotate through each authored role. Scene initially
contains Crime Scene Smash and Scene Sweep. These are candidate pools, not
permanent one-package beat bindings.

### Task 1: Refresh Mainline and Produce a Safety Report

**Files:**

- Read: `docs/superpowers/plans/2026-08-02-mini-game-platform-readiness-program.md`
- Read: `.git` refs and worktree metadata
- Read: GitHub pull requests merged after baseline commit
- Create: `docs/product/mini-game-readiness/mainline-safety-report.md`

**Interfaces:**

- Consumes: baseline SHA `d26d7b8dee2aafa59ef6a0fd985da5bea771dbf1` and the selected execution-plan file list.
- Produces: `PreflightReport { origin_main_sha, merged_prs, overlapping_files, worktree_clean, baseline_checks, changed_assumptions }` plus a founder go or stop decision.

- [ ] **Step 1: Fetch current refs without changing files**

```powershell
git fetch origin --prune
```

Expected: exit 0 and current `origin/main` available locally.

- [ ] **Step 2: List merged pull requests since the planning baseline**

```powershell
gh pr list --state merged --base main --search "merged:>=2026-08-03" --json number,title,mergedAt,mergeCommit,headRefName,baseRefName,url
```

Expected: JSON containing every same-day merge, including reverts.

- [ ] **Step 3: Compare changed files with the selected plan**

```powershell
git diff --name-only d26d7b8dee2aafa59ef6a0fd985da5bea771dbf1..origin/main
git status --short --branch
git merge-base --is-ancestor origin/main HEAD
```

Expected: a clean worktree and exit 0 from the ancestry check. If main advanced,
rebase a clean planning branch or recreate the execution worktree before any
implementation.

- [ ] **Step 4: Run the selected plan's baseline commands**

Use the exact commands in that plan's first task. Record each result as
`PASS`, `FAIL_BASELINE`, or `BLOCKED_ENVIRONMENT`; do not describe an unrun
check as passing.

- [ ] **Step 5: Present the report and stop**

Expected: explicit founder implementation approval is required after reviewing
the current SHA, merged PRs, overlap, and baseline results.

### Task 2: Reconcile Canonical and GitHub Authority

**Files:**

- Modify: `docs/product/aw285-discovery-and-checkpoints.md`
- Modify: `docs/roadmap/tasks/AW-285-couch-race-tv-and-phone-rendering.md`
- Modify: `docs/roadmap/tasks/AW-286-couch-race-rehearsal-slice-and-rehearsal-1-retarget.md`
- Modify: `docs/roadmap/tasks/AW-288-couch-race-mini-game-beat-coverage-and-tmst-acceleration.md`
- Modify: `docs/roadmap/epics/M4-E-nightcap-mini-game-interaction-layer.md`
- Modify: `docs/roadmap/epics/M5-F-tell-me-something-true-social-opener.md`
- Modify: `docs/roadmap/epics/M5-I-nightcap-couch-race-arc-and-interrogation.md`
- Modify: `docs/roadmap/milestones/M6-first-qualifying-sessions.md`
- Modify: `docs/roadmap/index.json`
- Modify: GitHub issues `#223`, `#228`, `#234`, `#240`, and `#258` only after
  their local canonical records are correct
- Read only unless independent scope changes: GitHub issues `#183`, `#187`,
  `#239`, `#254`, and `#270`

**Interfaces:**

- Consumes: verified merged-PR evidence and canonical status hierarchy from `docs/README.md`.
- Produces: one `ArtifactCloseoutMatrix` row per affected spec, plan, task, epic, milestone, issue, and PR with `action`, `evidence`, `final_status`, and `remaining_gate`.

- [ ] **Step 1: Add a failing roadmap consistency fixture**

```python
def test_minigame_parent_status_matches_children(roadmap_index):
    assert roadmap_index.task("AW-287").status == "Complete"
    assert "AW-287" in roadmap_index.epic("M5-I").children
```

Place the assertion in the repository's roadmap validation test discovered by:

```powershell
rg -n "roadmap.*index|parent.*children|GitHub issue" tests engine/tests docs -g "*.py"
```

- [ ] **Step 2: Run the focused consistency test and confirm failure**

Run the exact discovered test path with `pytest -q`.

Expected: failure naming the stale parent or missing child before documentation
changes.

- [ ] **Step 3: Apply the evidence-backed status corrections**

Record these exact outcomes:

```text
M4-E: Complete with AW-249 through AW-253 evidence
AW-287: Complete with merged implementation evidence
AW-254/spec 0051: Superseded, real-device gate carried into AW-285/AW-286
AW-285/#239: merged work complete to the ticket's accepted scope, subject to fresh GitHub checklist readback
Issue #270: separate blocked restoration of reverted embedded-script CI coverage; do not silently reopen or duplicate AW-285
AW-288: Reduced to TMST activation, placement, and pacing integration
AW-286: Integrated minigame and device rehearsal gate
M5-I: One authoritative child list including AW-287 through AW-292
M6: Correct current Couch Race dependency and player-count language
AW-275/#223: shared experience-design-system dependency, not one-off game CSS
AW-278/#228: align Truth reveal accounting with spec 0085, not a parallel system
AW-286/#240: preserve as final live-operation and blocker-log gate
Issue #254: remain deferred until AW-286 tie-frequency evidence
PRs #273/#274: authoritative Scene Sweep baseline; do not duplicate backend or design
```

Do not change AW-266 or issue #183 until the founder chooses whether integrated
Couch Race evidence supersedes the separate TMST rehearsal.

- [ ] **Step 4: Validate local records**

```powershell
python -m json.tool docs/roadmap/index.json
git diff --check
```

Expected: both commands exit 0.

- [ ] **Step 5: Update GitHub from canonical truth and read it back**

Use `gh issue edit` only for approved rows in `ArtifactCloseoutMatrix`, then run:

```powershell
gh issue view 239 --json number,title,state,body,labels,milestone,url
gh issue view 258 --json number,title,state,body,labels,milestone,url
```

Expected: GitHub state matches the local task and spec status exactly.

- [ ] **Step 6: Commit the reconciliation**

```powershell
git add docs/product docs/roadmap docs/specs
git commit -m "docs(nightcap): reconcile minigame program status"
```

### Task 3: Reserve and Approve Canonical Specs

**Files:**

- Verify: `docs/specs/0077-mini-game-registration-and-story-opportunities.md`
- Verify: `docs/specs/0078-mini-game-invocation-and-execution-adapters.md`
- Verify: `docs/specs/0079-mini-game-results-consequences-theme-and-telemetry.md`
- Verify: `docs/specs/0080-mini-game-onboarding-preview-and-certification.md`
- Modify: `docs/specs/0076-aw-289-interrogation-room.md`
- Modify as each creative gate closes: `docs/specs/0081-tell-me-something-true-game-ready.md`
- Modify as each creative gate closes: `docs/specs/0082-crime-scene-smash-game-ready.md`
- Modify as each creative gate closes: `docs/specs/0083-evidence-locker-402-game-ready.md`
- Modify as each creative gate closes: `docs/specs/0084-the-grill-interrogation-minigame.md`
- Modify as each creative gate closes: `docs/specs/0085-the-unmasking-reveal-reconstruction.md`
- Modify as each creative gate closes: `docs/specs/0086-scene-sweep-game-ready.md`
- Modify: `docs/decisions/0018-mini-game-orchestration-and-execution-adapters.md`
- Modify: `docs/architecture/03-arc-execution.md`
- Modify: `docs/architecture/09-developer-api.md`
- Modify: `docs/architecture/14-architecture-validation.md`

**Interfaces:**

- Consumes: founder-approved orchestration design v0.3 and ADR 0018.
- Produces: four approved platform specs plus seven game-specific specs that
  retain their explicit creative and production gates.

- [ ] **Step 1: Verify the canonical spec packet exists once**

```powershell
rg --files docs/specs | Sort-Object | Select-Object -Last 12
```

Expected: exactly one canonical file exists for each spec number 0076 through
0086 and every cross-reference resolves.

- [ ] **Step 2: Verify platform approval and preserve game gates**

Specs 0077 through 0080 must report `Status: Approved`, approval date
2026-08-03, and the separate implementation go-ahead. Specs 0076 and 0081
through 0086 remain Draft until their own gameplay, presentation, tuning, or
production decisions are explicitly approved.

- [ ] **Step 3: Run architecture and placeholder checks**

```powershell
rg -n "TBD|TODO|implement later|fill in details" docs/specs --glob "0076-*.md" --glob "0077-*.md" --glob "0078-*.md" --glob "0079-*.md" --glob "0080-*.md" --glob "0081-*.md" --glob "0082-*.md" --glob "0083-*.md" --glob "0084-*.md" --glob "0085-*.md" --glob "0086-*.md"
git diff --check
```

Expected: no placeholder matches and clean diff output.

- [ ] **Step 4: Present only unresolved game-specific decisions**

Do not reopen the approved platform contracts unless implementation evidence
finds a contradiction. Present each game's unresolved gameplay, presentation,
tuning, real-device, real-player, and production decisions at that plan's
named gate. Do not approve all game-specific specs as a batch.

- [ ] **Step 5: Commit the approved platform packet and gated game specs**

```powershell
git add docs/specs docs/decisions docs/architecture
git commit -m "docs(arc): specify minigame orchestration contracts"
```

### Task 4: Execute and Gate the Subsystem Plans

**Files:**

- Read: `docs/superpowers/plans/2026-08-03-browser-minigame-golden-path.md`
- Read: `docs/superpowers/plans/2026-08-03-minigame-capability-and-trust-platform.md`
- Read: `docs/superpowers/plans/2026-08-03-minigame-creator-and-readiness-labs.md`
- Read: `docs/superpowers/plans/2026-08-02-tell-me-something-true-game-ready.md`
- Read: `docs/superpowers/plans/2026-08-02-crime-scene-smash-game-ready.md`
- Read: `docs/superpowers/plans/2026-08-03-scene-sweep-game-ready.md`
- Read: `docs/superpowers/plans/2026-08-02-evidence-locker-402-game-ready.md`
- Read: `docs/superpowers/plans/2026-08-02-the-grill-game-ready.md`
- Read: `docs/superpowers/plans/2026-08-02-interrogation-room-trivia-game-ready.md`
- Read: `docs/superpowers/plans/2026-08-02-the-unmasking-game-ready.md`
- Read: `docs/superpowers/plans/2026-08-02-nightcap-mini-game-foundation.md`
- Read: `docs/superpowers/plans/2026-08-02-nightcap-existing-minigames-game-ready.md`
- Modify: `docs/superpowers/plans/2026-08-02-mini-game-platform-readiness-program.md`

**Interfaces:**

- Consumes: approved specs 0076 through 0086 and each plan's explicit founder implementation approval.
- Produces: one reviewed commit series and completion-evidence block per independently testable plan.

- [ ] **Step 1: Execute plans in Program Map order**

For each plan, run its preflight, TDD tasks, focused checks, review checkpoint,
and status reconciliation before beginning the next plan.

- [ ] **Step 2: Record each checkpoint**

Use this exact evidence shape in this file:

```markdown
- Plan: docs/superpowers/plans/2026-08-03-browser-minigame-golden-path.md
  Commit: Not created
  Focused checks: Not run
  Human gates: Implementation approval not granted
  GitHub records: No execution updates made
  Remaining blockers: Fresh-main audit and founder implementation approval
```

Copy this block once per Program Map row and replace every value with observed
evidence as that plan executes.

- [ ] **Step 3: Stop on a failed gate**

Do not continue to a dependent plan when contract tests, certification,
creative approval, real-device evidence, or real-player evidence is missing.

### Task 5: Close the Program

### Execution Checkpoints

- Plan: `docs/superpowers/plans/2026-08-03-browser-minigame-golden-path.md`
  Commit: `d435bf9`, `2a0906e273ff70f057518cc3dbb06bb533a621dd`,
  `5e50f10c07b7b3f705c6255be54708f459079efe`,
  `fa0878ae2431161215dcf53d4470287af2477bbe`, `315a1e0`, `775c63e`
  Focused checks: Python onboarding/helper tests passed, Nightcap web
  typecheck passed, Nightcap web suite passed, TMST package validation passed
  Human gates: First-time developer session not run; returning user session not run
  GitHub records: No execution updates made in this slice
  Remaining blockers: Human timing and comprehension evidence required before
  generalizing the browser golden path

Decision: `REVISE` for the browser golden path. The internal walking skeleton
reaches local Playtest-ready with preview-only evidence, but the human
developer proof required by the plan is still missing.

**Files:**

- Modify: `docs/superpowers/plans/2026-08-02-mini-game-platform-readiness-program.md`
- Modify: `docs/product/mini-game-readiness/couch-race-program-status.json`
- Modify: `docs/product/decisions-log.csv`
- Modify: `docs/roadmap/index.json`
- Modify: `docs/roadmap/operations/rehearsal-1-blocker-log.md`
- Modify: `docs/roadmap/tasks/AW-286-couch-race-rehearsal-slice-and-rehearsal-1-retarget.md`
- Modify: `docs/roadmap/epics/M5-I-nightcap-couch-race-arc-and-interrogation.md`
- Modify: `docs/roadmap/milestones/M6-first-qualifying-sessions.md`

**Interfaces:**

- Consumes: six game readiness reports, six-opportunity Couch Race report, synthetic host report, AW-286 rehearsal evidence, and `ArtifactCloseoutMatrix`.
- Produces: one final inventory with package, automated, device, human, and founder status reported separately.

- [ ] **Step 1: Verify the required evidence files exist and pass schema validation**

```powershell
python -m json.tool docs/product/mini-game-readiness/couch-race-program-status.json
python -m json.tool docs/roadmap/index.json
git diff --check
```

Expected: all commands exit 0.

- [ ] **Step 2: Read back every mutated GitHub issue**

```powershell
gh issue list --state all --search "minigame OR mini-game" --json number,title,state,labels,milestone,url
```

Expected: no local `Complete` record points to an open blocking checklist and
no closed issue retains unmet game-ready acceptance criteria.

- [ ] **Step 3: Present final founder sign-off evidence**

Report package active status, automated certification, real-device status,
real-player status, founder sign-off, and non-blocking follow-ups separately.

- [ ] **Step 4: Commit final status reconciliation**

```powershell
git add docs
git commit -m "docs(nightcap): close minigame readiness program"
```

The D-097 optional currency-funded Grill mechanic becomes eligible for a new
design interview only after this program is explicitly signed off. It is not
part of this implementation plan.
