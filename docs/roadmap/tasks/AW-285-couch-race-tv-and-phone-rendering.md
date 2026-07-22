# AW-285: Couch Race TV And Phone Rendering

**Milestone / Epic:** M5 / M5-I
**Size:** L
**Status:** Planned

## Plain-English Summary

Render Couch Race in the Nightcap web experience: TV shared display (cold open staging, suspect stage with answers, evidence waves, countdown, scoreboard/reveal moments) and phone surfaces (detective identity, private evidence, question-intent selection, contradiction flagging, accusation lock-in), consuming engine ContentEvents with presentation hints per D-070.

## Why This Matters

The TV is the stage and the phones are the notebooks; this task is where the couch experience actually happens, reusing the M4 shared-display and player-device layers.

## Player Impact

Join in under 30 seconds, play from the couch, never see another player's private information.

## Business Value

Tier 1 polish bar (D-066): correct, legible, and snappy for the rehearsal surface.

## Technical Scope

- Shared display views: cold-open sequence staging (seq-* per spec 0069), suspect stage with answer presentation, group evidence, countdown, accusation results, reveal and scoreboard.
- Phone views: identity card, private evidence list, intent menu with token counter, tell notifications, contradiction flag flow, accusation submission with lockout state.
- Event subscription and input submission through the existing SDK; no arc logic in TypeScript.
- Privacy: private events (tells, private evidence, accusations) never render on the shared display (M4-D matrix extended with the new event types).

## Human Collaboration Contract

**Interaction profile:** Creative collaboration.

**Founder input:** Surface priorities, visual hierarchy, interaction
expectations, TV-versus-phone responsibilities, representative moments,
accessibility needs, and success definition.

**Required phases:** Begin with focused discovery before choosing layouts.
Confirm a short surface brief, then present low-cost wireframes, state maps, and
clickable or representative prototypes before full rendering. For every
artifact, explain what it represents, which assumptions it tests, how to review
it, and exactly what needs founder attention. Offer bounded options and a
recommendation when a choice remains, then ask one interactive question at a
time.

**Gates:** Pause for explicit direction after discovery, wireframes, prototype
flows, and the implemented thin slice. Research and reversible preparation may
continue while the founder is unavailable, but no subjective UI choice or full
implementation may proceed.

**Evidence:** Preserve discovery answers, wireframes and prototypes with review
instructions, options, recommendation, founder feedback, explicit checkpoint
approvals, dates, and owner actions.

## Acceptance Criteria

- [ ] A full Couch Race session is playable on real devices via the D-065 local-tunnel deployment.
- [ ] Join flow stays under 30 seconds.
- [ ] Extended privacy matrix passes: no private event type renders on the shared display.
- [ ] TV renders D-070 presentation hints (voice/animation/pause) where assets exist; degrades to text cleanly where they do not (Tier 2 assets remain M5-G scope).
- [ ] **Catch/squirm quality gate (D-090):** the suspect's reaction on a *confirmed contradiction catch* renders as a high-quality audiovisual moment (animation + audio per D-070), NOT a text fallback. Text degradation is acceptable for ambient narration but the catch moment is the mechanic's payoff and must clear the bar. This is validated in Rehearsal 1.
- [ ] **Asker-crediting staging (D-091 / G3):** the shared display attributes each question to its asker and shows what it bought, on the co-opetition model.
- [ ] **Room-watch staging (D-091 / G5):** the suspect's visible state (at ease / rattled / cracking) renders on the shared display during every question, giving the whole room a reason to watch another player's turn.

## Tests/Verification

- `cd sdk && npm run typecheck && npm run build`; dashboard equivalents.
- Real-device privacy walkthrough per the AW-230 matrix method.

## Dependencies

- AW-282/AW-283/AW-284 event contracts
- M4 layers: AW-226–AW-230, AW-253 mini-game rendering
- Spec 0069 visual design system (Tier 1 application)

## Must Not Do

- No arc execution logic in TypeScript.
- No Tier 2 art/animation/sound investment beyond existing spec 0069 sequences (D-066).
- No rendering assumptions pushed into engine events.

## Architecture References

- `docs/decisions/0003-nightcap-web-experience-runtime.md`
- `docs/specs/0069-nightcap-visual-design-system.md`
- `docs/architecture/08-event-system.md`, `docs/architecture/09-developer-api.md`

## Playtest Relevance

Direct: this is the surface Rehearsal 1 (retargeted) plays on.
