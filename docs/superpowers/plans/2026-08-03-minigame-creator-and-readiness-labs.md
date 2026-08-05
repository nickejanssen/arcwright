# Mini-game Creator and Readiness Labs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the proven browser onboarding workflow into a managed, permission-first authoring plane with shared APIs, guided CLI and SDK access, one-click local playtesting, understandable readiness states, production visualization, promotion, rollback, and independent developer usability proof.

**Architecture:** Extend `engine.mini_games.authoring` from the golden path into persistent resources and services. FastAPI exposes thin authoring routes. The existing helper and SDK call those resources instead of implementing their own workflow. The Arcwright dashboard visualizes the same readiness and lab resources, creating the foundation for the future no-code Studio without creating a separate no-code backend. Managed browser hosting is default. External hosting is an advanced profile over the same bridge and readiness contracts.

**Tech Stack:** Python 3.11, Pydantic 2, SQLAlchemy 2, Alembic, FastAPI, TypeScript, React 18, Vite, Node.js, pytest, Ruff.

## Global Constraints

- Required approved spec: `docs/specs/0080-mini-game-onboarding-preview-and-certification.md`.
- Required completed dependencies: the browser golden path and capability and trust platform plans.
- Stop before source changes until the founder gives the separate implementation go-ahead.
- Schema, migration, auth, security, telemetry, and cross-module approvals are required before execution.
- Extend the canonical skill, helper, loader, package model, renderer kit, fixture system, and certification evidence. Do not duplicate them.
- Imported source remains private, tenant-scoped, unchanged, and absent from telemetry.
- Ask before generating code, art, animation, audio, copy, or configuration.
- Every generated change is private Draft, provenance-linked, inspectable, reversible, and separately promotable.
- Preview-only authority cannot mutate production state.
- Managed hosting is the default. External hosting is advanced and never silently selected.
- Playtest-ready and Production-ready are evidence states, not package-existence flags.
- The dashboard is a consumer of shared APIs. It must not own arc logic, placement logic, adaptation generation, or certification rules.
- No marketplace, billing, public source export, public package signing, or third-party credential portal is part of Horizon 1.

---

### Task 1: Refresh Mainline, Verify Dependencies, and Stop

**Files:**

- Read: `docs/product/mini-game-readiness/mainline-safety-report.md`
- Read: `docs/product/mini-game-readiness/tmst-golden-path-report.md`
- Read: `docs/specs/0080-mini-game-onboarding-preview-and-certification.md`
- Modify: `docs/product/mini-game-readiness/mainline-safety-report.md`

- [ ] **Step 1: Fetch and inspect current main and merged PRs**

```powershell
git fetch origin --prune
gh pr list --state merged --base main --search "merged:>=2026-08-03" --json number,title,mergedAt,mergeCommit,headRefName,baseRefName,url
git status --short --branch
```

- [ ] **Step 2: Verify dependency evidence**

Expected: the canary is Playtest-ready, capability contracts pass with a non-Nightcap fixture, preview isolation is proven, and no unresolved overlap exists.

- [ ] **Step 3: Run the focused baseline**

```powershell
python -m pytest engine/tests/test_mini_game_onboarding.py engine/tests/test_mini_game_platform_contract.py api/tests/test_mini_games_api.py -q
npm --prefix sdk run typecheck
npm --prefix dashboard run typecheck
npm --prefix nightcap-web test
```

- [ ] **Step 4: Stop for schema, migration, auth, security, and telemetry approval**

Expected: approval is recorded before Task 2.

### Task 2: Persist Authoring Resources and Private Artifact Provenance

**Files:**

- Modify: `engine/db/orm.py`
- Create: `migrations/versions/0009_add_mini_game_authoring_resources.py`
- Modify: `engine/mini_games/authoring/models.py`
- Modify: `engine/mini_games/authoring/workspace.py`
- Create: `engine/mini_games/authoring/repository.py`
- Modify: `engine/mini_games/authoring/service.py`
- Create: `engine/tests/test_mini_game_authoring_repository.py`
- Modify: `engine/tests/test_mini_game_onboarding.py`

**Interfaces:**

- Consumes: tenant, user, import, package, adaptation, permission, change-set, readiness, evidence, and promotion resources.
- Produces: durable authoring sessions with immutable artifact versions and private blob references.

- [ ] **Step 1: Add failing tenant-isolation and provenance tests**

Test cross-tenant read denial, source fingerprint, immutable confirmed artifact, parent version, permission receipt, generated change set, evidence ownership, retirement, and rollback pointer.

- [ ] **Step 2: Add normalized resource tables**

Add tables for `mini_game_imports`, `mini_game_artifacts`, `mini_game_adaptations`, `mini_game_permission_receipts`, `mini_game_change_sets`, `mini_game_readiness_reports`, `mini_game_readiness_evidence`, and `mini_game_promotions`. Store private source and generated payloads by opaque blob reference, not in telemetry or event rows.

- [ ] **Step 3: Define repository interfaces**

```python
class MiniGameAuthoringRepository(Protocol):
    async def create_import(self, tenant_id: UUID, request: MiniGameOnboardingRequest) -> MiniGameImport: ...
    async def save_artifact(self, tenant_id: UUID, artifact: VersionedMiniGameArtifact) -> None: ...
    async def save_permission(self, tenant_id: UUID, receipt: GenerationPermissionReceipt) -> None: ...
    async def save_readiness(self, tenant_id: UUID, report: MiniGameReadinessReport) -> None: ...
    async def promote(self, tenant_id: UUID, request: PromotionRequest) -> PromotionRecord: ...
```

The service owns validation and state transitions. The repository owns persistence only.

- [ ] **Step 4: Preserve local and managed workspace parity**

The local workspace from the canary implements the same repository protocol for offline playtest. Managed persistence adds tenant isolation and durable refs without changing package, adaptation, permission, or readiness models.

- [ ] **Step 5: Verify migration and commit**

```powershell
alembic upgrade head
alembic downgrade -1
alembic upgrade head
python -m pytest engine/tests/test_mini_game_authoring_repository.py engine/tests/test_mini_game_onboarding.py -q
git add engine/db/orm.py migrations/versions/0009_add_mini_game_authoring_resources.py engine/mini_games/authoring engine/tests/test_mini_game_authoring_repository.py engine/tests/test_mini_game_onboarding.py
git commit -m "feat(config): persist minigame authoring resources"
```

### Task 3: Add Managed Browser Intake and Sandbox Analysis

**Files:**

- Create: `engine/mini_games/authoring/browser.py`
- Create: `engine/mini_games/authoring/analysis.py`
- Create: `engine/mini_games/authoring/security.py`
- Create: `engine/tests/test_mini_game_browser_import.py`
- Create: `engine/tests/fixtures/browser_minigames/networked-game/`
- Create: `engine/tests/fixtures/browser_minigames/unsafe-game/`

**Interfaces:**

- Consumes: static bundle or hosted URL and source access level.
- Produces: private import, browser behavior report, asset and network inventory, bridge observations, uncertainty, and confirmation questions.

- [ ] **Step 1: Add failing safe and unsafe intake tests**

Cover path escape, symlink escape, executable upload, oversized file, external network request, credential prompt, browser storage, popup, top navigation, microphone, camera, clipboard, and cross-origin isolation.

- [ ] **Step 2: Implement managed static-bundle intake**

Fingerprint each file, reject disallowed types and escapes, retain original bytes privately, and serve the analysis copy under a restrictive sandbox and content-security policy. Never execute imported code in the Python process.

- [ ] **Step 3: Implement hosted-URL analysis**

Record URL, observed capabilities, required external origins, bridge compatibility, and uncertainty. Do not copy source unless the user provides it. External hosting remains the selected hosting profile until explicitly changed.

- [ ] **Step 4: Generate only the smallest question set**

Compile observed facts into proposals. Ask for story role, result meaning, participation, placement authority, private information, and unresolved high-impact behavior. Do not ask users to restate confidently observed low-risk details.

- [ ] **Step 5: Run and commit**

```powershell
python -m pytest engine/tests/test_mini_game_browser_import.py -q
python -m ruff check engine/mini_games/authoring
git add engine/mini_games/authoring engine/tests/test_mini_game_browser_import.py engine/tests/fixtures/browser_minigames
git commit -m "feat(config): analyze browser minigame imports"
```

### Task 4: Generate Participation, Story-fit, and Presentation Adaptations with Permission

**Files:**

- Create: `engine/mini_games/authoring/adaptation.py`
- Create: `engine/mini_games/authoring/permissions.py`
- Create: `engine/mini_games/authoring/design_system.py`
- Create: `engine/tests/test_mini_game_adaptation.py`
- Create: `engine/tests/test_mini_game_generation_permissions.py`

**Interfaces:**

- Consumes: reusable package, destination capabilities, experience design system, creator intent, permission receipt, and immutable asset roles.
- Produces: one recommended adaptation, up to two alternatives, reversible change sets, and exact placement and consequence Drafts.

- [ ] **Step 1: Add failing alternative-quality tests**

For a 1-player source and a 2-to-4-player destination, assert exactly one recommended playable model and at most two materially different alternatives. Each includes social, pacing, fairness, surface, authority, and implementation tradeoffs.

- [ ] **Step 2: Add failing permission tests**

Assert category omission, denial, denied asset, immutable role, expired receipt, wrong adaptation, and changed source all block generation. Approval of code does not imply art, copy, audio, animation, or configuration approval.

- [ ] **Step 3: Implement deterministic proposal assembly**

Use authored templates and rule-based capability matching first. Optional generated explanations or artifacts run only after permission, existing routing, safety, cost logging, and public-safe context filtering. Two failed attempts use the authored fallback.

- [ ] **Step 4: Implement experience-design-system mapping**

Map semantic roles, typography, art direction, motion, audio, copy voice, surface layouts, accessibility, and intensity bounds. The engine receives only a validated surface-neutral projection.

- [ ] **Step 5: Preserve and compare versions**

Every generated change set points to source provenance, permission receipt, changed artifact refs, generator policy version, review status, and parent version. Reject in-place edits to playtest or active artifacts.

- [ ] **Step 6: Run and commit**

```powershell
python -m pytest engine/tests/test_mini_game_adaptation.py engine/tests/test_mini_game_generation_permissions.py -q
git add engine/mini_games/authoring engine/tests/test_mini_game_adaptation.py engine/tests/test_mini_game_generation_permissions.py
git commit -m "feat(config): generate minigame adaptations"
```

### Task 5: Expose One Shared Authoring API and SDK

**Files:**

- Create: `api/routers/mini_game_authoring.py`
- Modify: `api/routers/__init__.py`
- Create: `api/schemas/mini_game_authoring.py`
- Create: `api/tests/test_mini_game_authoring_api.py`
- Modify: `sdk/src/types.ts`
- Modify: `sdk/src/index.ts`
- Create: `sdk/tests/mini-game-authoring.test.mjs`
- Modify: `docs/skills/arcwright-minigame/scripts/minigame_tool.py`
- Modify: `engine/tests/test_minigame_tool.py`

**Interfaces:**

- Implements the exact routes approved in spec 0080.
- Produces identical typed resources for dashboard, CLI, SDK, and future Studio.

- [ ] **Step 1: Add failing route-auth and thinness tests**

Test tenant isolation, role authorization, idempotency, validation, source privacy, permission derivation, and that route functions delegate without package, adaptation, placement, or promotion logic.

- [ ] **Step 2: Implement import, confirm, adaptation, permission, variant, simulation, local-lab, readiness, rehearsal, and promotion routes**

Use the route names from spec 0080. Keep original source and generated content out of response payloads unless the authenticated owner explicitly requests a private artifact download that excludes Arcwright platform source.

- [ ] **Step 3: Add SDK resources and methods**

Mirror Python resource names and enums. Keep `Record<string, unknown>` only at registered extension boundaries, not for core package, adaptation, placement, permission, or readiness models.

- [ ] **Step 4: Convert helper commands into API clients with local fallback**

`onboard-browser`, `resume`, `status`, `playtest`, `rehearse`, and `promote` use the shared API when configured. Explicit `--local` uses the local repository implementation. The helper does not reimplement state transitions.

- [ ] **Step 5: Run and commit**

```powershell
python -m pytest api/tests/test_mini_game_authoring_api.py engine/tests/test_minigame_tool.py -q
npm --prefix sdk run typecheck
npm --prefix sdk run build
git add api/routers/mini_game_authoring.py api/routers/__init__.py api/schemas/mini_game_authoring.py api/tests/test_mini_game_authoring_api.py sdk/src/types.ts sdk/src/index.ts sdk/tests/mini-game-authoring.test.mjs docs/skills/arcwright-minigame/scripts/minigame_tool.py engine/tests/test_minigame_tool.py
git commit -m "feat(api): expose minigame authoring resources"
```

### Task 6: Build the Playtest-ready Local Lab

**Files:**

- Create: `dashboard/src/screens/minigames/MiniGameLocalLab.tsx`
- Create: `dashboard/src/screens/minigames/ReadinessStateCard.tsx`
- Create: `dashboard/src/screens/minigames/SurfacePreviewGrid.tsx`
- Create: `dashboard/src/api/miniGameAuthoring.ts`
- Modify: `dashboard/src/App.tsx`
- Create: `dashboard/tests/mini-game-local-lab.test.tsx`
- Create: `dashboard/scripts/test.mjs`
- Modify: `dashboard/package.json`
- Modify: `nightcap-web/scripts/playtest-mini-game.mjs`
- Modify: `nightcap-web/tests/mini-game-local-playtest.test.ts`

**Interfaces:**

- Consumes: local-lab session, exact adaptation, fixture, player count, surfaces, and preview-only result.
- Produces: understandable state, one-click launch, deterministic simulation, real-device join information, record, replay, reset, comparison, and evidence export.

- [ ] **Step 1: Add failing state-comprehension and accessibility tests**

Every state uses label, icon, structure, explanation, blockers, evidence, next action, and estimate. Test keyboard navigation, focus visibility, screen-reader names, high contrast, and reduced motion.

- [ ] **Step 2: Add the multi-surface preview grid**

Support phone, shared-focus, host, and destination-defined roles. Each surface receives only its authorized projection. Resize controls test small phone, large phone, tablet, shared display, and custom viewport.

- [ ] **Step 3: Add scenario controls**

Provide active, complete, timeout, error, cancel, pause, reconnect, fallback, host loss, reset, and deterministic replay. Show selected candidate, rejected candidates, and reason without exposing private story state.

- [ ] **Step 4: Add real-device bootstrap**

Show a QR-ready local-network URL when available and an explicit copy action. Never claim device acceptance from simulator evidence.

- [ ] **Step 5: Run and commit**

```powershell
npm --prefix dashboard test
npm --prefix dashboard run typecheck
npm --prefix dashboard run build
npm --prefix nightcap-web test
git add dashboard/src/screens/minigames dashboard/src/api/miniGameAuthoring.ts dashboard/src/App.tsx dashboard/tests/mini-game-local-lab.test.tsx dashboard/scripts/test.mjs dashboard/package.json nightcap-web/scripts/playtest-mini-game.mjs nightcap-web/tests/mini-game-local-playtest.test.ts
git commit -m "feat(dashboard): add minigame local lab"
```

`dashboard/scripts/test.mjs` uses the repository's existing esbuild and Node
test runner to compile and run dashboard tests. Do not add a second test
framework for this plan.

### Task 7: Build the Production-ready Visual Lab, Promotion, and Rollback

**Files:**

- Create: `engine/mini_games/authoring/readiness.py`
- Create: `engine/mini_games/authoring/promotion.py`
- Create: `engine/tests/test_mini_game_readiness.py`
- Create: `engine/tests/test_mini_game_promotion.py`
- Create: `dashboard/src/screens/minigames/MiniGameProductionLab.tsx`
- Create: `dashboard/src/screens/minigames/EvidenceGateMap.tsx`
- Create: `dashboard/src/screens/minigames/VersionComparison.tsx`
- Create: `dashboard/tests/mini-game-production-lab.test.tsx`

**Interfaces:**

- Consumes: automated evidence, human evidence, scenario matrix, performance, security, privacy, creative approval, real-device and real-player records.
- Produces: five understandable gate groups, exact promotion decision, and rollback target.

- [ ] **Step 1: Add failing readiness transition tests**

Assert package and adaptation readiness are independent. Missing, blocked, not-run, and human-review evidence cannot become pass. Promotion requires every applicable Production-ready gate and destination-owner approval.

- [ ] **Step 2: Implement the five gate groups**

Use the exact groups from spec 0080: Plays correctly, Fits the story, Feels native, Survives reality, and Approved by people. Preserve underlying machine-readable evidence categories.

- [ ] **Step 3: Add timeline, matrix, comparison, and rehearsal views**

Visualize multi-surface event timing, player-count and scenario coverage, version diffs, evidence provenance, authority profile, performance budgets, and selected placement reasoning.

- [ ] **Step 4: Implement exact-version promotion and rollback**

Promotion pins package and adaptation digests. Retired versions receive no new invocations but remain available for resume, replay, and audit. Rollback points new invocations to a previously certified pair and never rewrites artifacts.

- [ ] **Step 5: Run and commit**

```powershell
python -m pytest engine/tests/test_mini_game_readiness.py engine/tests/test_mini_game_promotion.py -q
npm --prefix dashboard test
npm --prefix dashboard run typecheck
npm --prefix dashboard run build
git add engine/mini_games/authoring/readiness.py engine/mini_games/authoring/promotion.py engine/tests/test_mini_game_readiness.py engine/tests/test_mini_game_promotion.py dashboard/src/screens/minigames/MiniGameProductionLab.tsx dashboard/src/screens/minigames/EvidenceGateMap.tsx dashboard/src/screens/minigames/VersionComparison.tsx dashboard/tests/mini-game-production-lab.test.tsx
git commit -m "feat(dashboard): visualize minigame readiness"
```

### Task 8: Measure Onboarding, Prove an Independent Developer, and Reconcile Status

**Files:**

- Create: `engine/telemetry/mini_game_authoring.py`
- Create: `engine/tests/test_mini_game_authoring_telemetry.py`
- Create: `docs/roadmap/operations/minigame-developer-usability-protocol.md`
- Create: `docs/product/mini-game-readiness/independent-browser-developer-report.md`
- Modify: `docs/product/mini-game-readiness/artifact-closeout-matrix.md`
- Modify: related roadmap tasks, epics, milestones, and GitHub issues only after local canonical reconciliation

- [ ] **Step 1: Add failing telemetry privacy tests**

Record cohort, elapsed milliseconds, state reached, intervention count, approved aggregate adaptation band, format ID, and reason codes. Exclude source, assets, prompts, generated output, private project content, answers, and story secrets.

- [ ] **Step 2: Run the internal protocol fixture**

Prove deterministic API behavior, local and managed parity, preview isolation, promotion, rollback, and no hidden manual edit.

- [ ] **Step 3: Run a first-time independent developer session**

Use a browser game and destination unrelated to Nightcap. The participant must not have built Arcwright. Measure time, interventions, errors, comprehension, confidence, local device success, and state reached.

- [ ] **Step 4: Apply the timing gate honestly**

First-time target is 10 to 15 minutes and 20 minutes maximum. Returning target is 5 to 10 minutes and 15 minutes maximum. If the maximum is missed, keep the feature below its claimed readiness and record remediation.

- [ ] **Step 5: Reconcile canonical and GitHub status**

Update the closeout matrix first. Then update only approved related issues, epics, milestones, specs, and plans. Read every GitHub mutation back and record the final state and remaining human gate.

- [ ] **Step 6: Run full verification**

```powershell
python -m pytest engine/tests/test_mini_game_onboarding.py engine/tests/test_mini_game_authoring_repository.py engine/tests/test_mini_game_browser_import.py engine/tests/test_mini_game_adaptation.py engine/tests/test_mini_game_generation_permissions.py engine/tests/test_mini_game_readiness.py engine/tests/test_mini_game_promotion.py engine/tests/test_mini_game_authoring_telemetry.py api/tests/test_mini_game_authoring_api.py -q
python -m ruff check engine api
python -m ruff format --check engine api
npm --prefix sdk run typecheck
npm --prefix sdk run build
npm --prefix dashboard test
npm --prefix dashboard run typecheck
npm --prefix dashboard run build
npm --prefix nightcap-web test
git diff --check
```

- [ ] **Step 7: Commit evidence and reconciliation**

```powershell
git add engine/telemetry/mini_game_authoring.py engine/tests/test_mini_game_authoring_telemetry.py docs/roadmap/operations/minigame-developer-usability-protocol.md docs/product/mini-game-readiness docs/roadmap docs/specs
git commit -m "test(config): prove minigame creator readiness"
```

## Acceptance Criteria Satisfied by This Plan

- A developer can import a browser game, confirm intent, adapt participation, fit it to story, style it, simulate it, and reach local Playtest-ready through one guided workflow.
- First-time and returning timing claims are backed by human evidence, not agent-only runs.
- Managed hosting is the default and external hosting uses the same protocol and readiness resources.
- Generation is permission-first, source-preserving, private, reviewable, reversible, and versioned.
- Local Playtest-ready testing is one click or command and visibly non-authoritative.
- Production-ready is easy to visualize and separates automated evidence from human approval.
- Package and destination readiness are independently versioned and auditable.
- Dashboard, CLI, SDK, skill, and future no-code Studio share the same APIs and artifacts.
- Promotion and rollback use exact immutable package and adaptation versions.
- The workflow is proven by a developer and game unrelated to Nightcap.
