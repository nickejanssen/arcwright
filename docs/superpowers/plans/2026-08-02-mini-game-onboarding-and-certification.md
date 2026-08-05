# Mini-game Onboarding, Preview, and Certification Implementation Plan

> **Execution status:** Superseded by the founder-approved 2026-08-03 browser
> golden path and creator/readiness-lab design. Do not execute this plan. Its
> useful validator and fixture details must be reconciled into the replacement
> golden-path and readiness-lab plans after spec 0080 is approved.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the existing Arcwright mini-game skill, helper, package template, loader, renderer kit, and CI into one coherent path from prototype import to evidence-backed deployment readiness.

**Architecture:** Extend the existing `arcwright-minigame` skill and `minigame_tool.py`; do not create a second CLI, validator, registry, package format, renderer kit, or skill. The Python engine remains the schema authority, Nightcap web provides fixture-driven preview for hosted renderers, and certification emits machine-readable evidence without pretending automated checks prove fun, device quality, or human approval.

**Tech Stack:** Python 3.11, argparse, Pydantic 2, JSON Schema, TypeScript, Node test runner, happy-dom, esbuild, pytest, Make, GitHub Actions.

## Global Constraints

- Required approved spec: `docs/specs/0080-mini-game-onboarding-preview-and-certification.md`.
- Required completed dependency: the contract checkpoint in `2026-08-02-mini-game-contracts-and-adapters.md`.
- Use `docs/skills/arcwright-minigame/SKILL.md` as the canonical skill and `.agents/skills/arcwright-minigame/SKILL.md` only as a thin launcher.
- Reuse `docs/skills/arcwright-minigame/scripts/minigame_tool.py` for every command.
- The engine's Pydantic models remain the single validation source of truth.
- Automated human gates must report `NOT_RUN`, never `PASS`.
- Preview uses deterministic fixtures and makes no production session or model call.
- No new dependency is permitted by this plan.
- Do not publish credentials, external authentication, billing, a marketplace, or engine-specific SDKs.

---

## File Responsibility Map

| File | Responsibility |
| --- | --- |
| `docs/skills/arcwright-minigame/SKILL.md` | Canonical onboarding workflow and gates |
| `docs/skills/arcwright-minigame/scripts/minigame_tool.py` | Single scaffold, registration, opportunity, preview, validation, and certification CLI |
| `nightcap/mini_games/_template/` | Valid draft package and renderer starting point |
| `nightcap-web/scripts/discover-mini-games.mjs` | Experience-aware production package discovery and exact-version bundling |
| `nightcap-web/src/mini-games/preview.ts` | Fixture-driven renderer preview |
| `engine/mini_games/certification.py` | Readiness evidence evaluation |
| `docs/specs/schemas/mini-game-readiness-report.schema.json` | Machine-readable report contract |
| `docs/specs/schemas/mini-game-external-preview-evidence.schema.json` | Host-authoritative external-engine preview evidence contract |

### Task 1: Preflight and Baseline

**Files:**

- Read: `docs/specs/0080-mini-game-onboarding-preview-and-certification.md`
- Read: `docs/skills/arcwright-minigame/SKILL.md`
- Read: `docs/skills/arcwright-minigame/scripts/minigame_tool.py`

**Interfaces:**

- Consumes: approved spec 0080 and completed platform contracts.
- Produces: a written baseline report and explicit implementation approval.

- [ ] **Step 1: Execute the master-plan safety gate**

Record current `origin/main`, merged PR overlap, and clean worktree evidence.

- [ ] **Step 2: Run the exact baseline**

```powershell
python docs/skills/arcwright-minigame/scripts/minigame_tool.py validate nightcap/mini_games
python -m pytest engine/tests/test_mini_game_models.py -q
npm --prefix nightcap-web test
```

Expected: record current behavior, including active packages skipped for missing
renderers. Do not reinterpret a known baseline failure as a change regression.

- [ ] **Step 3: Stop for explicit founder implementation approval**

Expected: no tooling, template, documentation, or CI change before approval.

### Task 2: Correct the Canonical Authoring Contract

**Files:**

- Modify: `docs/skills/arcwright-minigame/SKILL.md`
- Modify: `.agents/skills/arcwright-minigame/SKILL.md`
- Modify: `docs/conventions/mini-game-authoring.md`
- Modify: `docs/agents/USAGE.md`
- Modify: `README.md`
- Modify: `docs/architecture/09-developer-api.md`
- Test: `engine/tests/test_mini_game_documentation.py`

**Interfaces:**

- Consumes: ADR 0018, specs 0077 through 0080, and existing thin-launcher convention.
- Produces: one documented workflow named `intake -> scaffold -> register -> bind -> preview -> validate -> certify -> promote`.

- [ ] **Step 1: Write a failing documentation contract test**

```python
from pathlib import Path


def test_minigame_docs_reference_adapter_aware_workflow():
    guide = Path("docs/conventions/mini-game-authoring.md").read_text()
    assert "engine/mini_games/models.py" in guide
    assert "arcwright_hosted" in guide
    assert "host_authoritative" in guide
    assert "certify" in guide
    assert "engine/mini_games/schemas.py" not in guide
```

- [ ] **Step 2: Run and confirm failure**

```powershell
python -m pytest engine/tests/test_mini_game_documentation.py -q
```

Expected: stale schema path or missing adapter workflow assertion fails.

- [ ] **Step 3: Update the canonical skill and guide**

Document these exact commands:

```powershell
python docs/skills/arcwright-minigame/scripts/minigame_tool.py scaffold --experience nightcap --game-id sample-game --title "Sample Game"
python docs/skills/arcwright-minigame/scripts/minigame_tool.py register --arc nightcap/couch-race.arc.json --package nightcap/mini_games/sample-game --registration-id couch-race-sample --adapter arcwright_hosted
python docs/skills/arcwright-minigame/scripts/minigame_tool.py bind --arc nightcap/couch-race.arc.json --beat-id scene --opportunity-id scene-sample --registration-id couch-race-sample --consequence-profile-id sample-results
python docs/skills/arcwright-minigame/scripts/minigame_tool.py preview --experience nightcap --game-id sample-game --surface phone --fixture active
python docs/skills/arcwright-minigame/scripts/minigame_tool.py validate nightcap/mini_games/sample-game
python docs/skills/arcwright-minigame/scripts/minigame_tool.py certify --package nightcap/mini_games/sample-game --output build/sample-game-package-readiness.json
python docs/skills/arcwright-minigame/scripts/minigame_tool.py certify --arc nightcap/couch-race.arc.json --registration-id couch-race-sample --output build/sample-game-readiness.json
```

Explain ownership, exact-version immutability, trusted-host limits, human gates,
and rollback. Keep the launcher limited to canonical skill discovery metadata.

- [ ] **Step 4: Run and commit**

```powershell
python -m pytest engine/tests/test_mini_game_documentation.py -q
rg -n "engine/mini_games/schemas.py|AW-250.*unbuilt" docs .agents README.md
git diff --check
git add docs/skills/arcwright-minigame .agents/skills/arcwright-minigame docs/conventions/mini-game-authoring.md docs/agents/USAGE.md README.md docs/architecture/09-developer-api.md engine/tests/test_mini_game_documentation.py
git commit -m "docs(arc): update minigame onboarding contract"
```

Expected: tests pass and stale-reference search returns no matches.

### Task 3: Extend the Existing Helper with Registration and Binding

**Files:**

- Modify: `docs/skills/arcwright-minigame/scripts/minigame_tool.py`
- Create: `engine/tests/test_mini_game_tool.py`
- Modify: `nightcap/mini_games/_template/manifest.json`
- Modify: `nightcap/mini_games/_template/definitions/0.1.0.json`
- Create: `nightcap/mini_games/_template/client/renderer.ts`
- Modify: `nightcap/mini_games/_template/README.md`

**Interfaces:**

- Consumes: `load_mini_game_package`, `ArcDefinition`, `MiniGameRegistration`, `MiniGameOpportunity`, and package template.
- Produces: `register_package(...) -> int`, `bind_opportunity(...) -> int`, and CLI commands `register` and `bind`.

- [ ] **Step 1: Write failing registration tests**

```python
def test_register_adds_exact_version_and_digest(tmp_path):
    arc_path, package_path = copy_arc_and_package(tmp_path)
    exit_code = register_package(
        arc_path=arc_path,
        package_path=package_path,
        registration_id="sample-registration",
        adapter="arcwright_hosted",
    )
    arc = json.loads(arc_path.read_text())
    registration = arc["mini_game_registrations"][0]
    assert exit_code == 0
    assert registration["version"] == "0.1.0"
    assert len(registration["definition_sha256"]) == 64
```

- [ ] **Step 2: Write failing binding tests**

```python
def test_bind_adds_opportunity_to_named_beat(tmp_path):
    arc_path = registered_arc(tmp_path)
    exit_code = bind_opportunity(
        arc_path=arc_path,
        beat_id="scene",
        opportunity_id="scene-sample",
        registration_id="sample-registration",
        consequence_profile_id="sample-results",
    )
    arc = json.loads(arc_path.read_text())
    scene = next(beat for beat in arc["beats"] if beat["beat_id"] == "scene")
    assert exit_code == 0
    assert scene["mini_game_opportunities"][0]["opportunity_id"] == "scene-sample"
```

- [ ] **Step 3: Run and confirm failure**

```powershell
python -m pytest engine/tests/test_mini_game_tool.py -q
```

Expected: missing helper functions.

- [ ] **Step 4: Implement exact helper signatures**

```python
def register_package(
    *,
    arc_path: Path,
    package_path: Path,
    registration_id: str,
    adapter: str,
) -> int:
    ...


def bind_opportunity(
    *,
    arc_path: Path,
    beat_id: str,
    opportunity_id: str,
    registration_id: str,
    consequence_profile_id: str,
) -> int:
    ...
```

Load and validate before writing. Write UTF-8 JSON with two-space indentation
and one trailing newline. Reject duplicate IDs, unknown beats, missing profiles,
host-authoritative packages without adapter support, selector-less
opportunities, and both reserved request modes: `host_request` and
`player_request`.

- [ ] **Step 5: Make the template production-valid as a draft**

Add a default-exported renderer created by `defineRenderer` for the
`arcwright_hosted` starting path, exact adapter and digest fields, one authored
fallback, and a README that states every value the developer must replace
before playtest promotion. Document that `host_authoritative` may remove the
Arcwright renderer only when it declares external presentation and later
attaches version/digest-matched external preview evidence.

- [ ] **Step 6: Run and commit**

```powershell
python -m pytest engine/tests/test_mini_game_tool.py engine/tests/test_mini_game_models.py -q
python docs/skills/arcwright-minigame/scripts/minigame_tool.py validate nightcap/mini_games/_template
git add docs/skills/arcwright-minigame/scripts/minigame_tool.py engine/tests/test_mini_game_tool.py nightcap/mini_games/_template
git commit -m "feat(arc): extend minigame authoring tool"
```

### Task 4: Make Package Discovery Experience-aware and Exact-versioned

**Files:**

- Modify: `nightcap-web/scripts/discover-mini-games.mjs`
- Modify: `nightcap-web/src/mini-games/registry-bindings.ts`
- Test: `nightcap-web/tests/mini-game-registry.test.ts`
- Test: `nightcap-web/tests/mini-game-asset-route.test.ts`

**Interfaces:**

- Consumes: an experience root, package manifests, exact definition versions, lifecycle, and renderers.
- Produces: `findPackages({ experienceRoot, includeFixtures }) -> Promise<DiscoveredPackage[]>` and no `latest.json` alias.

- [ ] **Step 1: Export discovery functions and write failing tests**

```typescript
test("production discovery excludes fixtures and incomplete active packages", async () => {
  const packages = await findPackages({
    experienceRoot: fixtureRoot,
    includeFixtures: false,
  });
  assert.deepEqual(packages.map((item) => item.gameId), ["complete-active"]);
});

test("definition output is exact version only", async () => {
  await copyDefinitions([packageV01], outputRoot);
  assert.equal(existsSync(join(outputRoot, "sample", "0.1.0.json")), true);
  assert.equal(existsSync(join(outputRoot, "sample", "latest.json")), false);
});
```

- [ ] **Step 2: Run and confirm failure**

```powershell
npm --prefix nightcap-web test
```

Expected: functions are not exported or `latest.json` assertion fails.

- [ ] **Step 3: Implement the discovery interface**

```typescript
export interface DiscoveryOptions {
  experienceRoot: string;
  includeFixtures: boolean;
}

export interface DiscoveredPackage {
  gameId: string;
  version: string;
  lifecycle: "draft" | "playtest" | "active" | "retired";
  definitionSha256: string;
  rendererPath: string;
  definitionPath: string;
}
```

Production discovery rejects an active `arcwright_hosted` package missing its
renderer, exact definition, matching digest, or supported hosted adapter.
`host_authoritative` packages with external presentation are excluded from the
Arcwright renderer bundle without failing package integrity. Draft packages are
available only to adapter-aware preview. Retired packages are excluded from new
bundles.

- [ ] **Step 4: Run and commit**

```powershell
npm --prefix nightcap-web test
npm --prefix nightcap-web run typecheck
git add nightcap-web/scripts/discover-mini-games.mjs nightcap-web/src/mini-games/registry-bindings.ts nightcap-web/tests/mini-game-registry.test.ts nightcap-web/tests/mini-game-asset-route.test.ts
git commit -m "fix(nightcap): validate minigame discovery"
```

### Task 5: Add Adapter-aware Deterministic Preview

**Files:**

- Modify: `docs/skills/arcwright-minigame/scripts/minigame_tool.py`
- Create: `nightcap-web/src/mini-games/preview.ts`
- Test: `nightcap-web/tests/mini-game-preview.test.ts`
- Modify: `nightcap-web/src/mini-games/stage.ts`

**Interfaces:**

- Consumes: package adapter, definition, optional Arcwright renderer, surface,
  fixture name, opaque theme, adapter-neutral `MiniGameState`, and optional
  external-engine preview evidence.
- Produces: hosted `renderMiniGamePreview(options: PreviewOptions) ->
  Promise<PreviewController>`, host-authoritative protocol-fixture output, and
  CLI `preview`.

- [ ] **Step 1: Write a failing phone preview test**

```typescript
test("preview mounts exact version without a production request", async () => {
  const calls: string[] = [];
  const controller = await renderMiniGamePreview({
    root,
    renderer,
    definition,
    surface: "phone",
    fixture: "active",
    theme: { colorScheme: "midnight" },
    fetcher: async (url) => { calls.push(String(url)); throw new Error("network disabled"); },
  });
  assert.equal(root.dataset.miniGameState, "active:sample-game");
  assert.deepEqual(calls, []);
  controller.unmount();
});

test("host-authoritative preview does not require Arcwright renderer", async () => {
  const result = await previewHostAuthoritative({
    definition,
    protocolFixtures,
    externalPreviewEvidence,
  });
  assert.equal(result.protocolStatus, "PASS");
  assert.equal(result.arcwrightRendererRequired, false);
});
```

- [ ] **Step 2: Run and confirm failure**

```powershell
npm --prefix nightcap-web test
```

Expected: missing preview module.

- [ ] **Step 3: Implement exact preview types**

```typescript
export type PreviewFixture = "active" | "timed_out" | "completed" | "error" | "reconnect";

export interface PreviewOptions {
  root: HTMLElement;
  renderer: MiniGameRenderer;
  definition: MiniGameDefinition;
  surface: Surface;
  fixture: PreviewFixture;
  theme: Record<string, unknown>;
  fetcher?: typeof fetch;
}

export interface PreviewController {
  setFixture(fixture: PreviewFixture): void;
  unmount(): void;
}
```

Use fixed IDs, fixed deadlines, and fixed sequence numbers. Make `ctx.submit`
return a pre-authored accepted fixture response without network access or
canonical score/outcome computation. Render a visible banner stating `Fixture
preview, not device or gameplay evidence`.

- [ ] **Step 4: Wire the existing Python command to the preview build**

For `arcwright_hosted`, the `preview` command validates the package, runs the
Nightcap preview build, and prints the local artifact path. For
`host_authoritative`, it runs only invocation, resume, rejection, result, and
consequence protocol fixtures, validates the optional external evidence record,
and reports that presentation runs in the developer's engine. It does not
require or synthesize an Arcwright renderer, start a production session,
compute canonical gameplay outcomes, execute external code, or invoke a model.

- [ ] **Step 5: Run and commit**

```powershell
npm --prefix nightcap-web test
npm --prefix nightcap-web run typecheck
python -m pytest engine/tests/test_mini_game_tool.py -q
git add docs/skills/arcwright-minigame/scripts/minigame_tool.py nightcap-web/src/mini-games/preview.ts nightcap-web/src/mini-games/stage.ts nightcap-web/tests/mini-game-preview.test.ts engine/tests/test_mini_game_tool.py
git commit -m "feat(nightcap): preview minigame packages"
```

### Task 6: Add Machine-readable Certification

**Files:**

- Create: `engine/mini_games/certification.py`
- Test: `engine/tests/test_mini_game_certification.py`
- Create: `docs/specs/schemas/mini-game-readiness-report.schema.json`
- Create: `docs/specs/schemas/mini-game-external-preview-evidence.schema.json`
- Modify: `docs/skills/arcwright-minigame/scripts/minigame_tool.py`

**Interfaces:**

- Consumes: package path, optional arc and registration, opportunity, test evidence paths, and explicit human evidence records.
- Produces: `certify_package(request: CertificationRequest) -> MiniGameReadinessReport`, `certify_registration(request: CertificationRequest) -> MiniGameReadinessReport`, and CLI `certify` package or registration modes.

- [ ] **Step 1: Write failing certification tests**

```python
def test_missing_human_evidence_is_not_run(certification_request):
    report = certify_registration(certification_request)
    assert report.gates["real_device"].status == "NOT_RUN"
    assert report.gates["real_player"].status == "NOT_RUN"
    assert report.overall_status == "BLOCKED"


def test_active_package_with_digest_drift_fails(certification_request):
    certification_request.registration.definition_sha256 = "0" * 64
    report = certify_registration(certification_request)
    assert report.gates["package_integrity"].status == "FAIL"


def test_package_only_certification_marks_integration_pending(package_request):
    report = certify_package(package_request)
    assert report.registration_id is None
    assert report.gates["registration"].status == "INTEGRATION_PENDING"
    assert report.gates["story_opportunity"].status == "INTEGRATION_PENDING"
    assert report.gates["integrated_session"].status == "INTEGRATION_PENDING"
    assert report.overall_status == "BLOCKED"


def test_host_authoritative_package_does_not_require_arcwright_renderer(host_request):
    host_request.arcwright_renderer_path = None
    host_request.external_preview_evidence = matching_external_preview_evidence()
    report = certify_package(host_request)
    assert report.gates["package_integrity"].status == "PASS"
    assert report.gates["presentation_preview"].status == "PASS"


def test_host_authoritative_preview_evidence_must_match_digest(host_request):
    host_request.external_preview_evidence = external_preview_evidence(
        definition_sha256="0" * 64,
    )
    report = certify_package(host_request)
    assert report.gates["presentation_preview"].status == "FAIL"
```

- [ ] **Step 2: Run and confirm failure**

```powershell
python -m pytest engine/tests/test_mini_game_certification.py -q
```

Expected: missing certification module.

- [ ] **Step 3: Define exact report models**

```python
class GateStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    NOT_RUN = "NOT_RUN"
    INTEGRATION_PENDING = "INTEGRATION_PENDING"


class ReadinessGate(BaseModel):
    status: GateStatus
    evidence: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)


class MiniGameReadinessReport(BaseModel):
    schema_version: Literal["1.0"] = "1.0"
    game_id: str
    registration_id: str | None = None
    package_version: str
    definition_sha256: str
    generated_at: datetime
    gates: dict[str, ReadinessGate]
    overall_status: Literal["READY", "BLOCKED"]
```

Required gate keys are `contract`, `exact_version`, `package_integrity`,
`adapter`, `presentation_preview`, `deterministic_replay`, `lifecycle`, `registration`,
`story_opportunity`, `integrated_session`, `consequence_idempotency`,
`privacy`, `safety`, `telemetry`, `generation_budget`, `reconnect`,
`accessibility`, `performance`, `player_counts`, `creative_approval`,
`real_device`, and `real_player`.

- [ ] **Step 4: Implement report evaluation and schema**

Set `READY` only when every adapter-required gate is `PASS`. Package-only mode
evaluates package, hosted mechanic or host protocol, adapter-aware presentation
preview, privacy, safety, simulation, and human gates, then marks registration,
story opportunity, and integrated session as `INTEGRATION_PENDING`.
`arcwright_hosted` requires an exact-version Arcwright fixture renderer.
`host_authoritative` requires passing protocol fixtures and matching external
preview evidence; missing Arcwright renderer is not a failure. Human gates
accept only explicit evidence file paths and approval metadata; absence is
`NOT_RUN`.
Serialize with Pydantic and validate the output against the JSON Schema in the
test.

- [ ] **Step 5: Run and commit**

```powershell
python -m pytest engine/tests/test_mini_game_certification.py engine/tests/test_mini_game_tool.py -q
git add engine/mini_games/certification.py engine/tests/test_mini_game_certification.py docs/specs/schemas/mini-game-readiness-report.schema.json docs/specs/schemas/mini-game-external-preview-evidence.schema.json docs/skills/arcwright-minigame/scripts/minigame_tool.py
git commit -m "feat(arc): certify minigame readiness"
```

### Task 7: Add Command Wrappers and CI Enforcement

**Files:**

- Modify: `Makefile`
- Modify: `make.cmd`
- Modify: `.github/workflows/ci.yml`
- Test: `engine/tests/test_mini_game_tool.py`

**Interfaces:**

- Consumes: the single helper commands.
- Produces: `minigame-validate`, `minigame-preview`, and `minigame-certify` wrappers plus CI blockers for active packages.

- [ ] **Step 1: Add failing wrapper assertions**

```python
def test_make_wrappers_use_the_canonical_helper():
    makefile = Path("Makefile").read_text()
    assert "minigame-validate:" in makefile
    assert "docs/skills/arcwright-minigame/scripts/minigame_tool.py" in makefile
```

- [ ] **Step 2: Add exact wrappers**

```make
minigame-validate:
	$(PYTHON) docs/skills/arcwright-minigame/scripts/minigame_tool.py validate nightcap/mini_games

minigame-certify:
	$(PYTHON) docs/skills/arcwright-minigame/scripts/minigame_tool.py certify --arc nightcap/couch-race.arc.json --all-registrations --output build/minigame-readiness.json
```

Mirror commands in `make.cmd`. Add CI steps for Python mini-game tests,
production discovery, renderer build, readiness schema validation, and active
package blockers.

- [ ] **Step 3: Run commands locally**

```powershell
python -m pytest engine/tests/test_mini_game_tool.py engine/tests/test_mini_game_certification.py -q
npm --prefix nightcap-web run bundle:mini-games
python docs/skills/arcwright-minigame/scripts/minigame_tool.py validate nightcap/mini_games
git diff --check
```

- [ ] **Step 4: Commit CI enforcement**

```powershell
git add Makefile make.cmd .github/workflows/ci.yml engine/tests/test_mini_game_tool.py
git commit -m "test(arc): enforce minigame certification"
```

### Task 8: Run the Synthetic Developer Walkthrough

**Files:**

- Create: `docs/examples/mini-games/synthetic-host-game/manifest.json`
- Create: `docs/examples/mini-games/synthetic-host-game/definitions/0.1.0.json`
- Create: `docs/guides/mini-game-getting-started.md`
- Create: `docs/roadmap/operations/mini-game-onboarding-walkthrough.md`

**Interfaces:**

- Consumes: the exact CLI workflow and synthetic host contract fixture.
- Produces: one reproducible walkthrough with commands, outputs, elapsed steps, and readiness report path.

- [ ] **Step 1: Execute every onboarding command from a clean temporary directory**

Run scaffold, register, bind, adapter-aware preview, validate, and certify
exactly as written in the canonical skill. Use `host_authoritative`, neutral
story vocabulary, Arcwright protocol fixtures, no Arcwright renderer, and an
external-engine preview evidence fixture whose version and digest match the
package.

- [ ] **Step 2: Record exact command results**

Use this fixed table:

```markdown
| Command | Exit code | Artifact | Confusion observed |
| --- | --- | --- | --- |
| scaffold | 0 | synthetic package | None |
| register | 0 | exact registration | None |
| bind | 0 | story opportunity | None |
| preview | 0 | protocol fixture output plus external preview evidence | None |
| validate | 0 | validation output | None |
| certify | 0 | blocked readiness report with human gates NOT_RUN | None |
```

Replace `None` only with an observed issue and its evidence. Do not infer
external developer usability from an internal walkthrough.

- [ ] **Step 3: Verify and commit documentation**

```powershell
git diff --check
rg -n "Nightcap|Leverage|suspect|clue" docs/examples/mini-games/synthetic-host-game
git add docs/examples/mini-games/synthetic-host-game docs/guides/mini-game-getting-started.md docs/roadmap/operations/mini-game-onboarding-walkthrough.md
git commit -m "docs(arc): document minigame onboarding"
```

Expected: no Nightcap vocabulary in the synthetic example.

### Task 9: Full Verification and Checkpoint

**Files:**

- Modify: `docs/specs/0080-mini-game-onboarding-preview-and-certification.md`
- Modify: `docs/roadmap/index.json`

**Interfaces:**

- Consumes: Tasks 2 through 8 commits and synthetic walkthrough evidence.
- Produces: reviewed onboarding checkpoint and explicit approval before Nightcap package migration.

- [ ] **Step 1: Run the full focused suite**

```powershell
python -m pytest engine/tests/test_mini_game_tool.py engine/tests/test_mini_game_certification.py engine/tests/test_mini_game_documentation.py engine/tests/test_mini_game_models.py -q
npm --prefix nightcap-web test
npm --prefix nightcap-web run typecheck
python docs/skills/arcwright-minigame/scripts/minigame_tool.py validate nightcap/mini_games
git diff --check
```

- [ ] **Step 2: Run architecture review**

Use `arcwright-reviewer`, resolve blocking findings, and rerun affected checks.

- [ ] **Step 3: Reconcile spec and tracker evidence**

Record exact commands, commits, report schema version, walkthrough limits, and
human-gate behavior.

- [ ] **Step 4: Stop for founder checkpoint approval**

Do not begin Nightcap foundation integration without explicit approval.
