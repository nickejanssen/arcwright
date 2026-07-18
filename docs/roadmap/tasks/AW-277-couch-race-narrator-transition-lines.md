# AW-277: Couch Race Narrator Transition Lines

**Milestone / Epic:** M5 / M5-I
**Size:** M
**Status:** Planned

## Plain-English Summary

Compose the cold open and narrator transitions for the six-beat Couch Race arc
from resolved session state and emit them as structured content events.

## Why This Matters

Beat transitions currently risk feeling like state changes instead of a staged
mystery hosted by a consistent narrator.

## Player Impact

Players understand the current beat, feel its dramatic turn, and know where to
look without reading system-like status text.

## Business Value

The narrator is a visible product-quality signal and a high-leverage source of
personalization perception.

## Technical Scope

- Target The Pour cold open and transitions into The Scene, The Grill, The
  Twist, Last Call, and The Truth.
- Compose from already-resolved beat state, case context, arc voice, and
  authorial intent. Generation cannot decide or mutate session state.
- Emit shared-audience structured content events only after deterministic
  transition resolution.
- Populate D-070 voice, animation, lighting, and pause hints. Do not put TV or
  phone rendering logic in the engine.
- Exclude private case truth and knowledge that the shared audience may not
  receive.

## Human Collaboration Contract

**Interaction profile:** Creative collaboration.

**Discovery:** Begin with the founder's open-ended goals, references, taste,
audience, constraints, and success definition. Ask one focused question at a
time.

**Directions:** Present 2 to 3 explained narrator approaches with expert advice
and a recommendation. Pause to lock one direction.

**Intermediate artifacts:** Present representative transition samples in
six-beat context plus failure examples. Explain what each sample is, where it
fits, what is fixed or open, what to inspect, how to review it, known limits,
and the exact decision needed.

**Implementation gates:** Pause after direction selection, sample review,
agreed implementation batches, and final sign-off.

**Evidence:** Tie every approval to the named sample set or version and date.

## Acceptance Criteria

- [ ] The cold open and every beat transition emit narrator `content_text` from
  resolved state.
- [ ] Shared events contain no private or unresolved case truth.
- [ ] D-070 presentation hints are populated.
- [ ] Knowledge, safety, and provider-agnostic routing gates remain active.
- [ ] Founder-approved representative samples satisfy the selected direction.

## Tests/Verification

- Synthetic event-dump coverage for all six beats.
- Tests prove generation occurs after deterministic transition resolution.
- Content review covers selected samples and named failure examples.

## Dependencies

- AW-276
- AW-281
- `docs/story-bibles/nightcap-couch-race.md`

## Must Not Do

- Do not let generated narration choose the next beat or case truth.
- Do not leak private evidence on a shared audience event.
- Do not hardcode surface rendering in the engine.

## Architecture References

- `docs/architecture/03-arc-execution.md`
- `docs/architecture/08-event-system.md`
- D-069, D-070, and D-071

## Playtest Relevance

Provides the staged narrative spine observed during the Couch Race rehearsal.
