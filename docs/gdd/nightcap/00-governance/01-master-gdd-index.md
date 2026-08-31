# Nightcap Master GDD Index

**Master package date:** 2026-08-30  
**Current canonical source:** Checkpoint 05 / Session B / Decisions 1–17 / Structured Reconstruction + Case Graph  
**Purpose:** one durable Nightcap GDD package containing current canon, validation state, playtest evidence, supporting design-control artifacts, continuation material, and complete supplied checkpoint history.

## Required Read Order for a Fresh Session

1. `00-governance/00-decision-ledger.md`
2. `00-governance/01-master-gdd-index.md` (this file)
3. `00-governance/02-current-design-state.md`
4. `02-validation/98-validation-state-and-remaining-plan.md`
5. Load individual pages in `01-authoritative-gdd/` only as needed.
6. Use supporting-design material only for adversarial/cohesion work; those files are not canon by themselves.
7. Use playtest evidence only as evidence. Test findings do not silently become design decisions.
8. Use archived checkpoint/source material only for provenance/history unless the current ledger explicitly reopens an older decision.

## Status Vocabulary

Use these statuses exactly:

- **DECIDED** — explicitly approved current Nightcap design. It may be reopened by stronger evidence.
- **TESTING** — preferred direction awaiting evidence.
- **OPEN** — unresolved.
- **RECOMMENDATION** — proposal, not approved canon.
- **PARKED** — deliberately deferred.

## Current Authority

### Governance

- `00-governance/00-decision-ledger.md` — highest-level approval/status authority.
- `00-governance/02-current-design-state.md` — compact current Nightcap North Star.
- `00-governance/05-repository-migration-and-conflict-policy.md` — repository authority/precedence and Story Bible migration rules.

### Authoritative GDD pages

- `01-authoritative-gdd/02-investigation-deduction.md`
- `01-authoritative-gdd/03-case-board-memory.md`
- `01-authoritative-gdd/04-minigame-competitive-pulse.md`
- `01-authoritative-gdd/05-last-call-case-file.md`
- `01-authoritative-gdd/06-story-reactivity-reentry.md`
- `01-authoritative-gdd/07-espionage-leverage-update.md`
- `01-authoritative-gdd/08-truth-verdict-postmortem.md`
- `01-authoritative-gdd/09-player-count-scaling.md`
- `01-authoritative-gdd/10-difficulty-accessibility.md`
- `01-authoritative-gdd/11-arcwright-runtime-boundary.md`
- `01-authoritative-gdd/12-experience-world-content-boundaries.md`

## Validation

- `02-validation/94-difficulty-accessibility-validation-plan.md`
- `02-validation/98-validation-state-and-remaining-plan.md`
- `02-validation/98b-paper-test-02-v2.2-handoff-requirements.md`

The external GitHub Pages harness, Jotform survey, deployment code, and telemetry implementation are intentionally outside this GDD directory.

## Specialist Authorities

- `docs/design/the-host.md` — Vesper's character/voice authority where it does not conflict with the GDD.
- `docs/design/nightcap-art-direction.md` — Nightcap visual authority where it does not conflict with the GDD.

## Archive Rule

Former Nightcap Story Bibles live under `docs/archive/nightcap-story-bibles/`. Their old paths are redirect stubs. Archived documents may contain stale or superseded rules. **Never treat archive recency, filename similarity, or older Current/Accepted/DECIDED labels as authority over the current decision ledger.**

## Known Missing Source

**Checkpoint 02 was not supplied during the checkpoint consolidation.** It was not reconstructed from conversation memory or generic design knowledge.
