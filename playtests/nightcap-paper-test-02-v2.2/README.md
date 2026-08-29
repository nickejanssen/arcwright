# Nightcap External Playtest Harness

Version: `nightcap-paper-test-02-v2.2`

Disposable, static research tooling for independent Nightcap playtests. It is intentionally **not** Arcwright/Nightcap production architecture.

## Architecture

- Plain HTML/CSS/JavaScript; no build step and no dependencies.
- `config.js` contains all test copy/fixture choices and the feedback integration mapping.
- `runtime.js` contains only anonymous session/telemetry utilities.
- `app.js` renders the test flow and stores the current run in `sessionStorage` so an accidental refresh can resume.
- Jotform receives post-play research responses and URL-prefilled telemetry.
- GitHub Pages hosts only this folder through the included workflow.

## Run locally

From this directory:

```bash
python -m http.server 8000
```

Open `http://localhost:8000`.

Run the dependency-free tests:

```bash
node --test tests/runtime.test.mjs
```

## Change prototype content

Edit only `config.js` for story copy, investigation choices, discoveries, fixture pulse content, commitments, and survey URL/prefill mapping. Do not turn fixture convenience into GDD canon.

The included **Room With No Door** content is explicitly a NON-CANON TEST FIXTURE recovered from Paper Test #2 material. The reaction and party-pulse interactions are likewise fixture-only placeholders to exercise v2.2-shaped harness slots; they are not approved Nightcap mechanics.

## Change research questions

Research questions live in Jotform, not this codebase. Form ID: `262397917027062`. Keep gameplay free of research prompts. When questions change, edit the Jotform form; no site deployment is needed unless telemetry fields or the form URL change.

## Jotform telemetry prefill — one-time check

Jotform prepopulates fields using each field's **Unique Name**. In the form builder, open each hidden telemetry field → Advanced → Field Details → Unique Name. Make sure the values match `feedback.prefillMap` in `config.js`. This is the only field-specific integration configuration.

Jotform may retain submission-level technical metadata such as IP address. The prototype itself does not collect names, emails, cross-run identifiers, cookies, advertising IDs, or third-party analytics.

## Results / export

Use Jotform's submission table as the central result store. Export to CSV for analysis. The intended shape is one row per submitted run, with readable telemetry strings such as `Examine bookcase > Press Jonas`.

## Increment the test version

1. Change `version` in `config.js`, e.g. `nightcap-paper-test-02-v2.3`.
2. Change only the fixture/research content required for that version.
3. Commit/deploy. The version is attached to every survey handoff automatically.

## Telemetry fields

`prototype_version`, `run_id`, `started_at`, `completed_at`, `duration_seconds`, `action_sequence`, `investigation_branches`, `discoveries`, `pulse_result`, `case_commitment`, `final_next_interest`, `device_class`, `browser_class`, `completion_status`.

No fingerprinting. Device/browser are coarse classes only.

## Failure / abandonment limits

- Completed run: telemetry is passed to the survey with `completion_status=completed`.
- Voluntary early exit: the explicit **End test early & give feedback** path passes `completion_status=abandoned`.
- Browser/tab close cannot be reliably recorded without a backend and is intentionally deferred.
- An incomplete Jotform submission cannot be distinguished from a tester who never opened/submitted the survey without adding event ingestion; also deferred.

## Deployment

The repo currently has GitHub Pages disabled. The workflow `.github/workflows/nightcap-playtest-pages.yml` deploys this folder once Pages is enabled for GitHub Actions.

One owner action:

**GitHub → `nickejanssen/arcwright` → Settings → Pages → Build and deployment → Source → GitHub Actions.**

Then run/re-run the workflow or push any change under this playtest folder. Expected URL:

`https://nickejanssen.github.io/arcwright/`

## QR code

Do not make QR generation a deployment dependency. After the public URL is live, Chrome/Edge can generate one directly with **Share → Create QR code**. Use the exact public test URL so the QR automatically follows the deployed version.

## Intentionally deferred

Accounts/auth, backend/API, database, custom analytics, CMS/admin UI, production Case Board, multiplayer networking, persistent identity, production minigame systems, cross-run tracking, closed-tab abandonment telemetry, and any custom QR service.
