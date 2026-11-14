---
id: productroadmap.product.nightcap-status
namespace: product-roadmap
title: "Nightcap: Where Things Stand"
owner: Nico Janssen
status: active
review_by: "2027-02-14"
sensitivity: internal
source: authored
tags: []
supersedes: []
---

> Current version: v1.0
> Last updated: 2026-11-14
> Status: Current
> Canonical path: docs/product/nightcap-status.md

# Nightcap: Where Things Stand

One page that says what is done, what is paused, what is next, and what the founder needs to do. It is updated whenever a decision is recorded. It does not replace the task tracker: whether an individual task is open or closed is answered on GitHub (`python scripts/roadmap_status.py`).

## In one paragraph

The online playtest of Nightcap is paused. The founder chose on 2026-11-13 to stop sending the playtest to testers and instead rebuild the real TV-and-phones game so it matches the current game design. That rebuild has a draft plan that is not yet approved and not yet saved to GitHub. Until the rebuilt game is played once on a TV, work on AI helper tooling stays limited to fixing things that break. Both choices are recorded as decision D-111 in [decisions-log.csv](decisions-log.csv).

## Done

| What | Result | Where |
| --- | --- | --- |
| Clearing development friction (the September "Phase 0") | Finished and merged 2026-09-27 | [spec 0090](../specs/0090-phase-0-development-friction.md) |
| Bug-test of playtest v3.0 | 14 checks passed, 2 known gaps written down | [pre-send QA](../gdd/nightcap/03-playtest-evidence/99-paper-test-02-v3.0-pre-send-qa.md) |
| Results of the earlier playtest (v2.2), as the comparison point | Written up | [v2.2 results](../gdd/nightcap/03-playtest-evidence/98-paper-test-02-v2.2-results.md) |
| The pass bar for v3.0 (what the numbers must show to call it a success) | Approved by the founder 2026-09-28 | [v3.0 analysis plan](../gdd/nightcap/02-validation/99-paper-test-02-v3.0-analysis-plan.md) |
| Improved playtest v3.1 | Built and online as an unlisted draft, merged 2026-10-03. Automated checks only. | [spec 0091](../specs/0091-nightcap-v3.1-improvements.md), [v3.1 validation](../gdd/nightcap/03-playtest-evidence/99-paper-test-02-v3.1-validation.md) |

## Paused

The online playtest ("Paper Test #2"). At the moment it was paused:

- v3.0 was ready to send except for two founder steps that were never done: one run on a phone, and inviting testers.
- v3.1 had never been tried in a real browser or on a phone.
- No testers were invited and no outside results exist.
- The question the playtest was meant to answer, "do new players find it fun quickly?" (called Gate 1 in the design documents), is still unanswered. Its recorded status is still NOT PASSED.

Nothing is lost. v3.0 and v3.1 stay online exactly as they are. Restarting the playtest needs a new decision.

## Next: the rebuild

The plan is draft spec 0092, "Nightcap GDD Rebuild". Its goal is that the full designed game runs from joining to the final debrief on a TV with phones.

- **Status: draft. Not approved. No building may start.**
- **It is not on GitHub yet.** It exists only as unsaved files in another working session, along with the working notes for the first new case, *The Lido*. The founder plays that case unspoiled, so this page says nothing more about it.
- Already answered by the founder: 2 to 4 players, Leverage is earned only, six investigations per player, a brand-new first case.
- Still open: how players put together their final theory (question 3 in the spec), the cap on Leverage, and confirming the session-length target (normally 30 minutes or less, never more than 60).

## The tooling freeze

Since 2026-09-27, work on AI helper tooling and the knowledge base has been limited to fixing things that break (decision D-110). It was due to end when the playtest question was answered. Because the playtest is paused, it now ends when the rebuilt game's first TV session is played (decision D-111).

One side effect: the knowledge base's index is a few documents behind. The specialist agents still read everything that is merged, so this is safe to leave until the freeze ends.

## Your steps

1. **Save the rebuild plan.** Open the session where you answered the rebuild questions on 2026-11-13 and send it this: "Commit and push spec 0092 and the case method logs, and open a PR. Do not add a decision for the playtest pause; it is already recorded as D-111. Tell me what the two changed v3.1 playtest files are for and whether to keep them." Until this is done, the plan can be lost and no other session or agent can see it.
2. **Read spec 0092 and answer what is still open** (see "Next: the rebuild" above). Each open question has a recommendation; "agree" is a valid answer.
3. **Approve it** by replying "approve 0092" in that session, if you are happy with it.
4. **Review the first deliverable**, an inventory of what exists today against the design, when that session produces it.

Nothing else is waiting on you.
