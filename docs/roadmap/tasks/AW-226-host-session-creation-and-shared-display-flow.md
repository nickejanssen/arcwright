# AW-226: Host Session Creation And Shared Display Flow

**Milestone / Epic:** M4 / M4-B  
**Size:** M  
**Status:** Complete

## Plain-English Summary

Build host controls and shared display flow on the Nightcap web experience runtime.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/prd/02-requirements.md Host experience` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Build host controls and shared display flow on the Cloudflare-hosted Nightcap web experience runtime selected by AW-202. Likely files affected: Cloudflare Pages, Workers, Durable Objects or PartyKit files, SDK usage if needed.

## Acceptance Criteria

- [ ] Host can create, start, pause, resume, and end a session through the Nightcap web experience runtime.
- [ ] Host session creation captures the v1 personalization intake seed fields once the exact three questions are resolved.
- [ ] Shared display shows only public or shared-display ContentEvents.
- [ ] Host controls use API lifecycle endpoints rather than bypassing the platform API.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-225

## Likely Files Affected

Cloudflare Pages, Workers, Durable Objects or PartyKit files, SDK usage if needed

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.
- Do not bypass the AW-202 Nightcap web experience runtime contract.
- Do not put arc execution logic in TypeScript.

## Architecture References

- docs/prd/02-requirements.md Host experience
- `docs/decisions/0003-nightcap-web-experience-runtime.md`
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.
