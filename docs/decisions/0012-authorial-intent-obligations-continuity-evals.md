# Status

**Accepted** (founder approval, July 11, 2026)

---

# Context

The founder compared the pre-research dissertation draft "Story Logic Before Story Language" (working draft v0.7, external document) against the canonical platform docs to find architecture and product-design improvements the platform had missed. The draft formalizes the same core thesis the platform is built on: the engine owns durable story state, and the language model renders from resolved state.

Most of the draft's concepts are already platform commitments (deterministic arc execution, knowledge graph as first-class infrastructure, structured interaction events, mandatory telemetry, configurable AI initiative, provider-agnostic routing). The comparison surfaced three genuine gaps and two ideas that are noted but not built:

1. Arc definitions encode structure, constraints, and content rails, but no structured representation of soft authorial logic: theme, tone, or intended emotional progression. The pacing engine computes a live dramatic tension score with no authored target curve to compare it against (see `docs/architecture/03-arc-execution.md` Section 3.3).
2. Nothing tracks narrative obligations (setups, promises, injected misdirection) as durable state. Concretely: when the pacing engine injects a generative red herring, no platform state records that the misdirection exists and should be acknowledged or resolved before an arc's resolution beat. This is an untracked coherence risk.
3. The eval harness and headless session runner exist, but no eval checks narrative continuity: knowledge leaks (an AI character revealing a fact outside its knowledge state) or character contradictions across a session. The Tier 2 telemetry signal "behavior consistency score" (`docs/architecture/11-telemetry.md` Section 11.6) anticipates this but nothing exercises it today.

Alternatives considered and rejected:

- **Adopt the draft's authoring-time concepts** (proposed-versus-accepted story state approval workflow, AI roles such as mirror/critic/architect, versioned intent editing). Rejected: these are creator-tool concepts. The PRD non-goals state the platform executes human-authored arcs and does not write them, and the no-code arc builder is parked. Importing authoring-workflow scope now would violate the platform's own scope rules.
- **Build a runtime post-generation continuity check now.** Rejected for the same reason L4 post-generation safety filtering was deferred in `docs/architecture/10-content-safety.md`: added latency and cost are not justified until an observed failure pattern exists. Recorded as a watchpoint open question instead.
- **Do nothing.** Rejected: item 2 is a real coherence hole in the current design, and items 1 and 3 deepen existing principles (human arc primacy, telemetry as Tier 2 data moat) at low schema cost.

---

# Decision

We adopt three platform improvements:

1. **Authorial intent as a structured arc object.** The ArcDefinition schema gains an optional `authorial_intent` block carrying theme, tone, and per-beat emotional targets (an authored target tension curve). The runtime injects this block into generation context assembly, and pacing telemetry logs realized-versus-intended tension per beat. The block is optional so existing arc definitions remain valid, and it preserves the authored-versus-generative dial. It is an authoring input the engine executes against, not engine-side creative authorship.
2. **Narrative obligations model with a reveal-readiness signal.** The platform tracks narrative obligations (authored setups, generative misdirection injections, promises requiring payoff) as durable session state. Any pacing-engine misdirection injection creates an obligation record. The engine exposes a generic `all_mandatory_obligations_resolved` boolean in the session context so arcs can use it as a beat exit condition, consistent with the generic condition-evaluation contract in `docs/architecture/03-arc-execution.md` Section 3.2. Whether obligations live as a dimension on `facts` or as a dedicated table is a spec-time decision; any schema change follows the migration-review hard rule in `AGENTS.md`.
3. **Continuity and coherence evals on the existing eval harness.** A continuity eval suite runs over headless-runner sessions with synthetic players, checking at minimum knowledge-leak rate and character-contradiction incidents. This gives the "behavior consistency score" Tier 2 signal its first concrete consumer and contributes to the open narrative-quality-metrics question for simulation harness batches (see `docs/product/open-questions-log.csv`).

We explicitly do not adopt: authoring-time approval workflows, AI creative roles, intent version editing (out of platform scope per PRD non-goals); a runtime post-generation continuity classifier (watchpoint open question, mirroring the L4 deferral pattern); host-facing session state rollback (open question, adjacent to parked authoring scope).

---

# Consequences

## Positive consequences

- Closes the untracked generative-misdirection coherence gap with deterministic state, consistent with the principle that AI never manages canonical session state.
- Deepens human arc primacy: authors gain a structured way to declare intended emotional shape, and the runtime can measure fidelity to it.
- Realized-versus-intended tension curves and obligation-resolution telemetry become additional Tier 2 training signals at low collection cost.
- Continuity evals convert an aspirational Tier 2 signal into a working quality gate usable before playtests.

## Negative consequences

- ArcDefinition schema grows; validation and documentation surface increases.
- Obligations add engine state and one likely migration.
- Eval runs consume model budget; suite sizing must respect the AI cost policy.

## Trade-offs

- Gained runtime fidelity measurement and coherence enforcement without importing authoring-tool scope. Lost some schema simplicity. Deferred (not lost) the runtime continuity classifier until evidence justifies its latency and cost.

---

# References

- Source analysis: comparison of dissertation working draft v0.7 "Story Logic Before Story Language" (external, not in repo) against `docs/architecture/` and `docs/prd/`.
- `docs/architecture/03-arc-execution.md` (pacing engine, generic condition contract), `docs/architecture/04-knowledge-graph.md`, `docs/architecture/10-content-safety.md` (L4 deferral pattern), `docs/architecture/11-telemetry.md` (Tier 2 signals).
- `docs/prd/04-non-goals.md` (authoring scope boundary).
- Product log: D-068 in `docs/product/decisions-log.csv`; open questions for the continuity-classifier watchpoint and host-facing rollback in `docs/product/open-questions-log.csv`.
- Follow-up: Planner to sequence roadmap epics/tasks and Spec Author to produce per-feature specs before implementation.
