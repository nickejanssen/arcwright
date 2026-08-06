# 0019 - Mini-game Readiness Execution Gated on AW-286 Ownership Reconciliation

**Date:** 2026-08-05
**Status:** Accepted
**Decision authority:** Founder decision recorded 2026-08-05 (D-100)
**Related decisions:** D-099, ADR `docs/decisions/0018-mini-game-orchestration-and-execution-adapters.md`
**Roadmap references:** AW-285, AW-286 (issue #240), M5-I, M6

---

# Status

**Accepted**

---

# Context

The mini-game readiness program is a twelve-plan ordered sequence defined in
`docs/superpowers/plans/2026-08-02-mini-game-platform-readiness-program.md`
lines 44 through 58. Order 1, the browser golden path, was approved for
execution by D-099 and merged as `78166d4`/PR #275 on 2026-08-04. Every later
order remains gated on separate founder execution approval, as recorded in
`docs/product/mini-game-readiness/artifact-closeout-matrix.md` lines 18 and 20.

The founder asked whether to greenlight the next slice. The review that
preceded this decision established four findings against repository state on
2026-08-05.

**Finding 1: the next slice cannot start on its own terms.** Order 2 is
`docs/superpowers/plans/2026-08-03-minigame-capability-and-trust-platform.md`.
Its Global Constraints line 18 requires that the golden-path canary report be
`GO` or that its required revisions be completed.
`docs/product/mini-game-readiness/tmst-golden-path-report.md` line 5 records
`Status: Playtest-ready internally, human usability gate not run`, and line 60
records that the required human usability proof is missing. D-099 carries the
same condition.

**Finding 2: the declared dependencies of the Scene Sweep slice do not exist.**
`docs/superpowers/plans/2026-08-03-scene-sweep-game-ready.md` line 15 declares
the browser golden path, the capability and trust platform, and the creator and
readiness labs as required completed dependencies. Verification against the
repository found no implementing code for the latter two, no roadmap task ID for
either in `docs/roadmap/index.json`, and zero completed steps (0 of 47 and 0 of
42 respectively). Alembic revisions stop at
`migrations/versions/0007_add_accusations_table.py`; the capability and labs
plans introduce `0008_add_mini_game_invocation_contracts.py` and
`0009_add_mini_game_authoring_resources.py`, and the labs plan modifies
`dashboard/package.json`. Under the `AGENTS.md` Hard Rules those are schema,
migration, cross-module, telemetry, and new-dependency changes requiring
separate approval.

**Finding 3: the next slices overlap AW-286 on named surfaces.** The following
artifacts are claimed by both the program plans and AW-286:
`nightcap/couch-race.arc.json` (two of six beats bound today; `pour`, `grill`,
`last_call`, and `truth` carry empty `mini_games` arrays),
`engine/mini_games/models.py` lines 161 through 168 (`MiniGameBinding`),
`nightcap-web/src/filters.ts` lines 3 through 24 (the shared-display privacy
gate), `nightcap-web/src/couch-race/display-projection.ts`,
`api/routers/mini_games.py`, the `ContentEvent` contract at
`engine/events/models.py` lines 43, 50, and 53 with its TypeScript mirrors, and
the rehearsal operations documents under `docs/roadmap/operations/`.

**Finding 4: three canonical records disagree on who owns the remaining AW-285
scope, and the sequencing is circular.**

| Record | Assigns six-beat integration, privacy and device checks, and audiovisual polish to |
| --- | --- |
| `docs/product/road-to-live/status.md` lines 37 to 39 | AW-286 |
| `docs/product/mini-game-readiness/artifact-closeout-matrix.md` line 23 | The program |
| `docs/product/mini-game-readiness/artifact-closeout-matrix.md` line 30 | AW-286 as the gate, waiting on the program |

`docs/roadmap/tasks/AW-286-couch-race-rehearsal-slice-and-rehearsal-1-retarget.md`
lines 74 through 81 lists the program's certification gates as an AW-286
dependency. The program's own Order 12 plan,
`docs/superpowers/plans/2026-08-02-nightcap-existing-minigames-game-ready.md`
Task 6 at lines 314 through 356, is titled "Run AW-286 Real-player Rehearsal and
Remediate". AW-286 waits on the program and the program waits on AW-286.

Alternatives presented to the founder and not chosen:

- Defer the whole program until after Rehearsal 1 and cap permanently at the
  merged browser golden path.
- Approve Order 2 only, after running the human usability session, and freeze
  the overlapping AW-286 surfaces until it lands.
- Approve a narrow Scene Sweep carve-out limited to presentation and renderer
  work, excluding the `run_seed` change, the transport rewrite, and the arc
  placement policy.

---

# Decision

No execution approval is granted for any mini-game readiness slice beyond the
merged browser golden path. The program remains capped where D-099 left it.

Before any further execution decision, the ownership conflict recorded in
Finding 4 must be reconciled to a single owner for the remaining AW-285 scope,
and the AW-286 circularity must be resolved. The execution question is then
re-decided in a separate second pass.

Assigning that owner is a founder call. It is not made by this record and is
not inferred from any existing document. The three conflicting records stand
unaltered until the founder makes that call, so that the reconciliation pass
resolves them from a decision rather than from a Scribe's preference among
them.

---

# Consequences

## Positive consequences

- No migration, no new dependency, and no generic transport rewrite lands
  beneath the surfaces AW-286 must certify on real devices while ownership of
  those surfaces is ambiguous.
- The reconciliation pass has an explicit, evidence-backed input set rather than
  three records that silently contradict each other.
- The unmet golden-path human usability gate is surfaced as a real blocker on
  Order 2 rather than being stepped over.

## Negative consequences

- Rehearsal 1 planning continues without a settled owner for six-beat
  integration, privacy and device checks, and audiovisual polish.
- The execution question is deferred rather than answered, which costs one
  additional founder pass.
- Mini-game coverage at Rehearsal 1 remains at two of six beats.

## Trade-offs

Gained: a correct record and a single owner before cross-module work begins.
Lost: elapsed time, and the option of starting Order 2 in parallel with the
reconciliation.

---

# References

- `docs/decisions/0018-mini-game-orchestration-and-execution-adapters.md`
- `docs/product/decisions-log.csv`, D-099 and D-100
- `docs/product/road-to-live/status.md`
- `docs/product/mini-game-readiness/artifact-closeout-matrix.md`
- `docs/product/mini-game-readiness/tmst-golden-path-report.md`
- `docs/superpowers/plans/2026-08-02-mini-game-platform-readiness-program.md`
- `docs/roadmap/tasks/AW-286-couch-race-rehearsal-slice-and-rehearsal-1-retarget.md`
- `docs/specs/0086-scene-sweep-game-ready.md`

## Open questions this decision does not resolve

- Who owns six-beat integration, privacy and device checks, and audiovisual
  polish: AW-286, the program, or a new task. Founder call required.
- How the AW-286 and Order 12 mutual dependency is broken.
- Whether Order 2 proceeds after the golden-path human usability session runs.
- `docs/specs/0086-scene-sweep-game-ready.md` Task 3 Step 3 in the linked plan
  requires removing the generated `run_seed` stopgap. That is a cross-module
  change across `engine/mini_games/resolver.py`,
  `engine/mini_games/plugins/_evidence_search_race.py` line 184, and
  `engine/mini_games/plugins/_social_truth_bluff.py` line 539. It is currently
  off-limits and needs its own approval.
