# Playtest Lab Agent Rules

> Current version: v1.0
> Last updated: 2026-08-29
> Status: Current
> Canonical path: playtests/AGENTS.md

These rules apply to every human or AI agent working inside `playtests/`.
The Playtest Lab is research tooling for published test artifacts. It is not
Nightcap canon and it is not production Arcwright runtime code.

## Naming

- Use stable lowercase IDs with hyphenated words and a version suffix, for
  example `nightcap-paper-test-02-v2.2`.
- Keep public routes permanent and versioned, for example
  `/nightcap/paper-test-02/v2.2/`.
- Match each catalog entry to one source directory under `playtests/`.
- Do not reuse an ID, route, or source directory for a different test.

## Immutable Versioning

- Published versions are immutable. Do not edit a published artifact in place.
- Material fixture, telemetry, route, or research-instrument changes require a
  new version and a new catalog entry.
- Historical routes must continue to resolve after newer tests are published.
- The catalog may add metadata for discovery and archival state, but it must not
  rewrite the substance of an archived artifact.

## Archive Rules

- Archive by exact catalog ID only.
- Archiving changes catalog metadata only. It must preserve the artifact
  directory, route history, instrument references, and publication metadata.
- Archived entries stay readable and must not become the target of `current_tests`.
- Do not mutate archived entries except to correct catalog metadata with explicit
  founder approval and a documented reason.

## Canon Boundaries

- Test fixtures under `playtests/` are non-canon unless a canonical doc says
  otherwise.
- Do not treat a playtest fixture, survey response, or generated page as a
  change to the Nightcap story bible, PRD, architecture, roadmap, or production
  game rules.
- Production engine, API, SDK, dashboard, database, and routing behavior must
  not import or depend on Playtest Lab helpers.
- Fixture content changes require founder approval before implementation.

## Telemetry

- Every external test must declare telemetry fields and instrument handoff in
  its README or companion spec.
- Keep telemetry anonymous and session scoped unless a canonical privacy or
  research decision explicitly approves otherwise.
- Do not add secrets, credentials, private tokens, or hidden owner-only data to
  fixture files, catalog metadata, URLs, or generated pages.
- Record abandoned, incomplete, and completed runs distinctly when the static
  harness can observe them. Closed-tab abandonment remains unsupported without a
  backend.

## Instrument Versioning

- Each catalog entry must include `instrument_id` and `instrument_version`.
- Changing survey fields, hidden telemetry names, redirect behavior, or answer
  scales requires a new instrument version.
- Jotform or other external form edits are external side effects. Inspect and
  document them, but do not submit or mutate them without action-time approval.
- Verification submissions must be labeled as smoke tests and must not be
  counted as research evidence.

## Deployment Checks

- Before publishing, run catalog validation, focused playtest tests, and the
  deterministic site build.
- Confirm generated routes for `/`, per-game indexes, and immutable versioned
  artifacts before treating the package as publish-ready.
- Live Pages verification is separate from local build validation.
- Real-device and real-human readiness require explicit evidence. Do not infer
  readiness from a passing static build.

## Founder Approval Gates

- Founder approval is required before adding or changing creative fixture
  content, changing research questions, changing survey instruments, promoting a
  draft to current, or treating playtest results as product decisions.
- Plan approval, artifact approval, deployment approval, live-session approval,
  and durable product decision recording are separate approvals.
- Silence, merged branches, review activity, or successful automation do not
  count as founder approval.

## Steward CLI

Use `python scripts/playtest_tool.py` for deterministic local operations:

- `list` and `validate` are read-only.
- `new` creates a metadata-only draft scaffold after validating explicit
  metadata and an unused ID.
- `archive` requires an exact ID and preserves artifact history.
- `build` delegates to `scripts/build_playtest_site.py`.

The CLI must remain standard-library Python and must reject overwrites,
archived-entry mutation, secret-like metadata, and creative content.
