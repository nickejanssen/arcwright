# AW-278: Couch Race Truth Sequence And Reveal Accounting

**Milestone / Epic:** M5 / M5-I
**Size:** M
**Status:** Planned

## Plain-English Summary

Compose The Truth as a shared reveal sequence from resolved case truth,
authorized lies, claim provenance, and deterministic player outcomes.

## Why This Matters

The reveal is the fairness contract. It must show why the case was solvable and
how the room's best catches and near misses connected to the truth.

## Player Impact

Players receive a satisfying explanation, see their investigation recognized,
and understand why each red herring or lie was fair.

## Business Value

A trustworthy reveal supports replay intent and distinguishes a coherent case
from disposable generated content.

## Technical Scope

- Target Beat 6, The Truth, after case and scoring outcomes are resolved.
- Compose from deterministic case truth, authorized lies, clue provenance,
  claim records, contradiction catches, accusations, and superlatives.
- Emit a shared-audience structured sequence with D-070 presentation hints.
- Keep private evidence private until the resolved reveal contract authorizes
  it for the shared audience.
- AI composes language only. It cannot determine guilt, evidence validity,
  scoring, or outcome.

## Human Collaboration Contract

**Interaction profile:** Creative collaboration.

**Discovery:** Begin with the founder's open-ended reveal goals, references,
tone, fairness expectations, constraints, and success definition. Ask one
focused question at a time.

**Directions:** Present 2 to 3 explained reveal approaches with expert advice
and a recommendation. Pause to lock one direction.

**Intermediate artifacts:** Present representative reveal samples in six-beat
context plus failure examples. Explain what each sample is, where it fits, what
is fixed or open, what to inspect, how to review it, known limits, and the
exact decision needed.

**Implementation gates:** Pause after direction selection, sample review,
agreed implementation batches, and final sign-off.

**Evidence:** Tie every approval to the named sample set or version and date.

## Acceptance Criteria

- [ ] The Truth reconstructs the resolved case without changing any fact or
  outcome.
- [ ] The sequence accounts for genuine clues, authorized lies, catches,
  accusations, and deterministic superlatives.
- [ ] Shared reveal events respect the privacy-release contract and carry
  D-070 presentation hints.
- [ ] Founder-approved samples make fairness legible and avoid scoreboard-only
  delivery.

## Tests/Verification

- Seeded cases prove the rendered reveal matches resolved truth and scores.
- Privacy tests prove evidence is shared only when reveal rules authorize it.
- Content review covers successful, unsolved, and mixed-catch sample cases.

## Dependencies

- AW-276
- AW-281
- AW-283
- AW-284

## Must Not Do

- Do not let generation infer or modify whodunit.
- Do not omit evidence that is required to explain case fairness.
- Do not expose private information before the reveal contract permits it.

## Architecture References

- `docs/architecture/03-arc-execution.md`
- `docs/architecture/04-knowledge-graph.md`
- `docs/architecture/08-event-system.md`
- D-069, D-070, and D-071

## Playtest Relevance

Makes reveal fairness and replay enthusiasm directly observable in rehearsal.
