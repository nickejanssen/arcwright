# M5-F: Tell Me Something True Social Opener Implementation

**Milestone:** M5
**Status:** Planned

## Plain-English Summary

Implement the full Tell Me Something True social-opener mini-game across
package, runtime, API, SDK, and web layers; then run Rehearsal 2 with real
humans.

## Why This Matters

Spec 0061 (AW-258) is approved but unimplemented. D-064 sequences TMST as
Rehearsal 2 (after the Rehearsal 1 promotion-only path closes M4). This
epic carries that sequencing into execution.

## Player Impact

A polished social opener that runs in beats 1-3 of a Nightcap session,
giving players a low-stakes warm-up before the murder mystery proper begins.

## Business Value

Validates the platform's mini-game extensibility under a net-new mechanic
type (`social-truth-bluff`) and a 4-phase shared-display plus
private-device flow that exercises the API event filtering and privacy
contract more thoroughly than the single-phase Rehearsal 1 mini-games do.

## Technical Scope

The technical scope is limited to the tasks listed below and the
architecture references named in those task files.

## Tasks

- [AW-262: TMST Package Authoring and Schema Resolution](../tasks/AW-262-tmst-package-authoring-and-schema-resolution.md)
- [AW-263: TMST Runtime - social-truth-bluff Mechanic](../tasks/AW-263-tmst-runtime-social-truth-bluff-mechanic.md)
- [AW-264: TMST API, Events, and SDK](../tasks/AW-264-tmst-api-events-and-sdk.md)
- [AW-265: TMST Web Rendering for Four Phases](../tasks/AW-265-tmst-web-rendering-four-phases.md)
- [AW-266: Rehearsal 2 - TMST Real-Human Session](../tasks/AW-266-rehearsal-2-tmst-real-human-session.md)

## Acceptance Criteria

- All child tasks satisfy their acceptance criteria.
- TMST runs end-to-end on real devices with at least 4 humans.
- Privacy contract held under the 4-phase flow.

## Tests/Verification

- Verify every child task is complete and has evidence linked from its task
  issue.
- Verify Rehearsal 2 (AW-266) ran and its blockers are triaged.

## Dependencies

- Parent milestone: M5
- AW-259 (Rehearsal 1) closed (so Rehearsal 1 blocker fixes are folded
  back before Rehearsal 2)
- AW-258 spec 0061 approved (already)

## Must Not Do

- Do not skip any of the four implementation layers (package, runtime,
  API/SDK, web).
- Do not wire behavioral signals into killer assignment or cross-session
  behavior (v1.1 work per spec 0061).
- Do not run Rehearsal 2 with fixtures only.

## Architecture References

- `docs/specs/0061-aw-258-tell-me-something-true.md`
- `docs/decisions/0009-mini-game-runtime-boundary.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

Adds a second real-human rehearsal data point and validates a richer
mini-game surface than Rehearsal 1.
