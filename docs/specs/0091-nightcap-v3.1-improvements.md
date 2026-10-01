---
id: nightcap.specs.0091-nightcap-v3.1-improvements
namespace: nightcap
title: Nightcap v3.1 Improvement and Validation Contract
owner: Nico Janssen
status: active
review_by: "2027-04-01"
sensitivity: internal
source: authored
x-scope-evidence: none
tags: []
supersedes: []
---

# Nightcap v3.1 Improvement and Validation Contract

**Status:** Approved by founder, 2026-10-01; implementation in progress.  
**Version:** 1.0  
**Author:** Codex | **Date:** 2026-10-01  
**Canonical path:** `docs/specs/0091-nightcap-v3.1-improvements.md`

# References

- [32-item improvement review](../gdd/nightcap/04-supporting-design/99-paper-test-02-v3.0-improvement-review.md).
- [GDD authority](../gdd/nightcap/README.md), [decision ledger](../gdd/nightcap/00-governance/00-decision-ledger.md), [memory](../gdd/nightcap/01-authoritative-gdd/03-case-board-memory.md), [Last Call](../gdd/nightcap/01-authoritative-gdd/05-last-call-case-file.md), and [accessibility](../gdd/nightcap/01-authoritative-gdd/10-difficulty-accessibility.md).
- [PRD scope](../prd/03-scope.md), [arc execution architecture](../architecture/03-arc-execution.md), [runtime boundary](../gdd/nightcap/01-authoritative-gdd/11-arcwright-runtime-boundary.md), and [Playtest Lab contract](0088-arcwright-playtest-lab-contract.md).
- [Human collaboration](../conventions/human-collaboration.md), [playtest rules](../../playtests/AGENTS.md), [Phase 1 design](../superpowers/specs/2026-09-27-phase-1-v3-send-readiness-design.md), and [approved v3.0 analysis](../gdd/nightcap/02-validation/99-paper-test-02-v3.0-analysis-plan.md).
- [Implementation plan](../superpowers/plans/2026-10-01-nightcap-v3.1-improvements.md) and [creative samples](../gdd/nightcap/04-supporting-design/99-paper-test-02-v3.1-creative-samples.md).

**x-scope-evidence:** `none`. This contract proposes non-canon research-fixture improvements within existing GDD direction. It approves no new production capability. Any new product scope requires its own durable decision record.

# Overview

Address all 32 reviewed improvements in a draft v3.1 successor to *A Knock at Midnight*. Each receives implementation or a concrete research/validation artifact, with human-dependent checks recorded separately. Preserve the published v3.0 artifact and its research history.

The user's 2026-10-01 request authorizes the 32-item objective and subagent-driven execution. This package supplies the concrete choices and acceptance criteria required before implementation. It is not a claim that the objective or these choices are already validated.

# In Scope

- Vanilla HTML/CSS/JavaScript successor at `playtests/nightcap-paper-test-02-v3.1/`, ID `nightcap-paper-test-02-v3.1`, version `3.1`, proposed route `/nightcap/paper-test-02/v3.1/`.
- All 32 improvements, grouped into six sequential implementation/review tasks.
- Separate v3.1 protocol, creative samples, evidence/proof dossier, tests, local browser QA, and a 32-row evidence ledger.
- Read-only Jotform inspection using form `262397917027062`, instrument version `2.2`; local draft registration and build.

# Out of Scope

- Editing published v2.2/v3.0 fixture files, deleting historical routes, or mixing version cohorts.
- Production runtime changes, dependencies, backend analytics, accounts, generalized framework, new minigame pool, multiplayer, production Leverage economy, full Case Board, final Postmortem, production Structured Reconstruction, or Vesper performance implementation.
- Form mutation, automatic submissions, publishing, promotion, invitations, push, or merge without their explicit approvals.
- Treating automated checks as evidence of fun, beautiful prose, physical-phone behavior, or accessible competitive equivalence.

# Human Collaboration Contract

**Interaction profiles:** Independent execution for approved technical work; decision interview for research rules; creative collaboration for narrative; facilitated live operation for phone/research sessions.

**Required founder inputs:** approve this package's concrete choices and sample direction; review the resulting playable artifact; approve any external release/return arrangement; conduct the labeled phone smoke. External players provide experience evidence.

**Phase gates:**

1. Approve this spec, companion implementation plan, and creative sample direction. This permits implementation and local validation.
2. Review the rewritten case, proof dossier, and playable local artifact. Technical work can finish while subjective sign-off remains pending.
3. Approve the exact version-safe survey return and publishing arrangement after local verification. Survey changes need action-time approval.
4. Founder phone smoke, read-only submission verification, then a separate external-invite decision.

**Review package:** spec, six-task plan, three samples, and eventually a 32-row validation ledger. Every row identifies artifact, automated evidence, human evidence, and remaining action.

**Approval evidence:** on 2026-10-01 the founder replied "Approved" to the concrete specification, six-task plan, and creative-sample package. This approves the design/research choices, sample direction and proposed opening framing for implementation. Final artifact sign-off, release, phone smoke, and external-player evidence remain separate gates.

**Owner actions:** creative review, phone play/submission, screenshot and approximate time, publication approval, recruitment. Warn before each live timed lock run so the Browser pane can stay visible.

# Proposed Design

## 1. Version and release integrity

Copy the existing fixture into the new directory and use a separate state key. Register v3.1 as `draft`, `published: null`; preserve `current_tests.nightcap = nightcap-paper-test-02-v3.0`. Preserve historical source byte-for-byte.

The builder derives root `?reveal=1` from `current_tests.nightcap`. Promotion can therefore redirect historical form returns to a newer case version. The actual Jotform return target was not verified in Phase 1. Read-only preflight must determine it. Present a concrete version-safe release solution before changing any root/form routing. Retaining both fixture URLs alone does not resolve this risk. The builder includes draft artifacts, so merging a draft catalog entry can publish its route even without promotion.

## 2. Research rules proposed for v3.1

Preserve the approved v3.0 numbers and historical interpretation. Correct its stale closing approval paragraph only. Create a separate protocol for v3.1 with these proposed amendments:

- Retain 6-8 eligible new players and the three-week window. Exclude all QA, founder, team, smoke, repeat, and prior-case-exposed players; exposure includes v3.0 and solution/design material. Keep identities private.
- H1: let `N` be included players, `U` missing first targets, and `C` the largest observed target count. Pass only if `(C + U) / N <= 0.75`; fail if `C / N > 0.75`; otherwise inconclusive. No observed target is inconclusive. Report observed distribution as well.
- H2/H3: retain numeric bars; missing observations cannot count as success. Report bounds. If missingness can change the conclusion, mark that hypothesis inconclusive rather than invent a result.
- Name H3 inference-action uptake. A click is not proof of deduction. After play ask the neutral descriptive question, "What made you change your theory?" Record the answer privately, outside Jotform unless a later instrument change is approved.
- H4 retains at least 75% explicit spend/save interaction. Add a genuine explicit save option after a human lock win when Leverage remains. Distinguish spend, explicit save, and unused balance; the latter alone establishes no intent.
- `post_lock_return_seconds` keeps attempted-lock result to next investigation/inference semantics. Keep the median bar at 60 seconds. Require at least six measured attempted-lock intervals and an interval for every included attempted-lock run; otherwise the timing submeasure is inconclusive. Declines are reported separately and emit no fake minigame duration. This can require additional research when many decline.
- H5 remains pre-reveal ratings and submission completion, with existing median 4, continuation 50%, and completion 75% bars. Separate gameplay completion, verified submission, and observed reveal return. Add a descriptive post-reveal debrief about what felt satisfying or unresolved, without changing survey order or scales.
- Any inconclusive hypothesis prevents an overall pass or an automatic design-failure classification. Missing evidence leads to research follow-up. It is not itself a game failure.

Keep Jotform fields/scales/hidden names and instrument version unchanged. Document successor event values as a fixture-version change. Never put private notes or raw tester comments in telemetry URLs.

## 3. Investigation, memory, and evidence

- Retain Last Call availability after five major investigations and a maximum of six new investigations; define both in case configuration and enforce in runtime plus UI.
- A new person/location costs one action. Rereading is free. Earned conditional challenges and the single paid Follow the Thread remain available after action six until entering Last Call. Entering Last Call closes new acquisition while preserving read-only access.
- Explain costs before the first move; make cap behavior independent of which scene remains open.
- Persist a source-attributed earned scene/claim journal, public suspect hooks, and earned suspect history. Add optional local private notes capped at 500 characters. Notes never grant proof or enter telemetry.
- Establish every granted discovery in its visible source scene. In particular add Clara's transcription acknowledgment, Beatrice's letters encounter, and the observable transcript initials where those facts are currently granted.
- Replace comparison-giving prompts with concrete, known objects/statements and neutral actions. A contextual prompt must not mention a fact the player has not encountered.

**Proof conflict to resolve:** both descriptive motive routes in current `essential_truths.routes` require two distinct Follow the Thread rewards, while one Leverage and the single-use restriction prevent acquiring both. Do not copy those routes into the scorer.

Retain the four/five-piece evaluator as the starting operational model. Produce a dossier explaining each sufficient group and its legitimate acquisition path, then reconcile descriptive routes with reachable and justified sets. Document scoring compression explicitly. A group without a defensible causal explanation requires a proposed authored correction, not extra Leverage or weaker proof to make tests green. Founder review owns narrative sufficiency; legal-path tests own reachability.

## 4. Lock, information, and rival

- Provide an untimed ready screen. Start begins both clocks. Decline emits `competitive_window_declined`, releases the cylinder publicly with an authored explanation, and consumes no action/Leverage. It emits no `minigame_started`, `minigame_result`, or lock duration.
- Retain four pins, current tolerances, the 2,400 ms cycle, and the 19-second rival clock initially. Show 19 seconds as the operative competitive deadline. Keep the 45-second defensive timeout and its documented normal unreachability; do not create new gameplay solely to exercise it.
- Judge input against the last displayed marker position. Resolve an elapsed deadline before accepting queued or resumed input. Hidden-tab time continues; return resolves once before further input.
- Retain or restore Set pin focus between pins. Use tap/click wording and meaningful pin/result announcements. Avoid continuous frame announcements.
- Suppress nonessential motion. Document that the core moving target remains and requires human accessibility assessment. Decline is an exit, not equivalent accessible competition. A replacement mechanic is a separate design decision.
- Show Listen In's acquired fact immediately. State that first look expires on the next new major investigation or entering Last Call; free review/questions do not consume it. Public release occurs once; learned facts remain.
- Nora follows a small fixed authored evidence trajectory independent of lock victory. Proposed bounded direction: her suspicion of Quill follows evidence of fraudulent performance; a mistaken theory need not become correct when she wins a box. Approve the actual trajectory and copy during the case artifact review. Never leak human-private facts to her.

## 5. Narrative, Case File, and recovery

- Preserve the culprit, murder method, cast, and fixed timeline. New opening framing and sample prose are explicit proposals in the companion artifact. No secret motive facts may be silently invented by a prose edit.
- Apply approved voice direction across existing encounters; preserve evidence and distinguish direct observation, testimony, and inference. Review the opening, pressured interview, and reveal samples before full rewrite.
- Keep the four/five unordered-fact proxy. Add selection count, accessible constraints, retained draft, and read-only journal access. Do not label it proof of production reconstruction UX.
- After Truth, map the stored verdict reason to one concise factual explanation. Keep correctness hidden before commitment and move implementation jargon to documentation.
- In reveal mode without a valid committed same-fixture Case File, show the solution with "Your saved Case File is unavailable, so your individual verdict cannot be shown." Create neither a synthetic run nor completion/return telemetry. Preserve actual verdict for intact committed state.
- Handle storage access exceptions with an explicitly labeled in-memory session where possible. Warn that refresh/return persistence is unavailable. Provide bounded retry for case-data load failure. Never invent restored state.

# Acceptance Criteria

**A:** automated/source evidence. **B:** browser interaction. **H:** founder/human observation. **E:** external survey/release evidence. Rows stay pending until their actual required evidence exists.

| Item | Required outcome | Task | Evidence |
|---|---|---|---|
| 01 | Explicit spend/save/unused distinct, including human-win-save | 1, 3 | A, B |
| 02 | Click uptake distinguished from deduction; neutral debrief | 1, 2 | A, H |
| 03 | Missingness cannot fabricate pass; sample limits explicit | 1 | A |
| 04 | Accurate interval endpoints and interpretation | 1, 3 | A |
| 05 | Gameplay/submission/reveal separate; phone handoff verified | 1, 5, 6 | A, B, E |
| 06 | Consistent approval prose; triage records evidence, cause, class, confidence, smallest fix and what would disprove the diagnosis | 1 | A |
| 07 | Each fact established by an earned visible encounter | 2, 4 | A, H |
| 08 | Earned transcript and private notes retained without new grants | 2 | A, B |
| 09 | Costs/cap/free questions consistent in runtime and UI | 2 | A, B |
| 10 | Clear decline path preserving solvability | 3 | A, B, H |
| 11 | Clear contextual actions without supplied inference | 2, 4 | A, H |
| 12 | Public hooks and earned suspect history without spoilers | 2, 4 | A, H |
| 13 | Untimed instructions, accurate deadline and input wording | 3 | A, B, H |
| 14 | Stable focus; truthful accessibility assessment | 3, 6 | A, B, H |
| 15 | Input timing checked; first-use tuning evidence recorded | 3, 6 | A, B, H |
| 16 | Acquired information and expiry visible and precise | 3 | A, B, H |
| 17 | Justified rival trajectory independent of lock winner | 3, 4 | A, H |
| 18 | Concise causal release/rival transitions | 3, 4 | A, H |
| 19 | Clear player role, purpose, and rivalry | 4 | H |
| 20 | Distinguishable suspect voices | 4 | H |
| 21 | Attributable testimony; alternate routes preserved | 2, 4 | A, H |
| 22 | Credible stakes grounded in existing truth | 4 | H |
| 23 | Delivered evidence supports timeline/access causal chain | 2, 4 | A, H |
| 24 | Samples and full prose reviewed by founder | 4 | H |
| 25 | Count/review reduce bookkeeping; proxy limitation explicit | 5 | A, B, H |
| 26 | Justified sufficient proof sets with legal acquisition paths | 2 | A, H |
| 27 | Post-truth verdict explains decisive reason | 5 | A, B, H |
| 28 | Missing-state reveal fabricates no failure or completion | 5 | A, B |
| 29 | Correct visibility/outcome-specific QA assertions | 6 | A, B |
| 30 | Physical device distinguished from CSS viewport | 1, 6 | A, H |
| 31 | Long URL, submitted read-back, storage and return checked | 5, 6 | A, B, E |
| 32 | Immutable versions, bounded scope, exclusions and gates | 1, 6 | A, E |

# Test Plan

- **Baseline on 2026-10-01:** all five existing v3.0 Node suites ran: 31 tests passed, zero failed. No browser or new implementation acceptance is implied. The existing Rusk test seeds state directly and therefore proves scorer acceptance, not reachability.
- **TDD:** changed pure transitions, ownership/provenance, caps, legitimate proof acquisition, deadline/decline/save/spend, idempotence, notes exclusion, missing-state reveal, storage exceptions, and research arithmetic. No new dependency.
- **Integration:** use the same transitions as the app from initial state through commitment. Cover Beatrice and Rusk alternatives, all lock outcomes, red-herring-first, spent/saved Leverage, and refresh. Tests claiming legal paths must not inject discoveries or action counts.
- **Browser:** desktop, 360 CSS-pixel viewport, keyboard lock, journal/notes, free questions at cap, refresh, hidden-tab deadline, intact and missing-state reveal. Record run IDs, viewport, and observed actions. Warn before timed play.
- **Transport:** measure a deterministic stress stream of 1,000 repeated miss attempts within an allowed timestamp and verify local URL encode/decode fidelity. Label it transport stress, not human timing. Separately verify an owner-approved long smoke submission read-back; do not invent a universal URL ceiling or equate local fidelity with Jotform acceptance.
- **Regression:** unchanged published tree hashes; historical and successor suites pass; catalog validates; local build preserves original routes and noncurrent draft status.
- **Human/external:** founder approves creative artifact/proof reasoning; actual first-use/device/accessibility observations; labeled phone survey-return smoke; eligible external cohort. Missing observations remain pending with owner action, never replaced by agent judgment.

# Risks and Unknowns

- Actual form return may require a separately approved version-safe mechanism before v3.1 release.
- Reachable proof groups still require an authored sufficiency argument; automated reachability does not establish narrative fairness.
- Declines can leave fewer than six measured attempted-lock intervals and make H4 inconclusive.
- A moving-target task has unresolved accessibility limits after focus corrections.
- Story/UX changes affect comparisons; version cohorts must remain separate.
- All 32 includes human-dependent work. Technical completion cannot close those acceptance criteria prematurely.

# Open Questions

1. Resolved 2026-10-01: founder approved this exact v3.1 design, research rules, companion task plan, and sample direction.
2. What exact version-safe survey return can be demonstrated for release? Resolve after read-only preflight and before publishing, not by guessing in code.

No acceptance row is passed merely because this specification exists.
