# M4-D: Real-Device Privacy And Join Validation

**Milestone:** M4  
**Status:** Planned

## Plain-English Summary

Verify the complete real-device setup before any qualifying playtest.

## Why This Matters

This epic is part of the documented path from M1 complete to M6 first qualifying Nightcap playtests. Its scope is grounded in `docs/roadmap/milestones/M4-nightcap-experience-layer.md` and the milestone exit gates in `docs/roadmap/00-overview.md`.

## Player Impact

The player impact is that Nightcap moves closer to a coherent, safe, private, measurable play experience for real groups.

## Business Value

This work protects the H1 proof path: build the platform foundation, prove it through Nightcap, and avoid premature external-developer or dashboard polish scope.

## Technical Scope

The technical scope is limited to the tasks listed below and the architecture references named in those task files.

## Tasks

- [AW-230: Real-Device Privacy Matrix](../tasks/AW-230-real-device-privacy-matrix.md)
- [AW-231: M4 Real-Human Rehearsal](../tasks/AW-231-m4-real-human-rehearsal.md)

## Acceptance Criteria

- All child tasks satisfy their acceptance criteria.
- The milestone exit gate remains consistent with `docs/roadmap/00-overview.md`.
- Any open decision is explicitly recorded before implementation proceeds.

## Tests/Verification

- Verify every child task is complete and has evidence linked from its task issue.
- Verify the parent milestone exit gate still matches `docs/roadmap/00-overview.md`.
- Verify any open decision named by this epic is recorded before dependent implementation starts.

## Dependencies

- Parent milestone: M4
- Relevant prior milestone work must be complete before implementation begins.

## Must Not Do

- Do not duplicate closed M1 work.
- Do not bypass Arcwright architecture principles in `AGENTS.md`.
- Do not turn Nightcap-specific requirements into platform assumptions.

## Architecture References

- docs/roadmap/milestones/M4-nightcap-experience-layer.md
- `docs/roadmap/00-overview.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This epic contributes directly to the gated progression from backend validation to real-device rehearsal to first qualifying outside-group sessions.
