# AW-275: Design System Follow-Ups: Semantic Tokens And Focus Visible

**Milestone / Epic:** M5 / M5-G
**Size:** S
**Status:** Planned

## Plain-English Summary

Finish the approved Stage A design-system cleanup by replacing retired
mini-game CSS variables and adding visible keyboard-focus states.

## Why This Matters

Retired variables currently fall back to colors outside the semantic token
system, and missing focus indicators make keyboard navigation difficult to
follow.

## Player Impact

Mini-game states remain visually coherent, and keyboard users can see which
control has focus.

## Business Value

This closes a small but visible quality and accessibility gap without adding a
framework, dependency, or new product surface.

## Technical Scope

- Replace retired mini-game variables with `--ink-muted`, `--accuse`, and
  `--theme-glow` without raw-color fallbacks.
- Add `:focus-visible` states using semantic glow tokens to interactive host,
  join, shared-display, and mini-game elements.
- Keep changes inside `nightcap-web` and the existing design-token boundary.

## Human Collaboration Contract

**Interaction profile:** Independent execution.

**Rationale:** Approved spec 0069 and issue #223 fully constrain the semantic
token replacements and accessibility acceptance criteria. The normal
plan-approval workflow applies. If implementation uncovers a subjective visual
direction or user-testing choice, reclassify before deciding.

**Founder input:** None unless a reclassification trigger occurs.

## Acceptance Criteria

- [ ] Mini-game stage styles use the current semantic tokens with no raw-color
  fallback.
- [ ] Every interactive host, join, shared-display, and mini-game control has a
  visible `:focus-visible` state.
- [ ] No raw color literal exists outside `nightcap-web/src/design/`.
- [ ] Nightcap web typecheck and tests pass.

## Tests/Verification

- Run the raw-color grep defined by spec 0069.
- Keyboard-tab through host, join, and shared-display flows.
- Run the Nightcap web typecheck and test suite.

## Dependencies

- `docs/specs/0069-nightcap-visual-design-system.md`
- Stage A design-system implementation from PR #212

## Must Not Do

- Do not change the engine or API.
- Do not add a UI framework or dependency.
- Do not introduce component-local color values.

## Architecture References

- `docs/specs/0069-nightcap-visual-design-system.md`
- `AGENTS.md` surface-agnostic boundary

## Playtest Relevance

Improves basic accessibility and presentation coherence before real-device
sessions.
