# Decisions Log Additions, May 2026

**Merge target:** `docs/product/decisions-log.csv` (append-only; add these entries at the end)
**Produced in:** Build planning session, May 2026

---

## Entry 1

**Decision:** M0 Wizard-of-Oz validation gate overridden
**Date:** May 2026
**Rationale:** PRD v1.3 Section 9 defined a manual Wizard-of-Oz facilitation phase (minimum 10 sessions, personalization perception signal required in 2+) as a required gate before significant production engineering. This gate is explicitly overridden. The founder's build sequence is: Engine, Platform, Game, live test with real users, iterate. No game exists yet and no one has played a session. Validation of the personalization thesis will happen through real-user qualifying sessions at M6, not a pre-engineering simulation phase. The personalization thesis is treated as a working hypothesis to be confirmed or disproved by the real product in real users' hands. This is consistent with the PRD's explicit founder-override provision.
**Risk accepted:** Production engineering begins before the personalization layer has been validated with real users. If M6 live testing reveals the personalization thesis does not hold, more engineering will need to be revisited than if a WoZ phase had surfaced this earlier. Founder accepts this tradeoff explicitly.
**Status:** Active. Logged May 2026.
**Section:** Process / MVP
**Tags:** M0, validation, wizard-of-oz, MVP, override, personalization

---

## Entry 2

**Decision:** GitHub Projects and Issues is the primary project tracker for the Arcwright build
**Date:** May 2026
**Rationale:** Code, AI agents (Claude Code, Codex, Copilot), and task tracking live in one place. Agents can read issues, execute against them, open PRs, and close issues via commit message references natively. No integration bridge required between code and tracker. GitHub sub-issues (GA) and milestones support the roadmap's milestone, epic, and task hierarchy. Zero admin overhead for a solo founder. Linear and Jira were considered and rejected: Linear adds context-switching cost without proportionate benefit at this team size; Jira is designed for multi-team process governance that does not yet exist.
**Revisit trigger:** First non-technical co-founder or PM hire who needs richer reporting or lives in a different tool.
**Status:** Active.
**Section:** Process / Tooling
**Tags:** tooling, project-management, github, planning

---

## Entry 3

**Decision:** Nightcap game UI will be built on an external platform connecting to Arcwright via API; not built directly by Arcwright
**Date:** May 2026
**Rationale:** Founder confirmed the Nightcap experience layer (host interface, player interface) will be delivered via a third-party platform that connects to the Arcwright platform through its API, rather than Arcwright building those surfaces directly. This is consistent with the PRD surface-agnosticism principle: the engine emits content events tagged with context; the experience layer renders them. The specific external platform is not yet named.
**Implication for roadmap:** M4 (Nightcap experience layer) task decomposition is deferred until the external platform is selected. The platform choice drives what SDK or integration tasks are required. M1 through M3 are unaffected; they are backend and API only.
**Status:** Active. Platform TBD; revisit when M3 nears its exit gate.
**Section:** Product / Architecture
**Tags:** M4, Nightcap, experience-layer, surface-agnosticism, platform

---

*End of additions. Do not edit earlier entries. Append only.*
