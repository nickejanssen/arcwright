# AW-268: Nightcap Asset Pipeline and Motion System

**Milestone / Epic:** M5 / M5-G
**Size:** M
**Status:** Planned

## Plain-English Summary

Implement the Nightcap art direction brief as a real asset pipeline and
motion system: per-theme folder structure, illustration set per theme,
animation specs, and motion tokens consumable by the AW-253 web rendering
layer.

## Why This Matters

The brief alone does not change what players see. AW-268 is the work that
makes Crime Scene Smash, Evidence Locker, and Tell Me Something True
visually coherent and demo-ready.

## Player Impact

Players see polished, themed mini-games with consistent motion and
typography across all three wrappers.

## Business Value

Brings the product to demo-quality for M6 qualifying sessions and outside
audiences.

## Technical Scope

- Asset folder structure under `nightcap/assets/themes/<theme>/`.
- Illustration set per theme (High Society, Corporate, Sci-Fi).
- Animation specs and the chosen runtime decision (Rive vs Lottie vs sprite,
  decided as part of this task and recorded in the package or a short
  decision note).
- Motion tokens consumable by AW-253 web rendering.
- Backfill polish into Crime Scene Smash, Evidence Locker, and Tell Me
  Something True.

## Human Collaboration Contract

**Interaction profiles:** Creative collaboration plus Decision interview.

**Founder input:** Final AW-267 art-direction approval, representative asset and
motion expectations, wrapper behavior, accessibility priorities, and the
animation-runtime choice.

**Creative flow:** Treat AW-267 as a hard prerequisite. Explain each proposed
artifact, why it exists, how to review it, and what needs founder attention.
Present low-cost representative assets, motion studies, and wrapper mockups in
phases. Pause after each checkpoint for focused interactive feedback before
expanding the system or producing final assets.

**Runtime decision flow:** Research the constraints, explain cost, performance,
accessibility, and maintenance trade-offs in plain language, and present two or
three viable runtime options with a recommendation. Ask one focused interactive
choice question at a time and confirm the selected option.

**Gates:** No asset or motion production begins before explicit AW-267 final
sign-off. No broad production follows a sample checkpoint without explicit
direction. No runtime implementation begins until the founder explicitly
approves the named option.

**Evidence:** Preserve the approved AW-267 reference, artifacts shown, review
instructions, founder feedback, runtime options and recommendation, explicit
approvals, dates, and owner actions.

## Acceptance Criteria

- [ ] Per-theme asset folder structure exists and is documented.
- [ ] Illustration sets exist for all three wrappers.
- [ ] Animation runtime decision recorded with rationale.
- [ ] Motion tokens are consumable by the AW-253 web layer.
- [ ] All three mini-games consume the motion system.
- [ ] Visual diff (screenshots before and after) captured for at least one
  mini-game.

## Tests/Verification

- AW-253 web tests still pass against the new motion tokens.
- Visual diff screenshots archived alongside the epic.
- Asset paths resolve in both Rehearsal 1 games and TMST.

## Dependencies

- AW-267 (approved art direction brief)

## Must Not Do

- Do not block any rehearsal on this task.
- Do not couple visual tokens to a single mini-game.
- Do not modify canonical state, runtime, or API logic.

## Architecture References

- `docs/design/nightcap-art-direction.md` (produced by AW-267)
- `docs/story-bibles/nightcap-murder-mystery.md`
- `docs/specs/0061-aw-258-tell-me-something-true.md`

## Playtest Relevance

Closes the visual gap between rehearsal-quality and demo-quality for M6.
