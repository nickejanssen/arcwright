# The Unmasking Reveal-reconstruction Game-ready Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver The Unmasking as The Truth's production-ready reveal-reconstruction mini-game, turning locked accusations and deterministic case truth into an escalating suspect-clear sequence, culprit reveal, credited reconstruction, and score-podium handoff.

**Architecture:** Python resolves the complete reveal script data before presentation: locked guesses, canonical killer, innocent-clear order, secrets, lies, established evidence, contradiction catches, player credits, solved or house-win state, and final score snapshot. AI may compose approved Vesper wording only from that resolved projection. Clients stage the sequence but cannot reorder suspects, alter truth, credit, scores, ranks, or winners.

**Tech Stack:** Python 3.11, Pydantic, existing accusation, claims, scoring, knowledge, routing, and safety services, pytest, JSON package contracts, TypeScript, Nightcap renderer kit, Node test runner, happy-dom.

## Global Constraints

- Create and approve `docs/specs/0085-the-unmasking-reveal-reconstruction.md` before package work.
- Implement D-086's Unmasking as the first certified `reveal_reconstruction` game; future certified alternatives may rotate into the same authored role.
- Start only after Last Call guesses are locked and immutable.
- Support 2 to 8 session players and the configured case cast.
- Resolve case truth, solved status, credits, scores, ranks, and podium before any narrative generation or rendering.
- Preserve the locked Vesper three-movement structure: grave reconstruction, delight at the killer's best move, ordinary last line.
- If nobody solves the case, the case wins; the reveal still completes.
- Do not expose private guesses before the authored reveal point or leak hidden knowledge into generation.
- Founder approval of sequence, copy, audiovisual artifact, pacing, and real-player reveal is mandatory.

---

### Task 1: Author and Approve the Reveal-reconstruction Contract

**Files:**

- Create: `docs/specs/0085-the-unmasking-reveal-reconstruction.md`
- Modify: `docs/design/line-libraries/truth-sequence-shapes.md`
- Modify: `docs/roadmap/tasks/AW-278-couch-race-truth-sequence-and-reveal-accounting.md`
- Read: `docs/story-bibles/nightcap-couch-race.md`
- Read: `docs/product/decisions-log.csv`

**Interfaces:**

- Consumes: D-086, D-093, locked accusations, resolved case truth, established claims, contradiction credit, AW-284 score snapshot, Vesper voice rules, and Truth's 3 to 5 minute budget.
- Produces: approved sequence schema, ordering rules, credit policy, solved and house-win variants, podium handoff, copy envelope, and three-surface artifact.

- [ ] **Step 1: Run the accusation, claims, and scoring baseline**

```powershell
python -m pytest engine/tests/test_claims_integration.py engine/tests/test_claims_resolver.py engine/tests/test_scoring_resolver.py engine/tests/test_scoring_integration.py -q
npm --prefix nightcap-web test
```

- [ ] **Step 2: Lock the exact initial sequence**

```text
precondition: all eligible final guesses are locked
movement 1: clear each innocent portrait one at a time
per innocent: name the secret, explain the lie, relight the portrait, and credit the player whose established catch earned credit
culprit turn: leave the culprit portrait, re-ring it, and name the killer
movement 2: reconstruct motive, method, timeline, genuine clues, lies, red herrings, near-misses, and the killer's best move
outcome: solved table or house win
handoff: animate final scores, ranks, winner podium, superlatives, and replay prompt
movement 3: Vesper delivers one approved ordinary last line
```

- [ ] **Step 3: Specify deterministic ordering**

Order innocent clears by the authored case reveal order. When absent, sort by
stable cast order, never by a model. Credit each established contradiction to
the first canonical catcher; display additional credited players in stable
submission order. Score ties use AW-284's canonical tiebreakers.

- [ ] **Step 4: Present solved and house-win artifacts**

Show 2-player and 8-player versions, short and long casts, inline credit,
uncaught lies, no-credit clears, culprit ring, reconstruction, score animation,
ties, podium, superlatives, sound, motion, reduced motion, reconnect, and host
recovery.

- [ ] **Step 5: Stop for founder sequence, copy, audiovisual, and implementation approval**

### Task 2: Build the Immutable Reveal Projection

**Files:**

- Create: `engine/mini_games/reveal.py`
- Create: `engine/tests/test_mini_game_reveal.py`
- Read: `engine/scoring/resolver.py`
- Read: `engine/scoring/superlatives.py`
- Read: `engine/claims/`

**Interfaces:**

- Consumes: resolved case snapshot, locked accusation records, claim and contradiction records, participant identities, authoritative score snapshot, and authored cast order.
- Produces: `RevealReconstructionProjection` with no raw private knowledge or mutable session references.

- [ ] **Step 1: Write a failing projection test**

```python
def test_projection_clears_innocents_then_leaves_culprit(resolver):
    projection = resolver.resolve(REVEAL_INPUT)
    assert [item.character_id for item in projection.innocent_clears] == [SUSPECT_A, SUSPECT_C]
    assert projection.culprit.character_id == SUSPECT_B
    assert projection.guesses_locked is True
```

- [ ] **Step 2: Write failing truth and privacy tests**

```python
def test_projection_uses_canonical_case_truth_not_majority_guess(resolver):
    projection = resolver.resolve(REVEAL_INPUT_WITH_WRONG_MAJORITY)
    assert projection.culprit.character_id == CANONICAL_KILLER_ID


def test_projection_excludes_raw_private_knowledge(resolver):
    payload = resolver.resolve(REVEAL_INPUT).model_dump()
    assert "knowledge_graph" not in payload
    assert "private_evidence" not in payload
```

- [ ] **Step 3: Run and confirm failure**

```powershell
python -m pytest engine/tests/test_mini_game_reveal.py -q
```

- [ ] **Step 4: Implement exact immutable models**

```python
class InnocentClear(BaseModel):
    character_id: UUID
    display_name: str
    secret_summary: str
    lie_explanation: str
    credited_participant_ids: tuple[UUID, ...]
    evidence_refs: tuple[str, ...]


class RevealReconstructionProjection(BaseModel):
    guesses_locked: Literal[True]
    solved: bool
    innocent_clears: tuple[InnocentClear, ...]
    culprit: CulpritReveal
    reconstruction: Reconstruction
    standings: tuple[FinalStanding, ...]
    superlatives: tuple[SuperlativeAward, ...]
    source_revision: int = Field(ge=0)
```

Use frozen Pydantic models. Reject unlocked guesses, missing canonical truth,
unestablished evidence, duplicate ranks, and a culprit included among innocent
clears.

- [ ] **Step 5: Run and commit**

```powershell
python -m pytest engine/tests/test_mini_game_reveal.py -q
git add engine/mini_games/reveal.py engine/tests/test_mini_game_reveal.py
git commit -m "feat(nightcap): resolve truth reveal projection"
```

### Task 3: Scaffold The Unmasking Package and Hosted Mechanic

**Files:**

- Create: `nightcap/mini_games/the-unmasking/manifest.json`
- Create: `nightcap/mini_games/the-unmasking/definitions/0.1.0.json`
- Create: `nightcap/mini_games/the-unmasking/README.md`
- Create: `engine/mini_games/plugins/_the_unmasking.py`
- Modify: `engine/mini_games/plugins/__init__.py`
- Create: `engine/tests/test_the_unmasking_minigame.py`

**Interfaces:**

- Consumes: `RevealReconstructionProjection`, narration resolver, provider-agnostic router, knowledge query, safety validator, and `StatefulMechanicPlugin`.
- Produces: `TheUnmaskingState`, validated narration segments, deterministic lifecycle, and result schema version `1.0`.

- [ ] **Step 1: Write failing package and lifecycle tests**

```python
def test_unmasking_declares_reveal_reconstruction_role():
    loaded = load_mini_game_package(Path("nightcap/mini_games/the-unmasking"))
    assert loaded.definition.mechanic_type == "reveal-reconstruction"
    assert (loaded.definition.session_min_players, loaded.definition.session_max_players) == (2, 8)
    assert "reveal-reconstruction" in loaded.manifest.capability_tags


def test_unmasking_refuses_unlocked_projection(plugin):
    with pytest.raises(InvalidTransition, match="guesses must be locked"):
        plugin.start(UNLOCKED_PROJECTION, CONTEXT)
```

- [ ] **Step 2: Write failing generation-boundary tests**

```python
async def test_narration_runs_after_projection_and_cannot_change_truth(plugin, router_spy):
    state = await plugin.start(LOCKED_PROJECTION, CONTEXT)
    assert router_spy.calls[0].task_type == "narrative_generation"
    assert state.projection.culprit.character_id == LOCKED_PROJECTION.culprit.character_id
    assert state.projection.standings == LOCKED_PROJECTION.standings
```

- [ ] **Step 3: Run and confirm failure**

```powershell
python -m pytest engine/tests/test_the_unmasking_minigame.py -q
```

- [ ] **Step 4: Implement exact lifecycle state**

```python
class TheUnmaskingState(BaseModel):
    phase: Literal["clearing", "culprit", "reconstruction", "podium", "complete"]
    projection: RevealReconstructionProjection
    clear_index: int = Field(ge=0)
    narration: ResolvedRevealNarration
    acknowledged_cues: set[str] = Field(default_factory=set)
    revision: int = Field(ge=0)
```

Resolve narration once per immutable projection and cache it by projection
digest. On generation timeout or validation failure, use the authored D-086
safe copy. The plugin advances only through server-owned cue acknowledgments
and remains replayable after reconnect.

- [ ] **Step 5: Author package `0.1.0` as `playtest`**

Declare hosted execution, 2 to 8 session players, reveal-reconstruction role,
3 to 5 minute budget, presentation cues, renderer entrypoint, authored
fallback, result schema, generation budget, and definition digest.

- [ ] **Step 6: Run and commit**

```powershell
python -m pytest engine/tests/test_mini_game_reveal.py engine/tests/test_the_unmasking_minigame.py -q
python docs/skills/arcwright-minigame/scripts/minigame_tool.py validate nightcap/mini_games/the-unmasking
git add docs/specs/0085-the-unmasking-reveal-reconstruction.md docs/design/line-libraries/truth-sequence-shapes.md docs/roadmap/tasks/AW-278-couch-race-truth-sequence-and-reveal-accounting.md nightcap/mini_games/the-unmasking engine/mini_games/plugins/_the_unmasking.py engine/mini_games/plugins/__init__.py engine/tests/test_the_unmasking_minigame.py
git commit -m "feat(nightcap): add the unmasking package"
```

### Task 4: Build the Shared Reveal, Phone Reflection, and Host Controls

**Files:**

- Create: `nightcap/mini_games/the-unmasking/client/renderer.ts`
- Create: `nightcap/mini_games/the-unmasking/client/styles.css`
- Create: `nightcap/mini_games/the-unmasking/client/renderer.test.ts`

**Interfaces:**

- Consumes: authorized reveal cues, innocent clears, player credits, culprit, reconstruction, standings, podium, superlatives, semantic theme, sound, and accessibility settings.
- Produces: shared cinematic reveal, private phone reflection and score, host cue controls, reconnect-safe playback, audio, motion, and reduced-motion sequence.

- [ ] **Step 1: Write failing order and truth tests**

```typescript
test("renderer cannot show culprit before innocent clears", () => {
  const lifecycle = renderer.mount(sharedRoot, clearingContext());
  lifecycle.handleEvent(culpritCueBeforeClears());
  assert.doesNotMatch(sharedRoot.textContent ?? "", /culprit/i);
});

test("podium order comes from authoritative standings", () => {
  renderer.mount(sharedRoot, podiumContext());
  assert.deepEqual(podiumNames(sharedRoot), ["Wren", "Vale", "Ash"]);
});
```

- [ ] **Step 2: Write failing privacy and reconnect tests**

```typescript
test("phone hides other private guesses", () => {
  renderer.mount(phoneRoot, phoneRevealContext());
  assert.doesNotMatch(phoneRoot.textContent ?? "", /Vale guessed/i);
});

test("reconnect resumes the current cue without replaying applied cues", () => {
  renderer.mount(sharedRoot, reconstructionContext({ revision: 12 }));
  assert.equal(sharedRoot.dataset.phase, "reconstruction");
  assert.equal(sharedRoot.dataset.revision, "12");
});
```

- [ ] **Step 3: Implement the approved sequence**

Build portrait clears, ok and accuse semantic tokens, inline credits, culprit
ring, grave reconstruction, killer-best-move beat, solved and house-win copy,
score count-up, rank movement, tie-safe podium, superlatives, replay prompt,
ordinary last line, phone personal result, host pause/resume/skip-safe controls,
sound controls, captions, accessible focus, and reduced motion.

- [ ] **Step 4: Run and commit**

```powershell
npm --prefix nightcap-web test
npm --prefix nightcap-web run typecheck
npm --prefix nightcap-web run bundle:mini-games
git add nightcap/mini_games/the-unmasking/client
git commit -m "feat(nightcap): stage the unmasking reveal"
```

### Task 5: Tune and Produce the Package-readiness Evidence

**Files:**

- Modify: `nightcap/mini_games/the-unmasking/manifest.json`
- Modify: `nightcap/mini_games/the-unmasking/definitions/0.1.0.json`
- Create: `docs/product/mini-game-readiness/the-unmasking-0.1.0.json`
- Modify: `docs/roadmap/tasks/AW-278-couch-race-truth-sequence-and-reveal-accounting.md`

**Interfaces:**

- Consumes: package-only certification, solved and house-win simulations, real-device evidence, founder reveal review, and audiovisual quality evidence.
- Produces: immutable playtest candidate and explicit `INTEGRATION_PENDING` evidence for Truth registration.

- [ ] **Step 1: Run deterministic package simulations**

```powershell
python docs/skills/arcwright-minigame/scripts/minigame_tool.py simulate --package nightcap/mini_games/the-unmasking --players 2 --seed truth-solved-2
python docs/skills/arcwright-minigame/scripts/minigame_tool.py simulate --package nightcap/mini_games/the-unmasking --players 8 --seed truth-house-win-8
python -m pytest engine/tests/test_mini_game_reveal.py engine/tests/test_the_unmasking_minigame.py -q
```

- [ ] **Step 2: Run package-only certification**

```powershell
python docs/skills/arcwright-minigame/scripts/minigame_tool.py certify --package nightcap/mini_games/the-unmasking --output docs/product/mini-game-readiness/the-unmasking-0.1.0.json
```

Expected: truth immutability, privacy, narration fallback, renderer, score,
podium, simulation, and human-artifact gates pass. Registration and integrated
session gates are `INTEGRATION_PENDING`.

- [ ] **Step 3: Run founder reveal and real-device gates**

Verify solved and house-win variants, all cast sizes, inline credit fairness,
culprit timing, reconstruction clarity, score animation, ties, podium,
superlatives, phone privacy, reconnect, audio, captions, and reduced motion.
Record exact devices, players, build SHA, decisions, findings, and remediation.

- [ ] **Step 4: Keep lifecycle at `playtest` and commit evidence**

```powershell
git add nightcap/mini_games/the-unmasking/manifest.json nightcap/mini_games/the-unmasking/definitions/0.1.0.json docs/product/mini-game-readiness/the-unmasking-0.1.0.json docs/roadmap/tasks/AW-278-couch-race-truth-sequence-and-reveal-accounting.md
git commit -m "test(nightcap): certify the unmasking package"
```

Do not promote to `active` here. The final integration plan registers the
exact version and digest, proves Last Call lock through Truth and podium, then
performs active promotion and GitHub closure.
