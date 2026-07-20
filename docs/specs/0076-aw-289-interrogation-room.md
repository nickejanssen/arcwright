> Current version: v0.1
> Last updated: 2026-07-20
> Status: Draft; awaiting founder design-gate approval
> Canonical path: docs/specs/0076-aw-289-interrogation-room.md

# AW-289: The Interrogation Room

## References

- GitHub issue: [#258](https://github.com/nickejanssen/arcwright/issues/258)
- Roadmap task: `docs/roadmap/tasks/AW-289-couch-race-trivia-mini-game.md`
- Rehearsal gate: `docs/roadmap/tasks/AW-286-couch-race-rehearsal-slice-and-rehearsal-1-retarget.md`
- Scoring dependency: `docs/roadmap/tasks/AW-284-race-scoring-and-accusation-state.md`
- Product approval: `docs/product/decisions-log.csv` D-079
- Runtime boundary: `docs/decisions/0009-mini-game-runtime-boundary.md`
- Story bible: `docs/story-bibles/nightcap-couch-race.md` Sections 4, 6, 7, and 8
- Authoring foundation: `docs/specs/0046-aw-249-nightcap-mini-game-authoring-foundation.md`
- Content and safety foundation: `docs/specs/0047-aw-250-mini-game-content-resolution-and-safety.md`

## Status and gate

This is a proposed design brief, not an implementation authorization. The
founder must approve the brief and the representative sample in this document
before a package is scaffolded or bound into `nightcap/arc.json`.

The only new trivia game authorized for Rehearsal 1 is The Interrogation Room.
The following are future candidates and are not current implementation scope:

1. Contradiction Trap
2. Planted Evidence
3. Alibi Auction
4. Chain of Custody

Those candidates should be reconsidered after Rehearsal 1 using observed
player engagement, fairness, pacing, replay desire, and implementation cost.

## Proposed locked brief

### Concept

**Game ID:** `interrogation-room`

**Title:** The Interrogation Room

**Logline:** The narrator presents a case-grounded question drawn from the
resolved evidence and suspect claims. Players answer under pressure, then the
room sees which investigator noticed the detail that makes the next
interrogation sharper.

**Core verb:** Recall, connect, and answer.

**Nightcap purpose:** Convert the case's existing evidence and interrogation
claims into a short, legible Murder Mystery Trivia challenge. The result is an
investigative lead or neutral observation, never a detached arcade score.

### Proposed runtime shape

- **Target beat:** Beat 3, The Grill, between interrogation rounds.
- **Participation:** Individual, with simultaneous or staggered private
  answers and a table-visible resolution.
- **Player range:** 2 to 8, with rehearsal coverage at 2 to 5 players and
  catalog compatibility through 8 players.
- **Duration:** 90 seconds for the initial thin slice.
- **Content mode:** Hybrid. Each session receives newly generated questions,
  but every question is generated inside an authored schema, tone envelope,
  difficulty band, answer contract, and safety policy.
- **Question source:** Setting- and genre-matched general trivia by default,
  with occasional case callbacks. Case-linked questions should be sparse and
  memorable rather than repetitive. No question may require an external fact
  to solve the mystery.
- **Question count:** Three generated question slots in the first thin slice.
- **Answer format:** A deliberate adaptive mix of selectable options,
  true/false, ordering, and tightly bounded short answers with a
  pre-resolved canonical answer and deterministic accepted aliases. Fully
  open-ended prose grading is out of scope.
- **Failure policy:** A wrong or missing answer does not eliminate a player or
  block the case. The game resolves to the fallback clue when the deadline or
  content delay requires it.

### Proposed question contract

Each resolved question must contain:

- A case fact or claim reference.
- A deterministic set of answer options.
- One canonical answer key.
- A self-contained evidence basis sufficient to answer the question.
- A narrative-grounding reference showing which resolved context is allowed at
  the current moment.
- A public explanation safe for the shared display.
- A private result payload for the submitting player.
- A clue or lead consequence for success.
- A reduced fallback clue that preserves solvability.

General trivia facts must come from an approved, safety-reviewed fact and
answer source. The session generator may compose the prompt, options, and
presentation, but the canonical answer key must be derived from or validated
against that source before play.

The runtime must compare the submitted option with the resolved answer key.
No model call may grade correctness or select the answer key after play begins.

### Generation validation and failure handling

Generated content must pass validation before it is shown to any player or
used to select a clue. Validation is a hard gate, not a post-play telemetry
check.

The validator must confirm:

- **Structure:** The requested answer format, options, timing, difficulty, and
  required fields are present.
- **Answer integrity:** Exactly one canonical answer is supported by the
  approved fact source or resolved case data; distractors are distinct and
  not accidentally correct.
- **Self-containment:** The player has enough public information to answer;
  the question does not rely on an unstated fact.
- **Narrative grounding:** A case callback references only facts or claims
  marked established and available at the current arc position. It must never
  reveal a future clue, hidden truth, private evidence, killer identity, or
  unresolved event.
- **Safety and privacy:** Tone, wording, and payloads pass the AW-250 safety
  policy and the two-surface privacy contract.
- **Tone and fit:** The question matches the resolved session tone and the
  intended humor, wonder, and genre without becoming gruesome or incoherent.
- **Variety and pacing:** The question respects format cooldowns, category
  rotation, difficulty bounds, and the current adaptive room momentum.

If any check fails, the content is discarded before delivery. The system may
make a bounded replacement attempt, but it must use the authored safe question
or reduced clue fallback when the retry budget is exhausted or generation is
late. The player receives no penalty for invalid content.

Validation failures should emit a replayable, non-sensitive reason code such
as `missing-evidence-basis`, `unestablished-reference`, `ambiguous-answer`,
`unsafe-content`, or `format-contract-failure`. Raw private content must not
be included in the telemetry payload.

### Adaptive room momentum

Immersion is the product outcome, not a runtime variable. The engine must not
pretend to measure a player's psychological state with an opaque score. The
platform-neutral runtime concept is **adaptive room momentum**, a bounded
context assembled from observable events and resolved narrative intent.

The mini-game reads this context only at question boundaries. It never reads
Nightcap beat names, killer identity, hidden truth, raw knowledge-graph state,
or private evidence.

#### V1 adaptive context

The following signals are the recommended first contract. Each is represented
as a small enum or bounded value with an `unknown` state, not as an unbounded
model judgment.

| Signal | Meaning and measurement | Allowed effect |
| --- | --- | --- |
| `narrative_phase_role` | Platform-neutral arc role such as opening, discovery, pressure, reveal, or release, resolved by the arc | Selects an approved format family and presentation posture |
| `tension_band` | Resolved narrative pacing state and target direction, supplied by the arc engine | Moves intensity one step toward rising, holding, or releasing |
| `time_budget_band` | Server-authoritative time remaining before the next arc transition | Selects short, standard, or extended question timing |
| `participation_health` | Rolling ratio of eligible players who started or submitted an answer, with disconnects and timeouts recorded separately | Invites faster, clearer, or more collaborative formats; never punishes low participation |
| `response_pace_band` | Rolling median of response time normalized by the question deadline | Adjusts presentation tempo and pressure within configured bounds |
| `challenge_fit_band` | Recent correctness and timeout rate over completed answers, requiring a minimum sample | Moves difficulty by at most one band; never makes the mystery less solvable |
| `player_count_profile` | Active player count and whether the group is fully represented | Selects formats that remain legible and fair for the table size |
| `format_variety_state` | Recent format history and per-format cooldown state | Prevents repetition and creates deliberate contrast |
| `spotlight_balance_band` | Aggregate distribution of recent participation and successful moments | Offers quieter players opportunities without exposing a hidden ranking |
| `session_tone_tags` | Authored or resolved tags such as wry, chaotic, wondrous, eerie, or competitive | Shapes generated language, humor, imagery, and format flavor |
| `content_readiness` | Whether generated content has passed structural, safety, privacy, and solvability validation | Uses ready content or an authored fallback; never waits indefinitely |

For the first thin slice, the rolling window is the most recent three resolved
questions, with no adaptation from a single event. Thresholds are configuration
and rehearsal-tunable. When sample size is insufficient, the value is
`unknown` and the selector uses the safe default.

#### Adaptive policy guardrails

- Read context only between questions, never while a player is answering.
- Change difficulty or pressure by at most one step at a time.
- Use hysteresis so the game does not oscillate between states.
- Preserve per-format cooldowns and minimum variety.
- Do not interpret a slow answer as disengagement without corroborating data.
- Do not adapt by removing a player's agency, hiding required information, or
  making a failure state permanent.
- Use deterministic seeded variation so a run can be replayed and debugged.
- Log the input context, selected format, content validation result, and
  outcome for rehearsal analysis.

#### Visionary Arcwright signal families

These are valuable engine capabilities to design toward, but they are not
additional AW-289 runtime dependencies:

- `narrative_obligation_pressure`: whether the arc has an unresolved,
  platform-neutral obligation that a mini-game can help surface.
- `emotional_contrast_need`: whether the experience needs levity, wonder,
  tension, or release to avoid a flat emotional curve.
- `curiosity_opportunity`: whether the resolved arc has a safe open question
  or reveal opportunity that can invite player speculation.
- `novelty_budget`: how much format, presentation, or content novelty the
  session can spend before clarity and fairness suffer.
- `agency_balance`: whether recent interactions have offered sufficient
  player choice, risk, and expression across the group.
- `cognitive_load_band`: a platform-neutral estimate from recent interaction
  complexity, timing pressure, and accessibility constraints.
- `memory_echo_opportunity`: a future continuity signal for experiences that
  are allowed to reference prior sessions. It must remain outside Nightcap v1.

These signals should be emitted as generic context by Arcwright and consumed
through a declared mini-game capability contract. A mini-game may request a
signal family, but it may not depend on a specific experience's internal state.

### Proposed scoring and investigative output

- Correct answer: award the AW-284-defined mini-game performance reward and
  stage the associated investigative lead.
- Incorrect answer: award no trivia reward and preserve the normal arc path;
  do not apply elimination or a permanent lockout.
- Timeout, invalid, duplicate, or missing submission: resolve once according
  to the authoritative server state and use the authored fallback policy.
- Tie: resolve by the AW-284 deterministic tie policy, not by client order.
- Trivia performance contributes to the documented evidence/mini-game
  scoring dimension only. It cannot alter accusation truth, killer identity,
  case resolution, or knowledge state.

The first thin slice should expose neutral, game-scoped outputs such as:

- `questions-answered`
- `correct-answer-count`
- `completion-time-ms`
- `fallback-used`

These outputs must not feed killer assignment or cross-session behavior.

### Two-surface contract

**Player phone:** private question, answer options, deadline, submission
acknowledgment, and personal result.

**Shared display:** narrator framing, public question title when safe,
resolution state, public lead or neutral observation, and table-safe ranking.

**Host:** progress, deadline, fallback state, and safe operational controls.

Private answers, unrevealed options, private clues, and player-specific
results must not reach another player or the shared display.

### Authoritative boundary

Python owns the timer, question resolution, answer validation, duplicate and
late-submission handling, scoring, outcome, clue/lead selection, fallback,
persistence, and reconnect state.

TypeScript renders authorized state and submits player actions. It must not
compute deadlines, validate answers, award points, select clues, or decide
outcomes.

AI may provide permitted narrative framing after deterministic resolution, but
it may not manage state, grade answers, choose outcomes, or mutate the case.

### Content and safety

- Use fictional, setting-matched content only.
- Keep general trivia dominant and case callbacks occasional.
- Make generated humor witty, wry, irreverent, surprising, and non-gruesome.
- Avoid graphic violence and real-person targeting.
- Do not infer protected traits.
- Do not expose private evidence through a public question or explanation.
- Do not require external web knowledge for a case-critical answer.
- Keep final narrator copy and character voice subject to founder review.

### Delayed clue fallback

The package must define an authored fallback with:

- A server-owned delay threshold.
- A reduced clue variant.
- Host override support.
- A guarantee that every timeout, content delay, abort, or full-table failure
  advances the arc without making the case unsolvable.

## Representative sample for founder review

The following sample demonstrates the intended shape. It is illustrative
content only and must be replaced or approved before package authoring.

### Sample question 1: timeline recall

**Prompt:** The gallery ledger places the south door alarm before the lights
failed. Which suspect's alibi does that immediately pressure?

**Options:**

- Mara Vale
- Julian Cross
- The night porter
- It does not pressure an alibi yet

**Canonical answer:** The option resolved from the case ledger.

**Success output:** A lead pointing to the affected timeline contradiction.

**Fallback output:** The south-door timing is preserved as a reduced clue.

### Sample question 2: claim provenance

**Prompt:** Which statement was heard directly from the suspect rather than
  inferred from the evidence board?

**Options:** Four resolved claim references.

**Canonical answer:** The authored claim reference selected during case
resolution.

**Success output:** A neutral observation identifying a claim worth testing.

**Fallback output:** The claim remains available through the normal
interrogation path.

### Sample question 3: motive and method separation

**Prompt:** Which detail establishes opportunity without proving motive?

**Options:** Four resolved evidence references.

**Canonical answer:** The authored evidence reference selected during case
resolution.

**Success output:** A lead that sharpens the next interrogation intent.

**Fallback output:** The opportunity detail is released in reduced form.

## Founder approval checklist

- [ ] Confirm per-session generated questions within authored constraints.
- [ ] Confirm setting-matched general trivia as the dominant source, with
  sparse case callbacks.
- [ ] Confirm Beat 3 placement.
- [ ] Confirm the deliberate adaptive answer-format mix.
- [ ] Confirm individual answer model with public resolution.
- [ ] Confirm 90-second target and three-question thin slice.
- [ ] Confirm adaptive room momentum as the runtime concept and immersion as
  a playtest outcome.
- [ ] Confirm the V1 signal set and the adaptive policy guardrails.
- [ ] Confirm pre-delivery validation of structure, answer integrity,
  self-containment, narrative grounding, safety, privacy, tone, and variety.

## Design test findings

The first paper test used a three-format sequence in a fictional Murder at
the Circus session. The third question was initially under-specified because
it asked players to order events without providing the evidence that
established the order. The question was invalid, and correctly received no
score impact after correction.

This test confirms that the implementation must validate narrative grounding
and answer sufficiency before delivery. An invalid question can break
immersion, and an invalid case callback could reveal a clue that the story has
not established yet. This is a blocking content-resolution failure, not a
player error.
- [ ] Confirm AW-284 scoring integration.
- [ ] Approve representative question and scoring sample.
- [ ] Approve final diegetic framing and narrator copy direction.

## Acceptance criteria

- [ ] Founder approves this brief and representative sample before package
  authoring.
- [ ] Package validates against the AW-249 schema and loader.
- [ ] Every definition includes an authored delayed-clue fallback.
- [ ] Question answer keys resolve deterministically before execution.
- [ ] No question reaches a player unless its evidence basis, answer key,
  narrative grounding, safety, privacy, and format contract validate.
- [ ] A question cannot reference an unestablished clue, hidden truth, private
  evidence, or future narrative event.
- [ ] Invalid generated content is discarded without player penalty and uses
  bounded regeneration or the authored fallback.
- [ ] Correct, incorrect, late, duplicate, invalid, timeout, and abort cases
  resolve exactly once.
- [ ] AW-284 scoring integration is deterministic and cannot alter accusation
  authority or case truth.
- [ ] Private payloads are excluded from unauthorized players and the shared
  display.
- [ ] Reconnect restores the authorized authoritative state.
- [ ] Content passes AW-250 safety review.
- [ ] Existing Crime Scene Smash, Evidence Locker, and Tell Me Something True
  behavior remains unchanged.
- [ ] Rehearsal event-dump verification proves the expected lifecycle.
- [ ] The game works for the supported rehearsal player range.

## Explicit non-goals

- Building the four future candidate games before Rehearsal 1.
- Adding player-killer, informant, or elimination roles.
- Adding free-text answer grading.
- Adding external web trivia dependencies.
- Binding a draft package into the production arc.
- Moving scoring, timing, or outcomes into a client.
- Wiring behavioral outputs into killer assignment or cross-session memory.

## Implementation gate

Once the founder approves the checklist above, create the implementation
worktree from updated `origin/main` on `codex/aw-289-interrogation-room`.
Then scaffold `nightcap/mini_games/interrogation-room/` through the
`arcwright-minigame` lifecycle. Do not use the AW-284 worktree or cherry-pick
from its branch.
