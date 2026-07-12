# AW-202: Nightcap Web Experience Runtime Decision

**Milestone / Epic:** M2 / M2-A  
**Size:** M  
**Status:** Complete

## Plain-English Summary

Select the Nightcap web experience runtime and document the integration contract.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/product/decisions-log-additions-may2026.md Entry 3` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Select the browser-based Nightcap web experience runtime and document the integration contract. This task is not a decision to use a third-party app builder, and it does not move Arcwright core infrastructure or canonical state ownership out of Arcwright. Likely files affected: docs/specs, docs/decisions, docs/roadmap/tasks/AW-225-through-AW-231.

## Acceptance Criteria

- [ ] A decision record names the selected Nightcap web experience runtime or explicitly blocks M4 if no runtime is acceptable.
- [ ] The integration contract lists API, SDK, auth, event, deployment, privacy, state ownership, and performance assumptions.
- [ ] M4 tasks are updated or unblocked according to the decision.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-201

## Likely Files Affected

docs/specs, docs/decisions, docs/roadmap/tasks/AW-225-through-AW-231

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.

## Architecture References

- docs/product/decisions-log-additions-may2026.md Entry 3
- `docs/specs/0022-aw-202-nightcap-web-experience-runtime-decision.md`
- `docs/decisions/0003-nightcap-web-experience-runtime.md`
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.
