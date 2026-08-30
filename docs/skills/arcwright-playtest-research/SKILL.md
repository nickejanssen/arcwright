---
name: arcwright-playtest-research
description: Version playtest research instruments, capture tester evidence, and report findings while preserving approval gates and data boundaries.
---

# Arcwright Playtest Research

## When To Use

Use this for Playtest Lab research operations: instrument versioning, response schema review, run evidence capture, tester feedback synthesis, survey handoff verification, and deciding what the evidence can and cannot support.

## Operating Contract

Start with `docs/README.md`, then read the active canonical playtest spec, catalog entry, relevant PRD success criteria, and any research or runbook file named by the task. For the current external test, `docs/specs/nightcap-external-playtest-harness.md` defines the instrument boundary and `playtests/catalog.json` records the published version.

Treat every instrument version as evidence infrastructure. Preserve the version, fixture id, instrument id, instrument version, run id rules, and hidden telemetry field list. Do not mix responses from incompatible versions without naming the version boundary.

Use `scripts/playtest_tool.py` to list or validate catalog metadata before relying on a published id or version. Require explicit approval before external writes, survey or form edits, exports from owner accounts, public sharing, issue or PR comments, or publishing changes.

## Workflow

For instrument work, define or verify:

- version: fixture id, fixture version, instrument id, instrument version, published date, and any immutable artifact boundary;
- telemetry: run id, timestamps, duration, action sequence, discoveries, investigation branches, case commitment, device/browser class, completion status, abandonment point, and any added fields named by the spec;
- evidence capture: sample size, tester relationship, device context, completion path, raw export location if approved, and redaction state;
- interpretation: what the data supports, what it does not support, and which product gates remain open.

For new research scaffolds, route metadata-only creation through `scripts/playtest_tool.py` after approval. For analysis, keep raw data private unless the user explicitly asks for a shareable artifact and approves the redaction standard.

For feedback consolidation, produce this structure:

- Dataset boundary: catalog id, fixture version, instrument id, instrument version, submission count, date range, source type, and whether raw data was fetched this turn.
- Telemetry health: which hidden fields are populated, empty, inconsistent, or not available.
- Player experience themes: comprehension, engagement, friction, pacing, solvability, emotional response, and replay intent.
- Evidence strength: high-confidence findings, weak signals, contradictions, and sample-size limits.
- Research gaps: missing tester contexts, missing paths through the fixture, unverified survey handoff, or unverified reveal return.
- Product implications: questions for the GDD, PRD, roadmap, architecture, or telemetry, stated as proposals rather than decisions.
- Founder decisions needed: exact choices required before canonical docs, published artifacts, survey instruments, or implementation change.

Do not turn feedback into canon directly. If findings suggest GDD, product, roadmap, architecture, or telemetry changes, hand the summarized evidence to `arcwright-sme` and keep the final output separated into evidence, interpretation, and proposed decision.

## Evidence And Stop Conditions

Report findings with source paths, version ids, commands run, dataset boundaries, redactions, and confidence level. Separate survey response evidence from live observation and from automated harness telemetry.

Stop if versions are mixed without traceability, approval for external data access is missing, private tester data would be exposed, a fixture tries to become canon product truth, or an external write is needed without explicit approval.
