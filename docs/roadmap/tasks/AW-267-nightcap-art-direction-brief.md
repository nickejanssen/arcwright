# AW-267: Nightcap Art Direction Brief

**Milestone / Epic:** M5 / M5-G
**Size:** S
**Status:** Planned

## Plain-English Summary

Author the founder-approved Nightcap art direction brief that defines
visual identity, per-wrapper theme aesthetic, motion principles, typography,
color, and narrator visual presence so the AW-268 asset pipeline has a
single source of truth to implement.

## Why This Matters

Tier 2 polish (visual identity, art, animation) was explicitly deferred from
Rehearsal 1 per D-066. Without an approved brief, AW-268 cannot start
without re-litigating direction mid-implementation.

## Player Impact

Indirect. Players will see a themed, coherent visual experience instead of
a functional prototype once AW-268 implements the brief.

## Business Value

Sets the visual standard the platform will be measured against for M6
qualifying sessions. Prevents per-asset, per-wrapper visual drift.

## Technical Scope

- Founder-authored or commissioned brief covering: visual identity, theme
  aesthetic per diegetic wrapper (High Society, Corporate, Sci-Fi per story
  bible section 2 and spec 0061), motion system principles, typography,
  color, narrator visual presence.
- Output is `docs/design/nightcap-art-direction.md` plus reference
  moodboards stored or linked alongside.
- Founder sign-off recorded in `docs/product/decisions-log.csv`.

## Acceptance Criteria

- [ ] `docs/design/nightcap-art-direction.md` exists and covers every
  section above.
- [ ] Reference moodboards exist for each diegetic wrapper.
- [ ] Founder sign-off recorded in the decisions log.

## Tests/Verification

- Founder review and approval recorded.
- Visual contract is consumable by AW-268 without further direction.

## Dependencies

- `docs/story-bibles/nightcap-murder-mystery.md` v1.1
- `docs/specs/0061-aw-258-tell-me-something-true.md`

## Must Not Do

- Do not ship any code in this task.
- Do not couple visual tokens to a single mini-game.
- Do not block any rehearsal on this task.

## Architecture References

- `docs/story-bibles/nightcap-murder-mystery.md`
- `docs/specs/0061-aw-258-tell-me-something-true.md`

## Playtest Relevance

Enables AW-268, which brings Nightcap to demo-quality for M6 qualifying
sessions.
