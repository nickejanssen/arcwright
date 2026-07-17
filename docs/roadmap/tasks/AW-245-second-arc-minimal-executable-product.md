# AW-245: Second Arc Minimal Executable Product

**Milestone / Epic:** Post-M6 / M5-C follow-through
**Size:** L
**Status:** Planned after Nightcap M6 proof

## Plain-English Summary

Build Daily Case, the second arc schema from AW-235, as a minimal executable product after Nightcap M6 proof.

## Why This Matters

D-056 upgrades the M5 second arc deliverable from designed-only to executable follow-through sequenced after Nightcap M6 proof. This proves platform reuse by execution rather than assertion while protecting the Nightcap timeline.

## Player Impact

Players benefit when the platform claim is validated through a second real experience without delaying Nightcap's first proof sessions.

## Business Value

This task strengthens Arcwright's core platform claim: the engine can run more than one kind of authored arc, including Daily Case, a solo daily single-suspect interrogation game where the suspect remembers prior days through the knowledge graph.

## Technical Scope

Implement the minimal real product defined by the AW-235 Daily Case schema after M6 proof. Likely files affected depend on the selected schema and runtime surface.

## Human Collaboration Contract

**Interaction profile:** Independent execution.

**Why independent:** D-056, AW-235,
`docs/specs/0031-aw-245-second-arc-minimal-executable-product.md`, and the
post-M6 sequence constrain this implementation once its prerequisites are met.

**Required flow:** After normal plan approval and prerequisite proof, implement
the approved minimum product, explain how it demonstrates platform reuse, and
verify each documented boundary.

**Reclassification gate:** Stop and switch to Creative collaboration or
Decision interview before inventing new Daily Case direction, adding schema,
API, privacy, or telemetry scope, or changing the post-M6 sequence.

**Evidence:** Preserve plan approval, prerequisite evidence, spec references,
platform-reuse verification, test results, dates, and owner actions.

## Acceptance Criteria

- [ ] Implementation starts only after AW-244 records the H1 proof analysis and next-step decision.
- [ ] The executable product is based on the Daily Case schema designed in AW-235 and `docs/story-bibles/daily-case.md`.
- [ ] The implementation exercises platform reuse through arc execution, knowledge graph, event delivery, safety, routing, cost tracking, and telemetry where applicable.
- [ ] The implementation preserves Daily Case's core shape: one player, one suspect, one primary surface, cross-day memory, contradiction accumulation, and final accusation.
- [ ] The implementation does not require Nightcap-specific engine assumptions.
- [ ] Any new schema, API, privacy, or telemetry scope is backed by a dedicated approved spec before code work begins.

## Tests/Verification

- Run the smallest automated tests that prove the second arc runs through its intended loop or completion condition.
- Verify the implementation uses platform primitives rather than Nightcap-only paths.
- Verify no provider or model names are hardcoded outside approved routing files.

## Dependencies

- AW-235
- AW-244

## Likely Files Affected

TBD by the AW-235 schema and follow-up implementation spec.

## Must Not Do

- Do not start before Nightcap M6 proof and AW-244 analysis.
- Do not delay Nightcap M2-M6 work.
- Do not turn the working concept into v1 Nightcap scope.
- Do not hardcode secrets or API keys.

## Architecture References

- docs/product/decisions-log.csv D-056
- docs/architecture/14-architecture-validation.md
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task is post-proof platform validation. It is not required for Nightcap M6 qualifying sessions.
