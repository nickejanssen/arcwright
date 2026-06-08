# M3-D: Telemetry And Full Simulation Harness

**Milestone:** M3  
**Status:** Planned

## Plain-English Summary

Log required signals and prove the full API path through repeated offline sessions.

## Why This Matters

This epic is part of the documented path from M1 complete to M6 first qualifying Nightcap playtests. Its scope is grounded in `docs/architecture/11-telemetry.md` and the milestone exit gates in `docs/roadmap/00-overview.md`.

## Player Impact

The player impact is that Nightcap moves closer to a coherent, safe, private, measurable play experience for real groups.

## Business Value

This work protects the H1 proof path: build the platform foundation, prove it through Nightcap, and avoid premature external-developer or dashboard polish scope.

## Technical Scope

The technical scope is limited to the tasks listed below and the architecture references named in those task files.

## Tasks

- [AW-222: Five MVP Telemetry Signals](../tasks/AW-222-five-mvp-telemetry-signals.md)
- [AW-223: Cost And Usage Summary](../tasks/AW-223-cost-and-usage-summary.md)
- [AW-224: Full API Batch Harness](../tasks/AW-224-full-api-batch-harness.md)

## Epic Exit Criteria

- All child tasks satisfy their acceptance criteria.
- The milestone exit gate remains consistent with `docs/roadmap/00-overview.md`.
- Any open decision is explicitly recorded before implementation proceeds.

## Dependencies

- Parent milestone: M3
- Relevant prior milestone work must be complete before implementation begins.

## Must Not Do

- Do not duplicate closed M1 work.
- Do not bypass Arcwright architecture principles in `AGENTS.md`.
- Do not turn Nightcap-specific requirements into platform assumptions.

## Architecture References

- docs/architecture/11-telemetry.md
- `docs/roadmap/00-overview.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This epic contributes directly to the gated progression from backend validation to real-device rehearsal to first qualifying outside-group sessions.
