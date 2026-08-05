# The Grill Interrogation Game-ready Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Package the existing Nightcap interrogation, claim, contradiction, and asker-credit systems as a production-ready automatic Beat 3 mini-game named The Grill.

**Architecture:** The package orchestrates existing `engine/interactions` and `engine/claims` services; it does not duplicate suspect answer generation, knowledge checks, claim provenance, contradiction resolution, or Leverage effects. The hosted mechanic owns round order, question windows, public room-watch state, and game result semantics. Existing interaction services remain the authoritative source of questions and answers.

**Tech Stack:** Python 3.11, existing interaction and claim services, pytest, TypeScript, Nightcap mini-game kit, Node test runner, happy-dom, JSON.

## Global Constraints

- Create and approve `docs/specs/0084-the-grill-interrogation-minigame.md` before implementation.
- Beat 3 and the mini-game are separate typed objects that both display the title `The Grill`.
- The Grill starts automatically on Beat 3 entry and runs once in the current session plan.
- Support 2 to 8 players using the existing per-player selection limits.
- Knowledge state queries remain mandatory before every suspect answer.
- Existing interaction claims and contradiction flags remain canonical.
- D-090 catch audiovisual quality, G3 asker credit, and G5 room-watch are hard gates.
- D-090 forbids flat text-only degradation for the contradiction catch. Captions, muted operation, and reduced motion must preserve a designed audiovisual-equivalent squirm.
- Do not implement player-request UI, currency deduction, price, refund, or cross-beat invocation from D-097.
- Human interrogation-flow, device, audiovisual, and player gates are required before activation.

---

### Task 1: Approve the Grill Loop and Presentation Artifact

**Files:**

- Create: `docs/specs/0084-the-grill-interrogation-minigame.md`
- Modify: `docs/design/authoring/couch-race-systems-map.md`
- Read: `docs/specs/0074-aw282-structured-interaction-loop.md`
- Read: `docs/decisions/0016-aw283-claim-ledger-schema.md`

**Interfaces:**

- Consumes: AW-282 interactions, AW-283 claims, D-090, D-091, D-096, and the Couch Race investigation interaction configuration.
- Produces: approved automatic loop, round timing, participant order, result semantics, and three-surface artifact.

- [ ] **Step 1: Execute preflight and baseline**

```powershell
python -m pytest engine/tests/test_interactions.py engine/tests/test_claims.py engine/tests/test_contradictions.py -q
npm --prefix nightcap-web test
```

Use the exact existing test paths found by `rg --files engine/tests | rg "interaction|claim|contradiction"` when names differ.

- [ ] **Step 2: Write the exact proposed loop**

```text
round count: one authored selection window per active player, scaled by existing interaction limit configuration
turn order: stable participant join order, with simultaneous private intent selection inside each window
player action: select suspect, then one currently eligible question intent
resolution: existing interaction service resolves public answer, private tell, claim provenance, and asker identity
catch window: every falsifiable answer opens the existing contradiction flag path
competition: asker credit and confirmed contradiction catches; no new score authority
completion: all authored selection windows resolve or host invokes approved safe completion
fallback: unresolved windows close, existing clue and interrogation paths remain available
```

- [ ] **Step 3: Present the artifact**

Show phone notebook, suspect and intent selection, private tell, shared suspect
stage, public asker credit, room-watch progress, contradiction catch, false flag,
host controls, 2-player and 8-player pacing, reconnect, timeout, audio, motion,
and reduced motion.

- [ ] **Step 4: Stop for founder loop, artifact, and implementation approval**

### Task 2: Create the Package and Hosted Mechanic Wrapper

**Files:**

- Create: `nightcap/mini_games/the-grill-interrogation/manifest.json`
- Create: `nightcap/mini_games/the-grill-interrogation/definitions/0.1.0.json`
- Create: `nightcap/mini_games/the-grill-interrogation/README.md`
- Create: `engine/mini_games/plugins/_the_grill_interrogation.py`
- Modify: `engine/mini_games/plugins/__init__.py`
- Create: `engine/tests/test_the_grill_minigame.py`

**Interfaces:**

- Consumes: `InteractionDefinition`, `InteractionSelection`, public answer events, private feedback events, claim records, and contradiction outcomes.
- Produces: `TheGrillInterrogationPlugin` implementing `StatefulMechanicPlugin` and package capability `interrogation`.

- [ ] **Step 1: Write a failing package test**

```python
def test_the_grill_package_is_hosted_for_two_to_eight_players():
    loaded = load_mini_game_package(Path("nightcap/mini_games/the-grill-interrogation"))
    assert loaded.definition.mechanic_type == "the-grill-interrogation"
    assert (loaded.definition.session_min_players, loaded.definition.session_max_players) == (2, 8)
    assert "interrogation" in loaded.manifest.capability_tags
```

- [ ] **Step 2: Write a failing no-duplication test**

```python
async def test_plugin_delegates_answer_resolution_to_interaction_service(plugin, interaction_spy):
    await plugin.resolve_selection(SELECTION, interaction_service=interaction_spy)
    interaction_spy.resolve.assert_awaited_once_with(SELECTION)
    assert interaction_spy.knowledge_query_count == 1
```

- [ ] **Step 3: Run and confirm failure**

```powershell
python -m pytest engine/tests/test_the_grill_minigame.py -q
```

- [ ] **Step 4: Define exact mechanic state**

```python
class TheGrillState(BaseModel):
    phase: Literal["selection", "answer", "catch_window", "complete"]
    round_index: int = Field(ge=0)
    active_character_ids: list[UUID]
    resolved_selection_ids: list[str] = Field(default_factory=list)
    current_group_id: str | None = None
    current_asker_participant_id: UUID | None = None
    catch_window_deadline: datetime | None = None
```

The plugin invokes existing services and stores only orchestration references.
It must not copy answer text into private surfaces, infer contradictions, or
write knowledge directly.

- [ ] **Step 5: Author and validate package 0.1.0**

Declare automatic hosted execution, 2 to 8 session range, existing interaction
ID `investigation`, safe fallback, generic result semantics, renderer path, and
definition digest. Set lifecycle to `playtest`.

- [ ] **Step 6: Run and commit**

```powershell
python -m pytest engine/tests/test_the_grill_minigame.py -q
python docs/skills/arcwright-minigame/scripts/minigame_tool.py validate nightcap/mini_games/the-grill-interrogation
git add nightcap/mini_games/the-grill-interrogation engine/mini_games/plugins/_the_grill_interrogation.py engine/mini_games/plugins/__init__.py engine/tests/test_the_grill_minigame.py
git commit -m "feat(nightcap): package the grill interrogation"
```

### Task 3: Connect Automatic Beat 3 Invocation and Existing Events

**Files:**

- Modify: `engine/mini_games/plugins/_the_grill_interrogation.py`
- Modify: `engine/interactions/events.py`
- Modify: `engine/interactions/models.py`
- Test: `engine/tests/test_the_grill_minigame.py`
- Test: existing interaction event tests

**Interfaces:**

- Consumes: Beat 3 opportunity, interaction selection limits, `build_public_answer_event`, private tell event, and contradiction events.
- Produces: exactly-once automatic invocation, public asker credit, room-watch projection, and deterministic completion.

- [ ] **Step 1: Write a failing automatic invocation test**

```python
async def test_grill_beat_starts_one_automatic_invocation(harness):
    await harness.enter_beat("grill")
    first = await harness.active_runs(game_id="the-grill-interrogation")
    await harness.retry_beat_entry("grill")
    second = await harness.active_runs(game_id="the-grill-interrogation")
    assert len(first) == 1
    assert [run.run_id for run in second] == [first[0].run_id]
```

- [ ] **Step 2: Write failing asker-credit and room-watch tests**

```python
def test_public_answer_names_session_scoped_asker(public_answer_event):
    assert public_answer_event.payload["asker_participant_id"] == str(ASKER_ID)


def test_room_watch_exposes_progress_not_private_tell(projected_state):
    assert projected_state["resolved_question_count"] == 2
    assert "private_tell" not in projected_state
```

- [ ] **Step 3: Run and confirm failure**

```powershell
python -m pytest engine/tests/test_the_grill_minigame.py -q
```

- [ ] **Step 4: Add the narrow event and orchestration fields**

Carry `asker_participant_id` from `InteractionSelection` to the existing public
answer event. Project suspect, public question intent, asker display identity,
resolved count, remaining windows, catch-window state, and deadline. Private
tells stay on their existing specific-player event.

- [ ] **Step 5: Verify no deferred request path exists**

```powershell
rg -n "player_request|request_cost|currency_deduction|refund" engine/mini_games/plugins/_the_grill_interrogation.py nightcap/mini_games/the-grill-interrogation
```

Expected: no matches.

- [ ] **Step 6: Run and commit**

```powershell
python -m pytest engine/tests/test_the_grill_minigame.py engine/tests -q -k "interaction or claim or contradiction"
git add engine/mini_games/plugins/_the_grill_interrogation.py engine/interactions/events.py engine/interactions/models.py engine/tests
git commit -m "feat(nightcap): orchestrate the grill interrogation"
```

### Task 4: Build Phone Notebook and Shared Suspect Stage

**Files:**

- Create: `nightcap/mini_games/the-grill-interrogation/client/renderer.ts`
- Create: `nightcap/mini_games/the-grill-interrogation/client/styles.css`
- Create: `nightcap/mini_games/the-grill-interrogation/client/renderer.test.ts`

**Interfaces:**

- Consumes: local intent menu, public suspect and answer state, private tell event, asker credit, catch event, room-watch state, semantic theme, and deadline.
- Produces: phone, shared-display, and host renderer surfaces.

- [ ] **Step 1: Write failing phone privacy tests**

```typescript
test("phone shows local tell without exposing it publicly", () => {
  renderer.mount(phoneRoot, phoneContextWithTell());
  renderer.mount(sharedRoot, sharedContext());
  assert.match(phoneRoot.textContent ?? "", /nervous detail/);
  assert.doesNotMatch(sharedRoot.textContent ?? "", /nervous detail/);
});
```

- [ ] **Step 2: Write failing catch spectacle tests**

```typescript
test("confirmed catch credits the asker and stages the suspect reaction", () => {
  const lifecycle = renderer.mount(sharedRoot, sharedContext());
  lifecycle.handleEvent(confirmedCatchEvent({ askerName: "Detective Wren" }));
  assert.match(sharedRoot.textContent ?? "", /Detective Wren/);
  assert.equal(sharedRoot.dataset.sequence, "contradiction-catch");
});
```

- [ ] **Step 3: Implement three surfaces**

Build phone suspect and intent selection, private notebook and tell, catch
control, shared suspect portrait/answer/asker stage, D-090 audiovisual catch,
room-watch progress, host controls, timeout, reconnect, accessibility, sound
controls, captions, and reduced motion. The catch may not fall back to plain
text. Captions retain audio meaning; reduced motion uses a deliberate static or
low-motion reaction plus timed audio/caption cues; muted mode retains the
designed visual reaction. If the equivalent cannot render, use an authored
audiovisual-safe pause/recovery and leave the D-090 gate failed.

- [ ] **Step 4: Run and commit**

```powershell
npm --prefix nightcap-web test
npm --prefix nightcap-web run typecheck
npm --prefix nightcap-web run bundle:mini-games
git add nightcap/mini_games/the-grill-interrogation/client
git commit -m "feat(nightcap): stage the grill interrogation"
```

### Task 5: Produce The Grill Package-readiness Evidence

**Files:**

- Modify: `nightcap/mini_games/the-grill-interrogation/manifest.json`
- Create: `docs/roadmap/operations/the-grill-device-walkthrough.md`
- Create: `docs/roadmap/operations/the-grill-rehearsal.md`
- Modify: `docs/specs/0084-the-grill-interrogation-minigame.md`
- Create: `docs/product/mini-game-readiness/the-grill-interrogation-0.1.0.json`

**Interfaces:**

- Consumes: automated integration evidence, real-device interrogation flow, real-player rehearsal, D-090 evidence, and founder sign-off.
- Produces: immutable 0.1.0 playtest candidate and explicit `INTEGRATION_PENDING` evidence.

- [ ] **Step 1: Run automated certification**

```powershell
python -m pytest engine/tests/test_the_grill_minigame.py -q
npm --prefix nightcap-web test
python docs/skills/arcwright-minigame/scripts/minigame_tool.py certify --package nightcap/mini_games/the-grill-interrogation --output docs/product/mini-game-readiness/the-grill-interrogation-0.1.0.json
```

- [ ] **Step 2: Run real-device walkthrough**

Verify automatic start, phone notebook, suspect choice, public asker credit,
private tell, shared answer, catch, false flag, room-watch, host operations,
reconnect, timeout, 2-player and 8-player pacing, D-090 sound/motion, reduced
motion, captions, muted visual reaction, no text-only degradation, and privacy.

- [ ] **Step 3: Run real-player rehearsal**

Measure question clarity, shared attention, competition, clue value, turn pace,
catch satisfaction, fairness, story enhancement, confusion, and replay desire.
Blocking findings require a new version and repeated gates.

- [ ] **Step 4: Obtain package sign-off, keep playtest lifecycle, and commit**

```powershell
python docs/skills/arcwright-minigame/scripts/minigame_tool.py validate nightcap/mini_games/the-grill-interrogation
git diff --check
git add nightcap/mini_games/the-grill-interrogation/manifest.json docs/specs/0084-the-grill-interrogation-minigame.md docs/roadmap/operations/the-grill-device-walkthrough.md docs/roadmap/operations/the-grill-rehearsal.md docs/product/mini-game-readiness/the-grill-interrogation-0.1.0.json
git commit -m "test(nightcap): certify the grill interrogation"
```

Do not promote to `active` here. The final integration plan owns exact
registration, whole-session evidence, active promotion, and GitHub closure.
