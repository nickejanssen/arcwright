# M5-D: Visual Storyworld Phase 1 Inspection

**Milestone:** M5  
**Status:** Planned

## Plain-English Summary

Ship all four read-only inspection surfaces required for H1.

## Why This Matters

This epic is part of the documented path from M1 complete to M6 first qualifying Nightcap playtests. Its scope is grounded in `docs/prd/03-scope.md Visual Storyworld Roadmap` and the milestone exit gates in `docs/roadmap/00-overview.md`.

## Player Impact

The player impact is that Nightcap moves closer to a coherent, safe, private, measurable play experience for real groups.

## Business Value

This work protects the H1 proof path: build the platform foundation, prove it through Nightcap, and avoid premature external-developer or dashboard polish scope.

## Technical Scope

The technical scope is limited to the tasks listed below and the architecture references named in those task files.

## Tasks

- [AW-236: Live Knowledge Graph Inspection](../tasks/AW-236-live-knowledge-graph-inspection.md)
- [AW-237: Read-Only Arc Structure Inspection](../tasks/AW-237-read-only-arc-structure-inspection.md)
- [AW-238: Live Event Stream Inspection](../tasks/AW-238-live-event-stream-inspection.md)
- [AW-239: Character State Inspection](../tasks/AW-239-character-state-inspection.md)

## Epic Exit Criteria

- All child tasks satisfy their acceptance criteria.
- The milestone exit gate remains consistent with `docs/roadmap/00-overview.md`.
- Any open decision is explicitly recorded before implementation proceeds.

## Dependencies

- Parent milestone: M5
- Relevant prior milestone work must be complete before implementation begins.

## Must Not Do

- Do not duplicate closed M1 work.
- Do not bypass Arcwright architecture principles in `AGENTS.md`.
- Do not turn Nightcap-specific requirements into platform assumptions.

## Architecture References

- docs/prd/03-scope.md Visual Storyworld Roadmap
- `docs/roadmap/00-overview.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This epic contributes directly to the gated progression from backend validation to real-device rehearsal to first qualifying outside-group sessions.
