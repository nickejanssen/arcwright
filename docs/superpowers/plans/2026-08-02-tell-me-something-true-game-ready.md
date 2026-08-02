# Tell Me Something True Game-ready Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Promote Tell Me Something True from an unbound hybrid package with a working mechanic into a production-ready social-opener game for 2 to 8 players.

**Architecture:** Preserve `SocialTruthBluffPlugin` as the deterministic phase, vote, reveal, and scoring authority. Move TMST-specific API projections behind the hosted adapter, preserve generic runtime state across reconnects, and add package-local phone, shared-display, and host renderers. The package emits social competition and bounded Leverage semantics but never gates a required clue.

**Tech Stack:** Python 3.11, Pydantic, pytest, TypeScript, Nightcap mini-game kit, Node test runner, happy-dom, JSON.

## Global Constraints

- Create and approve `docs/specs/0081-tell-me-something-true-game-ready.md` before code changes.
- Keep the four phases `input`, `spotlight`, `reveal`, and `scoreboard`.
- Support 2 to 8 active players: one eligible voter per spotlight at 2 players and two eligible voters at 3 players.
- Preserve deterministic spotlight order, 45-second input window, 15-second vote window, AFK truth fallback, disconnected-player skip, and no self-vote.
- Use exact package version `0.2.0`; do not mutate `0.1.0`.
- No required clue is gated by this game.
- Do not add TMST branches to FastAPI or the public SDK.
- Human creative, device, and player gates are required before `active` promotion.

---

### Task 1: Approve the Game-ready Spec and Artifact

**Files:**

- Create: `docs/specs/0081-tell-me-something-true-game-ready.md`
- Modify: `docs/roadmap/tasks/AW-262-tmst-package-authoring-and-schema-resolution.md`
- Modify: `docs/roadmap/tasks/AW-263-tmst-runtime-social-truth-bluff-mechanic.md`
- Modify: `docs/roadmap/tasks/AW-264-tmst-api-events-and-sdk.md`
- Modify: `docs/roadmap/tasks/AW-265-tmst-web-rendering-four-phases.md`

**Interfaces:**

- Consumes: spec 0061, existing package 0.1.0, D-063, D-079, and generic adapter contracts.
- Produces: approved 0.2.0 rules, exact low-player behavior, consequence vocabulary, surface wireframes, and acceptance criteria.

- [ ] **Step 1: Execute mainline preflight and current tests**

```powershell
python -m pytest engine/tests/test_social_truth_bluff_runtime.py api/tests/test_mini_games_api.py -q
npm --prefix nightcap-web test
```

- [ ] **Step 2: Write the exact 0.2.0 contract**

```text
2 players: each spotlight has one eligible voter
3 players: each spotlight has two eligible voters
4-8 players: existing all-other-connected-players voter rule
score: correct vote +1; successful lie fools voter +1 to spotlighted player
tie order: score descending, correct votes descending, stable spotlight order
fallback: flavor-only completion, no required clue
result semantics: winner-count, participation-rate, all-truth-round, all-lie-round
```

- [ ] **Step 3: Present a fixture preview for approval**

Show phone input, phone vote, shared spotlight, shared reveal, scoreboard, host
progress, 2-player state, disconnected state, timeout, and reduced motion.

- [ ] **Step 4: Stop for founder artifact and implementation approval**

No package, plugin, API, or renderer change before approval.

### Task 2: Version and Validate the Package

**Files:**

- Modify: `nightcap/mini_games/tell-me-something-true/manifest.json`
- Create: `nightcap/mini_games/tell-me-something-true/definitions/0.2.0.json`
- Create: `nightcap/mini_games/tell-me-something-true/README.md`
- Test: `engine/tests/test_mini_game_models.py`

**Interfaces:**

- Consumes: approved spec 0081 and package 0.1.0.
- Produces: immutable playtest package 0.2.0 with `social-opener` capability and exact digest.

- [ ] **Step 1: Write a failing package test**

```python
def test_tmst_020_supports_two_to_eight_players():
    loaded = load_mini_game_package(Path("nightcap/mini_games/tell-me-something-true"))
    assert loaded.definition.version == "0.2.0"
    assert loaded.definition.min_players == 2
    assert loaded.definition.max_players == 8
    assert "social-opener" in loaded.manifest.capability_tags
```

- [ ] **Step 2: Run and confirm failure**

```powershell
python -m pytest engine/tests/test_mini_game_models.py -q
```

- [ ] **Step 3: Author 0.2.0 and update the manifest**

Copy 0.1.0, apply the approved low-player and semantic contract, add hosted
adapter and story-role declarations, calculate the definition SHA-256, and set
lifecycle to `playtest`.

- [ ] **Step 4: Validate and commit**

```powershell
python docs/skills/arcwright-minigame/scripts/minigame_tool.py validate nightcap/mini_games/tell-me-something-true
python -m pytest engine/tests/test_mini_game_models.py -q
git add nightcap/mini_games/tell-me-something-true engine/tests/test_mini_game_models.py
git commit -m "feat(nightcap): version tell me something true"
```

### Task 3: Make the Hosted Mechanic Adapter-neutral and Reconnect-safe

**Files:**

- Modify: `engine/mini_games/plugins/_social_truth_bluff.py`
- Test: `engine/tests/test_social_truth_bluff_runtime.py`
- Modify: `api/routers/mini_games.py`
- Test: `api/tests/test_mini_games_api.py`
- Modify: `sdk/src/types.ts`
- Modify: `nightcap-web/src/mini-games/client.ts`
- Test: `nightcap-web/tests/mini-game-client.test.ts`

**Interfaces:**

- Consumes: generic `runtime_state`, generic submission payload, and existing stateful mechanic protocol.
- Produces: plugin-owned `project_state(...) -> dict[str, Any]` and no TMST type in public API/SDK transport.

- [ ] **Step 1: Add failing 2-player and reconnect tests**

```python
async def test_two_player_round_reaches_scoreboard(runtime):
    run = await start_tmst(runtime, participant_count=2)
    await submit_all_inputs(runtime, run)
    await submit_single_votes(runtime, run)
    assert (await runtime.get_run(run.run_id)).status == "completed"


async def test_projected_state_survives_reconnect(runtime):
    state = await fetch_projected_state(runtime, phase="spotlight")
    assert state["phase"] == "spotlight"
    assert state["eligible_voter_ids"]
```

- [ ] **Step 2: Run and confirm failure**

```powershell
python -m pytest engine/tests/test_social_truth_bluff_runtime.py api/tests/test_mini_games_api.py -q
```

- [ ] **Step 3: Add plugin projection**

```python
def project_state(
    self,
    *,
    state: dict[str, Any],
    character_id: UUID,
    participant_id: UUID,
) -> dict[str, Any]:
    ...
```

Return only the local prompt-ready flag, local submission state, current public
spotlight, eligible voters, local vote eligibility, deadline, and public phase.
Remove `_tmst_*` helpers and TMST Pydantic response unions from the route and
public SDK.

- [ ] **Step 4: Map generic browser state without dropping runtime state**

Set `MiniGameState.runtimeState` directly from `runtime_state`; preserve it on
refresh and reconnect.

- [ ] **Step 5: Run and commit**

```powershell
python -m pytest engine/tests/test_social_truth_bluff_runtime.py api/tests/test_mini_games_api.py -q
npm --prefix sdk run typecheck
npm --prefix nightcap-web test
git add engine/mini_games/plugins/_social_truth_bluff.py engine/tests/test_social_truth_bluff_runtime.py api/routers/mini_games.py api/tests/test_mini_games_api.py sdk/src/types.ts nightcap-web/src/mini-games/client.ts nightcap-web/tests/mini-game-client.test.ts
git commit -m "refactor(nightcap): isolate social truth bluff state"
```

### Task 4: Build Package-local Renderers

**Files:**

- Create: `nightcap/mini_games/tell-me-something-true/client/renderer.ts`
- Create: `nightcap/mini_games/tell-me-something-true/client/styles.css`
- Create: `nightcap/mini_games/tell-me-something-true/client/renderer.test.ts`

**Interfaces:**

- Consumes: `MiniGameContext`, generic `runtimeState`, semantic theme, and TMST public events.
- Produces: phone, shared-display, and host `SurfaceHandler` implementations.

- [ ] **Step 1: Write failing phone privacy and vote tests**

```typescript
test("phone renders only local prompt and eligible vote", async () => {
  const ctx = tmstContext({ phase: "spotlight", can_vote: true });
  const lifecycle = renderer.mount(root, ctx);
  assert.match(root.textContent ?? "", /Truth|Lie/);
  assert.doesNotMatch(root.textContent ?? "", /other-player-private-statement/);
  lifecycle.unmount();
});
```

- [ ] **Step 2: Write failing shared-display and host tests**

```typescript
test("shared display stages spotlight without private inputs", () => {
  renderer.mount(root, tmstSharedContext());
  assert.match(root.textContent ?? "", /Spotlight/);
  assert.doesNotMatch(root.textContent ?? "", /private prompt/);
});
```

- [ ] **Step 3: Run and confirm failure**

```powershell
npm --prefix nightcap-web test
```

- [ ] **Step 4: Implement all three surfaces**

Use `defineRenderer`, `createSubmissionGuard`, `useCountdown`, DOM helpers,
semantic tokens, reduced motion, 44-pixel targets, ARIA live regions, and
package-scoped styles. Render input, spotlight, reveal, scoreboard, timeout,
disconnect, and completed states.

- [ ] **Step 5: Run and commit**

```powershell
npm --prefix nightcap-web test
npm --prefix nightcap-web run typecheck
npm --prefix nightcap-web run bundle:mini-games
git add nightcap/mini_games/tell-me-something-true/client
git commit -m "feat(nightcap): render tell me something true"
```

### Task 5: Produce the Tell Me Something True Package-readiness Evidence

**Files:**

- Modify: `nightcap/mini_games/tell-me-something-true/manifest.json`
- Create: `docs/roadmap/operations/tmst-device-walkthrough.md`
- Create: `docs/roadmap/operations/tmst-rehearsal.md`
- Modify: `docs/specs/0081-tell-me-something-true-game-ready.md`
- Create: `docs/product/mini-game-readiness/tell-me-something-true-0.2.0.json`

**Interfaces:**

- Consumes: automated tests, preview, real-device walkthrough, real-player rehearsal, and founder sign-off.
- Produces: immutable playtest candidate and explicit `INTEGRATION_PENDING` evidence for final Nightcap registration.

- [ ] **Step 1: Run automated certification**

```powershell
python docs/skills/arcwright-minigame/scripts/minigame_tool.py certify --package nightcap/mini_games/tell-me-something-true --output docs/product/mini-game-readiness/tell-me-something-true-0.2.0.json
python -m json.tool docs/product/mini-game-readiness/tell-me-something-true-0.2.0.json
```

Expected before human evidence: `overall_status` is `BLOCKED`, registration,
opportunity, and integrated-session gates are `INTEGRATION_PENDING`, and human
gates are `NOT_RUN`.

- [ ] **Step 2: Run real-device walkthrough**

Verify phone input, vote, reconnect, shared spotlight/reveal/scoreboard, host
progress, 2-player behavior, 8-player legibility, disconnect, timeout, audio,
motion, reduced motion, and no private leakage. Record devices and results.

- [ ] **Step 3: Run real-player rehearsal**

Measure duration, dead air, bluff clarity, vote tension, social comfort,
spectacle, competition, story transition, and desire to replay. Remediate every
blocking finding through a new patch version and repeat affected gates.

- [ ] **Step 4: Obtain founder package sign-off**

Keep lifecycle at `playtest`. The final integration plan owns exact
registration, whole-session evidence, active promotion, and GitHub closure.

- [ ] **Step 5: Verify and commit**

```powershell
python -m pytest engine/tests/test_social_truth_bluff_runtime.py api/tests/test_mini_games_api.py -q
npm --prefix nightcap-web test
python docs/skills/arcwright-minigame/scripts/minigame_tool.py validate nightcap/mini_games/tell-me-something-true
git diff --check
git add nightcap/mini_games/tell-me-something-true/manifest.json docs/specs/0081-tell-me-something-true-game-ready.md docs/roadmap/operations/tmst-device-walkthrough.md docs/roadmap/operations/tmst-rehearsal.md docs/product/mini-game-readiness/tell-me-something-true-0.2.0.json
git commit -m "test(nightcap): certify tell me something true"
```
