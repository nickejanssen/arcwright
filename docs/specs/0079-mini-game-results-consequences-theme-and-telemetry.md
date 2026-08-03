> Current version: v0.2
> Last updated: 2026-08-03
> Status: Approved
> Canonical path: docs/specs/0079-mini-game-results-consequences-theme-and-telemetry.md

# Mini-game Results, Consequences, Theme, and Telemetry

## References

- ADR: `docs/decisions/0018-mini-game-orchestration-and-execution-adapters.md`
- Architecture: `docs/architecture/04-knowledge-graph.md`, `docs/architecture/08-event-system.md`, `docs/architecture/10-content-safety.md`, `docs/architecture/11-telemetry.md`, `docs/architecture/13-cost-model.md`
- Related specs: `docs/specs/0077-mini-game-registration-and-story-opportunities.md`, `docs/specs/0078-mini-game-invocation-and-execution-adapters.md`

## Overview and gate

This approved spec defines authority-bound gameplay facts, bounded authored
consequences, destination experience design systems, permission-first
generation, privacy-safe telemetry, and optional generation budgets. The
founder approved this version on 2026-08-03. Implementation still requires the
separate implementation go-ahead.

## Human collaboration contract

**Profiles:** Decision interview and independent execution. The founder
approved the consequence vocabulary, privacy boundary, generation fallback,
and certification evidence posture on 2026-08-03. Implementation remains
paused pending the separate implementation go-ahead.

## Result contract

```python
class MiniGameResultEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")
    run_id: UUID
    adaptation_id: str = Field(pattern=_SLUG_PATTERN)
    adaptation_version: str = Field(pattern=_SEMVER_PATTERN)
    package_id: str = Field(pattern=_SLUG_PATTERN)
    package_version: str = Field(pattern=_SEMVER_PATTERN)
    result_schema_version: str = Field(pattern=_SEMVER_PATTERN)
    authority_profile_id: str
    authority_proof_ref: str | None = None
    transcript_sha256: str | None = Field(default=None, pattern=r"^[a-f0-9]{64}$")
    status_revision: int = Field(ge=0)
    idempotency_key: str = Field(min_length=1, max_length=256)
    completion_status: Literal["completed", "timed_out", "cancelled"]
    duration_ms: int = Field(ge=0)
    participant_results: dict[str, dict[str, Any]] = Field(default_factory=dict)
    team_results: dict[str, dict[str, Any]] = Field(default_factory=dict)
    semantics: dict[str, int | float | bool | str] = Field(default_factory=dict)
    evidence_ref: str | None = Field(default=None, max_length=512)
```

Results report gameplay facts. They cannot contain callbacks, code, SQL,
arbitrary state patches, raw knowledge graphs, secrets, or private answers.
Identity, version, profile, proof, and transcript fields must match the
invocation and negotiated authority requirements. Preview-only results are
stored in a non-production simulation ledger and cannot reach the consequence
dispatcher.

## Consequence contract and recovery

```python
class ResourceConsequenceTarget(BaseModel):
    model_config = ConfigDict(extra="forbid")
    resource_id: str = Field(pattern=_SLUG_PATTERN)
    subject: Literal["participant", "team", "session"]

class ScoreConsequenceTarget(BaseModel):
    model_config = ConfigDict(extra="forbid")
    score_id: str = Field(pattern=_SLUG_PATTERN)
    subject: Literal["participant", "team"]

class NumericConsequenceRule(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rule_id: str = Field(pattern=_SLUG_PATTERN)
    semantic_key: str = Field(pattern=_SLUG_PATTERN)
    multiplier: FiniteFloat = 1.0
    minimum: FiniteFloat
    maximum: FiniteFloat

    @model_validator(mode="after")
    def validate_bounds(self) -> Self:
        if self.minimum > self.maximum:
            raise ValueError("minimum cannot exceed maximum")
        return self

class ResourceDeltaRule(NumericConsequenceRule):
    action: Literal["resource_delta"]
    target: ResourceConsequenceTarget

class ScoreDeltaRule(NumericConsequenceRule):
    action: Literal["score_delta"]
    target: ScoreConsequenceTarget

class KnowledgeAssertionRule(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rule_id: str = Field(pattern=_SLUG_PATTERN)
    semantic_key: str = Field(pattern=_SLUG_PATTERN)
    action: Literal["knowledge_assertion"]
    fact_template_id: str = Field(pattern=_SLUG_PATTERN)
    recipient: Literal["participant", "team", "session"]

class ObligationProgressRule(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rule_id: str = Field(pattern=_SLUG_PATTERN)
    semantic_key: str = Field(pattern=_SLUG_PATTERN)
    action: Literal["obligation_progress"]
    obligation_id: str = Field(pattern=_SLUG_PATTERN)
    progress_mode: Literal["advance", "resolve"]

class ContentEventRule(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rule_id: str = Field(pattern=_SLUG_PATTERN)
    semantic_key: str = Field(pattern=_SLUG_PATTERN)
    action: Literal["content_event"]
    event_template_id: str = Field(pattern=_SLUG_PATTERN)
    target_audience: Literal["all", "specific_player", "host_only", "shared_display"]

MiniGameConsequenceRule = Annotated[
    ResourceDeltaRule
    | ScoreDeltaRule
    | KnowledgeAssertionRule
    | ObligationProgressRule
    | ContentEventRule,
    Field(discriminator="action"),
]

class MiniGameConsequenceProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")
    profile_id: str = Field(pattern=_SLUG_PATTERN)
    rules: list[MiniGameConsequenceRule]
```

The arc owns profiles. Every numeric score/resource rule requires finite
minimum and maximum values and rejects `minimum > maximum`, NaN, infinity, or
a non-finite multiplier. The dispatcher multiplies the finite semantic value,
truncates toward zero for integer canonical services, then clamps inclusively
to the authored bounds. It never executes an unbounded numeric action.

Targets are action-specific models, not arbitrary strings. Arc validation
resolves every `resource_id`, `score_id`, `fact_template_id`, `obligation_id`,
and `event_template_id` against the corresponding authored registry before a
session can start. Knowledge, obligation, and content-event actions are
dedicated typed variants and cannot carry numeric bound or multiplier fields.
The dispatcher accepts only declared semantic keys and delegates to existing
canonical services. Unknown semantics or target identifiers cannot mutate
state.

Recovery state is `pending_result -> pending_application -> applied`. The dispatcher persists each `rule_id` before the next rule. A crash after one rule resumes by skipping recorded rules, preventing double application. Result receipt and consequence application are separate durable records. Required story evidence remains available on failure; game rewards are an edge, never a solvability gate.

```python
@dataclass(frozen=True)
class ConsequenceApplication:
    run_id: UUID
    applied_rule_ids: tuple[str, ...]
    skipped_rule_ids: tuple[str, ...]
    resource_deltas: dict[str, int]
    score_deltas: dict[str, int]
    duplicate: bool

class MiniGameConsequenceDispatcher:
    async def apply(
        self,
        db: AsyncSession,
        run: MiniGameRun,
        profile: MiniGameConsequenceProfile,
        result: MiniGameResultEnvelope,
    ) -> ConsequenceApplication: ...
```

## Public, private, and generated context

`MiniGamePlacementPolicy.public_context_keys` is an allowlist. Only allowlisted,
public-safe values may enter package resolution or generation. Private answers,
hidden truth, killer identity, unrevealed evidence, raw prompts, and raw
knowledge state remain outside generation and telemetry. Every AI character
generation still performs its mandatory knowledge query through existing
services.

```python
class MiniGameGenerationBudget(BaseModel):
    model_config = ConfigDict(extra="forbid")
    max_attempts: int = Field(default=2, ge=1, le=2)
    max_latency_ms: int = Field(default=2500, ge=100)
    deterministic_fallback: Literal["authored_content", "cancel_invocation"]
```

Generation is optional, provider-agnostic, cost-logged, safety-checked, and presentation/content-only after deterministic state resolution. Exhaustion uses the configured authored fallback or cancellation; it cannot change game selection, answer authority, score, truth, or consequence.

## Destination experience design system

```python
class ExperienceDesignSystem(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    system_id: str = Field(pattern=_SLUG_PATTERN)
    version: str = Field(pattern=_SEMVER_PATTERN)
    semantic_tokens_schema_ref: str
    typography_profile_ref: str
    art_direction_profile_ref: str
    motion_profile_ref: str
    audio_profile_ref: str
    copy_voice_profile_ref: str
    surface_layout_profile_refs: tuple[str, ...]
    accessibility_profile_ref: str
    intensity_bounds: dict[str, FiniteFloat]
    immutable_role_ids: tuple[str, ...] = ()

class GenerationPermissionReceipt(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    receipt_id: str = Field(min_length=1, max_length=256)
    destination_game_id: str = Field(pattern=_SLUG_PATTERN)
    adaptation_id: str = Field(pattern=_SLUG_PATTERN)
    approved_categories: tuple[Literal[
        "code", "art", "animation", "audio", "copy", "configuration"
    ], ...]
    denied_asset_refs: tuple[str, ...] = ()
    remember_for_project: bool = False
    approved_by: str = Field(min_length=1, max_length=256)
    approved_at: datetime
```

The destination design system maps package semantic presentation roles to
destination assets and behavior. The Python engine receives only a validated,
surface-neutral projection containing semantic roles, accessibility, locale,
intensity, attention, and public-safe context. No generic engine contract names
TV, phone, Nightcap, CSS, or engine-specific assets.

Arcwright must request permission before generating code, art, animation,
audio, copy, or configuration. The request explains the proposed categories,
source assets, reason, and preservation behavior. Generated output remains a
private Draft linked to its permission receipt and source provenance. Locked
or denied assets are never replaced. Promotion requires separate adaptation
approval.

## Telemetry

Emit append-only events for `mini_game_placement_policy_evaluated`,
`mini_game_selected`, `mini_game_started`, `mini_game_adaptation_selected`,
`mini_game_completed`, `mini_game_timed_out`, `mini_game_cancelled`,
`mini_game_result_rejected`, `mini_game_consequence_applied`,
`mini_game_fallback_used`, and `mini_game_reconnected`. Legacy
`mini_game_opportunity_evaluated` remains readable during migration.

The authoring plane also emits privacy-reviewed events for
`mini_game_import_started`, `mini_game_import_analyzed`,
`mini_game_package_confirmed`, `mini_game_adaptation_generated`,
`mini_game_generation_permission_decided`, `mini_game_local_preview_started`,
`mini_game_readiness_changed`, and `mini_game_onboarding_completed`.
Onboarding completion records first-time or returning cohort, elapsed
milliseconds, state reached, intervention count, and reason codes. It excludes
source, assets, prompts, generated output, and private project content.

Allowed fields are neutral IDs, capability profiles, package, adaptation, and schema versions, lifecycle
status, duration, player count, reason code, fallback marker, certification
references, privacy-reviewed aggregate adaptation bands, and selected approved
format ID. Excluded fields are raw submissions, result semantics payloads,
prompts, generated text, runtime state, raw adaptation input context,
per-player signal values, private story context, and knowledge state.

```python
async def record_mini_game_event(
    db: AsyncSession,
    *,
    session_id: UUID,
    event_type: str,
    run: MiniGameRun,
    reason_code: str | None = None,
    duration_ms: int | None = None,
    player_count: int | None = None,
) -> None: ...
```

## Acceptance criteria and tests

- [ ] Result identity, version, revision, and idempotency are validated before persistence.
- [ ] Authority profile, proof, and transcript requirements are validated
  before a result can reach production consequences.
- [ ] Only authored, bounded consequence rules can mutate canonical services.
- [ ] Every score/resource rule has finite required bounds with `minimum <= maximum`; NaN, infinity, missing bounds, and arbitrary target strings are rejected.
- [ ] Knowledge, obligation, and content-event rules use dedicated typed variants whose identifiers resolve against authored registries.
- [ ] Crash recovery applies every rule exactly once.
- [ ] Public/private context and audience filtering prevent hidden-data leakage.
- [ ] Destination styling uses semantic roles and remains surface-neutral to
  the engine.
- [ ] Generation is permission-first, provenance-linked, reversible, and
  blocked from replacing immutable or denied assets.
- [ ] Generation has a two-attempt maximum and deterministic authored fallback.
- [ ] Telemetry covers lifecycle and certification without private content.
- [ ] Onboarding telemetry measures the approved time targets without storing
  imported source or private generated content.
- [ ] Loss, timeout, cancellation, invalid generated content, and adapter failure preserve the authored story path.

Tests cover consequence clamping and replay, unknown semantics, crash recovery,
preview-result exclusion, authority proof mismatch, privacy allowlists, safety
fallback, permission denial, immutable assets, telemetry field exclusions,
onboarding timing, and game-agnostic design-system forwarding.

## Approval record

The founder approved the named consequence actions, per-rule crash recovery,
public-safe context allowlist, destination design-system contract,
permission-receipt contract, and two-attempt authored-fallback generation
budget in this version on 2026-08-03. Implementation remains subject to a
separate go-ahead.
