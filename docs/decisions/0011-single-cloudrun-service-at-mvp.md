# Status

**Accepted**

---

# Context

The technical architecture (§2.2) specifies two Cloud Run services at MVP: `arcwright-api` (the FastAPI application server) and `arcwright-worker` (a background task processor). However, the inter-service communication mechanism between these two services — Cloud Tasks queuing versus direct async HTTP calls — is an open question recorded in `docs/product/open-questions-log.csv`. Architecture §5 (session persistence) explicitly states this decision must be made before production deployment of the worker service.

Deploying `arcwright-worker` as part of the initial cloud automation before the communication contract is resolved would force an arbitrary implementation choice that may need to be redesigned once the open question closes. Deferring the worker service avoids locking in that choice prematurely and keeps the initial deploy surface small and verifiable.

Alternatives considered:
- Deploy both services immediately with Cloud Tasks: premature; forces the comms decision without adequate design review.
- Deploy both services immediately with direct async HTTP: same problem, different implementation.
- Defer worker indefinitely: not the intent; the worker is part of MVP architecture and will be added once the comms decision closes.

---

# Decision

We deploy only `arcwright-api` in the initial cloud deploy automation (`AW-269`). `arcwright-worker` is intentionally deferred until the inter-service communication mechanism (Cloud Tasks vs direct async HTTP) is resolved via the open-questions process.

The `.github/workflows/deploy-api.yml` workflow provisions and deploys `arcwright-api` only. No worker service, queue, or inter-service IAM binding is configured in that workflow.

---

# Consequences

## Positive consequences
- Initial deploy surface is minimal and fully verifiable without a worker service dependency.
- No premature commitment to a Cloud Tasks or async HTTP communication contract.
- Easier to iterate on the worker architecture once the comms decision is made.

## Negative consequences
- Any background processing that would be handled by `arcwright-worker` is unavailable until the worker is added.
- The deployed system does not fully match the two-service architecture described in §2.2 until the follow-up task lands.

## Trade-offs
- We gain a simpler, faster initial deployment and avoid a design mistake.
- We temporarily diverge from the target two-service architecture. This is acceptable at MVP stage; the architecture is the target state, not the day-one state.

---

# References

- Architecture §2.2 — two Cloud Run services at MVP
- Architecture §5 — session persistence and inter-service communication (open question)
- `docs/product/open-questions-log.csv` — inter-service comms open question
- `docs/decisions/0006-nightcap-continuity-v11.md` — related scope boundary decision
- AW-269 — Nightcap cloud deploy automation task
