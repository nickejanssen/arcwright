# AW-280: Couch Race Clue Release Content

**Milestone / Epic:** M5 / M5-I
**Size:** M
**Status:** Planned

## Plain-English Summary

Compose and release fair Couch Race clue content from deterministic case truth,
with provenance, audience targeting, and evidence-to-intent unlock semantics.

## Why This Matters

Clues power both the mystery and the interrogation strategy. They must be
specific, fair, sayable aloud, and connected to sharper question choices.

## Player Impact

Evidence gives players concrete reasons to suspect or clear someone and opens
meaningful new interrogation options.

## Business Value

Fair, variable clue content supports repeatable case generation without
weakening player trust.

## Technical Scope

- Target releases in The Scene, The Grill, The Twist, and Last Call according
  to resolved beat, mini-game, and pacing gates.
- Compose language from the deterministic clue web, target or exoneration
  direction, provenance, authorized red herrings, and audience assignment.
- Preserve private, split, group, and targeted audience rules through existing
  event filtering.
- Emit D-070 presentation hints appropriate to the declared narrative moment,
  without surface-specific engine logic.
- Attach evidence-to-intent unlock metadata resolved by the interrogation
  system. Generation cannot invent an unlock or change clue truth.

## Human Collaboration Contract

**Interaction profile:** Creative collaboration.

**Discovery:** Begin with the founder's open-ended clue goals, references,
tone, clarity and fairness expectations, constraints, and success definition.
Ask one focused question at a time.

**Directions:** Present 2 to 3 explained clue-writing approaches with expert
advice and a recommendation. Pause to lock one direction.

**Intermediate artifacts:** Present representative clue samples in six-beat
context plus failure examples. Explain what each sample is, where it fits, what
is fixed or open, what to inspect, how to review it, known limits, and the
exact decision needed.

**Implementation gates:** Pause after direction selection, sample review,
agreed implementation batches, and final sign-off.

**Evidence:** Tie every approval to the named sample set or version and date.

## Acceptance Criteria

- [ ] Every clue points toward or away from a specific suspect and retains
  provenance to resolved case truth.
- [ ] False signals remain deterministically falsifiable after the reveal.
- [ ] Private, split, group, and targeted delivery pass audience filtering.
- [ ] Evidence unlocks only the interrogation intents authorized by resolved
  state.
- [ ] D-070 presentation hints are present, and founder-approved samples pass
  clarity, sayability, world-detail, and fairness review.

## Tests/Verification

- Seeded cases compare emitted clue payloads with the resolved clue web.
- Privacy tests cover every delivery type.
- Content review covers implicating, exonerating, private, and red-herring
  samples plus named failure examples.

## Dependencies

- AW-276
- AW-281
- AW-282
- AW-251

## Must Not Do

- Do not let generation decide clue truth, target, provenance, or unlocks.
- Do not emit private evidence to the shared audience.
- Do not create filler clues without investigative value.

## Architecture References

- `docs/architecture/03-arc-execution.md`
- `docs/architecture/04-knowledge-graph.md`
- `docs/architecture/08-event-system.md`
- D-069, D-070, and D-071

## Playtest Relevance

Makes clue fairness, asymmetry, and interrogation payoff observable in the
Couch Race rehearsal.
