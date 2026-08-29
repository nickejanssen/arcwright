# Nightcap External Playtest Harness

**Status**: In Progress

**Author**: OpenAI | **Date**: 2026-08-28

---

# References

- Canonical Nightcap GDD: `docs/story-bibles/nightcap-murder-mystery.md`
- Repo guardrails: `AGENTS.md`
- Paper Test #2 v2/v2.1 supporting evidence supplied by founder

---

# Overview

Define the smallest disposable external playtest surface for Nightcap Paper Test #2 v2.2: static browser UI, silent anonymous run telemetry, post-play Jotform research, and GitHub Pages hosting.

This spec defines research tooling only. It does not approve or alter Nightcap production gameplay.

# Human Collaboration Contract

**Interaction profiles:** Independent execution + Decision interview (privacy/deployment external-service constraints) + Facilitated live operation (future playtest only).

**Classification rationale:** The founder supplied explicit implementation constraints and directed implementation. Third-party account configuration and live tester observations remain owner/facilitator actions.

**Required founder inputs:** One GitHub Pages enablement action; verify Jotform hidden-field Unique Names after form generation.

**Approval evidence:** Founder prompt dated 2026-08-28 explicitly directs assessment followed by implementation with static HTML/CSS/JS, GitHub Pages preference, external form collection, versioning, telemetry, and no production infrastructure.

# Supplied Game Design Boundaries

- Investigation/deduction remain central.
- Gameplay precedes research questions.
- Confirm discovered facts, never inferred truth.
- Representative slice should include story, investigation, information use/reaction, competitive/social pressure, a short story-wrapped party/minigame pulse, consequence, resumed investigation, and lightweight commitment.
- Existing Room With No Door fixture is non-canon test material.

# Harness Decisions

- Static HTML/CSS/vanilla JavaScript under `playtests/`.
- No dependencies or build step.
- Content/config separated from runtime code.
- Session-scoped anonymous run ID and coarse device/browser classification only.
- `sessionStorage` preserves accidental refresh state; Restart generates a new run.
- Human-readable telemetry is URL-prefilled into Jotform after the playable slice.
- Explicit early-exit path records `completion_status=abandoned`; closed-tab abandonment is deferred.
- GitHub Actions deploys only the playtest folder to GitHub Pages.

# Missing Game Design — Not Approved Here

The harness does not approve exact v2.2 suspect/evidence logic, social competition rules, Leverage behavior, minigame rules/scoring, production Case Board UX, or production consequence tuning. Fixture interactions needed to exercise those harness slots remain explicitly NON-CANON.

# Privacy Constraint

The prototype asks for no name, email, account, persistent identity, advertising identifier, or cross-run identifier. Jotform may retain service-level technical metadata such as submitter IP; this limitation must remain documented. No additional analytics are enabled.

# Acceptance Criteria

- [x] Static site runs in modern browsers without installation or account.
- [x] Gameplay contains no research prompts.
- [x] Anonymous session telemetry accumulates silently.
- [x] Refresh can resume a run; restart creates a new run.
- [x] Post-play boundary clearly labels research.
- [x] Jotform handoff includes configurable hidden-field prefill mapping.
- [x] Test version is automatically attached.
- [x] Content can be changed in one config file.
- [x] No production Arcwright/Nightcap engine code is modified.
- [ ] GitHub Pages is enabled for the repository and the public URL is live.
- [ ] Jotform generated field Unique Names are verified against `config.js` before collecting research evidence.

# Test Plan

- Node built-in unit tests for run IDs, ordered telemetry, duration/status, CSV-friendly serialization, and feedback URL prefill.
- Static server smoke test for `index.html`.
- Static assertions for mobile viewport, tap target sizing, post-play research boundary, and voluntary exit path.
- Live phone/desktop smoke test after GitHub Pages enablement.

# Known Research Limitations

- Closed-tab/connection-loss abandonment cannot be observed without event ingestion.
- Incomplete Jotform submissions cannot be distinguished from survey non-entry without more infrastructure.
- The included v2.2-shaped reaction/pulse content is harness fixture material, not validated game design.
