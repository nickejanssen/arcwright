---
name: arcwright-playtest-harness
description: Run Arcwright Playtest Lab harness preflight, fixture checks, telemetry checks, and evidence reporting without changing production runtime modules.
---

# Arcwright Playtest Harness

## When To Use

Use this for preflight, QA, troubleshooting, or status reporting on a Playtest Lab harness or fixture. This includes static runtime checks, fixture tests, telemetry field checks, refresh or re-entry checks, survey handoff checks, mobile layout checks, and local smoke evidence.

## Operating Contract

Start with `docs/README.md`, then read the active playtest spec, catalog entry, fixture README, and any fixture-local `AGENTS.md` before running or changing harness files. For the current Nightcap fixture, include `docs/specs/nightcap-external-playtest-harness.md`, `playtests/catalog.json`, and `playtests/nightcap-paper-test-02-v2.2/README.md` when relevant.

Keep this work outside production engine, API, SDK, dashboard, and canonical arc modules. A static playtest harness is research infrastructure. It does not prove production multiplayer, real-device readiness, fun, or live deployment unless those checks were actually performed.

Use `scripts/playtest_tool.py` to validate catalog state before and after harness work that depends on published metadata. Require explicit approval before external writes, deploys, survey changes, or publishing actions.

## Workflow

Preflight the harness in layers:

- Catalog: run `python scripts/playtest_tool.py --json validate` and verify the current id, route, source directory, instrument id, and instrument version.
- Fixture: inspect the fixture-local README and tests, then run the focused JavaScript or browser checks available for that fixture.
- Telemetry: confirm required fields are emitted, versioned, and stable across ordinary completion, abandonment, refresh, survey handoff, and reveal return paths.
- Evidence: record commands, exact outputs, viewport or device claims, known gaps, and whether the check is automated, manual, or external.

When diagnosing failures, identify the first broken layer before proposing a fix. Do not widen into production runtime changes unless the user explicitly asks and canonical docs approve that scope.

## Evidence And Stop Conditions

Report evidence-backed status only. Say "not verified" for any live device, external survey, deployment, or tester claim that was not directly checked in the current run.

Stop if the catalog is invalid, the fixture source does not match the catalog, telemetry fields would need unapproved instrument changes, a production module change appears necessary, or an external write is needed without explicit approval.
