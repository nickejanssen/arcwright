# AW-269: Nightcap Cloud Deploy (Cloudflare + GCP backend)

**Milestone / Epic:** M5 / TBD (epic assignment when M5 starts)
**Size:** L
**Status:** Planned

## Plain-English Summary

Deploy the Arcwright engine to Cloud Run + Cloud SQL and the Nightcap web
experience to Cloudflare Pages + Workers + Durable Objects, per ADR-0003
post-validation outcome (D-067).

## Why This Matters

Rehearsal 2 (AW-266) and M6 qualifying sessions need a real cloud target.
Local-tunnel was acceptable for Rehearsal 1 per D-065 but does not scale
beyond founder hosting.

## Player Impact

Sessions run on infrastructure that does not depend on the founder's
laptop being awake.

## Business Value

Unblocks Rehearsal 2 and all M6 qualifying-session work.

## Technical Scope

- Provision Cloud Run service for Arcwright engine FastAPI app.
- Provision Cloud SQL Postgres 15 instance with pgvector extension.
- Provision Firebase Auth project.
- Provision Cloudflare Pages project for the web app.
- Provision Cloudflare Workers + Durable Objects for room coordination.
- Wire DNS + custom domain.
- Configure CI/CD for both deploy targets.
- Document the deploy runbook at
  `docs/roadmap/operations/cloud-deploy-runbook.md`.

## Human Collaboration Contract

**Interaction profile:** Decision interview.

**Founder input:** Deployment targets, acceptable cost and operational risk,
credential ownership, billing controls, and required console actions.

**Required flow:** Research the current deployment constraints and explain each
choice, risk, cost implication, and founder action in plain language. Present
two or three viable deployment approaches with a recommendation. Ask one
focused interactive choice question at a time, confirm each decision, and guide
the founder through owner-only actions without requesting secrets in chat.

**Gate:** Deployment stops before any choice, credential-dependent action,
billing change, or external mutation until the founder explicitly approves the
named choice and completes the required owner action.

**Evidence:** Preserve the options, recommendation, explicit approvals, dates,
redacted completion evidence, and outstanding owner actions. Never record
credentials or secret values.

## Acceptance Criteria

- [ ] Engine reachable at a stable Cloud Run URL.
- [ ] Web app reachable at a stable Cloudflare Pages URL.
- [ ] A test session created via the web app reaches the engine and
  returns events.
- [ ] Cost monitoring alerts configured.
- [ ] Deploy runbook lives at
  `docs/roadmap/operations/cloud-deploy-runbook.md`.

## Tests/Verification

- End-to-end smoke test: create session, join from a real phone, complete
  one mini-game, close session.

## Dependencies

- AW-261 (validation decision recorded)
- AW-259 (Rehearsal 1 complete; blockers triaged so deploy work does not
  fight against unstable code)

## Must Not Do

- Do not hardcode secrets.
- Do not skip auth setup.
- Do not couple this deploy to a single Nightcap mini-game.

## Architecture References

- `docs/decisions/0003-nightcap-web-experience-runtime.md`
- `docs/architecture/02-technology-stack.md`
- `docs/roadmap/epics/M4-A-nightcap-external-platform-integration.md`

## Playtest Relevance

Hosts Rehearsal 2 and all M6 qualifying sessions.
