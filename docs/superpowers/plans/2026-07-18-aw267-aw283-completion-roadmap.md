# AW-267 + AW-287 + AW-283 Completion Roadmap

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers-extended-cc:subagent-driven-development (recommended) or superpowers-extended-cc:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close AW-267 (#184, art-direction brief) with real founder sign-off — done, see Phase 1 — then close AW-287 (#250, Leverage advantages/sabotages) and AW-283 (#237, suspect answer generation and contradiction detection) in that order, each with real founder sign-off and a code-reviewed PR.

**Architecture:** All three tasks are tagged **Creative collaboration** in `docs/conventions/human-collaboration.md` and carry a failure pattern already recorded on this repo (AW-267 via PR #243/#246, AW-281 per the founder's own PR review, and this roadmap's own first draft per PR #249/#251 review) — generating finished subjective content, or claiming process compliance, before the founder is actually interviewed and evidence is preserved honestly. AW-287 was added mid-session: AW-283's contradiction-catch visibility depends on which Leverage effect is active, so Leverage moved from proposed design direction to a real, ADR- and spec-backed dependency (D-075, ADR-0015, spec 0075) sequenced before AW-283's implementation.

**Tech Stack:** Python engine (arc execution, knowledge graph, character behavior, event system, resource/effect resolution) for AW-287/AW-283; Markdown/CSV documentation artifacts for AW-267. No SDK/dashboard changes in any of the three tasks.

**User decisions (already made):**
- Complete AW-267 first (done), then AW-287, then AW-283, in that order.
- AW-267's PR #243 content and D-073 are candidate research only — not founder direction, not sign-off evidence on their own (confirmed by PR #246 and the AW-267 task file's own gate language). AW-267's actual approval is a 2026-07-18 consolidated review, documented honestly as such (not as retroactive phase completion) per PR #249 review resolution.
- Leverage is an approved AW-283 dependency (explicit founder direction, superseding an earlier PR #252 framing that predated D-075).
- Call Their Bluff is replaced by Make Them Wait in the Leverage launch set (no public-theory input contract exists; ADR-0015).
- AW-282 is the template to follow: discovery record → checkpoint table → explicit founder approval before merge.

---

## Phase 1 — AW-267 (#184): Nightcap Art Direction Brief — DONE

Completed and PR'd: [PR #249](https://github.com/nickejanssen/arcwright/pull/249). Full record: `docs/product/aw267-discovery-and-checkpoints.md`. Approved scope: the v0.3 art-direction brief, twelve moodboards, and the Host (Vesper) bible, excluding brief §8.5 (launch-surface direction), which remains an unapproved candidate note pending its own review.

---

## Phase 2 — AW-287 (#250): Nightcap Leverage Advantages And Sabotages

Discovery, the representative-interaction walkthrough, the ADR (0015), and the implementation spec (0075) are complete — see `docs/product/aw287-discovery-and-checkpoints.md`. Remaining work:

### Task 15: Write the AW-287 implementation plan

Author a full TDD implementation plan via `superpowers-extended-cc:writing-plans`, grounded in spec 0075's runtime contract, schemas, and acceptance criteria. No placeholders — spec 0075 already resolves every design question, so this plan should be code-concrete.

### Task 16: Execute the AW-287 implementation plan

TDD implementation in an isolated git worktree per `superpowers-extended-cc:using-git-worktrees`. All spec 0075 acceptance criteria must pass, including the audience-filtering, determinism, and generic-naming-enforcement tests.

### Task 17: Code review

`superpowers-extended-cc:requesting-code-review`, then the `reviewer` agent against the Arcwright checklist (game/surface agnosticism, generic engine naming with no Nightcap-specific terms, deterministic effect resolution, no truth mutation, audience filtering).

### Task 18: Present the implemented thin slice and open the AW-287 PR

**USER-ORDERED GATE — NON-SKIPPABLE.**

Per AW-287's Human Collaboration Contract gates, present the implemented thin slice for explicit founder approval **before** recording sign-off or opening the PR — this is the same gate whose absence in Phase 3 below was flagged in PR #249 review, so it is built into this phase from the start rather than retrofitted.

1. Present the working thin slice (e.g. a scripted session-shaped scenario matching the walkthrough) and ask the founder to approve or request changes.
2. Only after explicit approval: record sign-off in `docs/product/decisions-log.csv`, `git status` check for agent-local files, commit, push, open the PR closing #250.
3. Stop for founder review before Phase 3 (AW-283) implementation begins.

---

## Phase 3 — AW-283 (#237): Suspect Answer Generation And Contradiction Detection

Discovery is complete — see `docs/product/aw283-discovery-and-checkpoints.md`. Behavior-brief confirmation and sample review remain, followed by implementation once AW-287 (Phase 2) is merged.

### Task 8: Synthesize and confirm the behavior brief

Draft a short brief from the discovery answers (tone, lie readability, catch mechanic/visibility, latency target, success definition); present for confirmation via `AskUserQuestion`; record in the checkpoint file.

### Task 9: Present answer/lie/contradiction samples

At least 3 truthful-answer samples, 2 authorized-lie samples, 2 confirmed-contradiction cases, 2 fairness edge cases, each explaining what it represents and what needs founder attention. Present via `AskUserQuestion`; record approval in the checkpoint file.

### Task 10: Write the AW-283 implementation plan

Full TDD plan via `writing-plans`, grounded in Tasks 8–9's outputs and AW-287's now-shipped resource/effect capability (AW-283 consumes Leverage effect outcomes when generating answers — e.g. an answer generated under an active Rattle the Witness effect). Blocked on AW-287's PR (Task 18) merging.

### Task 11: Execute the AW-283 implementation plan

TDD implementation in an isolated worktree. All AW-283 acceptance criteria pass: no knowledge-state leaks (AW-272 eval batch, clean seed), seeded lie deterministically catchable, false-positive guard, claim provenance queryable, p95 latency recorded.

### Task 12: Code review

`requesting-code-review`, then the `reviewer` agent against the Arcwright checklist.

### Task 12.5: Present the implemented thin slice for explicit founder approval

**USER-ORDERED GATE — NON-SKIPPABLE.** This is the step PR #249 review found missing: AW-283's Human Collaboration Contract requires a pause for explicit direction after the implemented thin slice, distinct from and in addition to approval of the earlier discovery/brief/sample artifacts. An executor must not record durable sign-off or open the PR from pre-implementation artifacts alone.

1. Present the working thin slice (a real session-shaped run: a truthful answer, an authorized lie, a confirmed catch, a false-flag rejection) with instructions on what to inspect.
2. Pause for the founder's explicit approval or revision request via `AskUserQuestion`.
3. Do not proceed to Task 13 without that explicit approval captured with a date in the checkpoint file.

### Task 13: Record sign-off and open the AW-283 PR

**USER-ORDERED GATE — NON-SKIPPABLE.**

Only after Task 12.5's explicit approval: record founder sign-off in `docs/product/decisions-log.csv` (mirroring D-074/D-075), `git status` check for agent-local files, commit, push, open the PR closing #237, and stop for founder review.
