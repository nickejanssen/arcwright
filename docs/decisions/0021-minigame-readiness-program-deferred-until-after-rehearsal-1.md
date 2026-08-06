# 0021 - Mini-game Readiness Program Deferred Until After Rehearsal 1

**Date:** 2026-08-05
**Status:** Accepted
**Decision authority:** Founder decision recorded 2026-08-05 (D-102)
**Resolves:** the second-pass execution question left open by `docs/decisions/0019-minigame-readiness-execution-gated-on-ownership-reconciliation.md` and restated in `docs/decisions/0020-aw-286-owns-remaining-couch-race-integration.md`
**Roadmap references:** AW-286 (issue #240), M5-I, M6

---

# Status

**Accepted**

---

# Context

ADR 0019 held all mini-game readiness execution at the merged browser golden
path and deferred the execution question to a second pass, gated on resolving
who owned the remaining AW-285 scope. ADR 0020 and D-101 cleared that gate by
assigning the scope to AW-286 and reclassifying the program as a supplier rather
than a gate.

That reclassification changed the premise of the execution question. Before
D-101, the program appeared to gate AW-286 and therefore Rehearsal 1, which
created pressure to execute it. After D-101 the dependency is one-way, so
deferring the program costs mini-game breadth at Rehearsal 1 rather than
Rehearsal 1 itself.

The constraints that argued against execution were unchanged at the time of this
decision and were verified against the repository on 2026-08-05:

- Program map order 2,
  `docs/superpowers/plans/2026-08-03-minigame-capability-and-trust-platform.md`,
  requires at line 18 that the golden-path canary report be `GO` or that its
  required revisions be completed.
  `docs/product/mini-game-readiness/tmst-golden-path-report.md` line 5 records
  the human usability gate as not run. Order 2 cannot legitimately start.
- Order 2 and order 3 introduce
  `migrations/versions/0008_add_mini_game_invocation_contracts.py`,
  `migrations/versions/0009_add_mini_game_authoring_resources.py`, and a
  `dashboard/package.json` dependency. All are `AGENTS.md` Hard Rules requiring
  separate approval.
- The Scene Sweep plan at order 6 declares the order 2 and order 3 outputs as
  required completed dependencies. Both are documents only, at 0 of 47 and 0 of
  42 steps, with no roadmap task ID in `docs/roadmap/index.json`.
- Order 2 and order 6 write to surfaces AW-286 now owns and must certify on real
  devices: `nightcap/couch-race.arc.json`, `engine/mini_games/models.py`
  `MiniGameBinding`, `nightcap-web/src/filters.ts`,
  `nightcap-web/src/couch-race/display-projection.ts`,
  `api/routers/mini_games.py`, and the `ContentEvent` contract.

Alternatives presented to the founder and not chosen: run the golden-path human
usability session first and then decide order 2; approve order 2 now while
explicitly waiving its canary gate; approve a narrow Scene Sweep carve-out
limited to the presentation brief and renderers.

---

# Decision

The Mini-game Platform and Nightcap Readiness Program is deferred in full until
after AW-286 Rehearsal 1 has run and been debriefed.

Scope stays capped where D-099 left it: the merged browser golden path (PR #275,
`78166d4`). No plan at program map order 2 or later is executed. This includes
the capability and trust platform, the creator and readiness labs, every
per-game readiness plan including Scene Sweep, the Nightcap mini-game
foundation, and the whole-session certification plan.

Capacity is redirected to the Couch Race content path: AW-277 through AW-280,
and AW-290 and AW-291.

Rehearsal 1 proceeds under AW-286 with whatever certified mini-game candidates
exist. Beats with no certified candidate are recorded as deliberately unbound
with their authored story fallback, per D-101.

This deferral is reconsidered after the AW-286 debrief, informed by real-player
evidence rather than by plan assumptions.

---

# Consequences

## Positive consequences

- No migration, no new dependency, and no generic transport rewrite lands
  beneath the surfaces AW-286 must certify on real devices.
- Rehearsal 1 is not delayed by a 12-plan program whose first outstanding slice
  cannot legitimately start.
- The largest unclosed gap in the Road to Live program gets attention: the 468
  authored lines in `docs/design/line-libraries/` still have no engine reader,
  and AW-290 and AW-291 remain at zero PRs.
- The eventual execution decision is made against real-player evidence.

## Negative consequences

- Rehearsal 1 runs with mini-games at fewer than six beats.
  `nightcap/couch-race.arc.json` binds only `scene` and `twist` today.
- Three of the six assumed packages remain unbuilt. `the-grill-interrogation`,
  `interrogation-room`, and `the-unmasking` exist only as specs 0084, 0076, and
  0085.
- The platform work that would make Arcwright's mini-game layer usable by an
  external developer slips. This is H2 value under platform principle 7, so the
  slip is accepted rather than mitigated.
- Written plans age against a moving mainline. Each plan's Task 1 already
  requires a mainline refresh and characterization before any source change, so
  the cost is bounded but real.

## Trade-offs

Gained: a stable rehearsal surface, an unblocked content path, and an execution
decision deferred until evidence exists. Lost: mini-game breadth at Rehearsal 1
and elapsed calendar time on the platform track.

---

# References

- `docs/decisions/0019-minigame-readiness-execution-gated-on-ownership-reconciliation.md`
- `docs/decisions/0020-aw-286-owns-remaining-couch-race-integration.md`
- `docs/product/decisions-log.csv`, D-099, D-100, D-101, D-102
- `docs/superpowers/plans/2026-08-02-mini-game-platform-readiness-program.md`
- `docs/product/mini-game-readiness/artifact-closeout-matrix.md`
- `docs/product/mini-game-readiness/tmst-golden-path-report.md`
- `docs/product/road-to-live/status.md`
- `docs/roadmap/tasks/AW-286-couch-race-rehearsal-slice-and-rehearsal-1-retarget.md`

## Open questions this decision does not resolve

- Whether the golden-path human usability sessions are run before or after
  Rehearsal 1. They gate any future order 2 greenlight but are not themselves
  deferred by this decision.
- The `run_seed` cross-module change remains off-limits and unapproved. It is
  reached only through the Scene Sweep plan, which is deferred.
- AW-286 re-estimation and a possible split, routed to the Planner by D-101.
