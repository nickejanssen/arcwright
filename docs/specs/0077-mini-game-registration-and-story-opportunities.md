> Current version: v0.2
> Last updated: 2026-08-03
> Status: Approved
> Canonical path: docs/specs/0077-mini-game-registration-and-story-opportunities.md

# Reusable Mini-game Packages, Destination Adaptations, and Placement Policies

## References

- ADR: `docs/decisions/0018-mini-game-orchestration-and-execution-adapters.md`
- Architecture: `docs/architecture/03-arc-execution.md`, `docs/architecture/09-developer-api.md`
- Related specs: `docs/specs/0078-mini-game-invocation-and-execution-adapters.md`, `docs/specs/0079-mini-game-results-consequences-theme-and-telemetry.md`, `docs/specs/0080-mini-game-onboarding-preview-and-certification.md`
- Approved design: `docs/superpowers/specs/2026-08-02-mini-game-platform-orchestration-design.md`
- PRD: `docs/prd/02-requirements.md`

## Overview and gate

This spec defines the destination-neutral package, non-destructive destination
adaptation, and composable placement policy. It replaces manual registration
plus fixed trigger fields as the primary developer model. Existing
`MiniGameBinding` values remain readable during migration.

This spec was approved by the founder on 2026-08-03. Implementation still
requires the separate implementation go-ahead.

## Human collaboration contract

**Profiles:** Decision interview, creative collaboration, and independent
execution.

The founder approved package versus adaptation separation, designer-owned
placement authority, composable policies, browser-first onboarding,
non-destructive versioning, and the exact contracts and failure behavior in
this version on 2026-08-03. Implementation remains paused pending the separate
implementation go-ahead.

## Reusable package contract

```python
Slug = Annotated[str, Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")]
SemVer = Annotated[str, Field(pattern=r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")]
Sha256 = Annotated[str, Field(pattern=r"^[a-f0-9]{64}$")]
NamespacedKey = Annotated[
    str,
    Field(pattern=r"^[a-z0-9]+(?:[.-][a-z0-9]+)+$")
]
JsonScalar = str | int | float | bool | None
JsonValue = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]

class CapabilityClaim(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    key: NamespacedKey
    version: SemVer
    parameters: dict[str, JsonValue] = Field(default_factory=dict)

class ParticipationCapabilities(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    active_min_players: int = Field(ge=1, le=64)
    active_max_players: int = Field(ge=1, le=64)
    session_min_players: int = Field(ge=1, le=64)
    session_max_players: int = Field(ge=1, le=64)
    supported_models: tuple[NamespacedKey, ...]
    adaptable_models: tuple[NamespacedKey, ...] = ()

class DurationCapabilities(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    minimum_seconds: int = Field(ge=1)
    recommended_seconds: int = Field(ge=1)
    maximum_seconds: int = Field(ge=1)

class PresentationRole(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    role: NamespacedKey
    required: bool = True
    content_types: tuple[str, ...] = ()

class ReusableMiniGamePackage(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    package_id: Slug
    version: SemVer
    definition_sha256: Sha256
    source_provenance_id: str = Field(min_length=1, max_length=256)
    protocol_version: SemVer
    lifecycle: Literal["draft", "playtest", "active", "retired"]
    participation: ParticipationCapabilities
    duration: DurationCapabilities
    capabilities: tuple[CapabilityClaim, ...]
    story_affordances: tuple[CapabilityClaim, ...]
    configuration_schema_ref: str
    input_schema_ref: str
    result_schema_ref: str
    presentation_roles: tuple[PresentationRole, ...]
    fallback_capabilities: tuple[NamespacedKey, ...]
    extension_values: dict[NamespacedKey, JsonValue] = Field(default_factory=dict)
```

Player and duration minima cannot exceed their maxima. Recommended duration
must be inside the declared range. Capability, affordance, presentation-role,
and extension keys are unique. Extension keys must be registered against a
versioned schema before package validation. Arbitrary unregistered JSON does
not become executable behavior.

Arcwright may infer a Draft package from an imported browser game. Inference
is proposed authoring data, never runtime authority. The developer confirms or
corrects high-impact and unresolved facts before the package becomes Reusable.

## Destination adaptation contract

```python
class ArtifactVersionRef(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    artifact_id: Slug
    version: SemVer
    sha256: Sha256

class AdaptationApproval(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    approved_by: str = Field(min_length=1, max_length=256)
    approved_at: datetime
    evidence_refs: tuple[str, ...]

class DestinationAdaptation(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    adaptation_id: Slug
    version: SemVer
    package: ArtifactVersionRef
    destination_game_id: Slug
    destination_version: SemVer
    participation_profile_ref: ArtifactVersionRef
    experience_design_system_ref: ArtifactVersionRef
    configuration_profile_ref: ArtifactVersionRef
    result_mapping_profile_ref: ArtifactVersionRef
    compatible_profile_ids: tuple[NamespacedKey, ...]
    provenance_parent: ArtifactVersionRef | None = None
    generated_change_set_ref: str | None = None
    approval: AdaptationApproval | None = None
    lifecycle: Literal["draft", "playtest", "active", "retired"]
```

An adaptation references one exact package version and never overwrites that
package or its imported source. Generated changes occur in a private derivative
workspace, preserve provenance, and remain reversible. Promotion to playtest or
active requires explicit approval. Updating the package produces a compatibility
report; it never silently changes an adaptation.

Arcwright-powered adaptation capabilities require the licensed Arcwright
runtime. Developers retain their original source and assets. Arcwright engine,
adaptation, orchestration, and platform source is not exportable through this
contract.

## Composable placement policy

```python
class PolicyPredicate(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    node_type: Literal["predicate"] = "predicate"
    fact_key: NamespacedKey
    operator: Literal["eq", "ne", "lt", "lte", "gt", "gte", "contains", "in"]
    expected: JsonValue

class PolicyAll(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    node_type: Literal["all"] = "all"
    children: tuple["PolicyExpression", ...]

class PolicyAny(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    node_type: Literal["any"] = "any"
    children: tuple["PolicyExpression", ...]

class PolicyNot(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    node_type: Literal["not"] = "not"
    child: "PolicyExpression"

PolicyExpression = Annotated[
    PolicyPredicate | PolicyAll | PolicyAny | PolicyNot,
    Field(discriminator="node_type"),
]

class PlacementAnchor(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    anchor_type: NamespacedKey
    anchor_ref: str = Field(min_length=1, max_length=256)
    position: NamespacedKey

class AuthorityGrant(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    source: Literal["designer_required", "engine_selected", "host_requested", "player_requested"]
    condition: PolicyExpression | None = None
    request_policy_ref: ArtifactVersionRef | None = None

class RecurrencePolicy(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    minimum_invocations: int = Field(default=0, ge=0, le=64)
    maximum_invocations: int = Field(default=1, ge=1, le=64)
    cooldown_seconds: int = Field(default=0, ge=0)
    lookback_count: int = Field(default=0, ge=0, le=64)

class CandidatePolicy(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    adaptation_refs: tuple[ArtifactVersionRef, ...] = ()
    required_capabilities: tuple[CapabilityClaim, ...] = ()
    selection_strategy: NamespacedKey
    strategy_parameters: dict[str, JsonValue] = Field(default_factory=dict)

class TimingPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    mode: NamespacedKey
    maximum_wait_seconds: int | None = Field(default=None, ge=0)

class MiniGamePlacementPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    policy_id: Slug
    version: SemVer
    anchors: tuple[PlacementAnchor, ...]
    authority_grants: tuple[AuthorityGrant, ...]
    eligibility: PolicyExpression | None
    recurrence: RecurrencePolicy
    candidates: CandidatePolicy
    timing: TimingPolicy
    fallback_policy_ref: ArtifactVersionRef
    consequence_profile_ref: ArtifactVersionRef
    public_context_keys: tuple[NamespacedKey, ...] = ()
    enabled: bool = True
```

At least one anchor, authority grant, and candidate selector is required.
`minimum_invocations` cannot exceed `maximum_invocations`. A player-requested
grant is invalid without a game-owned request policy, and remains non-executable
until a separately approved authenticated request contract exists. This
preserves the future Grill currency seam without implementing its economy.

The designer owns every anchor, authority grant, candidate set, consequence,
and fallback. Arcwright may explain, validate, simulate, and recommend a
policy. It cannot broaden authority or change a designer-required placement.

## Deterministic evaluation

The selector evaluates only public canonical facts allowlisted by the policy.
Eligibility is the intersection of:

```text
policy enabled
AND an anchor is active
AND an authority grant is valid for the caller or engine
AND the eligibility expression is true
AND recurrence and cooldown allow another invocation
AND the exact adaptation and package versions are active or playtest-compatible
AND required capability and profile negotiation succeeds
AND required content and fallback are available
```

The initial registered selection strategies are
`arcwright.authored-order.v1` and `arcwright.session-seeded-rotation.v1`.
Authored order preserves the declared adaptation order. Session-seeded rotation
canonicalizes eligible adaptations by ID, excludes lookback entries only when
an alternative remains, then chooses the lowest tuple of
`SHA-256(session_id:policy_id:adaptation_id)` and adaptation ID. Selection and
reason are persisted. Re-evaluating the same state returns the same invocation.

No model call selects the game, trigger, placement, winner, or consequence.

## Legacy compatibility

Legacy `MiniGameBinding {binding_id, game_id, version}` remains readable. A
compatibility translator creates an in-memory exact package reference,
destination adaptation, designer-required beat-entry placement policy, and
existing fallback. A beat uses either legacy bindings or placement policies,
never both. New authoring never writes legacy bindings.

## Acceptance criteria

- [ ] Imported source remains unchanged; every adaptation is versioned,
  provenance-linked, reviewable, and reversible.
- [ ] Package capabilities are destination-neutral and namespaced.
- [ ] One package supports multiple independently certified destination
  adaptations without copying the mechanic.
- [ ] The designer can require an exact moment, constrain a beat or window,
  delegate bounded selection, allow a future request, or compose those modes.
- [ ] Arcwright never receives placement authority the designer did not grant.
- [ ] Scene can rotate Crime Scene Smash and Scene Sweep without engine code or
  a new schema field.
- [ ] The Grill supports exact Beat 3 placement and a disabled future
  any-beat player-request policy in the same model.
- [ ] Deterministic selection and reason replay exactly.
- [ ] Legacy bindings remain readable during migration.
- [ ] A synthetic non-Nightcap browser game validates without Nightcap terms.

## Tests

Model tests cover package bounds, extension registration, immutable references,
adaptation provenance, approval gates, policy expression recursion, authority
grants, recurrence, request-policy rejection, candidate intersection,
deterministic rotation, replay, fallback, and legacy translation. Integration
tests prove exact placement, delegated selection, Scene rotation, and a
synthetic non-Nightcap destination.

## Approval record

The founder approved the exact package, adaptation, policy-expression,
authority, selection, and migration contracts in this version on 2026-08-03.
Implementation remains subject to a separate go-ahead.
