# Human Collaboration Contract Design

> Current version: v0.1
> Last updated: 2026-07-17
> Status: Approved design
> Canonical path: docs/superpowers/specs/2026-07-17-human-collaboration-contract-design.md

## Purpose

Establish a repo-wide contract for work that requires founder input. Agents
must collaborate before making subjective, strategic, operational, or live
session decisions. They may continue reversible research while the founder is
unavailable, but they must stop before choosing, approving, or implementing a
direction that depends on founder input.

This contract prevents a completed attempt plus final review from replacing
discovery, advice, intermediate artifacts, phase gates, and explicit founder
decisions.

## References

- `AGENTS.md`
- `docs/specs/0019-multi-agent-operating-model.md`
- `docs/specs/0021-operating-model-business-and-architect-roles.md`
- `docs/conventions/ai-contributions.md`
- `docs/conventions/review-checklist.md`
- `docs/agents/README.md`
- `docs/skills/github-task-implementer/SKILL.md`
- `docs/skills/arcwright-reviewer/SKILL.md`
- `docs/skills/arcwright-minigame/SKILL.md`
- `docs/roadmap/operations/working-model.md`
- `docs/specs/0000-template.md`
- `docs/prd/03-scope.md`
- `docs/architecture/15-development-guide.md`
- `docs/story-bibles/nightcap-couch-race.md`
- `docs/specs/0067-development-survey-and-path-to-first-playtest.md`
- `docs/specs/0068-game-experience-quality-bar.md`
- `docs/specs/0069-nightcap-visual-design-system.md`
- `docs/specs/0072-nightcap-couch-race-v1.md`
- `docs/specs/0073-m5-canonical-reconciliation.md`

## Problem

The current operating model requires a spec, a plan, plan approval, tests,
review, and human merge. It does not require agents to determine whether the
work itself depends on founder taste, intent, knowledge, risk tolerance,
external action, or observed feedback.

That gap allowed AW-267 and PR #243 to:

- author founder-owned art direction without a founder discovery interview;
- create full text moodboards before direction was selected;
- record D-073 as committed founder approval before explicit sign-off; and
- reduce founder participation to reviewing a completed attempt.

The same pattern would be harmful in rehearsals, playtests, product decisions,
pricing, cloud setup, narrative content, gameplay tuning, and user-interface
work.

## Design Principles

1. Founder input is a production dependency, not a final review courtesy.
2. Ask before choosing when the answer depends on human intent or judgment.
3. Prefer one focused question at a time.
4. Prefer interactive controls or multiple-choice forms when supported.
5. Explain every artifact so the founder knows what it is, how to review it,
   and what needs attention.
6. Use low-cost intermediate artifacts before expensive or complete work.
7. Keep approvals narrow, explicit, and tied to a named artifact or decision.
8. Reversible research may continue while input is unavailable. Directional
   choices and dependent implementation may not.
9. Live operations advance only through explicit phase gates.
10. Independent technical work should remain efficient and should not acquire
    unnecessary interview overhead.

## Interaction Profiles

Every task must declare one or more interaction profiles.

### Independent execution

Canonical direction is complete and completion does not depend on founder
taste, intent, private knowledge, risk tolerance, external action, or observed
feedback. The normal spec, plan, implementation, verification, and review flow
applies.

### Decision interview

Use for product, business, architecture, scope, pricing, risk, infrastructure,
privacy, or other choices that require founder judgment.

The agent must research the decision, explain the constraints and implications,
present options with a recommendation, ask for one selection, confirm the
selected decision, and record only what was explicitly approved.

### Creative collaboration

Use for UI, art, narrative, content, gameplay design, or tuning.

The agent must begin with the founder's open-ended vision, then synthesize 2 to
3 advised directions. After a direction is selected, the agent produces
explained low-cost artifacts, pauses for feedback, and only then produces the
full implementation in reviewable batches.

### Facilitated live operation

Use for rehearsals, playtests, workshops, interviews, migrations requiring
hands-on validation, and other live activities.

The agent acts as a facilitator. It prepares evidence, guides each phase,
collects structured feedback, and pauses at every go or no-go boundary.

### Classification rule

A task cannot be classified as independent when completion depends on any of
the following:

- founder taste, intent, goals, or definition of quality;
- a product, business, architecture, scope, pricing, or risk choice;
- private or external facts that only the founder can supply;
- credentials, accounts, physical devices, scheduling, recruitment, or other
  owner action;
- a rehearsal, playtest, observation, walkthrough, or debrief;
- subjective evaluation of UI, art, narrative, content, gameplay, or tuning.

Profiles may be combined. For example, AW-268 requires creative collaboration
for asset and motion direction plus a decision interview for the animation
runtime.

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

The agent must not batch unrelated questions merely to reduce interaction.
Questions may be skipped when canonical records already contain a current,
explicit answer and no new decision is required.

## Approval Semantics

The following are separate approvals and none implies another:

- plan approval;
- direction approval;
- artifact approval;
- phase go-ahead;
- implementation approval;
- final sign-off;
- permission to record a durable product or architecture decision.

Approval is valid only when the founder explicitly approves a named decision,
artifact, version, or phase. Silence, PR creation, review activity, merge
readiness, prior general approval, or lack of objections do not count.

If the founder changes a decision, the affected phase reopens. Downstream
approvals that depended on the old decision become invalid until the changes
are propagated and reviewed.

## Required Phase Gates

### Decision interview flow

1. Research and frame the decision.
2. Explain constraints and implications.
3. Present options with a recommendation.
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

1. Prepare materials and environment.
2. Present preflight evidence and unresolved risks.
3. Pause for readiness approval.
4. Guide the founder walkthrough or smoke test.
5. Pause for feedback and a live-session go or no-go.
6. Facilitate the live session without silently advancing phases.
7. Conduct a structured debrief.
8. Recommend remediation and pause before another session or scope change.

A failed or blocked phase cannot be marked complete. The agent must explain
what failed, what evidence is missing, and the safest next action.

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
- Gameplay and tuning: concrete scenarios, tuning tables, simulations, or
  play examples.
- Rehearsals: readiness dashboard, checklist, risks, and explicit go or no-go
  control.
- Product, business, and architecture: option comparison with implications
  and recommendation.

A completed implementation cannot substitute for an intermediate artifact
when earlier feedback could materially change the result.

## Evidence Contract

Each collaborative task must maintain a compact evidence block containing:

- interaction profiles and classification rationale;
- required founder inputs;
- current phase and next gate;
- artifacts presented and review instructions;
- locked decisions, tied to the exact artifact or version approved;
- explicit approval evidence and date; and
- outstanding decisions or owner actions.

A decision summary is sufficient. Full interview transcripts are not required.
The evidence must be available to the Implementer and Reviewer through the
canonical task or spec and its synchronized GitHub issue or PR.

## Enforcement Surfaces

The implementation must update these canonical surfaces:

- create `docs/conventions/human-collaboration.md` as the procedure of record;
- add always-on classification, interview, phase, and approval rules to
  `AGENTS.md`;
- synchronize `.github/copilot-instructions.md` with `AGENTS.md`;
- update `docs/conventions/ai-contributions.md` so async delegation is limited
  to independent execution or reversible preparation;
- update `docs/agents/README.md` and the Product Steward, Business Steward,
  System Architect, Planner, Spec Author, and Scribe contracts;
- update `docs/skills/github-task-implementer/SKILL.md` to declare profiles,
  conduct required interviews, and stop at phase gates;
- update `docs/skills/arcwright-reviewer/SKILL.md` and
  `docs/conventions/review-checklist.md` with blocking collaboration checks;
- add a required Human Collaboration Contract section to
  `docs/specs/0000-template.md`;
- update `docs/roadmap/operations/working-model.md` so task records and issue
  mirrors carry the collaboration contract;
- update `docs/agents/USAGE.md` with cross-client behavior and fallbacks; and
- update affected canonical specs, roadmap tasks, and live GitHub issues only
  after the global contract is approved and merged.

GitHub issues remain execution mirrors. Canonical repo documents must be
updated before synchronized issue bodies.

## Current Work Retrofit

Every open task receives an explicit profile. Independent technical tasks do
not gain unnecessary interview overhead.

### Creative collaboration

- AW-267 Nightcap Art Direction Brief
- AW-268 Nightcap Asset Pipeline and Motion System
- AW-277 through AW-285 narrative, arc, gameplay, tuning, and rendering work

### Facilitated live operation

- AW-232 Adversarial Safety Playtest Protocol
- AW-242 Founder-Run Final Rehearsal
- AW-243 Five Outside Qualifying Sessions
- AW-266 Rehearsal 2
- AW-273 Rehearsal 1 Execution
- AW-286 Couch Race Rehearsal Slice and Rehearsal 1 Retarget

### Decision interview

- AW-234 gross-margin assumptions
- AW-244 H1 proof analysis and next-step decision
- AW-268 animation-runtime choice
- AW-269 cloud and environment choices
- issue #220 schema, API, telemetry, and compatibility choices

### Operational collaboration

- AW-240 Closed Playtest Operations Runbook
- AW-241 Qualifying Session Instrumentation Checklist

### Owner-action gates

AW-269 and any task requiring credentials, cloud-console actions, scheduling,
recruitment, physical devices, or people must explain the action and wait for
completion evidence.

## PR #243 Correction

The existing art-direction brief and text moodboards are useful reversible
research, but they are not approved founder direction.

The implementation plan must:

1. Move PR #243 back to draft or otherwise mark it blocked on collaboration.
2. Remove or downgrade the premature D-073 approval claim.
3. Treat the current brief and moodboards as candidate research artifacts.
4. Conduct the AW-267 art-direction interview from the founder's open-ended
   vision.
5. Present explained visual directions and moodboards for feedback.
6. Lock the selected direction before revising the full brief.
7. Obtain explicit final sign-off before recording D-073 or starting AW-268.

No existing direction may be presented as the founder's choice until the
founder confirms it.

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

## Architecture Implications

This design changes the development operating model only. It does not change
engine authority, schemas, APIs, telemetry payloads, prompts, routing, safety,
dependencies, migrations, or product scope.

The relevant implications are:

- Human arc primacy is strengthened because agents cannot silently author
  founder-owned creative direction.
- Product-scope approval is strengthened because explicit direction and
  durable recording are separate gates.
- The solo-founder critical path remains protected because independent tasks
  avoid unnecessary interviews and reversible preparation may continue while
  input is unavailable.

## Verification

Implementation verification must include:

1. Confirm `AGENTS.md` and `.github/copilot-instructions.md` remain synchronized.
2. Confirm every enforcement surface references the same interaction profiles,
   approval semantics, and stop conditions.
3. Confirm affected task records, specs, and GitHub issues carry matching
   collaboration requirements.
4. Confirm PR #243 and D-073 no longer claim unearned approval.
5. Run scenario checks:
   - AW-267 pauses after reversible research and begins a founder interview.
   - AW-286 stops after preflight until readiness approval.
   - AW-244 presents evidence, options, and a recommendation before recording a
     next-step decision.
   - an independent technical bug follows the normal plan and implementation
     flow without added interview phases.
   - a client without interactive controls uses the numbered-choice fallback.
6. Run repository documentation, formatting, and link checks required by the
   implementation plan.

## Acceptance Criteria

- [ ] One canonical human-collaboration procedure defines profiles, interviews,
  phase gates, review packages, approval semantics, evidence, and failures.
- [ ] Always-on agent rules require classification before planning or
  implementation.
- [ ] Implementer and Reviewer skills enforce the collaboration contract.
- [ ] The Scribe cannot record founder approval without explicit evidence tied
  to a named decision or artifact.
- [ ] Spec and roadmap guidance require explicit collaboration metadata.
- [ ] Cross-client usage guidance prefers interactive multiple-choice controls
  and documents the numbered fallback.
- [ ] Current open work is classified without adding unnecessary interview
  overhead to independent tasks.
- [ ] Affected canonical docs and live GitHub issues agree.
- [ ] PR #243 and D-073 do not claim founder approval before the completed
  AW-267 interview and explicit sign-off.
- [ ] Rehearsal and playtest tasks have explicit phase-by-phase go or no-go
  gates.
- [ ] Creative work requires explained intermediate artifacts before full
  production.
- [ ] Decision records are tied to explicit approval of a named decision or
  artifact.
- [ ] No engine, API, SDK, schema, migration, prompt, eval, routing, safety, or
  dependency change is introduced.

## Out of Scope

- Implementing the collaboration contract in this design-document change.
- Editing live GitHub issues or PR #243 before the implementation plan is
  approved.
- Rewriting completed historical task records.
- Reopening decisions whose explicit approval evidence is already valid.
- Changing Arcwright runtime or product behavior.

## Open Questions

None. The founder approved every design section on 2026-07-17.
