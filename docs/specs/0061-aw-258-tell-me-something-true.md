# AW-258: Tell Me Something True

> Current version: v0.1
> Last updated: 2026-06-25
> Status: Approved
> Canonical path: docs/specs/0061-aw-258-tell-me-something-true.md

**Status**: Approved

**Author**: Codex | **Date**: 2026-06-25

---

# References

- Instructions: `AGENTS.md`, `CLAUDE.md`, `docs/README.md`
- PRD sections: `docs/prd/02-requirements.md`, `docs/prd/03-scope.md`
- Architecture sections: `docs/architecture/03-arc-execution.md`,
  `docs/architecture/08-event-system.md`
- Related ADRs: `docs/decisions/0009-mini-game-runtime-boundary.md`
- Story bible: `docs/story-bibles/nightcap-murder-mystery.md`
- Related specs:
  `docs/specs/0046-aw-249-nightcap-mini-game-authoring-foundation.md`,
  `docs/specs/0047-aw-250-mini-game-content-resolution-and-safety.md`,
  `docs/specs/0048-aw-251-mini-game-runtime-persistence-and-clue-gating.md`,
  `docs/specs/0049-aw-252-mini-game-api-events-and-sdk.md`,
  `docs/specs/0050-aw-253-nightcap-web-mini-game-rendering.md`,
  `docs/specs/0051-aw-254-first-production-nightcap-mini-game.md`
- Roadmap context:
  `docs/roadmap/tasks/AW-257-promote-crime-scene-smash-and-evidence-locker.md`
- Product decisions: `docs/product/decisions-log.csv` D-052, D-058, D-059,
  D-060, D-061, D-062, D-063

---

# Overview

Define the locked MVP design for the founder-selected Nightcap social
mini-game candidate: **Tell Me Something True**.

AW-258 is a spec-only task. It records the design, architecture boundaries,
signal contract, and downstream implementation split. It does not add runtime,
persistence, API, SDK, frontend, package, schema migration, dependency, or arc
binding changes.

D-063 is the durable product decision that approves Tell Me Something True as a
Nightcap social opener mini-game design candidate. D-063 approves the game ID
and design direction for AW-258, not final shipped package content and not a
replacement for the first production package decision in D-062. Crime Scene
Smash remains the first production Nightcap mini-game package under AW-257 and
AW-254.

---

# Repo Findings

- `AW-258` is the next available task ID after `AW-257` in
  `docs/roadmap/index.json`.
- `docs/specs/0060-aw-230-real-device-privacy-matrix.md` is the latest numbered
  spec in `docs/specs/`; this spec uses `0061`.
- Existing checked-in Nightcap mini-game package:
  `nightcap/mini_games/evidence-locker-402`.
- Non-shipping fixtures and template are present under
  `nightcap/mini_games/_fixtures/` and `nightcap/mini_games/_template/`.
- No checked-in Candy Crush variant was found in canonical repo paths during
  AW-258 inspection.
- `cmd /c make.cmd type` currently fails because default `python` resolves to
  Python 3.9.18, while repo syntax requires Python 3.11 or newer. The local
  `.aw102-venv` interpreter reports Python 3.11.15.
- D-062 records Crime Scene Smash as the first production Nightcap mini-game
  package.
- D-063 records founder approval of Tell Me Something True as a Nightcap social
  opener mini-game design candidate.

---

# In Scope

- Locked game design for `tell-me-something-true`.
- Phase, surface, scoring, edge-case, and replay-variance contracts.
- v1 signal data contract for future analysis only.
- Mapping to future implementation boundaries if this candidate is scheduled:
  - future package authoring for production package files and content review.
  - AW-251 for deterministic runtime, persistence, submissions, scoring, and
    signal computation.
  - AW-252 for API, events, and SDK.
  - AW-253 for web rendering and device integration.
  - a future promotion and rehearsal task after package approval.
- Explicit no-clue-gate behavior.
- Explicit v1 prohibition on killer-assignment, cross-session, or persistent
  standing effects.

---

# Out Of Scope

- Runtime execution, timers, submissions, scoring, outcomes, persistence, or
  signal computation.
- Database schema changes or migrations.
- API endpoints, ContentEvent model changes, SDK methods, or frontend
  rendering.
- Production package files under `nightcap/mini_games/`.
- Arc bindings in `nightcap/arc.json`.
- New dependencies, secrets, model names, provider names, prompt changes, or
  eval changes.
- v1.1 behavioral signal wiring into killer assignment, continuity, or
  cross-session behavior.

---

# Locked Game Design

## Identity

- Game name: **Tell Me Something True**.
- Game ID: `tell-me-something-true`.
- Mechanic type: `social-truth-bluff`.
- Nightcap role: pure social opener and icebreaker.
- Target position: Beats 1 to 3.
- Clue behavior: does not gate a clue, unlock a clue, delay a clue, or block arc
  progress.
- Player floor: four human players, enforced by lobby or session start
  validation.
- Two-player and three-player handling: no graceful skip path in v1.
- Participation mode: group.
- Content mode: hybrid.
- Target duration: one 45-second input window plus sequential spotlights,
  reveals, and scoreboard.

## Fact Provenance

- For each player, the engine selects one low-stakes fact from that player's
  generated character profile.
- Facts must come from character profile data, not from player real-world
  identity, account metadata, device data, or inferred protected traits.
- Facts must stay inside Nightcap content territory from the story bible.
- Facts must be suitable for public reveal on the shared display after the
  player submits.
- Candidate fact categories must rotate across sessions. Initial allowed
  categories:
  - `past_transgressions`
  - `social_embarrassments`
  - `professional_tells`
  - `odd_habits`
  - `minor_rivalries`
  - `party_gossip`

## Lie Input

- Input format: hybrid Mad Libs.
- The engine provides the true fact with one key word or phrase blanked out.
- The player types a replacement into the blank.
- The player chooses one submit action:
  - `Submit Truth`
  - `Submit Lie`
- A player may type the actual truth and mark it Truth.
- A player may fabricate and mark it Lie.
- The engine stores the declared truth state from the submit action. AI
  commentary may not override it.

## Round Structure

- Single round.
- All connected players submit simultaneously during Phase 1.
- Statements reveal sequentially during Phase 2.
- Each spotlight focuses on one player at a time.
- The spotlighted player does not vote on their own statement.
- Every other connected player may vote Truth or Lie.
- Voting has no per-player limit across the round.

## Scoring

- Score is throwaway mini-game score only.
- Score is used only for the game's internal leaderboard.
- Score does not affect persistent Arcwright standing, accusation tokens,
  killer assignment, character behavior, clue distribution, pacing policy, or
  continuity.
- The exact point schedule belongs to AW-251, but it must preserve these
  invariants:
  - points can reward fooling voters with a lie.
  - points can reward correctly identifying truth or lie.
  - abstentions earn no points.
  - no score can mutate canonical Nightcap standing.

---

# Phase And Surface Contract

Arcwright remains surface-agnostic. Engine code must emit audience-targeted
events and presentation hints. It must not include rendering logic or hardcode
surface-specific presentation.

Nightcap presentation mapping:

| Nightcap presentation | Arcwright target |
| --- | --- |
| Shared display | `target_audience=shared_display` |
| Player device | `target_audience=specific_player` |

## Phase 1: Input

- Shared display:
  - narrator frames the game in the selected diegetic wrapper.
  - displays a 45-second timer.
  - does not show private facts, blanks, or typed inputs before reveal.
- Player device:
  - shows the player's fact with a blank.
  - shows a text field for the blank.
  - shows `Submit Truth` and `Submit Lie`.
- Authoritative owner:
  - Python owns the input deadline.
  - Python owns accepted submission state.
- AFK input:
  - if the player does not submit before deadline, Python auto-submits the true
    statement.
  - auto-submit is marked as a truth submission.

## Phase 2: Spotlight

- Shared display:
  - spotlights one submitted statement.
  - shows the spotlighted player as the current focus.
  - shows disconnected players as unavailable.
- Spotlighted player device:
  - shows `Look at the screen`.
- Other connected player devices:
  - show `Truth` and `Lie` voting buttons.
- Authoritative owner:
  - Python owns spotlight order.
  - Python owns vote acceptance and vote deadline.
- Disconnect:
  - disconnected players are grayed out on the shared display.
  - disconnected players are skipped for their own spotlight.
  - disconnected players do not cast votes while disconnected.

## Phase 3: Reveal

- Shared display:
  - flips the spotlighted statement to true or false.
  - shows vote breakdown.
  - may include narrator commentary.
- Player devices:
  - show personal success or failure feedback.
- Authoritative owner:
  - Python owns truth result, vote breakdown, and score delta.
- AFK voting:
  - no submitted vote before the vote deadline counts as abstain.
  - abstentions earn no points.

## Phase 4: Scoreboard

- Shared display:
  - shows the internal leaderboard.
  - shows any degenerate-case narrator beat.
- Player devices:
  - show `Look at the screen`.
- Authoritative owner:
  - Python owns final score totals and run completion.

---

# Diegetic Framing

Final narrator prose remains human-authored unless explicitly delegated. This
spec locks structural scaffolding only.

| Session frame | Diegetic title | Presentation scaffold |
| --- | --- | --- |
| High Society | The Host's Parlor Game | blackmail journal pages |
| Corporate | Mandatory Synergy | radical candor app |
| Sci-Fi | Biometric Calibration | AI stress test |

The shared display must prominently feature the Arcwright AI narrator driving
the action through the selected frame. The narrator may comment on submitted
lies after deterministic state is resolved. The narrator may not decide truth,
score, votes, signals, outcomes, or session state.

Degenerate cases:

- If every submitted statement is marked Truth, the narrator mocks the table.
- If every submitted statement is marked Lie, the narrator mocks the table.
- Mockery is flavor only and cannot affect score beyond the normal deterministic
  scoring rules.
- Mockery cannot affect canonical Nightcap state.

---

# Signal Data Contract

Signals are captured for future v1.1 analysis only. In v1 they are neutral,
deterministic, game-scoped observations.

Signals must not feed:

- killer assignment.
- dialogue policy.
- clue targeting.
- pacing policy.
- persistent Arcwright standing.
- continuity.
- cross-session behavior.

## `deception_aptitude`

- Type: number.
- Range: 0.0 to 1.0.
- Scope: participant.
- Meaning: percentage of Truth votes received on a fabricated lie.
- Calculation:
  - compute only for statements submitted as Lie.
  - numerator is count of Truth votes on that lie.
  - denominator is count of non-abstaining votes on that spotlight.
  - if there are no non-abstaining votes, value is 0.0.
- Truth submissions do not inflate this metric.

## `deflection_tendency`

- Type: structured map in runtime event payloads.
- Scope: participant.
- Shape: `{target_player_id: lie_vote_count}`.
- Meaning: count of times the current player voted Lie against each target
  player.
- Current schema note:
  - AW-249 authoring declarations support scalar value types.
  - AW-251 must either add approved structured behavioral output support or
    emit `deflection_tendency` as structured event payload while retaining a
    scalar authoring declaration for validation.
  - AW-258 does not change schema.

---

# Replay Variance

- Rotate fact categories across sessions.
- Use dynamic blanking by phrase type. Minimum initial phrase types:
  - noun phrase.
  - verb phrase.
  - object phrase.
  - relationship phrase.
- Vary spotlight order deterministically from run seed and accepted
  participants.
- Feed typed lies to narrator commentary only after deterministic state is
  resolved.
- Commentary generation is expressive only. It cannot decide truth, score,
  votes, signals, outcomes, or session state.

---

# Implementation Split

## Future Package Authoring

- Create `nightcap/mini_games/tell-me-something-true/` only under an approved
  future package-authoring task.
- Use manifest lifecycle `draft` until content review passes.
- Use content mode `hybrid`.
- Define rules, authored framing scaffolds, generation constraints, player
  count, duration, authored delayed clue fallback, and behavioral outputs.
- Include presentation prototype files only if they contain no authoritative
  timing, scoring, outcomes, clue unlocking, or session state.
- Do not bind the draft package into `nightcap/arc.json`.

Fallback contract:

- AW-249, D-059, and ADR 0009 require every production mini-game definition to
  declare an authored delayed clue fallback.
- Tell Me Something True is not a clue gate during normal completion. The
  fallback still must be authored and real if it is authored as a production
  package, because the package must remain valid under the existing mini-game
  contract.
- The fallback for this game should preserve mystery solvability by advancing
  the session without withholding required information and by providing the
  authored fallback behavior selected during future content review.
- AW-251 must ensure timeout and failure paths follow the authored fallback and
  do not leave the arc waiting on this social opener.
- No schema change is approved by AW-258.

## AW-251: Runtime

- Add closed-registry mechanic support for `social-truth-bluff`.
- Python owns:
  - input deadline.
  - auto-truth AFK handling.
  - accepted submissions.
  - spotlight order.
  - disconnect skip.
  - vote acceptance.
  - abstentions.
  - truth reveal.
  - score computation.
  - signal computation.
  - run completion.
- Runtime must reject unknown mechanic types before run creation.
- Runtime must not call AI to decide truth, score, votes, signals, or outcomes.

## AW-252: API, Events, And SDK

- Add typed mini-game state and submission payloads for:
  - input phase.
  - spotlight phase.
  - reveal phase.
  - scoreboard phase.
- Preserve privacy:
  - private fact prompts go only to `specific_player`.
  - shared display does not receive another player's prompt before reveal.
  - reconnect exposes only authorized state.
- SDK methods submit actions only.
- SDK and route handlers may not resolve outcomes locally.

## AW-253: Web Rendering

- Render all four phases for shared display and player devices.
- Support loading, timeout, disconnected, skipped, reveal, and scoreboard
  states.
- Render narrator-led framing for the selected diegetic wrapper.
- Preserve accessibility and degraded-network states.
- Do not add canonical timing, scoring, outcome, or state logic to web clients.

## Future Promotion And Rehearsal

- Promote only after founder content approval.
- Verify complete flow on supported devices.
- Verify privacy, reconnect, pause and resume, behavioral output, accessibility,
  and rehearsal blocker triage.

---

# Acceptance Criteria

- [ ] Spec exists at `docs/specs/0061-aw-258-tell-me-something-true.md`.
- [ ] Spec captures the locked game name and ID.
- [ ] Spec states that the game is a pure social opener for Beats 1 to 3.
- [ ] Spec states that the game does not gate, unlock, reduce, delay, or assert
  a clue during normal completion.
- [ ] Spec preserves the authored delayed clue fallback requirement for the
  future production package.
- [ ] Spec states that scoring is internal and non-persistent.
- [ ] Spec preserves ADR 0009: Python owns deterministic game authority.
- [ ] Spec preserves surface agnosticism: engine emits audience-targeted events,
  clients render.
- [ ] Spec records the v1.1 signal contract and forbids v1 behavioral wiring
  into killer assignment, dialogue policy, continuity, or cross-session
  behavior.
- [ ] Spec states the four-player floor and no two-player or three-player v1
  skip behavior.
- [ ] Spec covers AFK input, AFK voting, disconnect, and all-truth or all-lie
  degenerate cases.
- [ ] Spec records the current `make.cmd type` Python 3.9 environment blocker.
- [ ] No runtime, schema, API, SDK, frontend, package, arc binding, dependency,
  provider string, model string, secret, or agent-local file is added.

---

# Test Plan

## AW-258 Verification

- Run `git status --short --branch` before and after the change.
- Confirm only the AW-258 spec file, decision log, and directly affected
  roadmap records changed.
- Confirm no agent-local files are staged.
- Confirm the new spec contains no em dash characters.
- Confirm the new spec contains no secrets, API keys, provider names, or model
  names.
- Run `cmd /c make.cmd type` and record the known Python 3.9 blocker if it
  remains.

## Later Implementation Verification

- Package validation via `load_mini_game_package`.
- Unit tests for fact selection, blanking, input deadline, auto-truth,
  abstention, disconnect skip, vote tally, scoring, and signal computation.
- Runtime tests for closed mechanic registry and no clue unlock behavior.
- API tests for authorization, idempotency, phase event payloads, and privacy
  filtering.
- SDK typecheck and build.
- Frontend tests for all four phases, reconnect, loading, timeout, and error
  states.
- Real-device privacy and accessibility matrix before AW-254 completion.

---

# Risks and Unknowns

**Risks**:

- Current mini-game authoring schema requires a clue fallback record even though
  this mechanic does not gate a clue. Future package authoring and AW-251 must
  preserve no-clue runtime behavior while remaining schema-valid.
- `deflection_tendency` is map-shaped, while current authoring declarations are
  scalar. AW-251 must resolve the structured-output representation without
  weakening validation.
- Narrator commentary could be mistaken for game authority unless runtime tests
  prove AI never decides truth, scoring, votes, signals, or outcomes.

**Unknowns**:

- Final narrator copy for each diegetic wrapper remains human-authored unless
  explicitly delegated.
- The exact point schedule belongs to AW-251.
- The final package lifecycle target belongs to a future package and promotion
  task.

---

# Open Questions

- Should the mini-game authoring schema grow an explicit non-clue fallback mode,
  or should non-clue games keep a neutral schema-valid `clue_fallback` record?
- Should structured behavioral outputs become first-class authoring schema in
  AW-251, or should map-shaped signals remain event-payload-only in v1?
