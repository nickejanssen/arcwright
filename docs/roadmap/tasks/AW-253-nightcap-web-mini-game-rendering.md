# AW-253: Nightcap Web Mini-game Rendering And Device Integration

**Milestone / Epic:** M4 / M4-E
**Size:** L
**Status:** Draft

## Plain-English Summary

Render mini-games in the Cloudflare-hosted Nightcap experience while Arcwright
remains authoritative.

## Acceptance Criteria

- [ ] ADR 0003 is reconsidered before the first Cloudflare-specific dependency
  or deployment configuration.
- [ ] Individual, collaborative, and group fixtures render on intended devices.
- [ ] Clients submit through the SDK and cannot resolve outcomes locally.
- [ ] Reconnect restores authorized presentation state.
- [ ] Privacy and accessibility checks pass.

## Dependencies

- AW-252
- AW-225
- AW-227
- AW-229

## Must Not Do

- Do not make Durable Objects a second session authority.
- Do not place deterministic game rules in TypeScript.

## References

- `docs/specs/0050-aw-253-nightcap-web-mini-game-rendering.md`
- `docs/decisions/0003-nightcap-web-experience-runtime.md`
- `docs/decisions/0009-mini-game-runtime-boundary.md`
