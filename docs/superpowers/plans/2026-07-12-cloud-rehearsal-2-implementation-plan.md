# Cloud Rehearsal 2 Implementation Plan

> Execution contract: use `superpowers:executing-plans` in a fresh Codex task. Do not provision cloud resources or edit application code until the preflight checkpoint passes.

## Goal

Deploy the approved Cloud Rehearsal 2 topology with Firebase Authentication in `arcwright-53ea3`, runtime infrastructure in a separate disposable GCP project, Cloudflare as the Nightcap web runtime, and cost controls targeting less than $10 per billable service per month.

## Non-negotiable constraints

- Firebase Auth stays in `arcwright-53ea3`.
- Cloud Run, Cloud SQL, Artifact Registry, and billing shutdown controls use the disposable runtime project.
- Python remains authoritative for session state, persistence, arc execution, knowledge, safety, and API behavior.
- Cloudflare remains responsible for browser rendering, join flow, and ephemeral Durable Object coordination.
- Durable Objects must not become canonical game state.
- Firestore is not provisioned for this rehearsal.
- Real Phone Auth SMS is not sent during rehearsal.
- No service account key files, raw API keys, tokens, or secret values enter Git, chat, memory, or documentation.
- No provider or model names are added outside the existing routing configuration boundaries.

## Phase 0: isolate and preflight

1. Start in an isolated `codex/cloud-rehearsal-2` worktree or branch. Leave the main checkout unchanged.
2. Read `AGENTS.md`, `docs/README.md`, the Cloud Rehearsal 2 design, `docs/architecture/02-technology-stack.md`, `docs/decisions/0003-nightcap-web-experience-runtime.md`, `docs/decisions/0011-single-cloudrun-service-at-mvp.md`, `docs/roadmap/operations/cloud-deploy-runbook.md`, and `docs/roadmap/tasks/AW-269-nightcap-cloud-deploy.md`.
3. Verify Node 20 or newer and `npx -y firebase-tools@latest --version`.
4. Verify the current Git status and confirm that `.agents/` and `skills-lock.json` remain untracked.
5. Record only non-secret identifiers: Firebase project ID, runtime project ID, GCP region, Cloudflare account ID, Worker name, Pages project, and public rehearsal hostname.

Checkpoint: stop if the billing account, Firebase project access, Cloudflare account access, or target hostname is unavailable.

## Phase 1: create and constrain the runtime project

1. Create a globally unique disposable GCP project under the selected billing account.
2. Enable only the APIs required for Cloud Run, Cloud SQL Admin, Artifact Registry, Secret Manager, Cloud Billing budgets, Pub/Sub, IAM, and logging/monitoring.
3. Create a dedicated Cloud Run service account with least-privilege roles:
   - Cloud SQL client on the runtime project.
   - Secret Manager accessor on named secrets only.
   - Runtime logging permissions as required by Cloud Run.
   - The minimum documented Firebase Admin permission on `arcwright-53ea3` for token verification and custom-token issuance.
4. Do not create service account JSON keys.
5. Create Secret Manager entries for `DATABASE_URL`, `ARCWRIGHT_API_KEY`, the configured primary and secondary model credentials, and any other backend-only secret required by the existing runbook. Enter values through the console or approved secret command without printing them.
6. Create the smallest supported Cloud SQL PostgreSQL instance in the same region as Cloud Run. Use the rehearsal database as disposable unless an export requirement is explicitly selected. Keep deletion protection disabled only in the disposable project.
7. Configure Cloud Run for request-based billing, minimum instances zero, maximum instances one, conservative CPU and memory, and no separate worker service.
8. Create an Artifact Registry repository with a retention policy that prevents unbounded image accumulation.

Checkpoint: verify service accounts, secret names, region alignment, Cloud Run limits, and Cloud SQL lifecycle settings without reading secret values.

## Phase 2: configure billing protection

1. Create service-scoped budgets for Cloud Run, Cloud SQL, Artifact Registry, Cloud Logging, Secret Manager, Pub/Sub, and any other billable runtime service.
2. Set notifications at 50%, 75%, 90%, and 100% of the $10 target. Treat $8 as the operational stop threshold because billing data is delayed.
3. Connect the budget to a Pub/Sub topic.
4. Implement an idempotent billing guard in a clearly isolated operations package. It must:
   - Accept only Cloud Billing budget notification envelopes.
   - Verify the expected runtime project ID and configured budget IDs.
   - Ignore duplicate, stale, malformed, or unrelated messages.
   - Record an audit log without including secret values.
   - Disable billing for the disposable runtime project or remove only the runtime resources at the approved threshold.
   - Never target `arcwright-53ea3`.
5. Give the billing guard only the minimum permission required to stop the runtime project. Do not grant Owner or broad Editor access.
6. Test the guard with a synthetic notification before connecting it to the live budget.

Checkpoint: prove that a test notification stops only the disposable runtime project and that a malformed message cannot trigger shutdown.

## Phase 3: Firebase Authentication configuration

1. In `arcwright-53ea3`, register the web app as `nightcap-web` if it is not already registered.
2. Enable Email/Password and Google sign-in.
3. Configure Phone Authentication only for controlled testing. Add Firebase test phone numbers and do not send live SMS.
4. Configure the authorized domains for localhost, the rehearsal hostname, and the final Cloudflare hostname.
5. Create two API keys with distinct purposes:
   - Browser key: Websites application restriction for the authorized domains and API restrictions limited to the Firebase APIs required by the web SDK.
   - Cloudflare token-exchange key: no referrer restriction because Cloudflare Workers do not provide a stable browser referrer, but restrict it to the narrow Identity Toolkit API surface and store it only as a Worker Secret.
6. Never use the Cloudflare token-exchange key in browser HTML or committed configuration.

Checkpoint: verify Email/Password, Google, and test-phone sign-in in the Firebase console and verify API key restrictions without exposing key values.

## Phase 4: implement the host identity bridge

### Python API

1. Extend `api/auth/__init__.py` with a narrowly scoped account-token verifier that validates Firebase ID tokens and returns the Firebase `uid` and account metadata without weakening existing participant-token checks.
2. Extend `api/routers/sessions.py` with a host session creation path authenticated by the Firebase account token. Preserve the existing developer API-key path for developer tooling.
3. Persist the stable Firebase account identity in the existing host-account/session model rather than generating a new anonymous host identity for authenticated hosts.
4. Preserve session-scoped custom claims and session matching for host, player, and display tokens.
5. Update `api/schemas.py` only if the existing request/response contract requires a typed Firebase host-session request.
6. Add focused tests in `api/tests/test_sessions_api.py` and auth tests for valid Firebase account tokens, expired tokens, wrong-project tokens, missing tokens, and session claim mismatch.

### Cloudflare Worker and web client

1. Add the Firebase Web SDK to `nightcap-web/package.json` only if the existing web runtime cannot use the approved SDK path without it.
2. Update `nightcap-web/src/worker.ts` to require an authenticated host token for host session creation, proxy the Firebase account token to the Arcwright API, and keep the Arcwright API key server-side.
3. Keep the existing player QR/join flow anonymous and session-scoped.
4. Replace the current manual host-token flow in `nightcap-web/src/ui.ts` with Email/Password and Google sign-in controls. Keep test-phone sign-in behind a rehearsal-only control if needed.
5. Keep custom-token exchange server-side using the restricted Worker Secret key.
6. Update `nightcap-web/tests/worker.test.ts` and UI tests for authentication success, authentication failure, missing credentials, token exchange failure, and no browser exposure of backend secrets.

Checkpoint: local API and Worker tests pass before any cloud deployment.

## Phase 5: deploy and configure Cloudflare

1. Build and deploy the API image to Cloud Run.
2. Attach Cloud SQL and Secret Manager references without printing secret values.
3. Run database migrations using the approved migration process.
4. Configure Cloudflare Worker variables and secrets:
   - Public API base URL as a variable.
   - Firebase web configuration as public client configuration where required.
   - Arcwright API key, token-exchange key, bootstrap values, and other credentials as Worker Secrets only.
5. Deploy the Worker and Pages assets with the rehearsal hostname.
6. Configure Durable Object bindings and verify SQLite-backed ephemeral storage and hibernation-safe WebSocket behavior.
7. Confirm the Worker cannot reach the API without the required server-side secret and that players cannot access host-only events.

## Phase 6: verification gates

Run and record evidence for:

1. Python unit and API tests.
2. TypeScript typecheck, tests, and build.
3. Ruff, formatting, and mypy checks required by the repository.
4. Firebase Email/Password sign-in.
5. Firebase Google sign-in.
6. Firebase test-phone sign-in without live SMS.
7. Authenticated host session creation.
8. Anonymous player QR join.
9. Cloud Run to Cloud SQL persistence and migration.
10. Host lifecycle controls: start, pause, resume, and end.
11. Durable Object reconnect and hibernation behavior.
12. Privacy filtering for host-only, player-only, display, and public events.
13. Synthetic budget notification and billing-guard shutdown test.
14. Secret rotation: create new versions, redeploy, verify, and revoke old versions.
15. End-to-end rehearsal with the planned participant count and mini-game.
16. Teardown: export required data, delete or stop Cloud SQL, remove rehearsal images, confirm Cloud Run scales to zero, and verify post-teardown billing state.

The rehearsal is not declared ready until every gate passes or an explicit exception is documented and approved.

## Handoff

After implementation, report:

- Cloud resources created and their non-secret identifiers.
- Each budget and threshold.
- Shutdown test evidence.
- Authentication test evidence.
- Deployment URLs.
- Test commands and results.
- Remaining risks and the exact teardown command or browser path.
- Acceptance criteria satisfied.

