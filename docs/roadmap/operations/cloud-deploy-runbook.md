> Current version: v1.0
> Last updated: 2026-06-28
> Status: Current
> Canonical path: docs/roadmap/operations/cloud-deploy-runbook.md

# Cloud Deploy Runbook

## 1. Prerequisites

- Install `gcloud`.
- Install `wrangler`.
- Install Node 20.
- Install Python 3.11.

## 2. GCP Setup

1. Enable the Cloud Run, Artifact Registry, Cloud SQL Admin, Secret Manager, IAM, IAM Credentials, and Security Token Service APIs in the target GCP project.
2. Create an Artifact Registry Docker repository named `arcwright`.
3. Create a Cloud SQL for PostgreSQL 15 instance sized `db-f1-micro`.
4. Enable the `vector` extension in the application database after provisioning.
5. Create the `arcwright` database and an application user with a least-privilege password.
6. Build the `DATABASE_URL` from the same Postgres names used in `docker-compose.yml`: `POSTGRES_DB`, `POSTGRES_USER`, and `POSTGRES_PASSWORD`.
7. Create Secret Manager secrets named `DATABASE_URL`, `ARCWRIGHT_API_KEY`, `PRIMARY_LLM_API_KEY`, `SECONDARY_LLM_API_KEY`, and `FIREBASE_SERVICE_ACCOUNT_JSON`. The names `PRIMARY_LLM_API_KEY` and `SECONDARY_LLM_API_KEY` are provider-neutral; store the actual Anthropic API key under `PRIMARY_LLM_API_KEY` and the Groq API key under `SECONDARY_LLM_API_KEY`. Do not use provider names in Secret Manager secret names.
8. Create a Workload Identity pool and provider for this GitHub repository, then allow the GitHub deployer service account to impersonate through that provider.
9. Before the first production deploy, record the unresolved API-service to worker-service communication decision from `docs/architecture/05-session-persistence.md`. This PR only deploys `arcwright-api`; do not treat AW-269 as production-complete until that prerequisite is documented.

## 3. GitHub Actions Secrets

- Add `GCP_PROJECT_ID`.
- Add `GCP_REGION`.
- Add `AR_REPO`.
- Add `CLOUDFLARE_API_TOKEN`.
- Add `CLOUDFLARE_ACCOUNT_ID`.

## 4. Cloudflare Setup

1. Create or connect the Cloudflare Pages project for this repository.
2. From `nightcap-web/`, set the production API base URL with `wrangler secret put ARCWRIGHT_API_BASE_URL --env production` using the Cloud Run service URL after the first backend deploy.
3. From `nightcap-web/`, set the Arcwright server API key with `wrangler secret put ARCWRIGHT_API_KEY --env production`.
4. From `nightcap-web/`, set the Firebase web key with `wrangler secret put FIREBASE_WEB_API_KEY --env production`.

## 5. Firebase Auth

1. Use the Firebase project named `arcwright-prod`.
2. Enable custom token sign-in.
3. Enable anonymous sign-in.
4. Create a Firebase service account JSON credential and store it in Secret Manager as `FIREBASE_SERVICE_ACCOUNT_JSON`.
5. Confirm the Cloud Run deploy command in `.github/workflows/deploy-api.yml` includes both `ARCWRIGHT_API_KEY=ARCWRIGHT_API_KEY:latest` and `FIREBASE_SERVICE_ACCOUNT_JSON=FIREBASE_SERVICE_ACCOUNT_JSON:latest` in `--set-secrets`.

## 6. Smoke Test

1. Deploy the API and web targets from `main` only after the worker-service prerequisite above is resolved and documented.
2. Create a session through `POST /v1/sessions`.
3. Join the session from a real phone using the Pages URL.
4. Verify SSE event delivery on the phone client.
5. Complete one TMST round end to end.
6. Set a GCP budget alert at `$100/month`.

## 7. Post-Deploy Verification Checklist

Run these three steps manually after every deploy to confirm the core acceptance criteria are met before declaring the deploy successful.

**Step 1 — Engine health endpoint**

```bash
curl -f https://<CLOUD_RUN_SERVICE_URL>/health
```

Expected: HTTP 200. A non-200 or connection error means the Cloud Run service did not start correctly. Check Cloud Run logs in GCP Console.

**Step 2 — Web app reachability**

Open the Cloudflare Pages production URL (visible in the Cloudflare dashboard or in the `wrangler deploy` output) in a browser. Confirm the Nightcap landing page renders without a 5xx error or broken asset load.

**Step 3 — Scripted session ping**

```bash
curl -sf -X POST https://<CLOUD_RUN_SERVICE_URL>/v1/sessions \
  -H "Content-Type: application/json" \
  -d '{"arc_id": "nightcap-v1"}' \
  | jq '.session_id'
```

Expected: a non-empty session ID string is printed. A 4xx or 5xx response means the API is reachable but session creation is broken — check database connectivity and Secret Manager secret bindings in the Cloud Run service configuration.
