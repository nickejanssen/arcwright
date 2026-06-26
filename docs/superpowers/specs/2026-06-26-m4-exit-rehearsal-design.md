# M4 Exit + First Real-Human Nightcap Rehearsal — Design

> Status: Approved (founder approved 2026-06-26 in brainstorming session)
> Author: Brainstorming session with founder, captured by Claude (Opus 4.7)
> Canonical path: docs/superpowers/specs/2026-06-26-m4-exit-rehearsal-design.md
> Next artifact: implementation plan at docs/superpowers/plans/2026-06-26-m4-exit-rehearsal-plan.md

---

## Purpose

This design consolidates the work required to close M4 (Nightcap Experience Layer) and run the first real-human Nightcap session. It supersedes GitHub issues #148 (AW-254) and #84 (AW-231) without losing any of their original context, acceptance criteria, or must-not constraints. It also schedules a second rehearsal and a polish thread that grow out of the same body of work but do not block M4 close.

The design is the input to the `writing-plans` skill, which will produce the batched implementation plan the executing chat consumes.

---

## Founder Decisions Locked in this Session

| Decision | Outcome | Recorded as |
|---|---|---|
| Scope of consolidated work | C: AW-254 + AW-231 + AW-257 (as promotion) + Rehearsal Runbook + AW-225 validation gate decision | This doc |
| Deployment strategy | D: Local + cloudflared tunnel for Rehearsal 1; cloud deploy deferred to a separate post-rehearsal task | D-065 |
| Production mini-game selection | Both existing draft games (Crime Scene Smash + Evidence Locker) promoted for Rehearsal 1; Tell Me Something True scheduled separately as Rehearsal 2 | D-064 |
| Polish bar for Rehearsal 1 | A: Tier 1 only (engineering correctness, performance, M4 exit-gate, basic UX, accessibility). Tier 2 (art, animation, sound, brand visual system) deferred to a dedicated polish thread | D-066 |
| Issue structure | Approach 2: parent issue AW-259 + sub-issues for each parallelizable unit; TMST and Polish get their own epics under M5 | This doc |

---

## Governance Answers Grounded in Canonical Docs

These were the founder's six governance questions; resolved answers below inform the design.

1. **GCP and Cloudflare provisioning is not required for Rehearsal 1.** Both are the locked production runtimes per ADR-0003 and `docs/architecture/02-technology-stack.md`, but the system is HTTP/SSE-based and can run a real-human rehearsal locally with a tunnel. ADR-0003 has an unresolved validation gate (compare Cloudflare vs GCP-only) that has been deferred since AW-225 closed. AW-261 in this design records that comparison decision; an actual cloud deploy becomes a later M5 task.

2. **Real-human testing instructions do not exist yet.** AW-240 (operations runbook) is M6 work. AW-260 in this design creates a Founder Rehearsal Runbook plus a Blocker Log Template covering pre-flight, setup, in-session checks, wrap, and a failure-mode decision tree.

3. **The "world-class polish" standard is split into Tier 1 (correctness, performance, basic UX, accessibility) for Rehearsal 1 and Tier 2 (visual identity, art, animation, sound) for a separate M5-G polish epic.** M4's exit gate is explicitly a non-qualifying rehearsal whose purpose is to surface blockers; investing in Tier 2 before any human has played wastes design budget on the wrong moments.

4. **M4 is 13-of-16 tasks complete.** Open items: #148 (AW-254 blocked on AW-257), #84 (AW-231 blocked on AW-254), four epic issues (#142, #47, #46, #44 — auto-close when children close), AW-257 missing a GitHub issue, AW-225 validation gate unresolved, AW-256 (last engine game-specific hardcode) tracked for M5. This design closes all M4-blocking items.

5. **Nightcap game design next steps:** story bible v1.1 locked. Two draft mini-games exist in repo and will be promoted by AW-257. Spec 0061 (AW-258 Tell Me Something True) is approved but unimplemented; M5-F epic in this design schedules its full build. Art and animation pipeline does not exist anywhere in the roadmap; M5-G epic in this design creates that thread.

6. **Engine vs game agnosticism is confirmed clean.** No hardcoded Nightcap game IDs, beats, characters, or accusation mechanics in `engine/` core execution paths. The single residual game-specific hardcode (AW-256) is already tracked in M5. Nightcap is configuration and content, not engine code. This is the platform-customer pattern AGENTS.md requires.

---

## Artifact Set

### New GitHub issues created by the executing chat

| ID | Title | Type | Milestone |
|---|---|---|---|
| AW-257 | Promote Crime Scene Smash and Evidence Locker to active | task | M4 |
| AW-259 | Rehearsal 1: M4 Exit, First Real-Human Nightcap Session | task (parent) | M4 |
| AW-260 | Founder Rehearsal Runbook and Blocker Log | task | M4 |
| AW-261 | ADR-0003 Cloudflare vs GCP Validation Decision | task | M4 |
| M5-F epic | Tell Me Something True Social Opener Implementation | epic | M5 |
| AW-262 | TMST Package Authoring and Schema Resolution | task | M5 |
| AW-263 | TMST Runtime: social-truth-bluff Mechanic | task | M5 |
| AW-264 | TMST API, Events, and SDK | task | M5 |
| AW-265 | TMST Web Rendering for Four Phases | task | M5 |
| AW-266 | Rehearsal 2: TMST Real-Human Session | task | M5 |
| M5-G epic | Nightcap Visual Identity and Polish | epic | M5 |
| AW-267 | Nightcap Art Direction Brief | task | M5 |
| AW-268 | Nightcap Asset Pipeline and Motion System | task | M5 |

### Repurposed GitHub issues

- **#148 (AW-254)** — body rewritten to: integration and device verification of the two promoted games. Original acceptance criteria preserved and extended for dual-game coverage. Depends on AW-257 and AW-261.
- **#84 (AW-231)** — body rewritten to: execute the rehearsal session. Original acceptance criteria preserved and tied to the new runbook. Depends on AW-254 and AW-260.

### Decision records created

| ID | Locks |
|---|---|
| D-064 | Two-rehearsal sequence. Crime Scene Smash and Evidence Locker ship in Rehearsal 1; TMST in Rehearsal 2 after full implementation. |
| D-065 | Local-tunnel deployment for Rehearsal 1. Cloud deployment deferred until AW-261 records ADR-0003 validation outcome. |
| D-066 | Tier 2 polish deferred to M5-G; Tier 1 polish is the Rehearsal 1 bar. |
| D-067 | (Filed by AW-261) Cloudflare vs GCP comparison outcome and resulting cloud path. |

### Roadmap files touched

- `docs/roadmap/index.json` — add 11 tasks + 2 epics; backfill GitHub issue numbers after creation; mark M4 epic statuses `complete` once children close.
- `docs/roadmap/milestones/M4-nightcap-experience-layer.md` — append "Closure" section listing AW-257..AW-261 as M4 close items.
- `docs/roadmap/milestones/M5-hardening-proof-prerequisites.md` — add M5-F and M5-G epics; note H1 proof depends on Rehearsal 1 and Rehearsal 2 outcomes.
- `docs/roadmap/tasks/AW-257-promote-crime-scene-smash-and-evidence-locker.md` (new)
- `docs/roadmap/tasks/AW-259-rehearsal-1-m4-exit.md` (new)
- `docs/roadmap/tasks/AW-260-founder-rehearsal-runbook-and-blocker-log.md` (new)
- `docs/roadmap/tasks/AW-261-adr-0003-cloudflare-vs-gcp-validation-decision.md` (new)
- `docs/roadmap/tasks/AW-262-tmst-package-authoring.md` (new)
- `docs/roadmap/tasks/AW-263-tmst-runtime-social-truth-bluff-mechanic.md` (new)
- `docs/roadmap/tasks/AW-264-tmst-api-events-and-sdk.md` (new)
- `docs/roadmap/tasks/AW-265-tmst-web-rendering-four-phases.md` (new)
- `docs/roadmap/tasks/AW-266-rehearsal-2-tmst-real-human-session.md` (new)
- `docs/roadmap/tasks/AW-267-nightcap-art-direction-brief.md` (new)
- `docs/roadmap/tasks/AW-268-nightcap-asset-pipeline-and-motion-system.md` (new)
- `docs/roadmap/epics/M5-F-tell-me-something-true-social-opener.md` (new)
- `docs/roadmap/epics/M5-G-nightcap-visual-identity-and-polish.md` (new)
- `docs/roadmap/operations/rehearsal-1-runbook.md` (new, authored by AW-260)
- `docs/roadmap/operations/blocker-log-template.md` (new, authored by AW-260)
- `docs/product/decisions-log.csv` — append D-064, D-065, D-066, D-067.
- `docs/decisions/0003-nightcap-web-experience-runtime.md` — Status line acknowledges AW-261 as the validation gate ticket; updated by AW-261 to "Accepted, validation complete".

---

## Dependency Graph for Rehearsal 1 (M4 Close)

```
Roadmap refresh (first task)
       |
       v
  AW-257 (promote both games)
       |
       +---------------------+--------+
       |                     |        |
       v                     v        v
  AW-261 (ADR-0003)    AW-260 (runbook)
       |                     |        |
       +-----------+---------+        |
                   v                  |
              AW-254 (verify) <-------+
                   |
                   v
              AW-231 (rehearse)
                   |
                   v
        AW-259 closes (M4 exit)
```

Roadmap refresh, AW-261, AW-257, and AW-260 are independent and can run in parallel worktrees per AGENTS.md `using-git-worktrees` guidance. AW-254 is the integration point. AW-231 is the founder-led rehearsal session.

---

## AW-259 Parent Issue Contract

**Title:** Rehearsal 1: M4 Exit, First Real-Human Nightcap Session
**Labels:** `task`, `size:L`, `M4`
**Milestone:** M4

**Body structure:**

1. **Plain-English summary** — three-sentence description of what closes M4 and why this is the single body of work.
2. **Scope** — five named threads with sub-issue links:
   - Promote two production mini-games (AW-257)
   - Resolve ADR-0003 validation gate as a paper decision (AW-261)
   - Author the Founder Rehearsal Runbook + Blocker Log (AW-260)
   - Integration and device verification of both promoted games (AW-254, repurposed)
   - Run the rehearsal, log blockers, triage them (AW-231, repurposed)
3. **Out of scope** — TMST implementation (M5-F), art and animation (M5-G), cloud deploy (deferred until AW-261 decision lands), v1.1 continuity, AI players, killer-assignment behavioral wiring.
4. **Supersedes** — explicit note that this issue absorbs #148 and #84 without losing their criteria; criteria preserved in AW-254 and AW-231 rewrites.
5. **Sub-issue tracking checklist** — AW-257, AW-261, AW-260, AW-254, AW-231.
6. **Definition of Done** — verbatim M4 exit gate plus Tier 1 polish:
   - Real humans played end-to-end on real devices.
   - Join flow under 30 seconds.
   - Private information never appeared on the shared display.
   - Both promoted mini-games completed on real devices through both normal and delayed-clue fallback paths.
   - All Tier 1 polish criteria met (zero crashes; loading / error / reconnect states on every screen; basic accessibility; 60fps target on mid-range Android).
   - Every rehearsal blocker is recorded in the blocker log and triaged into a new issue with milestone assignment before AW-259 closes.
   - Roadmap manifest reflects M4 closure and M5-F / M5-G epics exist.
7. **References** — story bible, ADR-0003, ADR-0009, AGENTS.md, AW-249 through AW-253 specs, D-061 through D-066.

---

## Sub-Issue Contracts for Rehearsal 1

### AW-257: Promote Crime Scene Smash and Evidence Locker to active

**Size:** M. **Labels:** `task`, `size:M`, `M4`. **Blocks:** AW-254.

**In scope:**
- Draft copy for the `[final authored copy needed]` placeholders in `nightcap/mini_games/crime-scene-smash/definitions/0.1.0.json` (narrator intro, success / fail / tie lines, leaderboard callouts). Executing chat drafts the copy in PR; founder reviews and approves before lifecycle promotion.
- Confirm Evidence Locker authored content is complete (already complete on inspection).
- Run AW-250 content and safety review for both packages.
- Bump both manifests to `lifecycle: active`.
- Bind both packages into `nightcap/arc.json` at the founder-specified beat positions.
- Confirm authored delayed-clue fallback per AW-249 / D-059 / ADR-0009 for both.

**Out of scope:** authoring a third game; promoting fixtures; runtime or engine changes; behavioral wiring into killer assignment.

**Acceptance:**
- Both packages validate against the AW-249 schema and loader.
- Both pass AW-250 safety review.
- Founder signs off on Crime Scene Smash authored copy.
- Both packages bound into `nightcap/arc.json`.
- D-062 record updated to also name Evidence Locker as an approved production package.

**Must-not:**
- Promote `_fixtures/*` or `_template`.
- Invent content without founder approval.
- Modify runtime, persistence, transport, or rendering.

**References:** Spec 0046 (AW-249), Spec 0047 (AW-250), ADR-0009, D-061, D-062.

### AW-260: Founder Rehearsal Runbook and Blocker Log

**Size:** S. **Labels:** `task`, `size:S`, `M4`. **Blocks:** AW-231.

**Deliverables:**
- `docs/roadmap/operations/rehearsal-1-runbook.md` — pre-flight (Docker up, migrations run, API keys set, tunnel command), session setup (shared display URL, player join URL and code, host check-in), in-session checks (privacy spot-check, mini-game launch timing), wrap (export session log, gather blocker notes).
- `docs/roadmap/operations/blocker-log-template.md` — single-row schema: timestamp, player count at incident, device and OS, what happened, what you expected, severity (P0 crash / P1 broken UX / P2 polish), repro steps, screenshot or video link.
- A one-page founder cheat sheet with decision tree for common failures: player disconnect, mini-game timeout, shared-display freeze, narrator silent.

**Out of scope:** outside-group operations (M6 AW-240); cloud deployment instructions (deferred to AW-261 follow-on).

**Acceptance:**
- Founder reads runbook cold and can execute every step without questions.
- Blocker template field-tested by walking through one fabricated blocker entry.

**References:** AW-240 (future M6 cousin), ADR-0003, M4-D epic.

### AW-261: ADR-0003 Cloudflare vs GCP Validation Decision

**Size:** S. **Labels:** `task`, `size:S`, `M4`. **Blocks:** AW-254.

**In scope:**
- Update `docs/decisions/0003-nightcap-web-experience-runtime.md` with the recorded comparison: what Cloudflare gives that Cloud Run + Firebase + Cloud CDN does not (or vice versa); what Rehearsal 1 (running on neither) does not tell us; what the decision criteria for the actual cloud deploy will be; which decision wins.

**Out of scope:** actually provisioning either provider; deploying anything; spending money. The deploy itself becomes a separate M5 task triggered by this decision.

**Acceptance:**
- ADR-0003 status moves from "Accepted with validation gate" to "Accepted, validation complete".
- D-067 records the comparison outcome.
- A follow-on M5 deployment task is filed (no implementation in AW-261).

### AW-254 (repurposed): Verify Two Promoted Mini-games on Real Devices

**Size:** M. **Labels:** `task`, `size:M`, `M4`. **Depends on:** AW-257, AW-261. **Blocks:** AW-231.

**In scope:**
- End-to-end run of Crime Scene Smash and Evidence Locker on the device matrix: iOS Safari, Android Chrome, mid-range Android, shared-display browser.
- Both clue paths verified (normal completion and authored delayed fallback) for each game.
- Privacy, reconnect, pause and resume, behavioral output, accessibility verification per AW-230 matrix.
- Tier 1 polish bar met: zero crashes, all loading and error and reconnect states present, 60fps target on mid-range Android, basic accessibility (color contrast, screen reader landmarks, keyboard navigation).

**Out of scope:** outside-group session (M6); art or animation polish; new game authoring; behavioral signals wired into killer assignment.

**Acceptance:**
- All AW-230 matrix cells pass for both games.
- Tier 1 polish gates pass.
- Founder demos both games end-to-end on a recorded call.

**Must-not:** activate fixtures; alter AW-202 runtime contract.

**References:** Spec 0051 (original AW-254 spec preserved), AW-230 matrix, ADR-0009.

### AW-231 (repurposed): Execute Real-Human Nightcap Rehearsal 1

**Size:** M. **Labels:** `task`, `size:M`, `M4`. **Depends on:** AW-254, AW-260.

**In scope:**
- Run the rehearsal per AW-260 runbook with real humans on real devices: founder plus at least three invitees, hitting the 4-player floor required for Crime Scene Smash.
- Record join timing, privacy results, mini-game completion or fallback for each game, session completion state, blockers.
- Triage every blocker into a follow-up GitHub issue with milestone assignment (M5 hardening, M5-G polish, M6 ops, or wontfix) before closing AW-231.

**Acceptance:**
- Rehearsal occurred.
- Every blocker has a GitHub issue.
- M4 milestone marked complete.

**Must-not:** run with fixtures only; bypass AW-202 runtime contract; bypass AW-260 runbook (if the runbook is wrong, fix the runbook).

**References:** preserved from original AW-231 spec, AW-260 runbook, ADR-0003.

---

## M5-F Epic: Tell Me Something True Social Opener Implementation

Parent epic that maps spec 0061 (AW-258) onto execution tasks across the four layers the spec already says it touches.

**Sub-tasks:**

- **AW-262: TMST Package Authoring and Schema Resolution** (M) — author `nightcap/mini_games/tell-me-something-true/` package; resolve the open `deflection_tendency` structured-output question raised in spec 0061 (either extend the AW-249 schema to support map-shaped behavioral outputs, or formalize the "scalar declaration plus event-payload-only" workaround); produce the authored delayed-clue fallback even though TMST is non-clue-gating per spec 0061's fallback contract; founder content sign-off required.
- **AW-263: TMST Runtime: social-truth-bluff Mechanic** (M) — add closed-registry mechanic in AW-251 runtime; Python owns input deadline, AFK auto-truth, accepted submissions, spotlight order, disconnect skip, vote acceptance, abstentions, truth reveal, score computation, signal computation, run completion; runtime must reject unknown mechanic types before run creation; no AI authority over truth, score, or votes.
- **AW-264: TMST API, Events, and SDK** (M) — extend AW-252 with typed payloads for input, spotlight, reveal, scoreboard phases; preserve privacy (private fact prompts go only to `specific_player`, shared display never sees another player's prompt before reveal, reconnect exposes only authorized state); SDK methods submit actions only.
- **AW-265: TMST Web Rendering for Four Phases** (M) — extend AW-253 to render all four phases on shared display and player devices; cover loading, timeout, disconnected, skipped, reveal, scoreboard states; narrator-led diegetic framing scaffold (High Society / Corporate / Sci-Fi per story bible and spec 0061); no canonical timing, scoring, outcome, or state logic in the web client.
- **AW-266: Rehearsal 2: TMST Real-Human Session** (M) — mirror of AW-231 pattern; promote TMST to active; run a real-human rehearsal with at least 4 humans using the Rehearsal-1 runbook updated for TMST specifics; log and triage blockers.

**Dependency chain:** AW-262 → AW-263 → AW-264 → AW-265 → AW-266. AW-266 also depends on AW-259 closure so that Rehearsal 1 blocker fixes are folded back before Rehearsal 2.

**Epic acceptance:**
- TMST runs end-to-end on real devices with at least 4 humans.
- All five DoD checks from AW-259 (translated to TMST context) pass.
- New blockers triaged.

**References:** Spec 0061 (AW-258), ADR-0009, D-063.

---

## M5-G Epic: Nightcap Visual Identity and Polish

Parent epic for all Tier 2 polish the founder deferred from Rehearsal 1. Does not block any rehearsal. Runs in parallel with M5-F when capacity allows.

**Sub-tasks:**

- **AW-267: Nightcap Art Direction Brief** (S) — founder-authored or commissioned brief defining visual identity, theme aesthetic per diegetic wrapper (High Society / Corporate / Sci-Fi per story bible section 2 and spec 0061), motion system principles, typography, color, narrator visual presence; output is a single canonical doc at `docs/design/nightcap-art-direction.md` plus reference moodboards; no code.
- **AW-268: Nightcap Asset Pipeline and Motion System** (M) — implementation of the brief: asset folder structure under `nightcap/assets/themes/<theme>/`, illustration set per theme, animation specs (Rive or Lottie or sprite — decision part of this task), motion tokens consumable by AW-253 web rendering; backfills polish into both Rehearsal 1 games and TMST.

**Epic acceptance:**
- Brief approved by founder.
- First theme implemented and visible in at least one mini-game.
- Crime Scene Smash, Evidence Locker, TMST all consuming the motion system.

**References:** Story bible section 2, spec 0061 "Diegetic Framing".

---

## Handoff Plan

The next chat (the executing chat) receives:

1. **This design doc** at `docs/superpowers/specs/2026-06-26-m4-exit-rehearsal-design.md`.
2. **The implementation plan** that the `writing-plans` skill will produce next, at `docs/superpowers/plans/2026-06-26-m4-exit-rehearsal-plan.md`.
3. **One-sentence brief** the founder hands to the executing chat:

   > Execute the plan at `docs/superpowers/plans/2026-06-26-m4-exit-rehearsal-plan.md`. Start with the roadmap-refresh task, then create AW-259 and use it as your tracking parent. Use git worktrees for parallel sub-tasks per AGENTS.md and CLAUDE.md.

**Executing chat's order of operations:**

1. Roadmap refresh — creates all manifest entries, creates GitHub issues for AW-257, AW-259, AW-260, AW-261, AW-262 through AW-268, M5-F epic, M5-G epic; backfills numbers into `docs/roadmap/index.json`.
2. Worktree 1 in parallel: AW-261 ADR-0003 decision (paper work).
3. Worktree 2 in parallel: AW-257 promote both games (content work).
4. Worktree 3 in parallel: AW-260 author runbook + blocker template (operational doc work).
5. After worktrees 2 and 3 land: AW-254 verification (single worktree, integration).
6. After AW-254 and AW-260 land: founder schedules and runs the rehearsal session (AW-231). Executing chat captures blockers, triages them into new issues, closes AW-259.
7. Out of scope for the executing chat: M5-F and M5-G are created as roadmap entries and GitHub issues but their sub-tasks await a separate execution chat in M5.

**What the founder must provide before the executing chat starts:**

- Confirmation that this design and the resulting plan are locked.
- API keys: Anthropic, Groq (already provisioned for engine work).
- For the cloudflared tunnel: either a free Cloudflare account + domain bound via the dashboard (more durable, 10 minutes setup), or use `cloudflared tunnel --url http://localhost:PORT` quick-tunnels (no account required, ephemeral random `*.trycloudflare.com` URL, fine for one-shot rehearsals). AW-260 runbook covers both paths.
- Schedule for at least three invitees to attend Rehearsal 1 (so the runbook is exercised at the 4-player floor).
- Sign-off on Crime Scene Smash narrator and leaderboard copy when AW-257 surfaces it.

---

## Out of Scope for This Body of Work

The following are intentionally excluded; tracked elsewhere or deferred.

- Cloud deployment of Arcwright engine or Nightcap web experience. Deferred until AW-261 records the ADR-0003 validation outcome, then handled as a separate M5 task.
- Tell Me Something True implementation. Scheduled as the M5-F epic; runs after Rehearsal 1.
- Nightcap art, animation, sound, brand visual system. Scheduled as the M5-G epic; runs after the art direction brief is approved.
- Outside-group qualifying sessions. M6 work (AW-243).
- v1.1 features: cross-session continuity, AI player slots, behavioral signals wired into killer assignment.
- Removing the last engine game-specific hardcode (AW-256). Already scheduled in M5-C.

---

## Risks and Unknowns

**Risks:**

- Crime Scene Smash content gaps (`[final authored copy needed]`) may surface design questions that take longer than the AW-257 size:M estimate. Mitigation: AW-257 founder sign-off step explicitly gates the lifecycle promotion; if copy is not ready, lifecycle stays at `playtest` and Rehearsal 1 proceeds with Evidence Locker only.
- The cloudflared tunnel could fail mid-rehearsal if the founder's laptop loses network. Mitigation: AW-260 runbook includes a "lost tunnel" recovery procedure.
- Rehearsal 1 blocker triage could surface a P0 that blocks M4 closure even after AW-259 is otherwise done. Mitigation: AW-231 acceptance ties M4 closure to "every blocker triaged into a milestone-assigned issue", not "every blocker fixed".

**Unknowns:**

- Which beat positions in `nightcap/arc.json` the founder wants for each promoted game. To be resolved during AW-257 founder sign-off.
- Whether the AW-261 decision lands on Cloudflare or GCP. AW-261 will resolve.
- Whether the founder runs Rehearsal 1 with exactly 4 humans (minimum) or more. Affects Crime Scene Smash leaderboard density.

---

## Open Questions (none blocking, surfaced for the executing chat)

- Should D-064 also cover Rehearsal 3 and beyond, or stay scoped to the two-rehearsal sequence?
- Should the AW-260 runbook be cross-referenced into the AW-240 M6 task spec now, so AW-240 inherits from it later?
- Should AW-267 art direction brief be a Scribe-driven doc or a founder-authored doc with Scribe doing the formatting?

---

## References

- `docs/decisions/0003-nightcap-web-experience-runtime.md`
- `docs/decisions/0006-nightcap-continuity-v11.md`
- `docs/decisions/0009-mini-game-runtime-boundary.md`
- `docs/specs/0046-aw-249-nightcap-mini-game-authoring-foundation.md`
- `docs/specs/0047-aw-250-mini-game-content-resolution-and-safety.md`
- `docs/specs/0048-aw-251-mini-game-runtime-persistence-and-clue-gating.md`
- `docs/specs/0049-aw-252-mini-game-api-events-and-sdk.md`
- `docs/specs/0050-aw-253-nightcap-web-mini-game-rendering.md`
- `docs/specs/0051-aw-254-first-production-nightcap-mini-game.md`
- `docs/specs/0060-aw-230-real-device-privacy-matrix.md`
- `docs/specs/0061-aw-258-tell-me-something-true.md`
- `docs/story-bibles/nightcap-murder-mystery.md`
- `docs/roadmap/milestones/M4-nightcap-experience-layer.md`
- `docs/roadmap/index.json`
- `docs/product/decisions-log.csv` (D-058, D-059, D-061, D-062, D-063)
- `AGENTS.md`, `CLAUDE.md`
- GitHub issues #148 (AW-254), #84 (AW-231)
