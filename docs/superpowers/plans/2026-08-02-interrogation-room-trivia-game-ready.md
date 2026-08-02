# Interrogation Room Trivia Game-ready Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver The Interrogation Room as a production-ready, replayable Last Call pressure-capstone mini-game that increases urgency without deciding case truth or replacing the final accusation.

**Architecture:** The package is an Arcwright-hosted mechanic. Python resolves question content, answer keys, timing, scoring, fallback, and result semantics before clients render them. The Last Call opportunity selects the package deterministically; after the three-question game completes, the authored arc resumes its final interrogation and Leverage window, locks private guesses, and transitions to The Truth.

**Tech Stack:** Python 3.11, Pydantic, pytest, JSON package contracts, TypeScript, Nightcap renderer kit, Node test runner, happy-dom.

## Global Constraints

- Approve the amended `docs/specs/0076-aw-289-interrogation-room.md` before package work.
- Target Last Call with story role `pressure_capstone`; remove the obsolete Grill placement.
- Support 2 to 8 session players and three questions per run.
- Use authored fact records and established case callbacks only. External lookup is not allowed.
- AI may compose bounded wording only after the answer and evidence basis are deterministic; it may not grade, score, select truth, or reveal a future fact.
- General trivia remains dominant and case callbacks remain sparse.
- Mini-game performance grants bounded edge through generic result semantics; it cannot change killer identity, accusation truth, or required clue access.
- Final interrogation, Leverage spending, guess lock, reveal, and podium remain arc-owned transitions outside this package.
- Founder approval of the brief, representative sample, scoring, voice, thin slice, and real-player artifact is mandatory.

---

### Task 1: Amend and Approve the Last Call Creative Contract

**Files:**

- Modify: `docs/specs/0076-aw-289-interrogation-room.md`
- Modify: `docs/roadmap/tasks/AW-289-couch-race-trivia-mini-game.md`
- Modify: `docs/design/authoring/couch-race-session-experience.md`
- Read: `docs/story-bibles/nightcap-couch-race.md`

**Interfaces:**

- Consumes: D-092, D-093, D-094, Last Call's authored convergence function, and the existing representative question set.
- Produces: approved Last Call placement, exact gameplay brief, scoring table, content contract, narration posture, and handoff to final guesses.

- [ ] **Step 1: Run the documentation and package baseline**

```powershell
python -m pytest engine/tests/test_mini_game_content.py engine/tests/test_mini_game_runtime.py -q
npm --prefix nightcap-web test
```

- [ ] **Step 2: Amend the target and exact sequence**

```text
beat: Last Call
story role: pressure_capstone
opening: Vesper frames a rapid three-question evidence check
questions: multiple choice, true/false, and ordering
answers: private and simultaneous on phones
public resolution: table-safe explanation plus live circus-themed standings
completion: emit score and Leverage-compatible result semantics
handoff: final interrogation and Leverage window, then private guesses lock
next beat: The Truth begins only after guesses are immutable
```

- [ ] **Step 3: Correct obsolete authority records**

Replace every Beat 3 placement in the spec and roadmap task with Last Call.
Preserve the existing generated-content validation, authored fact provenance,
deterministic grading, fallback, and scoring proposal. Record the change as a
founder-approved placement correction, not a new trivia design.

- [ ] **Step 4: Present the representative artifact**

Show all three question formats, 2-player and 8-player pacing, generated-copy
validation, authored fallback, private answer handling, shared standings,
sound, motion, reduced motion, and the Last Call handoff.

- [ ] **Step 5: Stop for founder brief, sample, scoring, voice, and implementation approval**

### Task 2: Scaffold the Package and Deterministic Question Resolver

**Files:**

- Create: `nightcap/mini_games/interrogation-room/manifest.json`
- Create: `nightcap/mini_games/interrogation-room/definitions/0.1.0.json`
- Create: `nightcap/mini_games/interrogation-room/content/general_trivia_v1.json`
- Create: `nightcap/mini_games/interrogation-room/README.md`
- Create: `engine/mini_games/plugins/_interrogation_room.py`
- Modify: `engine/mini_games/plugins/__init__.py`
- Create: `engine/tests/test_interrogation_room_minigame.py`

**Interfaces:**

- Consumes: `StatefulMechanicPlugin`, approved fact records, public-safe case snapshot references, content resolver, safety validator, and provider-agnostic routing.
- Produces: `InterrogationRoomState`, immutable resolved questions, deterministic answer evaluation, and package version `0.1.0`.

- [ ] **Step 1: Write failing package and provenance tests**

```python
def test_interrogation_room_declares_last_call_capabilities():
    loaded = load_mini_game_package(Path("nightcap/mini_games/interrogation-room"))
    assert loaded.definition.mechanic_type == "interrogation-room"
    assert (loaded.definition.session_min_players, loaded.definition.session_max_players) == (2, 8)
    assert {"trivia", "pressure-capstone"} <= set(loaded.manifest.capability_tags)


def test_every_general_question_has_approved_provenance(resolved_questions):
    assert all(question.source.source_id == "general-trivia-v1" for question in resolved_questions.general)
    assert all(question.source.safety_review_status == "approved" for question in resolved_questions.general)
```

- [ ] **Step 2: Write failing future-fact and answer-authority tests**

```python
def test_case_callback_rejects_unestablished_fact(resolver):
    with pytest.raises(ContentValidationError, match="unestablished-reference"):
        resolver.resolve(CASE_CALLBACK_WITH_FUTURE_FACT)


def test_answer_key_is_frozen_before_question_starts(plugin):
    state = plugin.start(RESOLVED_DEFINITION, CONTEXT)
    assert state.questions[0].canonical_answer_id == "option-a"
    assert plugin.submit(state, WRONG_SUBMISSION).is_correct is False
```

- [ ] **Step 3: Run and confirm failure**

```powershell
python -m pytest engine/tests/test_interrogation_room_minigame.py -q
```

- [ ] **Step 4: Implement exact state and bounded adaptation**

```python
class InterrogationRoomState(BaseModel):
    phase: Literal["question", "resolution", "standings", "complete"]
    question_index: int = Field(ge=0, le=2)
    questions: tuple[ResolvedTriviaQuestion, ResolvedTriviaQuestion, ResolvedTriviaQuestion]
    submissions_by_question: dict[str, dict[UUID, TriviaSubmission]] = Field(default_factory=dict)
    score_by_participant: dict[UUID, int] = Field(default_factory=dict)
    recent_formats: list[TriviaFormat] = Field(default_factory=list)
    revision: int = Field(ge=0)
```

At question boundaries only, choose the next already-approved question with a
seeded selector. Move difficulty or pressure by at most one band, enforce
format cooldowns, and use `unknown` when the rolling sample is insufficient.
Never rewrite an active question or answer key.

- [ ] **Step 5: Author package `0.1.0` as `playtest`**

Declare three questions, 2 to 8 session players, hybrid authored/generative
content, deterministic fallback, renderer entrypoint, pressure-capstone role,
result schema, time budget, and exact definition digest.

- [ ] **Step 6: Run and commit**

```powershell
python -m pytest engine/tests/test_interrogation_room_minigame.py -q
python docs/skills/arcwright-minigame/scripts/minigame_tool.py validate nightcap/mini_games/interrogation-room
git add docs/specs/0076-aw-289-interrogation-room.md docs/roadmap/tasks/AW-289-couch-race-trivia-mini-game.md docs/design/authoring/couch-race-session-experience.md nightcap/mini_games/interrogation-room engine/mini_games/plugins/_interrogation_room.py engine/mini_games/plugins/__init__.py engine/tests/test_interrogation_room_minigame.py
git commit -m "feat(nightcap): add last call trivia package"
```

### Task 3: Implement Submission, Scoring, Fallback, and Result Semantics

**Files:**

- Modify: `engine/mini_games/plugins/_interrogation_room.py`
- Test: `engine/tests/test_interrogation_room_minigame.py`

**Interfaces:**

- Consumes: server receipt time, immutable answer key, difficulty band, submission idempotency key, and content readiness.
- Produces: per-player score delta, correctness count, duration, fallback marker, and generic `resource_award` semantics.

- [ ] **Step 1: Write failing scoring matrix tests**

```python
@pytest.mark.parametrize(
    ("difficulty", "remaining_ratio", "answer", "expected"),
    [("easy", 0.8, "correct", 140), ("medium", 0.52, "correct", 176), ("hard", 0.0, "correct", 200), ("easy", 0.5, "wrong", -10), ("easy", 0.5, "timeout", 0)],
)
def test_scoring_matrix(difficulty, remaining_ratio, answer, expected):
    assert score_answer(difficulty, remaining_ratio, answer) == expected
```

- [ ] **Step 2: Write failing idempotency and fallback tests**

```python
def test_duplicate_submission_scores_once(plugin, active_state):
    first = plugin.submit(active_state, SUBMISSION)
    second = plugin.submit(first.state, SUBMISSION)
    assert second.state.score_by_participant[PLAYER_ID] == first.state.score_by_participant[PLAYER_ID]


def test_invalid_generated_content_uses_authored_fallback(resolver):
    resolved = resolver.resolve(INVALID_GENERATED_QUESTION)
    assert resolved.fallback_used is True
    assert resolved.question.source.source_id == "general-trivia-v1"
```

- [ ] **Step 3: Implement the approved formula exactly**

For correct answers use `base + floor(50 * clamped_remaining_ratio)` with
bases 100, 150, and 200. Wrong answers are -10. Timeout, invalid, duplicate,
and missing submissions are 0. Clamp authoritative total score at zero. Sort
standings by score, correct count, cumulative response time, then stable join
order.

- [ ] **Step 4: Emit bounded result semantics**

Emit `questions_answered`, `correct_answer_count`, `completion_time_ms`,
`fallback_used`, `mini_game_score_delta`, and an approved generic
`resource_award`. Do not emit case mutations or direct score writes.

- [ ] **Step 5: Run and commit**

```powershell
python -m pytest engine/tests/test_interrogation_room_minigame.py engine/tests/test_mini_game_content.py -q
git add engine/mini_games/plugins/_interrogation_room.py engine/tests/test_interrogation_room_minigame.py
git commit -m "feat(nightcap): resolve last call trivia"
```

### Task 4: Build the Phone Quiz and Shared Pressure Stage

**Files:**

- Create: `nightcap/mini_games/interrogation-room/client/renderer.ts`
- Create: `nightcap/mini_games/interrogation-room/client/styles.css`
- Create: `nightcap/mini_games/interrogation-room/client/renderer.test.ts`

**Interfaces:**

- Consumes: authorized player question projection, public question framing, deadline, personal result, public explanation, standings, semantic theme, locale, sound, and reduced-motion settings.
- Produces: private phone interaction, shared countdown and resolution, host progress controls, reconnect-safe rendering, animation, and audio.

- [ ] **Step 1: Write failing privacy and authority tests**

```typescript
test("shared display never receives private answers", () => {
  renderer.mount(sharedRoot, sharedContext());
  assert.doesNotMatch(sharedRoot.textContent ?? "", /option-a/);
  assert.equal(sharedRoot.querySelector("[data-submit-answer]"), null);
});

test("reconnect renders the authoritative active question", () => {
  renderer.mount(phoneRoot, phoneContext({ questionIndex: 1, revision: 8 }));
  assert.equal(phoneRoot.dataset.questionIndex, "1");
  assert.equal(phoneRoot.dataset.revision, "8");
});
```

- [ ] **Step 2: Write a failing Last Call handoff test**

```typescript
test("completion cues final interrogation without claiming reveal authority", () => {
  renderer.mount(sharedRoot, completedContext());
  assert.match(sharedRoot.textContent ?? "", /final questions/i);
  assert.doesNotMatch(sharedRoot.textContent ?? "", /the killer is/i);
});
```

- [ ] **Step 3: Implement all three surfaces**

Build answer controls for each format, server deadline display, submission
acknowledgment, personal result, public framing, explanation, standings,
Vesper pressure lines, 2-player and 8-player layouts, host fallback, reconnect,
sound controls, accessible focus, color-independent states, and reduced motion.

- [ ] **Step 4: Run and commit**

```powershell
npm --prefix nightcap-web test
npm --prefix nightcap-web run typecheck
npm --prefix nightcap-web run bundle:mini-games
git add nightcap/mini_games/interrogation-room/client
git commit -m "feat(nightcap): render last call trivia"
```

### Task 5: Tune and Produce the Package-readiness Evidence

**Files:**

- Modify: `nightcap/mini_games/interrogation-room/manifest.json`
- Modify: `nightcap/mini_games/interrogation-room/definitions/0.1.0.json`
- Create: `docs/product/mini-game-readiness/interrogation-room-0.1.0.json`
- Modify: `docs/roadmap/tasks/AW-289-couch-race-trivia-mini-game.md`

**Interfaces:**

- Consumes: package-only certification, deterministic simulations, content validation evidence, real-device evidence, and founder thin-slice review.
- Produces: immutable playtest candidate and explicit `INTEGRATION_PENDING` evidence for final Nightcap registration.

- [ ] **Step 1: Run deterministic package simulations**

```powershell
python docs/skills/arcwright-minigame/scripts/minigame_tool.py simulate --package nightcap/mini_games/interrogation-room --players 2 --seed last-call-2
python docs/skills/arcwright-minigame/scripts/minigame_tool.py simulate --package nightcap/mini_games/interrogation-room --players 8 --seed last-call-8
python -m pytest engine/tests/test_interrogation_room_minigame.py -q
```

- [ ] **Step 2: Run package-only certification**

```powershell
python docs/skills/arcwright-minigame/scripts/minigame_tool.py certify --package nightcap/mini_games/interrogation-room --output docs/product/mini-game-readiness/interrogation-room-0.1.0.json
```

Expected: package, mechanic, privacy, content, fallback, simulation, renderer,
and human-artifact gates pass. Registration and integrated-session gates are
`INTEGRATION_PENDING`, not silently treated as passes.

- [ ] **Step 3: Run founder thin-slice and real-device gates**

Verify all three formats, question quality, wrong-answer feel, standings,
phone privacy, shared pressure, fallback, reconnect, animation, audio, reduced
motion, and the handoff to final interrogation. Record exact devices, players,
build SHA, findings, decisions, and remediation.

- [ ] **Step 4: Keep lifecycle at `playtest` and commit evidence**

```powershell
git add nightcap/mini_games/interrogation-room/manifest.json nightcap/mini_games/interrogation-room/definitions/0.1.0.json docs/product/mini-game-readiness/interrogation-room-0.1.0.json docs/roadmap/tasks/AW-289-couch-race-trivia-mini-game.md
git commit -m "test(nightcap): certify last call trivia package"
```

Do not promote to `active` here. The final integration plan registers the
exact version and digest, proves the Last Call handoff and whole-session path,
then performs active promotion and GitHub closure.
