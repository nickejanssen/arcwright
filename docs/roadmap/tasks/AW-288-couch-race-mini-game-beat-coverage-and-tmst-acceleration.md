# AW-288: Tell Me Something True Couch Race Activation, Placement, And Pacing

**Milestone / Epic:** M5 / M5-I
**Size:** M
**Status:** Planned

## Plain-English Summary

Prepare Tell Me Something True for an approved Couch Race opportunity pool:
activate the already-built package for this host, validate its placement and
pacing role, and preserve its independent real-human rehearsal disposition.

## Why This Matters

Surfaced during AW-284 discovery: the founder's product vision for Couch
Race is mini-games "throughout the game, like Mario Party," but the shipped
`nightcap/couch-race.arc.json` only wires mini-games into 2 of 6 beats.
D-079 records the founder's explicit direction to close part of that gap
before Rehearsal 1 rather than waiting for Rehearsal 2.

## Player Impact

An approved social opener can enter Couch Race without treating it as a
mandatory or permanent beat binding.

## Business Value

This makes TMST available as a rotating, story-appropriate opportunity while
leaving the program's broader six-beat coverage and package certification to
the dedicated readiness program.

## Technical Scope

- Confirm the `social-truth-bluff` package's host registration, exact version,
  permitted opportunity role, and bounded result semantics for Couch Race.
- Present placement and pacing evidence for founder approval before binding it
  to a rotating opportunity pool. The host, not Arcwright, owns registration.
- Preserve AW-266 as a separate TMST real-human rehearsal decision. Do not
  infer that Couch Race evidence supersedes it.
- Update M5-F and AW-286 with this bounded relationship.

## Human Collaboration Contract

**Interaction profile:** Creative collaboration.

**Founder input:** TMST's opportunity role, placement constraints, and
confirmation that pacing fits the 20–40 minute session target.

**Required phases:** Present the proposed beat placement and updated pacing
estimate before wiring it into the arc; confirm before implementation.

**Gates:** Pause for explicit founder direction on beat placement before
implementation; pause again before this task is marked complete and used to
gate AW-286.

**Evidence:** Preserve the placement proposal, founder feedback, approved
placement, and pacing-estimate confirmation.

## Acceptance Criteria

- [ ] TMST has a certified exact package version and host registration for an
  approved Couch Race opportunity pool.
- [ ] TMST placement and session pacing are founder-approved and recorded;
  they fit the 20–40 minute target without creating a required story gate.
- [ ] M5-F epic file carries a note pointing to D-079 and this task.
- [ ] AW-286's Dependencies section lists this task.

## Tests/Verification

- Package certification and host-registration validation for the chosen
  `social-truth-bluff` version.
- Headless harness confirms the selected opportunity is reachable at player
  counts 2 and 8 without changing deterministic story progression.

## Dependencies

- D-079 (founder direction to reopen D-064 for TMST)
- AW-262/AW-263/AW-264/AW-265 (Tell Me Something True package, runtime,
  API/SDK, and web rendering -- all Complete)
- `nightcap/couch-race.arc.json` (AW-281, shipped)

## Must Not Do

- Do not re-litigate Tell Me Something True's own design (spec 0061 is
  already approved); this task integrates it into Couch Race, it does not
  redesign it.
- Do not treat Couch Race activation evidence as a replacement for AW-266's
  separate real-human TMST rehearsal disposition. That decision remains with
  the founder; this task does not reopen completed implementation work.
- Do not expand this task into coverage for every beat. The readiness program
  owns the six-opportunity architecture and other package work.

## Architecture References

- `docs/story-bibles/nightcap-couch-race.md`
- `docs/decisions/0009-mini-game-runtime-boundary.md`
- `docs/product/decisions-log.csv` (D-064, D-079)
- `docs/roadmap/epics/M5-F-tell-me-something-true-social-opener.md`

## Playtest Relevance

Direct: this is what Rehearsal 1 will actually run.
