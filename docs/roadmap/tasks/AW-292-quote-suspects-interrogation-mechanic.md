# AW-292: Quote-Suspects Interrogation Mechanic

**Milestone / Epic:** M5 / M5-I
**Size:** M
**Status:** Planned — GATED on paper-test validation (D-091)

## Plain-English Summary

Let a player quote one suspect's recorded claim into another suspect's
interrogation ("Julian says you were in the study"), and have the second
suspect react within their knowledge state — deny, fluster, or contradict.
The strongest available demonstration of the platform's headline
primitive (suspects remember what was said; catching a lie is a
provenance query), turned into a gameplay verb.

## Why This Matters

Identified as the highest value-per-effort interrogation mechanic
(`interrogation-experience-review.md` G2). It is the classic
detective-fiction move and the clearest "only Arcwright can do this"
moment — a contradiction the whole room witnesses, generated from real
knowledge state rather than scripted.

## Gate (do not start until cleared)

**This task is greenlit only after the interrogation paper test
(`docs/design/authoring/interrogation-paper-test.md`, experiment E3)
validates that quoting is the payoff moment (D-091).** If the paper test
shows it lands, build. If not, redesign or drop. Do not build on
assumption.

## Player Impact

A player can weaponise what one suspect said against another, live, and
the room watches a lie collapse in real time.

## Business Value

The most differentiated moment in the product and the most direct proof
of the knowledge-graph primitive as gameplay — the demo that sells the
platform.

## Technical Scope

- Add an interrogation option/target that references a recorded claim
  (the claim ledger already exists — AW-283, ADR-0016; `InteractionTarget`
  already accepts entities beyond characters — AW-282). Prefer reusing
  the shipped claim/interaction infrastructure over new schema.
- On resolution, the quoted claim enters the target suspect's answer
  generation as context, constrained by the mandatory pre-generation
  knowledge-state query (never let the suspect know something outside
  their state).
- The reaction is deterministic in *outcome* (does this create a
  contradiction the ledger records?), generated only in *language*.
- Emit the reaction with D-070 presentation hints so the squirm clears
  the D-090 quality gate.

## Human Collaboration Contract

**Interaction profile:** Creative collaboration (the mechanic's feel)
plus independent execution. Founder reviews the paper-test evidence
before build (the gate), and the reaction-staging samples during build.

## Acceptance Criteria

- [ ] Paper-test E3 evidence recorded and founder-greenlit before build.
- [ ] A player can quote a recorded claim from suspect A into suspect
  B's interrogation.
- [ ] Suspect B's reaction is constrained by B's knowledge state
  (mandatory pre-generation query; never leaks outside-state facts).
- [ ] Any resulting contradiction is recorded in the claim ledger with
  provenance (reuses AW-283 infrastructure).
- [ ] The reaction renders through D-070 hints and clears the D-090
  catch/squirm quality gate.
- [ ] No game-specific vocabulary leaks into engine/ generic interaction
  or knowledge APIs.

## Tests/Verification

- Knowledge-state test: quoting a claim never makes B assert an
  outside-state fact.
- Provenance test: a quote-induced contradiction is ledger-recorded.
- Determinism test: whether a quote creates a contradiction is a
  deterministic function of resolved state, not of generation.

## Dependencies

- Paper-test validation (D-091) — the gate
- AW-282 (interaction targets), AW-283 (claim ledger, ADR-0016)
- AW-285 (rendering — the squirm), AW-291 (narrator resolver, adjacent)
- `docs/design/authoring/interrogation-experience-review.md` (G2)
- `docs/design/authoring/couch-race-competition-model.md`

## Must Not Do

- Do not start before the paper-test gate clears.
- Do not let a suspect reference knowledge outside their state.
- Do not let AI decide whether a contradiction exists — that is
  deterministic ledger logic.
- Do not name the mechanic or its schema after Nightcap (platform-clean).
