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

## Human Collaboration Contract

**Interaction profile:** Creative collaboration.

**Founder input:** Visual goals, references, tastes and dislikes, wrapper-level
expectations, constraints, desired player feeling, and the definition of a
successful Nightcap identity.

**Required phases:**

1. Interview the founder before proposing direction. Use focused interactive
   questions, one decision at a time, and offer informed examples and advice.
2. Synthesize the answers into a short creative brief and obtain confirmation.
3. Present two or three comparative, low-cost moodboard directions with a
   recommendation before drafting the full art-direction document.
4. For every artifact, explain what it represents, which assumptions it tests,
   how to review it, and exactly what needs founder attention.
5. Pause for explicit direction after the brief, moodboards, wrapper studies,
   and final assembled brief. Revise only the approved direction.

**Gates:** Research and reversible preparation may continue while the founder is
unavailable, but no creative choice may be made. No full brief or production
direction proceeds without the preceding explicit approval. PR #243 content and
D-073 are candidate research only until this fresh interview process produces
explicit approval; they are not founder direction or sign-off evidence.

**Evidence:** Preserve discovery answers, alternatives, recommendation,
artifacts and review instructions, founder feedback, explicit checkpoint and
final approvals, dates, and owner actions.

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
