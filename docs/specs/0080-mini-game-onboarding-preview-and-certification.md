> Current version: v0.2
> Last updated: 2026-08-03
> Status: Approved
> Canonical path: docs/specs/0080-mini-game-onboarding-preview-and-certification.md

# Browser Mini-game Onboarding, Local Playtest, and Visual Readiness

## References

- ADR: `docs/decisions/0018-mini-game-orchestration-and-execution-adapters.md`
- Architecture: `docs/architecture/09-developer-api.md`, `docs/architecture/14-architecture-validation.md`
- Related specs: `docs/specs/0077-mini-game-registration-and-story-opportunities.md` through `docs/specs/0079-mini-game-results-consequences-theme-and-telemetry.md`
- Canonical skill: `docs/skills/arcwright-minigame/SKILL.md`
- Existing helper: `docs/skills/arcwright-minigame/scripts/minigame_tool.py`
- Existing template: `nightcap/mini_games/_template/`
- Approved design: `docs/superpowers/specs/2026-08-02-mini-game-platform-orchestration-design.md`

## Overview and gate

This approved spec turns the existing procedural mini-game lifecycle into an
assisted browser-first golden path. It extends the existing skill, helper,
loader, runtime, preview kit, fixtures, and validators. It must not create a
second package format, schema authority, renderer registry, certification
system, or no-code-only backend.

The founder approved this version on 2026-08-03. Implementation still requires
the separate implementation go-ahead.

## Human collaboration contract

**Profiles:** Decision interview, creative collaboration, facilitated live
operation, and independent execution.

The founder approved the timing targets, destination-first recommendation,
managed-hosting default, non-destructive adaptation, permission-first
generation, progressive readiness, local playtest lab, visual production lab,
and the exact contracts and failure behavior in this version on 2026-08-03.
Gameplay, presentation, and production promotion retain their separate human
gates. Implementation remains paused pending the separate implementation
go-ahead.

## Product-level timing requirements

| Cohort | Target | Maximum |
| --- | ---: | ---: |
| First-time browser developer | 10 to 15 minutes | 20 minutes |
| Returning browser developer | 5 to 10 minutes | 15 minutes |

The clock begins when the developer starts an import and ends when one
destination adaptation reaches Playtest-ready. Playtest-ready means integrated,
story-aware, styled, simulated, locally testable, and passing automated
preflight. It does not imply Production-ready certification.

Timing targets are met through analysis, generated adapters, reusable
destination profiles, defaults, and progressive disclosure. A gate cannot be
removed, auto-passed, or mislabeled to meet the target.

## Supported Horizon 1 intake

```python
class BrowserImportSource(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    source_type: Literal["static_bundle", "hosted_url"]
    source_ref: str = Field(min_length=1, max_length=2048)
    source_sha256: Sha256 | None = None
    source_access: Literal["build_only", "source_and_build"]

class MiniGameOnboardingRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    source: BrowserImportSource
    destination_game_id: str | None = Field(default=None, pattern=_SLUG_PATTERN)
    hosting_preference: Literal["managed", "external"] = "managed"
    cohort: Literal["first_time", "returning"]
```

Managed hosting is the recommended default. A static bundle is uploaded into a
private, tenant-scoped import workspace. A hosted URL is analyzed through the
browser bridge and remains externally hosted unless the developer later
supplies a managed bundle. Import never exposes credentials or secrets to the
game and never copies source into telemetry.

The first screen asks where the developer wants to use the game first. A
destination is recommended but optional. Skipping it creates a reusable Draft
tested against representative destination-neutral configurations.

## Golden path

1. **Import.** Launch the browser game in a private sandbox and verify basic
   lifecycle, input, output, asset, network, and surface behavior.
2. **Analyze.** Generate a Draft reusable package, uncertainty report, and
   smallest set of confirmation questions.
3. **Confirm intent.** Ask what the game does for players and story in plain
   language. Compile the response into inspectable package affordances and a
   destination placement policy Draft.
4. **Adapt participation.** When source and destination player models differ,
   generate one recommended playable adaptation and up to two meaningful
   alternatives. Explain social, pacing, fairness, and surface tradeoffs.
5. **Ask before generation.** Request category-level permission before
   generating code, art, animation, audio, copy, or configuration. Preserve
   denied and immutable assets.
6. **Apply destination fit.** Map semantic presentation roles into the
   experience design system and map typed results into bounded story
   consequences.
7. **Compose placement.** Let the designer require an exact moment, constrain a
   beat or window, delegate bounded selection, allow a future request, or
   combine these controls. Arcwright explains but never broadens authority.
8. **Simulate and test.** Show deterministic selection reasons, rejected
   alternatives, pacing effects, multi-surface behavior, and one-click local
   playtest.
9. **Report readiness.** Show the current state, evidence, blocker, smallest
   next action, and elapsed onboarding time.

Structured contracts are available behind an advanced view and through CLI
and SDK. They are not required reading for the default flow.

## Adaptation workspace

```python
class GeneratedChangeSet(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    change_set_id: str
    source_provenance_id: str
    permission_receipt_id: str
    categories: tuple[str, ...]
    changed_artifact_refs: tuple[str, ...]
    generated_at: datetime
    generator_policy_version: str
    review_status: Literal["draft", "approved", "rejected", "superseded"]

class AdaptationWorkspace(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    workspace_id: UUID
    package_ref: ArtifactVersionRef
    destination_game_id: str | None
    generated_change_sets: tuple[GeneratedChangeSet, ...]
    original_source_unchanged: Literal[True]
```

Every generated change is inspectable, reversible, and provenance-linked.
Arcwright never overwrites the imported original. Arcwright-powered
adaptations require the licensed runtime. The API does not export Arcwright
engine, orchestration, adaptation, or platform source.

## Progressive readiness resource

```python
class ReadinessState(str, Enum):
    imported = "imported"
    reusable = "reusable"
    playtest_ready = "playtest_ready"
    production_ready = "production_ready"

class ReadinessEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    evidence_id: str
    category: NamespacedKey
    status: Literal["pass", "fail", "not_run", "blocked", "human_review"]
    summary: str
    artifact_refs: tuple[str, ...] = ()
    observed_at: datetime | None = None

class MiniGameReadinessReport(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    report_id: str
    package_ref: ArtifactVersionRef
    adaptation_ref: ArtifactVersionRef | None
    current_state: ReadinessState
    state_label: str
    state_explanation: str
    next_action: str | None
    estimated_next_action_minutes: int | None = Field(default=None, ge=0)
    blockers: tuple[str, ...]
    evidence: tuple[ReadinessEvidence, ...]
    first_time_elapsed_ms: int | None = Field(default=None, ge=0)
    returning_elapsed_ms: int | None = Field(default=None, ge=0)
```

Every state is visible in plain language. UI uses text, iconography, and
structure in addition to color. A state change requires corresponding evidence
and cannot be inferred from package existence.

## Playtest-ready local lab

The local lab provides one button and one equivalent CLI command to:

- launch managed local hosting with hot reload;
- create deterministic sample sessions and simulated players;
- open phone, shared-focus, host, and destination-defined surface previews;
- display QR codes for real devices on the local network;
- run active, completed, timeout, error, cancel, pause, reconnect, and fallback
  fixtures;
- record, replay, reset, and compare an invocation;
- show provisional result and consequence mapping in the simulation ledger;
- display selection explanation and rejected candidates; and
- export a privacy-safe local evidence bundle.

The lab performs no production model call and applies no production canonical
consequence. A persistent banner identifies preview-only authority.

## Production-ready visual lab

The production lab groups internal gates into understandable outcomes:

1. **Plays correctly:** rules, player counts, timing, scoring, fairness, and
   deterministic authority.
2. **Fits the story:** placement policy, consequence mapping, pacing,
   transition, fallback, and replay safety.
3. **Feels native:** experience design system, graphics, animation, audio,
   copy, surfaces, accessibility, and reduced-motion behavior.
4. **Survives reality:** reconnect, pause, resume, timeout, host loss,
   rollback, performance, privacy, security, and telemetry.
5. **Approved by people:** gameplay review, creative approval, real-device
   evidence, real-player evidence, and destination-owner sign-off.

The visual lab provides a gate map, multi-surface timeline, scenario and
player-count matrix, side-by-side version comparison, recorded evidence,
selection explanations, and one-click staged rehearsal. It always distinguishes
automated checks from human evidence.

Production-ready requires all applicable internal gates to pass. Missing human
evidence remains `not_run` or `human_review`, never an inferred pass. Package
readiness and each destination adaptation's readiness are independent.

## Shared authoring API

Studio, CLI, SDK, and the canonical skill use the same resources:

```text
POST /v1/minigames/imports
GET  /v1/minigames/imports/{import_id}
POST /v1/minigames/packages/{package_id}/confirm
POST /v1/minigames/adaptations
POST /v1/minigames/adaptations/{adaptation_id}/permissions
POST /v1/minigames/adaptations/{adaptation_id}/variants
POST /v1/minigames/placement-policies/simulate
POST /v1/minigames/local-labs
GET  /v1/minigames/readiness/{artifact_id}
POST /v1/minigames/rehearsals
POST /v1/minigames/promotions
```

Route handlers validate, call authoring or engine services, and return typed
resources. They contain no arc logic, adaptation generation logic, or
mechanic-specific branches.

The existing helper gains thin commands over these resources. Existing
`scaffold`, `validate`, package loading, renderer kit, fixtures, and discovery
are extended rather than copied. Pydantic engine models remain the schema
authority.

## Independent developer proof

A synthetic non-Nightcap browser game must complete the full destination-first
flow without Nightcap code or vocabulary. Validation has two separate cohorts:

- an internal deterministic fixture proving protocol behavior; and
- a first-time developer who did not build the platform, proving usability.

The usability session records elapsed time, interventions, misunderstood
concepts, corrections, state reached, local playtest success, and qualitative
confidence. The platform cannot claim the first-time target from an internal
agent-only walkthrough.

## Promotion and rollback

Definitions become immutable at playtest. Changes require a new semantic
version and digest. Production promotion requires a Production-ready adaptation
report and explicit destination-owner approval. Retired versions receive no new
invocations but remain available for resume, replay, and audit. Rollback points
new invocations to a previously certified exact package and adaptation pair;
it never rewrites immutable artifacts.

## Acceptance criteria

- [ ] The existing skill, helper, template, loader, renderer kit, fixtures, and
  validators are extended rather than duplicated.
- [ ] A first-time browser developer reaches Playtest-ready in 10 to 15 minutes
  target and 20 minutes maximum without editing Arcwright engine code.
- [ ] A returning browser developer reaches Playtest-ready in 5 to 10 minutes
  target and 15 minutes maximum.
- [ ] Managed hosting is the default and external hosting uses the same browser
  protocol.
- [ ] Destination-first and reusable-first paths produce the same canonical
  package resources.
- [ ] Multiplayer mismatch produces one recommended playable adaptation and no
  more than two alternatives.
- [ ] Generation asks permission first and never overwrites the original.
- [ ] Playtest-ready is locally testable through one button or command without
  cloud deployment.
- [ ] Production-ready is easy to visualize and separates automated from human
  evidence.
- [ ] Preview-only results cannot apply production consequences.
- [ ] Studio, CLI, SDK, and skill use the same APIs and artifacts.
- [ ] A first-time non-Nightcap developer proves the usability claim.
- [ ] Promotion and rollback use exact package and adaptation versions.

## Tests

Tests cover private import workspaces, source preservation, analysis
uncertainty, confirmation, participation alternatives, permission denial,
immutable assets, exact-version managed hosting, local lab fixtures, QR/device
bootstrap, preview-result isolation, readiness state transitions, human-evidence
semantics, authoring API thinness, timing telemetry, promotion, rollback, and
the synthetic non-Nightcap walkthrough.

## Approval record

The founder approved the exact intake types, golden-path stages, readiness
resource, local lab, production lab, authoring API, timing evidence, and
promotion contract in this version on 2026-08-03. Implementation remains
subject to a separate go-ahead.
