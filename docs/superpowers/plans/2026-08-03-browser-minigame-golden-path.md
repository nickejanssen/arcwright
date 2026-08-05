# Browser Mini-game Golden Path Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove that Tell Me Something True can move from an existing browser-capable package to a destination-fitted, locally Playtest-ready Nightcap adaptation through one measured workflow that a first-time external browser developer can understand.

**Architecture:** Build a narrow walking skeleton through the approved package, adaptation, permission, readiness, and preview contracts. Extend the existing `arcwright-minigame` skill and helper. Do not create a second package format, CLI, renderer registry, or readiness model. This slice uses a local authoring workspace and preview-only authority. The capability and trust plan generalizes and persists the same artifacts after this canary proves the developer flow.

**Tech Stack:** Python 3.11, Pydantic 2, argparse, TypeScript, Node.js, esbuild, happy-dom, pytest, Ruff.

## Global Constraints

- Required approved specs: `docs/specs/0077-mini-game-registration-and-story-opportunities.md` through `docs/specs/0080-mini-game-onboarding-preview-and-certification.md`.
- Required game spec: `docs/specs/0081-tell-me-something-true-game-ready.md` remains a separate creative and production gate.
- Stop before source changes until the founder gives the separate implementation go-ahead.
- Never overwrite imported source or an existing versioned definition.
- Preview-only results use a simulation ledger and cannot change score, Leverage, evidence, knowledge, winners, or story state.
- Use the existing `docs/skills/arcwright-minigame/scripts/minigame_tool.py`, package loader, renderer discovery, mini-game kit, and Nightcap web runtime.
- Ask before generating code, art, animation, audio, copy, or configuration. Record the answer in a `GenerationPermissionReceipt`.
- The golden path must expose advanced structured artifacts without requiring the developer to edit them.
- No new dependency, migration, authentication behavior, or cloud deployment is part of this plan.
- Preserve D-097: do not implement currency-funded player requests.

---

### Task 1: Refresh Mainline, Run the Focused Baseline, and Stop for Approval

**Files:**

- Read: `docs/product/mini-game-readiness/mainline-safety-report.md`
- Read: `docs/specs/0077-mini-game-registration-and-story-opportunities.md`
- Read: `docs/specs/0080-mini-game-onboarding-preview-and-certification.md`
- Read: `docs/specs/0081-tell-me-something-true-game-ready.md`
- Modify after verification: `docs/product/mini-game-readiness/mainline-safety-report.md`

**Interfaces:**

- Consumes: latest `origin/main`, merged PRs, and current canary files.
- Produces: a current `PreflightReport` with overlap, baseline, and go or stop status.

- [ ] **Step 1: Refresh and compare main**

```powershell
git fetch origin --prune
gh pr list --state merged --base main --search "merged:>=2026-08-03" --json number,title,mergedAt,mergeCommit,headRefName,baseRefName,url
git diff --name-status d26d7b8dee2aafa59ef6a0fd985da5bea771dbf1..origin/main
git status --short --branch
```

Expected: the execution worktree is clean and any change to the plan's files is reviewed before continuing.

- [ ] **Step 2: Run the focused baseline with a writable temp directory**

```powershell
$env:TMPDIR = (Resolve-Path .).Path + "\.pytest-baseline"
python -m pytest engine/tests/test_mini_game_models.py engine/tests/test_social_truth_bluff_runtime.py api/tests/test_mini_games_api.py -q --basetemp .pytest-baseline
npm --prefix nightcap-web test
```

Expected: product failures are zero. Record permission or environment failures separately and remove only the verified worktree-local temporary directory.

- [ ] **Step 3: Stop for the implementation go-ahead**

Expected: no source file below is changed until the founder reviews the refreshed report and explicitly approves implementation.

### Task 2: Characterize the Existing Workflow and Lock the Canary Contract

**Files:**

- Modify: `docs/skills/arcwright-minigame/SKILL.md`
- Create: `engine/tests/fixtures/browser_minigames/tmst-canary/index.html`
- Create: `engine/tests/fixtures/browser_minigames/tmst-canary/game.js`
- Create: `engine/tests/test_mini_game_onboarding.py`
- Create: `docs/product/mini-game-readiness/tmst-golden-path-fixture.json`

**Interfaces:**

- Consumes: one self-contained browser bundle and the existing TMST package.
- Produces: a deterministic fixture plus a locked list of required confirmations, permissions, artifacts, and readiness evidence.

- [ ] **Step 1: Write the failing workflow characterization test**

```python
def test_tmst_canary_requires_one_destination_and_only_high_impact_questions(
    onboarding_service,
    tmst_browser_source,
):
    analysis = onboarding_service.analyze(
        source=tmst_browser_source,
        destination_game_id="nightcap-couch-race-v1",
    )
    assert analysis.recommended_path == "destination_first"
    assert analysis.destination_game_id == "nightcap-couch-race-v1"
    assert {item.key for item in analysis.confirmations} == {
        "story_affordance",
        "participation_model",
        "result_meaning",
        "placement_authority",
    }
```

- [ ] **Step 2: Run the test and confirm the missing authoring service**

```powershell
python -m pytest engine/tests/test_mini_game_onboarding.py -q
```

Expected: import failure for `engine.mini_games.authoring`.

- [ ] **Step 3: Create a dependency-free canary bundle**

The fixture must expose start, input, finish, reset, and result events through a small browser bridge. It must not calculate an authoritative winner or mutate Nightcap state. Keep the fixture free of Nightcap names so later usability tests can reuse it.

- [ ] **Step 4: Update the existing skill's capability inventory**

Correct the stale statement that runtime, API, SDK, and rendering are unbuilt. Describe the current package loader, runtime, API, SDK, renderer kit, Scene Sweep backend, and the new readiness workflow without duplicating canonical architecture text.

- [ ] **Step 5: Run and commit the characterization**

```powershell
python -m pytest engine/tests/test_mini_game_onboarding.py -q
git add docs/skills/arcwright-minigame/SKILL.md engine/tests/fixtures/browser_minigames engine/tests/test_mini_game_onboarding.py docs/product/mini-game-readiness/tmst-golden-path-fixture.json
git commit -m "test(config): lock browser minigame golden path"
```

### Task 3: Add the Local Authoring Session and Source-preserving Workspace

**Files:**

- Create: `engine/mini_games/authoring/__init__.py`
- Create: `engine/mini_games/authoring/models.py`
- Create: `engine/mini_games/authoring/workspace.py`
- Create: `engine/mini_games/authoring/service.py`
- Modify: `engine/mini_games/__init__.py`
- Modify: `engine/tests/test_mini_game_onboarding.py`

**Interfaces:**

- Consumes: `BrowserImportSource`, destination ID, explicit workspace path, and user confirmations.
- Produces: `MiniGameOnboardingSession`, source fingerprint, analysis, proposed package, proposed adaptation, permission receipt, and readiness report.

- [ ] **Step 1: Add failing source-preservation and resume tests**

```python
def test_import_copies_to_private_workspace_and_preserves_source(onboarding_service):
    before = sha256_tree(SOURCE)
    session = onboarding_service.start(REQUEST, workspace_root=WORKSPACE)
    assert sha256_tree(SOURCE) == before
    assert session.original_source_unchanged is True
    assert session.state == "imported"


def test_onboarding_session_resumes_from_versioned_artifacts(onboarding_service):
    first = onboarding_service.start(REQUEST, workspace_root=WORKSPACE)
    resumed = onboarding_service.load(first.session_id, workspace_root=WORKSPACE)
    assert resumed == first
```

- [ ] **Step 2: Define the canary subset using approved spec types**

Implement `BrowserImportSource`, `MiniGameOnboardingRequest`, `OnboardingConfirmation`, `OnboardingAnalysis`, `GenerationPermissionReceipt`, `ReadinessEvidence`, `MiniGameReadinessReport`, and `MiniGameOnboardingSession`. Re-export the exact shared types rather than creating canary-only equivalents.

- [ ] **Step 3: Implement an explicit local workspace boundary**

```python
class LocalAuthoringWorkspace:
    def create(self, request: MiniGameOnboardingRequest, root: Path) -> MiniGameOnboardingSession: ...
    def load(self, session_id: UUID, root: Path) -> MiniGameOnboardingSession: ...
    def save(self, session: MiniGameOnboardingSession, root: Path) -> None: ...
```

Reject a workspace inside imported source, a path escape, symlink escape, duplicate session ID, or overwrite of a confirmed artifact. Use atomic replace for metadata files. Never place private import contents in telemetry or tracked readiness evidence.

- [ ] **Step 4: Implement deterministic analysis with uncertainty**

The canary analyzer may inspect HTML, JavaScript, assets, and bridge events. It must emit evidence and uncertainty, not claim to understand hidden gameplay intent. High-impact fields remain confirmations even when inferred.

- [ ] **Step 5: Run and commit**

```powershell
python -m pytest engine/tests/test_mini_game_onboarding.py -q
python -m ruff check engine/mini_games/authoring
python -m ruff format --check engine/mini_games/authoring
git add engine/mini_games/authoring engine/mini_games/__init__.py engine/tests/test_mini_game_onboarding.py
git commit -m "feat(config): add minigame authoring sessions"
```

### Task 4: Extend the Existing Helper into One Guided Command

**Files:**

- Modify: `docs/skills/arcwright-minigame/scripts/minigame_tool.py`
- Create: `engine/tests/test_minigame_tool.py`
- Modify: `docs/skills/arcwright-minigame/SKILL.md`

**Interfaces:**

- Consumes: `onboard-browser SOURCE --destination GAME --workspace PATH`.
- Produces: resumable session ID, plain-language questions, permission prompt, adaptation alternatives, next action, and machine-readable `--json` output.

- [ ] **Step 1: Add failing CLI tests**

```python
def test_onboard_browser_defaults_to_managed_destination_first(run_tool):
    result = run_tool("onboard-browser", SOURCE, "--destination", "nightcap-couch-race-v1", "--workspace", WORKSPACE, "--json")
    assert result.returncode == 0
    assert result.json["hosting_preference"] == "managed"
    assert result.json["recommended_path"] == "destination_first"


def test_generation_requires_explicit_permission(run_tool):
    result = run_tool("onboard-browser", SOURCE, "--destination", "nightcap-couch-race-v1", "--workspace", WORKSPACE, "--non-interactive")
    assert result.returncode == 2
    assert "generation permission required" in result.stderr
```

- [ ] **Step 2: Add `onboard-browser`, `resume`, and `status` subcommands**

Keep `scaffold` and `validate` compatible. Interactive mode asks one focused question at a time. Non-interactive mode accepts a versioned answer file and fails on missing high-impact confirmations or permissions.

- [ ] **Step 3: Display progressive state plainly**

Every response must show `Imported`, `Reusable`, `Playtest-ready`, or `Production-ready`, why the state applies, blockers, and the smallest next action. Do not use color as the only signal.

- [ ] **Step 4: Run and commit**

```powershell
python -m pytest engine/tests/test_minigame_tool.py engine/tests/test_mini_game_onboarding.py -q
python docs/skills/arcwright-minigame/scripts/minigame_tool.py --help
git add docs/skills/arcwright-minigame engine/tests/test_minigame_tool.py
git commit -m "feat(config): guide browser minigame onboarding"
```

### Task 5: Produce the TMST Destination Adaptation and Preview Renderer

**Files:**

- Create after permission: `nightcap/mini_games/tell-me-something-true/client/renderer.ts`
- Create after permission: `nightcap/mini_games/tell-me-something-true/client/styles.css`
- Create: `nightcap/mini_games/tell-me-something-true/client/renderer.test.ts`
- Create: `nightcap/mini_games/tell-me-something-true/adaptations/nightcap-couch-race-v1/0.1.0.json`
- Create: `nightcap/mini_games/tell-me-something-true/adaptations/nightcap-couch-race-v1/readiness.json`
- Modify: `nightcap/mini_games/tell-me-something-true/manifest.json`
- Modify: `nightcap-web/scripts/discover-mini-games.mjs`
- Modify: `nightcap-web/tests/mini-game-registry.test.ts`

**Interfaces:**

- Consumes: approved TMST game design, approved generation categories, Nightcap semantic tokens, and current generic renderer kit.
- Produces: one versioned Nightcap adaptation with phone, shared-focus, and host roles under preview-only authority.

- [ ] **Step 1: Stop for category-level generation permission**

Present the exact proposed code, styling, copy, animation, audio, and configuration categories. Record approval or denial. Do not infer permission from the implementation go-ahead.

- [ ] **Step 2: Add failing renderer discovery and privacy tests**

Test exact-version discovery, no private prompt on shared display, no other player's vote on phone, reduced-motion behavior, reconnect, timeout, and fallback.

- [ ] **Step 3: Create the adaptation artifact before presentation code**

The artifact references the existing package version, preview-only authority, managed local hosting, Nightcap experience design system, public context allowlist, result mapping, and exact placement Draft. It does not modify the original definition.

- [ ] **Step 4: Implement the renderer through `defineRenderer`**

Render only authorized `runtime_state`, `presentation`, and events. Submit actions through `MiniGameContext.submit`. Keep timers, phase transitions, winner calculation, and consequence logic in Python.

- [ ] **Step 5: Remove `latest.json` from the canary loading path**

Change discovery and tests so the canary loads the exact definition version from invocation state. Preserve compatibility only where explicitly tested.

- [ ] **Step 6: Run and commit**

```powershell
npm --prefix nightcap-web test
npm --prefix nightcap-web run typecheck
python docs/skills/arcwright-minigame/scripts/minigame_tool.py validate nightcap/mini_games/tell-me-something-true
git add nightcap/mini_games/tell-me-something-true nightcap-web/scripts/discover-mini-games.mjs nightcap-web/tests/mini-game-registry.test.ts
git commit -m "feat(nightcap): add tmst preview adaptation"
```

### Task 6: Add One-command Local Playtest and Simulation Evidence

**Files:**

- Create: `nightcap-web/scripts/playtest-mini-game.mjs`
- Modify: `nightcap-web/package.json`
- Create: `nightcap-web/tests/mini-game-local-playtest.test.ts`
- Modify: `docs/skills/arcwright-minigame/scripts/minigame_tool.py`
- Modify: `engine/tests/test_minigame_tool.py`

**Interfaces:**

- Consumes: onboarding session ID, adaptation ref, fixture scenario, player count, and surface list.
- Produces: local URL, QR-ready LAN URL when available, preview-only banner, simulated players, replay file, and privacy-safe evidence bundle.

- [ ] **Step 1: Add failing local-lab lifecycle tests**

Cover active, completed, timeout, cancel, pause, reconnect, fallback, reset, and deterministic replay for 2, 4, and 8 simulated players.

- [ ] **Step 2: Add `playtest` to the helper**

```powershell
python docs/skills/arcwright-minigame/scripts/minigame_tool.py playtest --session SESSION_ID --scenario happy-path --players 4
```

The helper launches the existing web bundle and local fixture server. It must not require cloud credentials, a production model call, or production database consequences.

- [ ] **Step 3: Make preview authority unmistakable**

Show `NON_AUTHORITATIVE_PREVIEW` in every surface, readiness report, result projection, and exported bundle. A production promotion command must reject this evidence as authority proof.

- [ ] **Step 4: Run and commit**

```powershell
npm --prefix nightcap-web test
python -m pytest engine/tests/test_minigame_tool.py engine/tests/test_mini_game_onboarding.py -q
git add nightcap-web/scripts/playtest-mini-game.mjs nightcap-web/package.json nightcap-web/tests/mini-game-local-playtest.test.ts docs/skills/arcwright-minigame/scripts/minigame_tool.py engine/tests/test_minigame_tool.py
git commit -m "feat(config): add local minigame playtest"
```

### Task 7: Measure the Golden Path and Decide Whether to Generalize

**Files:**

- Create: `docs/product/mini-game-readiness/tmst-golden-path-report.md`
- Create: `docs/product/mini-game-readiness/tmst-golden-path-evidence.json`
- Modify: `docs/superpowers/plans/2026-08-02-mini-game-platform-readiness-program.md`

**Interfaces:**

- Consumes: clean first-time run, returning run, command logs, intervention count, readiness artifact, and local playtest evidence.
- Produces: timing report and a go, revise, or stop decision for the capability and trust plan.

- [ ] **Step 1: Run an internal deterministic walkthrough**

Expected: the workflow reaches Playtest-ready, proves every artifact transition, and identifies no hidden manual edit.

- [ ] **Step 2: Run a first-time developer session**

Use someone who did not build the platform. Measure elapsed time from import start to local Playtest-ready, interventions, corrections, misunderstood concepts, and confidence. Do not substitute an agent-only walkthrough.

- [ ] **Step 3: Run a returning-user session**

Expected target: 5 to 10 minutes, 15 minutes maximum.

- [ ] **Step 4: Evaluate the gate**

```text
GO: first-time <= 20 minutes, returning <= 15 minutes, local playtest succeeds, no source overwrite, no production consequence, and no hidden manual schema edit
REVISE: quality is sound but timing or comprehension misses the target
STOP: the walking skeleton requires a second model, duplicated platform component, unsafe authority, or destination-specific engine code
```

- [ ] **Step 5: Run final verification and commit the evidence**

```powershell
python -m pytest engine/tests/test_mini_game_onboarding.py engine/tests/test_minigame_tool.py engine/tests/test_social_truth_bluff_runtime.py api/tests/test_mini_games_api.py -q
npm --prefix nightcap-web test
python -m ruff check engine/mini_games
git diff --check
git add docs/product/mini-game-readiness docs/superpowers/plans/2026-08-02-mini-game-platform-readiness-program.md
git commit -m "test(config): record minigame onboarding proof"
```

## Acceptance Criteria Satisfied by This Plan

- A first-time browser developer can reach locally Playtest-ready in the approved target window without editing engine code.
- A returning developer can repeat the flow in the approved target window.
- Managed local hosting is the default and requires no cloud deployment.
- The original source and versioned package remain unchanged.
- Permission is requested before any generated artifact category.
- Readiness states, blockers, evidence, and next actions are visible and understandable.
- Preview-only results cannot mutate production state.
- The existing skill, helper, package loader, renderer kit, and discovery pipeline are extended rather than duplicated.
- The canary produces a reusable contract and evidence for the capability and trust plan.
