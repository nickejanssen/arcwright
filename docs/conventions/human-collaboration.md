# Human Collaboration Contract

> Current version: v1.0
> Last updated: 2026-07-17
> Status: Current
> Canonical path: docs/conventions/human-collaboration.md

## Purpose

This contract governs Arcwright work that depends on founder input. Agents must
collaborate before making subjective, strategic, operational, or live-session
decisions. Reversible research may continue while the founder is unavailable,
but an agent must stop before choosing, approving, or implementing a direction
that depends on founder input.

The contract prevents a completed attempt plus final review from replacing
discovery, advice, intermediate artifacts, phase gates, and explicit founder
decisions. It does not add interview overhead to work that canonical records
already constrain completely.

## Interaction Profiles

Every task must declare one or more of these profiles before planning or
implementation.

### Independent execution

Use when canonical direction is complete and completion does not depend on
founder taste, intent, private knowledge, risk tolerance, external action, or
observed feedback. The normal spec, plan, implementation, verification, and
review flow applies.

### Decision interview

Use for product, business, architecture, scope, pricing, risk, infrastructure,
privacy, or other choices that require founder judgment. Research the decision,
explain its constraints and implications, present 2 to 3 options with a
recommendation, ask for one selection, confirm the selection, and record only
what the founder explicitly approved.

### Creative collaboration

Use for UI, art, narrative, content, gameplay design, or tuning. Begin with the
founder's open-ended vision, then synthesize 2 to 3 advised directions. After a
direction is selected, produce explained low-cost artifacts, pause for feedback,
and only then produce the full implementation in reviewable batches.

### Facilitated live operation

Use for rehearsals, playtests, workshops, interviews, migrations requiring
hands-on validation, and other live activities. Act as a facilitator: prepare
evidence, guide each phase, collect structured feedback, and pause at every go
or no-go boundary.

Profiles may be combined. For example, asset execution may require Creative
collaboration while an animation-runtime choice requires a Decision interview.

## Classification Rule

A task cannot be classified as Independent execution when completion depends
on any of the following:

- founder taste, intent, goals, or definition of quality;
- a product, business, architecture, scope, pricing, or risk choice;
- private or external facts that only the founder can supply;
- credentials, accounts, physical devices, scheduling, recruitment, or other
  owner action;
- a rehearsal, playtest, observation, walkthrough, or debrief; or
- subjective evaluation of UI, art, narrative, content, gameplay, or tuning.

If an independent task uncovers one of these dependencies, stop and reclassify
it before making the dependent choice.

## Interview Contract

For every non-independent profile, the agent must:

1. Explain the current phase, artifact, or decision in plain language.
2. State why it matters and how it affects the product.
3. Separate fixed constraints from open choices.
4. Identify exactly what needs founder attention and how to review it.
5. Ask one focused question at a time.
6. Prefer a multiple-choice form or interactive control with the recommended
   option clearly marked and free-form input available.
7. Use a clearly explained numbered-choice fallback only when the active
   client cannot render interactive controls.
8. Begin creative work with open-ended founder vision before presenting
   options or recommendations.
9. Give expert advice and a recommendation when evidence supports one.
10. Summarize each answer into a proposed locked decision and obtain
    confirmation before relying on it.

Do not batch unrelated questions to reduce interaction. A question may be
skipped only when canonical records contain a current, explicit answer and no
new decision is required.

## Approval Semantics

The following approvals are separate, and none implies another:

- plan approval;
- direction approval;
- artifact approval;
- phase go-ahead;
- implementation approval;
- final sign-off; and
- permission to record a durable product or architecture decision.

Approval is valid only when the founder explicitly approves a named decision,
artifact, version, or phase. Silence, PR creation, review activity, merge
readiness, prior general approval, or lack of objections do not count.

If the founder changes a decision, reopen the affected phase. Downstream
approvals that depended on the old decision are invalid until the changes are
propagated and reviewed.

## Required Phase Gates

### Decision interview flow

1. Research and frame the decision.
2. Explain constraints and implications.
3. Present 2 to 3 options with a recommendation.
4. Pause for founder selection.
5. Confirm and record the selected decision.

### Creative collaboration flow

1. Interview the founder about goals, references, taste, audience,
   constraints, and success.
2. Present 2 to 3 directions with advice.
3. Pause and lock the selected direction.
4. Produce explained low-cost artifacts.
5. Pause for artifact feedback.
6. Produce the full implementation in reviewable batches.
7. Pause at agreed checkpoints.
8. Obtain explicit final sign-off.

### Facilitated live operation flow

1. Prepare materials and the environment.
2. Present preflight evidence and unresolved risks.
3. Pause for readiness approval.
4. Guide the founder walkthrough or smoke test.
5. Pause for feedback and a live-session go or no-go.
6. Facilitate the live session without silently advancing phases.
7. Conduct a structured debrief.
8. Recommend remediation and pause before another session or scope change.

A failed or blocked phase cannot be marked complete. Explain what failed, what
evidence is missing, and the safest next action.

## Checkpoint Review Package

Every artifact requiring founder input must include:

- what the artifact is and its level of fidelity;
- why it exists and where it fits in the product;
- the prior decisions and canonical constraints that shaped it;
- what remains open versus what is already locked;
- what to inspect, in priority order;
- how to inspect or test it;
- known limitations that should not influence judgment yet;
- the agent's critique, advice, and recommended direction;
- the exact decision needed from the founder; and
- what work follows approval.

Use a format appropriate to the decision:

- Art and UI: visible mockups, comparisons, or interactive prototypes when
  supported.
- Narrative: representative samples in context, including tone and failure
  examples.
- Gameplay and tuning: concrete scenarios, tuning tables, simulations, or play
  examples.
- Rehearsals: readiness dashboard, checklist, risks, and an explicit go or
  no-go control.
- Product, business, and architecture: option comparison with implications and
  a recommendation.

A completed implementation cannot substitute for an intermediate artifact when
earlier feedback could materially change the result.

## Evidence Contract

Each collaborative task must maintain a compact evidence block containing:

- interaction profiles and classification rationale;
- required founder inputs;
- current phase and next gate;
- artifacts presented and review instructions;
- locked decisions tied to the exact artifact or version approved;
- explicit approval evidence and date; and
- outstanding decisions or owner actions.

A decision summary is sufficient. Full interview transcripts are not required.
Evidence must be available to the Implementer and Reviewer through the
canonical task or spec and its synchronized GitHub issue or PR.

## Failure Handling

- Interactive controls unavailable: use a clearly explained numbered-choice
  fallback.
- Founder unavailable: continue reversible research only, then stop before a
  choice or dependent implementation.
- Decision changed: reopen the affected phase and invalidate dependent
  approvals.
- Phase failed: record the blocker and stop before the next phase.
- External action required: explain the action, risk, expected result, and
  verification, then wait.
- Canonical sources conflict: cite the paths and stop for resolution.

## Reviewer Blocking Rules

The Reviewer must block when:

- a required interview or phase was skipped;
- a completed implementation replaced a required intermediate artifact;
- an artifact was not explained well enough for informed review;
- approval was inferred rather than explicit;
- a decision record claims more than the approved scope;
- a live operation advanced without its go or no-go;
- a changed founder decision was not propagated to dependent work; or
- a task was classified as independent despite a founder-input dependency.

The smallest unblocking action is to reopen the missed phase, provide the
required explanation or artifact, obtain the explicit decision, and update
dependent records.
