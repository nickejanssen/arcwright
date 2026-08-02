# Evidence Locker 402 Game-ready Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert Evidence Locker 402 from a single-player HTML prototype and stub plugin into a production-ready selected-player lock-picking challenge that engages a 2 to 8 player room.

**Architecture:** The package supports sessions of 2 to 8 players while selecting one active participant per invocation. Python deterministically chooses the least-recently-selected eligible player, resolves pin targets and order from the invocation seed, validates release actions, and owns timeout and outcome. Non-selected phones and the shared display receive spectator-safe progress, never private target values.

**Tech Stack:** Python 3.11, deterministic hashing, pytest, TypeScript, Nightcap mini-game kit, Node test runner, happy-dom, JSON.

## Global Constraints

- Create and approve `docs/specs/0083-evidence-locker-402-game-ready.md` before implementation.
- Use exact package version `0.2.0`; preserve 0.1.0.
- Support a 2 to 8 player session with exactly one active puzzle participant.
- Selection order is fewest prior selections in the session, then deterministic invocation-seeded hash, then stable join order.
- Python owns selected player, pin order, target bands, tolerance, action revision, break, success, timeout, and result.
- Shared display and non-selected phones never receive exact target positions or the selected player's private controls.
- Success provides an edge; failure and timeout preserve the normal evidence path.
- Human device, spectator-engagement, accessibility, and gameplay gates are required before activation.

---

### Task 1: Approve Selected-player Rules and Artifact

**Files:**

- Create: `docs/specs/0083-evidence-locker-402-game-ready.md`
- Modify: `nightcap/mini_games/evidence-locker-402/README.md`

**Interfaces:**

- Consumes: D-062, package 0.1.0, Twist role, and generic hosted adapter contracts.
- Produces: approved participant selection, pressure-mode puzzle, payload, spectator, result, and fallback contracts.

- [ ] **Step 1: Execute preflight and baseline**

```powershell
python -m pytest engine/tests/test_mini_game_runtime.py engine/tests/test_mini_game_models.py -q
npm --prefix nightcap-web test
```

- [ ] **Step 2: Write the exact proposed rules**

```text
session range: 2-8 players
active participant count: 1
selection: fewest prior selected-player runs, seeded hash, join order
mode: pressure, four pins, 45 seconds, tolerance 10 units
input: release_pin with pin_index, lift_value 0-100, state_revision
success: four pins released in authored order inside target tolerance
break: wrong-order release or lift_value in authored red zone
timeout/break: reduced-edge fallback, story continues
spectators: public pin count, time, selected detective, success/break staging
```

- [ ] **Step 3: Present phone, spectator, shared, and host fixture preview**

Show keyboard and touch control, selected-player handoff, non-selected phone,
shared pin progress, reconnect, disconnect before selection, disconnect during
play, break, success, timeout, sound, motion, and reduced motion.

- [ ] **Step 4: Stop for founder rules, artifact, and implementation approval**

### Task 2: Clarify Session and Active Participant Ranges

**Files:**

- Modify: `engine/mini_games/models.py`
- Modify: `nightcap-web/src/mini-game-kit/types.ts`
- Modify: `nightcap/mini_games/evidence-locker-402/manifest.json`
- Create: `nightcap/mini_games/evidence-locker-402/definitions/0.2.0.json`
- Test: `engine/tests/test_mini_game_models.py`

**Interfaces:**

- Consumes: existing `min_players` and `max_players` as active participant range.
- Produces: `session_min_players`, `session_max_players`, and unambiguous eligibility behavior.

- [ ] **Step 1: Write a failing range test**

```python
def test_single_active_player_package_supports_eight_player_session():
    loaded = load_mini_game_package(Path("nightcap/mini_games/evidence-locker-402"))
    definition = loaded.definition
    assert (definition.min_players, definition.max_players) == (1, 1)
    assert (definition.session_min_players, definition.session_max_players) == (2, 8)
```

- [ ] **Step 2: Run and confirm failure**

```powershell
python -m pytest engine/tests/test_mini_game_models.py -q
```

- [ ] **Step 3: Add explicit session range fields**

```python
class MiniGameDefinition(BaseModel):
    min_players: int = Field(ge=1)
    max_players: int = Field(ge=1)
    session_min_players: int = Field(ge=1)
    session_max_players: int = Field(ge=1)
```

Validate both ranges independently. Existing package definitions receive
explicit session ranges equal to their current active ranges during migration.
The coordinator checks session range; the hosted adapter checks selected active
participant range.

- [ ] **Step 4: Author package 0.2.0**

Normalize `success_clue` and `fallback_clue` into result semantics and the
generic edge-not-gate profile. Add `solo-recontextualization` capability,
hosted adapter support, renderer declaration, and exact digest. Set lifecycle
to `playtest`.

- [ ] **Step 5: Run and commit**

```powershell
python -m pytest engine/tests/test_mini_game_models.py -q
python docs/skills/arcwright-minigame/scripts/minigame_tool.py validate nightcap/mini_games/evidence-locker-402
npm --prefix nightcap-web run typecheck
git add engine/mini_games/models.py engine/tests/test_mini_game_models.py nightcap-web/src/mini-game-kit/types.ts nightcap/mini_games/evidence-locker-402
git commit -m "feat(arc): distinguish session and active players"
```

### Task 3: Implement Deterministic Selection and Lock State

**Files:**

- Modify: `engine/mini_games/plugins/_evidence_locker_breach.py`
- Create: `engine/tests/test_evidence_locker_breach_runtime.py`

**Interfaces:**

- Consumes: stateful mechanic protocol, participant list, selection history, invocation seed, and release payload.
- Produces: `EvidenceLockerState`, selected-player projection, spectator projection, and deterministic result semantics.

- [ ] **Step 1: Write failing selection tests**

```python
def test_selects_least_recently_used_player(plugin):
    selected = plugin.select_participant(
        participants=PARTICIPANTS,
        prior_selection_counts={str(CHAR_A): 2, str(CHAR_B): 0},
        seed="run-1",
    )
    assert selected == CHAR_B


def test_selection_is_replayable(plugin):
    first = plugin.select_participant(PARTICIPANTS, {}, seed="run-1")
    second = plugin.select_participant(PARTICIPANTS, {}, seed="run-1")
    assert second == first
```

- [ ] **Step 2: Write failing pin validation tests**

```python
def test_release_inside_tolerance_sets_current_pin(plugin, pressure_state):
    progress = plugin.release_pin(
        pressure_state,
        pin_index=pressure_state.pin_order[0],
        lift_value=pressure_state.targets[pressure_state.pin_order[0]],
        state_revision=0,
    )
    assert progress.set_pin_count == 1
    assert progress.state_revision == 1


def test_wrong_order_breaks_pick(plugin, pressure_state):
    with pytest.raises(PickBrokenError):
        plugin.release_pin(
            pressure_state,
            pin_index=pressure_state.pin_order[1],
            lift_value=50,
            state_revision=0,
        )
```

- [ ] **Step 3: Run and confirm failure**

```powershell
python -m pytest engine/tests/test_evidence_locker_breach_runtime.py -q
```

- [ ] **Step 4: Define exact state interface**

```python
class EvidenceLockerState(BaseModel):
    selected_character_id: UUID
    mode: Literal["pressure"]
    pin_order: tuple[int, int, int, int]
    targets: tuple[int, int, int, int]
    tolerance: int = 10
    set_pin_indices: tuple[int, ...] = ()
    state_revision: int = 0
    status: Literal["active", "opened", "broken"] = "active"
```

Generate order and targets from SHA-256 of invocation seed and selected
character. Project targets and order only to the selected player. Public
projection contains selected character, set-pin count, total pins, deadline,
and status.

- [ ] **Step 5: Add runtime success, disconnect, timeout, and reconnect tests**

```python
async def test_selected_player_disconnect_uses_fallback(runtime):
    run = await start_evidence_locker(runtime)
    await submit_presence(runtime, selected_character(run), connected=False)
    assert (await runtime.get_run(run.run_id)).status == "cancelled"
    assert run.outcome["fallback-used"] is True
```

- [ ] **Step 6: Run and commit**

```powershell
python -m pytest engine/tests/test_evidence_locker_breach_runtime.py engine/tests/test_mini_game_runtime.py -q
git add engine/mini_games/plugins/_evidence_locker_breach.py engine/tests/test_evidence_locker_breach_runtime.py
git commit -m "feat(nightcap): implement evidence locker 402"
```

### Task 4: Build Selected-player and Spectator Renderers

**Files:**

- Create: `nightcap/mini_games/evidence-locker-402/client/renderer.ts`
- Create: `nightcap/mini_games/evidence-locker-402/client/styles.css`
- Create: `nightcap/mini_games/evidence-locker-402/client/renderer.test.ts`
- Preserve as reference: `nightcap/mini_games/evidence-locker-402/client/index.html`

**Interfaces:**

- Consumes: selected-player private state, spectator-safe state, authoritative deadline, semantic theme, and lifecycle events.
- Produces: selected phone controls, spectator phone status, shared spectacle, and host operations.

- [ ] **Step 1: Write failing privacy tests**

```typescript
test("only selected phone receives pin targets", () => {
  renderer.mount(selectedRoot, selectedContext());
  renderer.mount(spectatorRoot, spectatorContext());
  assert.match(selectedRoot.textContent ?? "", /Lift/);
  assert.doesNotMatch(spectatorRoot.textContent ?? "", /Target 63/);
});
```

- [ ] **Step 2: Write failing release payload test**

```typescript
test("release sends pin value and revision only", async () => {
  const ctx = selectedContext();
  renderer.mount(root, ctx);
  await releaseCurrentPin(root, 63);
  assert.deepEqual(ctx.lastPayload, {
    action: "release_pin",
    pin_index: 2,
    lift_value: 63,
    state_revision: 0,
  });
});
```

- [ ] **Step 3: Implement all states and surfaces**

Use accessible lift controls, authoritative timer, haptic-safe visual feedback,
shared pin animation, spectator tension copy, reconnect, disconnect fallback,
success, break, timeout, reduced motion, and audio controls.

- [ ] **Step 4: Run and commit**

```powershell
npm --prefix nightcap-web test
npm --prefix nightcap-web run typecheck
npm --prefix nightcap-web run bundle:mini-games
git add nightcap/mini_games/evidence-locker-402/client
git commit -m "feat(nightcap): render evidence locker 402"
```

### Task 5: Produce the Evidence Locker 402 Package-readiness Evidence

**Files:**

- Modify: `nightcap/mini_games/evidence-locker-402/manifest.json`
- Create: `docs/roadmap/operations/evidence-locker-device-walkthrough.md`
- Create: `docs/roadmap/operations/evidence-locker-rehearsal.md`
- Modify: `docs/specs/0083-evidence-locker-402-game-ready.md`
- Create: `docs/product/mini-game-readiness/evidence-locker-402-0.2.0.json`

**Interfaces:**

- Consumes: automated evidence, selected and spectator device evidence, human rehearsal, and founder sign-off.
- Produces: immutable 0.2.0 playtest candidate and explicit `INTEGRATION_PENDING` evidence.

- [ ] **Step 1: Run automated certification**

```powershell
python -m pytest engine/tests/test_evidence_locker_breach_runtime.py engine/tests/test_mini_game_models.py -q
npm --prefix nightcap-web test
python docs/skills/arcwright-minigame/scripts/minigame_tool.py certify --package nightcap/mini_games/evidence-locker-402 --output docs/product/mini-game-readiness/evidence-locker-402-0.2.0.json
```

- [ ] **Step 2: Run real-device walkthrough**

Verify selected controls, spectator engagement, shared display, host status,
fair player selection, handoff, reconnect, disconnect, timeout, accessibility,
sound, motion, reduced motion, and privacy for 2 and 8 players.

- [ ] **Step 3: Run real-player rehearsal**

Measure selection fairness, pressure, spectator attention, control clarity,
success satisfaction, failure grace, Twist fit, and replay desire. Blocking
findings require a new package version and repeated gates.

- [ ] **Step 4: Obtain package sign-off, keep playtest lifecycle, and commit**

```powershell
python docs/skills/arcwright-minigame/scripts/minigame_tool.py validate nightcap/mini_games/evidence-locker-402
git diff --check
git add nightcap/mini_games/evidence-locker-402/manifest.json docs/specs/0083-evidence-locker-402-game-ready.md docs/roadmap/operations/evidence-locker-device-walkthrough.md docs/roadmap/operations/evidence-locker-rehearsal.md docs/product/mini-game-readiness/evidence-locker-402-0.2.0.json
git commit -m "test(nightcap): certify evidence locker 402"
```

Do not promote to `active` here. The final integration plan owns exact
registration, whole-session evidence, active promotion, and GitHub closure.
