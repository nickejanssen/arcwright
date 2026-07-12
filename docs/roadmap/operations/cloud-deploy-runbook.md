> Current version: v1.1
> Last updated: 2026-06-29
> Status: Current
> Canonical path: docs/roadmap/operations/cloud-deploy-runbook.md

# Cloud Deploy Runbook

## 1. Prerequisites

- Install Google Cloud CLI (`gcloud`).
- Install Cloudflare Wrangler CLI (`wrangler`).
- Install Node 20.
- Install Python 3.11.
- Install Docker Desktop and confirm `docker build` works locally.
- Confirm you can sign in to both Google Cloud and Cloudflare from this machine.

Quick verification:

```bash
gcloud --version
wrangler --version
node --version
python --version
docker --version
```

If any command fails, fix that before continuing.

## 2. GCP Setup

### 2.1 Create or select the GCP project

1. In Google Cloud Console, create a production project or choose the existing one you want to use.
2. Copy the project ID. You will need it later for the GitHub secret `GCP_PROJECT_ID`.
3. Set the CLI defaults:

```bash
gcloud auth login
gcloud config set project YOUR_GCP_PROJECT_ID
```

### 2.2 Enable the required Google Cloud APIs

Enable these APIs in `APIs & Services > Enabled APIs & services`:

- Cloud Run Admin API
- Artifact Registry API
- Cloud Build API
- Cloud SQL Admin API
- Secret Manager API
- IAM API
- IAM Service Account Credentials API
- Security Token Service API
- Firebase Management API

CLI option:

```bash
gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com sqladmin.googleapis.com secretmanager.googleapis.com iam.googleapis.com iamcredentials.googleapis.com sts.googleapis.com firebase.googleapis.com
```

### 2.3 Create the Artifact Registry Docker repository

Create one Docker repository named `arcwright` in your chosen region.

Console path:

1. Open `Artifact Registry`.
2. Click `Create repository`.
3. Name: `arcwright`
4. Format: `Docker`
5. Mode: `Standard`
6. Region: pick the same region you will use for Cloud Run.

CLI option:

```bash
gcloud artifacts repositories create arcwright --repository-format=docker --location=YOUR_GCP_REGION
```

Save the region value for the GitHub secret `GCP_REGION` and the repo name `arcwright` for the GitHub secret `AR_REPO`.

### 2.4 Create the Cloud SQL PostgreSQL instance

Create one PostgreSQL 15 instance sized `db-f1-micro`.

Console path:

1. Open `Cloud SQL`.
2. Click `Create instance`.
3. Choose `PostgreSQL`.
4. Version: `PostgreSQL 15`
5. Instance ID: choose a production-safe name
6. Preset: `Development`
7. Machine type: `db-f1-micro`
8. Set a strong `postgres` password and store it securely.
9. Choose the same region as Cloud Run if possible.
10. Create the instance.

After the instance is ready:

1. Open the instance.
2. Create a database named `arcwright`.
3. Create an application user. Use the same names expected by local compose:
   - database name maps to `POSTGRES_DB`
   - user name maps to `POSTGRES_USER`
   - password maps to `POSTGRES_PASSWORD`
4. Open the `Databases` tab and run:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

If the console SQL editor is not available, connect with `psql` and run the same command against the `arcwright` database.

### 2.5 Build the production `DATABASE_URL`

Use the Cloud SQL connection values plus the app database credentials you just created.

Format:

```text
postgresql://POSTGRES_USER:POSTGRES_PASSWORD@HOST:5432/POSTGRES_DB
```

Use the real Cloud SQL private or public host that matches your network setup. Do not commit this value anywhere.

### 2.6 Create the required Secret Manager secrets

Create these Secret Manager secrets:

- `DATABASE_URL`
- `ARCWRIGHT_API_KEY`
- `PRIMARY_LLM_API_KEY`
- `SECONDARY_LLM_API_KEY`
- `FIREBASE_SERVICE_ACCOUNT_JSON`

Notes:

- `PRIMARY_LLM_API_KEY` should contain the Anthropic key.
- `SECONDARY_LLM_API_KEY` should contain the Groq key.
- `ARCWRIGHT_API_KEY` is the server-side API key used by the Nightcap worker when it calls the Arcwright API.
- `FIREBASE_SERVICE_ACCOUNT_JSON` must contain the full raw JSON service account document, not a file path.

CLI pattern:

```bash
printf 'YOUR_SECRET_VALUE' | gcloud secrets create SECRET_NAME --data-file=-
```

If the secret already exists, add a new version instead:

```bash
printf 'YOUR_SECRET_VALUE' | gcloud secrets versions add SECRET_NAME --data-file=-
```

### 2.7 Create the GitHub deployer service account

Create one service account for GitHub Actions, for example `github-deployer`.

Console path:

1. Open `IAM & Admin > Service Accounts`.
2. Click `Create service account`.
3. Give it a clear name such as `github-deployer`.

Grant it these roles:

- `Cloud Run Admin`
- `Artifact Registry Writer`
- `Secret Manager Secret Accessor`
- `Service Account User`

If your Cloud Run deployment path needs more permissions in your org, grant the smallest additional role required and document why.

### 2.8 Configure Workload Identity Federation for GitHub Actions

This repository deploys with GitHub OIDC, not a JSON key file.

Console path:

1. Open `IAM & Admin > Workload Identity Federation`.
2. Create a workload identity pool.
3. Inside that pool, create an OIDC provider for GitHub.
4. Use issuer `https://token.actions.githubusercontent.com`.
5. Restrict the provider to this repository.
6. Bind the GitHub deployer service account so this provider can impersonate it.

You need two values from this setup:

- the full workload identity provider resource name for GitHub Actions variable `GCP_WORKLOAD_IDENTITY_PROVIDER`
- the service account email for GitHub Actions variable `GCP_SERVICE_ACCOUNT`

The workflow already reads those from GitHub Actions repository variables.

### 2.9 Create the Cloud Run service

You can let the first GitHub Actions deploy create the service, or create it once manually from the console to verify permissions.

Target service name:

- `arcwright-api`

Deployment behavior expected by the workflow:

- public URL enabled with `--allow-unauthenticated`
- secrets mounted through `--set-secrets`

### 2.10 Pre-deploy architecture note

Before the first live production rollout, record the unresolved API-service to worker-service communication decision from [docs/architecture/05-session-persistence.md](/C:/Users/nicke/OneDrive/Desktop/arcwright/docs/architecture/05-session-persistence.md). AW-269 deploys `arcwright-api` plus the Nightcap worker, but it does not resolve that longer-term architecture decision by itself.

## 3. GitHub Actions Secrets

Open `GitHub repo > Settings > Secrets and variables > Actions`.

Add these repository secrets:

- `GCP_PROJECT_ID`
- `GCP_REGION`
- `AR_REPO`
- `CLOUDFLARE_API_TOKEN`
- `CLOUDFLARE_ACCOUNT_ID`

Add these repository variables:

- `GCP_WORKLOAD_IDENTITY_PROVIDER`
- `GCP_SERVICE_ACCOUNT`

Recommended values:

- `AR_REPO`: `arcwright`
- `GCP_REGION`: the same region used for Artifact Registry and Cloud Run
- `GCP_WORKLOAD_IDENTITY_PROVIDER`: the full provider resource path from Workload Identity Federation
- `GCP_SERVICE_ACCOUNT`: the GitHub deployer service account email

After saving them, open `.github/workflows/deploy-api.yml` and `.github/workflows/deploy-web.yml` in GitHub UI once to sanity-check the names match exactly.

## 4. Cloudflare Setup

This repo deploys `nightcap-web` with Wrangler as a Cloudflare Worker that serves static assets and uses a Durable Object. Treat Cloudflare Workers as the required product. A custom domain is optional but recommended.

### 4.1 Sign in to Cloudflare from Wrangler

```bash
wrangler login
```

If your Cloudflare org uses API-token-only access, keep the token ready for GitHub Actions and local deploys.

### 4.2 Create the Worker and Durable Object environment

The repo already defines:

- Worker name: `nightcap-web`
- production Worker name: `nightcap-web-prod`
- Durable Object binding: `ROOMS`
- Durable Object class: `NightcapRoom`

You do not need to create the Durable Object manually in the dashboard. Wrangler will provision it on first deploy because it is declared in [nightcap-web/wrangler.toml](/C:/Users/nicke/OneDrive/Desktop/arcwright/nightcap-web/wrangler.toml).

### 4.3 Create the Cloudflare API token for GitHub Actions

In Cloudflare dashboard:

1. Open `My Profile > API Tokens`.
2. Create a token that can deploy Workers for the target account.
3. Copy the token into GitHub secret `CLOUDFLARE_API_TOKEN`.
4. Copy the account ID into GitHub secret `CLOUDFLARE_ACCOUNT_ID`.

### 4.4 Set the production Worker secrets

Run these from the repo root or from `nightcap-web/`.

After the API is live, set the Arcwright API base URL:

```bash
cd nightcap-web
wrangler secret put ARCWRIGHT_API_BASE_URL --env production
```

Paste the full Cloud Run HTTPS base URL when prompted.

Set the worker-to-API server key:

```bash
wrangler secret put ARCWRIGHT_API_KEY --env production
```

Paste the same value you stored in Secret Manager as `ARCWRIGHT_API_KEY`.

Set the Firebase web API key:

```bash
wrangler secret put FIREBASE_WEB_API_KEY --env production
```

Paste the Firebase Web App API key from Firebase project settings.

### 4.5 Optional custom domain

If you want a branded production URL instead of the default `workers.dev` hostname:

1. Add or select the domain in Cloudflare.
2. Open `Workers & Pages`.
3. Attach a custom domain to `nightcap-web-prod`.
4. Wait for DNS and certificate provisioning.

Use that custom domain for the phone smoke test if it is ready.

## 5. Firebase Auth

### 5.1 Create or select the Firebase project

Use the Firebase project named `arcwright-prod` unless the founder has approved a different production project name.

Console path:

1. Open [Firebase Console](https://console.firebase.google.com/).
2. Create the project or select the existing production project.
3. If prompted, attach it to the same Google Cloud project used above.

### 5.2 Enable authentication providers

Open `Build > Authentication > Sign-in method`.

Enable:

- Anonymous

The client also uses Firebase custom tokens issued by the backend. Keep the Identity Toolkit API enabled in the linked GCP project.

### 5.3 Create the web app credential

1. Open `Project settings`.
2. Add a Web App if one does not exist.
3. Copy the Web API key.
4. Store it in Cloudflare with:

```bash
cd nightcap-web
wrangler secret put FIREBASE_WEB_API_KEY --env production
```

### 5.4 Create the backend service account JSON

1. Open `Project settings > Service accounts`.
2. Generate a new private key for a service account that can mint Firebase custom tokens.
3. Download the JSON once.
4. Immediately store the full JSON content in Secret Manager as `FIREBASE_SERVICE_ACCOUNT_JSON`.
5. Do not commit the JSON file. Delete the local file after you store it securely.

### 5.5 Confirm the workflow secret bindings

The current API workflow must bind all of these secrets into Cloud Run:

- `DATABASE_URL=DATABASE_URL:latest`
- `ARCWRIGHT_API_KEY=ARCWRIGHT_API_KEY:latest`
- `PRIMARY_LLM_API_KEY=PRIMARY_LLM_API_KEY:latest`
- `SECONDARY_LLM_API_KEY=SECONDARY_LLM_API_KEY:latest`
- `FIREBASE_SERVICE_ACCOUNT_JSON=FIREBASE_SERVICE_ACCOUNT_JSON:latest`

Verify that list in [deploy-api.yml](/C:/Users/nicke/OneDrive/Desktop/arcwright/.github/workflows/deploy-api.yml) before your first production push.

## 6. Smoke Test

### 6.1 Trigger the production deploys

1. Merge the deployment branch into `main`.
2. Wait for both GitHub Actions workflows to finish:
   - `Deploy API`
   - `Deploy Web`
3. If either fails, stop and fix that before live testing.

### 6.2 Confirm the API is healthy

```bash
curl -f https://YOUR_CLOUD_RUN_URL/health
```

Expected result: HTTP 200.

### 6.3 Create a real Nightcap session

Use the production API URL and API key. Export the key into your shell first so it never appears in the command line or shell history file directly.

Example:

```bash
export ARCWRIGHT_API_KEY="(paste from Secret Manager)"
curl -X POST https://YOUR_CLOUD_RUN_URL/v1/sessions \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: $ARCWRIGHT_API_KEY" \
  -d '{"arc_id":"nightcap-v1","quality_tier":"standard"}'
```

Save these values from the response:

- `session_id`
- `join_url`
- `host_join_token`

### 6.4 Open the web surfaces

1. On your laptop, open the production Worker URL.
2. On your laptop, also open the host page if needed:
   - `https://YOUR_WEB_URL/host`
3. On a second browser tab or device, open the shared display if needed:
   - `https://YOUR_WEB_URL/shared-display`
4. On a real phone, open the `join_url` returned by the API or build the join URL manually with the session ID and token.

### 6.5 Verify end-to-end realtime behavior

Confirm all of these happen:

1. The phone can join without a fatal auth error.
2. The worker can call the API successfully.
3. SSE updates arrive when session state changes.
4. The host, shared display, and phone stay in sync.
5. One TMST round can be started, played, and completed.

If the phone joins but no live updates appear, inspect:

- Cloudflare Worker logs
- Cloud Run logs
- Firebase auth errors
- any failed request from the worker to the API

### 6.6 Set budget protection

In Google Cloud Console:

1. Open `Billing`.
2. Open `Budgets & alerts`.
3. Create a monthly budget of `$100`.
4. Add at least one email alert threshold.

## 7. Post-Deploy Verification Checklist

Run these three steps manually after every deploy to confirm the core acceptance criteria are met before declaring the deploy successful.

**Step 1 - Engine health endpoint**

```bash
curl -f https://<CLOUD_RUN_SERVICE_URL>/health
```

Expected: HTTP 200. A non-200 or connection error means the Cloud Run service did not start correctly. Check Cloud Run logs in GCP Console.

**Step 2 - Web app reachability**

Open the Cloudflare production Worker URL or custom domain in a browser. Confirm the Nightcap landing page renders without a 5xx error or broken asset load.

**Step 3 - Scripted session ping**

```bash
curl -sf -X POST https://<CLOUD_RUN_SERVICE_URL>/v1/sessions \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: <ARCWRIGHT_API_KEY>" \
  -d '{"arc_id":"nightcap-v1","quality_tier":"standard"}' \
  | jq '.session_id'
```

Expected: a non-empty session ID string is printed. A 4xx or 5xx response means the API is reachable but session creation is broken. Check database connectivity, Secret Manager bindings, Firebase setup, and the Cloud Run service configuration.
