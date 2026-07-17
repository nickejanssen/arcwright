# M5 Canonical Reconciliation and Tracker Synchronization

**Status**: Draft

**Author**: Codex | **Date**: 2026-07-16

---

# References

- Product decisions: `docs/product/decisions-log.csv` (D-069, D-071, D-072)
- Related ADRs: `docs/decisions/0012-authorial-intent-obligations-continuity-evals.md`, `docs/decisions/0013-nightcap-couch-race-v1-launch-target.md`
- Roadmap: `docs/roadmap/milestones/M5-hardening-proof-prerequisites.md`, `docs/roadmap/index.json`, `docs/roadmap/operations/github-project-setup.md`
- Related specs: `docs/specs/0064-aw-270-authorial-intent-block.md`, `docs/specs/0065-aw-271-narrative-obligations-model.md`, `docs/specs/0068-game-experience-quality-bar.md`, `docs/specs/0069-nightcap-visual-design-system.md`, `docs/specs/0071-live-loop-ai-character-dialogue.md`, `docs/specs/0072-nightcap-couch-race-v1.md`
- Architecture: `docs/architecture/03-arc-execution.md`, `docs/architecture/04-knowledge-graph.md`, `docs/architecture/06-model-routing.md`, `docs/architecture/08-event-system.md`, `docs/architecture/11-telemetry.md`
- PRD: `docs/prd/02-requirements.md`, `docs/prd/03-scope.md`
- Story bible: `docs/story-bibles/nightcap-couch-race.md`

---

# Overview

This specification repairs the M5 documentation graph and synchronizes GitHub
execution records to it. It does not add gameplay scope. It makes the current
Couch Race launch target, M5 proof gate, task records, parent specifications,
and GitHub issues agree on one executable contract.

The result is a complete, traceable M5 portfolio: every active M5 item has a
durable scope source, acceptance criteria, dependencies, roadmap mapping, and
matching GitHub execution record. Post-M6 work remains visible but cannot be
mistaken for an M5 launch dependency.

---

# In Scope

- Audit every M5 roadmap epic, task, parent spec, decision, and open GitHub
  issue against the current `origin/main` documentation snapshot.
- Create canonical task records and `index.json` mappings for approved M5
  work that currently exists only as GitHub issues or a parent spec.
- Correct milestone, epic, dependency, status, and acceptance-criteria drift
  before changing GitHub records.
- Retarget D-069 narrative-pipeline tasks AW-276 through AW-280 to the Couch
  Race experience established by D-071 and ADR-0013.
- Update stale references that contradict merged repository state, including
  the spec 0072 note that PR #225 is unmerged.
- Synchronize issue bodies, labels, and dependency references only after the
  corresponding canonical documentation has been reviewed.

---

# Out of Scope

- Engine, SDK, dashboard, Nightcap web, schema, migration, or prompt changes.
- New gameplay beyond approved D-069, D-071, D-072, and parent spec 0072.
- Free-text or voice interrogation, team play, co-op scoring, the Imposter
  Variant, new visual themes, or asset production.
- Re-sequencing AW-270 or AW-271 into M5 without a later durable founder
  decision.
- Treating a GitHub issue, PR, chat summary, or branch diff as approval for
  new product scope.

---

# Authority and Synchronization Model

All sources below are in GitHub `docs/`; their order resolves a conflict:

1. A current durable product decision and ADR define approved product scope
   and supersede an older incompatible decision.
2. PRD, architecture, story bible, milestone, epic, task, and approved parent
   spec define the product and technical contract for execution.
3. `docs/roadmap/index.json` is the join layer linking canonical records to
   GitHub objects. It must not invent scope or omit approved active work.
4. GitHub issues, labels, milestones, and project fields are execution
   mirrors. They must be updated from canonical docs, never the reverse.

Before each document batch, fetch `origin/main` and inspect the current
decision log, affected specs, roadmap records, and changed files. Before each
GitHub batch, re-check those records plus each affected issue's `updatedAt`.
If a newer durable decision conflicts with this spec, stop that batch and
reconcile the decision in documentation first.

---

# Required Reconciliations

## 1. Post-M6 narrative-fidelity tasks

AW-270 and AW-271 remain Post-M6. Their task records and `index.json` already
identify that status, and both task records prohibit implementation before M6
exit. GitHub issues #202 and #203 must lose the `M5` label and must not appear
as M5 exit-gate work. Their issue bodies may retain their existing Post-M6
contract.

## 2. AW-275 visual-system follow-up

AW-275 is approved M5-G follow-up work under spec 0069 and GitHub issue #223.
Create its canonical task record and `index.json` entry, map it to M5-G, and
give the issue matching M5, task, and size metadata. The canonical task record
and manifest carry the M5-G epic relationship unless the tracker convention
explicitly supports epic labels. Its scope remains
limited to semantic token cleanup and keyboard focus visibility in
`nightcap-web`; it must not create engine or API work.

## 3. D-069 narrative-pipeline tasks retargeted to Couch Race

D-069 approved AW-276 through AW-280 before Rehearsal 1. D-071 and ADR-0013
changed the launch experience from player-killer murder mystery to Couch Race:
all players are rival investigators and the killer is an AI suspect. The
following canonical task records and `index.json` entries are required before
their GitHub issues are updated:

| Task | Canonical Couch Race contract |
| --- | --- |
| AW-276 | Inject an arc-declared, cacheable voice block into eligible generation paths without game-specific engine vocabulary. |
| AW-277 | Compose narrator transition lines, including the cold open, from resolved six-beat state; emit only structured content events and D-070 presentation hints. |
| AW-278 | Compose the shared Truth sequence and reveal accounting from already-resolved case truth, authorized lies, and provenance. It must not privately reveal a player-killer. |
| AW-279 | Deliver a light detective identity and opening briefing. It may contain name and flavor for address and scoreboard personality, but no hidden role, secret, or performance burden. |
| AW-280 | Compose and release fair clue content from deterministic case truth, with provenance, audience targeting, and evidence-to-intent unlock semantics. |

Each task must name its six-beat target, source state, audience, privacy rule,
presentation-hint behavior, acceptance evidence, and architecture constraints.
AW-286 records the final Rehearsal 1 beat alignment and must link to all five
records.

## 4. M5-I and M5 exit gate

M5-I, AW-281 through AW-286, and parent spec 0072 are the authoritative Couch
Race delivery path. Preserve their explicit dependencies and ensure every
related M5 record points to the Couch Race story bible, not the Imposter
Variant as the v1 experience. Update spec 0072 to record that the live-loop
dialogue dependency introduced by PR #225 is now merged on `origin/main`.

M5 exit evidence must continue to include the Couch Race real-device thin
slice and AW-272 batch continuity input. A mapped task cannot claim the gate
is satisfied without the required test or rehearsal evidence.

---

# Architecture and Product Guardrails

- Case truth, authorized lies, clue web, scoring, and state transitions resolve
  deterministically before any generation. AI does not decide what happened.
- A knowledge-state query remains mandatory before every AI suspect response
  or other character generation.
- Python owns runtime, session state, knowledge, safety, routing, and API
  logic. TypeScript remains rendering, subscription, and input submission.
- Engine events remain surface-agnostic. They carry audience and presentation
  hints, not TV or phone rendering logic.
- Private evidence, tells, and accusations never render on a shared display.
  Couch Race detective identities contain no hidden role information.
- All generation routes through the task-type and quality-tier abstraction;
  no provider or model name is introduced outside the approved routing files.
- Content quality, cost telemetry, replay intent, knowledge-constraint
  activations, beat engagement, and completion evidence remain testable M5
  proof signals.

---

# Acceptance Criteria

- [ ] Every active M5 roadmap task and implementation issue is represented in
  a reconciliation matrix with canonical source, owner epic, status,
  dependencies, acceptance evidence, and GitHub mapping.
- [ ] Every open M5 issue maps to an existing canonical task record or an
  approved parent spec with an explicit child-task relationship.
- [ ] AW-275 through AW-280 have canonical records and `index.json` mappings
  before their GitHub issues are altered.
- [ ] AW-276 through AW-280 contain no player-killer, secret-player-role, or
  eight-beat-launch assumptions.
- [ ] GitHub issues #202 and #203 no longer carry M5 execution metadata;
  their Post-M6 status remains explicit.
- [ ] M5-I and the M5 milestone exit gate map Couch Race proof work to
  AW-281 through AW-286 and AW-272 without broken links or stale dependencies.
- [ ] Spec 0072 no longer describes the merged PR #225 dependency as
  unmerged.
- [ ] No change violates deterministic authority, knowledge gating, surface
  agnosticism, privacy, provider agnosticism, or cost-aware routing.
- [ ] A final `origin/main` plus GitHub review finds no scope conflict,
  missing canonical path, or tracker-only M5 scope.

---

# Test Plan

- Documentation checks: parse `docs/roadmap/index.json`; verify each mapped
  `doc_path` exists; verify each task link resolves; verify M5 and Post-M6
  classifications agree across task records, milestone/epic records, and the
  manifest.
- Contract review: compare every changed GitHub issue body and label against
  its canonical task record and cited parent spec before publishing.
- Architecture review: validate each retargeted AW-276 through AW-280 record
  against the Couch Race story bible and the guardrails above.
- Regression baseline: run `pytest engine/tests -q` with an isolated pytest
  base-temp directory. The expected baseline is 496 passed, 1 skipped when
  `DATABASE_URL` is not set.
- Manual tracker review: inspect the M5 milestone, M5-G, M5-I, and every
  changed issue after synchronization.

---

# Risks and Unknowns

**Risks**:

- A GitHub issue may be edited after the documentation snapshot and before
  synchronization. The second `updatedAt` check prevents overwriting it.
- A parent spec may have accurate scope but stale delivery status. Update only
  the stale status/reference, not the approved contract, unless a newer
  decision requires it.
- Copying D-069's original player-killer language would ship the wrong product.
  The Couch Race retarget is mandatory before implementation planning.

**Unknowns**:

- The final issue-level dependency representation must use the repository's
  current GitHub tracker convention. The canonical dependency graph remains
  `index.json` until that convention is verified.
- Rehearsal evidence and real-device latency remain future execution evidence,
  not documentation claims. They stay open until AW-286 produces them.

---

# Open Questions

None block this reconciliation. Any future request to move AW-270 or AW-271
into M5 requires a new durable product decision and an explicit roadmap
re-sequencing update.
