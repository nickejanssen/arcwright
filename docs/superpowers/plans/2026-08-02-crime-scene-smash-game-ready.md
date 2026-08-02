# Crime Scene Smash Game-ready Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert Crime Scene Smash from an active prototype with a stub mechanic into a deterministic, competitive, production-ready evidence-smash race for 2 to 8 players.

**Architecture:** Python generates and advances one private 8x8 board per participant from the invocation seed. Clients submit adjacent swaps with the authoritative board revision; the hosted plugin validates swaps, resolves matches and cascades, and emits private board state plus table-safe leaderboard events. Package result semantics expose ranks and performance only; the arc maps them to bounded rewards.

**Tech Stack:** Python 3.11, hashlib-seeded board generation, pytest, TypeScript, Nightcap mini-game kit, Node test runner, happy-dom, JSON.

## Global Constraints

- Create and approve `docs/specs/0082-crime-scene-smash-game-ready.md` before implementation.
- Use exact package version `0.2.0`; preserve `0.1.0`.
- Support 2 to 8 simultaneous players for 90 seconds.
- Use six authored tile roles on an 8x8 private board.
- Python owns board seed, swap validation, match resolution, cascade order, score, rank, timeout, and tie-breaks.
- The browser never sends a score, match set, replacement tile, or winner.
- Tie-break order is final score, maximum chain depth, completion timestamp, then stable participant join order.
- A loss or timeout never removes required evidence.
- Human visual, device, performance, and fun gates are required before activation.

---

### Task 1: Approve Rules, Formula, and Presentation Artifact

**Files:**

- Create: `docs/specs/0082-crime-scene-smash-game-ready.md`
- Modify: `nightcap/mini_games/crime-scene-smash/README.md`

**Interfaces:**

- Consumes: D-062, D-093, package 0.1.0, and generic hosted adapter contracts.
- Produces: approved board algorithm, payload, formula, tie-break, event, reward-semantic, and surface contracts.

- [ ] **Step 1: Execute preflight and baseline**

```powershell
python -m pytest engine/tests/test_mini_game_runtime.py engine/tests/test_mini_game_models.py -q
npm --prefix nightcap-web test
```

- [ ] **Step 2: Write the exact proposed rules**

```text
board: 8 columns x 8 rows, six tile roles, no initial matches
input: swap two orthogonally adjacent coordinates plus board_revision
valid move: swap creates at least one horizontal or vertical run of 3+
resolution: horizontal and vertical matches union, remove, fall by column, refill from seeded stream, repeat cascades
score: 10 points per removed tile x cascade depth
special activation: every run of 5+ adds a 50-point lead-burst
invalid move: board unchanged, invalid-swap-count increments
round end: server deadline at 90 seconds
tie-break: score, maximum cascade depth, earliest final accepted move, stable join order
```

- [ ] **Step 3: Present interactive and audiovisual fixture**

Show private board, valid and invalid swap feedback, cascade, combo, shared
leaderboard, final-five countdown, winner reveal, 2-player state, 8-player
state, reduced motion, timeout, and reconnect.

- [ ] **Step 4: Stop for founder rules, artifact, and implementation approval**

### Task 2: Version the Package Contract

**Files:**

- Modify: `nightcap/mini_games/crime-scene-smash/manifest.json`
- Create: `nightcap/mini_games/crime-scene-smash/definitions/0.2.0.json`
- Test: `engine/tests/test_mini_game_models.py`

**Interfaces:**

- Consumes: approved spec 0082.
- Produces: immutable playtest definition 0.2.0 with `competitive-discovery` capability.

- [ ] **Step 1: Write a failing version test**

```python
def test_crime_scene_smash_020_is_two_to_eight_player_hosted_game():
    loaded = load_mini_game_package(Path("nightcap/mini_games/crime-scene-smash"))
    assert loaded.definition.version == "0.2.0"
    assert (loaded.definition.min_players, loaded.definition.max_players) == (2, 8)
    assert loaded.definition.mechanic_type == "match-3-clue-race"
    assert "competitive-discovery" in loaded.manifest.capability_tags
```

- [ ] **Step 2: Run and confirm failure**

```powershell
python -m pytest engine/tests/test_mini_game_models.py -q
```

- [ ] **Step 3: Author 0.2.0 and calculate digest**

Replace `tie_break: narrative` with the approved deterministic tie-break. Add
payload schema, event vocabulary, result semantics, two-player behavior,
adapter support, renderer declaration, and exact definition digest. Set
lifecycle to `playtest`.

- [ ] **Step 4: Validate and commit**

```powershell
python docs/skills/arcwright-minigame/scripts/minigame_tool.py validate nightcap/mini_games/crime-scene-smash
git add nightcap/mini_games/crime-scene-smash engine/tests/test_mini_game_models.py
git commit -m "feat(nightcap): version crime scene smash"
```

### Task 3: Implement Authoritative Match-3 State

**Files:**

- Modify: `engine/mini_games/plugins/_match_3_clue_race.py`
- Create: `engine/tests/test_match_3_clue_race_runtime.py`

**Interfaces:**

- Consumes: `StatefulMechanicPlugin`, participant list, resolved snapshot seed, and swap payload.
- Produces: `Match3State`, private board projections, deterministic score outcome, and leaderboard events.

- [ ] **Step 1: Write failing board determinism tests**

```python
def test_same_seed_and_character_produce_same_match_free_board(plugin):
    first = plugin.build_board(seed="run-1", character_id=CHARACTER_ID)
    second = plugin.build_board(seed="run-1", character_id=CHARACTER_ID)
    assert first == second
    assert len(first) == 8 and all(len(row) == 8 for row in first)
    assert plugin.find_matches(first) == set()
```

- [ ] **Step 2: Write failing swap and cascade tests**

```python
def test_valid_swap_resolves_cascade_and_increments_revision(plugin, board_fixture):
    result = plugin.resolve_swap(board_fixture, (2, 3), (2, 4), revision=7)
    assert result.accepted is True
    assert result.board_revision == 8
    assert result.removed_tile_count >= 3
    assert result.score_delta >= 30


def test_non_adjacent_swap_is_rejected(plugin, board_fixture):
    with pytest.raises(ValueError, match="orthogonally adjacent"):
        plugin.resolve_swap(board_fixture, (0, 0), (2, 0), revision=1)
```

- [ ] **Step 3: Run and confirm failure**

```powershell
python -m pytest engine/tests/test_match_3_clue_race_runtime.py -q
```

- [ ] **Step 4: Define exact state and move interfaces**

```python
@dataclass(frozen=True)
class Match3MoveResult:
    accepted: bool
    board: tuple[tuple[str, ...], ...]
    board_revision: int
    removed_tile_count: int
    cascade_depth: int
    score_delta: int
    special_activations: int


def resolve_swap(
    self,
    board: tuple[tuple[str, ...], ...],
    source: tuple[int, int],
    destination: tuple[int, int],
    *,
    revision: int,
) -> Match3MoveResult:
    ...
```

Persist participant boards, revisions, scores, invalid counts, combo counts,
maximum chain depth, last accepted move timestamp, and seeded refill cursor in
mechanic state.

- [ ] **Step 5: Add runtime phase and result tests**

```python
async def test_deadline_finalizes_deterministic_leaderboard(runtime):
    run = await start_crime_scene_smash(runtime, player_count=4)
    await advance_clock_past_deadline(runtime)
    result = await runtime.check_timeout(run.run_id)
    assert result.outcome["ranked_character_ids"] == expected_rank_order()
```

- [ ] **Step 6: Run and commit**

```powershell
python -m pytest engine/tests/test_match_3_clue_race_runtime.py engine/tests/test_mini_game_runtime.py -q
git add engine/mini_games/plugins/_match_3_clue_race.py engine/tests/test_match_3_clue_race_runtime.py
git commit -m "feat(nightcap): implement crime scene smash"
```

### Task 4: Build Production Renderers

**Files:**

- Create: `nightcap/mini_games/crime-scene-smash/client/renderer.ts`
- Create: `nightcap/mini_games/crime-scene-smash/client/styles.css`
- Create: `nightcap/mini_games/crime-scene-smash/client/renderer.test.ts`
- Preserve as reference: `nightcap/mini_games/crime-scene-smash/client/index.html`

**Interfaces:**

- Consumes: private board projection, board revision, score, timer, table-safe leaderboard, semantic theme, and result events.
- Produces: phone board input, shared leaderboard and countdown, and host progress/control surfaces.

- [ ] **Step 1: Write failing private-board tests**

```typescript
test("phone submits coordinates and revision without a client score", async () => {
  const ctx = crimeSceneContext();
  renderer.mount(root, ctx);
  await clickTile(root, 2, 3);
  await clickTile(root, 2, 4);
  assert.deepEqual(ctx.lastPayload, {
    action: "swap",
    source: [2, 3],
    destination: [2, 4],
    board_revision: 7,
  });
  assert.equal("score" in ctx.lastPayload, false);
});
```

- [ ] **Step 2: Write failing leaderboard privacy tests**

```typescript
test("shared display shows rank but not private boards", () => {
  renderer.mount(root, crimeSceneSharedContext());
  assert.match(root.textContent ?? "", /Leaderboard/);
  assert.equal(root.querySelector("[data-private-board]"), null);
});
```

- [ ] **Step 3: Implement all surfaces**

Compose kit primitives, keyboard-accessible grid controls, touch targets,
authoritative countdown, pending submission guard, cascade animation, reduced
motion substitution, reconnect remount, final-five spectacle, and winner reveal.

- [ ] **Step 4: Run and commit**

```powershell
npm --prefix nightcap-web test
npm --prefix nightcap-web run typecheck
npm --prefix nightcap-web run bundle:mini-games
git add nightcap/mini_games/crime-scene-smash/client
git commit -m "feat(nightcap): render crime scene smash"
```

### Task 5: Produce the Crime Scene Smash Package-readiness Evidence

**Files:**

- Modify: `nightcap/mini_games/crime-scene-smash/manifest.json`
- Create: `docs/roadmap/operations/crime-scene-smash-device-walkthrough.md`
- Create: `docs/roadmap/operations/crime-scene-smash-rehearsal.md`
- Modify: `docs/specs/0082-crime-scene-smash-game-ready.md`
- Create: `docs/product/mini-game-readiness/crime-scene-smash-0.2.0.json`

**Interfaces:**

- Consumes: automated evidence, 2-player and 8-player load runs, device walkthrough, human rehearsal, and founder sign-off.
- Produces: immutable 0.2.0 playtest candidate and explicit `INTEGRATION_PENDING` evidence.

- [ ] **Step 1: Run automated checks and certification**

```powershell
python -m pytest engine/tests/test_match_3_clue_race_runtime.py engine/tests/test_mini_game_runtime.py -q
npm --prefix nightcap-web test
python docs/skills/arcwright-minigame/scripts/minigame_tool.py certify --package nightcap/mini_games/crime-scene-smash --output docs/product/mini-game-readiness/crime-scene-smash-0.2.0.json
```

- [ ] **Step 2: Run real-device walkthrough**

Verify swap accuracy, input latency, simultaneous play, shared rank legibility,
final-five countdown, reconnect, timeout, 2-player and 8-player layouts, sound,
motion, reduced motion, and no private board leakage.

- [ ] **Step 3: Run real-player rehearsal**

Measure fun, immediate comprehension, fairness, visual payoff, leaderboard
motivation, 90-second pacing, transition back to story, and replay desire.
Blocking findings require a new package version and repeated gates.

- [ ] **Step 4: Obtain package sign-off, keep playtest lifecycle, and commit**

```powershell
python docs/skills/arcwright-minigame/scripts/minigame_tool.py validate nightcap/mini_games/crime-scene-smash
git diff --check
git add nightcap/mini_games/crime-scene-smash/manifest.json docs/specs/0082-crime-scene-smash-game-ready.md docs/roadmap/operations/crime-scene-smash-device-walkthrough.md docs/roadmap/operations/crime-scene-smash-rehearsal.md docs/product/mini-game-readiness/crime-scene-smash-0.2.0.json
git commit -m "test(nightcap): certify crime scene smash"
```

Do not promote to `active` here. The final integration plan owns exact
registration, whole-session evidence, active promotion, and GitHub closure.
