---
id: productroadmap.roadmap.tasks.aw-309-build-versus-adopt-review-for-the-layers-session-1-needs
namespace: product-roadmap
title: "AW-309: Build-Versus-Adopt Review For The Layers Session 1 Needs"
owner: Nico Janssen
status: active
review_by: "2027-02-15"
sensitivity: internal
source: authored
x-scope-evidence: D-114
tags: []
supersedes: []
---

# AW-309: Build-Versus-Adopt Review For The Layers Session 1 Needs

**Milestone / Epic:** M7 / M7-B  
**Size:** M  
**Product:** Shared (Arcwright and Nightcap)  
**Owner:** One AI build session (Claude or Codex)  
**Target date:** 2026-11-25

## Plain-English Summary

Apply the build-versus-adopt rule (ADR-0026) to each layer the thin version needs: screens, motion, voice, sound. Say for each whether to keep what exists, adopt something, or wait.

## Why This Matters

The Nightcap web client is about 5,300 lines with no third-party libraries, the clearest current case of building what exists. The rule is recorded; this task applies it before the screens spec is written.

## Technical Scope

- Screens: one client; React is already in the repository through `dashboard/`.
- Motion: Rive (MIT runtime; free editor; exports carry a splash screen until a paid seat).
- Voice: Kokoro (Apache-2.0, self-hosted), or the ElevenLabs or Inworld free tiers. The ElevenLabs free plan carries no commercial licence.
- Sound: Howler.js (MIT).
- For each: cost against the budget in ADR-0026, licence, what it replaces, and when.
- Take voices from a product; never let a talking-character product decide what a character says.

## Human Collaboration Contract

**Interaction profile:** Independent execution, then founder choice on any paid option or new dependency.

## Acceptance Criteria

- [ ] One table, one row per layer, with a recommendation and a verified licence and price.
- [ ] Anything needing a new dependency or a paid plan is raised to the founder as one decision each.
- [ ] The result is reflected in section 2.11 of `docs/architecture/02-technology-stack.md`.

## Tests/Verification

- Licence and pricing pages re-checked on the day, with dates in the table.

## Dependencies

- None
- Findings and evidence: `docs/product/2026-11-15-reset-audit.md`

## Must Not Do

- Install nothing, sign up for nothing and spend nothing without founder approval.
