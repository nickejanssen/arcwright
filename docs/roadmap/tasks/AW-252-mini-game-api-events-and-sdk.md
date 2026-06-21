# AW-252: Mini-game API, Events, And TypeScript SDK

**Milestone / Epic:** M4 / M4-E
**Size:** M
**Status:** Draft

## Plain-English Summary

Expose mini-game state and submissions through thin API handlers, structured
ContentEvents, and typed SDK methods.

## Acceptance Criteria

- [ ] API handlers authenticate, validate, call engine services, and return
  typed responses without arc logic.
- [ ] Submissions are idempotent and participant-scoped.
- [ ] Events preserve audience privacy.
- [ ] Reconnect recovers authorized active state.
- [ ] SDK types contain no `any` or deterministic game logic.

## Dependencies

- AW-251
- AW-219

## Must Not Do

- Do not make routes or TypeScript authoritative for game state.

## References

- `docs/specs/0049-aw-252-mini-game-api-events-and-sdk.md`
- `docs/architecture/08-event-system.md`
- `docs/architecture/09-developer-api.md`
