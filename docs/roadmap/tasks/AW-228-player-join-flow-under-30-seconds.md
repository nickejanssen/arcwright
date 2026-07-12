# AW-228: Player Join Flow Under 30 Seconds

**Milestone / Epic:** M4 / M4-C  
**Size:** M  
**Status:** Complete

## Plain-English Summary

Build QR or code join flow for player devices.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/prd/02-requirements.md Player experience` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Build QR or code join flow for player devices in the Cloudflare-hosted Nightcap web experience runtime selected by AW-202. Likely files affected: Cloudflare Pages, Workers, Durable Objects or PartyKit files, api join flow if needed.

## Acceptance Criteria

- [ ] A new player can join by QR or code in under 30 seconds in rehearsal conditions.
- [ ] Player join does not require a Firebase account or app install.
- [ ] Player join captures one to two v1 personalization prompts once the exact prompt set is resolved.
- [ ] Player receives only their assigned character context after join.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-225

## Likely Files Affected

Cloudflare Pages, Workers, Durable Objects or PartyKit files, api join flow if needed

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.
- Do not bypass the AW-202 Nightcap web experience runtime contract.
- Do not put arc execution logic in FastAPI route handlers.

## Architecture References

- docs/prd/02-requirements.md Player experience
- `docs/decisions/0003-nightcap-web-experience-runtime.md`
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.
