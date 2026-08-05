# Nightcap Mini-game Opportunity Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Register Nightcap's initial mini-game set, author one rotating candidate pool per Couch Race beat, and connect opportunities to production phone, shared-display, host, consequence, theme, and lifecycle paths.

**Architecture:** Nightcap owns package registrations, candidate pools, consequence profiles, presentation configuration, and renderer implementations. Arcwright selects deterministically from each authored pool and applies canonical consequences without knowing Couch Race beat names, Leverage vocabulary, or Nightcap surfaces. Last Call uses a `pressure_capstone` opportunity before final guesses lock; The Truth uses a `reveal_reconstruction` opportunity whose first game implements D-086's Unmasking.

**Tech Stack:** JSON arc definitions, Python 3.11, Pydantic, pytest, TypeScript, Nightcap web, Node test runner, semantic design tokens.

## Global Constraints

- Required completed dependencies: contract checkpoint and onboarding checkpoint.
- Required approved placements: Pour social opener, Scene competitive discovery, Grill interrogation, Twist solo recontextualization, Last Call pressure capstone, Truth reveal reconstruction.
- Initial packages: Tell Me Something True, Crime Scene Smash, The Grill, Evidence Locker 402, Interrogation Room, and The Unmasking.
- Each opportunity is a candidate pool. Adding a certified alternative must not require engine code.
- Selection uses `session_seeded_rotation`; current-session repeat avoidance is required.
- Cross-session history is optional input and must not make Nightcap Continuity a v1 dependency.
- Last Call ends with final guesses locked. The Truth reads locked guesses but never changes them.
- The Unmasking presents canonical resolved truth; AI may compose approved narration only after truth and sequence order are resolved.
- Mini-game loss, timeout, or absence never makes the mystery unsolvable.
- Do not implement the D-097 optional currency-funded Grill request.
- Keep Nightcap theme and surface names out of generic engine modules.

---

## File Responsibility Map

| File | Responsibility |
| --- | --- |
| `nightcap/couch-race.arc.json` | Registrations, six opportunity pools, rotation, consequences, and Nightcap presentation configuration |
| `engine/tests/test_couch_race_arc_json.py` | Static arc and placement contract |
| `engine/tests/test_couch_race_harness.py` | Deterministic six-opportunity session proof |
| `nightcap-web/src/mini-games/stage.ts` | Production stage bootstrap attributes |
| `nightcap-web/src/mini-games/browser-entry.ts` | Stage discovery and boot |
| `nightcap-web/src/design/themes/midnight.ts` | Nightcap-owned opaque mini-game theme payload |
| `nightcap-web/tests/mini-game-privacy-matrix.test.ts` | Phone, shared-display, and host privacy boundaries |

### Task 1: Preflight and Canonical Flow Reconciliation

**Files:**

- Modify: `docs/story-bibles/nightcap-couch-race.md`
- Modify: `docs/design/authoring/couch-race-systems-map.md`
- Modify: `docs/design/authoring/couch-race-session-experience.md`
- Modify: `docs/specs/0072-nightcap-couch-race-v1.md`
- Modify: `docs/product/decisions-log.csv`
- Test: `engine/tests/test_couch_race_documentation.py`

**Interfaces:**

- Consumes: D-086, D-093, D-094, D-095, ADR 0018, and founder direction recorded during plan creation.
- Produces: D-098 plus one canonical beat flow shared by story bible, systems map, parent spec, and arc implementation.

- [ ] **Step 1: Execute the master-plan safety gate and baseline**

```powershell
python -m pytest engine/tests/test_couch_race_arc_json.py engine/tests/test_couch_race_harness.py -q
npm --prefix nightcap-web test
```

Expected: record the current two-binding baseline and renderer limitations.

- [ ] **Step 2: Write a failing canonical-flow test**

```python
from pathlib import Path


def test_canonical_docs_name_last_call_and_truth_game_roles():
    bible = Path("docs/story-bibles/nightcap-couch-race.md").read_text()
    systems = Path("docs/design/authoring/couch-race-systems-map.md").read_text()
    assert "pressure_capstone" in bible
    assert "reveal_reconstruction" in bible
    assert "rotating candidate pool" in systems
```

- [ ] **Step 3: Run and confirm failure**

```powershell
python -m pytest engine/tests/test_couch_race_documentation.py -q
```

Expected: role text is absent.

- [ ] **Step 4: Record D-098 exactly**

Add one CSV row with this decision:

```text
D-098 Couch Race mini-game opportunities use rotating certified candidate pools. The initial Last Call role is pressure_capstone and ends with final guesses locked. The Truth role is reveal_reconstruction; its initial implementation follows D-086's Unmasking and leads into score animation, rankings, and the winners podium. Arcwright selects deterministically from human-authored eligible pools and never changes canonical case truth or guess outcomes.
```

- [ ] **Step 5: Reconcile canonical beat flow**

Use this exact sequence:

```text
Pour: social_opener
Scene: competitive_discovery
Grill: interrogation
Twist: solo_recontextualization
Last Call: pressure_capstone -> final interrogation/Leverage window -> final guess lock
Truth: reveal_reconstruction -> canonical reveal -> score animation -> rankings -> podium -> replay prompt
```

- [ ] **Step 6: Run and commit documentation**

```powershell
python -m pytest engine/tests/test_couch_race_documentation.py -q
git diff --check
git add docs/story-bibles/nightcap-couch-race.md docs/design/authoring/couch-race-systems-map.md docs/design/authoring/couch-race-session-experience.md docs/specs/0072-nightcap-couch-race-v1.md docs/product/decisions-log.csv engine/tests/test_couch_race_documentation.py
git commit -m "docs(nightcap): lock rotating minigame beat roles"
```

- [ ] **Step 7: Stop for explicit founder implementation approval**

No arc, web, or engine integration begins before approval of the reconciled
canonical flow.

### Task 2: Author Six Registrations and Rotating Opportunity Pools

**Files:**

- Modify: `nightcap/couch-race.arc.json`
- Test: `engine/tests/test_couch_race_arc_json.py`
- Test: `engine/tests/test_aw256_beat_hardcode.py`

**Interfaces:**

- Consumes: exact active or playtest package versions and digests from each game-ready plan.
- Produces: six `MiniGameRegistration` records, six `MiniGameConsequenceProfile` records, and six `MiniGameOpportunity` pools.

- [ ] **Step 1: Write failing six-pool tests**

```python
def test_couch_race_has_one_rotating_pool_per_beat(couch_race_arc):
    opportunities = {
        beat.beat_id: beat.mini_game_opportunities
        for beat in couch_race_arc.beats
    }
    assert set(opportunities) == {"pour", "scene", "grill", "twist", "last_call", "truth"}
    assert all(len(pool) == 1 for pool in opportunities.values())
    assert all(pool[0].selection_policy == "session_seeded_rotation" for pool in opportunities.values())


def test_initial_story_roles_are_exact(couch_race_arc):
    roles = {
        beat.beat_id: beat.mini_game_opportunities[0].story_role
        for beat in couch_race_arc.beats
    }
    assert roles == {
        "pour": "social_opener",
        "scene": "competitive_discovery",
        "grill": "interrogation",
        "twist": "solo_recontextualization",
        "last_call": "pressure_capstone",
        "truth": "reveal_reconstruction",
    }
```

- [ ] **Step 2: Run and confirm failure**

```powershell
python -m pytest engine/tests/test_couch_race_arc_json.py -q
```

Expected: missing opportunity pools and registrations.

- [ ] **Step 3: Add the exact initial registrations**

Use these IDs and package mappings:

```json
[
  {"registration_id":"couch-race-tmst","game_id":"tell-me-something-true","adapter":"arcwright_hosted"},
  {"registration_id":"couch-race-crime-scene","game_id":"crime-scene-smash","adapter":"arcwright_hosted"},
  {"registration_id":"couch-race-grill","game_id":"the-grill-interrogation","adapter":"arcwright_hosted"},
  {"registration_id":"couch-race-evidence-locker","game_id":"evidence-locker-402","adapter":"arcwright_hosted"},
  {"registration_id":"couch-race-interrogation-room","game_id":"interrogation-room","adapter":"arcwright_hosted"},
  {"registration_id":"couch-race-unmasking","game_id":"the-unmasking","adapter":"arcwright_hosted"}
]
```

Copy each exact version and SHA-256 digest from its validated package. Use the
package's declared capability and story-role tags. Do not use `latest`.

- [ ] **Step 4: Add exact opportunity policy**

Every beat receives one opportunity with:

```json
{
  "trigger_mode": "beat_entry",
  "max_invocations": 1,
  "cooldown_seconds": 0,
  "selection_policy": "session_seeded_rotation",
  "rotation_lookback": 1,
  "fallback": "continue_arc"
}
```

Set `eligible_registration_ids` to the initial registration for that beat.
Future certified alternatives append to this list without changing engine code.
The Grill has no player-request opportunity.

- [ ] **Step 5: Add exact consequence profiles**

Use these profile IDs:

```text
pour-social-results
scene-discovery-results
grill-interrogation-results
twist-recontextualization-results
last-call-pressure-results
truth-reveal-results
```

Minigame performance may grant bounded Leverage, race score, a sharper clue
variant, public celebration, or presentation signals. `truth-reveal-results`
may emit presentation and credit events but cannot change guesses, scores, case
truth, knowledge, or culprit identity.

- [ ] **Step 6: Run and commit**

```powershell
python -m pytest engine/tests/test_couch_race_arc_json.py engine/tests/test_aw256_beat_hardcode.py -q
python -m json.tool nightcap/couch-race.arc.json
git add nightcap/couch-race.arc.json engine/tests/test_couch_race_arc_json.py engine/tests/test_aw256_beat_hardcode.py
git commit -m "feat(nightcap): author six rotating minigame pools"
```

### Task 3: Map Nightcap Consequences Without Engine Vocabulary Leaks

**Files:**

- Modify: `nightcap/couch-race.arc.json`
- Test: `engine/tests/test_resources_integration.py`
- Test: `engine/tests/test_scoring_integration.py`
- Test: `engine/tests/test_couch_race_harness.py`

**Interfaces:**

- Consumes: generic `MiniGameConsequenceProfile` actions and existing Leverage/scoring services.
- Produces: bounded Nightcap-specific rules stored only in the arc.

- [ ] **Step 1: Write failing edge-not-gate tests**

```python
@pytest.mark.parametrize("completion_status", ["completed", "timed_out", "cancelled"])
async def test_every_minigame_outcome_preserves_solvable_case(completion_status, harness):
    session = await harness.run_all_minigames_as(completion_status)
    assert session.all_required_clues_reachable is True
    assert session.final_guess_available is True


async def test_truth_game_cannot_mutate_locked_guesses(harness):
    before = await harness.lock_final_guesses()
    await harness.run_truth_game()
    after = await harness.load_final_guesses()
    assert after == before
```

- [ ] **Step 2: Run and confirm failure**

```powershell
python -m pytest engine/tests/test_resources_integration.py engine/tests/test_scoring_integration.py engine/tests/test_couch_race_harness.py -q
```

- [ ] **Step 3: Author bounded rules**

Set per-profile maximum Leverage and score values within existing bank caps and
AW-284 scoring. Loss and timeout use reduced edge or no reward; no profile
removes required evidence. The Last Call game finishes before final guess lock.
The Truth game reads immutable reveal and credit data and emits no score delta.

- [ ] **Step 4: Run and commit**

```powershell
python -m pytest engine/tests/test_resources_integration.py engine/tests/test_scoring_integration.py engine/tests/test_couch_race_harness.py -q
git add nightcap/couch-race.arc.json engine/tests/test_resources_integration.py engine/tests/test_scoring_integration.py engine/tests/test_couch_race_harness.py
git commit -m "feat(nightcap): map minigame story consequences"
```

### Task 4: Fix Production Stage Bootstrap

**Files:**

- Modify: `nightcap-web/src/mini-games/stage.ts`
- Modify: `nightcap-web/src/mini-games/browser-entry.ts`
- Modify: `nightcap-web/src/mini-games/client.ts`
- Modify: `nightcap-web/src/runtime.ts`
- Test: `nightcap-web/tests/mini-game-stage.test.ts`
- Test: `nightcap-web/tests/mini-game-client.test.ts`
- Test: `nightcap-web/tests/mini-game-client-race.test.ts`

**Interfaces:**

- Consumes: session ID, scoped token, API base URL, exact package version, surface identity, participant identity, status revision, runtime state, and opaque theme.
- Produces: `MiniGameStageBootstrap` serialized as data attributes and consumed by `bootStage`.

- [ ] **Step 1: Write a failing bootstrap test**

```typescript
test("stage carries complete scoped bootstrap", () => {
  const html = renderMiniGameStage("phone", {
    sessionId: "session-1",
    token: "scoped-token",
    apiBaseUrl: "https://api.example.test",
    participantId: "participant-1",
    characterId: "character-1",
  });
  assert.match(html, /data-session-id="session-1"/);
  assert.match(html, /data-api-base-url="https:\/\/api.example.test"/);
});
```

- [ ] **Step 2: Run and confirm failure**

```powershell
npm --prefix nightcap-web test
```

- [ ] **Step 3: Define exact bootstrap type**

```typescript
export interface MiniGameStageBootstrap {
  sessionId: string;
  token: string;
  apiBaseUrl: string;
  participantId: string;
  characterId: string;
}
```

Escape attribute values. Never copy one surface's token or private state to
another surface. Preserve generic `runtimeState` on fetch and reconnect.

- [ ] **Step 4: Run and commit**

```powershell
npm --prefix nightcap-web test
npm --prefix nightcap-web run typecheck
git add nightcap-web/src/mini-games nightcap-web/src/runtime.ts nightcap-web/tests/mini-game-stage.test.ts nightcap-web/tests/mini-game-client.test.ts nightcap-web/tests/mini-game-client-race.test.ts
git commit -m "fix(nightcap): bootstrap minigame stages"
```

### Task 5: Forward the Nightcap Theme Contract

**Files:**

- Modify: `nightcap-web/src/design/tokens.base.ts`
- Modify: `nightcap-web/src/design/themes/midnight.ts`
- Modify: `nightcap-web/src/mini-game-kit/types.ts`
- Modify: `nightcap-web/src/mini-game-kit/define-renderer.ts`
- Test: `nightcap-web/tests/mini-game-define-renderer.test.ts`
- Test: `nightcap-web/tests/mini-game-perf.test.ts`
- Modify: `docs/specs/0069-nightcap-visual-design-system.md`

**Interfaces:**

- Consumes: opaque `presentation.theme` plus surface-neutral posture and accessibility preferences.
- Produces: `MiniGamePresentationContext` interpreted only by Nightcap renderers.

- [ ] **Step 1: Write failing theme tests**

```typescript
test("renderer receives opaque Nightcap theme without rule changes", () => {
  const ctx = contextWithPresentation({
    theme: { colorScheme: "midnight", motionIntensity: "high" },
    posture: "shared_focus",
    reducedMotion: false,
  });
  renderer.mount(root, ctx);
  assert.equal(root.dataset.theme, "midnight");
  assert.equal(ctx.state.statusRevision, 3);
});
```

- [ ] **Step 2: Define exact presentation context**

```typescript
export interface MiniGamePresentationContext {
  theme: Record<string, unknown>;
  posture: "private_focus" | "shared_focus" | "mixed_focus";
  locale: string;
  reducedMotion: boolean;
  urgency: "low" | "medium" | "high";
}
```

- [ ] **Step 3: Implement Nightcap interpretation**

Use spec 0069 tokens, reduced motion, couch-distance typography, phone intimacy,
shared-display staging, and missing-asset fallback. Do not create a second
design system or add Nightcap token interpretation to Python.

- [ ] **Step 4: Run and commit**

```powershell
npm --prefix nightcap-web test
npm --prefix nightcap-web run typecheck
git add nightcap-web/src/design nightcap-web/src/mini-game-kit nightcap-web/tests/mini-game-define-renderer.test.ts nightcap-web/tests/mini-game-perf.test.ts docs/specs/0069-nightcap-visual-design-system.md
git commit -m "feat(nightcap): theme minigame surfaces"
```

### Task 6: Restore Embedded-script Safety Coverage

**Files:**

- Modify: `nightcap-web/tests/ui.test.ts`
- Modify: `nightcap-web/src/ui.ts`
- Modify: GitHub issue `#270` after tests pass

**Interfaces:**

- Consumes: embedded page scripts and privacy markers.
- Produces: isolated-VM execution coverage for every embedded script.

- [ ] **Step 1: Add the reverted safety assertion against current main**

```typescript
test("every embedded page script executes without private marker leakage", async () => {
  for (const script of extractEmbeddedScripts(renderedPages())) {
    const result = executeInIsolatedVm(script);
    assert.equal(result.referenceError, null);
    assert.equal(result.output.includes("private-marker"), false);
  }
});
```

- [ ] **Step 2: Run and confirm current behavior**

```powershell
npm --prefix nightcap-web test
```

Expected: test fails before the safe extraction or runtime fix.

- [ ] **Step 3: Apply the narrow current-main fix and run**

Do not restore unrelated helper deduplication from reverted PR #271.

```powershell
npm --prefix nightcap-web test
npm --prefix nightcap-web run typecheck
```

- [ ] **Step 4: Commit and update issue #270**

```powershell
git add nightcap-web/tests/ui.test.ts nightcap-web/src/ui.ts
git commit -m "test(nightcap): cover embedded page scripts"
```

Update issue #270 with the exact test and commit evidence.

### Task 7: Prove Six Opportunities Before Active Promotion

**Files:**

- Test: `engine/tests/test_couch_race_harness.py`
- Test: `api/tests/test_mini_games_api.py`
- Test: `nightcap-web/tests/mini-game-privacy-matrix.test.ts`
- Test: `nightcap-web/tests/runtime.test.ts`

**Interfaces:**

- Consumes: six candidate pools and the six immutable package versions certified at playtest lifecycle.
- Produces: deterministic opportunity, fallback, privacy, reconnect, rotation, and flow evidence without asserting game readiness.

- [ ] **Step 1: Add a failing six-beat harness case**

```python
async def test_two_and_eight_player_sessions_reach_six_opportunities(harness):
    for player_count in (2, 8):
        session = await harness.run(player_count=player_count)
        assert session.opportunity_roles == [
            "social_opener",
            "competitive_discovery",
            "interrogation",
            "solo_recontextualization",
            "pressure_capstone",
            "reveal_reconstruction",
        ]
        assert session.final_guesses_locked_before_truth is True
```

- [ ] **Step 2: Add a failing rotation test**

```python
async def test_pool_selection_is_replayable_and_avoids_current_session_repeat(harness):
    first = await harness.select_with_seed("session-a", alternatives=True)
    replay = await harness.select_with_seed("session-a", alternatives=True)
    assert replay == first
    assert len(first) == len(set(first))
```

- [ ] **Step 3: Run focused integration checks**

```powershell
python -m pytest engine/tests/test_couch_race_harness.py api/tests/test_mini_games_api.py -q
npm --prefix nightcap-web test
```

Expected: pass after exact playtest package adapters are wired. Keep every
package's registration and integrated-session readiness gates open.

- [ ] **Step 4: Commit foundation evidence**

```powershell
git add engine/tests/test_couch_race_harness.py api/tests/test_mini_games_api.py nightcap-web/tests/mini-game-privacy-matrix.test.ts nightcap-web/tests/runtime.test.ts
git commit -m "test(nightcap): prove six minigame opportunities"
```

### Task 8: Foundation Verification and Reconciliation

**Files:**

- Modify: `docs/roadmap/tasks/AW-285-couch-race-tv-and-phone-rendering.md`
- Modify: `docs/roadmap/tasks/AW-288-couch-race-mini-game-beat-coverage-and-tmst-acceleration.md`
- Modify: `docs/roadmap/epics/M5-I-nightcap-couch-race-arc-and-interrogation.md`
- Modify: `docs/roadmap/index.json`

**Interfaces:**

- Consumes: Tasks 1 through 7 evidence.
- Produces: foundation checkpoint with all individual game-ready gates still open.

- [ ] **Step 1: Run full focused verification**

```powershell
python -m pytest engine/tests/test_couch_race_arc_json.py engine/tests/test_couch_race_harness.py engine/tests/test_resources_integration.py engine/tests/test_scoring_integration.py api/tests/test_mini_games_api.py -q
npm --prefix nightcap-web test
npm --prefix nightcap-web run typecheck
python -m json.tool nightcap/couch-race.arc.json
git diff --check
```

- [ ] **Step 2: Run architecture review**

Use `arcwright-reviewer`; resolve blocking findings and rerun affected checks.

- [ ] **Step 3: Reconcile only foundation evidence**

Record six valid pools, deterministic rotation, generic consequences, stage
bootstrap, theme, and privacy. Do not mark any package game-ready.

- [ ] **Step 4: Stop for founder checkpoint approval**

The whole-session certification and closeout plan is next after approval.
