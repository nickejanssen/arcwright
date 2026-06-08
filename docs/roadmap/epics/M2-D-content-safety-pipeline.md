# M2-D: Content Safety Pipeline

**Milestone:** M2  
**Status:** Planned

## Plain-English Summary

Add engine-layer safety before every generation path.

## Why This Matters

This epic is part of the documented path from M1 complete to M6 first qualifying Nightcap playtests. Its scope is grounded in `docs/architecture/10-content-safety.md` and the milestone exit gates in `docs/roadmap/00-overview.md`.

## Player Impact

The player impact is that Nightcap moves closer to a coherent, safe, private, measurable play experience for real groups.

## Business Value

This work protects the H1 proof path: build the platform foundation, prove it through Nightcap, and avoid premature external-developer or dashboard polish scope.

## Technical Scope

The technical scope is limited to the tasks listed below and the architecture references named in those task files.

## Tasks

- [AW-208: L1 Hard Stops](../tasks/AW-208-l1-hard-stops.md)
- [AW-209: L2 Pre-Generation Classification](../tasks/AW-209-l2-pre-generation-classification.md)
- [AW-210: L3 Policy Injection And Neutral Bridge](../tasks/AW-210-l3-policy-injection-and-neutral-bridge.md)

## Epic Exit Criteria

- All child tasks satisfy their acceptance criteria.
- The milestone exit gate remains consistent with `docs/roadmap/00-overview.md`.
- Any open decision is explicitly recorded before implementation proceeds.

## Dependencies

- Parent milestone: M2
- Relevant prior milestone work must be complete before implementation begins.

## Must Not Do

- Do not duplicate closed M1 work.
- Do not bypass Arcwright architecture principles in `AGENTS.md`.
- Do not turn Nightcap-specific requirements into platform assumptions.

## Architecture References

- docs/architecture/10-content-safety.md
- `docs/roadmap/00-overview.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This epic contributes directly to the gated progression from backend validation to real-device rehearsal to first qualifying outside-group sessions.
