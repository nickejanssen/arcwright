# M5-G: Nightcap Visual Identity and Polish

**Milestone:** M5
**Status:** Planned

## Plain-English Summary

Author the Nightcap art direction brief and implement the asset pipeline
plus motion system so all mini-games (Crime Scene Smash, Evidence Locker,
Tell Me Something True) consume the same visual identity.

## Why This Matters

Tier 1 polish (engineering correctness, performance, basic UX) ships in
Rehearsal 1. Tier 2 polish (visual identity, art, animation) was
explicitly deferred per D-066 to avoid art-directing before any human had
played. After Rehearsal 1, this epic ships Tier 2.

## Player Impact

Players see a polished, themed product instead of a functional prototype.

## Business Value

Closes the gap between "rehearsal-quality" and "demo-quality" for outside
audiences and qualifying sessions in M6.

## Technical Scope

The technical scope is limited to the tasks listed below.

## Tasks

- [AW-275: Design System Follow-Ups: Semantic Tokens And Focus Visible](../tasks/AW-275-design-system-follow-ups.md)
- [AW-267: Nightcap Art Direction Brief](../tasks/AW-267-nightcap-art-direction-brief.md)
- [AW-268: Nightcap Asset Pipeline and Motion System](../tasks/AW-268-nightcap-asset-pipeline-and-motion-system.md)

## Acceptance Criteria

- All child tasks satisfy their acceptance criteria.
- The art direction brief is approved by the founder.
- At least one theme is implemented and visible in at least one mini-game.
- Crime Scene Smash, Evidence Locker, and Tell Me Something True all
  consume the motion system.

## Tests/Verification

- Brief approval recorded in the decision log.
- Visual diff (screenshots before / after) of at least one mini-game.

## Dependencies

- Parent milestone: M5
- AW-259 (Rehearsal 1) closed (Tier 2 work informed by Rehearsal 1 findings)

## Must Not Do

- Do not block any rehearsal on this epic.
- Do not couple visual tokens to a single mini-game.

## Architecture References

- `docs/story-bibles/nightcap-murder-mystery.md`
- `docs/specs/0061-aw-258-tell-me-something-true.md`

## Playtest Relevance

Brings the product to demo-quality for M6 qualifying sessions.
