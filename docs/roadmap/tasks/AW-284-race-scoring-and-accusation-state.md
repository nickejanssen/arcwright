# AW-284: Race Scoring And Accusation State

**Milestone / Epic:** M5 / M5-I
**Size:** M
**Status:** Planned

## Plain-English Summary

Build race scoring (evidence uncovered, contradictions caught, accusation accuracy weighted by earliness) and accusation state (private submissions, wrong-accusation lockout window with score penalty, first-correct triggers table-wide Last Call, countdown expiry) as deterministic session state.

## Why This Matters

Scoring is the competitive spine of Couch Race and the concrete expression of the competition dial (solo race in v1; structure must not preclude teams/co-op configurations later).

## Player Impact

Stakes every minute, no elimination ever, and an endgame that keeps the whole couch in play.

## Business Value

The scoreboard and superlatives are the replay hook ("run it back") that M6 measures.

## Technical Scope

- Scoring rules as arc-configurable deterministic state transitions emitting scoring events.
- Accusation submissions (suspect, optional motive/method bonus) as private inputs; lockout windows timed by session clock.
- First-correct-accusation transition: opens table-wide final lock-in, then forces beat transition to The Truth.
- Countdown-expiry transition to The Truth with case-wins outcome.
- Superlative computation at session end (Best Interrogator, Lie Detector, Most Confidently Wrong) from telemetry already captured.

## Human Collaboration Contract

**Interaction profile:** Creative collaboration.

**Founder input:** Desired competitive feel, risk tolerance, pacing, penalty and
reward expectations, representative endgames, and success definition.

**Required phases:** Begin with focused discovery before locking tuning. Confirm
a short scoring brief, then present representative scoring scenarios, endgame
walkthroughs, and tuning tables before implementing final values. Explain every
table and scenario in plain language, including how to review it, the assumptions
being tested, and which cells or outcomes need founder attention. Offer bounded
options and a recommendation, then ask one interactive question at a time.

**Gates:** Pause for explicit direction after discovery, scenario review, tuning
table review, and the implemented thin slice. Research and reversible
preparation may continue while the founder is unavailable, but no tuning choice
or full implementation may proceed.

**Evidence:** Preserve discovery answers, scenarios and review instructions,
options, recommendation, founder feedback, approved tuning table, explicit
checkpoint approvals, dates, and owner actions.

## Acceptance Criteria

- [ ] All win/end paths reachable in harness: first-correct then table lock-in; countdown expiry; all-players-locked-early.
- [ ] Wrong accusation applies lockout and penalty deterministically; no elimination state exists.
- [ ] Scores and superlatives reproducible under deterministic replay.
- [ ] Guarded transitions verified by configuration values after firing (StateChart silent-guard behavior).

## Tests/Verification

- `pytest engine/tests/` scoring and accusation state tests pass, covering every end path.

## Dependencies

- AW-281 (arc transitions), AW-283 (catch events feed scoring)

## Must Not Do

- Do not let AI adjust scores, weights, or accusation outcomes.
- Do not build team or co-op scoring in v1 (structure stays configurable; implementations deferred).
- Do not surface running score as raw numbers in engine events without presentation hints (D-070: scoreboard moments are staged).

## Architecture References

- `docs/architecture/03-arc-execution.md`
- `docs/story-bibles/nightcap-couch-race.md` Sections 8–9

## Playtest Relevance

Direct: whether the race feels alive is a primary fun-rubric observation.
