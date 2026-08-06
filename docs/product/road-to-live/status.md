> Current version: v1.2
> Last updated: 2026-08-05
> Status: Current
> Canonical path: docs/product/road-to-live/status.md

# Road to Live Status

This record reconciles the "Road to Live" program against repo state as of
2026-08-04, superseding the 26 Jul artifact snapshot's completion picture. It
does not revise any prior approval or decision; it records what has changed
since that snapshot.

## Spot-checked facts

Verified directly against the repository on 2026-08-04:

- AW-276 (Arc Voice Block Injection): recorded status is `Done (PR #231)` in
  `docs/roadmap/tasks/AW-276-arc-voice-block-injection.md` line 5.
- `nightcap/content/` does not exist in the repo. No engine or API source file
  references `line-libraries` or `line_libraries` as a read path; all matches
  for that term are documentation under `docs/design/line-libraries/` and
  related planning docs. There is no engine reader for the 468 authored lines
  in the line-library docs.
- `git status --short --branch` is clean. Local `main` and `origin/main` are
  both at `dc56b7fab5d64205312016fce1e16e046c4860b1`.

## Done since the 26 Jul Road to Live artifact snapshot

- **Stage 0 credentials, issue #264**: closed 2026-08-01. Live two-player
  rehearsal joins, starts, and transitions pour to scene on real devices;
  automated smoke passes. Hidden blockers fixed en route: wrong default arc,
  missing `rehearsal-start` make target, token leaking into a URL, and
  Firebase preflight gaps.
- **AW-287 Leverage payout**: merged (PR #251, PR #253). The prior artifact's
  "minigames don't pay Leverage" finding is closed; the win-to-currency-to-
  sabotage loop exists.
- **AW-285**: complete to accepted Phase 1 structural scope (PR #269). The
  shared-display projection layer exists. Six-beat integration, privacy and
  device checks, and audiovisual polish remain open under AW-286. **AW-286 owns
  that scope**, confirmed 2026-08-05 by D-101. The mini-game readiness program
  supplies certified packages into it and is not a gate on it. This line was
  previously in conflict with the closeout matrix; both records now agree. See
  `docs/decisions/0020-aw-286-owns-remaining-couch-race-integration.md`.
- **AW-281, AW-282, AW-283, AW-284**: all Complete. PR #277 (2026-08-04)
  corrected their task files, which were stale at Planned or In Progress.
- **AW-276 Arc Voice Block Injection**: Done (PR #231), unblocking AW-277
  through AW-280.
- **Parallel track the 26 Jul artifact did not anticipate**: the mini-game
  readiness program. Scene Sweep backend and design shipped (PR #273, PR
  #274). Browser-first mini-game platform specs 0077 through 0080 are
  partially implemented (PR #275, merged as `78166d4` on 2026-08-04, decision
  D-099). Scope is capped at the browser golden path; further slices are
  gated on founder execution approval. See
  `docs/product/mini-game-readiness/mainline-safety-report.md` and
  `docs/product/mini-game-readiness/artifact-closeout-matrix.md` for the
  full record.

## Still unmoved

- **AW-290 to AW-291 (Vesper's voice)**: Planned, zero PRs. The 468 authored
  lines in `docs/design/line-libraries/` remain docs-only prose with no
  engine reader (confirmed above). This is the largest unclosed gap in the
  program.
- **AW-288 / AW-289**: Planned, blocked on founder creative approval.
- **AW-277 through AW-280**: Planned but unblocked now that AW-276 is done.
  Each carries a creative gate.
- **AW-286 and Stage 6+ (art)**: untouched, correctly sequenced after the
  items above.

## Open founder decisions

Recorded as blocking and unresolved:

- Approve the AW-289 Interrogation Room creative brief.
- ~~Greenlight, or decline to greenlight, the next slice of the mini-game
  readiness program.~~ Answered 2026-08-05 by D-100: no execution approval
  beyond the merged browser golden path. The decision is deferred to a second
  pass that runs only after the ownership question below is settled.
- ~~Assign a single owner for the remaining AW-285 scope and break the AW-286
  versus program mutual dependency.~~ Answered 2026-08-05 by D-101: AW-286 owns
  it; the program is a supplier, not a gate. Recorded in
  `docs/decisions/0020-aw-286-owns-remaining-couch-race-integration.md`.
- ~~Re-decide mini-game readiness program execution (the second pass ADR 0019
  called for).~~ Answered 2026-08-05 by D-102: the program is **deferred in
  full** until AW-286 Rehearsal 1 has run and been debriefed. Scope stays capped
  at the merged browser golden path. Capacity redirects to the Couch Race
  content path (AW-277 to AW-280, AW-290, AW-291). Recorded in
  `docs/decisions/0021-minigame-readiness-program-deferred-until-after-rehearsal-1.md`.

No founder decisions from the 2026-08-05 mini-game readiness review remain open.
The AW-289 creative brief above is the only carried-over blocking item.

## Nightcap trademark status

Still open. `docs/product/open-questions-log.csv` records: "Has trademark
counsel cleared Nightcap for registration in Class 41 and 9?" as Critical
priority, status Open, with conflicts identified against Studio Nightcap
(Pittsburgh indie studio, murder mystery genre) and NBA Nightcap (Amazon
Prime, Class 41 entertainment). Fallback committed: Revel. The log directs
that Nightcap must not be used in public launch materials until cleared, and
that resolution requires a separate counsel engagement before public launch
of the game.
