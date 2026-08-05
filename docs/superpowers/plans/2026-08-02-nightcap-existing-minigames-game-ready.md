# Nightcap Mini-game Whole-session Certification and Closeout Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Integrate all six initial Couch Race mini-games into rotating authored opportunities, prove seamless phone, shared-display, host, multiplayer, story, scoring, and recovery behavior, promote only passing versions to active, and reconcile every related local and GitHub record.

**Architecture:** This is the final integration plan. It consumes approved platform contracts, onboarding tooling, Nightcap registrations and opportunities, and six immutable playtest package candidates. The deterministic coordinator selects each package from its authored candidate pool; package results flow through declarative consequence mappings; the authored arc remains in charge of story progression, Last Call guess lock, Truth, scoring, and replay.

**Tech Stack:** Python 3.11, pytest, FastAPI, SQLAlchemy, Alembic, TypeScript SDK, Nightcap web app, Node test runner, Playwright or the existing browser harness, Arcwright rehearsal harness, Git, GitHub CLI.

## Global Constraints

- Execute only after the contracts, onboarding, six package plans, and Nightcap foundation plan have passed their named gates.
- Refresh from current `origin/main`, audit every PR merged since the plan baseline, and stop on overlapping changes before creating the execution branch.
- Initial opportunities and roles are: Pour `social_opener`, Scene `competitive_discovery`, Grill `interrogation`, Twist `solo_recontextualization`, Last Call `pressure_capstone`, and Truth `reveal_reconstruction`.
- Initial packages are Tell Me Something True, Crime Scene Smash, The Grill, Evidence Locker 402, Interrogation Room, and The Unmasking.
- Eligible pools must support later certified alternatives and deterministic rotation. Initial one-candidate pools are valid but are not hardcoded permanent bindings.
- Last Call must finish its mini-game, allow final interrogation and Leverage use, lock guesses, then enter Truth. Truth must not change a locked guess or case truth.
- Do not implement D-097's currency-funded player-requested Grill.
- Package lifecycle becomes `active` only after package, registration, integrated-session, real-device, real-player, founder, and status-reconciliation gates pass.
- A merged partial PR is not completion evidence for an unmet issue, epic, or milestone criterion.

---

### Task 1: Execute the Fresh-main and Dependency Gate

**Files:**

- Read: `docs/product/mini-game-readiness/mainline-safety-report.md`
- Read: `docs/product/mini-game-readiness/`
- Read: `docs/roadmap/index.json`
- Read: `nightcap/couch-race.arc.json`

**Interfaces:**

- Consumes: current GitHub merged-PR state, clean worktree evidence, approved specs 0076 through 0085, accepted ADR 0018, and all prerequisite plan checkpoints.
- Produces: one current safety report and an explicit founder approval to begin final integration.

- [ ] **Step 1: Fetch and audit current main**

```powershell
git fetch origin --prune
git log --oneline --decorate --max-count=20 origin/main
gh pr list --state merged --limit 30 --json number,title,mergedAt,mergeCommit,files
git status --short
```

Compare merged files against every file named in this plan and its prerequisite
plans. If main advanced, recreate or rebase the isolated `codex/` worktree from
the new `origin/main`; never execute from the planning branch's stale base.

- [ ] **Step 2: Verify prerequisite evidence**

```powershell
rg -n '"status": "READY"|"status": "INTEGRATION_PENDING"' docs/product/mini-game-readiness
rg -n "Status: Approved|Status: Accepted" docs/specs docs/decisions/0018-mini-game-platform-orchestration.md
python docs/skills/arcwright-minigame/scripts/minigame_tool.py validate-arc nightcap/couch-race.arc.json
```

Required: six immutable playtest package versions and digests, six valid
registrations, six valid opportunity pools, no unresolved contract blocker,
and all founder creative checkpoints recorded.

- [ ] **Step 3: Run the integrated baseline**

```powershell
python -m pytest engine/tests api/tests -q
python -m ruff check engine api
python -m ruff format --check engine api
npm --prefix sdk run typecheck
npm --prefix sdk run build
npm --prefix nightcap-web test
npm --prefix nightcap-web run typecheck
npm --prefix nightcap-web run build
```

- [ ] **Step 4: Stop for separate founder final-integration approval**

### Task 2: Pin Registrations to Certified Package Artifacts

**Files:**

- Modify: `nightcap/couch-race.arc.json`
- Modify: `nightcap-web/scripts/discover-mini-games.mjs`
- Create: `engine/tests/test_nightcap_mini_game_opportunities.py`
- Modify: `nightcap-web/tests/mini-game-registry.test.ts`

**Interfaces:**

- Consumes: exact package versions, SHA-256 definition digests, registration IDs, candidate pools, lifecycle metadata, and renderer discovery.
- Produces: reproducible registration resolution with no `latest` alias or unpinned package load.

- [ ] **Step 1: Write failing exact-version tests**

```python
EXPECTED = {
    "couch-race-tmst": "tell-me-something-true",
    "couch-race-crime-scene": "crime-scene-smash",
    "couch-race-grill": "the-grill-interrogation",
    "couch-race-evidence-locker": "evidence-locker-402",
    "couch-race-interrogation-room": "interrogation-room",
    "couch-race-unmasking": "the-unmasking",
}


def test_every_initial_registration_resolves_exact_certified_artifact(catalog):
    assert {item.registration_id: item.game_id for item in catalog.registrations} == EXPECTED
    assert all(item.version and item.definition_sha256 for item in catalog.registrations)
    assert all(catalog.verify_digest(item) for item in catalog.registrations)
```

- [ ] **Step 2: Write a failing renderer-version test**

```javascript
test("registry contains only exact registered package versions", async () => {
  const registry = await buildRegistry();
  assert.equal(registry.entries.length, 6);
  assert.equal(registry.entries.some((entry) => entry.version === "latest"), false);
  assert.equal(registry.entries.every((entry) => entry.definitionSha256.length === 64), true);
});
```

- [ ] **Step 3: Run and confirm failure**

```powershell
python -m pytest engine/tests/test_nightcap_mini_game_opportunities.py -q
npm --prefix nightcap-web test
```

- [ ] **Step 4: Pin all artifacts and remove stale aliases**

Copy the exact playtest version and digest from each readiness report into its
registration. Keep each beat's `eligible_registration_ids` as a candidate
pool, even when the initial pool has one member. Registry generation must fail
closed for a missing renderer, inactive registration, digest mismatch, fixture,
or unpinned version.

- [ ] **Step 5: Run and commit**

```powershell
python -m pytest engine/tests/test_nightcap_mini_game_opportunities.py -q
npm --prefix nightcap-web test
git add nightcap/couch-race.arc.json nightcap-web/scripts/discover-mini-games.mjs engine/tests/test_nightcap_mini_game_opportunities.py nightcap-web/tests/mini-game-registry.test.ts
git commit -m "feat(nightcap): pin couch race minigame pool"
```

### Task 3: Prove Candidate Rotation and Story-role Boundaries

**Files:**

- Create: `engine/tests/fixtures/mini_games/rotation-candidate-a/manifest.json`
- Create: `engine/tests/fixtures/mini_games/rotation-candidate-a/definitions/1.0.0.json`
- Create: `engine/tests/fixtures/mini_games/rotation-candidate-b/manifest.json`
- Create: `engine/tests/fixtures/mini_games/rotation-candidate-b/definitions/1.0.0.json`
- Modify: `engine/tests/test_nightcap_mini_game_opportunities.py`

**Interfaces:**

- Consumes: deterministic `session_seeded_rotation`, candidate eligibility, within-session history, story roles, and fallback.
- Produces: evidence that future certified games can rotate into a beat without code changes or autonomous story design.

- [ ] **Step 1: Write failing rotation tests**

```python
def test_same_session_state_replays_same_selection(coordinator, opportunity):
    first = coordinator.select(opportunity, session_id="session-a", recent_registration_ids=[])
    replay = coordinator.select(opportunity, session_id="session-a", recent_registration_ids=[])
    assert replay.registration_id == first.registration_id


def test_repeatable_opportunity_avoids_recent_candidate_when_another_is_eligible(coordinator, opportunity):
    first = coordinator.select(opportunity, session_id="session-a", recent_registration_ids=[])
    second = coordinator.select(opportunity, session_id="session-a", recent_registration_ids=[first.registration_id])
    assert second.registration_id != first.registration_id
```

- [ ] **Step 2: Write failing authored-role tests**

```python
def test_candidate_cannot_escape_authored_story_role(coordinator, pressure_opportunity):
    selected = coordinator.eligible(pressure_opportunity)
    assert all("pressure_capstone" in candidate.story_roles for candidate in selected)


def test_selector_never_uses_model_router(router_spy, coordinator, opportunity):
    coordinator.select(opportunity, session_id="session-a", recent_registration_ids=[])
    router_spy.assert_not_called()
```

- [ ] **Step 3: Implement fixtures and run**

```powershell
python -m pytest engine/tests/test_nightcap_mini_game_opportunities.py -q
```

Expected: selection is replayable, avoids the recent candidate when policy
allows, falls back deterministically when none are eligible, and never changes
the human-authored story role. Cross-session history remains an optional
continuity input, not a Nightcap v1 dependency.

- [ ] **Step 4: Commit**

```powershell
git add engine/tests/fixtures/mini_games/rotation-candidate-a engine/tests/fixtures/mini_games/rotation-candidate-b engine/tests/test_nightcap_mini_game_opportunities.py
git commit -m "test(arc): prove minigame candidate rotation"
```

### Task 4: Prove Two-player and Eight-player Whole Sessions

**Files:**

- Create: `engine/tests/fixtures/nightcap_minigame_full_session.json`
- Create: `engine/tests/test_nightcap_minigame_full_session.py`
- Modify: `scripts/rehearsal_smoke.py`

**Interfaces:**

- Consumes: registered Couch Race arc, six opportunities, two-surface projections, deterministic package actions, timeouts, reconnects, consequence services, guess lock, reveal, and final scores.
- Produces: replayable headless evidence for the entire six-beat session at both player-count limits.

- [ ] **Step 1: Write the failing whole-session assertions**

```python
@pytest.mark.parametrize("player_count", [2, 8])
async def test_all_six_opportunities_complete_in_story_order(harness, player_count):
    result = await harness.run_couch_race(player_count=player_count, seed=f"full-{player_count}")
    assert result.completed_opportunity_roles == [
        "social_opener", "competitive_discovery", "interrogation",
        "solo_recontextualization", "pressure_capstone", "reveal_reconstruction",
    ]
    assert result.guesses_locked_before_truth is True
    assert result.case_truth_revision == 1
    assert result.podium.completed is True
```

- [ ] **Step 2: Add failure-path assertions**

```python
async def test_timeout_disconnect_and_generation_failure_preserve_story_progress(harness):
    result = await harness.run_failure_matrix()
    assert result.duplicate_consequence_count == 0
    assert result.required_clues_available is True
    assert result.finished_truth is True
```

- [ ] **Step 3: Run and confirm failure**

```powershell
python -m pytest engine/tests/test_nightcap_minigame_full_session.py -q
```

- [ ] **Step 4: Extend the harness only where evidence requires it**

Add deterministic actions for all package mechanics, player-count projections,
disconnect and reconnect, duplicate delivery, pause and resume, timeout,
generated-content failure, host loss, Last Call lock, solved and house-win
Truth, score animation events, ranks, and podium.

- [ ] **Step 5: Run and commit**

```powershell
python -m pytest engine/tests/test_nightcap_minigame_full_session.py engine/tests/test_harness_scenarios.py -q
python scripts/rehearsal_smoke.py --arc nightcap-couch-race-v1 --players 2
python scripts/rehearsal_smoke.py --arc nightcap-couch-race-v1 --players 8
git add engine/tests/fixtures/nightcap_minigame_full_session.json engine/tests/test_nightcap_minigame_full_session.py scripts/rehearsal_smoke.py
git commit -m "test(nightcap): prove six-beat minigame sessions"
```

### Task 5: Run Real-device and Founder Experience Gates

**Files:**

- Create: `docs/product/mini-game-readiness/couch-race-device-matrix.md`
- Create: `docs/product/mini-game-readiness/couch-race-founder-walkthrough.md`
- Modify: `docs/product/mini-game-readiness/tell-me-something-true-0.2.0.json`
- Modify: `docs/product/mini-game-readiness/crime-scene-smash-0.2.0.json`
- Modify: `docs/product/mini-game-readiness/the-grill-interrogation-0.1.0.json`
- Modify: `docs/product/mini-game-readiness/evidence-locker-402-0.2.0.json`
- Modify: `docs/product/mini-game-readiness/interrogation-room-0.1.0.json`
- Modify: `docs/product/mini-game-readiness/the-unmasking-0.1.0.json`

**Interfaces:**

- Consumes: deployed or local full stack, two to eight phones, shared display, host controls, six game artifacts, accessibility modes, and founder review.
- Produces: device evidence, experience decisions, remediation list, and explicit pass or fail per game and whole-session gate.

- [ ] **Step 1: Complete device preflight**

Record build SHA, URL, API version, package versions and digests, browser and
OS versions, network, phone identities, shared-display resolution, host
identity, audio route, and enabled accessibility settings.

- [ ] **Step 2: Walk every package on phone, TV, and host**

For each game verify join, launch, rules, gameplay, competition, story posture,
public and private separation, Leverage or score consequence, animation,
graphics, audio, timeout, reconnect, pause/resume, fallback, completion, and
transition. Verify 2-player and 8-player layouts.

- [ ] **Step 3: Walk the Last Call through Truth climax**

Verify Trivia raises pressure, final interrogation remains usable, Leverage
actions settle, guesses lock privately, Truth begins from immutable guesses,
The Unmasking clears suspects, credits catches, reveals the culprit, resolves
solved or house win, animates final scores and ranks, lands the winners podium,
awards superlatives, and offers replay.

- [ ] **Step 4: Stop for founder signoff or remediation direction**

Founder approval is required separately for each game's artifact and the
whole-session rhythm. Record findings verbatim enough to distinguish accepted
tuning from deferred ideas. Do not convert a failed quality gate into a pass.

### Task 6: Run AW-286 Real-player Rehearsal and Remediate

**Files:**

- Modify: `docs/roadmap/tasks/AW-286-couch-race-rehearsal-slice-and-rehearsal-1-retarget.md`
- Modify: `docs/roadmap/operations/rehearsal-1-blocker-log.md`
- Create: `docs/product/mini-game-readiness/couch-race-rehearsal-report.md`

**Interfaces:**

- Consumes: approved device build, real players, AW-286 observation guide, telemetry, facilitator notes, and founder checkpoints.
- Produces: real-player evidence for fun, fairness, comprehension, pressure curve, story enhancement, rotation value, replay desire, and technical stability.

- [ ] **Step 1: Pause at rehearsal preparation and preflight gates**

Verify participant consent, session configuration, telemetry privacy, test
wrapper, device readiness, fallback controls, observation roles, and build SHA.

- [ ] **Step 2: Run the session without coaching game outcomes**

Observe whether players understand each game, remain competitive, use the
story edge, watch the shared display, recover from failure, feel Last Call
pressure, understand The Truth, recognize their credited catches, and want a
new rotated set next session.

- [ ] **Step 3: Debrief before remediation**

Classify every finding as defect, tuning, creative choice, platform gap,
onboarding gap, deferred currency design, or future rotation candidate. Obtain
founder direction before changes requiring taste or expanded scope.

- [ ] **Step 4: Route accepted defects into scoped remediation plans**

For every accepted defect, write an exact-file remediation plan with the
smallest failing automated reproduction, focused implementation, affected
suite, commit, and repeated human gate. Stop this plan for approval, execute
the remediation plan, then resume here with its commit and evidence.

- [ ] **Step 5: Record exact rehearsal result**

Do not mark AW-286 passed from a headless or simulated session. Record player
count, devices, session ID, build SHA, completed beats, package versions,
observations, failures, remediations, founder decisions, and remaining gates.

### Task 7: Certify Registrations, Promote Active, and Reconcile All Status

**Files:**

- Modify: `nightcap/mini_games/tell-me-something-true/manifest.json`
- Modify: `nightcap/mini_games/crime-scene-smash/manifest.json`
- Modify: `nightcap/mini_games/the-grill-interrogation/manifest.json`
- Modify: `nightcap/mini_games/evidence-locker-402/manifest.json`
- Modify: `nightcap/mini_games/interrogation-room/manifest.json`
- Modify: `nightcap/mini_games/the-unmasking/manifest.json`
- Modify: `docs/product/mini-game-readiness/tell-me-something-true-0.2.0.json`
- Modify: `docs/product/mini-game-readiness/crime-scene-smash-0.2.0.json`
- Modify: `docs/product/mini-game-readiness/the-grill-interrogation-0.1.0.json`
- Modify: `docs/product/mini-game-readiness/evidence-locker-402-0.2.0.json`
- Modify: `docs/product/mini-game-readiness/interrogation-room-0.1.0.json`
- Modify: `docs/product/mini-game-readiness/the-unmasking-0.1.0.json`
- Modify: `docs/product/mini-game-readiness/couch-race-program-status.json`
- Modify: `docs/product/decisions-log.csv`
- Modify: `docs/roadmap/index.json`
- Modify: `docs/roadmap/tasks/AW-278-couch-race-truth-sequence-and-reveal-accounting.md`
- Modify: `docs/roadmap/tasks/AW-285-couch-race-tv-and-phone-rendering.md`
- Modify: `docs/roadmap/tasks/AW-286-couch-race-rehearsal-slice-and-rehearsal-1-retarget.md`
- Modify: `docs/roadmap/tasks/AW-288-couch-race-mini-game-beat-coverage-and-tmst-acceleration.md`
- Modify: `docs/roadmap/tasks/AW-289-couch-race-trivia-mini-game.md`
- Modify: `docs/roadmap/epics/M5-F-tell-me-something-true-social-opener.md`
- Modify: `docs/roadmap/epics/M5-I-nightcap-couch-race-arc-and-interrogation.md`
- Modify: `docs/roadmap/milestones/M6-first-qualifying-sessions.md`
- Modify: `docs/roadmap/operations/rehearsal-1-blocker-log.md`

**Interfaces:**

- Consumes: all automated, synthetic host, device, founder, and real-player evidence.
- Produces: active package lifecycle only for passing artifacts, machine-readable program status, consistent canonical records, and accurate GitHub closure.

- [ ] **Step 1: Run integrated certification for all registrations**

```powershell
python docs/skills/arcwright-minigame/scripts/minigame_tool.py certify --arc nightcap/couch-race.arc.json --registration-id couch-race-tmst --output docs/product/mini-game-readiness/tell-me-something-true-0.2.0.json
python docs/skills/arcwright-minigame/scripts/minigame_tool.py certify --arc nightcap/couch-race.arc.json --registration-id couch-race-crime-scene --output docs/product/mini-game-readiness/crime-scene-smash-0.2.0.json
python docs/skills/arcwright-minigame/scripts/minigame_tool.py certify --arc nightcap/couch-race.arc.json --registration-id couch-race-grill --output docs/product/mini-game-readiness/the-grill-interrogation-0.1.0.json
python docs/skills/arcwright-minigame/scripts/minigame_tool.py certify --arc nightcap/couch-race.arc.json --registration-id couch-race-evidence-locker --output docs/product/mini-game-readiness/evidence-locker-402-0.2.0.json
python docs/skills/arcwright-minigame/scripts/minigame_tool.py certify --arc nightcap/couch-race.arc.json --registration-id couch-race-interrogation-room --output docs/product/mini-game-readiness/interrogation-room-0.1.0.json
python docs/skills/arcwright-minigame/scripts/minigame_tool.py certify --arc nightcap/couch-race.arc.json --registration-id couch-race-unmasking --output docs/product/mini-game-readiness/the-unmasking-0.1.0.json
```

Expected: every applicable automated and human gate is `PASS`, every report
status is `READY`, and no field remains `INTEGRATION_PENDING`.

- [ ] **Step 2: Promote only passing package versions to active**

Change lifecycle metadata from `playtest` to `active` only after its exact
report passes. Recompute integrity metadata where lifecycle metadata is part of
the signed or hashed artifact; update the registration atomically.

- [ ] **Step 3: Run final verification**

```powershell
python -m pytest engine/tests api/tests -q
python -m ruff check engine api
python -m ruff format --check engine api
npm --prefix sdk run typecheck
npm --prefix sdk run build
npm --prefix nightcap-web test
npm --prefix nightcap-web run typecheck
npm --prefix nightcap-web run build
git diff --check
git status --short
```

- [ ] **Step 4: Reconcile canonical status by evidence**

Update each plan, spec, task, epic, milestone, decision reference, readiness
report, and roadmap index. Close only criteria proved by the recorded evidence.
Record partial outcomes and owner actions instead of overstating completion.
Keep D-097 deferred and link its future reopening condition.

- [ ] **Step 5: Reconcile GitHub last**

Use `gh issue view` and `gh pr view` to refresh every related record. Comment
with exact commit, tests, device evidence, rehearsal evidence, and remaining
gates. Close an issue only when all of its current acceptance criteria pass.
Update epic and milestone status only after their children and exit gates pass.

- [ ] **Step 6: Commit closeout and stop before merge**

```powershell
git add nightcap/mini_games docs/product/mini-game-readiness docs/product/decisions-log.csv docs/roadmap docs/specs docs/superpowers/plans docs/decisions
git commit -m "docs(nightcap): reconcile minigame readiness"
```

Request review with `superpowers:requesting-code-review`, address accepted
findings, rerun verification with `superpowers:verification-before-completion`,
and present the branch for founder merge approval. Do not merge automatically.
