# AW-287 Discovery and Checkpoint Record

**Date**: 2026-07-18

**Status**: Approved for implementation (design walkthrough gate still open, see Checkpoints)

**Interaction profile**: Creative collaboration

## Discovery decisions

Most of AW-287's design work was completed in an earlier founder-directed
session with Codex, recorded in full in
[the Leverage design doc](../superpowers/specs/2026-07-18-nightcap-leverage-advantages-sabotages-design.md):
the 25+25 initial catalog, the filtering criteria, three filter passes, the
final five-family taxonomy on each side, the interaction/combination review,
the danger-combination limits, and the six-effect launch set. That work is
real and is not re-litigated here.

This record captures the remaining decisions, resolved in this session
(2026-07-18) to close the design doc's own "Unknowns" section:

1. **Balance visibility**: Leverage balances are public — every player can
   see everyone's current Leverage total. Chosen to support the design doc's
   own filter criteria ("produce a visible table moment") and to let
   economy-pressure sabotages (Raise the Stakes, Pick Their Pocket) land as
   readable threats.
2. **Saboteur identity reveal timing**: a sabotage's source is revealed to
   its target after the sabotaged interaction resolves — not instantly.
   Sting Operation is the deliberate exception: exposing its source
   immediately is that advantage's defining payoff, not a general reveal
   rule.
3. **Cross-beat persistence**: Leverage carries between beats for the whole
   session; it does not expire at beat transitions. Bounded by the existing
   bank-cap guardrail from the design doc's economy guardrails section.
4. **Per-effect visibility**: there is no single global public/private
   toggle for Leverage effects or their outcomes. Each effect's visibility
   follows its own documented behavior in the catalog (Listen In: private to
   the saboteur; Sting Operation: exposes its source; Rattle the Witness:
   its effect on the public answer is visible to the table since it alters
   something everyone already hears). This also settled the adjacent
   question of contradiction-catch visibility for AW-283: a catch checks a
   claim that is already public per AW-282's routing, so it stays public by
   default, consistent with the catalog's rejection of "Quiet Word" (an
   advantage that would have made an answer private) specifically because it
   "weakened the shared TV moment."
5. **Team/co-op unknown**: not applicable. Nightcap v1 has no team or
   co-op configuration (top-level scope boundary), so the question of
   disabling player-targeted sabotage by configuration does not arise yet.
6. **Telemetry-signal unknown**: deferred. Rather than pre-committing to
   which signal "best predicts that sabotage felt exciting rather than
   frustrating," AW-287 captures the broad telemetry the design doc already
   specifies (grants, spends, targets, outcomes, counterplay, recovery) and
   leaves signal selection to post-rehearsal tuning with real data.

## Reviewed artifact

- [Nightcap Leverage design doc](../superpowers/specs/2026-07-18-nightcap-leverage-advantages-sabotages-design.md) — full catalog, filtering, guardrails, and the founder-approved scope decision for continued design.
- [AW-287 task file](../roadmap/tasks/AW-287-nightcap-leverage-advantages-and-sabotages.md) — implementation scope, acceptance criteria, dependencies.

## Checkpoints

| Checkpoint | Artifact | Approval evidence | Result |
|---|---|---|---|
| Catalog and family design | Leverage design doc | Founder-directed design session, 2026-07-18 (prior session) | Approved (design direction) |
| Remaining unknowns | This record, D-075 | Founder answers captured in the 2026-07-18 session | Approved |
| Move to implementation scope | AW-287 task file, GitHub issue #250 | Founder explicitly chose "lock remaining unknowns now, build alongside/before AW-283" | Approved |
| Representative-interaction walkthrough | *(pending — required before full implementation per AW-287's Human Collaboration Contract)* | Not yet presented | Pending |
| Thin slice | *(pending)* | Not yet implemented | Pending |

## Scope owner actions

- Claude Code owns AW-287 implementation and the follow-on AW-283 work.
- The remaining gate before full implementation is the representative-
  interaction walkthrough (AW-287's Required phases) — a low-cost example of
  2-3 effects firing in a session-shaped scenario, presented before the
  complete resolution engine is built.
