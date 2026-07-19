# AW-283: Suspect Answer Generation And Contradiction Detection

**Milestone / Epic:** M5 / M5-I
**Size:** L
**Status:** Planned

## Plain-English Summary

Generate suspect answers to resolved question intents through the knowledge-constrained dialogue pipeline (truthful answers from knowledge state; lies only where case resolution authorized them), record every answer as a claim with provenance, and detect contradictions deterministically (claim ledger versus knowledge state, evidence, and prior claims) so players can flag catches for points.

## Why This Matters

This is the platform's headline primitive made visible: suspects remember what they said, and catching a lie is a provenance query. It builds directly on the live-loop AI character dialogue work (spec 0071 / PR #225) and the Daily Case contradiction-ledger design (AW-235 lineage).

## Player Impact

Suspects that hold up under cross-examination; catches that feel earned, never arbitrary.

## Business Value

The differentiated mechanic no competitor ships; also the labeled continuity data source for AW-272 evals.

## Technical Scope

- Answer generation path: mandatory pre-generation knowledge query, behavior profile assembly (AW-211), routing per task type and quality tier, prompt caching of case context.
- Lie execution: authorized lies render in dialogue while ground truth stays intact in the knowledge graph; lie claims are marked internally, never exposed to players before the reveal.
- Claim ledger: every answer stored with speaker, asker, round, beat, and referenced facts.
- Deterministic contradiction detection: player flags a suspect statement; engine checks claim-versus-claim and claim-versus-evidence; confirmed catches emit scoring events; false flags emit penalty events.
- Latency budget: answer generation fast enough for a TV moment (fast-tier routing; measure and record p95).

## Human Collaboration Contract

**Interaction profile:** Creative collaboration.

**Founder input:** Suspect-answer tone, lie readability, contradiction fairness,
acceptable latency trade-offs, representative exchanges, and success
definition.

**Required phases:** Begin with focused discovery before locking answer behavior.
Confirm a short behavior brief, then present representative truthful answers,
authorized lies, contradiction cases, and fairness edge cases before full
implementation. For each artifact, explain what it represents, the assumptions
it tests, how to review it, and what needs founder attention. Offer bounded
options and a recommendation when a choice remains, then ask one interactive
question at a time.

**Gates:** Pause for explicit direction after discovery, answer and lie samples,
contradiction and fairness cases, and the implemented thin slice. Research and
reversible preparation may continue while the founder is unavailable, but no
subjective content choice or full implementation may proceed.

**Evidence:** Preserve discovery answers, samples and review instructions,
options, recommendation, founder feedback, explicit checkpoint approvals,
dates, and owner actions.

## Acceptance Criteria

- [ ] Suspect answers never reference facts outside the suspect's knowledge state (AW-272 eval batch reports zero leaks on a clean seed).
- [ ] A seeded authorized lie is catchable: the contradicting evidence exists and a flag on it confirms deterministically.
- [ ] Flags on consistent statements reject deterministically (false-positive guard).
- [ ] Claim provenance is queryable per session (feeds the reveal accounting).
- [ ] Answer-generation p95 latency recorded in telemetry.

## Tests/Verification

- `pytest engine/tests/` contradiction and claim-ledger tests pass.
- AW-272 continuity eval batch runs against a Couch Race synthetic batch.

## Dependencies

- AW-281, AW-282
- AW-287 (Leverage advantages/sabotages — contradiction-catch and answer
  behavior varies by active Leverage effect per the AW-283 discovery record)
- Spec 0071 / PR #225 live-loop AI character dialogue
- AW-212 knowledge-constrained dialogue pipeline; AW-272 eval suite

## Related design context

- [Nightcap Leverage advantages and sabotages design](../../product/nightcap-leverage-advantages-sabotages.md) is a proposed, design-only catalog. It is visible here for context but is not an AW-283 implementation dependency or authorization.

## Must Not Do

- Do not use a model call to judge whether a contradiction is real (deterministic only; the post-generation classifier is a logged open question).
- Do not expose lie markers or truth values in any player-facing event before the reveal.
- Do not route answer generation to frontier-tier models by default (cost policy).

## Architecture References

- `docs/architecture/04-knowledge-graph.md`, `docs/architecture/07-character-behavior.md`
- `docs/story-bibles/daily-case.md` (shared contradiction-ledger design spine)

## Playtest Relevance

Direct: answer quality and catch fairness are the rehearsal's central fun questions.
