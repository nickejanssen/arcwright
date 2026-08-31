# Nightcap Master GDD Reconciliation Report

**Status:** Process / provenance record — not game canon by itself  
**Date:** 2026-08-30

## Result

The supplied checkpoints are sufficient to build a coherent master package around the latest Checkpoint 05 authority. The package is internally usable without requiring older conversations for ordinary continuation.

## What Was Promoted Into Current Master Areas

Only documents identified as current by the latest Checkpoint 05 Source Manifest / GDD Index were placed in current governance, authoritative, validation, evidence, supporting-design, or continuation folders. Their contents were copied verbatim before the repository authority migration added a small number of explicitly approved current pages/clarifications.

No older page was promoted into current canon simply because it existed in an earlier checkpoint.

## Important Historical Pages Kept Only in Archive

### Checkpoint 01 — `01-game-overview.md`

This is the original strong one-page promise/experience framing and contains useful project history. It is **not** promoted as current authority because it also says the “strongest correct case” wins primarily through proof coverage. That winner model is superseded by the current Structured Reconstruction decision and deterministic solve outcome.

Its older Content Model also names Story Worlds / Case Foundry. The current decision ledger still carries Content/AI directions such as procedural scalability, hybrid library, evidence-gated autonomy, hybrid generation, continuity, and personalization, but Checkpoint 05 has no dedicated current Content/AI system page. Therefore the old Checkpoint 01 wording remains historical evidence, not a reconstructed current system page.

### Checkpoint 01 — `02-core-gameplay-loop.md`

The early WATCH → HUNT → THINK → PLAY → REACT hypothesis remains historically important, but specific older implementation language is superseded by current system pages and the current endgame. It remains archived rather than duplicated as a second authoritative loop owner.

### Checkpoints 03–04 — `08-postmortem-investigator-personality.md`

The latest source manifest explicitly says this page was consolidated into `08-truth-verdict-postmortem.md`. The old page also listed “abandoned theories” as an input even though the current design now forbids Nightcap from pretending to know unexpressed player thinking. It is safely archived only.

### Intermediate Checkpoint 05 packages

The base Session B and Decisions 1–12 packages are preserved as history. They are superseded by the Decisions 1–17 source and must not be used to roll back newer approvals accidentally.

## Known Gap

**Checkpoint 02 is absent.** No attempt was made to infer or rebuild it. If a future copy is found, it should be reconciled against the current ledger and added to historical provenance; it should not automatically change current canon.

## Current Under-Owned Area Worth Remembering

The decision ledger contains a `Content / AI` section, but the current authoritative file set still does not include a dedicated Content/AI one-pager. The repository migration adds `12-experience-world-content-boundaries.md` only for durable creative/world/content boundaries; it does not manufacture a detailed Content/AI subsystem.

## Archive Safety Rule

Archived documents preserve history, including old DECIDED labels. Those labels describe the state **at that checkpoint**. They do not outrank a later reopening, supersession, or current decision.

## Repository Migration

As of ADR-0023, current Nightcap design authority lives at `docs/gdd/nightcap/`. The former Couch Race and Imposter Story Bibles are preserved under `docs/archive/nightcap-story-bibles/`, while their old paths remain compatibility redirects.

## Recommended Repository Use

Use `00-governance`, `01-authoritative-gdd`, `02-validation`, `03-playtest-evidence`, `04-supporting-design`, and `05-continuation-process` for current Nightcap design work. Archived Story Bibles and historical implementation records are read for provenance/conflict investigation only.
