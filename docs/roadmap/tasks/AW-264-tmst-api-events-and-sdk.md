# AW-264: TMST API, Events, and SDK

**Milestone / Epic:** M5 / M5-F
**Size:** M
**Status:** Planned

## Plain-English Summary

Extend the AW-252 mini-game API and TypeScript SDK with the typed payloads
TMST needs for its input, spotlight, reveal, and scoreboard phases, while
preserving the privacy contract per ADR-0003 and the story bible.

## Why This Matters

The AW-253 web layer cannot render TMST until it can subscribe to typed
events and submit typed actions. Privacy under the four-phase flow is
strictly tighter than the single-phase Rehearsal 1 games and must be
enforced server-side.

## Player Impact

Indirect. Players see correct prompts on their own devices and never see
private prompts intended for other players on the shared display.

## Business Value

Validates the platform's event-filtering and privacy contract under a
richer four-phase flow than Rehearsal 1 mini-games exercise.

## Technical Scope

- Extend the AW-252 API and event schemas with typed payloads for input,
  spotlight, reveal, and scoreboard phases.
- Enforce privacy server-side: private fact prompts go only to
  `specific_player`; the shared display never sees another player's prompt
  before reveal; reconnect exposes only authorized state.
- SDK methods submit actions only; SDK never mutates canonical state.
- API rejects malformed or out-of-phase actions deterministically.

## Acceptance Criteria

- [ ] Typed payloads for all four phases land in the API schema and SDK
  types.
- [ ] Privacy contract verified by tests covering private prompt delivery,
  shared-display filtering, and reconnect authorization.
- [ ] SDK methods cover only action submission; no SDK code mutates
  canonical state.
- [ ] Out-of-phase or unknown actions are rejected at the API layer.

## Tests/Verification

- API tests for each phase payload (positive and negative cases).
- Privacy test covering shared-display filtering and reconnect.
- SDK typecheck and build pass.

## Dependencies

- AW-263 (runtime mechanic)
- AW-252 mini-game API, events, and TypeScript SDK (complete)

## Must Not Do

- Do not put any arc execution or state-transition logic in the SDK.
- Do not expose private-player payloads on the shared-display stream.
- Do not hardcode provider names or surface assumptions in the API.

## Architecture References

- `docs/specs/0061-aw-258-tell-me-something-true.md`
- `docs/decisions/0003-nightcap-web-experience-runtime.md`
- `docs/decisions/0009-mini-game-runtime-boundary.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

Powers the events the AW-265 web layer renders and the actions players
submit during Rehearsal 2.
