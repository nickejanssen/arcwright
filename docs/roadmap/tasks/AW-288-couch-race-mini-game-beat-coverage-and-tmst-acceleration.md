# AW-288: Couch Race Mini-Game Beat Coverage And Tell Me Something True Acceleration

**Milestone / Epic:** M5 / M5-I
**Size:** M
**Status:** Planned

## Plain-English Summary

Give the Couch Race arc mini-game coverage in more of its six beats (today
only Scene and Twist have one; Grill, the longest beat, has none), and pull
Tell Me Something True forward from its Rehearsal 2 target (M5-F, D-064) into
Rehearsal 1, so the retargeted rehearsal ships with three mini-games instead
of two.

## Why This Matters

Surfaced during AW-284 discovery: the founder's product vision for Couch
Race is mini-games "throughout the game, like Mario Party," but the shipped
`nightcap/couch-race.arc.json` only wires mini-games into 2 of 6 beats.
D-079 records the founder's explicit direction to close part of that gap
before Rehearsal 1 rather than waiting for Rehearsal 2.

## Player Impact

More variety and more frequent pacing breaks across a session, instead of
two mini-games separated by long stretches of pure interrogation.

## Business Value

A session that plays closer to "Mario Party energy" is the stronger
Rehearsal 1 proof point for the founder's own product thesis, and it front-
loads a real test of Tell Me Something True's 4-phase shared-display/private-
device flow before Rehearsal 2's larger human-test investment.

## Technical Scope

- Add at least one mini-game slot to a beat that currently has none (Grill is
  the leading candidate: it is the longest beat and the one the founder's
  gap observation was most about), using the existing `mini_games` binding
  shape already present at Scene and Twist in `nightcap/couch-race.arc.json`.
- Bind Tell Me Something True (package `social-truth-bluff`) into the Couch
  Race arc at a founder-chosen beat. Correction to this task's own initial
  framing: TMST is not merely spec-approved, its package, runtime, API/SDK,
  and web rendering are already implemented and marked Complete (AW-262
  through AW-265) -- only AW-266 (running it as Rehearsal 2 with real
  humans) remains open. This task is therefore an arc-binding and pacing
  task, not new TMST engineering; do not re-derive design decisions M5-F
  already settled, and do not duplicate AW-266's real-human test, which
  still runs separately per M5-F's own scope.
- Update `docs/roadmap/epics/M5-F-tell-me-something-true-social-opener.md`
  to note that TMST's Couch Race integration is no longer exclusively a
  Rehearsal 2 concern per D-079 -- do not delete or rewrite that epic's own
  scope, add a superseding note pointing here.
- Update AW-286's Dependencies to include this task; the retargeted
  Rehearsal 1 does not begin until this task's acceptance criteria pass.

## Human Collaboration Contract

**Interaction profile:** Creative collaboration.

**Founder input:** Which beat(s) receive the new slot, TMST's placement in
the beat sequence, and confirmation that pacing still fits the 20-40 minute
session target with three mini-games instead of two.

**Required phases:** Present the proposed beat placement and updated pacing
estimate before wiring it into the arc; confirm before implementation.

**Gates:** Pause for explicit founder direction on beat placement before
implementation; pause again before this task is marked complete and used to
gate AW-286.

**Evidence:** Preserve the placement proposal, founder feedback, approved
placement, and pacing-estimate confirmation.

## Acceptance Criteria

- [ ] At least one additional beat (recommend Grill) has a bound mini-game
  in `nightcap/couch-race.arc.json`.
- [ ] Tell Me Something True is bound into the Couch Race arc and passes
  AW-249's schema validator.
- [ ] Updated session pacing (three-plus mini-games) still fits the 20-40
  minute session target from the story bible; recorded, not assumed.
- [ ] M5-F epic file carries a note pointing to D-079 and this task.
- [ ] AW-286's Dependencies section lists this task.

## Tests/Verification

- AW-249 schema validator against the updated arc file.
- Headless harness run confirms all beats, including the new mini-game
  slot(s), are reachable at player counts 2 and 8.

## Dependencies

- D-079 (founder direction to reopen D-064 for TMST)
- AW-262/AW-263/AW-264/AW-265 (Tell Me Something True package, runtime,
  API/SDK, and web rendering -- all Complete)
- `nightcap/couch-race.arc.json` (AW-281, shipped)

## Must Not Do

- Do not re-litigate Tell Me Something True's own design (spec 0061 is
  already approved); this task integrates it into Couch Race, it does not
  redesign it.
- Do not silently drop M5-F's own Rehearsal 2 scope -- TMST still needs its
  full package/runtime/API/SDK/web implementation per M5-F; this task only
  changes which rehearsal first exercises it in Couch Race.
- Do not add mini-game slots to every beat reflexively; each addition needs
  a stated pacing reason.

## Architecture References

- `docs/story-bibles/nightcap-couch-race.md`
- `docs/decisions/0009-mini-game-runtime-boundary.md`
- `docs/product/decisions-log.csv` (D-064, D-079)
- `docs/roadmap/epics/M5-F-tell-me-something-true-social-opener.md`

## Playtest Relevance

Direct: this is what Rehearsal 1 will actually run.
