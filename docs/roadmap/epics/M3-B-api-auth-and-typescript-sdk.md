# M3-B: API, Auth, And TypeScript SDK

**Milestone:** M3  
**Status:** Planned

## Plain-English Summary

Expose session, character, knowledge, and event flows through thin API handlers and a typed SDK.

## Why This Matters

This epic is part of the documented path from M1 complete to M6 first qualifying Nightcap playtests. Its scope is grounded in `docs/architecture/09-developer-api.md` and the milestone exit gates in `docs/roadmap/00-overview.md`.

## Player Impact

The player impact is that Nightcap moves closer to a coherent, safe, private, measurable play experience for real groups.

## Business Value

This work protects the H1 proof path: build the platform foundation, prove it through Nightcap, and avoid premature external-developer or dashboard polish scope.

## Technical Scope

The technical scope is limited to the tasks listed below and the architecture references named in those task files.

## Tasks

- [AW-217: Session Lifecycle API And Auth](../tasks/AW-217-session-lifecycle-api-and-auth.md)
- [AW-218: Character Input And Knowledge Endpoints](../tasks/AW-218-character-input-and-knowledge-endpoints.md)
- [AW-219: TypeScript SDK Event And Input Client](../tasks/AW-219-typescript-sdk-event-and-input-client.md)

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

- docs/architecture/09-developer-api.md
- `docs/roadmap/00-overview.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This epic contributes directly to the gated progression from backend validation to real-device rehearsal to first qualifying outside-group sessions.
