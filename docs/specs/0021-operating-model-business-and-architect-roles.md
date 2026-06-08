# Operating Model: Business Steward and System Architect Roles

**Status**: Draft

**Author**: Claude Code | **Date**: 2026-06-08

---

# References

- Related specs: `docs/specs/0019-multi-agent-operating-model.md` (the operating model this extends)
- Operating model: `docs/agents/README.md`, `docs/agents/product-steward.md`, `docs/agents/scribe.md`
- Architecture SME: `docs/skills/arcwright-sme` (advisory architecture authority this spec distinguishes from a decision-making architect)
- Convention files: `docs/conventions/ai-contributions.md`, `docs/conventions/ai-cost-policy.md`
- PRD sections: `docs/prd/01-overview.md`, `docs/prd/03-scope.md`, `docs/prd/04-non-goals.md` (open business questions)

---

# Overview

Spec 0019 established the operating model with Product, planning, authoring, implementation, review, and an advisory Architecture SME. Founder review found two gaps: there was no explicit business or commercial representation, and architecture was advisory only (the SME informs but no role owns and approves design decisions). This spec adds a Business Steward and a decision-making System Architect as thinking-role contracts, and updates the pipeline so Product, Business, and Architecture form a shared intent and approval gate.

---

# In Scope

- Add `docs/agents/business-steward.md`: owns commercial intent and viability (market, revenue, pricing, go-to-market, business risk).
- Add `docs/agents/system-architect.md`: the decision authority for cross-cutting technical design and ADRs, explicitly distinct from the advisory Architecture SME (Architect decides, SME informs).
- Update `docs/agents/README.md`: add both roles to the thinking-roles list and the role-to-surface map, and revise the pipeline so the front is a shared intent and approval gate (Product Steward plus Business Steward plus System Architect) before Planner.

---

# Out of Scope

- Client launchers for these roles. Like Planner, Spec Author, and Scribe, the Business Steward and System Architect are thinking roles used in the Claude.ai Project chat; they get no Claude Code, Codex, or Copilot launcher.
- Any change to the Implementer, Reviewer, or SME skills, or to the client wiring delivered by spec 0019 Phases A through E.
- Any change to `AGENTS.md`, the engine constraints, or the architecture principles.
- Any engine, api, sdk, dashboard, migrations, or nightcap code.
- A roadmap AW-NNN ID. This is meta-tooling and ships as a numbered spec plus one PR, matching the spec 0019 precedent.

---

# Acceptance Criteria

- [ ] `docs/agents/business-steward.md` exists and defines purpose, when to use, inputs, outputs, guardrails, and handoff, scoped to commercial viability and bounded by `AGENTS.md`.
- [ ] `docs/agents/system-architect.md` exists and defines a decision-making architecture role, explicitly stating that it decides while the Architecture SME informs, and that it cannot override a non-negotiable constraint without a documented founder override.
- [ ] `docs/agents/README.md` lists both new roles in the thinking-roles list and the role-to-surface map, and the pipeline shows a shared intent and approval gate (Product, Business, Architect) before Planner.
- [ ] Neither new role has a client launcher (no `.claude/`, `.agents/`, or `.github/agents/` file is added for them).
- [ ] No new role contract restates engine constraints or principles as its own rules; each defers to `AGENTS.md`.
- [ ] No em dashes in any created or modified file.

---

# Test Plan

- Static: confirm the two new files exist and contain the required sections; grep `docs/agents/README.md` for both role names in the list, the pipeline gate, and the map; grep all changed files for em dashes (expect none).
- Consistency: confirm the Architect-decides / SME-informs distinction is stated in both `system-architect.md` and `README.md`.
- No regression: confirm no client launcher files were added for the new roles, and no code paths changed.

---

# Risks and Unknowns

**Risks**:
- Architect and SME overlap could confuse contributors. Mitigated by an explicit decides-versus-informs statement in both the Architect contract and the README.
- A three-role intent gate could slow simple decisions. Mitigated by keeping these as advisory thinking roles a human invokes as needed, not mandatory sign-offs on every change.

**Unknowns**:
- Whether the Business Steward should later own a dedicated business or cost doc under `docs/`. Deferred until there is content to put there.

---

# Open Questions

- None. Direction approved by the founder (add Business plus a decision-making System Architect, ship as a follow-up spec plus PR).
