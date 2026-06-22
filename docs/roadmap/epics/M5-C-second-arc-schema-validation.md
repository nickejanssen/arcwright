# M5-C: Second Arc Schema And Executable Follow-Through

**Milestone:** M5  
**Status:** Planned

## Plain-English Summary

Design Daily Case, a non-Nightcap solo daily interrogation arc, to prove platform-clean abstractions, then queue a post-M6 minimal executable product that proves platform reuse by execution.

## Why This Matters

This epic is part of the documented path from M1 complete to M6 first qualifying Nightcap playtests. Its scope is grounded in `docs/architecture/14-architecture-validation.md` and the milestone exit gates in `docs/roadmap/00-overview.md`.

## Player Impact

The player impact is that Nightcap moves closer to a coherent, safe, private, measurable play experience for real groups.

## Business Value

This work protects the H1 proof path: build the platform foundation, prove it through Nightcap, and define the smallest second executable arc that makes Arcwright's cross-session memory wedge visible without bloating current scope.

## Technical Scope

The technical scope is limited to the tasks listed below and the architecture references named in those task files. For M5-C, the canonical second arc is Daily Case: a solo, asynchronous, week-long suspect interrogation experience.

## Tasks

- [AW-256: Remove game-specific beat ID hardcode from arc transition gate](../tasks/AW-256-remove-beat-id-hardcode-from-arc-transition-gate.md)
- [AW-235: Second Arc Schema Design](../tasks/AW-235-second-arc-schema-design.md)
- [AW-245: Second Arc Minimal Executable Product](../tasks/AW-245-second-arc-minimal-executable-product.md) (post-M6)

## Acceptance Criteria

- All child tasks satisfy their acceptance criteria.
- Daily Case is documented as the canonical second-arc target for M5-C and post-M6 executable follow-through.
- The milestone exit gate remains consistent with `docs/roadmap/00-overview.md`.
- Any open decision is explicitly recorded before implementation proceeds.

## Tests/Verification

- Verify every child task is complete and has evidence linked from its task issue.
- Verify the parent milestone exit gate still matches `docs/roadmap/00-overview.md`.
- Verify any open decision named by this epic is recorded before dependent implementation starts.

## Dependencies

- Parent milestone: M5
- Relevant prior milestone work must be complete before implementation begins.

## Must Not Do

- Do not duplicate closed M1 work.
- Do not bypass Arcwright architecture principles in `AGENTS.md`.
- Do not turn Nightcap-specific requirements into platform assumptions.

## Architecture References

- docs/architecture/14-architecture-validation.md
- `docs/roadmap/00-overview.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This epic contributes directly to the gated progression from backend validation to real-device rehearsal to first qualifying outside-group sessions.
