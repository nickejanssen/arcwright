# Cloud Rehearsal 2 Cost Isolation Design

Status: Proposed
Last updated: 2026-07-12
Scope: Cloud Rehearsal 2 infrastructure and billing controls

## Context

Cloud Rehearsal 2 needs Firebase Authentication, Cloud Run, Cloud SQL, and the existing Cloudflare Nightcap runtime. The rehearsal must target less than $10 per service per month and must not expose the Firebase project to an unsafe project-wide shutdown.

Google Cloud budgets are notification mechanisms, not exact spending caps. Billing data can be delayed and estimated values can change before invoice finalization. Cloud SQL also has an always-on instance cost, so a month-long instance can exceed the target before storage, backups, or network charges.

The Arcwright architecture keeps Firebase Authentication as the human identity provider, Cloud SQL PostgreSQL as canonical persistence, Cloudflare as the Nightcap web runtime, and Durable Objects as ephemeral coordination only.

## Decision

Keep Firebase Authentication in the existing Firebase project `arcwright-53ea3`. Create a separate disposable GCP runtime project for Cloud Rehearsal 2. Place Cloud Run, Cloud SQL, Artifact Registry, and runtime cost controls in that project.

The runtime project will use the same billing account unless the owner requires a separate billing account. The Firebase project remains the identity project. The Cloud Run service account receives only the minimum cross-project Firebase Admin permissions required to verify Firebase identity tokens and create session-scoped credentials.

## Cost controls

1. Create service-scoped budgets for Cloud Run, Cloud SQL, Artifact Registry, Cloud Logging, Secret Manager, and any other billable runtime service.
2. Use alert thresholds at 50%, 75%, 90%, and 100% of the $10 target.
3. Treat $8 as the operational stop target because billing data is delayed.
4. Connect the budget to a programmatic notification channel.
5. Use an idempotent shutdown handler that disables billing for the disposable runtime project or removes its runtime resources after an approved threshold. The shutdown must not target `arcwright-53ea3`.
6. Configure Cloud Run with request-based billing, minimum instances zero, maximum instances one, conservative CPU and memory, and no separate worker service unless a documented architecture requirement appears.
7. Provision Cloud SQL only for the rehearsal window. Export required data before deletion, or explicitly treat the rehearsal database as disposable.
8. Keep Cloudflare on the Free plan when its Durable Objects SQLite limits are sufficient. If the Paid plan is required, its $5 monthly minimum remains below the service target, but CPU, request, storage, and retention limits still apply.
9. Do not send live Phone Authentication SMS during rehearsal. Use Firebase test phone numbers or leave live SMS disabled until a budget guard is verified.
10. Do not provision Firestore for this rehearsal. It is not canonical for Arcwright and adds an unnecessary billable surface.

## Runtime topology

```text
Browser
  -> Cloudflare Pages/Worker and Durable Objects
  -> Firebase Auth in arcwright-53ea3
  -> Cloud Run API in disposable rehearsal project
  -> Cloud SQL PostgreSQL in disposable rehearsal project
```

Cloudflare remains responsible for browser rendering, join flow, and ephemeral room coordination. Arcwright remains responsible for canonical session state, arc execution, knowledge, safety, and persistence.

## Alternatives considered

### All services in `arcwright-53ea3`

This is simpler and avoids cross-project IAM. It is rejected for strict cost protection because a project-level shutdown could disrupt Firebase resources, and service-level budgets cannot provide a precise hard cap.

### Separate runtime project without automated shutdown

This reduces blast radius but still relies on delayed alerts and manual intervention. It is acceptable only if the owner explicitly chooses operational convenience over strict protection.

### Dedicated billing account for the runtime project

This provides the clearest accounting boundary but adds billing administration and may not be available. It is not required for the first rehearsal if project-scoped budgets and shutdown controls are configured correctly.

## Security and secret handling

Raw secrets, API keys, service account JSON, and tokens must not be committed, placed in documentation, sent in chat, or stored in memory. Google Secret Manager stores backend secrets. Cloudflare Worker Secrets stores Worker secrets. Rotation uses a new version, deployment and verification, then revocation of the old value.

The runtime project uses a dedicated service account. No service account key files are created. Firebase Web API keys are treated as public client configuration and restricted by API and application restrictions; backend credentials remain server-side.

## Acceptance criteria

- Firebase Auth remains in `arcwright-53ea3`.
- Runtime resources are isolated in the disposable rehearsal project.
- Each billable runtime service has a visible $10 budget and alert thresholds.
- An approved automated stop path exists for the runtime project.
- Cloud SQL is not left running indefinitely.
- Cloud Run scales to zero and has a maximum instance limit of one.
- Cloudflare Durable Objects remain ephemeral and do not become canonical game state.
- No live Phone Auth SMS is sent during the rehearsal without an explicit budget decision.
- No raw secrets or API keys are stored in the repository or Codex artifacts.

## References

- `docs/architecture/02-technology-stack.md`
- `docs/decisions/0003-nightcap-web-experience-runtime.md`
- `docs/decisions/0011-single-cloudrun-service-at-mvp.md`
- `docs/roadmap/operations/cloud-deploy-runbook.md`
- `docs/roadmap/tasks/AW-269-nightcap-cloud-deploy.md`
- https://docs.cloud.google.com/billing/docs/how-to/budgets
- https://docs.cloud.google.com/billing/docs/how-to/budgets-programmatic-notifications
- https://cloud.google.com/sql/pricing
- https://cloud.google.com/run/pricing
- https://developers.cloudflare.com/workers/platform/pricing/
- https://firebase.google.com/pricing
