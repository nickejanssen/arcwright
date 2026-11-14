---
id: nightcap.specs.0092-nightcap-gdd-rebuild
namespace: nightcap
title: Nightcap GDD Rebuild and Reconciliation Contract
owner: Nico Janssen
status: active
review_by: "2027-05-13"
sensitivity: internal
source: authored
x-scope-evidence: D-108
tags: []
supersedes: []
---

# Nightcap GDD Rebuild and Reconciliation Contract

**Status**: Draft. Not approved. No implementation may start from this file.

**Author**: Claude Code | **Date**: 2026-11-13

**Canonical path**: `docs/specs/0092-nightcap-gdd-rebuild.md`

---

# Plain-language goal

Today the playable TV and phone game is the older Couch Race design. The Nightcap Master GDD replaced that design on 2026-08-31 (D-108), but no code was changed to match. This spec lists every difference, splits the rebuild into work packages, and names the decisions only the founder can make. When it is done, the full GDD game runs from join to Postmortem on a TV with phones, driven by the Python engine.

---

# References

- Product authority: [D-108](../product/decisions-log.csv), [ADR 0023](../decisions/0023-nightcap-master-gdd-authority.md), [GDD decision ledger](../gdd/nightcap/00-governance/00-decision-ledger.md), [current design state](../gdd/nightcap/00-governance/02-current-design-state.md).
- Conflict rule: [repository migration and conflict policy](../gdd/nightcap/00-governance/05-repository-migration-and-conflict-policy.md). Old code is not treated as compliant.
- GDD system pages: [investigation](../gdd/nightcap/01-authoritative-gdd/02-investigation-deduction.md), [case board and memory](../gdd/nightcap/01-authoritative-gdd/03-case-board-memory.md), [minigames](../gdd/nightcap/01-authoritative-gdd/04-minigame-competitive-pulse.md), [Last Call and Case File](../gdd/nightcap/01-authoritative-gdd/05-last-call-case-file.md), [reactivity](../gdd/nightcap/01-authoritative-gdd/06-story-reactivity-reentry.md), [Leverage](../gdd/nightcap/01-authoritative-gdd/07-espionage-leverage-update.md), [Truth, Verdict, Postmortem](../gdd/nightcap/01-authoritative-gdd/08-truth-verdict-postmortem.md), [player count](../gdd/nightcap/01-authoritative-gdd/09-player-count-scaling.md), [difficulty and accessibility](../gdd/nightcap/01-authoritative-gdd/10-difficulty-accessibility.md), [runtime boundary](../gdd/nightcap/01-authoritative-gdd/11-arcwright-runtime-boundary.md), [world and content](../gdd/nightcap/01-authoritative-gdd/12-experience-world-content-boundaries.md).
- Validation state: [validation plan](../gdd/nightcap/02-validation/98-validation-state-and-remaining-plan.md). Gate 1 is not passed.
- Behavioural reference only: [spec 0091](0091-nightcap-v3.1-improvements.md) and `playtests/nightcap-paper-test-02-v3.1/`. Non-canon research fixture.
- Architecture: [arc execution](../architecture/03-arc-execution.md), `AGENTS.md` principles 1, 2, 4, 5 and 8.
- Tooling freeze: D-110, with its end condition changed on 2026-11-14 to the rebuild's first TV session (see Q1). This spec is product work and is not covered by the freeze.

**x-scope-evidence**: `D-108`. The GDD is approved game-design authority. This spec adds no product scope beyond the GDD. Items the GDD marks TESTING or OPEN are listed under Open Questions and are not approved by this spec.

---

# Overview

Rebuild Nightcap on the Arcwright engine so the shipped arc, engine primitives, API and TV and phone clients implement the full Master GDD: the WATCH, HUNT, THINK, PLAY, REACT loop, then Last Call, Case File, The Truth, The Verdict and The Postmortem. This file is the umbrella contract. Each work package below gets its own implementation spec and plan before code is written.

---

# Reconciliation: GDD against the current build

Evidence basis: structure of `nightcap/couch-race.arc.json`, public classes and functions in `engine/`, routes in `nightcap-web/src/worker.ts`, and keyword scans. This is a first pass. Work package 0 replaces it with a line-by-line inventory.

| # | GDD requirement | Current build | Gap |
|---|---|---|---|
| R1 | Repeating loop until Last Call | `beat_graph` is a six-beat line: pour, scene, grill, twist, last_call, truth | Arc cannot express a repeating investigative middle |
| R2 | Hidden authored case graph: canonical truth, investigation opportunities, per-player knowledge and proof kept distinct | `engine/case` resolves a case from skeletons and a taxonomy (`ResolvedCase`, `CaseFact`, `EvidenceEntry`) | No authored essential truths, routes or opportunity topology |
| R3 | Bounded, diegetic investigation with several live leads; action budget | One `investigation` interaction with five fixed options inside beats (`engine/interactions`) | No opportunity graph, no per-player budget across a loop |
| R4 | Knowledge is not proof; proof ownership tracked per player | Knowledge graph (`engine/knowledge`) and evidence delivery (`engine/claims/evidence.py`) | No admissibility model for the endgame |
| R5 | Detective notebook, living suspect cards, transcript, private notes | No code found | Entire system |
| R6 | Optional Case Board | No code found | Entire system |
| R7 | Story-triggered competitive windows; minigames reconnect to murder-facing state; performance tracked for tie-break | Mini-game runtime and four packages exist, placed in fixed beat slots | Trigger model, reward model, tie-break record |
| R8 | Visible rival activity without exposing private theory | One engine reference | Activity feed |
| R9 | REACT as a cross-cutting layer; re-entry shows state, not inference | Pacing interventions and narrator bridge exist | Reaction rules tied to player actions; re-entry summary |
| R10 | Leverage: small capped bank, information and opportunity effects, Counterintel | `engine/resources` with effect families and costs | Effect set, sourcing, caps and Counterintel differ |
| R11 | Last Call: hybrid trigger (authored timing plus minimum fair solvability), hard countdown, private simultaneous lock | `last_call` beat with countdown; `solvability_check` exists in `engine/case/invariants.py` | Trigger rule; lock semantics |
| R12 | Structured Reconstruction resolved deterministically; no numeric score | `engine/scoring` computes points, momentum, accusation value, wrong-accusation cost | Replace scoring with deterministic solve resolution |
| R13 | Accused-culprit reveal, then Truth, Verdict, Postmortem | `truth` beat with scoreboard; `superlatives.py` | Verdict rule, Postmortem from recorded behaviour |
| R14 | Two-player first-class; scaling adapts opportunity, not truth; Spotlight | Arc allows 2 to 8; D-052 floor was four | Scaling rules; Spotlight; two-player verification |
| R15 | Case Challenge, Investigation Pressure, Accessibility; readiness gates; group rescue | Not found | Entire system |
| R16 | TV and phone surfaces for all of the above | Host, shared display and join pages; Couch Race projection | New renderers; no arc logic in TypeScript |

Reusable without design change: deterministic arc state charts, knowledge graph, unified character model, model routing, safety layers, content events with audience targeting and presentation hints, session persistence and resume, telemetry, API, SDK.

---

# In Scope

Work packages. Order is dependency order. Task IDs are assigned by the Planner after approval.

- **WP0 Inventory.** Line-by-line reconciliation of arc JSON, engine modules, API routes, web client and tests against the GDD ledger. Output: a retire, keep, change map.
- **WP1 Case graph.** Engine schema and loader for an authored case graph: essential truths, accepted routes, investigation opportunities, proof groups, authorised deceptions. Invariants: every essential truth has at least two legal routes; solvable at every supported player count.
- **WP2 Loop arc.** Arc definition support for a repeating investigative phase and the hybrid Last Call trigger. New Nightcap arc file.
- **WP3 Investigation.** Opportunity availability, per-player action budget, shared baseline plus private unlocks, hypothesis-driven actions.
- **WP4 Proof ownership.** Per-player record of legitimately acquired case concepts, separate from heard claims.
- **WP5 Notebook and memory.** Factual notebook, living suspect cards, attributed transcript, private notes.
- **WP6 Case Board.** Player-built grouping, linking and annotation. No system-suggested relationships.
- **WP7 Competitive windows.** Story-triggered minigame windows, opportunity-first rewards with expiry, performance record for tie-break and Postmortem.
- **WP8 Rival activity and REACT.** Activity feed, reaction rules, re-entry summary.
- **WP9 Leverage and Counterintel.** Capped bank, contextual spend windows, observe and copy effects, Counterintel.
- **WP10 Last Call and Case File.** Countdown, private simultaneous lock, Structured Reconstruction input, deterministic resolver, tie-break.
- **WP11 Endgame.** Accused-culprit reveal, The Truth, The Verdict, The Postmortem.
- **WP12 Player count.** Scaling rules, Spotlight distribution, two-player parity.
- **WP13 Difficulty and accessibility.** Case Challenge, Investigation Pressure, accessibility settings, readiness gates, group rescue.
- **WP14 Surfaces.** TV and phone rendering for WP3 to WP13.
- **WP15 End to end.** API endpoints, persistence, headless harness run of a full session, then a local TV session.
- **First authored case.** One new case authored in the WP1 format for 2 to 4 players. See Q7.

---

# Out of Scope

- No-code story authoring tools. That is the next phase and targets the WP1 format.
- Cinematic audio and visual production beyond existing presentation hints.
- Cloud deployment (AW-269) and outside playtests (M6).
- Deleting Couch Race files or history. See Q9.
- Post-V1 free-form investigation, auctions, proclamation scenes, and other PARKED items.
- Changes to published playtest fixtures.

---

# Human Collaboration Contract

**Interaction profiles:** Decision interview for the open questions. Creative collaboration for the first case, Vesper lines, Postmortem voice and all player-facing copy. Independent execution for approved engine work. Facilitated live operation for the TV session.

**Classification rationale:** Twenty-plus GDD items are still TESTING or OPEN and need founder choices before code. Player-facing prose and interaction feel depend on founder taste. Engine primitives with approved acceptance criteria do not.

**Required founder inputs:**
- Answers to Q1 to Q10 below.
- Approval of this spec, then of each work package spec.
- Creative review of the first case and of each new surface before it is built in full.

**Phase gates:**
1. Approve this umbrella spec. Permits WP0 only.
2. Approve the WP0 inventory. Permits work package specs.
3. Approve each work package spec and plan. Permits that package.
4. Approve low-cost samples (wireframes, sample copy) before each surface in WP14.
5. Preflight, walkthrough, live TV session, debrief.

**Review package:** each gate arrives with a plain-language summary, what is fixed, what is open, how to review it, and what approval unlocks.

**Approval evidence:** founder chose "Rebuild to GDD first" and "Full GDD scope" in session on 2026-11-13. That approves direction only. It does not approve this spec.

**Owner actions:** play the TV session; recruit players for it.

## Your steps

1. Open this file and read "Plain-language goal" and the reconciliation table.
2. Answer Q1 to Q10. Each has a recommendation; "agree" is a valid answer.
3. Reply "approve 0092" or list changes.
4. Review the WP0 inventory when it arrives.

---

# Acceptance Criteria

Umbrella criteria. Each work package spec adds its own.

- [ ] WP0 inventory lists every arc field, engine public symbol, API route and web renderer touched by R1 to R16, each marked retire, keep or change, with file paths.
- [ ] A Nightcap arc file validates against the arc schema and expresses a repeating investigative phase ending at Last Call.
- [ ] The case loader rejects a case where any essential truth has fewer than two legal routes, with a test.
- [ ] A headless session at two players and at four players runs from join to Postmortem with no model call deciding state. Test asserts the event sequence.
- [ ] Final resolution is a pure function of the locked reconstructions and the case graph. Property test: same inputs, same verdict, no model call.
- [ ] One solver wins; several solvers tie-break on recorded minigame performance; no solver means no player winner. One test per branch.
- [ ] A claim heard from another player is not admissible proof until legitimately acquired. Test.
- [ ] Knowledge state is queried before every character generation (`scripts/checks/knowledge_query_guard.py` passes).
- [ ] `engine/` contains no Nightcap vocabulary added by this work, and the existing `nightcap` default in `engine/arc/registry.py` is removed or justified in WP0.
- [ ] `scripts/checks/provider_leak_check.py` passes. No arc logic in TypeScript.
- [ ] `pytest engine/tests/`, ruff, and SDK and web typecheck pass.
- [ ] A local session is played on a TV with two phones from join to Postmortem, with a recorded debrief.

---

# Approval-gated content

- Cross-module engine changes: arc, case, interactions, claims, knowledge, resources, mini_games, scoring, session, events.
- Database schema and migrations: proof ownership, notebook, Case Board, reconstruction, minigame performance.
- Prompts and evals: Truth and Postmortem expression; safety evals for new generated surfaces.
- No new dependencies are assumed. Any that arise need separate approval.

---

# Risks

- **Building an unvalidated design.** Gate 1 is not passed. Evidence may reopen DECIDED items. Mitigation: every TESTING value is arc configuration, not code.
- **Size.** Sixteen work packages across most engine modules. Mitigation: WP1, WP2, WP4 and WP10 form a playable spine; the rest attach to it.
- **Game vocabulary leaking into the engine.** Mitigation: engine primitives are generic (case graph, proof ownership, repeating phase, reconstruction validation); Nightcap names live in `nightcap/`.
- **State chart guards fail silently.** Verify configuration after every transition in tests.
- **Roadmap drift.** Open Couch Race tasks (AW-277 to AW-289) describe a superseded design. WP0 proposes their disposition.

---

# Open Questions

Each blocks the named work package. Recommendations are the author's, not decisions.

**Standing rule (founder, 2026-11-13):** follow the GDD. Raise a question only when a more recent decision exists, the GDD has no decision, the GDD is ambiguous, or the author believes the founder should reconsider for the good of the game.

- **Q1. Order against Gate 1.** RESOLVED 2026-11-13: founder chose to pause the v3.1 paper test while the rebuild runs. The v3.1 draft stays unpublished at its current gate. D-110 originally froze agent and knowledge-base tooling until the Gate 1 call. On 2026-11-14 the founder changed that end condition to "the rebuild's first TV session is played"; the Scribe is recording the pause and the new end condition in `docs/product/decisions-log.csv` from a separate session. Cite that row here once it has an ID.
- **Q2. Player count for this rebuild.** RESOLVED 2026-11-13: founder chose 2 to 4 players. Build, tune and test for 2 to 4; keep data shapes valid to 8. This scopes the rebuild only. The GDD's V1 upper bound remains OPEN.
- **Q3. Structured Reconstruction interaction (TESTING).** Recommendation (corrected 2026-11-13 after rereading the GDD page): pick the culprit, then arrange a short causal chain from concepts the player encountered, acquired or heard, including misleading ones, in the GDD's illustrative shape "culprit, then route, then act". Do not use per-truth question slots: the GDD says the interaction should not feel like "filling out a questionnaire". RESOLVED 2026-11-13: founder confirmed the repository GDD page is correct and the rebuild follows it: culprit plus a short arranged causal chain. Exact grammar stays arc and case configuration because the GDD marks it TESTING. Blocks: none.
- **Q4. Leverage sourcing, cap and costs (TESTING).** RESOLVED 2026-11-13: founder chose earned-only Leverage. Players start with none. Grants come from authored story moments and minigame results, with minigames not the primary source and no compounding from repeated wins (GDD law). Still to set in the WP9 spec: bank cap (author suggests 2), costs, and the per-case limit on minigame grants. All values are arc configuration. Blocks: none for start; WP9 spec sets the numbers.
- **Q5. Investigation action budget (TESTING).** RESOLVED 2026-11-13: founder chose a per-player budget, default six new investigations, review and earned follow-ups free, value in arc configuration. The first TV session records how long each player waits for others. Blocks: none.
- **Q6. Case Board scope.** RESOLVED from the GDD under the founder's standing rule (below): build the DECIDED tools only (connect, group, annotate, optional labels, structured comparison) on the private phone surface. Provenance, re-entry cues and search or filtering are TESTING in the GDD and are not built until evidence justifies them. Blocks: none.
- **Q7. First case.** RESOLVED 2026-11-13: founder chose a new case written for 2 to 4 players, not an adaptation of *A Knock at Midnight*. Quality bar in the founder's words: "BBC Sherlock quality mystery" that "does not feel or look like AI slop". The case is designed through creative collaboration in its own design document and needs founder approval at premise, design and full-prose stages. Blocks: first authored case; does not block WP0 to WP2.
  - **Spoiler rule (founder, 2026-11-13):** the founder stays unspoiled so he can play the case blind. He approves premise, cast, tone and sample scenes without the solution. Culprit, method, essential truths and routes live only in a file marked as spoilers and are never stated in chat, commit messages, PR text or review summaries addressed to him. Review of the solution is delegated to the case-graph invariants plus a separate reviewer session. This is an explicit founder delegation, not silence.
  - **Premise chosen 2026-11-13:** The Lido (August 1976). Player detectives are each hired separately before the death. Method log: `docs/design/authoring/case-method-logs/001-the-lido.md`.
  - **Session length (founder, 2026-11-13; GDD runtime is TESTING):** normally 30 minutes or less, never more than 60. Author's reading of the founder's sentence, to be confirmed. Arc configuration, and a measured outcome of the first TV session.
- **Q8. Suspect dialogue.** RESOLVED from the GDD: deterministic authored truth and state first, generative expression only within resolved state, and AI ownership expands only through evidence-gated autonomy. Suspects are unified character-model objects; authored lines ship first and generated expression is a per-element arc setting, constrained by knowledge state. Blocks: none.
- **Q9. Couch Race arc and code.** No GDD or product decision covers the code. Deferred to the WP0 inventory, which proposes a disposition per file for founder approval. Until then nothing is deleted or unregistered. Blocks: none for WP0.
- **Q10. Procedural case resolver.** RESOLVED from the GDD ("procedural scalability with authored quality", "hybrid library"): keep `engine/case` skeleton resolution. This rebuild's first case is authored in the WP1 format; how the two sources combine is specified in WP1. Blocks: none.
