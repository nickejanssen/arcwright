# Nightcap External Playtest Harness

Version: `nightcap-paper-test-02-v2.2`

Disposable, static research tooling for independent Nightcap playtests. It is intentionally **not** Arcwright/Nightcap production architecture.

## Current instrument

Paper Test #2 v2.2 is the **Representative Time-to-Fun / Cohesion Test** using the explicitly non-canon fixture **The Last Toast**. It is designed as a roughly 15–20 minute solo test with one authored rival and five major investigation commitments.

Playable rhythm:

`WATCH → HUNT → HUNT → rival pressure → PLAY → REACT → HUNT → story reaction → HUNT → HUNT → LAST CALL → CASE FILE → POST-PLAY RESEARCH → THE TRUTH`

The fixture implements simple crime / layered proof. It does not establish permanent Nightcap rules or validate real multiplayer behavior.

## Architecture

- Plain HTML/CSS/JavaScript; no build step and no dependencies.
- `config.js` contains all non-canon fixture content, proof requirements, rival behavior, minigame content, and Jotform mapping.
- `runtime.js` contains anonymous session and telemetry utilities only.
- `app.js` renders the state flow and stores the current run in `sessionStorage` for refresh-safe re-entry.
- `tests/runtime.test.mjs` covers telemetry/session behavior.
- `tests/fixture.test.mjs` covers suspect representation, proof redundancy, minigame-loss solvability, red-herring routes, and bounded Leverage.
- Jotform receives post-play research responses plus URL-prefilled hidden telemetry.
- GitHub Pages hosts only this folder through the existing workflow.

## Run locally

From this directory:

```bash
python -m http.server 8000
```

Open `http://localhost:8000`.

Run the dependency-free tests:

```bash
node --test tests/runtime.test.mjs tests/fixture.test.mjs
```

## Test-design boundaries

The Last Toast has four suspects, one deterministic authored rival (Rhea Pike), one observation minigame for temporary first access, one bounded Leverage decision, five major investigation choices, and a four-part Case File.

Essential truths have redundant proof routes. Losing the minigame does not remove the ability to establish medication substitution. Rival observations are presented as knowledge rather than automatically owned proof.

The survey occurs after Case File commitment and before the reveal. The Jotform completion flow redirects to `?reveal=1` so baseline fun/detective ratings are not influenced by learning whether the accusation was correct.

## Jotform

Form ID: `262397917027062`

Research questions live in Jotform, not this repository. Hidden telemetry Unique Names must match `feedback.prefillMap` in `config.js`. The 14 generated legacy fields use the observed `q13_textbox11` through `q26_textbox24` parameter names; this is an intentional exception to the otherwise readable internal telemetry keys. The four v2.2 fields retain their `q28` through `q31` names. Respondents should never see or edit telemetry fields.

Prefill mapping verification is read-only: inspect the public form's field metadata and load a generated prefill URL with a `GET`, confirming the expected parameter names without submitting a response. Never use the harness or verification process to submit a Jotform response.

Jotform may retain submission-level technical metadata such as IP address. The prototype itself does not request names, emails, accounts, persistent identity, advertising IDs, or cross-run identity.

## Telemetry

Existing fields remain:

`prototype_version`, `run_id`, `started_at`, `completed_at`, `duration_seconds`, `action_sequence`, `investigation_branches`, `discoveries`, `pulse_result`, `case_commitment`, `final_next_interest`, `device_class`, `browser_class`, `completion_status`.

v2.2 adds lightweight fields:

`time_to_first_investigation_seconds`, `major_investigations`, `event_sequence`, `abandonment_point`.

The ordered event/action strings capture opening completion, five major investigations, rival lead, minigame outcome, Leverage choice, story reaction, Last Call, Case File commitment, completion/abandonment, and survey handoff without interrupting the tester.

## Failure / abandonment limits

- Completed run passes `completion_status=completed`.
- Voluntary early exit passes `completion_status=abandoned` and the current state as `abandonment_point`.
- Browser/tab close cannot be reliably recorded without a backend and remains intentionally deferred.
- Incomplete Jotform submissions cannot be distinguished from survey non-entry without event ingestion.

## Deployment

GitHub Pages is enabled and `.github/workflows/nightcap-playtest-pages.yml` builds the Playtest Lab site after changes reach `main`.

Public URL:

`https://nickejanssen.github.io/arcwright/`

The Pages root now hosts the Arcwright homepage and Playtests catalog, not the fixture itself.

Current fixture URL:

`https://nickejanssen.github.io/arcwright/nightcap/paper-test-02/v2.2/`

Legacy fixture alias:

`https://nickejanssen.github.io/arcwright/nightcap-paper-test-02-v2.2/`

The legacy alias preserves direct fixture access for bookmarks from the earlier root-hosted deployment while new links should use the catalog route above. The alias is the migration target for old direct fixture links.

Smoke-test verification of the public pages and survey handoff remains a separate gate from local build validation.

## Intentionally deferred

Memory Support A/B, advanced Case Board, Heat, full Counterintel, auctions/economy, Group Rescue, player-count balancing, accessibility minigame filtering, numerical Case Strength, full Postmortem, production AI generation, multiplayer networking, custom backend analytics, closed-tab abandonment telemetry, and custom QR infrastructure.
