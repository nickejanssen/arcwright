---
name: arcwright-playtest-steward
description: Organize Arcwright Playtest Lab work, route it to the right playtest skill, and make reviewed metadata-only changes through the Steward CLI.
---

# Arcwright Playtest Steward

## When To Use

Use this when a request asks to organize, triage, scaffold, or update Arcwright Playtest Lab work rather than directly authoring a fixture, running a harness, analyzing research, or publishing a catalog. The Steward is an organizer and router, not an autonomous creative author.

Use this as the one-stop shop for Playtest Lab requests when the user says or implies any of: add a case, add a test, update the harness, analyze feedback, inspect Jotform, consolidate responses, improve the GDD from feedback, update product docs, update architecture from findings, prepare Pages, archive an old test, promote a current test, or tell me what is verified.

## Operating Contract

Start with `docs/README.md`, then read the smallest relevant canonical spec, PRD, architecture, current experience authority, roadmap, and product decision files. For Nightcap, the current experience authority begins at `docs/gdd/nightcap/README.md` and its decision ledger; the archived Story Bibles are not current canon. Prefer `docs/specs/nightcap-external-playtest-harness.md`, `playtests/catalog.json`, and `playtests/AGENTS.md` for current Playtest Lab work.

Keep behavior platform-neutral. Do not assume a specific agent host, UI, device, or AI service. Do not change production engine, API, SDK, dashboard, arc, or story content unless the user's task and a canonical approval record explicitly require it.

Reuse existing architecture, docs, skills, agents, catalog entries, scripts, and role contracts before proposing anything new. Do not delete, replace, or fork an existing SME, skill, catalog structure, fixture route, or canonical document to simplify routing. If existing structures overlap or seem incomplete, summarize what exists, preserve important information, ask the user how to proceed, and provide clear options.

The Steward may create a metadata-only scaffold, register an already founder-approved existing fixture as a draft, validate catalog state, or update catalog metadata only through reviewed commands such as `python scripts/playtest_tool.py --json list`, `python scripts/playtest_tool.py --json validate`, and `python scripts/playtest_tool.py --json new ...`. Existing-fixture registration must use `new --use-existing-source`; it validates the candidate catalog and must not create, delete, or rewrite fixture files. Unpublished drafts may record `published: null`. The Steward does not invent fixture prose, research findings, or founder decisions.

Get explicit approval before external writes, deploys, survey or form changes, issue or PR comments, publishing, archiving, or any owner-account operation. Do not request or store secrets.

## Workflow

Classify the request into one route:

- Steward: intake, triage, task routing, metadata-only scaffold, existing-fixture draft registration, or status package.
- Harness: preflight, local playtest fixture verification, telemetry checks, or runtime QA.
- Research: instrument versioning, run evidence, survey handoff, response export, or analysis.
- Publishing: catalog validation, static site build, route verification, Pages handoff, or archive.
- SME: product, GDD, architecture, roadmap, decision-log, or canon implications after evidence has been summarized.

Before changing files, inspect the catalog and CLI state with `scripts/playtest_tool.py`. If the task needs a new test artifact, create only neutral metadata after the title, summary, version, route, source directory, and instrument id/version are approved. Use the CLI's scaffold path for a not-yet-created source directory. If founder-approved fixture content already exists, use `new --use-existing-source` so registration cannot overwrite it. Do not invent a publication date for a draft that has not been published.

Route creative or product choices to a founder approval gate. When enough information is available, hand off to the narrower skill with the canonical paths, commands already run, catalog entry ids, and unresolved approvals.

For feedback-to-product work, route in this order:

1. Research: consolidate feedback, telemetry, sample boundaries, confidence, and evidence limits.
2. SME: map findings to GDD, PRD, architecture, roadmap, specs, ADRs, or decision logs.
3. Founder gate: identify the exact decisions needed before docs or implementation change.
4. Steward: package approved next actions into metadata, issue, spec, or archive/publish work.

## One-Stop Prompts

Use these prompts as stable entry points:

```text
Use arcwright-playtest-steward as the one-stop shop for this Playtest Lab task. Route to harness, research, publishing, or SME as needed. Keep external writes gated for approval.
```

```text
Use arcwright-playtest-steward to consolidate feedback for <catalog id>, route to research for analysis, then route to SME for GDD, product, and architecture implications.
```

```text
Use arcwright-playtest-steward to create a metadata-only draft for a new <game> playtest case after checking catalog validity and approval gates. If the approved fixture source already exists, register it with `new --use-existing-source` instead of overwriting it.
```

## Evidence And Stop Conditions

Report status with the exact files read, commands run, command results, catalog ids, changed files, and what remains unverified. Separate automated checks, package validation, founder confirmation, deployment state, and live tester evidence.

Stop if canonical docs conflict, approval evidence is missing, the request would add creative content through the Steward, the CLI rejects metadata, a secret-like value appears, or an external write is needed without explicit approval.
