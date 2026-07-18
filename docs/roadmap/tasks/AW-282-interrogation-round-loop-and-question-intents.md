# AW-282: Interrogation Round Loop And Question Intents

**Milestone / Epic:** M5 / M5-I
**Size:** M
**Status:** Planned

## Plain-English Summary

Build the platform capability for structured player questioning of AI characters: round structure (character takes the stage, players privately select question intents, questions resolve in order), deterministic intent menus (baseline intents plus intents unlocked by held evidence), and per-beat question-token scarcity.

## Why This Matters

Interrogation is the Couch Race core loop and shared infrastructure with Daily Case's solo interrogation (D-034 wedge). It must land as a game-neutral platform capability.

## Player Impact

The moment-to-moment game: spend scarce questions well, hear answers with the room, work private tells.

## Business Value

Bounded question tokens bound per-session generation cost (M5 gross-margin gate).

## Technical Scope

- Engine-side round state machine: stage character, collect private intent selections, resolve in table order, emit answer events (public) and tell events (private to asker).
- Intent menu resolution: deterministic function of arc configuration, beat, and the player's held evidence. No model calls to build menus.
- Question-token accounting per player per beat, arc-configurable.
- Platform-clean naming: schemas describe structure (inquiry rounds, question intents, claim events), not Nightcap semantics (D-038/D-039).

## Human Collaboration Contract

**Interaction profile:** Creative collaboration.

**Founder input:** Desired interrogation feel, choice pressure, question-token
scarcity, representative player decisions, and success definition.

**Required phases:** Begin with focused discovery before finalizing interaction
behavior. Confirm a short experience brief, then present low-cost round-flow and
intent-menu scenarios before implementing the complete loop. For each artifact,
explain what it represents, the assumptions it tests, how to review it, and what
needs founder attention. Offer bounded options and a recommendation when a
choice remains, then ask one interactive question at a time.

**Gates:** Pause for explicit direction after discovery, representative round
scenarios, intent-menu scenarios, and the implemented thin slice. Research and
reversible preparation may continue while the founder is unavailable, but no
subjective interaction choice or full implementation may proceed.

**Evidence:** Preserve discovery answers, scenarios and review instructions,
options, recommendation, founder feedback, explicit checkpoint approvals,
dates, and owner actions.

## Acceptance Criteria

- [ ] A synthetic session runs interrogation rounds with intents resolving deterministically from evidence state.
- [ ] Public answers reach all session participants; tells reach only the asker (event audience filtering per AW-216).
- [ ] Token exhaustion blocks further questions and is arc-configurable.
- [ ] Daily Case can configure the same capability for one player, one suspect (design check recorded in spec, no Daily Case implementation).

## Tests/Verification

- `pytest engine/tests/` interrogation round tests pass, including audience-filtering leak tests.

## Dependencies

- AW-281 (arc and case resolution supply intents and characters)
- AW-215/AW-216 event system

## Must Not Do

- Do not accept free-text question input in v1.
- Do not put Nightcap-specific strings in engine schemas or module names.
- Do not let intent menus require model calls.

## Architecture References

- `docs/architecture/03-arc-execution.md`, `docs/architecture/08-event-system.md`
- `docs/story-bibles/nightcap-couch-race.md` Section 6

## Playtest Relevance

Direct: the rehearsal thin slice centers on this loop.
