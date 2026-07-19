# AW-287 Discovery and Checkpoint Record

**Date**: 2026-07-18

**Status**: Complete — thin slice implemented, code-reviewed, and founder-approved. D-076 records final sign-off.

**Interaction profile**: Creative collaboration

## Discovery decisions

Most of AW-287's design work was completed in an earlier founder-directed
session with Codex, recorded in full in
[the Leverage design doc](../product/nightcap-leverage-advantages-sabotages.md):
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

## Walkthrough decisions (2026-07-18, post-review)

The representative-interaction walkthrough
([docs/superpowers/specs/2026-07-18-aw287-leverage-walkthrough.md](../superpowers/specs/2026-07-18-aw287-leverage-walkthrough.md))
surfaced two further judgment calls, both resolved by the founder:

7. **Reveal scope**: saboteur-identity reveal and the post-target protection
   window trigger **per-question**, not per-round/turn — as soon as that one
   question's answer is delivered.
8. **Sting Operation exposure audience**: exposing a sabotage's source is
   **private to the Sting Operation user**, not broadcast table-wide.

## Scope correction: Call Their Bluff replaced by Make Them Wait

Review of the implementation spec found that **Call Their Bluff** (one of
the six originally-named launch-set sabotages) requires challenging a
"public theory" a player has publicly advanced, but no public-theory state,
event, or input model exists anywhere in the platform, and AW-282
prohibits free text — so it has no deterministic input contract today.
**Make Them Wait**, also one of the design doc's Final top five sabotages,
replaces it: a tempo effect needing no new state. Full reasoning:
`docs/decisions/0015-nightcap-leverage-advantages-sabotages.md`.

## Reviewed artifacts

- [Nightcap Leverage design doc](../product/nightcap-leverage-advantages-sabotages.md) — full catalog, filtering, guardrails, and the founder-approved scope decision for continued design.
- [AW-287 task file](../roadmap/tasks/AW-287-nightcap-leverage-advantages-and-sabotages.md) — implementation scope, acceptance criteria, dependencies.
- [ADR-0015](../decisions/0015-nightcap-leverage-advantages-sabotages.md) — architecture boundary, generic/Nightcap naming split, Call Their Bluff replacement rationale.
- [Implementation spec 0075](../specs/0075-aw287-nightcap-leverage-advantages-sabotages.md) — runtime contract, schemas, acceptance criteria, test plan.
- [Representative-interaction walkthrough](../superpowers/specs/2026-07-18-aw287-leverage-walkthrough.md) — session-shaped example and the two resolved judgment calls above.

## Checkpoints

| Checkpoint | Artifact | Approval evidence | Result |
|---|---|---|---|
| Catalog and family design | Leverage design doc | Founder-directed design session, 2026-07-18 (prior session) | Approved (design direction) |
| Remaining unknowns | This record, D-075 | Founder answers captured in the 2026-07-18 session | Approved |
| Move to implementation scope | AW-287 task file, GitHub issue #250 | Founder explicitly chose "lock remaining unknowns now, build alongside/before AW-283" | Approved |
| Representative-interaction walkthrough | Walkthrough artifact | Founder resolved both flagged judgment calls, 2026-07-18 | Approved |
| Architecture decision and implementation spec | ADR-0015, spec 0075 | Authored per AGENTS.md's ADR requirement and the design doc's own implementation-spec requirement | Complete |
| Thin slice | `engine/resources/` (694+ tests), `nightcap/scripts/leverage_thin_slice_demo.py`, code review with all findings fixed | Founder approved the implemented thin slice and its demo replay, 2026-07-19 session; D-076 | Approved |

## Scope owner actions

- Claude Code owns AW-287 implementation and the follow-on AW-283 work.
- The remaining gate before this task can close is the implemented thin
  slice, per AW-287's Human Collaboration Contract gates.
