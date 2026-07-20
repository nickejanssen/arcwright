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
- **Content mode:** Hybrid. Question templates, answer options, and clue
  meanings are authored; case facts and permitted values are resolved from
  deterministic session state before execution.
- **Question source:** Case-specific by default, with optional general-trivia
  framing only when it directly reinforces the case or setting. No question
  may require an external fact to solve the mystery.
- **Question count:** Three authored question slots in the first thin slice.
- **Answer format:** Deterministic selected answer, not free text.
- **Failure policy:** A wrong or missing answer does not eliminate a player or
  block the case. The game resolves to the fallback clue when the deadline or
  content delay requires it.

### Proposed question contract

Each resolved question must contain:

- A case fact or claim reference.
- A deterministic set of answer options.
- One canonical answer key.
- A public explanation safe for the shared display.
- A private result payload for the submitting player.
- A clue or lead consequence for success.
- A reduced fallback clue that preserves solvability.

The runtime must compare the submitted option with the resolved answer key.
No model call may grade correctness or select the answer key.

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

- Use fictional, case-grounded content only.
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

- [ ] Confirm hybrid, case-grounded question source.
- [ ] Confirm Beat 3 placement.
- [ ] Confirm individual answer model with public resolution.
- [ ] Confirm 90-second target and three-question thin slice.
- [ ] Confirm AW-284 scoring integration.
- [ ] Approve representative question and scoring sample.
- [ ] Approve final diegetic framing and narrator copy direction.

## Acceptance criteria

- [ ] Founder approves this brief and representative sample before package
  authoring.
- [ ] Package validates against the AW-249 schema and loader.
- [ ] Every definition includes an authored delayed-clue fallback.
- [ ] Question answer keys resolve deterministically before execution.
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
