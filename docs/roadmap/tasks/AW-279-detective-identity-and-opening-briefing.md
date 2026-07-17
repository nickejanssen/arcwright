# AW-279: Detective Identity And Opening Briefing

**Milestone / Epic:** M5 / M5-I
**Size:** M
**Status:** Planned

## Plain-English Summary

Deliver each player a light detective identity and opening briefing for The
Pour without adding hidden information or performance burden.

## Why This Matters

Couch Race promises immediate play. A small amount of identity flavor helps
the narrator address players and gives the scoreboard personality without
turning onboarding into role study.

## Player Impact

Players receive a memorable name and investigative flavor while remaining free
to play as themselves.

## Business Value

Fast, low-friction onboarding protects the two-player floor and short session
loop while preserving personalization.

## Technical Scope

- Target Beat 1, The Pour, before the narrator frames the race.
- Resolve a light detective name and flavor from approved arc content and
  session inputs.
- Deliver the identity privately to the assigned player phone. Only the name
  and public flavor may be used for shared narrator address or scoreboards.
- Carry D-070 phone-reveal hints without embedding phone rendering logic in the
  engine.
- Include no secret, hidden assignment, required performance, or case-truth
  advantage.

## Human Collaboration Contract

**Interaction profile:** Creative collaboration.

**Discovery:** Begin with the founder's open-ended identity and briefing goals,
references, tone, onboarding constraints, and success definition. Ask one
focused question at a time.

**Directions:** Present 2 to 3 explained approaches with expert advice and a
recommendation. Pause to lock one direction.

**Intermediate artifacts:** Present representative identity and briefing
samples in six-beat context plus failure examples. Explain what each sample is,
where it fits, what is fixed or open, what to inspect, how to review it, known
limits, and the exact decision needed.

**Implementation gates:** Pause after direction selection, sample review,
agreed implementation batches, and final sign-off.

**Evidence:** Tie every approval to the named sample set or version and date.

## Acceptance Criteria

- [ ] Every player receives one private detective identity during The Pour.
- [ ] Identity content contains no private case truth, hidden assignment, or
  required acting instruction.
- [ ] Shared surfaces receive only public name and flavor fields.
- [ ] D-070 presentation hints support a staged but fast phone reveal.
- [ ] Founder-approved samples pass clarity, tone, and low-burden review.

## Tests/Verification

- Privacy tests cover private delivery and public-field projection.
- Synthetic sessions cover the supported player-count range.
- Content review includes good samples and examples that create excess burden.

## Dependencies

- AW-276
- AW-281
- `docs/story-bibles/nightcap-couch-race.md`

## Must Not Do

- Do not assign players a hidden case role.
- Do not give one player privileged case truth through identity content.
- Do not require acting, memorization, or character performance.

## Architecture References

- `docs/architecture/07-character-behavior.md`
- `docs/architecture/08-event-system.md`
- D-069, D-070, and D-071

## Playtest Relevance

Tests whether personalized onboarding can remain clear and playable within one
minute.
