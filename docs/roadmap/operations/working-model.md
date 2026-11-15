---
id: productroadmap.roadmap.operations.working-model
namespace: product-roadmap
title: Working Model
owner: Nico Janssen
status: active
review_by: "2027-01-13"
sensitivity: internal
source: authored
tags: []
supersedes: []
---

# Working Model

## Tracker

Use GitHub Projects plus GitHub Issues.

- Milestones M1-M7 map to GitHub Milestones.
- Epics are parent issues.
- Tasks (`AW-xxx`) are sub-issues under their epic.

The task spec body in the roadmap should be copied into the issue body.

Every task record and synchronized issue mirror must declare a collaboration profile.
For non-independent work, it must also carry required founder inputs,
the current phase and next gate, intermediate artifacts and review instructions,
explicit approval evidence, and outstanding owner actions. Canonical roadmap
records are updated before their GitHub issue mirrors.

## Capture Rule (D-119)

Work is never left only in chat or in a temporary file. Anything a session finds that needs doing becomes, in the same session:

1. a task file in `docs/roadmap/tasks/` and an entry in `docs/roadmap/index.json`, then
2. a GitHub issue created from `.github/ISSUE_TEMPLATE/task.md`, with the task file's body as the issue body.

Every task answers who, what, when, where, why and how:

| Question | Field |
| --- | --- |
| Who | Owner (a build session, a named role, or the founder) |
| What | Plain-English Summary and Technical Scope |
| When | Target date and GitHub milestone |
| Where | Files and components in Technical Scope; Product |
| Why | Why This Matters, with the evidence or decision behind it |
| How we know it is done | Acceptance Criteria and Tests/Verification |

Labels on every task issue: `task`, one size, one milestone, one product (`product:nightcap`, `product:arcwright`, `product:shared`), and where they apply `blocked`, `needs-decision`, `founder-action`, `agent-ready`, `superseded`, `deferred`, `ops`.

Decisions go to `docs/product/decisions-log.csv`. Questions not yet answered go to `docs/product/open-questions-log.csv`. Session findings go to the GDD validation pages. `HANDOVER.md` gets one dated log line per merged pull request.

## Three Lanes (D-118)

Spec-driven development stays the method. The size of the unit approved depends on the lane.

| Lane | Examples | What is needed before work starts |
| --- | --- | --- |
| Small fix or documentation | A broken hook, a stale page, a break-fix under the tooling freeze | A task issue with acceptance criteria and a short plan. The founder's merge is the approval |
| Feature work | The Nightcap rebuild | An approved spec. The rebuild uses three combined specs (engine spine, screens, endgame) instead of one per work package (AW-302) |
| Hard-rule work | Database or migration changes, changes across engine modules, prompts or evals, new dependencies, secrets or auth | Explicit founder approval of the plan, always, whatever the lane |

For every player-facing task, say three things separately: merged, deployed, and seen in play. They are not the same.

## Limits And Cadence

- **Work in progress:** at most two build sessions and one writing session at a time, and never two sessions on the same file.
- **Weekly, about twenty minutes:** blockers, the next one to three tasks, and the decisions coming to the founder (issues labelled `needs-decision`).
- **Visual changes** are captured at TV and phone sizes and inspected by the session before the founder is asked to look.
- **Art exploration is separate from integration.** Record rights for every asset from the first day.

## Per Work Session

0. Read `HANDOVER.md`, run `git fetch origin`, and check open pull requests.
1. Identify the current milestone and epic.
2. Use the AW-201 decomposition for M2-M6. Revise task details when new decisions land, especially the AW-202 Nightcap web experience runtime contract that shapes M4 implementation.
3. Hand agents one task at a time.
4. If a coding decision affects strategy or architecture, record it in the Decisions Log flow described in `AGENTS.md`.

## Cadence

- Weekly: choose the next 1-3 tasks.
- Per milestone: verify exit criteria before starting the next milestone.
- Monthly: if you are still in the same milestone you expected to have finished, treat that as a signal to inspect scope, architecture friction, or execution assumptions.

## Open Dependencies and Risks

- Nightcap trademark clearance remains a high-priority non-engineering item.
- Enterprise buyer interviews should start once demo footage exists.
- The biggest schedule risk is treating M6 proof and personalization diagnosis as a formality rather than a real product gate.

