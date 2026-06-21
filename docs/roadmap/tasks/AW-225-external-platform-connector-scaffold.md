# AW-225: Nightcap Web Experience Runtime Connector Scaffold

**Milestone / Epic:** M4 / M4-A  
**Size:** M  
**Status:** Planned

## Plain-English Summary

Implement the Nightcap web experience runtime connector scaffold after AW-202.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/product/decisions-log-additions-may2026.md Entry 3` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Implement the Cloudflare-hosted Nightcap web experience runtime connector scaffold according to the AW-202 contract. Likely files affected: Cloudflare Pages, Workers, Durable Objects or PartyKit files, SDK usage, api docs.

## Acceptance Criteria

- [ ] Before adding a Cloudflare-specific dependency, Worker, Durable Object, or deployment configuration, compare ADR 0003 against a GCP-only implementation using then-current Cloud Run and Firebase capabilities; Cloudflare remains the default unless superseded by a founder decision.
- [ ] Connector can create or attach to a Nightcap session using the AW-202 runtime contract.
- [ ] Connector subscribes to Arcwright events without requiring engine surface assumptions.
- [ ] Connector keeps Arcwright authoritative for session state, event audience targeting, safety, and telemetry.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-202
- AW-224

## Likely Files Affected

Cloudflare Pages, Workers, Durable Objects or PartyKit files, SDK usage, api docs

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.
- Do not bypass the AW-202 Nightcap web experience runtime contract.
- Do not put arc execution logic in FastAPI route handlers.
- Do not put arc execution logic in TypeScript.
- Do not make the selected web runtime a second canonical session authority.

## Architecture References

- docs/product/decisions-log-additions-may2026.md Entry 3
- `docs/decisions/0003-nightcap-web-experience-runtime.md`
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.
