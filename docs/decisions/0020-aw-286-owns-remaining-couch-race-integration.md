# 0020 - AW-286 Owns Remaining Couch Race Integration; the Mini-game Program Is a Supplier

**Date:** 2026-08-05
**Status:** Accepted
**Decision authority:** Founder decision recorded 2026-08-05 (D-101)
**Resolves:** the open ownership question in `docs/decisions/0019-minigame-readiness-execution-gated-on-ownership-reconciliation.md`
**Roadmap references:** AW-285, AW-286 (issue #240), M5-I, M6

---

# Status

**Accepted**

---

# Context

ADR 0019 recorded that three canonical records disagreed about who owned the
remaining AW-285 scope, and that AW-286 and the mini-game readiness program each
listed the other as a dependency. It held all further program execution and
explicitly declined to assign an owner, since that was a founder call.

The founder made the call on 2026-08-05.

The disputed scope is the work left over after AW-285 Phase 1 merged as PR #269
(`7aa3f92`): six-beat mini-game integration, privacy and device checks, and
audiovisual polish.

The circular dependency was:

- `docs/roadmap/tasks/AW-286-couch-race-rehearsal-slice-and-rehearsal-1-retarget.md`
  listed "the Mini-game Platform and Nightcap Readiness Program's
  six-opportunity, device, and real-player certification gates" as an AW-286
  dependency.
- `docs/superpowers/plans/2026-08-02-nightcap-existing-minigames-game-ready.md`
  Task 6, the program's order 12 plan, was titled "Run AW-286 Real-player
  Rehearsal and Remediate" and listed the AW-286 task file among the files it
  modifies.

---

# Decision

**AW-286 owns the remaining AW-285 scope.** Six-beat mini-game integration,
privacy and device checks, and audiovisual polish are AW-286 deliverables.

**The Mini-game Platform and Nightcap Readiness Program is a supplier, not a
gate.** It supplies certified mini-game packages and adaptations that AW-286 may
consume. It does not gate AW-286, does not own the rehearsal, and cannot hold
AW-286 open.

The dependency direction is therefore one-way: program to AW-286. AW-286
proceeds with whatever certified candidates exist at rehearsal time. Where no
certified candidate exists for an authored beat, AW-286 records a deliberate
unbound decision with the authored story fallback rather than waiting.

---

# Consequences

## Positive consequences

- The circular dependency is broken. Rehearsal 1 has a definite owner and a
  path that does not depend on unbuilt platform slices.
- Rehearsal 1 is no longer blocked by the program. Six of the beats can be
  bound, or deliberately left unbound, from what exists today.
- The three previously conflicting records now agree, and each carries a
  pointer to this ADR.
- The mini-game readiness program becomes freely deferrable. Deferring it costs
  mini-game breadth at Rehearsal 1, not the rehearsal itself.

## Negative consequences

- AW-286 grows. It absorbs integration, privacy, device, and polish scope on
  top of its existing rehearsal-operations and facilitated-live-operation
  scope, while its recorded size is still `M`.
- AW-286's interaction profile was facilitated live operation. It now also
  carries build scope, so it spans two collaboration profiles and may need to
  be split.
- Rehearsal 1 will likely run with fewer than six beats carrying mini-games.
  `nightcap/couch-race.arc.json` binds only `scene` and `twist` today, and
  three of the six assumed packages do not exist on disk.

## Trade-offs

Gained: a single owner, a one-way dependency, and a Rehearsal 1 path
independent of platform work. Lost: the guarantee of six-beat mini-game
coverage at Rehearsal 1, and a clean single-profile AW-286.

---

# References

- `docs/decisions/0019-minigame-readiness-execution-gated-on-ownership-reconciliation.md`
- `docs/product/decisions-log.csv`, D-100 and D-101
- `docs/roadmap/tasks/AW-286-couch-race-rehearsal-slice-and-rehearsal-1-retarget.md`
- `docs/product/road-to-live/status.md`
- `docs/product/mini-game-readiness/artifact-closeout-matrix.md`
- `docs/superpowers/plans/2026-08-02-nightcap-existing-minigames-game-ready.md`
- `docs/decisions/0013-nightcap-couch-race-v1-launch-target.md`

## Open questions this decision does not resolve

- **Re-decide mini-game readiness program execution.** ADR 0019 deferred this
  to a second pass gated on the ownership call. That gate is now cleared, and
  the premise has changed: with the program reclassified as a supplier,
  deferring it no longer blocks AW-286 or Rehearsal 1. Founder decision
  outstanding.
- **AW-286 re-estimation and possible split.** Size is still recorded as `M`
  against materially larger scope, and the task now spans build and facilitated
  live operation. Routed to the Planner.
- The `run_seed` cross-module change noted in ADR 0019 remains off-limits and
  unapproved.
