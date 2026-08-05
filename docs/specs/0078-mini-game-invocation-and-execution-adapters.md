> Current version: v0.2
> Last updated: 2026-08-03
> Status: Approved
> Canonical path: docs/specs/0078-mini-game-invocation-and-execution-adapters.md

# Mini-game Invocation, Capability Negotiation, and Result Authority

## References

- ADR: `docs/decisions/0018-mini-game-orchestration-and-execution-adapters.md`
- Architecture: `docs/architecture/03-arc-execution.md`, `docs/architecture/05-session-persistence.md`, `docs/architecture/08-event-system.md`, `docs/architecture/09-developer-api.md`
- Related specs: `docs/specs/0077-mini-game-registration-and-story-opportunities.md`, `docs/specs/0079-mini-game-results-consequences-theme-and-telemetry.md`, `docs/specs/0080-mini-game-onboarding-preview-and-certification.md`

## Overview and gate

This spec separates hosting, execution, result authority, presentation, and
distribution. It defines capability negotiation, canonical invocation,
browser sandbox restrictions, managed transcript validation, authenticated
external authority, exact-version recovery, and future profile invariants.

This spec was approved by the founder on 2026-08-03. Implementation still
requires the separate implementation go-ahead.

## Human collaboration contract

**Profiles:** Decision interview and independent execution.

The founder approved capability-negotiated profiles, browser-first managed
hosting, non-authoritative local playtest, deterministic managed production,
authenticated external production, room for future verified runtimes, and the
exact serialized profiles and failure behavior on 2026-08-03. Implementation
remains paused pending the separate implementation go-ahead.

## Capability profile registry

```python
class CapabilityProfileFamily(str, Enum):
    hosting = "hosting"
    execution = "execution"
    result_authority = "result_authority"
    presentation = "presentation"
    distribution = "distribution"

class CapabilityProfileRef(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    family: CapabilityProfileFamily
    profile_id: NamespacedKey
    version: SemVer

class CapabilityProfileDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    ref: CapabilityProfileRef
    protocol_version: SemVer
    provided_capabilities: tuple[CapabilityClaim, ...]
    required_capabilities: tuple[CapabilityClaim, ...] = ()
    proof_schema_ref: str | None = None
    configuration_schema_ref: str
    lifecycle: Literal["experimental", "playtest", "active", "retired"]

class NegotiatedExecutionProfiles(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    hosting: CapabilityProfileRef
    execution: CapabilityProfileRef
    result_authority: CapabilityProfileRef
    presentation: tuple[CapabilityProfileRef, ...]
    distribution: CapabilityProfileRef
```

The registry is closed and code-reviewed. A profile definition is declarative
metadata and cannot load arbitrary code. Negotiation requires matching family,
compatible protocol version, active lifecycle, satisfied requirements, and an
exact profile allowed by the destination adaptation. Negotiation failure uses
the authored fallback and never chooses a weaker authority profile silently.

Horizon 1 registers these profile IDs:

```text
arcwright.hosting.local-browser.v1
arcwright.hosting.managed-browser.v1
arcwright.hosting.external-browser.v1
arcwright.execution.browser-bridge.v1
arcwright.execution.legacy-python-mechanic.v1
arcwright.authority.preview-only.v1
arcwright.authority.transcript-reducer.v1
arcwright.authority.external-backend.v1
arcwright.presentation.browser-surface.v1
arcwright.distribution.private.v1
```

These are initial profiles, not a fixed list in package or placement schemas.

## Permanent production authority invariants

Every active result-authority profile must prove:

1. producer identity and authorization;
2. exact session, invocation, package, adaptation, and profile versions;
3. input provenance and one-time result identity;
4. deterministic replay or independent verification;
5. the bounded consequence classes the profile may request;
6. revocation and retirement status;
7. append-only audit evidence; and
8. rollback and recovery behavior.

An untrusted browser claim alone never changes score, currency, evidence,
knowledge, winners, or canonical story state.

## Canonical invocation

```python
class AuthorityProofRef(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    proof_id: str = Field(min_length=1, max_length=256)
    profile: CapabilityProfileRef
    proof_sha256: Sha256

class MiniGameInvocationRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    run_id: UUID
    session_id: UUID
    placement_policy: ArtifactVersionRef
    adaptation: ArtifactVersionRef
    package: ArtifactVersionRef
    profiles: NegotiatedExecutionProfiles
    result_schema_version: SemVer
    selection_reason: str = Field(min_length=1, max_length=2048)
    authority_source: Literal["designer_required", "engine_selected", "host_requested", "player_requested"]
    resolved_snapshot_sha256: Sha256
    status: Literal["pending", "active", "paused", "completed", "timed_out", "cancelled"]
    status_revision: int = Field(ge=0)
    deadline_at: datetime | None
    remaining_duration_ms: int | None = Field(default=None, ge=0)
    authority_proof: AuthorityProofRef | None = None
    result_identity: str | None = None
    consequence_state: Literal["not_received", "pending", "applying", "applied", "failed"]
```

The persisted invocation also retains the immutable resolved snapshot and
profile configurations. Public projections expose only authorized runtime and
presentation state:

```python
class MiniGameInvocationResponse(BaseModel):
    run_id: UUID
    package_id: str
    package_version: str
    adaptation_id: str
    adaptation_version: str
    status: str
    status_revision: int
    deadline_at: datetime | None
    runtime_state: dict[str, JsonValue] = Field(default_factory=dict)
    presentation: dict[str, JsonValue] = Field(default_factory=dict)
    my_submissions: list[MiniGameSubmissionResponse] = Field(default_factory=list)
```

Audience filtering produces `runtime_state`; generic transport never exposes
another player's private state. Browser loading uses exact package and
adaptation versions, never `latest`.

## Preview-only browser authority

`arcwright.authority.preview-only.v1` supports local analysis and controlled
playtests. It may emit provisional results and exercise destination mappings in
a non-production simulation ledger. It cannot request or apply production
consequences. The API and readiness UI mark every invocation and result
`NON_AUTHORITATIVE_PREVIEW`.

Attempting to use this profile in an active production adaptation is a
validation failure, not a warning.

## Managed transcript authority

Managed browser production records accepted input events and computes results
through an approved deterministic reducer:

```python
class TranscriptEvent(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    sequence: int = Field(ge=0)
    participant_id: UUID | None
    action_type: NamespacedKey
    payload: dict[str, JsonValue]
    received_at: datetime
    state_revision: int = Field(ge=0)

class TranscriptResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    transcript_sha256: Sha256
    reducer_id: NamespacedKey
    reducer_version: SemVer
    result_payload: dict[str, JsonValue]

class DeterministicMiniGameReducer(Protocol):
    reducer_id: str
    version: str

    def initial_state(self, snapshot: ResolvedMiniGameSnapshot) -> JsonValue: ...
    def apply(self, state: JsonValue, event: TranscriptEvent) -> JsonValue: ...
    def finalize(self, state: JsonValue) -> TranscriptResult: ...
```

Arcwright may generate a reducer and tests during authoring, but it remains a
private Draft until the designer approves it and deterministic fixtures pass.
Production replays the exact reducer version and transcript. Client-supplied
scores, winners, or outcomes are ignored.

## Authenticated external authority

```python
@dataclass(frozen=True, slots=True)
class ExternalResultPrincipal:
    authenticated_subject: str
    tenant_id: UUID
    destination_game_id: str
    session_id: UUID
    authority_profile_id: str

async def derive_external_result_principal(
    db: AsyncSession,
    *,
    claims: JwtClaims,
    path_session_id: UUID,
    run: MiniGameRun,
) -> ExternalResultPrincipal: ...
```

The principal is internal, is never accepted from a request body, and is
derived from verified credentials plus canonical tenant, destination,
session, and invocation data. Presentation fields cannot grant authority.
The external backend submits one versioned result envelope and proof reference.
The adapter locks the invocation, verifies every identity and version field,
persists the canonical hash, and then accepts or rejects the result.

## Idempotency, resume, retirement, and host loss

- Creation is idempotent for one persisted placement evaluation.
- An identical result retry with the same identity and canonical hash returns
  the first acceptance without a second consequence.
- Conflicting duplicate, stale revision, wrong profile, wrong package or
  adaptation version, cross-session result, revoked principal, invalid proof,
  or client-authored production result is rejected.
- Pause stores remaining duration and revision. Resume rebuilds from the
  immutable snapshot and exact versions.
- A retired version cannot start a new run but remains loadable for valid
  resume, replay, and audit.
- Timeout evaluation runs on session input, transition, state reads, and the
  approved scheduler. It persists exactly once without browser authority.
- Host or verifier loss follows the authored fallback. The runtime never
  silently switches to a weaker authority profile or starts a second run.

## Future profile growth

A future profile may support WebAssembly, native engines, edge coordination,
confidential execution, signed replay proofs, or certified third-party
operators. It is added by registering a new profile definition, verifier, and
certification suite. It may not change package, adaptation, placement,
invocation, result, or consequence identity contracts.

## Acceptance criteria

- [ ] Hosting, execution, authority, presentation, and distribution negotiate
  independently.
- [ ] Initial browser profiles satisfy the permanent authority invariants.
- [ ] Local preview results are visibly non-authoritative and cannot mutate
  production state.
- [ ] Managed browser results are computed from an exact transcript and
  approved deterministic reducer.
- [ ] External results require an auth-derived principal and matching proof.
- [ ] Client claims, presentation metadata, stale results, conflicting
  duplicates, revoked profiles, and identity mismatches apply nothing.
- [ ] Exact-version resume and replay survive restart and retirement.
- [ ] Adding a synthetic future profile requires no package, placement, result,
  or consequence schema change.
- [ ] Generic API and SDK responses contain no Nightcap or mechanic-specific
  union branch.

## Tests

Focused tests cover profile negotiation, no-downgrade behavior, preview
restrictions, transcript ordering and replay, reducer determinism, external
principal derivation, proof mismatch, duplicate and stale results, retirement,
restart timeout, audience filtering, and a synthetic future profile.

## Approval record

The founder approved the exact profile registry, invocation, transcript
reducer, external principal, permanent authority invariants, and no-downgrade
behavior in this version on 2026-08-03. Implementation remains subject to a
separate go-ahead.
