# M4-C: Nightcap Player Device Experience

**Milestone:** M4  
**Status:** Planned

## Plain-English Summary

Build player join, private event, character, and input flows on player devices.

## Why This Matters

This epic is part of the documented path from M1 complete to M6 first qualifying Nightcap playtests. Its scope is grounded in `docs/prd/02-requirements.md Player experience` and the milestone exit gates in `docs/roadmap/00-overview.md`.

## Player Impact

The player impact is that Nightcap moves closer to a coherent, safe, private, measurable play experience for real groups.

## Business Value

This work protects the H1 proof path: build the platform foundation, prove it through Nightcap, and avoid premature external-developer or dashboard polish scope.

## Technical Scope

The technical scope is limited to the tasks listed below and the architecture references named in those task files.

## Tasks

- [AW-228: Player Join Flow Under 30 Seconds](../tasks/AW-228-player-join-flow-under-30-seconds.md)
- [AW-229: Player Private Event And Input Flow](../tasks/AW-229-player-private-event-and-input-flow.md)

## Epic Exit Criteria

- All child tasks satisfy their acceptance criteria.
- The milestone exit gate remains consistent with `docs/roadmap/00-overview.md`.
- Any open decision is explicitly recorded before implementation proceeds.

## Dependencies

- Parent milestone: M4
- Relevant prior milestone work must be complete before implementation begins.

## Must Not Do

- Do not duplicate closed M1 work.
- Do not bypass Arcwright architecture principles in `AGENTS.md`.
- Do not turn Nightcap-specific requirements into platform assumptions.

## Architecture References

- docs/prd/02-requirements.md Player experience
- `docs/roadmap/00-overview.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This epic contributes directly to the gated progression from backend validation to real-device rehearsal to first qualifying outside-group sessions.
