# Arcwright Playtest Lab Design

> Current version: v1.1
> Last updated: 2026-08-31
> Status: Founder-approved design; Nightcap authority reference reconciled after GDD migration
> Canonical path: docs/superpowers/specs/2026-08-29-arcwright-playtest-lab-design.md

## Decision

GitHub Pages will become a minimal Arcwright homepage with Playtests as the
prominent entry point. The site will highlight the current test, preserve older
tests at permanent versioned routes, and leave room for a broader Arcwright
public site later.

The surrounding tooling will become a durable Playtest Lab. It will support
multiple independently versioned tests without turning the disposable harness
into production Nightcap architecture.

Founder approval: Option C selected and confirmed on 2026-08-29.

## Context and authority

This design extends the existing Nightcap external-testing harness described in
`docs/specs/nightcap-external-playtest-harness.md` on the current `main`
branch. The canonical product and architecture boundaries are:

- `docs/README.md`: canonical documentation and versioning rules.
- `docs/conventions/human-collaboration.md`: approval and phase-gate rules.
- `docs/architecture/11-telemetry.md` sections 11.1 and 11.3: telemetry must
  be active before real-user sessions and must preserve structured signals.
- `docs/gdd/nightcap/README.md` and its decision ledger: current Nightcap
  game-design authority. The external harness remains non-canon fixture tooling
  and does not change Nightcap product scope.

The former `docs/story-bibles/nightcap-couch-race.md` authority referenced by
v1.0 of this document was archived by ADR-0023. Its retained path is now a
compatibility redirect and must not be used as current Nightcap canon.

The current public harness is merged and deployed at the repository root. The
current Jotform is enabled, but its fourteen legacy telemetry fields use
generated Unique Names that do not match the harness mapping. This design treats
that as a blocking research-instrument defect.

## Goals

- Preserve the current static, dependency-free harness model.
- Make every test and test version discoverable from one manifest.
- Publish one current test and any number of historical tests concurrently.
- Keep versioned test artifacts immutable after publication.
- Repair and verify the existing Jotform telemetry contract.
- Give Codex, Claude, and other agents the same repository-local operating rules
  and deterministic helper commands.
- Keep all test fixture content explicitly separate from Nightcap canon.
- Avoid accounts, backend services, databases, production analytics, or
  provider-specific model dependencies.

## Non-goals

- Production Nightcap runtime, multiplayer networking, or Case Board behavior.
- A custom analytics dashboard or event-ingestion backend.
- Persistent tester identity, invasive tracking, or advertising identifiers.
- An LLM-powered runtime game component.
- Automatic creative authorship or unreviewed changes to fixture content.
- Replacing the existing Jotform with a new instrument when the research
  questions have not materially changed.

## System shape

### Source manifest

`playtests/catalog.json` is the source of truth for published tests. Each entry
contains:

- stable `id` and `game` identifiers;
- immutable `version`;
- human-facing `title`, `summary`, and `status`;
- public `route`;
- source artifact directory;
- research instrument identifier and instrument version;
- `published` date and optional retirement metadata.

The validator rejects duplicate IDs, duplicate routes, missing source
directories, malformed versions, and more than one `current` entry per game.

### Static site build

`playtests/site/` contains the minimal Arcwright landing page and catalog
templates. A dependency-free `scripts/build_playtest_site.py` validates the
manifest, copies each immutable artifact to its declared route, writes the
catalog data consumed by the pages, and emits `_site/`.

The Pages workflow runs this builder and uploads `_site/`. The public layout is:

```text
/
/nightcap/
/nightcap/paper-test-02/v2.2/
```

The current harness remains under its existing source directory and is copied
to the versioned route. A root card links directly to the current test so the
homepage adds one click without hiding the recommended experience.

### Telemetry contract

The existing Jotform remains the v2.2 instrument. `config.js` maps the fourteen
legacy fields to their verified Unique Names (`q13_textbox11` through
`q26_textbox24`) and keeps the four newer readable names unchanged. Runtime
tests assert that every serialized telemetry key produces the expected query
parameter.

The live verification gate is a controlled private run: inspect the generated
feedback URL, confirm all hidden fields prepopulate while remaining invisible,
submit once, confirm the submission contains the telemetry, and verify the
post-submit reveal redirect. Any submission created for verification is labeled
as a smoke test and is not treated as research evidence.

### Steward and deterministic tooling

`playtests/AGENTS.md` defines naming, versioning, privacy, canon, survey, and
deployment rules. Canonical skills under `docs/skills/` and thin launchers under
`.agents/skills/` provide focused capabilities for:

- steward routing and phase gates;
- harness validation and fixture boundaries;
- research-instrument checks and result export guidance;
- catalog/build/publish preparation.

The `playtest` helper exposes deterministic local operations for `list`,
`validate`, `new`, `archive`, and `build`. It never embeds an LLM, provider, or
secret. External Jotform changes remain explicit owner actions through an
available connector or documented handoff.

## Data flow

```text
test artifact + catalog.json
        |
        v
build_playtest_site.py --validate --build
        |
        v
GitHub Pages: homepage -> catalog -> immutable test route
        |
        v
completed test -> serialized telemetry -> hidden Jotform fields
        |
        v
one row per submitted run -> CSV export / later analysis
```

## Error handling and safety

- A build fails closed on invalid manifest entries or unsafe route traversal.
- A test cannot be published without a declared version and source artifact.
- Archived versions remain readable and cannot be silently overwritten.
- The harness records only anonymous, session-scoped telemetry and coarse
  environment classes.
- Closed-tab abandonment remains explicitly unsupported without a backend.
- Jotform field edits and submissions are external side effects and require
  action-time confirmation when performed through a browser.
- No production Arcwright module imports the playtest tooling.

## Verification gates

Each implementation phase must provide:

1. dependency-free unit tests for the changed helper or runtime contract;
2. static site build and route smoke tests;
3. manifest validation and duplicate-route checks;
4. live Pages verification after deployment;
5. Jotform hidden-field and submission verification before research use;
6. documentation reconciliation against the harness spec and product decision
   record.

The first live research session remains blocked until the Jotform telemetry
contract is verified, consistent with `docs/architecture/11-telemetry.md`.

## Scope sequencing

1. Repair and verify v2.2 telemetry.
2. Add the manifest, builder, homepage, catalog, and versioned route.
3. Add repository rules, deterministic helper tooling, and focused skills.
4. Reconcile canonical documentation and record the durable product decision.

Each sequence produces a separately testable change and requires its own review
checkpoint.
