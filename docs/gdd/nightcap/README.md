# Nightcap Master GDD

> Current version: Master GDD / Checkpoint 05 Session B + Decisions 1–17 + source-of-truth migration
> Last updated: 2026-08-31
> Status: Current — canonical Nightcap game-design authority
> Canonical path: docs/gdd/nightcap/README.md

## Authority

This directory is the current source of truth for **Nightcap game design**. It supersedes the former Nightcap Story Bibles as active experience authority.

Read in this order:

1. `00-governance/00-decision-ledger.md`
2. `00-governance/01-master-gdd-index.md`
3. `00-governance/02-current-design-state.md`
4. `02-validation/98-validation-state-and-remaining-plan.md` when validation status matters
5. Only the relevant pages under `01-authoritative-gdd/`

Status vocabulary is exact: **DECIDED, TESTING, OPEN, RECOMMENDATION, PARKED**. A DECIDED item can be reopened by stronger evidence; preserve its history when that happens.

## Precedence

For Nightcap gameplay and experience-design questions:

1. Current GDD decision ledger
2. Current GDD authoritative system pages
3. Current specialist authorities explicitly retained by the GDD, including `docs/design/the-host.md` and `docs/design/nightcap-art-direction.md`
4. Current validation plans and approved specs for their own scope
5. Historical ADRs/product decisions as provenance
6. Archived Story Bibles and other historical design artifacts

A historical implementation decision is not erased. If it conflicts with the current GDD, the GDD defines the desired product state and the implementation difference must be reconciled explicitly before code changes are claimed complete.

## Former Story Bibles

The original Nightcap bibles are archived under `docs/archive/nightcap-story-bibles/`. Their former paths in `docs/story-bibles/` are compatibility redirects only.

## Scope boundary

The GDD is authoritative for Nightcap design. Arcwright platform architecture remains governed by architecture docs and ADRs. Approved implementation specs remain implementation records, but they may be stale relative to newer GDD decisions; use `00-governance/05-repository-migration-and-conflict-policy.md` when reconciling those seams.
