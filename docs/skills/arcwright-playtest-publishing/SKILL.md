---
name: arcwright-playtest-publishing
description: Verify and build Arcwright Playtest Lab catalog and static publishing artifacts while preserving immutable published history and external-write approvals.
---

# Arcwright Playtest Publishing

## When To Use

Use this for Playtest Lab publishing work: catalog validation, route checks, static site builds, archive preparation, GitHub Pages handoff, deployment evidence, and public artifact status reporting.

## Operating Contract

Start with `docs/README.md`, then read the active canonical playtest spec, `playtests/catalog.json`, `scripts/playtest_catalog.py`, `scripts/build_playtest_site.py`, and `scripts/playtest_tool.py` when those files affect the requested publishing action.

Publishing is metadata and static artifact management. It must not alter production engine, API, SDK, dashboard, arc behavior, or story canon. Published artifact history is preserved. Archive through metadata rather than deleting or moving existing published artifacts.

Use `scripts/playtest_tool.py` for catalog list, validate, scaffold, archive, and build actions where available. Require explicit approval before external writes, deploys, Pages changes, survey changes, public links, or issue and PR comments.

## Workflow

Verify the publishing chain in order:

- Catalog: run `python scripts/playtest_tool.py --json validate` and confirm schema version, current tests, ids, routes, source directories, instrument ids, and versions.
- Build: run `python scripts/playtest_tool.py --json build --output <local-output>` or the deterministic builder directly when a local artifact is requested.
- Routes: inspect generated index, game index, catalog data, copied fixture files, and legacy URLs if present.
- Archive or promote: use exact ids, preserve source directories, keep immutable published versions, and record why a current entry changed.
- External handoff: before deploying or updating public infrastructure, present the planned write and wait for explicit approval.

## Evidence And Stop Conditions

Report the exact command outputs, generated output path, catalog diff, route checks, deployment state, and what was not live-smoke-tested. Do not describe a deployment as live unless the deployment URL was checked after the current build.

Stop if catalog validation fails, a generated route escapes the expected public base path, an archive would delete artifact history, approval for an external write is missing, or a task asks publishing to add creative fixture content.
