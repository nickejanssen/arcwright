# Mini-game Capability and Trust Platform Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generalize the proven browser canary into game-agnostic reusable packages, destination adaptations, designer-owned placement policies, capability negotiation, authoritative result verification, bounded consequences, exact-version recovery, and generic API and SDK transport.

**Architecture:** Python remains authoritative for deterministic placement, profile negotiation, managed transcript reduction, invocation persistence, consequence application, and fallback. Hosting, execution, result authority, presentation, and distribution are independent profile families. TypeScript renders authorized projections and submits input. Legacy bindings remain readable through a compatibility translator, while new authoring writes only versioned packages, adaptations, and placement policies.

**Tech Stack:** Python 3.11, Pydantic 2, SQLAlchemy 2, Alembic, FastAPI, PostgreSQL, TypeScript, pytest, Node test runner, Ruff.

## Global Constraints

- Required approved specs: `docs/specs/0077-mini-game-registration-and-story-opportunities.md`, `docs/specs/0078-mini-game-invocation-and-execution-adapters.md`, and `docs/specs/0079-mini-game-results-consequences-theme-and-telemetry.md`.
- Required accepted decision: `docs/decisions/0018-mini-game-orchestration-and-execution-adapters.md`.
- Required canary gate: the golden-path report is `GO` or its required revisions are completed.
- Stop before source changes until the founder gives the separate implementation go-ahead.
- Cross-module, schema, migration, authentication, and telemetry work must receive the approvals required by `AGENTS.md` before execution.
- No arbitrary package code executes in the Python process.
- No browser claim alone can mutate production canonical state.
- No model call selects a mini-game, trigger, placement, winner, result, or consequence.
- No profile negotiation silently downgrades authority.
- No Nightcap, TV, phone, or mechanic-specific name enters a generic engine, API, or SDK contract.
- D-097 player-requested Grill execution remains disabled. Only the typed request-policy seam is modeled.
- Do not add a public marketplace, billing, public partner credentials, package signing service, Unity SDK, or Unreal SDK.

---

### Task 1: Refresh Mainline, Validate the Canary Gate, and Stop

**Files:**

- Read: `docs/product/mini-game-readiness/mainline-safety-report.md`
- Read: `docs/product/mini-game-readiness/tmst-golden-path-report.md`
- Read: `docs/specs/0077-mini-game-registration-and-story-opportunities.md`
- Read: `docs/specs/0078-mini-game-invocation-and-execution-adapters.md`
- Read: `docs/specs/0079-mini-game-results-consequences-theme-and-telemetry.md`
- Modify: `docs/product/mini-game-readiness/mainline-safety-report.md`

- [ ] **Step 1: Fetch and inspect every merge after the planning baseline**

```powershell
git fetch origin --prune
gh pr list --state merged --base main --search "merged:>=2026-08-03" --json number,title,mergedAt,mergeCommit,headRefName,baseRefName,url
git diff --name-status d26d7b8dee2aafa59ef6a0fd985da5bea771dbf1..origin/main
git status --short --branch
```

- [ ] **Step 2: Verify the canary gate**

Expected: source preservation, preview isolation, local playtest, first-time maximum, and returning-user maximum all pass. Otherwise execute only the recorded canary remediation.

- [ ] **Step 3: Run the focused baseline**

```powershell
python -m pytest engine/tests/test_mini_game_models.py engine/tests/test_mini_game_runtime.py engine/tests/test_arc_models.py api/tests/test_mini_games_api.py -q
npm --prefix sdk run typecheck
npm --prefix nightcap-web test
```

- [ ] **Step 4: Stop for cross-module, migration, auth, and telemetry approval**

Expected: approval is recorded before Task 2.

### Task 2: Add Reusable Package, Adaptation, and Placement Models

**Files:**

- Modify: `engine/mini_games/models.py`
- Modify: `engine/arc/models.py`
- Create: `engine/mini_games/placement.py`
- Modify: `engine/mini_games/__init__.py`
- Modify: `engine/tests/test_mini_game_models.py`
- Modify: `engine/tests/test_arc_models.py`
- Create: `engine/tests/test_mini_game_placement.py`

**Interfaces:**

- Consumes: current `MiniGameManifest`, `MiniGameDefinition`, `MiniGameBinding`, and approved spec 0077.
- Produces: `ReusableMiniGamePackage`, `DestinationAdaptation`, `MiniGamePlacementPolicy`, deterministic evaluator, and legacy translator.

- [ ] **Step 1: Add failing package and adaptation invariants**

Test exact semver and digest, player and duration bounds, unique namespaced capabilities, registered extension schemas, immutable artifact refs, source provenance, lifecycle, approval, and independent destination versions.

- [ ] **Step 2: Add failing placement tests**

```python
def test_designer_required_anchor_cannot_be_broadened(evaluator):
    decision = evaluator.evaluate(POLICY, STATE_AT_OTHER_BEAT, caller="engine")
    assert decision.eligible is False
    assert decision.reason_code == "anchor_inactive"


def test_session_seeded_rotation_replays_exactly(evaluator):
    first = evaluator.evaluate(SCENE_POLICY, STATE)
    second = evaluator.evaluate(SCENE_POLICY, STATE)
    assert second.selected_adaptation == first.selected_adaptation
    assert second.selection_reason == first.selection_reason
```

- [ ] **Step 3: Implement the exact approved models**

Add `CapabilityClaim`, `ParticipationCapabilities`, `DurationCapabilities`, `PresentationRole`, `ArtifactVersionRef`, `AdaptationApproval`, `DestinationAdaptation`, recursive policy expressions, anchors, authority grants, recurrence, candidate, timing, and placement policy exactly as spec 0077 defines them.

- [ ] **Step 4: Implement deterministic selection**

```python
@dataclass(frozen=True, slots=True)
class PlacementDecision:
    policy_ref: ArtifactVersionRef
    eligible: bool
    selected_adaptation: ArtifactVersionRef | None
    selection_reason: str
    rejected_candidates: tuple[RejectedCandidate, ...]
    reason_code: str


class MiniGamePlacementEvaluator:
    def evaluate(
        self,
        policy: MiniGamePlacementPolicy,
        state: PublicPlacementState,
        *,
        authority_source: str,
    ) -> PlacementDecision: ...
```

Implement only `arcwright.authored-order.v1` and `arcwright.session-seeded-rotation.v1`. Canonicalize candidates by ID, apply lookback only when an alternative remains, and persist a complete reason.

- [ ] **Step 5: Add the legacy translator**

Translate each `MiniGameBinding` in memory into an exact package ref, destination adaptation, designer-required beat-entry policy, current fallback, and consequence profile. Reject a beat that contains both legacy bindings and placement policies. New serialization never writes `MiniGameBinding`.

- [ ] **Step 6: Prove game agnosticism**

Create a synthetic `museum-heist` package, destination adaptation, and placement policy fixture. Assert no Nightcap vocabulary is required and no engine branch names the fixture.

- [ ] **Step 7: Run and commit**

```powershell
python -m pytest engine/tests/test_mini_game_models.py engine/tests/test_arc_models.py engine/tests/test_mini_game_placement.py -q
python -m ruff check engine/mini_games engine/arc/models.py
git add engine/mini_games/models.py engine/mini_games/placement.py engine/mini_games/__init__.py engine/arc/models.py engine/tests/test_mini_game_models.py engine/tests/test_arc_models.py engine/tests/test_mini_game_placement.py
git commit -m "feat(arc): add minigame placement policies"
```

### Task 3: Add Capability Profiles and No-downgrade Negotiation

**Files:**

- Create: `engine/mini_games/profiles.py`
- Create: `config/mini_game_capability_profiles.json`
- Create: `engine/tests/test_mini_game_profiles.py`
- Modify: `engine/mini_games/__init__.py`

**Interfaces:**

- Consumes: package claims, adaptation allowlist, environment capabilities, and closed profile registry.
- Produces: `NegotiatedExecutionProfiles` or an authored fallback reason.

- [ ] **Step 1: Add failing family and compatibility tests**

Cover family mismatch, protocol mismatch, retired profile, missing requirement, adaptation deny, duplicate profile ID, and forbidden silent downgrade.

- [ ] **Step 2: Register the Horizon 1 profiles**

Register the exact IDs in spec 0078 for local browser, managed browser, external browser, browser bridge, legacy Python mechanic, preview-only authority, transcript-reducer authority, external-backend authority, browser presentation, and private distribution.

- [ ] **Step 3: Implement the closed registry and negotiator**

```python
class MiniGameCapabilityProfileRegistry:
    def load(self, path: Path) -> None: ...
    def get(self, ref: CapabilityProfileRef) -> CapabilityProfileDefinition: ...


class MiniGameProfileNegotiator:
    def negotiate(
        self,
        package: ReusableMiniGamePackage,
        adaptation: DestinationAdaptation,
        available: AvailableMiniGameCapabilities,
    ) -> NegotiatedExecutionProfiles: ...
```

The JSON contains declarative definitions only. It cannot name a Python import, executable, callback, or source path.

- [ ] **Step 4: Add a synthetic future profile test**

Register `example.execution.future-sandbox.v1` in a test registry and prove package, placement, result, and consequence schemas remain unchanged.

- [ ] **Step 5: Run and commit**

```powershell
python -m pytest engine/tests/test_mini_game_profiles.py -q
python -m json.tool config/mini_game_capability_profiles.json
git add engine/mini_games/profiles.py engine/mini_games/__init__.py engine/tests/test_mini_game_profiles.py config/mini_game_capability_profiles.json
git commit -m "feat(config): negotiate minigame capabilities"
```

### Task 4: Persist Exact Invocation Identity and Recovery State

**Files:**

- Modify: `engine/db/orm.py`
- Create: `migrations/versions/0008_add_mini_game_invocation_contracts.py`
- Create: `engine/mini_games/coordinator.py`
- Modify: `engine/mini_games/runtime.py`
- Create: `engine/tests/test_mini_game_coordinator.py`
- Modify: `engine/tests/test_mini_game_runtime.py`
- Modify: `engine/tests/test_session_resume.py`

**Interfaces:**

- Consumes: placement decision, exact adaptation and package, negotiated profiles, immutable snapshot, and authority source.
- Produces: one idempotent `MiniGameInvocationRecord` and recoverable `MiniGameRun`.

- [ ] **Step 1: Add failing persistence and idempotency tests**

Assert exact policy, adaptation, package, profile versions, digest, reason, authority source, snapshot hash, revision, deadline, remaining duration, proof, result identity, and consequence state survive commit and reload.

- [ ] **Step 2: Add migration columns without destroying existing runs**

Add nullable or safe server-default columns for `placement_policy_id`, `placement_policy_version`, `adaptation_id`, `adaptation_version`, `package_id`, `package_version`, `definition_sha256`, `profiles`, `selection_reason`, `authority_source`, `resolved_snapshot_sha256`, `result_schema_version`, `authority_proof`, `result_identity`, `result_hash`, `result_received_at`, `consequence_state`, and `consequence_record`. Add a unique partial index for non-null result identity per run.

- [ ] **Step 3: Implement coordinator creation**

```python
class MiniGameCoordinator:
    async def evaluate_and_create(
        self,
        *,
        db: AsyncSession,
        session: Session,
        policy: MiniGamePlacementPolicy,
        authority_source: str,
    ) -> MiniGameRun | None: ...
```

Lock the relevant session evaluation row, persist the decision before starting the adapter, and make repeated evaluation of the same canonical state return the same run.

- [ ] **Step 4: Preserve pause, resume, timeout, retirement, and fallback**

New runs reject retired versions. Valid resume and replay load exact retired versions. Timeout runs on input, transition, state read, and the approved scheduler. Host loss uses the authored fallback and never starts a second run.

- [ ] **Step 5: Verify migration both directions**

```powershell
alembic upgrade head
alembic downgrade -1
alembic upgrade head
python -m pytest engine/tests/test_mini_game_coordinator.py engine/tests/test_mini_game_runtime.py engine/tests/test_session_resume.py -q
```

- [ ] **Step 6: Commit**

```powershell
git add engine/db/orm.py migrations/versions/0008_add_mini_game_invocation_contracts.py engine/mini_games/coordinator.py engine/mini_games/runtime.py engine/tests/test_mini_game_coordinator.py engine/tests/test_mini_game_runtime.py engine/tests/test_session_resume.py
git commit -m "feat(session): persist minigame invocations"
```

### Task 5: Add Preview, Managed Transcript, and External Result Authority

**Files:**

- Create: `engine/mini_games/adapters.py`
- Create: `engine/mini_games/transcripts.py`
- Modify: `engine/mini_games/runtime.py`
- Create: `engine/tests/test_mini_game_adapters.py`
- Create: `engine/tests/test_mini_game_transcripts.py`

**Interfaces:**

- Consumes: invocation, authenticated principal when required, transcript events, reducer, result envelope, and authority proof.
- Produces: provisional preview result or accepted production result with canonical hash.

- [ ] **Step 1: Add failing preview-isolation tests**

Assert preview results are marked `NON_AUTHORITATIVE_PREVIEW`, write only to a simulation ledger, and cannot enter the production consequence dispatcher.

- [ ] **Step 2: Add failing managed-transcript tests**

Cover ordered sequence, duplicate event, stale revision, cross-participant injection, exact reducer version, deterministic replay, client-supplied score ignored, and transcript digest mismatch.

- [ ] **Step 3: Define the reducer boundary**

```python
class DeterministicMiniGameReducer(Protocol):
    reducer_id: str
    version: str
    def initial_state(self, snapshot: ResolvedMiniGameSnapshot) -> JsonValue: ...
    def apply(self, state: JsonValue, event: TranscriptEvent) -> JsonValue: ...
    def finalize(self, state: JsonValue) -> TranscriptResult: ...
```

Reducers are code-reviewed platform plugins. Generated reducers remain Draft until explicit approval and fixture proof.

- [ ] **Step 4: Add failing external-authority tests**

Test auth-derived principal, tenant, destination, session, invocation, profile, package, adaptation, proof, revision, revocation, duplicate, and conflict. The request body must not supply the principal.

- [ ] **Step 5: Implement adapter registry and acceptance**

`PreviewOnlyAdapter`, `ManagedTranscriptAdapter`, and `ExternalBackendAdapter` implement one adapter protocol. Lock the invocation before accepting a result. Persist result identity and canonical hash before consequences. Do not import or execute partner code.

- [ ] **Step 6: Run and commit**

```powershell
python -m pytest engine/tests/test_mini_game_adapters.py engine/tests/test_mini_game_transcripts.py engine/tests/test_mini_game_runtime.py -q
git add engine/mini_games/adapters.py engine/mini_games/transcripts.py engine/mini_games/runtime.py engine/tests/test_mini_game_adapters.py engine/tests/test_mini_game_transcripts.py
git commit -m "feat(session): verify minigame result authority"
```

### Task 6: Apply Typed, Bounded Consequences Exactly Once

**Files:**

- Create: `engine/mini_games/consequences.py`
- Modify: `engine/mini_games/models.py`
- Modify: `engine/mini_games/runtime.py`
- Create: `engine/tests/test_mini_game_consequences.py`
- Modify: `engine/tests/test_resources_integration.py`
- Modify: `engine/tests/test_scoring_integration.py`
- Modify: `engine/tests/test_knowledge_graph.py`
- Modify: `engine/tests/test_obligations.py`

**Interfaces:**

- Consumes: accepted production result and an arc-owned consequence profile.
- Produces: exactly-once resource, score, knowledge, obligation, and content-event actions.

- [ ] **Step 1: Add failing type, bounds, and registry tests**

Reject missing finite bounds, inverted bounds, NaN, infinity, arbitrary target strings, unknown semantic keys, unresolved authored IDs, and a preview result.

- [ ] **Step 2: Add failing crash-recovery tests**

Simulate a crash after each rule. On retry, already recorded rule IDs are skipped and unapplied rules continue. Verify no double score, resource, knowledge, obligation, or event mutation.

- [ ] **Step 3: Implement exact typed rule variants from spec 0079**

Use dedicated target types for resource and score actions and dedicated models for knowledge, obligation, and content events. Truncate finite numeric values toward zero for integer services, then clamp inclusively.

- [ ] **Step 4: Delegate to existing canonical services**

The dispatcher never updates service tables directly. It calls the current resource, scoring, knowledge, obligation, and event service functions and records each applied rule before moving to the next.

- [ ] **Step 5: Run and commit**

```powershell
python -m pytest engine/tests/test_mini_game_consequences.py engine/tests/test_resources_integration.py engine/tests/test_scoring_integration.py engine/tests/test_knowledge_graph.py engine/tests/test_obligations.py -q
git add engine/mini_games/consequences.py engine/mini_games/models.py engine/mini_games/runtime.py engine/tests/test_mini_game_consequences.py engine/tests/test_resources_integration.py engine/tests/test_scoring_integration.py engine/tests/test_knowledge_graph.py engine/tests/test_obligations.py
git commit -m "feat(session): apply minigame consequences"
```

### Task 7: Make API and SDK Transport Generic and Exact-versioned

**Files:**

- Modify: `api/schemas/__init__.py`
- Modify: `api/routers/mini_games.py`
- Modify: `api/tests/test_mini_games_api.py`
- Modify: `api/tests/test_scene_sweep_api.py`
- Modify: `sdk/src/types.ts`
- Modify: `sdk/src/index.ts`
- Create: `sdk/tests/mini-game-invocations.test.mjs`
- Modify: `nightcap-web/src/mini-games/client.ts`
- Modify: `nightcap-web/tests/mini-game-client.test.ts`

**Interfaces:**

- Consumes: audience-filtered invocation projection, generic action, host or external result route, and exact versions.
- Produces: generic `MiniGameInvocationResponse`, SDK state, action, and result methods.

- [ ] **Step 1: Add failing generic-response tests**

Assert response includes package, adaptation, profile, version, revision, deadline, generic runtime state, generic presentation, and only the caller's submissions. Assert no TMST or Scene Sweep union branch is required.

- [ ] **Step 2: Move mechanic projections behind plugins**

Delete `_build_phase_state_for_game` branching from the router only after characterization tests prove TMST and Scene Sweep responses remain behaviorally equivalent. Plugins or projection strategies return generic authorized dictionaries.

- [ ] **Step 3: Add result submission with auth-derived authority**

Keep the route thin: authenticate, derive principal, validate schema, call adapter, commit, and return acceptance. Player principals receive 403 for production result submission.

- [ ] **Step 4: Update SDK and browser client**

Use exact `packageVersion` and `adaptationVersion`, generic `runtimeState` and `presentation`, and `submitMiniGameResult` only for authorized hosts. Remove `latest.json` from runtime loading.

- [ ] **Step 5: Run and commit**

```powershell
python -m pytest api/tests/test_mini_games_api.py api/tests/test_scene_sweep_api.py engine/tests/test_mini_game_adapters.py -q
npm --prefix sdk run typecheck
npm --prefix sdk run build
npm --prefix nightcap-web test
git add api/schemas/__init__.py api/routers/mini_games.py api/tests/test_mini_games_api.py api/tests/test_scene_sweep_api.py sdk/src/types.ts sdk/src/index.ts sdk/tests/mini-game-invocations.test.mjs nightcap-web/src/mini-games/client.ts nightcap-web/tests/mini-game-client.test.ts
git commit -m "feat(api): expose generic minigame invocations"
```

### Task 8: Add Privacy-safe Lifecycle Telemetry and Optional Generation Budgets

**Files:**

- Create: `engine/telemetry/mini_games.py`
- Modify: `engine/mini_games/coordinator.py`
- Modify: `engine/mini_games/runtime.py`
- Modify: `engine/mini_games/resolver.py`
- Create: `engine/tests/test_mini_game_telemetry.py`
- Modify: `engine/tests/test_mini_game_resolution.py`
- Modify: `engine/tests/test_generation_logging.py`

- [ ] **Step 1: Add failing telemetry exclusion tests**

Assert events exclude raw submissions, semantics, prompts, generated text, runtime state, private story context, per-player signals, and knowledge state.

- [ ] **Step 2: Emit the approved lifecycle events**

Emit placement evaluated, selected, started, adaptation selected, completed, timed out, cancelled, result rejected, consequence applied, fallback used, and reconnected. Preserve read compatibility for `mini_game_opportunity_evaluated`.

- [ ] **Step 3: Enforce public context and generation budget**

Only placement-policy allowlisted public-safe values reach optional content generation. Cap generation at two attempts and 2500 ms by default, then use authored content or cancel. Generation cannot affect selection, answer authority, score, truth, or consequence.

- [ ] **Step 4: Run and commit**

```powershell
python -m pytest engine/tests/test_mini_game_telemetry.py engine/tests/test_mini_game_resolution.py engine/tests/test_generation_logging.py -q
git add engine/telemetry/mini_games.py engine/mini_games/coordinator.py engine/mini_games/runtime.py engine/mini_games/resolver.py engine/tests/test_mini_game_telemetry.py engine/tests/test_mini_game_resolution.py engine/tests/test_generation_logging.py
git commit -m "feat(session): record minigame lifecycle telemetry"
```

### Task 9: Prove Compatibility, Game Agnosticism, Recovery, and Rollback

**Files:**

- Create: `engine/tests/fixtures/mini_games/museum-heist/`
- Create: `engine/tests/test_mini_game_platform_contract.py`
- Modify: `tests/test_roadmap_minigame_status.py`
- Modify: `docs/product/mini-game-readiness/artifact-closeout-matrix.md`

- [ ] **Step 1: Run legacy fixtures unchanged**

Verify current Nightcap bindings, TMST, Scene Sweep, Crime Scene Smash, and Evidence Locker load and run through the compatibility translator.

- [ ] **Step 2: Run synthetic non-Nightcap end to end**

The fixture must register package and adaptation, evaluate exact and delegated placement, negotiate profiles, run preview and managed transcript paths, reject an untrusted result, apply bounded consequences, pause, resume, retire, replay, and roll back without Nightcap code or vocabulary.

- [ ] **Step 3: Test future profile extension**

Add a test-only profile and verifier. Assert no package, adaptation, placement, invocation, result, or consequence schema changes.

- [ ] **Step 4: Run full verification**

```powershell
python -m pytest engine/tests/test_mini_game_models.py engine/tests/test_mini_game_placement.py engine/tests/test_mini_game_profiles.py engine/tests/test_mini_game_coordinator.py engine/tests/test_mini_game_adapters.py engine/tests/test_mini_game_transcripts.py engine/tests/test_mini_game_consequences.py engine/tests/test_mini_game_telemetry.py engine/tests/test_mini_game_platform_contract.py api/tests/test_mini_games_api.py -q
python -m ruff check engine api
python -m ruff format --check engine api
npm --prefix sdk run typecheck
npm --prefix sdk run build
npm --prefix nightcap-web test
git diff --check
```

- [ ] **Step 5: Update evidence and commit**

```powershell
git add engine/tests/fixtures/mini_games engine/tests/test_mini_game_platform_contract.py tests/test_roadmap_minigame_status.py docs/product/mini-game-readiness/artifact-closeout-matrix.md
git commit -m "test(arc): prove minigame platform contracts"
```

## Acceptance Criteria Satisfied by This Plan

- One package supports multiple versioned destination adaptations without copying or overwriting the source mechanic.
- Designers can require exact placement, delegate bounded selection, authorize requests, and compose those controls.
- Scene rotation and future Grill request eligibility require no engine-specific branch.
- Hosting, execution, authority, presentation, and distribution negotiate independently with no silent downgrade.
- Preview, managed transcript, and authenticated external authority satisfy permanent trust invariants.
- Results are exact-versioned facts and only authored bounded consequences mutate canonical services.
- Resume, timeout, retirement, replay, and rollback are deterministic and auditable.
- API and SDK transport are mechanic-neutral, destination-neutral, audience-filtered, and exact-versioned.
- A synthetic non-Nightcap game and future profile work without schema changes or Nightcap vocabulary.
