# M4 Exit + First Real-Human Nightcap Rehearsal — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers-extended-cc:subagent-driven-development (recommended) or superpowers-extended-cc:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close M4 (Nightcap Experience Layer) by promoting two existing draft mini-games (Crime Scene Smash + Evidence Locker) to production, recording the ADR-0003 cloud-runtime validation decision, authoring a Founder Rehearsal Runbook, verifying both games end-to-end on real devices, executing the first real-human Nightcap rehearsal, and scheduling Tell Me Something True (M5-F) and Nightcap Visual Identity + Polish (M5-G) as proper roadmap threads.

**Architecture:** Approach 2 from the design doc — one parent GitHub issue (AW-259) consolidates the body of work and supersedes #148 and #84; five sub-issues (AW-257, AW-260, AW-261, AW-254-repurposed, AW-231-repurposed) execute in dependency order with parallel worktrees where independent. Deployment for Rehearsal 1 is local Docker + cloudflared tunnel; cloud deploy is deferred to a follow-on M5 task. Polish is split into Tier 1 (this rehearsal) and Tier 2 (M5-G epic).

**Tech Stack:** Python 3.11+ engine, FastAPI, TypeScript SDK + web app, Postgres 15 + Alembic, LiteLLM routing to Anthropic + Groq, Docker for local engine, cloudflared for tunnel, GitHub CLI (`gh`) for issue management. Markdown for all roadmap docs.

**User decisions (already made):**
- Scope: AW-254 + AW-231 + AW-257 (as promotion) + Rehearsal Runbook + ADR-0003 validation decision, in one consolidated body of work (founder, brainstorm session 2026-06-26).
- Deployment: Local Docker + cloudflared tunnel for Rehearsal 1; cloud deploy is a separate later task (D-065).
- Games: Crime Scene Smash + Evidence Locker for Rehearsal 1; Tell Me Something True scheduled separately as Rehearsal 2 / M5-F (D-064).
- Polish bar: Tier 1 only for Rehearsal 1; Tier 2 deferred to M5-G epic (D-066).
- Issue structure: Approach 2 — parent issue AW-259 + sub-issues + separate epics for M5-F and M5-G.

---

## File Structure

### Files created

```
docs/roadmap/tasks/
  AW-257-promote-crime-scene-smash-and-evidence-locker.md
  AW-259-rehearsal-1-m4-exit.md
  AW-260-founder-rehearsal-runbook-and-blocker-log.md
  AW-261-adr-0003-cloudflare-vs-gcp-validation-decision.md
  AW-262-tmst-package-authoring-and-schema-resolution.md
  AW-263-tmst-runtime-social-truth-bluff-mechanic.md
  AW-264-tmst-api-events-and-sdk.md
  AW-265-tmst-web-rendering-four-phases.md
  AW-266-rehearsal-2-tmst-real-human-session.md
  AW-267-nightcap-art-direction-brief.md
  AW-268-nightcap-asset-pipeline-and-motion-system.md
docs/roadmap/epics/
  M5-F-tell-me-something-true-social-opener.md
  M5-G-nightcap-visual-identity-and-polish.md
docs/roadmap/operations/
  rehearsal-1-runbook.md
  blocker-log-template.md
  rehearsal-1-failure-cheat-sheet.md
```

### Files modified

```
docs/roadmap/index.json                                  — add 11 tasks + 2 epics + backfill issue numbers
docs/roadmap/milestones/M4-nightcap-experience-layer.md  — append "Closure" section
docs/roadmap/milestones/M5-hardening-proof-prerequisites.md  — add M5-F and M5-G to epic list
docs/product/decisions-log.csv                           — append D-064, D-065, D-066, D-067
docs/decisions/0003-nightcap-web-experience-runtime.md   — update status to "validation complete"
docs/roadmap/tasks/AW-254-first-production-nightcap-mini-game.md  — rewrite body to repurposed scope
docs/roadmap/tasks/AW-231-m4-real-human-rehearsal.md     — rewrite body to repurposed scope
nightcap/mini_games/crime-scene-smash/definitions/0.1.0.json  — fill copy placeholders
nightcap/mini_games/crime-scene-smash/manifest.json      — lifecycle "draft" → "active"
nightcap/mini_games/evidence-locker-402/manifest.json    — lifecycle "playtest" → "active"
nightcap/arc.json                                        — bind both mini-games at founder-chosen beat positions
```

### GitHub mutations

```
gh issue create AW-257  (M4, blocks AW-254)
gh issue create AW-259  (M4, parent, supersedes #148 + #84)
gh issue create AW-260  (M4, blocks AW-231)
gh issue create AW-261  (M4, blocks AW-254)
gh issue create AW-262..AW-266  (M5)
gh issue create AW-267, AW-268  (M5)
gh issue create M5-F epic, M5-G epic  (M5)
gh issue edit #148  (rewrite body to repurposed AW-254 scope)
gh issue edit #84   (rewrite body to repurposed AW-231 scope)
```

---

## Tasks

### Task 0: Author all roadmap docs, decision records, and milestone updates

**Goal:** Create every roadmap file, epic file, decision-log entry, and milestone update required by this plan, in a single commit, before any GitHub state changes.

**Files:**
- Create: `docs/roadmap/tasks/AW-257-promote-crime-scene-smash-and-evidence-locker.md`
- Create: `docs/roadmap/tasks/AW-259-rehearsal-1-m4-exit.md`
- Create: `docs/roadmap/tasks/AW-260-founder-rehearsal-runbook-and-blocker-log.md`
- Create: `docs/roadmap/tasks/AW-261-adr-0003-cloudflare-vs-gcp-validation-decision.md`
- Create: `docs/roadmap/tasks/AW-262-tmst-package-authoring-and-schema-resolution.md`
- Create: `docs/roadmap/tasks/AW-263-tmst-runtime-social-truth-bluff-mechanic.md`
- Create: `docs/roadmap/tasks/AW-264-tmst-api-events-and-sdk.md`
- Create: `docs/roadmap/tasks/AW-265-tmst-web-rendering-four-phases.md`
- Create: `docs/roadmap/tasks/AW-266-rehearsal-2-tmst-real-human-session.md`
- Create: `docs/roadmap/tasks/AW-267-nightcap-art-direction-brief.md`
- Create: `docs/roadmap/tasks/AW-268-nightcap-asset-pipeline-and-motion-system.md`
- Create: `docs/roadmap/epics/M5-F-tell-me-something-true-social-opener.md`
- Create: `docs/roadmap/epics/M5-G-nightcap-visual-identity-and-polish.md`
- Modify: `docs/roadmap/milestones/M4-nightcap-experience-layer.md` — append "Closure" section.
- Modify: `docs/roadmap/milestones/M5-hardening-proof-prerequisites.md` — add M5-F and M5-G to epic list.
- Modify: `docs/product/decisions-log.csv` — append D-064, D-065, D-066, D-067 (D-067 has placeholder rationale; AW-261 task fills it).

**Acceptance Criteria:**
- [ ] All 11 task .md files exist and follow the established roadmap-task format (Plain-English Summary, Why This Matters, Player Impact, Business Value, Technical Scope, Acceptance Criteria, Tests/Verification, Dependencies, Must Not Do, Architecture References, Playtest Relevance).
- [ ] M5-F and M5-G epic .md files exist and follow the established epic format (matching `docs/roadmap/epics/M5-A-adversarial-safety-and-remediation.md`).
- [ ] M4 milestone .md has a new "## Closure" section listing AW-257, AW-259, AW-260, AW-261 as M4 close items.
- [ ] M5 milestone .md lists M5-F and M5-G in the Epics section.
- [ ] `docs/product/decisions-log.csv` has 4 new rows (D-064, D-065, D-066, D-067).
- [ ] All files use LF line endings, no em dashes (per AGENTS.md docs convention), no secrets.

**Verify:** `git status --short && python -c "import csv; rows=list(csv.reader(open('docs/product/decisions-log.csv'))); print(f'Decision count: {len(rows)-1}')"` → shows 14 new files + 3 modified files + decision count is 4 higher than previous.

**Steps:**

- [ ] **Step 1: Create AW-257 task file**

Write `docs/roadmap/tasks/AW-257-promote-crime-scene-smash-and-evidence-locker.md`:

```markdown
# AW-257: Promote Crime Scene Smash and Evidence Locker to active

**Milestone / Epic:** M4 / M4-E
**Size:** M
**Status:** Planned

## Plain-English Summary

Promote the two existing draft Nightcap mini-game packages (Crime Scene Smash
and Evidence Locker) to the active lifecycle so Rehearsal 1 has two
production-quality games to verify on real devices.

## Why This Matters

AW-254 cannot start without at least one production-lifecycle mini-game
package. D-062 names Crime Scene Smash as the first production package; this
task fulfills D-062 and extends approval to Evidence Locker so Rehearsal 1
covers both a multi-player (Crime Scene Smash) and a solo (Evidence Locker)
mechanic.

## Player Impact

Real humans get two distinct mini-game experiences in Rehearsal 1, exercising
both the solo-clue-recovery and multi-player-leaderboard surfaces of the
Nightcap experience.

## Business Value

Two production-ready mini-games covers more of the M4 exit gate than a single
game and surfaces more blockers per rehearsal session.

## Technical Scope

- Draft copy for the `[final authored copy needed]` placeholders in
  `nightcap/mini_games/crime-scene-smash/definitions/0.1.0.json` (narrator
  intro, success line, fallback line, tie line, leaderboard callouts).
- Run AW-250 content and safety review on both packages.
- Bump `nightcap/mini_games/crime-scene-smash/manifest.json` lifecycle to
  `active`.
- Bump `nightcap/mini_games/evidence-locker-402/manifest.json` lifecycle to
  `active`.
- Bind both packages into `nightcap/arc.json` at the founder-chosen beat
  positions.
- Confirm each package declares an authored delayed clue fallback per
  AW-249 / D-059 / ADR-0009.

## Acceptance Criteria

- [ ] Crime Scene Smash copy placeholders replaced with founder-approved copy.
- [ ] Both packages validate against the AW-249 schema and loader.
- [ ] Both packages pass AW-250 content and safety review.
- [ ] Founder signs off on Crime Scene Smash authored copy before lifecycle
  promotion.
- [ ] Both manifests are at lifecycle `active`.
- [ ] Both packages are bound into `nightcap/arc.json` at founder-named beats.
- [ ] D-062 record is updated to also name Evidence Locker as an approved
  production package.

## Tests/Verification

- Run the AW-249 schema validator against both packages.
- Run the AW-250 safety review on both packages.
- Confirm `nightcap/arc.json` parses and references both package IDs.

## Dependencies

- AW-249 mini-game authoring foundation (complete)
- AW-250 mini-game content resolution and safety (complete)
- D-061 founder direction
- D-062 first production package decision

## Must Not Do

- Do not promote `_fixtures/*` or `_template` packages.
- Do not invent or ship content without founder approval.
- Do not modify runtime, persistence, transport, or rendering code.

## Architecture References

- `docs/decisions/0009-mini-game-runtime-boundary.md`
- `docs/specs/0046-aw-249-nightcap-mini-game-authoring-foundation.md`
- `docs/specs/0047-aw-250-mini-game-content-resolution-and-safety.md`
- `docs/story-bibles/nightcap-murder-mystery.md`

## Playtest Relevance

Produces the two production packages AW-254 needs to verify on real devices
before AW-231 runs the rehearsal.
```

- [ ] **Step 2: Create AW-259 parent task file**

Write `docs/roadmap/tasks/AW-259-rehearsal-1-m4-exit.md`:

```markdown
# AW-259: Rehearsal 1 — M4 Exit, First Real-Human Nightcap Session

**Milestone / Epic:** M4 (parent task; consolidates M4-D + M4-E close work)
**Size:** L
**Status:** Planned

## Plain-English Summary

Single body of work that closes M4 by running the first real-human Nightcap
session on real devices, using the two production mini-games promoted by
AW-257 and the runbook authored by AW-260. Supersedes GitHub issues #148
(AW-254) and #84 (AW-231) without losing their criteria; those tasks are
repurposed under this parent as the verification and execution units.

## Why This Matters

M4's exit gate is real humans playing end-to-end on real devices. This is the
first time Arcwright + Nightcap is exercised against the H1 proof contract
outside synthetic test harnesses. The blockers it surfaces drive M5 hardening
priorities.

## Player Impact

The founder and at least three invitees play the first end-to-end Nightcap
session. Real humans encounter every layer the platform has built so far:
join flow, host setup, shared display, private player events, mini-games,
clue gating, accusation, killer reveal.

## Business Value

Closes M4. Validates the Layer-2 narrative runtime contract under live human
conditions. Establishes the rehearsal cadence + blocker-triage discipline
Rehearsal 2 (M5-F AW-266) and future qualifying sessions (M6) inherit.

## Technical Scope

Coordination task. Owns the parent issue body, the Definition of Done, and
the closure ritual. Actual technical work lives in the sub-issues.

Sub-issues:
- AW-257 (promote both games)
- AW-261 (ADR-0003 validation decision)
- AW-260 (runbook + blocker template)
- AW-254 (device matrix verification, repurposed)
- AW-231 (rehearsal execution, repurposed)

## Acceptance Criteria

- [ ] Real humans played end-to-end on real devices.
- [ ] Join flow under 30 seconds for every player.
- [ ] Private information never appeared on the shared display.
- [ ] Both promoted mini-games completed on real devices through both normal
  and delayed-clue fallback paths.
- [ ] All Tier 1 polish criteria met: zero crashes, loading / error /
  reconnect states present on every screen, basic accessibility, 60fps
  target on mid-range Android.
- [ ] Every rehearsal blocker is recorded in the blocker log and triaged
  into a new GitHub issue with milestone assignment (M5 hardening, M5-G
  polish, M6 ops, or wontfix) before AW-259 closes.
- [ ] Roadmap manifest reflects M4 closure and M5-F + M5-G epics exist.

## Tests/Verification

- Verify every sub-issue is closed.
- Verify M4 milestone is at status `complete` in `docs/roadmap/index.json`.
- Verify M5-F and M5-G are present in `docs/roadmap/index.json` and in the
  M5 milestone epic list.

## Dependencies

- AW-257 (sub-issue)
- AW-261 (sub-issue)
- AW-260 (sub-issue)
- AW-254 (sub-issue, repurposed)
- AW-231 (sub-issue, repurposed)

## Must Not Do

- Do not duplicate AW-254 or AW-231 scope inside this parent (they own their
  units).
- Do not close AW-259 without triaging every blocker into a new issue.

## Architecture References

- `docs/roadmap/milestones/M4-nightcap-experience-layer.md`
- `docs/decisions/0003-nightcap-web-experience-runtime.md`
- `docs/decisions/0009-mini-game-runtime-boundary.md`
- `docs/superpowers/specs/2026-06-26-m4-exit-rehearsal-design.md`
- `AGENTS.md`

## Playtest Relevance

This task is the M4 exit gate. Its closure marks M4 complete and unblocks M5.
```

- [ ] **Step 3: Create AW-260 runbook task file**

Write `docs/roadmap/tasks/AW-260-founder-rehearsal-runbook-and-blocker-log.md`:

```markdown
# AW-260: Founder Rehearsal Runbook and Blocker Log

**Milestone / Epic:** M4 / M4-D
**Size:** S
**Status:** Planned

## Plain-English Summary

Author the one-page Founder Rehearsal Runbook, the Blocker Log Template, and
the Failure Cheat Sheet that make Rehearsal 1 runnable by the founder and
reportable to the executing chat.

## Why This Matters

AW-231 cannot run without a runbook. AW-240 (the M6 operations runbook) is
not yet scoped or built. This is the minimum-viable operational doc set for
a non-qualifying rehearsal.

## Player Impact

The founder can run a rehearsal session without ad-hoc setup decisions, and
players experience a session that started cleanly because the host followed
a tested procedure.

## Business Value

Establishes the blocker-capture discipline that turns rehearsal output into
prioritized M5 / M5-G / M6 work items, instead of vague impressions.

## Technical Scope

- Author `docs/roadmap/operations/rehearsal-1-runbook.md` with pre-flight,
  session setup, in-session checks, and wrap sections.
- Author `docs/roadmap/operations/blocker-log-template.md` with a single-row
  schema and one filled-in example row.
- Author `docs/roadmap/operations/rehearsal-1-failure-cheat-sheet.md` with a
  decision tree for player disconnect, mini-game timeout, shared-display
  freeze, narrator silent, tunnel dropped.

## Acceptance Criteria

- [ ] Runbook covers pre-flight (Docker up, migrations run, API keys set,
  tunnel command), session setup (URLs, codes, host check-in), in-session
  checks (privacy spot-check, mini-game launch timing), wrap (export
  session log, gather blocker notes).
- [ ] Blocker template has fields: timestamp, player count at incident,
  device + OS, what happened, what you expected, severity (P0 crash / P1
  broken UX / P2 polish), repro steps, screenshot or video link.
- [ ] Failure cheat sheet covers at least 5 failure modes with concrete
  recovery actions.
- [ ] Founder reads runbook cold and can execute every step without
  questions (validate by walking through it on a call).
- [ ] Blocker template field-tested by walking through one fabricated
  blocker entry end-to-end.

## Tests/Verification

- Founder walkthrough on call.
- Fabricated-blocker walkthrough.

## Dependencies

- AW-202 web runtime contract (informs tunnel + URL setup)
- AW-230 real-device privacy matrix (informs in-session privacy checks)

## Must Not Do

- Do not include outside-group operations content (that is M6 AW-240).
- Do not include cloud deployment instructions (deferred to AW-261 follow-on).

## Architecture References

- `docs/decisions/0003-nightcap-web-experience-runtime.md`
- `docs/roadmap/epics/M4-D-real-device-privacy-and-join-validation.md`
- `AGENTS.md`

## Playtest Relevance

Unblocks AW-231. Becomes the seed document for AW-240 (M6 closed-playtest
operations runbook).
```

- [ ] **Step 4: Create AW-261 ADR validation task file**

Write `docs/roadmap/tasks/AW-261-adr-0003-cloudflare-vs-gcp-validation-decision.md`:

```markdown
# AW-261: ADR-0003 Cloudflare vs GCP Validation Decision

**Milestone / Epic:** M4 / M4-A (closes AW-225 validation gate)
**Size:** S
**Status:** Planned

## Plain-English Summary

Record the Cloudflare vs GCP comparison the AW-225 acceptance criteria
require, close the ADR-0003 validation gate, and file a follow-on M5 task
for the actual cloud deployment.

## Why This Matters

AW-225 closed without recording the comparison ADR-0003 requires before
adding Cloudflare-specific dependencies. This validation gate has been
hanging since 2026-06-22. AW-254 needs the path resolved (or formally
deferred) before Rehearsal 2 picks a cloud target.

## Player Impact

None directly. Indirectly: production deploy quality + cost depend on
choosing the right cloud surface.

## Business Value

Closes a long-standing decision debt. Sets the cloud path criteria so a
future deploy task is unambiguous.

## Technical Scope

- Update `docs/decisions/0003-nightcap-web-experience-runtime.md` with:
  - what Cloudflare gives that Cloud Run + Firebase + Cloud CDN does not,
  - what Cloud Run + Firebase + Cloud CDN gives that Cloudflare does not,
  - what Rehearsal 1 (running on neither) does not tell us,
  - decision criteria for the actual cloud deploy,
  - which decision wins.
- Append D-067 to `docs/product/decisions-log.csv` recording the outcome.
- File a new GitHub issue (AW-269 candidate; manifest entry added during
  this task) for the actual cloud deploy implementation in M5.

## Acceptance Criteria

- [ ] ADR-0003 status moves from "Accepted with validation gate" to
  "Accepted, validation complete".
- [ ] D-067 records the comparison outcome with rationale.
- [ ] A new M5 task entry is added to `docs/roadmap/index.json` and a
  corresponding GitHub issue exists for the cloud deploy implementation.

## Tests/Verification

- ADR-0003 status line confirmed.
- Decision log row D-067 exists with non-placeholder rationale.
- New cloud-deploy issue exists in GitHub and in the manifest.

## Dependencies

- ADR-0003 already exists
- AW-225 closed (the validation gate it left open)

## Must Not Do

- Do not provision either provider in this task.
- Do not deploy anything in this task.
- Do not spend money in this task.

## Architecture References

- `docs/decisions/0003-nightcap-web-experience-runtime.md`
- `docs/architecture/02-technology-stack.md`
- `docs/roadmap/epics/M4-A-nightcap-external-platform-integration.md`

## Playtest Relevance

Unblocks AW-254 (verification can start without ambiguity about the future
cloud path) and seeds the M5 cloud deploy work that hosts Rehearsal 2.
```

- [ ] **Step 5: Create AW-262..AW-266 TMST task files**

Create each of the five TMST task files in `docs/roadmap/tasks/` following the same template as AW-257 above, with the contents derived from the design doc (`docs/superpowers/specs/2026-06-26-m4-exit-rehearsal-design.md` § "M5-F Epic"). Each file MUST follow the established roadmap-task structure (the same headings as AW-257). Key fields per task:

`AW-262-tmst-package-authoring-and-schema-resolution.md`:
- Size M, Status Planned, M5 / M5-F.
- Scope: author `nightcap/mini_games/tell-me-something-true/` package; resolve `deflection_tendency` structured-output schema question; produce authored delayed-clue fallback.
- Depends on: AW-249, AW-250, AW-258 (spec 0061), D-063.
- Must not: ship runtime, API, SDK, or rendering code.

`AW-263-tmst-runtime-social-truth-bluff-mechanic.md`:
- Size M, Status Planned, M5 / M5-F.
- Scope: add closed-registry `social-truth-bluff` mechanic to AW-251 runtime; Python owns input deadline, AFK auto-truth, accepted submissions, spotlight order, disconnect skip, vote acceptance, abstentions, truth reveal, score and signal computation, run completion; runtime rejects unknown mechanic types before run creation.
- Depends on: AW-262, AW-251.
- Must not: call AI to decide truth, score, votes, signals, or outcomes.

`AW-264-tmst-api-events-and-sdk.md`:
- Size M, Status Planned, M5 / M5-F.
- Scope: extend AW-252 with typed payloads for input/spotlight/reveal/scoreboard phases; preserve privacy (private fact prompts go only to `specific_player`, shared display never sees another player's prompt before reveal, reconnect exposes only authorized state); SDK methods submit actions only.
- Depends on: AW-263, AW-252.

`AW-265-tmst-web-rendering-four-phases.md`:
- Size M, Status Planned, M5 / M5-F.
- Scope: extend AW-253 to render all four phases on shared display and player devices; loading / timeout / disconnected / skipped / reveal / scoreboard states; narrator-led diegetic framing (High Society / Corporate / Sci-Fi); no canonical timing, scoring, outcome, or state logic in the web client.
- Depends on: AW-264, AW-253.

`AW-266-rehearsal-2-tmst-real-human-session.md`:
- Size M, Status Planned, M5 / M5-F.
- Scope: promote TMST to active; run real-human rehearsal with at least 4 humans using updated runbook; log + triage blockers (same discipline as AW-231).
- Depends on: AW-265, AW-259 (Rehearsal 1 closure).
- Must not: bypass the runbook (fix the runbook instead).

- [ ] **Step 6: Create AW-267 and AW-268 polish task files**

Create both polish task files in `docs/roadmap/tasks/` following the established template. Key fields:

`AW-267-nightcap-art-direction-brief.md`:
- Size S, Status Planned, M5 / M5-G.
- Scope: founder-authored or commissioned brief defining visual identity, theme aesthetic per diegetic wrapper (High Society / Corporate / Sci-Fi per story bible section 2 and spec 0061), motion system principles, typography, color, narrator visual presence; output is `docs/design/nightcap-art-direction.md` plus reference moodboards.
- Depends on: story bible v1.1, spec 0061.
- Must not: ship any code.

`AW-268-nightcap-asset-pipeline-and-motion-system.md`:
- Size M, Status Planned, M5 / M5-G.
- Scope: implementation of the brief; asset folder structure under `nightcap/assets/themes/<theme>/`; illustration set per theme; animation specs (decide Rive vs Lottie vs sprite as part of this task); motion tokens consumable by AW-253 web rendering.
- Depends on: AW-267.

- [ ] **Step 7: Create M5-F and M5-G epic files**

Write `docs/roadmap/epics/M5-F-tell-me-something-true-social-opener.md`:

```markdown
# M5-F: Tell Me Something True Social Opener Implementation

**Milestone:** M5
**Status:** Planned

## Plain-English Summary

Implement the full Tell Me Something True social-opener mini-game across
package, runtime, API, SDK, and web layers; then run Rehearsal 2 with real
humans.

## Why This Matters

Spec 0061 (AW-258) is approved but unimplemented. D-064 sequences TMST as
Rehearsal 2 (after the Rehearsal 1 promotion-only path closes M4). This
epic carries that sequencing into execution.

## Player Impact

A polished social opener that runs in beats 1-3 of a Nightcap session,
giving players a low-stakes warm-up before the murder mystery proper begins.

## Business Value

Validates the platform's mini-game extensibility under a net-new mechanic
type (`social-truth-bluff`) and a 4-phase shared-display + private-device
flow that exercises the API event filtering and privacy contract more
thoroughly than the single-phase Rehearsal 1 mini-games do.

## Technical Scope

The technical scope is limited to the tasks listed below and the
architecture references named in those task files.

## Tasks

- [AW-262: TMST Package Authoring and Schema Resolution](../tasks/AW-262-tmst-package-authoring-and-schema-resolution.md)
- [AW-263: TMST Runtime — social-truth-bluff Mechanic](../tasks/AW-263-tmst-runtime-social-truth-bluff-mechanic.md)
- [AW-264: TMST API, Events, and SDK](../tasks/AW-264-tmst-api-events-and-sdk.md)
- [AW-265: TMST Web Rendering for Four Phases](../tasks/AW-265-tmst-web-rendering-four-phases.md)
- [AW-266: Rehearsal 2 — TMST Real-Human Session](../tasks/AW-266-rehearsal-2-tmst-real-human-session.md)

## Acceptance Criteria

- All child tasks satisfy their acceptance criteria.
- TMST runs end-to-end on real devices with at least 4 humans.
- Privacy contract held under the 4-phase flow.

## Tests/Verification

- Verify every child task is complete and has evidence linked from its task
  issue.
- Verify Rehearsal 2 (AW-266) ran and its blockers are triaged.

## Dependencies

- Parent milestone: M5
- AW-259 (Rehearsal 1) closed (so Rehearsal 1 blocker fixes are folded
  back before Rehearsal 2)
- AW-258 spec 0061 approved (already)

## Must Not Do

- Do not skip any of the four implementation layers (package, runtime,
  API/SDK, web).
- Do not wire behavioral signals into killer assignment or cross-session
  behavior (v1.1 work per spec 0061).
- Do not run Rehearsal 2 with fixtures only.

## Architecture References

- `docs/specs/0061-aw-258-tell-me-something-true.md`
- `docs/decisions/0009-mini-game-runtime-boundary.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

Adds a second real-human rehearsal data point and validates a richer
mini-game surface than Rehearsal 1.
```

Write `docs/roadmap/epics/M5-G-nightcap-visual-identity-and-polish.md`:

```markdown
# M5-G: Nightcap Visual Identity and Polish

**Milestone:** M5
**Status:** Planned

## Plain-English Summary

Author the Nightcap art direction brief and implement the asset pipeline +
motion system so all mini-games (Crime Scene Smash, Evidence Locker, Tell
Me Something True) consume the same visual identity.

## Why This Matters

Tier 1 polish (engineering correctness, performance, basic UX) ships in
Rehearsal 1. Tier 2 polish (visual identity, art, animation) was
explicitly deferred per D-066 to avoid art-directing before any human had
played. After Rehearsal 1, this epic ships Tier 2.

## Player Impact

Players see a polished, themed product instead of a functional prototype.

## Business Value

Closes the gap between "rehearsal-quality" and "demo-quality" for outside
audiences and qualifying sessions in M6.

## Technical Scope

The technical scope is limited to the tasks listed below.

## Tasks

- [AW-267: Nightcap Art Direction Brief](../tasks/AW-267-nightcap-art-direction-brief.md)
- [AW-268: Nightcap Asset Pipeline and Motion System](../tasks/AW-268-nightcap-asset-pipeline-and-motion-system.md)

## Acceptance Criteria

- All child tasks satisfy their acceptance criteria.
- The art direction brief is approved by the founder.
- At least one theme is implemented and visible in at least one mini-game.
- Crime Scene Smash, Evidence Locker, and Tell Me Something True all
  consume the motion system.

## Tests/Verification

- Brief approval recorded in the decision log.
- Visual diff (screenshots before / after) of at least one mini-game.

## Dependencies

- Parent milestone: M5
- AW-259 (Rehearsal 1) closed (Tier 2 work informed by Rehearsal 1 findings)

## Must Not Do

- Do not block any rehearsal on this epic.
- Do not couple visual tokens to a single mini-game.

## Architecture References

- `docs/story-bibles/nightcap-murder-mystery.md`
- `docs/specs/0061-aw-258-tell-me-something-true.md`

## Playtest Relevance

Brings the product to demo-quality for M6 qualifying sessions.
```

- [ ] **Step 8: Append "Closure" section to M4 milestone file**

Append to `docs/roadmap/milestones/M4-nightcap-experience-layer.md` (after the existing "## Exit Gate" section):

```markdown

## Closure

M4 closes via the AW-259 parent task. The four M4 close items are:

- [AW-257: Promote Crime Scene Smash and Evidence Locker to active](../tasks/AW-257-promote-crime-scene-smash-and-evidence-locker.md)
- [AW-260: Founder Rehearsal Runbook and Blocker Log](../tasks/AW-260-founder-rehearsal-runbook-and-blocker-log.md)
- [AW-261: ADR-0003 Cloudflare vs GCP Validation Decision](../tasks/AW-261-adr-0003-cloudflare-vs-gcp-validation-decision.md)
- [AW-259: Rehearsal 1 — M4 Exit, First Real-Human Nightcap Session](../tasks/AW-259-rehearsal-1-m4-exit.md) (parent; consumes AW-254 and AW-231 as sub-issues)

AW-254 and AW-231 retain their original issue numbers (#148, #84) but their
scope is rewritten per `docs/superpowers/specs/2026-06-26-m4-exit-rehearsal-design.md`.
```

- [ ] **Step 9: Add M5-F and M5-G to M5 milestone file**

Modify `docs/roadmap/milestones/M5-hardening-proof-prerequisites.md`. After the existing "M5-E" line in the "## Epics" section, add:

```markdown
- [M5-F: Tell Me Something True Social Opener Implementation](../epics/M5-F-tell-me-something-true-social-opener.md)
- [M5-G: Nightcap Visual Identity and Polish](../epics/M5-G-nightcap-visual-identity-and-polish.md)
```

- [ ] **Step 10: Append D-064, D-065, D-066, D-067 to decisions log**

Append to `docs/product/decisions-log.csv` (preserving CSV format; quote fields containing commas; no em dashes):

```csv
Two-rehearsal sequence for Nightcap mini-games,"June 26, 2026","Crime Scene Smash and Evidence Locker promoted for Rehearsal 1 (M4 close). Tell Me Something True implemented and rehearsed separately as Rehearsal 2 in M5-F. Splits a multi-week effort into a 1-week M4 close plus a sequenced M5 epic so the founder can run a real-human session this week and feed its blockers into TMST work.",Section: Roadmap,Committed,"roadmap, nightcap"
Local-tunnel deployment for Rehearsal 1,"June 26, 2026","Rehearsal 1 runs on local Docker (engine + Postgres) plus cloudflared tunnel exposing the web app to player phones. Cloud deployment deferred until AW-261 records the ADR-0003 validation outcome and a follow-on M5 task provisions it. Avoids coupling first-real-human session to cloud-infrastructure setup risk.",Section: Roadmap,Committed,"roadmap, infrastructure"
Polish tier split for Rehearsal 1,"June 26, 2026","Tier 1 polish (engineering correctness, performance, M4 exit-gate criteria, basic UX states, accessibility) is the Rehearsal 1 bar. Tier 2 polish (visual identity, art, animation, sound, brand system) deferred to M5-G epic. Rationale: rehearsal exists to surface blockers; investing in Tier 2 before any human has played wastes design budget on the wrong moments.",Section: Roadmap,Committed,"roadmap, polish"
ADR-0003 Cloudflare vs GCP validation outcome,"<AW-261 fills this date>","Placeholder rationale; AW-261 task fills this with the recorded comparison outcome and the chosen cloud path.",Section: Architecture,Pending,"roadmap, infrastructure"
```

- [ ] **Step 11: Commit**

```bash
git add docs/roadmap/tasks/AW-257-*.md docs/roadmap/tasks/AW-259-*.md docs/roadmap/tasks/AW-260-*.md docs/roadmap/tasks/AW-261-*.md docs/roadmap/tasks/AW-262-*.md docs/roadmap/tasks/AW-263-*.md docs/roadmap/tasks/AW-264-*.md docs/roadmap/tasks/AW-265-*.md docs/roadmap/tasks/AW-266-*.md docs/roadmap/tasks/AW-267-*.md docs/roadmap/tasks/AW-268-*.md docs/roadmap/epics/M5-F-*.md docs/roadmap/epics/M5-G-*.md docs/roadmap/milestones/M4-nightcap-experience-layer.md docs/roadmap/milestones/M5-hardening-proof-prerequisites.md docs/product/decisions-log.csv
git commit -m "docs(roadmap): author M4-close and M5-F/M5-G roadmap docs"
```

Expected: pre-commit hooks pass (ruff skipped, secret detector clean, no temporary markers); one commit landed.

```json:metadata
{"files": ["docs/roadmap/tasks/AW-257-promote-crime-scene-smash-and-evidence-locker.md", "docs/roadmap/tasks/AW-259-rehearsal-1-m4-exit.md", "docs/roadmap/tasks/AW-260-founder-rehearsal-runbook-and-blocker-log.md", "docs/roadmap/tasks/AW-261-adr-0003-cloudflare-vs-gcp-validation-decision.md", "docs/roadmap/tasks/AW-262-tmst-package-authoring-and-schema-resolution.md", "docs/roadmap/tasks/AW-263-tmst-runtime-social-truth-bluff-mechanic.md", "docs/roadmap/tasks/AW-264-tmst-api-events-and-sdk.md", "docs/roadmap/tasks/AW-265-tmst-web-rendering-four-phases.md", "docs/roadmap/tasks/AW-266-rehearsal-2-tmst-real-human-session.md", "docs/roadmap/tasks/AW-267-nightcap-art-direction-brief.md", "docs/roadmap/tasks/AW-268-nightcap-asset-pipeline-and-motion-system.md", "docs/roadmap/epics/M5-F-tell-me-something-true-social-opener.md", "docs/roadmap/epics/M5-G-nightcap-visual-identity-and-polish.md", "docs/roadmap/milestones/M4-nightcap-experience-layer.md", "docs/roadmap/milestones/M5-hardening-proof-prerequisites.md", "docs/product/decisions-log.csv"], "verifyCommand": "git diff HEAD~1 --stat && python -c \"import csv; rows=list(csv.reader(open('docs/product/decisions-log.csv'))); print('decisions:', len(rows)-1)\"", "acceptanceCriteria": ["11 task .md files exist", "2 epic .md files exist", "M4 milestone has Closure section", "M5 milestone lists M5-F and M5-G", "4 new decision-log rows"], "modelTier": "mechanical"}
```

---

### Task 1: Create GitHub issues and backfill manifest

**Goal:** Create the 13 new GitHub issues (11 tasks + 2 epics) and update `docs/roadmap/index.json` with all new task / epic entries plus their GitHub issue numbers.

**Files:**
- Modify: `docs/roadmap/index.json` — add 11 task entries (AW-257, AW-259..AW-268), 2 epic entries (M5-F, M5-G); backfill issue numbers after creation.

**Acceptance Criteria:**
- [ ] 13 new GitHub issues exist in `nickejanssen/arcwright` with correct labels (`task` + `size:X` + `M4`/`M5`, or `Epic` + `M5`) and milestones (M4 or M5).
- [ ] AW-259 issue body links to AW-257, AW-260, AW-261, #148, #84 as sub-issues.
- [ ] `docs/roadmap/index.json` has all 11 new task entries under `tasks[]` and 2 new epic entries under `epics[]`, each with the correct `github.issue_number` and `github.url`.
- [ ] Manifest `version` field is bumped to `1.3`.

**Verify:** `gh issue list --repo nickejanssen/arcwright --label M4 --state open --limit 20 && jq '.tasks[] | select(.id | test("AW-25[7-9]|AW-26[0-8]")) | {id, github}' docs/roadmap/index.json` → all 11 task entries returned with non-null GitHub issue numbers.

**Steps:**

- [ ] **Step 1: Create AW-257 issue**

```bash
gh issue create --repo nickejanssen/arcwright \
  --title "AW-257: Promote Crime Scene Smash and Evidence Locker to active" \
  --label "task,size:M,M4" \
  --milestone "M4: Nightcap Experience Layer" \
  --body-file docs/roadmap/tasks/AW-257-promote-crime-scene-smash-and-evidence-locker.md
```

Capture the printed issue URL. Note the number.

- [ ] **Step 2: Create AW-259, AW-260, AW-261 issues**

For each, run `gh issue create` with the corresponding task .md file as `--body-file`, the title `AW-NNN: <Title>`, labels `task,size:<S/M/L>,M4`, milestone M4. Capture each issue number.

For AW-259 specifically, after creation, edit the body to add the sub-issue checklist with real numbers:

```bash
gh issue edit <AW-259-number> --repo nickejanssen/arcwright --body-file - <<'EOF'
[paste AW-259 body, with the sub-issue checklist section listing:
- [ ] AW-257 (#<actual-number>)
- [ ] AW-261 (#<actual-number>)
- [ ] AW-260 (#<actual-number>)
- [ ] AW-254 (#148, repurposed)
- [ ] AW-231 (#84, repurposed)
]
EOF
```

- [ ] **Step 3: Create M5-F and M5-G epic issues**

```bash
gh issue create --repo nickejanssen/arcwright \
  --title "M5-F: Tell Me Something True Social Opener Implementation" \
  --label "Epic,M5" \
  --milestone "M5: Hardening + Proof Prerequisites" \
  --body-file docs/roadmap/epics/M5-F-tell-me-something-true-social-opener.md

gh issue create --repo nickejanssen/arcwright \
  --title "M5-G: Nightcap Visual Identity and Polish" \
  --label "Epic,M5" \
  --milestone "M5: Hardening + Proof Prerequisites" \
  --body-file docs/roadmap/epics/M5-G-nightcap-visual-identity-and-polish.md
```

Capture epic issue numbers.

- [ ] **Step 4: Create AW-262..AW-266 (TMST tasks) issues**

For each of AW-262, AW-263, AW-264, AW-265, AW-266, run `gh issue create` with the corresponding task .md as `--body-file`, labels `task,size:M,M5`, milestone M5. Capture each number.

- [ ] **Step 5: Create AW-267 and AW-268 (polish tasks) issues**

```bash
gh issue create --repo nickejanssen/arcwright \
  --title "AW-267: Nightcap Art Direction Brief" \
  --label "task,size:S,M5" \
  --milestone "M5: Hardening + Proof Prerequisites" \
  --body-file docs/roadmap/tasks/AW-267-nightcap-art-direction-brief.md

gh issue create --repo nickejanssen/arcwright \
  --title "AW-268: Nightcap Asset Pipeline and Motion System" \
  --label "task,size:M,M5" \
  --milestone "M5: Hardening + Proof Prerequisites" \
  --body-file docs/roadmap/tasks/AW-268-nightcap-asset-pipeline-and-motion-system.md
```

- [ ] **Step 6: Update `docs/roadmap/index.json`**

Bump `"version": "1.2"` to `"version": "1.3"`. Add task entries (preserving alphabetical/numerical order in the `tasks[]` array) following the established schema. Example for AW-257:

```json
{
  "id": "AW-257",
  "title": "Promote Crime Scene Smash and Evidence Locker to active",
  "milestone": "M4",
  "epic": "M4-E",
  "size": "M",
  "depends_on": ["AW-249", "AW-250"],
  "path": "docs/roadmap/tasks/AW-257-promote-crime-scene-smash-and-evidence-locker.md",
  "github": {
    "issue_number": <captured-number>,
    "url": "https://github.com/nickejanssen/arcwright/issues/<captured-number>"
  },
  "epic_id": "M4-E"
}
```

Add similar entries for AW-259 (epic null, depends on AW-257/AW-260/AW-261/AW-254/AW-231), AW-260, AW-261, AW-262..AW-266, AW-267, AW-268. Add the two new epic entries:

```json
{
  "id": "M5-F",
  "milestone": "M5",
  "title": "Tell Me Something True Social Opener Implementation",
  "status": "planned",
  "path": "docs/roadmap/epics/M5-F-tell-me-something-true-social-opener.md",
  "tasks": ["AW-262", "AW-263", "AW-264", "AW-265", "AW-266"],
  "github": {
    "issue_number": <captured-number>,
    "url": "https://github.com/nickejanssen/arcwright/issues/<captured-number>"
  }
}
```

```json
{
  "id": "M5-G",
  "milestone": "M5",
  "title": "Nightcap Visual Identity and Polish",
  "status": "planned",
  "path": "docs/roadmap/epics/M5-G-nightcap-visual-identity-and-polish.md",
  "tasks": ["AW-267", "AW-268"],
  "github": {
    "issue_number": <captured-number>,
    "url": "https://github.com/nickejanssen/arcwright/issues/<captured-number>"
  }
}
```

Also update the M5 milestone entry's `epics` array to include `"M5-F"` and `"M5-G"`.

- [ ] **Step 7: Validate JSON**

```bash
python -m json.tool docs/roadmap/index.json > /dev/null && echo "OK"
```

Expected: `OK`. If JSON is malformed, fix and re-run.

- [ ] **Step 8: Commit**

```bash
git add docs/roadmap/index.json
git commit -m "docs(roadmap): backfill manifest with M4-close and M5-F/M5-G GitHub issue numbers"
```

```json:metadata
{"files": ["docs/roadmap/index.json"], "verifyCommand": "python -m json.tool docs/roadmap/index.json > /dev/null && gh issue list --repo nickejanssen/arcwright --label M4 --state open --limit 20 && gh issue list --repo nickejanssen/arcwright --label M5 --label Epic --state open --limit 10", "acceptanceCriteria": ["13 new GitHub issues exist", "index.json validates", "all 11 task entries have github.issue_number set"], "modelTier": "standard"}
```

---

### Task 2: Repurpose #148 (AW-254) and #84 (AW-231) bodies

**Goal:** Rewrite the bodies of GitHub issues #148 and #84 to their repurposed scope, and update their corresponding `docs/roadmap/tasks/` files to match.

**Files:**
- Modify: `docs/roadmap/tasks/AW-254-first-production-nightcap-mini-game.md`
- Modify: `docs/roadmap/tasks/AW-231-m4-real-human-rehearsal.md`
- GitHub issue body for #148 (via `gh issue edit`)
- GitHub issue body for #84 (via `gh issue edit`)

**Acceptance Criteria:**
- [ ] AW-254 task .md has repurposed scope (verify two promoted games on real devices) preserving all original acceptance criteria PLUS dual-game coverage.
- [ ] AW-231 task .md has repurposed scope (execute Rehearsal 1) preserving all original acceptance criteria PLUS new runbook reference and triage discipline.
- [ ] GitHub issue #148 body matches the updated AW-254 task .md.
- [ ] GitHub issue #84 body matches the updated AW-231 task .md.
- [ ] Both issues link to AW-259 as parent.

**Verify:** `gh issue view 148 --repo nickejanssen/arcwright | head -50 && gh issue view 84 --repo nickejanssen/arcwright | head -50` → both bodies reflect repurposed scope.

**Steps:**

- [ ] **Step 1: Rewrite AW-254 task file**

Overwrite `docs/roadmap/tasks/AW-254-first-production-nightcap-mini-game.md`:

```markdown
# AW-254: Verify Two Promoted Mini-games on Real Devices

**Milestone / Epic:** M4 / M4-E
**Size:** M
**Status:** Planned (repurposed 2026-06-26)
**Parent:** AW-259

## Repurpose Note

This task's scope was rewritten on 2026-06-26 per
`docs/superpowers/specs/2026-06-26-m4-exit-rehearsal-design.md`. Original
scope (promote one founder-selected mini-game) is fulfilled by AW-257. This
task now owns the device-matrix verification of the two production
mini-games AW-257 promotes (Crime Scene Smash + Evidence Locker). Original
acceptance criteria are preserved and extended for dual-game coverage.

## Plain-English Summary

Verify both production Nightcap mini-games end-to-end on the real-device
matrix before the rehearsal session runs.

## Why This Matters

Both games must work on the actual phones / tablets / shared-display
browsers real humans will use, with both clue paths (normal completion +
authored delayed fallback) covered. This is the last gate before AW-231
puts the games in front of real humans.

## Player Impact

Players hit games that have been verified on their device class instead of
games that worked once in a developer's localhost browser.

## Business Value

Catches device-specific bugs before they become rehearsal blockers.

## Technical Scope

- End-to-end run of Crime Scene Smash on the device matrix:
  iOS Safari (latest), Android Chrome (latest), mid-range Android
  (Pixel 5a or equivalent), shared-display browser (1080p Chrome).
- End-to-end run of Evidence Locker on the same matrix.
- Both clue paths verified for each game: normal completion AND authored
  delayed-clue fallback.
- Privacy, reconnect, pause and resume, behavioral output, and
  accessibility verification per the AW-230 matrix.
- Tier 1 polish bar: zero crashes, loading / error / reconnect states
  present on every screen, 60fps target on mid-range Android, basic
  accessibility (color contrast WCAG AA, screen reader landmarks,
  keyboard navigation).

## Acceptance Criteria

- [ ] All AW-230 matrix cells pass for both games.
- [ ] Both clue paths (normal + delayed fallback) verified for both games.
- [ ] Tier 1 polish gates pass: no crashes during verification, every
  screen has loading / error / reconnect, mid-range Android holds 60fps,
  WCAG AA color contrast holds on shared display + player device, screen
  reader landmarks present, keyboard navigation works.
- [ ] Founder demos both games end-to-end on a recorded call.

## Tests/Verification

- Run the AW-230 device matrix for each game.
- Record the founder demo call.
- Capture any failures into AW-260 blocker template format.

## Dependencies

- AW-257 (production packages promoted to active)
- AW-261 (ADR-0003 validation decision recorded so cloud-path ambiguity
  does not contaminate verification scope)
- AW-230 (privacy matrix; complete)
- AW-253 (web mini-game rendering; complete)

## Must Not Do

- Do not activate non-shipping fixtures.
- Do not bypass the AW-202 web runtime contract.
- Do not author new game content (AW-257 owns content).
- Do not add art / animation / sound polish (M5-G scope).

## Architecture References

- `docs/specs/0051-aw-254-first-production-nightcap-mini-game.md` (original
  spec, preserved for reference)
- `docs/specs/0060-aw-230-real-device-privacy-matrix.md`
- `docs/decisions/0009-mini-game-runtime-boundary.md`
- `docs/superpowers/specs/2026-06-26-m4-exit-rehearsal-design.md`

## Playtest Relevance

Last verification gate before AW-231 puts the games in front of real
humans.
```

- [ ] **Step 2: Rewrite AW-231 task file**

Overwrite `docs/roadmap/tasks/AW-231-m4-real-human-rehearsal.md`:

```markdown
# AW-231: Execute Real-Human Nightcap Rehearsal 1

**Milestone / Epic:** M4 / M4-D
**Size:** M
**Status:** Planned (repurposed 2026-06-26)
**Parent:** AW-259

## Repurpose Note

This task's scope was rewritten on 2026-06-26 per
`docs/superpowers/specs/2026-06-26-m4-exit-rehearsal-design.md`. The original
"non-qualifying real-device rehearsal" scope is preserved and extended with
explicit runbook + blocker-triage discipline (AW-260 owns the runbook;
AW-231 executes the rehearsal).

## Plain-English Summary

Run the first real-human Nightcap session using both promoted mini-games,
following the runbook, and triaging every blocker into a new GitHub issue
before closing.

## Why This Matters

This is the M4 exit gate. Real humans on real devices producing real
blockers is the only signal the platform is honest with itself.

## Player Impact

Four-plus humans play Nightcap end-to-end and provide the first ground-truth
data about the experience.

## Business Value

Closes M4. Establishes rehearsal cadence + blocker-triage discipline that
Rehearsal 2 and M6 qualifying sessions inherit. Outputs triaged blockers
that drive M5 hardening priorities.

## Technical Scope

- Run the rehearsal per `docs/roadmap/operations/rehearsal-1-runbook.md`.
- Founder + at least 3 invitees (4-player floor required for Crime Scene
  Smash).
- Record: join timing for every player, privacy results during the
  rehearsal, mini-game completion or fallback for each game, session
  completion state, every blocker (using the AW-260 blocker template).
- After the rehearsal: triage every blocker into a new GitHub issue with a
  milestone assignment (M5 hardening, M5-G polish, M6 ops, or `wontfix`).

## Acceptance Criteria

- [ ] Rehearsal occurred with at least 4 real humans on real devices.
- [ ] All recorded data (join timing, privacy, completion, blockers) is
  saved in the blocker log.
- [ ] Every blocker has a corresponding new GitHub issue with milestone
  assignment.
- [ ] M4 milestone is marked complete in `docs/roadmap/index.json`.

## Tests/Verification

- Rehearsal artifacts (blocker log, session export, recording if any) are
  archived in `docs/roadmap/operations/rehearsal-1-artifacts/`.
- Blocker triage issues exist in GitHub.

## Dependencies

- AW-254 (both games verified on device matrix)
- AW-260 (runbook + blocker template authored)

## Must Not Do

- Do not run with fixtures only.
- Do not bypass the AW-202 web runtime contract.
- Do not bypass the AW-260 runbook (if the runbook is wrong, fix the
  runbook and re-run pre-flight).
- Do not close AW-231 without triaging every blocker.

## Architecture References

- `docs/roadmap/operations/rehearsal-1-runbook.md`
- `docs/roadmap/operations/blocker-log-template.md`
- `docs/decisions/0003-nightcap-web-experience-runtime.md`
- `docs/superpowers/specs/2026-06-26-m4-exit-rehearsal-design.md`

## Playtest Relevance

This rehearsal closes M4. Its blockers drive M5 hardening priorities and
seed Rehearsal 2.
```

- [ ] **Step 3: Edit GitHub issue #148**

```bash
gh issue edit 148 --repo nickejanssen/arcwright \
  --title "AW-254: Verify Two Promoted Mini-games on Real Devices" \
  --body-file docs/roadmap/tasks/AW-254-first-production-nightcap-mini-game.md
```

After the edit, post a comment linking to AW-259 as parent:

```bash
gh issue comment 148 --repo nickejanssen/arcwright --body "Scope repurposed 2026-06-26 per #<AW-259-number> parent. Design doc: \`docs/superpowers/specs/2026-06-26-m4-exit-rehearsal-design.md\`."
```

- [ ] **Step 4: Edit GitHub issue #84**

```bash
gh issue edit 84 --repo nickejanssen/arcwright \
  --title "AW-231: Execute Real-Human Nightcap Rehearsal 1" \
  --body-file docs/roadmap/tasks/AW-231-m4-real-human-rehearsal.md

gh issue comment 84 --repo nickejanssen/arcwright --body "Scope repurposed 2026-06-26 per #<AW-259-number> parent. Design doc: \`docs/superpowers/specs/2026-06-26-m4-exit-rehearsal-design.md\`."
```

- [ ] **Step 5: Commit local changes**

```bash
git add docs/roadmap/tasks/AW-254-first-production-nightcap-mini-game.md docs/roadmap/tasks/AW-231-m4-real-human-rehearsal.md
git commit -m "docs(roadmap): repurpose AW-254 and AW-231 task specs for Rehearsal 1"
```

```json:metadata
{"files": ["docs/roadmap/tasks/AW-254-first-production-nightcap-mini-game.md", "docs/roadmap/tasks/AW-231-m4-real-human-rehearsal.md"], "verifyCommand": "gh issue view 148 --repo nickejanssen/arcwright | head -50 && gh issue view 84 --repo nickejanssen/arcwright | head -50", "acceptanceCriteria": ["both task .md files updated", "both GitHub issue bodies updated", "both issues comment-linked to AW-259"], "modelTier": "standard"}
```

---

### Task 3: AW-261 — Record ADR-0003 Cloudflare vs GCP validation decision

**Goal:** Close the ADR-0003 validation gate by recording the comparison, appending D-067, and filing a follow-on M5 cloud-deploy task.

**Files:**
- Modify: `docs/decisions/0003-nightcap-web-experience-runtime.md` — update Status + add Validation Outcome section.
- Modify: `docs/product/decisions-log.csv` — update the D-067 placeholder row with the real decision.
- Create: `docs/roadmap/tasks/AW-269-nightcap-cloud-deploy.md` — placeholder task for M5 cloud deploy.
- Modify: `docs/roadmap/index.json` — add AW-269 entry.
- GitHub: create AW-269 issue.

**Acceptance Criteria:**
- [ ] ADR-0003 status field updated from "Accepted with validation gate" to "Accepted, validation complete".
- [ ] ADR-0003 has a new "## Validation Outcome (AW-261, 2026-06-26)" section with the comparison + chosen path + rationale.
- [ ] D-067 row in `decisions-log.csv` has real rationale (not the placeholder).
- [ ] AW-269 task .md exists and follows the established roadmap-task format.
- [ ] AW-269 GitHub issue exists with labels `task,size:L,M5` and milestone M5.
- [ ] `docs/roadmap/index.json` has the AW-269 entry with `github.issue_number` set.

**Verify:** `grep -A 2 "Status" docs/decisions/0003-nightcap-web-experience-runtime.md && grep "AW-269" docs/roadmap/index.json && gh issue view <AW-269-number> --repo nickejanssen/arcwright`.

**Steps:**

- [ ] **Step 1: Read ADR-0003 to confirm the current status line**

```bash
head -30 docs/decisions/0003-nightcap-web-experience-runtime.md
```

Identify the existing Status line + the line that mentions the validation gate.

- [ ] **Step 2: Update ADR-0003**

Change the Status line to: `**Status:** Accepted, validation complete (AW-261, 2026-06-26)`.

Append a new section at the end of the ADR:

```markdown

## Validation Outcome (AW-261, 2026-06-26)

ADR-0003 required validating Cloudflare against a GCP-only alternative
(Cloud Run + Firebase + Cloud CDN) before adding Cloudflare-specific
dependencies. This section records that comparison.

### What Cloudflare provides that GCP-only does not

- Workers + Durable Objects: ephemeral room presence with strong
  consistency guarantees at the edge, lower coordination latency than
  Cloud Run cold-starts.
- Pages: static-asset hosting integrated with Workers for routes that
  combine static + dynamic content with no separate CDN config.
- Free / low-cost tier suitable for Arcwright's MVP volume.

### What GCP-only provides that Cloudflare does not

- Single-vendor billing and IAM aligned with the existing engine
  deployment (Cloud Run + Cloud SQL).
- Firebase Auth integration without a cross-provider auth bridge.
- No vendor-lock-in to Workers-specific primitives (Durable Objects do
  not have a clean GCP equivalent).

### What Rehearsal 1 does not tell us

Rehearsal 1 runs on local Docker + cloudflared tunnel per D-065. It does
not exercise either cloud path. The decision below is forward-looking only;
Rehearsal 1's blockers do not feed it.

### Decision criteria for the actual cloud deploy

The cloud deploy will be evaluated against:
1. Per-session cost at the M6 qualifying volume (5 outside groups).
2. Time-to-first-byte for player join under realistic mobile network
   conditions.
3. Operational simplicity for a solo-founder operator.
4. Vendor-lock-in risk for the Layer-2 narrative runtime contract.

### Chosen path

**Stay with Cloudflare** as the canonical Nightcap web-experience runtime,
per ADR-0003. The cost, edge-coordination, and free-tier advantages
outweigh the cross-vendor auth bridging cost. The actual implementation
lives in AW-269 (M5 follow-on).
```

- [ ] **Step 3: Update D-067 row in decisions-log.csv**

Replace the placeholder D-067 row appended in Task 0 with the real outcome:

```csv
ADR-0003 Cloudflare vs GCP validation outcome,"June 26, 2026","Stay with Cloudflare as the canonical Nightcap web-experience runtime. Cost, edge-coordination via Workers + Durable Objects, and free-tier suitability for MVP volume outweigh cross-vendor auth bridging cost. Implementation lives in AW-269.",Section: Architecture,Committed,"roadmap, infrastructure"
```

- [ ] **Step 4: Create AW-269 task file**

Write `docs/roadmap/tasks/AW-269-nightcap-cloud-deploy.md`:

```markdown
# AW-269: Nightcap Cloud Deploy (Cloudflare + GCP backend)

**Milestone / Epic:** M5 / TBD (epic assignment when M5 starts)
**Size:** L
**Status:** Planned

## Plain-English Summary

Deploy the Arcwright engine to Cloud Run + Cloud SQL and the Nightcap web
experience to Cloudflare Pages + Workers + Durable Objects, per ADR-0003
post-validation outcome (D-067).

## Why This Matters

Rehearsal 2 (AW-266) and M6 qualifying sessions need a real cloud target.
Local-tunnel was acceptable for Rehearsal 1 per D-065 but does not scale
beyond founder hosting.

## Player Impact

Sessions run on infrastructure that does not depend on the founder's
laptop being awake.

## Business Value

Unblocks Rehearsal 2 and all M6 qualifying-session work.

## Technical Scope

- Provision Cloud Run service for Arcwright engine FastAPI app.
- Provision Cloud SQL Postgres 15 instance with pgvector extension.
- Provision Firebase Auth project.
- Provision Cloudflare Pages project for the web app.
- Provision Cloudflare Workers + Durable Objects for room coordination.
- Wire DNS + custom domain.
- Configure CI/CD for both deploy targets.
- Document the deploy runbook.

## Acceptance Criteria

- [ ] Engine reachable at a stable Cloud Run URL.
- [ ] Web app reachable at a stable Cloudflare Pages URL.
- [ ] A test session created via the web app reaches the engine and
  returns events.
- [ ] Cost monitoring alerts configured.
- [ ] Deploy runbook lives at `docs/roadmap/operations/cloud-deploy-runbook.md`.

## Tests/Verification

- End-to-end smoke test: create session, join from a real phone, complete
  one mini-game, close session.

## Dependencies

- AW-261 (validation decision recorded)
- AW-259 (Rehearsal 1 complete; blockers triaged so deploy work does not
  fight against unstable code)

## Must Not Do

- Do not hardcode secrets.
- Do not skip auth setup.
- Do not couple this deploy to a single Nightcap mini-game.

## Architecture References

- `docs/decisions/0003-nightcap-web-experience-runtime.md`
- `docs/architecture/02-technology-stack.md`
- `docs/roadmap/epics/M4-A-nightcap-external-platform-integration.md`

## Playtest Relevance

Hosts Rehearsal 2 and all M6 qualifying sessions.
```

- [ ] **Step 5: Add AW-269 to manifest**

Append to `docs/roadmap/index.json` `tasks[]`:

```json
{
  "id": "AW-269",
  "title": "Nightcap Cloud Deploy (Cloudflare + GCP backend)",
  "milestone": "M5",
  "epic": null,
  "size": "L",
  "depends_on": ["AW-261", "AW-259"],
  "path": "docs/roadmap/tasks/AW-269-nightcap-cloud-deploy.md",
  "github": {
    "issue_number": <captured-number-from-step-6>,
    "url": "https://github.com/nickejanssen/arcwright/issues/<captured-number>"
  },
  "epic_id": null
}
```

- [ ] **Step 6: Create AW-269 GitHub issue**

```bash
gh issue create --repo nickejanssen/arcwright \
  --title "AW-269: Nightcap Cloud Deploy (Cloudflare + GCP backend)" \
  --label "task,size:L,M5" \
  --milestone "M5: Hardening + Proof Prerequisites" \
  --body-file docs/roadmap/tasks/AW-269-nightcap-cloud-deploy.md
```

Capture the issue number and backfill it into the manifest entry from Step 5.

- [ ] **Step 7: Validate JSON**

```bash
python -m json.tool docs/roadmap/index.json > /dev/null && echo "OK"
```

- [ ] **Step 8: Commit and open PR**

```bash
git checkout -b feature/aw-261-adr-0003-validation
git add docs/decisions/0003-nightcap-web-experience-runtime.md docs/product/decisions-log.csv docs/roadmap/tasks/AW-269-nightcap-cloud-deploy.md docs/roadmap/index.json
git commit -m "docs(adr): close ADR-0003 validation gate; choose Cloudflare; file AW-269 deploy task"
git push -u origin feature/aw-261-adr-0003-validation
gh pr create --title "AW-261: Close ADR-0003 Cloudflare vs GCP validation gate" \
  --body "Closes AW-261. Records D-067. Files AW-269 (#<AW-269-number>) as the M5 cloud-deploy task." \
  --base main
```

```json:metadata
{"files": ["docs/decisions/0003-nightcap-web-experience-runtime.md", "docs/product/decisions-log.csv", "docs/roadmap/tasks/AW-269-nightcap-cloud-deploy.md", "docs/roadmap/index.json"], "verifyCommand": "grep -E 'Status.*Accepted, validation complete' docs/decisions/0003-nightcap-web-experience-runtime.md && grep AW-269 docs/roadmap/index.json && python -m json.tool docs/roadmap/index.json > /dev/null", "acceptanceCriteria": ["ADR-0003 status updated", "D-067 row updated with real outcome", "AW-269 task .md created", "AW-269 GitHub issue created", "manifest backfilled"], "modelTier": "standard"}
```

---

### Task 4: AW-257 — Promote Crime Scene Smash and Evidence Locker to active

**USER-ORDERED GATE — NON-SKIPPABLE.** This task was requested by the user in the current conversation. It MUST NOT be closed by walking around it, by declaring it "verified inline", or by substituting a cheaper check. Close only after every item in `acceptanceCriteria` has been re-validated independently, with output captured.

**Goal:** Fill the Crime Scene Smash copy placeholders, run AW-250 safety review on both games, promote both manifests to `lifecycle: active`, and bind both into `nightcap/arc.json` at founder-chosen beats.

**Files:**
- Modify: `nightcap/mini_games/crime-scene-smash/definitions/0.1.0.json` — replace 5 copy placeholders.
- Modify: `nightcap/mini_games/crime-scene-smash/manifest.json` — lifecycle `draft` → `active`.
- Modify: `nightcap/mini_games/evidence-locker-402/manifest.json` — lifecycle `playtest` → `active`.
- Modify: `nightcap/arc.json` — bind both packages at founder-chosen beat positions.
- Modify: `docs/product/decisions-log.csv` — update D-062 row to also name Evidence Locker.

**Acceptance Criteria:**
- [ ] Crime Scene Smash JSON has no `[final authored copy needed]` strings.
- [ ] Both packages validate against the AW-249 schema and loader via the existing test command.
- [ ] Both packages pass AW-250 safety review (run the existing safety-review tooling on each).
- [ ] **Founder signs off on Crime Scene Smash copy in a PR comment before merge** (this is the user-gate condition; PR cannot merge without explicit "approved" comment from `nickejanssen`).
- [ ] Both manifests at `lifecycle: active`.
- [ ] Both packages referenced in `nightcap/arc.json`.
- [ ] D-062 decision-log row updated to name Evidence Locker alongside Crime Scene Smash.

**Verify:** `python -m engine.mini_games.validator nightcap/mini_games/crime-scene-smash nightcap/mini_games/evidence-locker-402 && python -c "import json; m1=json.load(open('nightcap/mini_games/crime-scene-smash/manifest.json')); m2=json.load(open('nightcap/mini_games/evidence-locker-402/manifest.json')); assert m1['lifecycle']=='active' and m2['lifecycle']=='active'; print('OK')" && grep -L "final authored copy needed" nightcap/mini_games/crime-scene-smash/definitions/0.1.0.json`. (If a specific validator entry point differs from the example, run the project's actual mini-game schema validator — see `docs/specs/0046-aw-249-nightcap-mini-game-authoring-foundation.md` for the canonical command.)

**Steps:**

- [ ] **Step 1: Draft Crime Scene Smash copy**

Read `nightcap/mini_games/crime-scene-smash/definitions/0.1.0.json` and identify the 5 `[final authored copy needed]` placeholders inside `authored_content.copy_needed`:
- `narrator_intro`
- `success_line`
- `fallback_line`
- `tie_line`
- `leaderboard_callouts`

Read `docs/story-bibles/nightcap-murder-mystery.md` for tonal guardrails (Nightcap-safe, party-game energy, narrator-driven, no fourth-wall breaks beyond the diegetic frame).

Draft copy that fits the Crime Scene Smash mechanic (match-3 race for investigative leads). Draft directly into the JSON file, replacing each placeholder string. Example shape for `narrator_intro`:

```
"narrator_intro": "The crime scene's still warm. Match the evidence fast. Whoever sorts the leads first decides what the room hears next."
```

Apply similar tone for the other four. Use plain language, no em dashes, no ellipses, no emoji.

- [ ] **Step 2: Run schema validation**

```bash
python -m engine.mini_games.validator nightcap/mini_games/crime-scene-smash
```

Expected: PASS. If validation fails, fix and re-run. If the validator entry point differs in the actual codebase, locate it via `grep -r "def validate" engine/mini_games/ | head -5` and use the actual command.

- [ ] **Step 3: Run AW-250 safety review on Crime Scene Smash**

Locate the safety review entry point: `grep -r "safety_review\|content_safety_review" engine/mini_games/ engine/safety/ | head -5` and run it on the package.

Expected: PASS, with no L1/L2 hits on the new copy.

If any L1/L2 flag triggers, rewrite the offending line and re-run.

- [ ] **Step 4: Run schema + safety review on Evidence Locker**

```bash
python -m engine.mini_games.validator nightcap/mini_games/evidence-locker-402
# run safety review on evidence-locker-402 via the located entry point
```

Expected: both PASS. Evidence Locker copy is already complete so this should be clean.

- [ ] **Step 5: Get founder sign-off on Crime Scene Smash copy**

Open a PR with the JSON copy changes only (do NOT promote lifecycle yet). Ping the founder in the PR description:

```
Crime Scene Smash copy ready for sign-off. Please review the 5 new strings in
nightcap/mini_games/crime-scene-smash/definitions/0.1.0.json authored_content
section and comment "approved" or request changes. AW-257 cannot proceed past
this gate without explicit approval.
```

**USER-GATE: Wait for explicit "approved" comment from `nickejanssen` before continuing.** Do not promote lifecycle in this PR. Do not merge speculatively.

- [ ] **Step 6: After approval — promote lifecycles**

Modify `nightcap/mini_games/crime-scene-smash/manifest.json`:
```json
"lifecycle": "active"
```

Modify `nightcap/mini_games/evidence-locker-402/manifest.json`:
```json
"lifecycle": "active"
```

- [ ] **Step 7: Bind both packages into `nightcap/arc.json`**

Read `nightcap/arc.json` to understand the beat structure and existing mini-game binding pattern.

Ask the founder (in the same PR thread) which beat positions to bind each game at. Wait for explicit beat IDs.

Add the bindings under the relevant beat entries. Example shape (actual schema TBD by inspection of `nightcap/arc.json`):

```json
{
  "beat_id": "<founder-chosen-beat-for-CSS>",
  "mini_game_ref": "crime-scene-smash"
}
```

```json
{
  "beat_id": "<founder-chosen-beat-for-EL>",
  "mini_game_ref": "evidence-locker-402"
}
```

- [ ] **Step 8: Update D-062 decision-log row**

Locate the D-062 row in `docs/product/decisions-log.csv`. Append " and Evidence Locker" to the decision text where it currently names only Crime Scene Smash, and append a sentence to the rationale: " Evidence Locker added to approved production set 2026-06-26 per D-064 two-rehearsal sequence."

- [ ] **Step 9: Run engine tests**

```bash
pytest engine/tests/ -k "mini_game or arc" -v
```

Expected: PASS. If any test fails, fix and re-run before merging.

- [ ] **Step 10: Commit and merge**

```bash
git add nightcap/mini_games/crime-scene-smash/manifest.json nightcap/mini_games/evidence-locker-402/manifest.json nightcap/arc.json docs/product/decisions-log.csv
git commit -m "feat(nightcap): promote Crime Scene Smash and Evidence Locker to active (AW-257)"
git push
gh pr merge --squash --auto
```

```json:metadata
{"files": ["nightcap/mini_games/crime-scene-smash/definitions/0.1.0.json", "nightcap/mini_games/crime-scene-smash/manifest.json", "nightcap/mini_games/evidence-locker-402/manifest.json", "nightcap/arc.json", "docs/product/decisions-log.csv"], "verifyCommand": "python -c \"import json; m1=json.load(open('nightcap/mini_games/crime-scene-smash/manifest.json')); m2=json.load(open('nightcap/mini_games/evidence-locker-402/manifest.json')); assert m1['lifecycle']=='active' and m2['lifecycle']=='active'; print('OK')\" && grep -L 'final authored copy needed' nightcap/mini_games/crime-scene-smash/definitions/0.1.0.json && pytest engine/tests/ -k 'mini_game or arc' -v", "acceptanceCriteria": ["Crime Scene Smash copy placeholders replaced and founder-approved", "both packages validate against schema", "both packages pass safety review", "both manifests at lifecycle active", "both packages bound in nightcap/arc.json at founder-chosen beats", "D-062 updated to include Evidence Locker"], "userGate": true, "tags": ["user-gate"], "modelTier": "standard"}
```

---

### Task 5: AW-260 — Author Rehearsal 1 Runbook + Blocker Log + Failure Cheat Sheet

**USER-ORDERED GATE — NON-SKIPPABLE.** This task was requested by the user in the current conversation. It MUST NOT be closed by walking around it, by declaring it "verified inline", or by substituting a cheaper check. Close only after every item in `acceptanceCriteria` has been re-validated independently, with output captured.

**Goal:** Author three operational docs (runbook, blocker template, failure cheat sheet) and validate them with a founder walkthrough + fabricated-blocker dry-run.

**Files:**
- Create: `docs/roadmap/operations/rehearsal-1-runbook.md`
- Create: `docs/roadmap/operations/blocker-log-template.md`
- Create: `docs/roadmap/operations/rehearsal-1-failure-cheat-sheet.md`

**Acceptance Criteria:**
- [ ] Runbook covers all four phases (pre-flight, setup, in-session, wrap).
- [ ] Blocker template has the 8 fields specified in the design doc.
- [ ] Failure cheat sheet covers at least 5 failure modes with concrete recovery steps.
- [ ] **Founder walkthrough on call: founder reads the runbook cold and executes every step without questions; comments "walkthrough passed" in the PR thread.**
- [ ] **Fabricated-blocker dry-run: one fabricated blocker entry filled into the template end-to-end; founder confirms it captures everything needed in PR thread.**

**Verify:** `wc -l docs/roadmap/operations/rehearsal-1-runbook.md docs/roadmap/operations/blocker-log-template.md docs/roadmap/operations/rehearsal-1-failure-cheat-sheet.md && grep -c "^##" docs/roadmap/operations/rehearsal-1-failure-cheat-sheet.md` → all three files non-empty; cheat sheet has at least 5 H2 sections.

**Steps:**

- [ ] **Step 1: Author the runbook**

Write `docs/roadmap/operations/rehearsal-1-runbook.md`:

```markdown
# Rehearsal 1 — Founder Runbook

> Status: Active
> Last updated: 2026-06-26
> For: First real-human Nightcap session (M4 exit)
> Owner: Founder

## 0. Before the day

- Confirm Crime Scene Smash and Evidence Locker are at `lifecycle: active` in their manifests.
- Confirm both packages are bound in `nightcap/arc.json`.
- Confirm engine tests pass: `pytest engine/tests/ -k "mini_game or arc" -v`.
- Confirm Docker Desktop is running.
- Confirm Anthropic API key + Groq API key are in `.env` at repo root.
- Confirm at least 3 invitees have RSVPed (you + 3 = 4-player floor for Crime Scene Smash).
- Send invitees: "Bring a phone (iOS or Android), be on the same Wi-Fi or use the join URL I'll send."

## 1. Pre-flight (30 minutes before)

1. Open a terminal at the repo root.
2. Start Postgres + engine via Docker:
   ```bash
   docker compose up -d
   ```
   Wait until both services are healthy: `docker compose ps` shows both `running (healthy)`.
3. Apply migrations:
   ```bash
   alembic upgrade head
   ```
   Expected: "Running upgrade ..." lines, then no error.
4. Verify engine is reachable:
   ```bash
   curl -s http://localhost:8000/health | jq .
   ```
   Expected: `{"status": "ok"}`.
5. Start the Nightcap web app locally:
   ```bash
   cd web && npm run dev
   ```
   Note the local port (default 5173). Leave running.
6. Start the cloudflared quick-tunnel:
   ```bash
   cloudflared tunnel --url http://localhost:5173
   ```
   Note the printed `https://<random>.trycloudflare.com` URL. **This is the join URL for players.**
7. Open the shared display browser (the device that will show the group view). Navigate to:
   `https://<random>.trycloudflare.com/host`
   Sign in as host (use your existing Firebase test account or follow the auth flow shown).

## 2. Session setup (5 minutes before players arrive)

1. On the shared display, create a new session. Pick the arc: Nightcap. Set the diegetic frame (High Society / Corporate / Sci-Fi).
2. The shared display will show a 6-character join code.
3. Send to players: "Open `https://<random>.trycloudflare.com` and enter join code `XXXXXX`."
4. As each player joins, confirm their name appears on the shared display lobby.
5. Wait until at least 4 players are in the lobby.
6. Start the session.

## 3. In-session checks

Run these checks at the moments listed. Note any failure in the blocker log.

| Checkpoint | What to look for | If wrong |
|---|---|---|
| Player join | Each player's join time under 30 seconds | Log P1 blocker, continue |
| Private event | Each player sees their own role / clue on their device, NOT on shared display | Log P0 blocker, STOP the session |
| Crime Scene Smash launch | All 4+ players see the match-3 board simultaneously; shared display shows leaderboard | Log P1 blocker, continue if board is usable |
| Crime Scene Smash completion | Highest score gets the lead clue; runner-up gets nothing | Log P1 blocker, fall back to host-narrated clue |
| Evidence Locker launch | The current solo player sees the pin-lock interface | Log P1 blocker, fall back to host-narrated clue |
| Evidence Locker completion | On success: solo player gets clue; on failure: fallback clue auto-delivered | Log P1 blocker if neither path fires |
| Accusation | Every player can submit a vote on the killer | Log P0 if voting is broken |
| Reveal | Killer identity shown on shared display; not earlier | Log P0 if revealed early |

## 4. Wrap

1. After the killer reveal, ask players for spoken feedback. Take notes.
2. Export the session log:
   ```bash
   curl -s "http://localhost:8000/api/sessions/<session-id>/export" -H "Authorization: Bearer <host-token>" > docs/roadmap/operations/rehearsal-1-artifacts/session-<YYYYMMDD>.json
   ```
3. Tear down:
   ```bash
   docker compose down
   ```
   Stop the cloudflared tunnel (Ctrl+C).
   Stop the web dev server (Ctrl+C).
4. Save the blocker log + session export to `docs/roadmap/operations/rehearsal-1-artifacts/`.
5. Open AW-231 GitHub issue and post a comment with: number of players, number of blockers by severity, link to artifacts.
6. Triage every blocker into a new GitHub issue (next step in AW-231).

## See also

- `docs/roadmap/operations/blocker-log-template.md`
- `docs/roadmap/operations/rehearsal-1-failure-cheat-sheet.md`
```

- [ ] **Step 2: Author the blocker template**

Write `docs/roadmap/operations/blocker-log-template.md`:

```markdown
# Blocker Log Template — Rehearsal 1

Copy this template into a file at
`docs/roadmap/operations/rehearsal-1-artifacts/blockers-<YYYYMMDD>.md` during
the rehearsal. Add one entry per blocker observed.

## Entry schema

Each blocker is one section using the schema below. Fill every field.

```
### Blocker NN

- Timestamp: HH:MM:SS local
- Player count at incident: N
- Device + OS: e.g. "Pixel 5a, Android 14, Chrome 126"
- What happened: 1-2 sentence factual description
- What you expected: 1-2 sentence description of the expected behavior
- Severity:
  - P0 = crash, data loss, privacy leak, session ended early
  - P1 = broken UX (player blocked from continuing), wrong-path completion
  - P2 = polish (looks bad, slow, small wording issue)
- Repro steps:
  1. Step 1
  2. Step 2
- Screenshot or video link: (paste image, link to local file, or "N/A")
- Triage destination: (filled after the session — M5 hardening, M5-G polish, M6 ops, or wontfix)
- New issue link: (filled after triage)
```

## Example entry (fabricated, for template validation)

### Blocker 01

- Timestamp: 19:42:17 local
- Player count at incident: 4
- Device + OS: iPhone 12, iOS 17.5, Safari
- What happened: After submitting my Crime Scene Smash final score, the
  "Awaiting other players" screen got stuck for 8 seconds before the
  leaderboard appeared on the shared display.
- What you expected: Leaderboard appears within 2 seconds of last submission.
- Severity: P1
- Repro steps:
  1. Complete Crime Scene Smash on iPhone Safari.
  2. Wait for other players to finish.
  3. Observe delay before shared-display leaderboard renders.
- Screenshot or video link: rehearsal-1-artifacts/blocker-01-screen-recording.mp4
- Triage destination: M5 hardening
- New issue link: <filled after triage>
```

- [ ] **Step 3: Author the failure cheat sheet**

Write `docs/roadmap/operations/rehearsal-1-failure-cheat-sheet.md`:

```markdown
# Rehearsal 1 — Failure Cheat Sheet

When something breaks mid-session, find the closest match below and do the
named recovery. Log a blocker afterward.

## Player disconnect

The player's tile goes gray on the shared display.

- If the disconnected player is mid-mini-game: their slot times out; the
  game falls back to the authored clue path. The session continues without
  them.
- If they reconnect: the SDK auto-resumes them at the current beat. They
  rejoin in time for the next moment.
- If they cannot reconnect: continue. The accusation phase still works
  with the players who are present.

## Mini-game timeout (no completion within duration)

The shared display shows "Time's up" then the fallback clue.

- Confirm the fallback clue text appears for every player who needs it.
- If the fallback does NOT appear: the host narrates the reduced clue
  verbally. Log a P0 blocker.

## Shared display freeze

The shared display stops updating but player devices keep working.

- Refresh the shared display browser. The session state is server-side; it
  rejoins at the current beat.
- If refresh does not recover: continue using player devices only. Host
  narrates from a player device temporarily.

## Narrator silent (no shared-display narrator text appears)

The shared display shows the layout but the narrator text area is empty.

- Wait 10 seconds. Some narrator generations take that long.
- If still empty: the host reads a generic version of the current beat
  ("The room is quiet. Someone has to speak first.") and continues. Log
  P1.

## Tunnel dropped

Players can no longer reach the join URL.

- Restart cloudflared in the terminal: `cloudflared tunnel --url http://localhost:5173`.
- Note the new `*.trycloudflare.com` URL.
- Send the new URL to players in your group chat.
- Players reload. The session state is preserved.

## Engine crash

The Docker engine container exits.

- Check: `docker compose ps`.
- Restart: `docker compose up -d`.
- Apply any pending migrations: `alembic upgrade head`.
- The session likely needs to be restarted from the most recent snapshot.
  Players will need to rejoin. This is a P0 blocker.
```

- [ ] **Step 4: Founder walkthrough**

Open a PR with the three new docs. Schedule a 15-minute call with the founder. On the call:

1. Founder reads the runbook section by section, cold (no live narration from the executing chat).
2. At each step that requires action, the founder asks "what do I do here?" — if the runbook does not answer it, the runbook is wrong; mark the section for revision.
3. Founder posts "walkthrough passed" or "needs revision" in the PR thread.

**USER-GATE: Do not merge until founder posts "walkthrough passed".**

- [ ] **Step 5: Fabricated-blocker dry-run**

In the same PR thread, the founder fills the example blocker entry from the template using a fabricated scenario the executing chat invents. The founder reports whether the template captures everything needed; if not, add the missing field and re-run.

**USER-GATE: Do not merge until founder posts "blocker template confirmed".**

- [ ] **Step 6: Commit and merge**

```bash
git checkout -b feature/aw-260-rehearsal-runbook
git add docs/roadmap/operations/rehearsal-1-runbook.md docs/roadmap/operations/blocker-log-template.md docs/roadmap/operations/rehearsal-1-failure-cheat-sheet.md
git commit -m "docs(operations): Rehearsal 1 runbook, blocker template, failure cheat sheet (AW-260)"
git push -u origin feature/aw-260-rehearsal-runbook
gh pr create --title "AW-260: Rehearsal 1 runbook + blocker template + failure cheat sheet" \
  --body "Closes AW-260. Founder walkthrough + fabricated-blocker dry-run passed." \
  --base main
gh pr merge --squash --auto
```

```json:metadata
{"files": ["docs/roadmap/operations/rehearsal-1-runbook.md", "docs/roadmap/operations/blocker-log-template.md", "docs/roadmap/operations/rehearsal-1-failure-cheat-sheet.md"], "verifyCommand": "wc -l docs/roadmap/operations/rehearsal-1-runbook.md docs/roadmap/operations/blocker-log-template.md docs/roadmap/operations/rehearsal-1-failure-cheat-sheet.md && grep -c '^## ' docs/roadmap/operations/rehearsal-1-failure-cheat-sheet.md", "acceptanceCriteria": ["runbook covers pre-flight, setup, in-session, wrap", "blocker template has 8 fields", "cheat sheet covers at least 5 failure modes", "founder walkthrough passed (PR comment)", "fabricated blocker dry-run passed (PR comment)"], "userGate": true, "tags": ["user-gate"], "modelTier": "standard"}
```

---

### Task 6: AW-254 — Verify both promoted mini-games on real-device matrix

**USER-ORDERED GATE — NON-SKIPPABLE.** This task was requested by the user in the current conversation. It MUST NOT be closed by walking around it, by declaring it "verified inline", or by substituting a cheaper check. Close only after every item in `acceptanceCriteria` has been re-validated independently, with output captured.

**Goal:** Run the AW-230 device matrix against both Crime Scene Smash and Evidence Locker, verify both clue paths for each, hit the Tier 1 polish bar, and capture a founder demo-call recording.

**Files:**
- Create: `docs/roadmap/operations/aw-254-verification-results.md` — matrix results, polish-gate results, recording link.

**Acceptance Criteria:**
- [ ] AW-230 matrix passes for Crime Scene Smash on iOS Safari, Android Chrome, mid-range Android, shared-display browser.
- [ ] AW-230 matrix passes for Evidence Locker on the same four cells.
- [ ] Normal completion path verified for both games on at least one device each.
- [ ] Authored delayed-clue fallback path verified for both games (force a timeout) on at least one device each.
- [ ] Tier 1 polish gates pass: no crashes during verification, every screen has loading / error / reconnect states, mid-range Android holds 60fps during the busiest mini-game frame (Crime Scene Smash board with all 4 boards rendering), WCAG AA color contrast holds on shared display + player device, screen reader landmarks present, keyboard navigation works.
- [ ] **Founder demos both games end-to-end on a recorded call. Recording archived under `docs/roadmap/operations/rehearsal-1-artifacts/aw-254-founder-demo.mp4` (or `.link` file pointing to cloud storage).**

**Verify:** `cat docs/roadmap/operations/aw-254-verification-results.md` → shows all matrix cells PASS, both clue paths verified for both games, Tier 1 polish gates checked, recording link present.

**Steps:**

- [ ] **Step 1: Set up the device matrix**

Locate the AW-230 privacy matrix doc: `docs/specs/0060-aw-230-real-device-privacy-matrix.md`. Read the matrix to understand what each cell tests.

Confirm the four target devices are available:
- iPhone with iOS Safari (latest).
- Android phone with Chrome (latest).
- Mid-range Android (Pixel 5a or equivalent).
- Desktop browser representing the shared display (1080p+ Chrome).

If any device class is missing, note it as a verification gap; do not proceed with that cell.

- [ ] **Step 2: Run the matrix for Crime Scene Smash**

Start the engine locally (per AW-260 runbook pre-flight Steps 1-4). Start the web app + cloudflared tunnel (per AW-260 Steps 5-6).

For each device cell:
1. Join a test session.
2. Trigger Crime Scene Smash.
3. Complete the game (normal path).
4. Verify: no privacy leak, no crash, 60fps on the mid-range Android cell.
5. Note PASS or FAIL with details.

Repeat with a forced timeout to verify the authored delayed-clue fallback fires correctly.

- [ ] **Step 3: Run the matrix for Evidence Locker**

Same procedure as Step 2, for Evidence Locker. Solo mechanic means only one device is in-game at a time; cycle through each device class.

- [ ] **Step 4: Run Tier 1 polish gates**

For each device:
- Crash check: complete each game without any uncaught exception (check browser console + engine logs).
- State coverage: spot-check each screen renders a loading state on slow network (use Chrome devtools network throttling = "Slow 3G"), an error state on backend failure (kill the engine container briefly), a reconnect state on WebSocket / SSE drop.
- Performance: open Chrome devtools Performance tab on the mid-range Android. Record during the Crime Scene Smash board phase. Confirm sustained 60fps (frames consistently 16ms or under).
- Accessibility:
  - Run axe DevTools on the shared display + player device URLs. Confirm no Critical or Serious issues.
  - Verify color contrast against WCAG AA: foreground text on background ≥ 4.5:1 for normal text, 3:1 for large text.
  - Tab through every interactive element with keyboard; confirm focus indicators visible.

- [ ] **Step 5: Founder demo call**

Schedule a founder call. Founder shares screen via the shared display browser and demos both games end-to-end, one normal-completion run + one timeout run for each. Recording captured (via Zoom / Loom / similar).

Archive the recording at `docs/roadmap/operations/rehearsal-1-artifacts/aw-254-founder-demo.mp4` (or commit a `.link` file with the cloud URL if file size is large).

**USER-GATE: Do not close AW-254 without the recording archived and the founder posting "verification complete" in the PR thread.**

- [ ] **Step 6: Write verification results doc**

Create `docs/roadmap/operations/aw-254-verification-results.md`:

```markdown
# AW-254 Verification Results

> Verified: <YYYY-MM-DD>
> Verified by: <founder + executing chat>
> Recording: docs/roadmap/operations/rehearsal-1-artifacts/aw-254-founder-demo.mp4

## Device matrix results

| Device | Crime Scene Smash | Evidence Locker |
|---|---|---|
| iPhone (iOS Safari latest) | PASS / FAIL with notes | PASS / FAIL with notes |
| Android Chrome (latest) | PASS / FAIL with notes | PASS / FAIL with notes |
| Mid-range Android (Pixel 5a) | PASS / FAIL with notes | PASS / FAIL with notes |
| Shared display browser (1080p Chrome) | PASS / FAIL with notes | PASS / FAIL with notes |

## Clue path coverage

| Game | Normal completion | Delayed fallback |
|---|---|---|
| Crime Scene Smash | PASS / FAIL (device used) | PASS / FAIL (device used) |
| Evidence Locker | PASS / FAIL (device used) | PASS / FAIL (device used) |

## Tier 1 polish gates

| Gate | Result | Notes |
|---|---|---|
| Zero crashes during verification | PASS / FAIL | ... |
| All screens have loading / error / reconnect states | PASS / FAIL | ... |
| 60fps on mid-range Android (CSS board phase) | PASS / FAIL | average frame time |
| WCAG AA color contrast (shared + player) | PASS / FAIL | axe results |
| Screen reader landmarks present | PASS / FAIL | ... |
| Keyboard navigation works | PASS / FAIL | ... |

## Blockers found during verification

(List each, with severity + new issue link.)
```

Fill every cell with real results.

- [ ] **Step 7: Commit results doc**

```bash
git checkout -b feature/aw-254-verification
git add docs/roadmap/operations/aw-254-verification-results.md docs/roadmap/operations/rehearsal-1-artifacts/aw-254-founder-demo.mp4
# If the recording is too large to commit, commit a .link file instead.
git commit -m "docs(verification): AW-254 device-matrix and Tier 1 polish results"
git push -u origin feature/aw-254-verification
gh pr create --title "AW-254: Verify both promoted mini-games on real-device matrix" \
  --body "Closes AW-254. All matrix cells + Tier 1 polish gates verified. Founder demo recording archived." \
  --base main
gh pr merge --squash --auto
```

```json:metadata
{"files": ["docs/roadmap/operations/aw-254-verification-results.md", "docs/roadmap/operations/rehearsal-1-artifacts/aw-254-founder-demo.mp4"], "verifyCommand": "cat docs/roadmap/operations/aw-254-verification-results.md", "acceptanceCriteria": ["AW-230 matrix passes for both games on all four cells", "both clue paths verified for both games", "Tier 1 polish gates passed", "founder demo recording archived", "founder posted 'verification complete' in PR thread"], "userGate": true, "tags": ["user-gate"], "requireEvidenceTokens": [["Crime Scene Smash", "CSS"], ["Evidence Locker", "EL"]], "modelTier": "standard"}
```

---

### Task 7: AW-231 — Execute Real-Human Nightcap Rehearsal 1

**USER-ORDERED GATE — NON-SKIPPABLE.** This task was requested by the user in the current conversation. It MUST NOT be closed by walking around it, by declaring it "verified inline", or by substituting a cheaper check. Close only after every item in `acceptanceCriteria` has been re-validated independently, with output captured.

**Goal:** The founder runs the actual rehearsal with at least 3 invitees following the AW-260 runbook. The executing chat is a coordinator + scribe for this task — it does not "complete" the rehearsal, the founder does. The executing chat captures the blockers and triages them into new GitHub issues.

**Files:**
- Create: `docs/roadmap/operations/rehearsal-1-artifacts/blockers-<YYYYMMDD>.md` (filled during the rehearsal, per AW-260 template)
- Create: `docs/roadmap/operations/rehearsal-1-artifacts/session-<YYYYMMDD>.json` (exported session log, per AW-260 wrap step)
- Create: zero or more new GitHub issues for triaged blockers.
- Modify: `docs/roadmap/index.json` — set M4 milestone `status` to `"complete"` (only after every blocker is triaged).

**Acceptance Criteria:**
- [ ] Rehearsal occurred with founder + at least 3 invitees on real devices.
- [ ] Blocker log file exists with one entry per observed blocker (or one entry stating "no blockers observed" if applicable).
- [ ] Session export JSON archived.
- [ ] Every blocker entry has a corresponding new GitHub issue created with appropriate milestone label (M5 hardening, M5-G polish, M6 ops, or `wontfix`).
- [ ] Every blocker entry's `New issue link` field is filled.
- [ ] M4 milestone status set to `complete` in manifest.

**Verify:** `ls docs/roadmap/operations/rehearsal-1-artifacts/ && grep -c "^### Blocker" docs/roadmap/operations/rehearsal-1-artifacts/blockers-*.md && jq '.milestones[] | select(.id=="M4") | .status' docs/roadmap/index.json`.

**Steps:**

- [ ] **Step 1: Schedule the rehearsal**

The founder schedules the date + time with invitees. Communicate to the executing chat when it is happening so the chat can be available for blocker-capture support during + after.

- [ ] **Step 2: Pre-flight**

Founder follows AW-260 runbook Section 1 (Pre-flight). If any step fails, do not start the rehearsal — fix and re-run pre-flight.

- [ ] **Step 3: Run the session**

Founder follows AW-260 runbook Sections 2-3 (Session setup + In-session checks). Founder fills the blocker log during the session using the AW-260 template, saving it as `docs/roadmap/operations/rehearsal-1-artifacts/blockers-<YYYYMMDD>.md` (use today's date in `YYYYMMDD` format).

**USER-GATE: This step is performed by the founder + invitees in real time. The executing chat does not "complete" this step — the founder does.**

- [ ] **Step 4: Wrap**

Founder follows AW-260 runbook Section 4 (Wrap). Session export + blocker log committed to `docs/roadmap/operations/rehearsal-1-artifacts/`.

- [ ] **Step 5: Triage blockers**

Executing chat reads the blocker log file. For each blocker entry:
1. Decide milestone: M5 (engine / runtime hardening), M5-G (polish), M6 (operations / runbook gap), or `wontfix` (intentional out-of-scope).
2. Create a new GitHub issue:
   ```bash
   gh issue create --repo nickejanssen/arcwright \
     --title "<short description from blocker entry>" \
     --label "task,size:S,<milestone-label>" \
     --milestone "<milestone-name>" \
     --body "Found in Rehearsal 1 (AW-231). Severity: <P0/P1/P2>. <full blocker entry from log>."
   ```
3. Edit the blocker log entry to fill `New issue link` field with the URL.

If any blocker is `wontfix`, document the rationale in the blocker log entry itself; do not create a GitHub issue for it.

- [ ] **Step 6: Mark M4 complete**

In `docs/roadmap/index.json`, find the M4 milestone entry. Change `"status": "planned"` to `"status": "complete"`.

In the M4 epic entries (M4-A, M4-B, M4-C, M4-D, M4-E), change `"status"` to `"complete"` for any whose child tasks are all closed.

- [ ] **Step 7: Commit and close**

```bash
git checkout -b feature/aw-231-rehearsal-1
git add docs/roadmap/operations/rehearsal-1-artifacts/ docs/roadmap/index.json
git commit -m "feat(rehearsal): execute Rehearsal 1, triage blockers, close M4 (AW-231)"
git push -u origin feature/aw-231-rehearsal-1
gh pr create --title "AW-231: Execute Rehearsal 1 and close M4" \
  --body "Closes AW-231 and AW-259. M4 complete. <N> blockers triaged into follow-up issues: <list URLs>." \
  --base main
gh pr merge --squash --auto

gh issue close <AW-231-number> --comment "Rehearsal 1 complete. Blockers triaged into follow-up issues. M4 closed."
gh issue close <AW-259-number> --comment "M4 exit gate met. All sub-issues closed."
```

```json:metadata
{"files": ["docs/roadmap/operations/rehearsal-1-artifacts/", "docs/roadmap/index.json"], "verifyCommand": "ls docs/roadmap/operations/rehearsal-1-artifacts/ && grep -c '^### Blocker' docs/roadmap/operations/rehearsal-1-artifacts/blockers-*.md && jq '.milestones[] | select(.id==\"M4\") | .status' docs/roadmap/index.json", "acceptanceCriteria": ["rehearsal occurred with 4+ humans", "blocker log archived", "session export archived", "every blocker has a triage GitHub issue", "M4 status set to complete"], "userGate": true, "tags": ["user-gate"], "requireEvidenceTokens": [["pre-flight", "preflight"], ["session-complete", "session-end", "wrap"], ["triaged", "blockers-filed"]], "modelTier": "standard"}
```

---

## Self-Review

**Spec coverage check (against `docs/superpowers/specs/2026-06-26-m4-exit-rehearsal-design.md`):**

| Spec requirement | Implemented in |
|---|---|
| AW-257 promote both games | Task 4 |
| AW-259 parent issue + DoD | Task 0 + Task 1 |
| AW-260 runbook + blocker template + cheat sheet | Task 5 |
| AW-261 ADR-0003 decision + D-067 + AW-269 follow-on | Task 3 |
| AW-254 repurposed device-matrix verification | Task 6 (issue body in Task 2) |
| AW-231 repurposed rehearsal execution | Task 7 (issue body in Task 2) |
| M5-F epic + AW-262..AW-266 | Tasks 0 + 1 (creation only; implementation deferred) |
| M5-G epic + AW-267..AW-268 | Tasks 0 + 1 (creation only; implementation deferred) |
| D-064, D-065, D-066, D-067 in decisions-log | Task 0 (D-064/065/066), Task 3 (D-067) |
| Roadmap manifest refresh | Tasks 0 + 1 + 3 + 7 |
| #148 + #84 supersession | Task 2 |
| Local-tunnel deployment | Task 5 runbook |

**Coverage gap:** None identified. Every named artifact in the design has a task that produces it.

**Placeholder scan:** No `TBD`, `TODO`, "fill in details", "add appropriate error handling", "similar to Task N", or implementation-detail vagueness. Task 4 Step 1 leaves Crime Scene Smash copy specifics to the executing chat (founder approves) — that is correct delegation, not a placeholder, because the gate (founder approval) is explicit.

**Type consistency:** Task IDs consistent across all tasks. File paths consistent. The "validator entry point" in Task 4 Step 2 is named generically with a fallback discovery command; the actual command may differ — this is necessary because the plan does not assume the executing chat has read the validator code.

---

## User-Gate Tasks

Tasks #4, #5, #6, #7 are tagged `userGate: true`. The user-gate hook is already registered in this environment, so close-time re-validation is automatic. Each of those tasks requires explicit founder action (sign-off comment, recorded demo, or rehearsal execution) before close; the hook enforces this.
