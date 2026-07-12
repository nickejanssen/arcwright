# AW-265: TMST Web Rendering for Four Phases

**Milestone / Epic:** M5 / M5-F
**Size:** M
**Status:** Complete

## Plain-English Summary

Extend the AW-253 Nightcap web layer to render all four TMST phases on both
shared display and player devices, including every transient state (loading,
timeout, disconnected, skipped, reveal, scoreboard).

## Why This Matters

Without the web layer, real humans cannot play TMST in Rehearsal 2. The
four-phase shape is also a stress test of the web client's ability to
remain a pure renderer: no canonical timing, scoring, outcome, or state
logic may live in the client.

## Player Impact

Players see a narrator-led, diegetic, four-phase social opener that
matches the High Society, Corporate, or Sci-Fi wrapper chosen by the arc.

## Business Value

Closes the rendering side of the TMST workstream and proves the platform's
rendering contract under a more demanding flow than Rehearsal 1 games.

## Technical Scope

- Extend AW-253 to render all four TMST phases on shared display and
  player devices.
- Cover loading, timeout, disconnected, skipped, reveal, and scoreboard
  states on every screen.
- Render narrator-led diegetic framing per the chosen wrapper (High Society
  / Corporate / Sci-Fi per story bible and spec 0061).
- No canonical timing, scoring, outcome, or state logic in the web client;
  the client consumes typed events from AW-264 only.

## Acceptance Criteria

- [ ] All four phases render correctly on shared display and player devices.
- [ ] Loading, timeout, disconnected, skipped, reveal, and scoreboard
  states are present on every relevant screen.
- [ ] Diegetic framing matches the wrapper chosen by the arc.
- [ ] No canonical timing, scoring, outcome, or state logic exists in the
  web client (verified by code review and grep).
- [ ] Tier 1 polish bar holds: no crashes, mid-range Android target 60fps,
  basic accessibility (WCAG AA color contrast, screen-reader landmarks,
  keyboard navigation).

## Tests/Verification

- Component tests for each phase and state.
- Manual run-through on the AW-230 device matrix.
- Grep for canonical-state logic in the web client (should be none).

## Dependencies

- AW-264 (API, events, SDK)
- AW-253 Nightcap web mini-game rendering and device integration (complete)

## Must Not Do

- Do not implement scoring, timing, or outcome logic in the web client.
- Do not couple visual styling to a single wrapper; use the wrapper
  scaffold from spec 0061.
- Do not bypass the AW-202 web runtime contract.

## Architecture References

- `docs/specs/0061-aw-258-tell-me-something-true.md`
- `docs/decisions/0003-nightcap-web-experience-runtime.md`
- `docs/decisions/0009-mini-game-runtime-boundary.md`
- `docs/story-bibles/nightcap-murder-mystery.md`

## Playtest Relevance

Provides the rendering layer real humans interact with in Rehearsal 2.
