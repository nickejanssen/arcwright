# Mini-game Contracts and Execution Adapters Implementation Plan

> **For Codex:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to execute
> this plan task by task. Do not begin without separate founder implementation
> approval.

**Goal:** Connect authored story opportunities to executable mini-game
invocations and canonical consequences through Arcwright-hosted and
host-authoritative adapters.

**Architecture:** Extend the current package and binding model into
registration, opportunity, invocation, adapter, result, and consequence
contracts. Preserve the current Python runtime behind arcwright_hosted. Add a
protocol-only host_authoritative path that never loads external gameplay code.

**Tech stack:** Python 3.11, Pydantic, SQLAlchemy, Alembic, FastAPI, TypeScript,
pytest, Ruff, JSON.

**Required approved specs:** docs/specs/0077 through docs/specs/0079.

---

## Task 1: Preflight and Contract Approval

**Files:** None.

1. Execute Task 0 from the program plan.
2. Confirm ADR 0018 and specs 0077 through 0079 are Approved.
3. Confirm explicit approval for cross-module and schema work.
4. Run baseline tests:

       python -m pytest engine/tests/test_mini_game_models.py engine/tests/test_mini_game_runtime.py engine/tests/test_mini_game_runtime_aw252.py api/tests/test_mini_games_api.py -q
       npm --prefix sdk run typecheck

5. Report baseline failures and pause for implementation approval.

## Task 2: Add Registration and Opportunity Models

**Files:**

- Modify: engine/mini_games/models.py
- Modify: engine/arc/models.py
- Modify: engine/tests/test_mini_game_models.py
- Modify: engine/tests/test_arc_models.py
- Modify: engine/tests/test_couch_race_arc_json.py

**Step 1: Write failing model tests**

Cover:

- version-pinned registration;
- package capabilities and adapter declaration;
- opportunity eligibility by registration and capability;
- trigger and repetition policy;
- public-safe context allowlist;
- authored fallback;
- result semantic and consequence mapping references;
- duplicate IDs;
- unknown registrations;
- impossible invocation counts;
- static MiniGameBinding compatibility.

**Step 2: Run tests and confirm failure**

    python -m pytest engine/tests/test_mini_game_models.py engine/tests/test_arc_models.py -q

Expected: failures because the new contracts do not exist.

**Step 3: Implement the smallest typed contracts**

Do not add scheduling behavior yet. Keep all identifiers game-agnostic and
forbid extra fields.

**Step 4: Run focused tests**

Expected: pass.

**Step 5: Commit**

    git add engine/mini_games/models.py engine/arc/models.py engine/tests/test_mini_game_models.py engine/tests/test_arc_models.py engine/tests/test_couch_race_arc_json.py
    git commit -m "feat(arc): add minigame opportunity contracts"

## Task 3: Load Exact Package Versions

**Files:**

- Modify: engine/mini_games/loader.py
- Modify: engine/tests/test_mini_game_models.py

**Step 1: Write failing tests**

Prove:

- an invocation loads the definition version pinned by registration;
- historical versions remain loadable after current_version changes;
- directory identity is enforced for every lifecycle;
- active packages without an executable adapter or required renderer fail
  production validation;
- template and fixture directories remain excluded.

**Step 2: Confirm failure**

    python -m pytest engine/tests/test_mini_game_models.py -q

**Step 3: Implement exact-version loading**

Do not silently fall back to latest.

**Step 4: Verify and commit**

    git add engine/mini_games/loader.py engine/tests/test_mini_game_models.py
    git commit -m "fix(arc): pin minigame package versions"

## Task 4: Persist Invocation Provenance

**Files:**

- Modify: engine/db/orm.py
- Modify: engine/mini_games/runtime.py
- Create with Alembic and record the generated path before editing:
  alembic/versions/*_mini_game_invocation_provenance.py
- Modify: engine/tests/test_mini_game_runtime.py
- Modify: engine/tests/test_session_resume.py

**Step 1: Write failing persistence tests**

Cover opportunity ID, registration ID, adapter, package version, trigger,
selection reason, result schema version, idempotency key, consequence status,
and applied-consequence record.

**Step 2: Confirm failure**

Run the focused runtime and resume tests.

**Step 3: Create and review the migration**

The migration must work for existing rows and preserve immutable definition
snapshots. Apply and downgrade in the supported test environment.

**Step 4: Implement persistence mapping**

Do not add game-specific columns.

**Step 5: Verify and commit**

    git add engine/db/orm.py engine/mini_games/runtime.py alembic/versions engine/tests/test_mini_game_runtime.py engine/tests/test_session_resume.py
    git commit -m "feat(session): persist minigame invocation provenance"

## Task 5: Add Deterministic Coordinator

**Files:**

- Create: engine/mini_games/coordinator.py
- Modify: engine/session/service.py
- Modify: engine/tests/test_session_lifecycle.py
- Create: engine/tests/test_mini_game_coordinator.py

**Step 1: Write failing coordinator tests**

Cover:

- session start and beat-entry invocation;
- authored-order and seeded deterministic selection;
- package lifecycle and adapter compatibility;
- player-count eligibility;
- cooldown and repetition;
- exactly-once invocation on retries;
- no eligible candidate fallback;
- automatic Beat 3 Grill shape without Nightcap IDs in coordinator code;
- no player-request execution.

**Step 2: Confirm failure**

Run the new coordinator test only.

**Step 3: Implement coordinator**

SessionService calls one game-agnostic coordinator hook after deterministic
beat resolution. The coordinator resolves and starts no more than the authored
count and persists provenance before event publication.

**Step 4: Run focused tests**

    python -m pytest engine/tests/test_mini_game_coordinator.py engine/tests/test_session_lifecycle.py engine/tests/test_aw256_beat_hardcode.py -q

**Step 5: Commit**

    git add engine/mini_games/coordinator.py engine/session/service.py engine/tests/test_mini_game_coordinator.py engine/tests/test_session_lifecycle.py
    git commit -m "feat(session): schedule authored minigame opportunities"

## Task 6: Add Adapter Boundary

**Files:**

- Create: engine/mini_games/adapters.py
- Modify: engine/mini_games/runtime.py
- Modify: engine/mini_games/__init__.py
- Create: engine/tests/test_mini_game_adapters.py

**Step 1: Write failing adapter contract tests**

Prove both adapters produce the same invocation lifecycle and result envelope.
Prove host_authoritative:

- cannot submit a result for another invocation;
- rejects wrong package and schema versions;
- is idempotent;
- rejects late or duplicate conflicting results;
- never executes supplied code;
- preserves opaque evidence references without trusting them as state writes.

**Step 2: Implement arcwright_hosted wrapper**

Move no mechanic behavior yet. Wrap existing runtime calls behind the adapter.

**Step 3: Implement host_authoritative protocol**

Keep it transport-independent and schema-only.

**Step 4: Verify and commit**

    python -m pytest engine/tests/test_mini_game_adapters.py engine/tests/test_mini_game_runtime.py -q
    git add engine/mini_games/adapters.py engine/mini_games/runtime.py engine/mini_games/__init__.py engine/tests/test_mini_game_adapters.py
    git commit -m "feat(session): add minigame execution adapters"

## Task 7: Apply Declarative Consequences

**Files:**

- Create: engine/mini_games/consequences.py
- Modify: engine/mini_games/runtime.py
- Modify: engine/resources/resolver.py
- Modify only if required by approved spec: engine/scoring/resolver.py
- Create: engine/tests/test_mini_game_consequences.py
- Modify: engine/tests/test_resources_integration.py
- Modify: engine/tests/test_scoring_integration.py

**Step 1: Write failing tests**

Cover resource delta, score delta, clue variant, knowledge assertion,
obligation or narrative signal, event emission, duplicate result, retry after
partial failure, unknown semantic, unauthorized mapping, and edge-not-gate
fallback.

**Step 2: Confirm failure**

**Step 3: Implement bounded consequence dispatcher**

Use existing canonical services. Never accept arbitrary state patches or
package-provided callables.

**Step 4: Verify**

    python -m pytest engine/tests/test_mini_game_consequences.py engine/tests/test_resources_integration.py engine/tests/test_scoring_integration.py engine/tests/test_knowledge_graph.py -q

**Step 5: Commit**

    git add engine/mini_games/consequences.py engine/mini_games/runtime.py engine/resources engine/scoring engine/tests
    git commit -m "feat(session): apply authored minigame consequences"

## Task 8: Make API and SDK Adapter-neutral

**Files:**

- Modify: api/schemas/__init__.py
- Modify: api/routers/mini_games.py
- Modify: api/tests/test_mini_games_api.py
- Modify: sdk/src/types.ts
- Modify: sdk/src/index.ts
- Create: sdk/tests/mini-game-invocations.test.mjs
- Modify: nightcap-web/src/mini-games/client.ts
- Modify: nightcap-web/tests/mini-game-client.test.ts

**Step 1: Write failing transport tests**

Require package and definition version, adapter, opportunity, status revision,
public-safe runtime config, generic phase or presentation state, and generic
result submission.

Add a regression proving a resumed run never loads latest when pinned to an
older version.

**Step 2: Remove game-ID branches**

Move Tell Me Something True payload and projection behavior behind its hosted
mechanic adapter. FastAPI remains thin.

**Step 3: Preserve authoritative state**

Nightcap web must not discard phase_state or equivalent adapter state during
fetch or reconnect.

**Step 4: Verify**

    python -m pytest api/tests/test_mini_games_api.py engine/tests/test_mini_game_runtime_aw252.py -q
    npm --prefix sdk run typecheck
    npm --prefix sdk run build
    npm --prefix nightcap-web test
    npm --prefix nightcap-web run typecheck

**Step 5: Commit**

    git add api sdk nightcap-web/src/mini-games nightcap-web/tests
    git commit -m "feat(api): expose generic minigame invocations"

## Task 9: Add Timeout Driver

**Files:**

- Modify: engine/mini_games/coordinator.py
- Modify: engine/session/service.py
- Modify: engine/tests/test_mini_game_coordinator.py
- Modify: engine/tests/test_session_resume.py

Write tests for active deadline expiry, pause, resume, process restart,
exactly-once timeout consequence, and no busy polling. Implement through the
session coordinator lifecycle. Verify and commit:

    git commit -m "feat(session): drive minigame timeouts"

## Task 10: Prove a Non-Nightcap Host

**Files:**

- Create: engine/tests/fixtures/arcs/synthetic-host-minigame.arc.json
- Create: engine/tests/fixtures/mini_games/synthetic-host-game
- Create: engine/tests/test_mini_game_host_authoritative_integration.py
- Modify: docs/architecture/14-architecture-validation.md

**Step 1: Write the integration test**

Create a session, enter an opportunity, receive launch data, emulate a host
result, apply a generic consequence, reconnect, and replay. The fixture must
contain no Nightcap beat, Leverage, TV, phone, suspect, or clue vocabulary.

**Step 2: Confirm failure, implement only missing generic behavior, and pass**

**Step 3: Update validation evidence**

Record exactly what was proved and what remains deferred for real SDKs.

**Step 4: Commit**

    git add engine/tests/fixtures engine/tests/test_mini_game_host_authoritative_integration.py docs/architecture/14-architecture-validation.md
    git commit -m "test(arc): prove host-authoritative minigame flow"

## Task 11: Full Verification and Status Reconciliation

Run:

    python -m pytest engine/tests api/tests -q
    python -m ruff check engine api
    python -m ruff format --check engine api
    npm --prefix sdk run typecheck
    npm --prefix sdk run build
    npm --prefix nightcap-web test
    npm --prefix nightcap-web run typecheck

Run migration apply and downgrade checks. Run git diff --check.

Update specs 0077 through 0079, the roadmap tasks, GitHub issues, and program
plan with exact evidence. Request architecture and code review. Do not begin
Nightcap integration until the founder approves the contract checkpoint.
