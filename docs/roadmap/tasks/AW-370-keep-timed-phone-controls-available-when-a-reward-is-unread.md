---
id: productroadmap.roadmap.tasks.aw-370-keep-timed-phone-controls-available-when-a-reward-is-unread
namespace: product-roadmap
title: "AW-370: Keep Timed Phone Controls Available When A Reward Is Unread"
owner: Nico Janssen
status: draft
review_by: "2027-02-26"
sensitivity: internal
source: authored
x-scope-evidence: "D-126, D-139"
tags: []
supersedes: []
---

# AW-370: Keep Timed Phone Controls Available When A Reward Is Unread

- **Milestone / Epic:** M7 / M7-B
- **Size:** M
- **Product:** Nightcap
- **Owner:** One build session after founder approval of the screen behavior and implementation plan
- **GitHub issue:** [#516](https://github.com/nickejanssen/arcwright/issues/516)
- **Target date:** 2026-12-05 (proposed)

## Plain-English Summary

A phone rewards a mini-game winner with an extra investigation. If the player leaves the reward card open, that phone can keep showing the card while the TV and other phones have moved to later activities. The player can tap OK to leave the card. The room clock keeps running even while the controls are covered.

## Why This Matters

- Observed in the 2026-11-26 two-phone browser rehearsal for #354. An unacknowledged reward remained over later mini-games and Last Call. The other phone could lock a theory while the winner was still on the reward card.
- In `dashboard/src/screens/WaitingScreen.tsx`, `RewardCard` wraps the active phone screen. An unread grant in `dashboard/src/screens/round/RewardCard.tsx` replaces that screen until acknowledged. Spec 0095 screen 12 requires acknowledgment of each grant, so the founder should choose how to keep the grant visible when timed play resumes.

## Technical Scope

1. Decide how a phone surfaces an unread reward while an investigation, mini-game or Last Call is live.
2. Keep all active timed controls available and preserve the saved grant, remaining budget and acknowledgment behavior from spec 0095.
3. Keep the TV on its existing public information boundary.

## Human Collaboration Contract

**Interaction profile:** Decision interview, then independent execution. Walk the founder through the unread card and timed screen, agree on how they coexist, and get explicit plan approval before code changes.

## Acceptance Criteria

- [ ] A player can operate an active mini-game and Last Call after leaving an earlier reward unread.
- [ ] The promised investigation and its remaining balance still appear on the correct phone. The player can acknowledge each grant separately.
- [ ] Reload and rejoin preserve the correct grant and do not open an already acknowledged card on the same phone.
- [ ] Shared screens and other phones receive no new private data.

## Tests/Verification

- `npm test --prefix dashboard`, including a phone that receives a reward, leaves it unread and advances into the next timed phase.
- Repeat the relevant path in the local 1a browser rehearsal, using spoiler-free evidence.

## Dependencies

- AW-332 and AW-333.

## Must Not Do

- Do not change the award, budget, phase timer or case content.
- Keep case details and captures out of GitHub under D-153.
