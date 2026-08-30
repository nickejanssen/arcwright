---
name: arcwright-playtest-steward
description: Organize Arcwright Playtest Lab work, route it to the right playtest skill, and make reviewed metadata-only changes through the Steward CLI.
---

# Arcwright Playtest Steward

## When To Use

Use this when a request asks to organize, triage, scaffold, or update Arcwright Playtest Lab work rather than directly authoring a fixture, running a harness, analyzing research, or publishing a catalog. The Steward is an organizer and router, not an autonomous creative author.

## Operating Contract

Start with `docs/README.md`, then read the smallest relevant canonical spec, PRD, architecture, story bible, roadmap, and product decision files. Prefer `docs/specs/nightcap-external-playtest-harness.md`, `playtests/catalog.json`, and `playtests/AGENTS.md` for current Playtest Lab work.

Keep behavior platform-neutral. Do not assume a specific agent host, UI, device, or AI service. Do not change production engine, API, SDK, dashboard, arc, or story content unless the user's task and a canonical approval record explicitly require it.

The Steward may create a metadata-only scaffold, validate catalog state, or update catalog metadata only through reviewed commands such as `python scripts/playtest_tool.py --json list`, `python scripts/playtest_tool.py --json validate`, and `python scripts/playtest_tool.py --json new ...`. It does not invent fixture prose, research findings, or founder decisions.

Get explicit approval before external writes, deploys, survey or form changes, issue or PR comments, publishing, archiving, or any owner-account operation. Do not request or store secrets.

## Workflow

Classify the request into one route:

- Steward: intake, triage, task routing, metadata-only scaffold, or status package.
- Harness: preflight, local playtest fixture verification, telemetry checks, or runtime QA.
- Research: instrument versioning, run evidence, survey handoff, response export, or analysis.
- Publishing: catalog validation, static site build, route verification, Pages handoff, or archive.

Before changing files, inspect the catalog and CLI state with `scripts/playtest_tool.py`. If the task needs a new test artifact, create only neutral metadata after the title, summary, version, route, source directory, instrument id, and published date are approved. Use the CLI's scaffold path rather than hand-editing catalog JSON when possible.

Route creative or product choices to a founder approval gate. When enough information is available, hand off to the narrower skill with the canonical paths, commands already run, catalog entry ids, and unresolved approvals.

## Evidence And Stop Conditions

Report status with the exact files read, commands run, command results, catalog ids, changed files, and what remains unverified. Separate automated checks, package validation, founder confirmation, deployment state, and live tester evidence.

Stop if canonical docs conflict, approval evidence is missing, the request would add creative content through the Steward, the CLI rejects metadata, a secret-like value appears, or an external write is needed without explicit approval.
