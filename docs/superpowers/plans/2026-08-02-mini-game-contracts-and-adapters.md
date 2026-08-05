# Mini-game Contracts and Execution Adapters Implementation Plan

> **Execution status:** Superseded by the founder-approved 2026-08-03
> browser-first package, adaptation, placement-policy, and
> capability-negotiation design. Do not execute this plan. Its useful test and
> compatibility details must be reconciled into the replacement capability and
> trust plan after specs 0077 through 0079 are approved.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Connect human-authored story opportunities to executable mini-game invocations and bounded canonical consequences through Arcwright-hosted and host-authoritative adapters.

**Architecture:** Extend the existing package, binding, and `mini_game_runs` foundations instead of replacing them. `MiniGameCoordinator` performs deterministic eligibility and scheduling, adapter implementations own gameplay handoff, and `MiniGameConsequenceDispatcher` is the only bridge from result semantics to canonical services. The host-authoritative path accepts results from a session host principal but never executes supplied code.

**Tech Stack:** Python 3.11, Pydantic 2, SQLAlchemy 2, Alembic, FastAPI, TypeScript, pytest, Node test runner, Ruff.

## Global Constraints

- Required approved specifications: `docs/specs/0077-mini-game-registration-and-story-opportunities.md`, `docs/specs/0078-mini-game-invocation-and-execution-adapters.md`, and `docs/specs/0079-mini-game-results-consequences-theme-and-telemetry.md`.
- Required accepted decision: `docs/decisions/0018-mini-game-orchestration-and-execution-adapters.md`.
- Python owns deterministic scheduling, authoritative hosted gameplay, persistence, results, and consequences.
- TypeScript remains adapter-neutral presentation and input transport.
- Every invocation pins package ID, definition version, definition digest, registration, opportunity, adapter, and result schema version.
- Host-authoritative results require an authenticated session host principal; player principals are rejected.
- Results are facts, never arbitrary state patches or executable callbacks.
- Generated content receives only an allowlisted public-safe context and uses existing routing, logging, knowledge, and safety boundaries.
- No new dependency is permitted by this plan.
- The D-097 currency-funded player-request trigger remains schema-reserved and execution-disabled.
- Do not build public partner credentials, package signing infrastructure, billing, or engine-specific SDKs.

---

## File Responsibility Map

| File | Responsibility |
| --- | --- |
| `engine/mini_games/models.py` | Package, registration, opportunity, result, and consequence value objects |
| `engine/arc/models.py` | Arc-owned registrations, profiles, and beat opportunities |
| `engine/mini_games/loader.py` | Exact-version loading and definition digest verification |
| `engine/mini_games/coordinator.py` | Deterministic eligibility, selection, invocation, and timeout scheduling |
| `engine/mini_games/adapters.py` | Hosted and host-authoritative execution boundary |
| `engine/mini_games/consequences.py` | Bounded semantic-result dispatch to canonical services |
| `engine/mini_games/runtime.py` | Persisted invocation lifecycle and existing hosted mechanic runtime |
| `engine/telemetry/mini_games.py` | Privacy-safe append-only mini-game lifecycle telemetry |
| `api/routers/mini_games.py` | Thin participant, host, and result transport |
| `api/schemas/__init__.py` | Adapter-neutral request and response schemas |
| `sdk/src/types.ts` | Exact public TypeScript mirror of invocation transport |

### Task 1: Preflight and Contract Gate

**Files:**

- Read: `docs/specs/0077-mini-game-registration-and-story-opportunities.md`
- Read: `docs/specs/0078-mini-game-invocation-and-execution-adapters.md`
- Read: `docs/specs/0079-mini-game-results-consequences-theme-and-telemetry.md`
- Read: `docs/decisions/0018-mini-game-orchestration-and-execution-adapters.md`

**Interfaces:**

- Consumes: founder-approved specs and the `PreflightReport` from the master plan.
- Produces: a written go or stop decision for cross-module, schema, migration, and authentication work.

- [ ] **Step 1: Execute the master-plan mainline safety gate**

Run Task 1 from `2026-08-02-mini-game-platform-readiness-program.md` and record
the current `origin/main` SHA and merged-PR overlap.

- [ ] **Step 2: Verify required document statuses**

```powershell
rg -n "Status: Approved|Status:\*\* Accepted|\*\*Status:\*\* Accepted" docs/specs docs/decisions --glob "0077-*.md" --glob "0078-*.md" --glob "0079-*.md" --glob "0018-*.md"
```

Expected: all four files report approved or accepted status.

- [ ] **Step 3: Run the exact baseline**

```powershell
python -m pytest engine/tests/test_mini_game_models.py engine/tests/test_mini_game_runtime.py engine/tests/test_mini_game_runtime_aw252.py api/tests/test_mini_games_api.py -q
npm --prefix sdk run typecheck
```

Expected: existing tests pass. Record environmental failures separately from
product failures.

- [ ] **Step 4: Stop for explicit founder implementation approval**

Expected: no source, migration, API, or SDK file changes before approval.

### Task 2: Add Registration, Opportunity, Result, and Consequence Models

**Files:**

- Modify: `engine/mini_games/models.py`
- Modify: `engine/arc/models.py`
- Test: `engine/tests/test_mini_game_models.py`
- Test: `engine/tests/test_arc_models.py`

**Interfaces:**

- Consumes: existing `MiniGameManifest`, `MiniGameDefinition`, `MiniGameBinding`, `BeatDefinition`, and `ArcDefinition`.
- Produces: `MiniGameExecutionAdapter`, `MiniGameRegistration`, `MiniGameOpportunity`, `MiniGameResultEnvelope`, `MiniGameConsequenceProfile`, `ArcDefinition.mini_game_registrations`, `ArcDefinition.mini_game_consequence_profiles`, and `BeatDefinition.mini_game_opportunities`.

- [ ] **Step 1: Add failing model tests for a valid registration and opportunity**

```python
from engine.arc.models import ArcDefinition
from engine.mini_games.models import (
    MiniGameExecutionAdapter,
    MiniGameOpportunity,
    MiniGameRegistration,
)


def test_registration_pins_package_adapter_digest_and_result_schema():
    registration = MiniGameRegistration(
        registration_id="couch-race-crime-scene",
        game_id="crime-scene-smash",
        version="0.2.0",
        definition_sha256="a" * 64,
        adapter=MiniGameExecutionAdapter.arcwright_hosted,
        result_schema_version="1.0",
        capability_tags=["competitive", "discovery"],
        story_roles=["discovery"],
        runtime_config={},
        theme_config={},
        enabled=True,
    )
    assert registration.version == "0.2.0"
    assert registration.adapter is MiniGameExecutionAdapter.arcwright_hosted


def test_opportunity_reserves_player_request_without_enabling_it():
    opportunity = MiniGameOpportunity(
        opportunity_id="grill-automatic",
        story_role="interrogation",
        eligible_registration_ids=["couch-race-grill"],
        eligible_capability_tags=[],
        trigger_mode="beat_entry",
        selection_policy="session_seeded_rotation",
        rotation_lookback=1,
        max_invocations=1,
        cooldown_seconds=0,
        time_budget_seconds=240,
        public_context_keys=["beat_id", "participant_count"],
        fallback="continue_arc",
        consequence_profile_id="grill-results",
        presentation_posture="shared_focus",
    )
    assert opportunity.trigger_mode == "beat_entry"
```

- [ ] **Step 2: Run the focused tests and confirm failure**

```powershell
python -m pytest engine/tests/test_mini_game_models.py engine/tests/test_arc_models.py -q
```

Expected: import failures for the new model names.

- [ ] **Step 3: Add the exact package and opportunity interfaces**

```python
class MiniGameExecutionAdapter(str, Enum):
    arcwright_hosted = "arcwright_hosted"
    host_authoritative = "host_authoritative"


class MiniGameRegistration(BaseModel):
    model_config = ConfigDict(extra="forbid")
    registration_id: str = Field(pattern=_SLUG_PATTERN)
    game_id: str = Field(pattern=_SLUG_PATTERN)
    version: str = Field(pattern=_SEMVER_PATTERN)
    definition_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    adapter: MiniGameExecutionAdapter
    result_schema_version: Literal["1.0"] = "1.0"
    capability_tags: list[str] = Field(default_factory=list)
    story_roles: list[str] = Field(default_factory=list)
    runtime_config: dict[str, Any] = Field(default_factory=dict)
    theme_config: dict[str, Any] = Field(default_factory=dict)
    enabled: bool = True


class MiniGameOpportunity(BaseModel):
    model_config = ConfigDict(extra="forbid")
    opportunity_id: str = Field(pattern=_SLUG_PATTERN)
    story_role: str = Field(pattern=_SLUG_PATTERN)
    eligible_registration_ids: list[str] = Field(default_factory=list)
    eligible_capability_tags: list[str] = Field(default_factory=list)
    trigger_mode: Literal["beat_entry", "host_request", "player_request"]
    selection_policy: Literal["authored_order", "session_seeded_rotation"] = "authored_order"
    rotation_lookback: int = Field(default=0, ge=0, le=8)
    max_invocations: int = Field(ge=1, le=2)
    cooldown_seconds: int = Field(ge=0)
    time_budget_seconds: int = Field(ge=1)
    public_context_keys: list[str] = Field(default_factory=list)
    fallback: Literal["continue_arc", "host_resolve", "reduced_reward"]
    consequence_profile_id: str = Field(pattern=_SLUG_PATTERN)
    presentation_posture: Literal["private_focus", "shared_focus", "mixed_focus"]
```

Add `supported_adapters`, `capability_tags`, `result_schema_version`, and
`definition_sha256` to `MiniGameManifest`. Add optional
`session_min_players` and `session_max_players` to `MiniGameDefinition`, with
effective properties that fall back to the existing active-participant range.
This preserves old packages while allowing Evidence Locker to declare a
2-to-8-player session with one active puzzle player. Keep defaults that make
existing version 1.0 manifests parse during compatibility migration.

- [ ] **Step 4: Add the exact result and consequence interfaces**

```python
class MiniGameResultEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")
    invocation_id: UUID
    registration_id: str = Field(pattern=_SLUG_PATTERN)
    game_id: str = Field(pattern=_SLUG_PATTERN)
    package_version: str = Field(pattern=_SEMVER_PATTERN)
    result_schema_version: Literal["1.0"] = "1.0"
    status_revision: int = Field(ge=0)
    idempotency_key: str = Field(min_length=1, max_length=256)
    completion_status: Literal["completed", "timed_out", "cancelled"]
    duration_ms: int = Field(ge=0)
    participant_results: dict[str, dict[str, Any]] = Field(default_factory=dict)
    team_results: dict[str, dict[str, Any]] = Field(default_factory=dict)
    semantics: dict[str, int | float | bool | str] = Field(default_factory=dict)
    evidence_ref: str | None = Field(default=None, max_length=512)


class MiniGameConsequenceRule(BaseModel):
    model_config = ConfigDict(extra="forbid")
    semantic_key: str = Field(pattern=_SLUG_PATTERN)
    action: Literal[
        "resource_delta",
        "score_delta",
        "knowledge_assertion",
        "obligation_progress",
        "content_event",
    ]
    target: str
    multiplier: float = 1.0
    minimum: float | None = None
    maximum: float | None = None


class MiniGameConsequenceProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")
    profile_id: str = Field(pattern=_SLUG_PATTERN)
    rules: list[MiniGameConsequenceRule]
```

- [ ] **Step 5: Add arc ownership and cross-reference validation**

```python
class BeatDefinition(BaseModel):
    mini_game_opportunities: list[MiniGameOpportunity] = Field(default_factory=list)


class ArcDefinition(BaseModel):
    mini_game_registrations: list[MiniGameRegistration] = Field(default_factory=list)
    mini_game_consequence_profiles: list[MiniGameConsequenceProfile] = Field(default_factory=list)
```

Add one `model_validator(mode="after")` that rejects duplicate IDs, unknown
registration references, unknown consequence profiles, mixed legacy bindings
and opportunities on one beat, and enabled `player_request` opportunities.

- [ ] **Step 6: Add failing compatibility and rejection tests**

```python
import pytest
from pydantic import ValidationError


@pytest.mark.parametrize(
    "field,value",
    [
        ("definition_sha256", "bad"),
        ("version", "latest"),
        ("result_schema_version", "2.0"),
    ],
)
def test_registration_rejects_unpinned_contract_fields(field, value, registration_data):
    registration_data[field] = value
    with pytest.raises(ValidationError):
        MiniGameRegistration.model_validate(registration_data)
```

- [ ] **Step 7: Run model tests**

```powershell
python -m pytest engine/tests/test_mini_game_models.py engine/tests/test_arc_models.py engine/tests/test_couch_race_arc_json.py -q
```

Expected: pass, including legacy static binding fixtures.

- [ ] **Step 8: Commit the model contract**

```powershell
git add engine/mini_games/models.py engine/arc/models.py engine/tests/test_mini_game_models.py engine/tests/test_arc_models.py engine/tests/test_couch_race_arc_json.py
git commit -m "feat(arc): add minigame opportunity contracts"
```

### Task 3: Load Exact Package Versions and Verify Digests

**Files:**

- Modify: `engine/mini_games/loader.py`
- Modify: `engine/mini_games/__init__.py`
- Test: `engine/tests/test_mini_game_models.py`

**Interfaces:**

- Consumes: `MiniGameRegistration` and immutable package definition files.
- Produces: `load_registered_mini_game(root_path: Path, registration: MiniGameRegistration) -> LoadedMiniGame` and `definition_sha256(path: Path) -> str`.

- [ ] **Step 1: Write a failing exact-version test**

```python
def test_registration_loads_pinned_version_after_manifest_advances(tmp_path):
    package = write_package_versions(tmp_path, versions=["0.1.0", "0.2.0"])
    registration = registration_for(package, version="0.1.0")
    loaded = load_registered_mini_game(tmp_path, registration)
    assert loaded.definition.version == "0.1.0"
```

- [ ] **Step 2: Write a failing digest and retirement test**

```python
def test_registered_definition_digest_must_match(tmp_path):
    registration = registration_for(write_active_package(tmp_path))
    registration = registration.model_copy(update={"definition_sha256": "0" * 64})
    with pytest.raises(MiniGamePackageError, match="definition digest mismatch"):
        load_registered_mini_game(tmp_path, registration)
```

- [ ] **Step 3: Run the focused loader tests and confirm failure**

```powershell
python -m pytest engine/tests/test_mini_game_models.py -q
```

Expected: missing `load_registered_mini_game`.

- [ ] **Step 4: Implement the exact loader functions**

```python
def definition_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def load_registered_mini_game(
    root_path: Path,
    registration: MiniGameRegistration,
) -> LoadedMiniGame:
    package_path = (root_path / registration.game_id).resolve()
    manifest = _load_model(package_path / "manifest.json", MiniGameManifest)
    definition_path = _resolve_package_child(
        package_path,
        f"definitions/{registration.version}.json",
    )
    definition = _load_model(definition_path, MiniGameDefinition)
    if definition_sha256(definition_path) != registration.definition_sha256:
        raise MiniGamePackageError("definition digest mismatch")
    if manifest.lifecycle is MiniGameLifecycle.retired:
        raise MiniGamePackageError("retired package cannot start a new invocation")
    return LoadedMiniGame(package_path, manifest, definition)
```

Resume and replay continue decoding the persisted definition snapshot and do
not call this new-invocation lifecycle guard.

- [ ] **Step 5: Run and commit**

```powershell
python -m pytest engine/tests/test_mini_game_models.py -q
git add engine/mini_games/loader.py engine/mini_games/__init__.py engine/tests/test_mini_game_models.py
git commit -m "fix(arc): pin minigame package versions"
```

### Task 4: Persist Invocation Provenance and Recovery State

**Files:**

- Modify: `engine/db/orm.py`
- Modify: `engine/mini_games/runtime.py`
- Create: `migrations/versions/0008_mini_game_invocation_contracts.py`
- Test: `engine/tests/test_mini_game_runtime.py`
- Test: `engine/tests/test_session_resume.py`

**Interfaces:**

- Consumes: exact registration, opportunity, snapshot, and adapter values.
- Produces: additional `MiniGameRun` columns and `MiniGameRuntime.create_invocation(...) -> MiniGameRun`.

- [ ] **Step 1: Write a failing persistence test**

```python
async def test_invocation_persists_selection_and_consequence_provenance(runtime):
    run = await runtime.create_invocation(
        session_id=SESSION_ID,
        registration=REGISTRATION,
        opportunity=OPPORTUNITY,
        resolved_snapshot=SNAPSHOT,
        selection_reason="authored_registration_order:0",
        trigger_mode="beat_entry",
    )
    assert run.registration_id == REGISTRATION.registration_id
    assert run.opportunity_id == OPPORTUNITY.opportunity_id
    assert run.consequence_status == "pending_result"
```

- [ ] **Step 2: Run the test and confirm failure**

```powershell
python -m pytest engine/tests/test_mini_game_runtime.py -q
```

Expected: `MiniGameRuntime` has no `create_invocation` method.

- [ ] **Step 3: Add the exact ORM columns and migration**

Add non-null server defaults for existing rows:

```python
opportunity_id: Mapped[str] = mapped_column(Text, nullable=False, server_default="legacy-binding")
registration_id: Mapped[str] = mapped_column(Text, nullable=False, server_default="legacy-registration")
execution_adapter: Mapped[str] = mapped_column(Text, nullable=False, server_default="arcwright_hosted")
definition_sha256: Mapped[str] = mapped_column(Text, nullable=False, server_default="legacy")
result_schema_version: Mapped[str] = mapped_column(Text, nullable=False, server_default="1.0")
selection_reason: Mapped[str] = mapped_column(Text, nullable=False, server_default="legacy_binding")
trigger_mode: Mapped[str] = mapped_column(Text, nullable=False, server_default="beat_entry")
result_idempotency_key: Mapped[str | None] = mapped_column(Text, nullable=True)
result_received_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
consequence_status: Mapped[str] = mapped_column(Text, nullable=False, server_default="pending_result")
consequence_record: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
```

Create a unique partial index on non-null `result_idempotency_key` scoped to
`run_id`.

- [ ] **Step 4: Add `create_invocation` without removing `create_run`**

```python
async def create_invocation(
    self,
    *,
    session_id: UUID,
    registration: MiniGameRegistration,
    opportunity: MiniGameOpportunity,
    resolved_snapshot: ResolvedMiniGameSnapshot,
    selection_reason: str,
    trigger_mode: str,
) -> MiniGameRun:
    run = await self.create_run(session_id, resolved_snapshot)
    run.registration_id = registration.registration_id
    run.opportunity_id = opportunity.opportunity_id
    run.execution_adapter = registration.adapter.value
    run.definition_sha256 = registration.definition_sha256
    run.result_schema_version = registration.result_schema_version
    run.selection_reason = selection_reason
    run.trigger_mode = trigger_mode
    await self._db.flush()
    return run
```

- [ ] **Step 5: Verify migration upgrade and downgrade**

```powershell
alembic upgrade head
alembic downgrade -1
alembic upgrade head
python -m pytest engine/tests/test_mini_game_runtime.py engine/tests/test_session_resume.py -q
```

Expected: migration round trip and tests pass.

- [ ] **Step 6: Commit persistence**

```powershell
git add engine/db/orm.py engine/mini_games/runtime.py migrations/versions/0008_mini_game_invocation_contracts.py engine/tests/test_mini_game_runtime.py engine/tests/test_session_resume.py
git commit -m "feat(session): persist minigame invocation provenance"
```

### Task 5: Add Deterministic Opportunity Coordination

**Files:**

- Create: `engine/mini_games/coordinator.py`
- Modify: `engine/session/service.py`
- Test: `engine/tests/test_mini_game_coordinator.py`
- Test: `engine/tests/test_session_lifecycle.py`
- Test: `engine/tests/test_aw256_beat_hardcode.py`

**Interfaces:**

- Consumes: `ArcDefinition`, exact package root, participant count, current beat, and `MiniGameRuntime.create_invocation`.
- Produces: `MiniGameCoordinator.on_beat_entry(...) -> list[MiniGameRun]`, `MiniGameCoordinator.check_session_timeouts(...) -> list[UUID]`, and deterministic reason codes.

- [ ] **Step 1: Write a failing deterministic selection test**

```python
async def test_beat_entry_selection_replays_for_same_session_state(coordinator):
    runs = await coordinator.on_beat_entry(
        db=DB,
        session_id=SESSION_ID,
        arc=ARC,
        beat_id="scene",
        participant_count=4,
        package_root=PACKAGE_ROOT,
    )
    replay = await coordinator.on_beat_entry(
        db=DB,
        session_id=SESSION_ID,
        arc=ARC,
        beat_id="scene",
        participant_count=4,
        package_root=PACKAGE_ROOT,
    )
    assert replay[0].run_id == runs[0].run_id
    assert replay[0].registration_id == runs[0].registration_id
    assert runs[0].selection_reason.startswith("session_seeded_rotation:")
```

- [ ] **Step 2: Write failing ineligibility and idempotency tests**

```python
@pytest.mark.parametrize("participant_count", [1, 9])
async def test_incompatible_player_count_uses_authored_fallback(coordinator, participant_count):
    runs = await coordinator.on_beat_entry(
        db=DB,
        session_id=SESSION_ID,
        arc=ARC,
        beat_id="scene",
        participant_count=participant_count,
        package_root=PACKAGE_ROOT,
    )
    assert runs == []
    assert last_event().payload["reason_code"] == "player_count_ineligible"


async def test_repeated_beat_entry_does_not_create_second_invocation(coordinator):
    first = await enter_scene(coordinator)
    second = await enter_scene(coordinator)
    assert second[0].run_id == first[0].run_id


async def test_repeatable_opportunity_avoids_recent_candidate(coordinator):
    first = await enter_repeatable_opportunity(coordinator)
    second = await reenter_repeatable_opportunity_after_completion(coordinator)
    assert second[0].registration_id != first[0].registration_id


async def test_rotation_never_selects_candidate_outside_authored_role(coordinator):
    run = (await enter_pressure_capstone(coordinator))[0]
    assert "pressure_capstone" in registration(run.registration_id).story_roles
```

- [ ] **Step 3: Run and confirm failure**

```powershell
python -m pytest engine/tests/test_mini_game_coordinator.py -q
```

Expected: missing coordinator module.

- [ ] **Step 4: Implement the coordinator interface**

```python
class MiniGameCoordinator:
    def __init__(self, runtime: MiniGameRuntime, *, clock: Clock = _utcnow) -> None:
        self._runtime = runtime
        self._clock = clock

    async def on_beat_entry(
        self,
        *,
        db: AsyncSession,
        session_id: UUID,
        arc: ArcDefinition,
        beat_id: str,
        participant_count: int,
        package_root: Path,
    ) -> list[MiniGameRun]:
        ...

    async def check_session_timeouts(
        self,
        *,
        db: AsyncSession,
        session_id: UUID,
    ) -> list[UUID]:
        ...
```

Filter by enabled registration, exact version, lifecycle, adapter, capability
tags, authored story role, effective session-player range, prior invocation
count, cooldown, and time budget. For `authored_order`, use authored candidate
order then registration ID. For `session_seeded_rotation`, sort eligible
candidates by SHA-256 of
`"{session_id}:{opportunity_id}:{registration_id}"`, exclude up to
`rotation_lookback` registrations from completed runs in the current session,
and select the first remaining candidate. If all candidates are excluded,
allow the least-recent eligible registration. Persist the selected registration
and reason so replay never recomputes an existing invocation. Cross-session
history may be supplied later by an experience continuity adapter; it is not a
Nightcap v1 dependency. Do not call AI.

- [ ] **Step 5: Call the coordinator from deterministic session transitions**

Add one private `SessionService._schedule_mini_games_for_beat(...)` call after
the current beat is persisted in `start_session` and
`advance_live_session_on_input`. Keep FastAPI routes unchanged.

- [ ] **Step 6: Run and commit**

```powershell
python -m pytest engine/tests/test_mini_game_coordinator.py engine/tests/test_session_lifecycle.py engine/tests/test_aw256_beat_hardcode.py -q
git add engine/mini_games/coordinator.py engine/session/service.py engine/tests/test_mini_game_coordinator.py engine/tests/test_session_lifecycle.py
git commit -m "feat(session): schedule authored minigame opportunities"
```

### Task 6: Add Hosted and Host-authoritative Adapters

**Files:**

- Create: `engine/mini_games/adapters.py`
- Modify: `engine/mini_games/runtime.py`
- Modify: `engine/mini_games/__init__.py`
- Test: `engine/tests/test_mini_game_adapters.py`

**Interfaces:**

- Consumes: persisted invocation and `MiniGameResultEnvelope`.
- Produces: `MiniGameAdapter` protocol, `ArcwrightHostedAdapter`, `HostAuthoritativeAdapter`, `HostResultPrincipal`, and `AcceptedMiniGameResult`.

- [ ] **Step 1: Write failing trust and idempotency tests**

```python
async def test_player_principal_cannot_submit_host_result(host_adapter):
    principal = HostResultPrincipal(participant_id=PLAYER_ID, surface_type="phone")
    with pytest.raises(HostResultForbiddenError):
        await host_adapter.accept_result(ENVELOPE, principal=principal)


async def test_identical_host_result_retry_is_idempotent(host_adapter):
    first = await host_adapter.accept_result(ENVELOPE, principal=HOST_PRINCIPAL)
    second = await host_adapter.accept_result(ENVELOPE, principal=HOST_PRINCIPAL)
    assert second == first


async def test_conflicting_duplicate_is_rejected(host_adapter):
    await host_adapter.accept_result(ENVELOPE, principal=HOST_PRINCIPAL)
    conflict = ENVELOPE.model_copy(update={"semantics": {"score": 999}})
    with pytest.raises(HostResultConflictError):
        await host_adapter.accept_result(conflict, principal=HOST_PRINCIPAL)
```

- [ ] **Step 2: Run and confirm failure**

```powershell
python -m pytest engine/tests/test_mini_game_adapters.py -q
```

Expected: missing adapter module.

- [ ] **Step 3: Define the exact adapter interfaces**

```python
@dataclass(frozen=True)
class HostResultPrincipal:
    participant_id: UUID
    surface_type: str


@dataclass(frozen=True)
class AcceptedMiniGameResult:
    run_id: UUID
    idempotency_key: str
    duplicate: bool


class MiniGameAdapter(Protocol):
    async def start(self, run: MiniGameRun) -> MiniGameRun: ...
    async def accept_result(
        self,
        envelope: MiniGameResultEnvelope,
        *,
        principal: HostResultPrincipal | None,
    ) -> AcceptedMiniGameResult: ...
```

- [ ] **Step 4: Implement the hosted wrapper**

`ArcwrightHostedAdapter.start` calls `MiniGameRuntime.start_run`. Its result is
created only by hosted runtime finalization and never accepts a host principal.

- [ ] **Step 5: Implement host-authoritative validation**

`HostAuthoritativeAdapter.accept_result` must lock the run, require
`surface_type == "host"`, compare every identity and version field, reject a
stale revision, hash the canonical envelope for duplicate comparison, persist
the result before returning, and never import or execute package code.

- [ ] **Step 6: Run and commit**

```powershell
python -m pytest engine/tests/test_mini_game_adapters.py engine/tests/test_mini_game_runtime.py -q
git add engine/mini_games/adapters.py engine/mini_games/runtime.py engine/mini_games/__init__.py engine/tests/test_mini_game_adapters.py
git commit -m "feat(session): add minigame execution adapters"
```

### Task 7: Apply Declarative Consequences Exactly Once

**Files:**

- Create: `engine/mini_games/consequences.py`
- Modify: `engine/mini_games/runtime.py`
- Test: `engine/tests/test_mini_game_consequences.py`
- Test: `engine/tests/test_resources_integration.py`
- Test: `engine/tests/test_scoring_integration.py`
- Test: `engine/tests/test_knowledge_graph.py`

**Interfaces:**

- Consumes: accepted `MiniGameResultEnvelope`, approved `MiniGameConsequenceProfile`, and existing canonical services.
- Produces: `MiniGameConsequenceDispatcher.apply(...) -> ConsequenceApplication` and durable `consequence_status` transitions `pending_result -> pending_application -> applied`.

- [ ] **Step 1: Write failing bounded-dispatch tests**

```python
async def test_resource_delta_is_clamped_and_applied_once(dispatcher):
    first = await dispatcher.apply(DB, RUN, PROFILE, RESULT)
    second = await dispatcher.apply(DB, RUN, PROFILE, RESULT)
    assert first.resource_deltas == {str(PLAYER_ID): 2}
    assert second.duplicate is True
    assert leverage_balance(PLAYER_ID) == 2


async def test_unknown_semantic_cannot_mutate_state(dispatcher):
    result = RESULT.model_copy(update={"semantics": {"database_patch": 1}})
    with pytest.raises(UnauthorizedMiniGameSemanticError):
        await dispatcher.apply(DB, RUN, PROFILE, result)
```

- [ ] **Step 2: Write a failing crash-recovery test**

```python
async def test_retry_after_result_receipt_does_not_double_apply(dispatcher):
    RUN.consequence_status = "pending_application"
    RUN.consequence_record = {"applied_rule_ids": ["winner-resource"]}
    application = await dispatcher.apply(DB, RUN, PROFILE, RESULT)
    assert application.skipped_rule_ids == ("winner-resource",)
```

- [ ] **Step 3: Run and confirm failure**

```powershell
python -m pytest engine/tests/test_mini_game_consequences.py -q
```

Expected: missing consequence module.

- [ ] **Step 4: Define and implement the dispatcher result**

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
    ) -> ConsequenceApplication:
        ...
```

Dispatch only named actions. Use existing resource, scoring, knowledge,
obligation, and event functions; persist each applied rule ID before moving to
the next rule. Reject result semantics absent from the profile.

- [ ] **Step 5: Run and commit**

```powershell
python -m pytest engine/tests/test_mini_game_consequences.py engine/tests/test_resources_integration.py engine/tests/test_scoring_integration.py engine/tests/test_knowledge_graph.py -q
git add engine/mini_games/consequences.py engine/mini_games/runtime.py engine/tests/test_mini_game_consequences.py engine/tests/test_resources_integration.py engine/tests/test_scoring_integration.py engine/tests/test_knowledge_graph.py
git commit -m "feat(session): apply authored minigame consequences"
```

### Task 8: Make API and SDK Transport Adapter-neutral

**Files:**

- Modify: `api/schemas/__init__.py`
- Modify: `api/routers/mini_games.py`
- Test: `api/tests/test_mini_games_api.py`
- Modify: `sdk/src/types.ts`
- Modify: `sdk/src/index.ts`
- Create: `sdk/tests/mini-game-invocations.test.mjs`
- Modify: `nightcap-web/src/mini-games/client.ts`
- Test: `nightcap-web/tests/mini-game-client.test.ts`

**Interfaces:**

- Consumes: invocation, result envelope, host principal, and generic hosted mechanic projection.
- Produces: `MiniGameInvocationResponse`, `HostMiniGameResultRequest`, generic TypeScript `MiniGameState`, and `ArcwrightClient.submitMiniGameResult`.

- [ ] **Step 1: Write failing API response tests**

```python
async def test_active_run_response_pins_invocation_contract(client, player_headers):
    response = await client.get(ACTIVE_URL, headers=player_headers)
    body = response.json()
    assert body["definition_version"] == "0.2.0"
    assert body["adapter"] == "arcwright_hosted"
    assert body["status_revision"] >= 0
    assert "phase_state" not in body


async def test_player_cannot_submit_host_result(client, player_headers):
    response = await client.post(RESULT_URL, headers=player_headers, json=RESULT_JSON)
    assert response.status_code == 403
```

- [ ] **Step 2: Run and confirm failure**

```powershell
python -m pytest api/tests/test_mini_games_api.py -q
```

Expected: response lacks version and adapter fields, and result route is absent.

- [ ] **Step 3: Add adapter-neutral API schemas**

```python
class MiniGameInvocationResponse(BaseModel):
    run_id: UUID
    game_id: str
    registration_id: str
    opportunity_id: str
    definition_version: str
    adapter: Literal["arcwright_hosted", "host_authoritative"]
    status: str
    status_revision: int
    deadline_at: datetime | None
    runtime_state: dict[str, Any] = Field(default_factory=dict)
    presentation: dict[str, Any] = Field(default_factory=dict)
    my_submissions: list[MiniGameSubmissionResponse] = Field(default_factory=list)


class HostMiniGameResultRequest(MiniGameResultEnvelope):
    pass
```

Move all TMST-specific projection and payload validation behind the hosted
plugin. Keep the route handler to authentication, schema validation, adapter
call, commit, and response.

- [ ] **Step 4: Add exact SDK types and method**

```typescript
export interface MiniGameState {
  runId: string;
  gameId: string;
  registrationId: string;
  opportunityId: string;
  definitionVersion: string;
  adapter: "arcwright_hosted" | "host_authoritative";
  statusRevision: number;
  status: "pending" | "active" | "paused" | "completed" | "timed_out" | "cancelled";
  deadlineAt: string | null;
  runtimeState: Record<string, unknown>;
  presentation: Record<string, unknown>;
  mySubmissions: MiniGameSubmissionResult[];
}

submitMiniGameResult(
  sessionId: string,
  runId: string,
  result: HostMiniGameResult,
): Promise<AcceptedMiniGameResult>;
```

- [ ] **Step 5: Preserve exact-version browser loading**

Change `fetchActiveState` to map `definition_version`, `runtime_state`, and all
new generic fields. Pass `state.definitionVersion` to `loadDefinition`; never
load `latest.json`.

- [ ] **Step 6: Run and commit**

```powershell
python -m pytest api/tests/test_mini_games_api.py engine/tests/test_mini_game_runtime_aw252.py -q
npm --prefix sdk run typecheck
npm --prefix sdk run build
npm --prefix nightcap-web test
git add api sdk nightcap-web/src/mini-games nightcap-web/tests/mini-game-client.test.ts
git commit -m "feat(api): expose generic minigame invocations"
```

### Task 9: Drive Timeouts and Resume Recovery

**Files:**

- Modify: `engine/mini_games/coordinator.py`
- Modify: `engine/session/service.py`
- Test: `engine/tests/test_mini_game_coordinator.py`
- Test: `engine/tests/test_session_resume.py`

**Interfaces:**

- Consumes: persisted active and paused invocations.
- Produces: session lifecycle hooks that pause, resume, and timeout invocations exactly once.

- [ ] **Step 1: Write failing pause, restart, and timeout tests**

```python
async def test_session_pause_and_resume_preserve_invocation_deadline(service):
    await service.pause_session(DB, SESSION_ID)
    assert await active_run_status(DB) == "paused"
    await service.resume_session(DB, SESSION_ID)
    assert await active_run_status(DB) == "active"


async def test_timeout_driver_is_exactly_once_after_restart(coordinator):
    first = await coordinator.check_session_timeouts(db=DB, session_id=SESSION_ID)
    second = await coordinator.check_session_timeouts(db=DB, session_id=SESSION_ID)
    assert first == [RUN_ID]
    assert second == []
```

- [ ] **Step 2: Run and confirm failure**

```powershell
python -m pytest engine/tests/test_mini_game_coordinator.py engine/tests/test_session_resume.py -q
```

- [ ] **Step 3: Add session lifecycle hooks**

In `pause_session`, pause every active hosted run. In `resume_session`, resume
paused runs from their remaining duration and leave host-authoritative runs in
their authored recovery mode. On each input, beat transition, and session state
read, call `check_session_timeouts` without busy polling.

- [ ] **Step 4: Run and commit**

```powershell
python -m pytest engine/tests/test_mini_game_coordinator.py engine/tests/test_session_resume.py engine/tests/test_session_lifecycle.py -q
git add engine/mini_games/coordinator.py engine/session/service.py engine/tests/test_mini_game_coordinator.py engine/tests/test_session_resume.py engine/tests/test_session_lifecycle.py
git commit -m "feat(session): recover minigame lifecycle"
```

### Task 10: Add Privacy-safe Telemetry and Generation Budgets

**Files:**

- Create: `engine/telemetry/mini_games.py`
- Modify: `engine/mini_games/coordinator.py`
- Modify: `engine/mini_games/runtime.py`
- Modify: `engine/mini_games/resolver.py`
- Test: `engine/tests/test_mini_game_telemetry.py`
- Test: `engine/tests/test_generation_logging.py`
- Test: `engine/tests/test_mini_game_resolution.py`

**Interfaces:**

- Consumes: opportunity decisions, invocation lifecycle, result rejection reason codes, public-safe context allowlist, and existing routing logs.
- Produces: `record_mini_game_event(...) -> None` and `MiniGameGenerationBudget` enforcement.

- [ ] **Step 1: Write a failing telemetry privacy test**

```python
async def test_lifecycle_event_excludes_private_payload(db_session):
    await record_mini_game_event(
        db_session,
        session_id=SESSION_ID,
        event_type="mini_game_result_rejected",
        run=RUN,
        reason_code="stale_revision",
        duration_ms=250,
        player_count=4,
    )
    event = await last_event(db_session)
    assert event.payload["reason_code"] == "stale_revision"
    assert "semantics" not in event.payload
    assert "runtime_state" not in event.payload
```

- [ ] **Step 2: Write a failing public-context and budget test**

```python
async def test_generation_receives_only_allowlisted_context(resolver, generate_spy):
    await resolver.resolve(public_context={"beat_id": "scene", "killer_id": "secret"})
    assert "beat_id" in generate_spy.input_context
    assert "killer_id" not in generate_spy.input_context
    assert generate_spy.max_attempts == 2
```

- [ ] **Step 3: Define telemetry and budget interfaces**

```python
class MiniGameGenerationBudget(BaseModel):
    model_config = ConfigDict(extra="forbid")
    max_attempts: int = Field(default=2, ge=1, le=2)
    max_latency_ms: int = Field(default=2500, ge=100)
    deterministic_fallback: Literal["authored_content", "cancel_invocation"]


async def record_mini_game_event(
    db: AsyncSession,
    *,
    session_id: UUID,
    event_type: str,
    run: MiniGameRun,
    reason_code: str | None = None,
    duration_ms: int | None = None,
    player_count: int | None = None,
) -> None:
    ...
```

Emit opportunity evaluated, selected, started, completed, timed out, cancelled,
result rejected, consequence applied, fallback, and reconnect events. Store
neutral IDs, adapter, package version, duration, player count, and reason code;
exclude raw submissions, prompts, results, and private story context.

- [ ] **Step 4: Enforce routing, safety, and fallback**

Filter `adaptation_context` and `session_context` by
`MiniGameOpportunity.public_context_keys` before resolution. Preserve existing
router, generation logging, L1, L2, and L3 paths. On budget exhaustion, use the
declared deterministic fallback without changing game selection or outcome.

- [ ] **Step 5: Run and commit**

```powershell
python -m pytest engine/tests/test_mini_game_telemetry.py engine/tests/test_generation_logging.py engine/tests/test_mini_game_resolution.py engine/tests/test_safety_l1.py engine/tests/test_safety_l2.py engine/tests/test_safety_l3.py -q
git add engine/telemetry/mini_games.py engine/mini_games/coordinator.py engine/mini_games/runtime.py engine/mini_games/resolver.py engine/tests/test_mini_game_telemetry.py engine/tests/test_generation_logging.py engine/tests/test_mini_game_resolution.py
git commit -m "feat(session): instrument minigame orchestration"
```

### Task 11: Prove a Synthetic Non-Nightcap Host

**Files:**

- Create: `engine/tests/fixtures/arcs/synthetic-host-minigame.arc.json`
- Create: `engine/tests/fixtures/mini_games/synthetic-host-game/manifest.json`
- Create: `engine/tests/fixtures/mini_games/synthetic-host-game/definitions/0.1.0.json`
- Test: `engine/tests/test_mini_game_host_authoritative_integration.py`
- Modify: `docs/architecture/14-architecture-validation.md`

**Interfaces:**

- Consumes: registration, opportunity, coordinator, host adapter, result envelope, consequence dispatcher, API-neutral state, and replay records.
- Produces: one end-to-end protocol proof containing no Nightcap vocabulary or gameplay code execution.

- [ ] **Step 1: Write the failing integration test**

```python
async def test_synthetic_host_result_changes_only_authored_resource():
    session = await create_synthetic_session()
    run = await enter_opportunity(session, "checkpoint-challenge")
    assert run.execution_adapter == "host_authoritative"
    accepted = await submit_host_result(run, semantic_key="team-progress", value=1)
    assert accepted.duplicate is False
    assert await resource_value(session, "team-progress") == 1
    assert await replayed_run(session, run.run_id) == run.run_id
```

- [ ] **Step 2: Run and confirm failure**

```powershell
python -m pytest engine/tests/test_mini_game_host_authoritative_integration.py -q
```

- [ ] **Step 3: Add the smallest neutral fixture**

Use `checkpoint-challenge`, `team-progress`, `chapter`, and `shared_focus` as
the only story vocabulary. The package has no Python mechanic and returns a
host-authored `team-progress` result.

- [ ] **Step 4: Run architecture leak checks**

```powershell
rg -n "Nightcap|Couch Race|Leverage|TV|phone|suspect|clue" engine/tests/fixtures/arcs/synthetic-host-minigame.arc.json engine/tests/fixtures/mini_games/synthetic-host-game engine/tests/test_mini_game_host_authoritative_integration.py
```

Expected: no matches.

- [ ] **Step 5: Run and commit**

```powershell
python -m pytest engine/tests/test_mini_game_host_authoritative_integration.py -q
git add engine/tests/fixtures/arcs/synthetic-host-minigame.arc.json engine/tests/fixtures/mini_games/synthetic-host-game engine/tests/test_mini_game_host_authoritative_integration.py docs/architecture/14-architecture-validation.md
git commit -m "test(arc): prove host-authoritative minigame flow"
```

### Task 12: Full Verification and Contract Checkpoint

**Files:**

- Modify: `docs/specs/0077-mini-game-registration-and-story-opportunities.md`
- Modify: `docs/specs/0078-mini-game-invocation-and-execution-adapters.md`
- Modify: `docs/specs/0079-mini-game-results-consequences-theme-and-telemetry.md`
- Modify: `docs/roadmap/index.json`

**Interfaces:**

- Consumes: all commits from Tasks 2 through 11.
- Produces: reviewed contract evidence and an explicit founder decision before Nightcap integration.

- [ ] **Step 1: Run full Python and TypeScript verification**

```powershell
python -m pytest engine/tests api/tests -q
python -m ruff check engine api
python -m ruff format --check engine api
npm --prefix sdk run typecheck
npm --prefix sdk run build
npm --prefix nightcap-web test
npm --prefix nightcap-web run typecheck
git diff --check
```

Expected: all commands pass. Record any environment blocker without converting
it to a pass.

- [ ] **Step 2: Verify migration round trip again**

```powershell
alembic downgrade -1
alembic upgrade head
```

Expected: both commands exit 0 against the supported test database.

- [ ] **Step 3: Run architecture review**

Use `arcwright-reviewer` against the complete change set. Resolve all blocking
findings and rerun affected checks.

- [ ] **Step 4: Reconcile specs and trackers**

Record exact test commands, commit SHAs, compatibility behavior, migration
evidence, and synthetic-host limits. Do not claim a public SDK or external
developer deployment.

- [ ] **Step 5: Stop for founder contract approval**

Nightcap integration does not begin until the founder approves this checkpoint.
