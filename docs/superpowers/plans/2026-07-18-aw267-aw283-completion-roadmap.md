# AW-267 + AW-283 Completion Roadmap

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers-extended-cc:subagent-driven-development (recommended) or superpowers-extended-cc:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fully close AW-267 (#184, art-direction brief) with real founder sign-off, then fully close AW-283 (#237, suspect answer generation and contradiction detection) with real founder sign-off, in that order.

**Architecture:** Both tasks are tagged **Creative collaboration** in `docs/conventions/human-collaboration.md` and carry an identical failure pattern already recorded twice on this repo (AW-267 via PR #243/#246, AW-281 per the founder's own PR review) — generating finished subjective content before the founder is interviewed. This plan is deliberately front-loaded with interview/artifact-review gate tasks that produce no code, because the actual content (visual direction; answer tone, lie readability, contradiction fairness) cannot be decided by an agent. Task 10 (AW-283 implementation plan) is a **nested plan**: it cannot be written with concrete code today because its content depends on founder decisions made in Tasks 7–9. It will be authored via a second `writing-plans` pass once those decisions are locked, then executed as its own plan.

**Tech Stack:** Python engine (arc execution, knowledge graph, character behavior, event system) for AW-283; Markdown/CSV documentation artifacts for AW-267. No SDK/dashboard changes in either task.

**User decisions (already made):**
- Complete AW-267 first, then AW-283, in that order, within this session. ("lets wrap up AW-267 then move on to AW-283... I want to make sure that we complete both")
- AW-267's PR #243 content and D-073 are candidate research only — not founder direction, not sign-off evidence (confirmed by PR #246 and the AW-267 task file's own gate language).
- AW-282 is the template to follow: discovery record → checkpoint table → explicit founder approval before merge, filed at `docs/product/aw282-discovery-and-checkpoints.md`.

---

## Phase 1 — AW-267 (#184): Nightcap Art Direction Brief

### Task 1: Founder discovery interview

**Goal:** Conduct the AW-267 founder discovery interview live in this session and record the answers.

**Files:**
- Create: `docs/product/aw267-discovery-and-checkpoints.md` (Discovery decisions section)

**Acceptance Criteria:**
- [ ] Interview covers, one question at a time via `AskUserQuestion`: visual goals, references, tastes/dislikes, wrapper-level expectations (High Society, Corporate, Sci-Fi per story bible §2 and spec 0061), constraints, desired player feeling, and the definition of a successful Nightcap identity.
- [ ] Each question offers a recommendation plus bounded options, per the contract.
- [ ] Answers are written verbatim (or faithfully summarized with the founder's confirmation) into the discovery record.

**Verify:** `docs/product/aw267-discovery-and-checkpoints.md` exists with a populated "Discovery decisions" section covering every founder-input item listed in the AW-267 task file's Human Collaboration Contract.

**Steps:**

- [ ] **Step 1:** Read `docs/story-bibles/nightcap-murder-mystery.md` §2 (diegetic wrappers) and `docs/specs/0061-aw-258-tell-me-something-true.md` for the vocabulary and constraints the interview questions must respect.
- [ ] **Step 2:** Ask the founder, one `AskUserQuestion` at a time: (a) overall visual goals/feeling, (b) reference points and dislikes, (c) per-wrapper expectations for High Society / Corporate / Sci-Fi, (d) hard constraints (budget, timeline, technical), (e) definition of success for the brief.
- [ ] **Step 3:** Write the answers into `docs/product/aw267-discovery-and-checkpoints.md` under a "Discovery decisions" heading, following the AW-282 checkpoint file's structure.
- [ ] **Step 4:** Commit.

```bash
git add docs/product/aw267-discovery-and-checkpoints.md
git commit -m "docs(design): AW-267 founder discovery record"
```

---

### Task 2: Synthesize and confirm the creative brief

**Goal:** Turn the discovery answers into a short creative brief and get explicit founder confirmation before any moodboard work.

**Files:**
- Modify: `docs/product/aw267-discovery-and-checkpoints.md` (add "Brief" section)

**Acceptance Criteria:**
- [ ] Brief is short (aim under 300 words), synthesizes Task 1's answers, and does not introduce new creative choices not traceable to the interview.
- [ ] Founder explicitly confirms the brief (or requests a revision loop) before Task 3 starts.

**Verify:** The checkpoint file's Brief section is present and the founder's confirmation is recorded in the Checkpoints table with a date.

**Steps:**

- [ ] **Step 1:** Draft the brief from Task 1's answers.
- [ ] **Step 2:** Present it to the founder and ask for confirmation or revision via `AskUserQuestion`.
- [ ] **Step 3:** Record the confirmed brief and the checkpoint row.
- [ ] **Step 4:** Commit.

```bash
git add docs/product/aw267-discovery-and-checkpoints.md
git commit -m "docs(design): AW-267 creative brief confirmed"
```

---

### Task 3: Present comparative moodboard directions

**Goal:** Present 2–3 low-cost, comparative moodboard directions with a recommendation; pause for explicit founder direction before drafting the full brief.

**Files:**
- Create/Modify: `docs/design/moodboards/` (direction candidates; reuse existing PR #243 moodboards as raw reference material only, not as pre-approved output)
- Modify: `docs/product/aw267-discovery-and-checkpoints.md` (add "Reviewed directions" section)

**Acceptance Criteria:**
- [ ] 2–3 directions presented, each covering visual identity, per-wrapper aesthetic notes, motion principles, typography, color, and narrator visual presence at a sketch level (not production detail).
- [ ] Each direction states what it represents, what assumption it tests, and what needs founder attention.
- [ ] A recommendation is given alongside the options.
- [ ] Founder picks a direction (or requests a hybrid/revision) via `AskUserQuestion` before Task 4 starts.

**Verify:** Checkpoint file records the chosen direction and the founder's explicit approval with a date.

**Steps:**

- [ ] **Step 1:** Draft 2–3 direction sketches grounded in Task 2's brief.
- [ ] **Step 2:** Present via `AskUserQuestion` with a recommendation.
- [ ] **Step 3:** Record the decision and checkpoint row.
- [ ] **Step 4:** Commit.

```bash
git add docs/design/moodboards docs/product/aw267-discovery-and-checkpoints.md
git commit -m "docs(design): AW-267 moodboard directions reviewed"
```

---

### Task 4: Draft the final art-direction document

**Goal:** Write `docs/design/nightcap-art-direction.md` v1.0 reflecting only the approved direction from Task 3.

**Files:**
- Modify: `docs/design/nightcap-art-direction.md` (full rewrite of status header + content to match approved direction; bump version, update status line to reflect approval)
- Modify: `docs/design/the-host.md` if narrator visual presence changes from the candidate draft

**Acceptance Criteria:**
- [ ] Document covers visual identity, per-wrapper theme aesthetic (High Society, Corporate, Sci-Fi), motion system principles, typography, color, and narrator visual presence — matching the AW-267 Technical Scope list exactly.
- [ ] Status header no longer reads "Candidate research, founder direction not yet selected"; it reflects the approved status and cites the checkpoint file as evidence.
- [ ] Reference moodboards exist for each diegetic wrapper (AW-267 AC #2).
- [ ] No code, schema, or engine changes included (Must Not Do).

**Verify:** `docs/design/nightcap-art-direction.md` header states an approved status with a reference to `docs/product/aw267-discovery-and-checkpoints.md`; all three wrapper sections present.

**Steps:**

- [ ] **Step 1:** Rewrite the document against the approved direction only (do not silently keep PR #243 language that wasn't part of the approved direction).
- [ ] **Step 2:** Update `docs/design/the-host.md` narrator visual presence section if the approved direction changed it.
- [ ] **Step 3:** Ask the founder to review the assembled document as the final gate (per Required Phase 5) via `AskUserQuestion`.
- [ ] **Step 4:** Commit.

```bash
git add docs/design/nightcap-art-direction.md docs/design/the-host.md
git commit -m "docs(design): AW-267 art direction brief v1.0, founder-approved"
```

---

### Task 5: Record sign-off and open the AW-267 PR

**USER-ORDERED GATE — NON-SKIPPABLE.** This task was requested by the user in the current conversation. It MUST NOT be closed by walking around it, by declaring it "verified inline", or by substituting a cheaper check. Close only after every item in `acceptanceCriteria` has been re-validated independently, with output captured.

**Goal:** Record founder sign-off in the decisions log, open the AW-267 PR, and stop for review before starting AW-283.

**Files:**
- Modify: `docs/product/decisions-log.csv` (update D-073 status to `Committed`, or add a new decision row if the founder's approved direction diverges materially from D-073's original framing)

**Acceptance Criteria:**
- [ ] `docs/product/decisions-log.csv` shows the AW-267 decision as `Committed` (not `Proposed`), with a reference to `docs/product/aw267-discovery-and-checkpoints.md` as approval evidence.
- [ ] `docs/design/nightcap-art-direction.md` header status reads approved, not "candidate research".
- [ ] Reference moodboards exist for each diegetic wrapper (file paths present under `docs/design/moodboards/`).
- [ ] A PR is opened closing #184, following `AGENTS.md`'s commit/PR conventions (no `.claude/`/`.codex/` files staged).
- [ ] Session stops here for founder review — no AW-283 work starts until this PR is explicitly reviewed/merged per user instruction.

**Verify:** `grep AW-267 docs/product/decisions-log.csv` shows `Committed`; `gh pr view <n>` shows the PR open and referencing #184.

**Steps:**

- [ ] **Step 1:** Update the decisions log row for D-073 (or add a new row) to `Committed` status, citing the checkpoint file.
- [ ] **Step 2:** Run `git status` to confirm no `.claude/`/`.codex/` files are staged.
- [ ] **Step 3:** Commit and push, open PR via `gh pr create` closing #184.

```bash
git add docs/product/decisions-log.csv
git commit -m "docs(product): AW-267 founder sign-off recorded, D-073 committed"
git push -u origin <branch>
gh pr create --title "docs(design): AW-267 Nightcap art direction, founder-approved" --body "Closes #184"
```

- [ ] **Step 4:** Stop and report to the user for review before proceeding to Phase 2.

---

## Phase 2 — AW-283 (#237): Suspect Answer Generation and Contradiction Detection

### Task 6: Ground the implementation in existing architecture

**Goal:** Read the code and specs AW-283 must integrate with, and produce a short internal integration note (no founder-facing artifact yet).

**Files:**
- Read only (no file changes): `engine/` character-behavior module, AW-282's `InteractionRuntime`/`InteractionResolution` implementation, the spec 0071 dialogue pipeline (PR #225), knowledge-graph query API, `config/routing_table.json`, `engine/routing/router.py`.

**Acceptance Criteria:**
- [ ] Can name the exact function/class that AW-283 will call to consume an `InteractionResolution` (per ADR-0014's stated AW-283 handoff).
- [ ] Can name the exact knowledge-graph query function used pre-generation (mandatory per AGENTS.md Key Engine Constraints).
- [ ] Can name the exact routing entry point and confirm no provider/model string will be needed outside `config/routing_table.json` / `engine/routing/router.py`.

**Verify:** A short note (in the task's working context, not committed) lists these integration points with file:line references.

**Steps:**

- [ ] **Step 1:** Read `docs/specs/0074-aw282-structured-interaction-loop.md` and `docs/decisions/0014-structured-interaction-resolution.md` for the `InteractionResolution` handoff contract.
- [ ] **Step 2:** Read the AW-282 engine code (`InteractionRuntime`, `InteractionResolution`) to find the exact object shape AW-283 will receive.
- [ ] **Step 3:** Read `docs/architecture/04-knowledge-graph.md` and `docs/architecture/07-character-behavior.md` for the mandatory pre-generation knowledge query and behavior-profile assembly (AW-211).
- [ ] **Step 4:** Read `config/routing_table.json` and `engine/routing/router.py` to confirm the fast-tier routing entry point for answer generation.
- [ ] **Step 5:** No commit — this is a read-only grounding task.

---

### Task 7: Founder discovery interview

**Goal:** Conduct the AW-283 founder discovery interview live in this session and record the answers.

**Files:**
- Create: `docs/product/aw283-discovery-and-checkpoints.md` (Discovery decisions section)

**Acceptance Criteria:**
- [ ] Interview covers, one question at a time via `AskUserQuestion`: suspect-answer tone, lie readability (how obvious/subtle an authorized lie should feel), contradiction fairness (what makes a catch feel earned vs. arbitrary), acceptable latency trade-offs, representative exchanges, and success definition.
- [ ] Each question offers a recommendation plus bounded options.
- [ ] Answers are written into the discovery record.

**Verify:** `docs/product/aw283-discovery-and-checkpoints.md` exists with a populated "Discovery decisions" section covering every founder-input item in AW-283's Human Collaboration Contract.

**Steps:**

- [ ] **Step 1:** Read `docs/story-bibles/nightcap-couch-race.md` and `docs/story-bibles/daily-case.md` for the existing contradiction-ledger design spine.
- [ ] **Step 2:** Ask the founder, one `AskUserQuestion` at a time, covering each founder-input item above.
- [ ] **Step 3:** Write answers into `docs/product/aw283-discovery-and-checkpoints.md`.
- [ ] **Step 4:** Commit.

```bash
git add docs/product/aw283-discovery-and-checkpoints.md
git commit -m "docs(nightcap): AW-283 founder discovery record"
```

---

### Task 8: Synthesize and confirm the behavior brief

**Goal:** Turn Task 7's answers into a short behavior brief and get explicit founder confirmation.

**Files:**
- Modify: `docs/product/aw283-discovery-and-checkpoints.md` (add "Brief" section)

**Acceptance Criteria:**
- [ ] Brief synthesizes tone, lie readability, and fairness rules traceable to Task 7's answers.
- [ ] Founder explicitly confirms the brief before Task 9 starts.

**Verify:** Checkpoint file's Brief section present; Checkpoints table has a dated confirmation row.

**Steps:**

- [ ] **Step 1:** Draft the brief.
- [ ] **Step 2:** Present for confirmation via `AskUserQuestion`.
- [ ] **Step 3:** Record confirmation and checkpoint row.
- [ ] **Step 4:** Commit.

```bash
git add docs/product/aw283-discovery-and-checkpoints.md
git commit -m "docs(nightcap): AW-283 behavior brief confirmed"
```

---

### Task 9: Present representative samples and fairness cases

**Goal:** Present representative truthful answers, authorized lies, contradiction cases, and fairness edge cases as low-cost text artifacts; pause for explicit founder direction before writing the implementation plan.

**Files:**
- Create: `docs/superpowers/specs/2026-07-18-aw283-answer-generation-design.md` (or a later date if this task runs on a different day) — samples, contradiction cases, fairness edge cases, review instructions
- Modify: `docs/product/aw283-discovery-and-checkpoints.md` (add "Reviewed scenarios" section, mirroring AW-282's checkpoint file structure)

**Acceptance Criteria:**
- [ ] At least 3 representative truthful answer samples, 2 authorized-lie samples, 2 confirmed-contradiction cases, and 2 fairness edge cases (e.g., a flag on a technically-true-but-misleading statement) are presented.
- [ ] Each sample explains what it represents, what assumption it tests, and what needs founder attention.
- [ ] A recommendation accompanies any open choice.
- [ ] Founder approves or requests revision via `AskUserQuestion` before Task 10 starts.

**Verify:** Checkpoint file's "Reviewed scenarios" section links to the design doc; Checkpoints table shows an approved row for this gate.

**Steps:**

- [ ] **Step 1:** Draft the samples grounded in Task 8's brief and Task 6's architecture note (so samples are realistic, not aspirational).
- [ ] **Step 2:** Present via `AskUserQuestion`, one open question at a time if any remain.
- [ ] **Step 3:** Record approval and checkpoint row.
- [ ] **Step 4:** Commit.

```bash
git add docs/superpowers/specs/2026-07-18-aw283-answer-generation-design.md docs/product/aw283-discovery-and-checkpoints.md
git commit -m "docs(nightcap): AW-283 answer/lie/contradiction samples reviewed"
```

---

### Task 10: Write the AW-283 implementation plan

**Goal:** Author a full TDD implementation plan for AW-283 using the `writing-plans` skill again, now grounded in the founder-approved brief and samples from Tasks 6–9.

**Files:**
- Create: `docs/superpowers/plans/<date>-aw283-suspect-answer-generation.md` and its `.tasks.json`

**Acceptance Criteria:**
- [ ] Plan covers: answer generation path (knowledge query → behavior profile → fast-tier routing → prompt-cached case context), lie execution (authorized lies rendered, ground truth intact in knowledge graph, lie markers internal-only), claim ledger schema (speaker, asker, round, beat, referenced facts), deterministic contradiction detection (claim-vs-claim, claim-vs-evidence), scoring/penalty event emission, and p95 latency telemetry.
- [ ] Every AW-283 acceptance criterion from the task file maps to a plan task.
- [ ] No placeholders (per the `writing-plans` skill's own rule) — this plan is written with full context, unlike Task 11 in *this* roadmap.
- [ ] Plan explicitly enforces the Must Not Do list: no model-call contradiction judging, no lie/truth markers in pre-reveal events, no frontier-tier default routing.

**Verify:** Plan file exists, passes the `writing-plans` skill's self-review (spec coverage, placeholder scan, type consistency).

**Steps:**

- [ ] **Step 1:** Invoke `superpowers-extended-cc:writing-plans` again, with Tasks 6–9's outputs as the spec input.
- [ ] **Step 2:** Follow that skill's process to completion, including its own `TaskList`/`TaskCreate` steps for the nested implementation tasks.
- [ ] **Step 3:** At that skill's Execution Handoff gate, choose the execution mode and proceed.

---

### Task 11: Execute the AW-283 implementation plan

**Goal:** Implement AW-283 via TDD per the plan from Task 10, in an isolated git worktree.

**Files:** Determined by Task 10's plan (engine character-behavior/dialogue modules, claim ledger, contradiction detection, telemetry — exact paths TBD by that plan since they depend on founder-approved samples not yet produced).

**Acceptance Criteria:**
- [ ] Isolated workspace created via `superpowers-extended-cc:using-git-worktrees` before implementation starts.
- [ ] Tests written with the code, not after (`superpowers-extended-cc:test-driven-development`).
- [ ] All AW-283 acceptance criteria pass: no out-of-knowledge-state leaks (AW-272 eval batch, clean seed), seeded lie is deterministically catchable, false-positive guard rejects flags on consistent statements, claim provenance is queryable, p95 latency recorded in telemetry.
- [ ] `pytest engine/tests/` green; `ruff check`/`ruff format --check` clean.

**Verify:** `pytest engine/tests/ -k "contradiction or claim_ledger"` passes; `python -m ruff check engine api` clean.

**Steps:**

- [ ] **Step 1:** Set up the worktree per `using-git-worktrees`.
- [ ] **Step 2:** Execute Task 10's plan task-by-task via `subagent-driven-development` or `executing-plans`.
- [ ] **Step 3:** Run the full engine test suite and the AW-272 eval batch against a Couch Race synthetic case.

---

### Task 12: Code review

**Goal:** Run `superpowers-extended-cc:requesting-code-review` and then the `reviewer` agent against the Arcwright review checklist before opening the PR.

**Files:** None (review only).

**Acceptance Criteria:**
- [ ] `requesting-code-review` skill run and feedback addressed per `superpowers-extended-cc:receiving-code-review`.
- [ ] `reviewer` agent reports pass on the Arcwright checklist (game agnosticism, surface agnosticism, routing table discipline, no hardcoded beat IDs, knowledge-state gating, deterministic contradiction logic, no pre-reveal truth leaks).

**Verify:** Reviewer agent's pass/block report, with per-criterion evidence, is captured.

**Steps:**

- [ ] **Step 1:** Invoke `superpowers-extended-cc:requesting-code-review`.
- [ ] **Step 2:** Dispatch the `reviewer` agent against the diff.
- [ ] **Step 3:** Fix any blocking findings and re-run.

---

### Task 13: Open the AW-283 PR

**USER-ORDERED GATE — NON-SKIPPABLE.** This task was requested by the user in the current conversation. It MUST NOT be closed by walking around it, by declaring it "verified inline", or by substituting a cheaper check. Close only after every item in `acceptanceCriteria` has been re-validated independently, with output captured.

**Goal:** Open the AW-283 PR and stop for founder review, completing both tasks from this session's request.

**Files:**
- Modify: `docs/product/decisions-log.csv` (record AW-283 founder sign-off, mirroring D-074's AW-282 entry)

**Acceptance Criteria:**
- [ ] `pytest engine/tests/` contradiction and claim-ledger tests pass (captured output).
- [ ] AW-272 continuity eval batch run against a Couch Race synthetic batch reports zero knowledge leaks on a clean seed (captured output).
- [ ] Answer-generation p95 latency recorded in telemetry (captured value).
- [ ] A decisions-log row records founder sign-off for AW-283, citing `docs/product/aw283-discovery-and-checkpoints.md`.
- [ ] A PR is opened closing #237, with no `.claude/`/`.codex/` files staged.
- [ ] Session stops here for founder review.

**Verify:** `gh pr view <n>` shows the PR open and referencing #237; `grep AW-283 docs/product/decisions-log.csv` shows a `Committed` row.

**Steps:**

- [ ] **Step 1:** Add the decisions-log row.
- [ ] **Step 2:** `git status` check for agent-local files.
- [ ] **Step 3:** Commit, push, open PR.

```bash
git add docs/product/decisions-log.csv
git commit -m "docs(product): AW-283 founder sign-off recorded"
git push -u origin <branch>
gh pr create --title "feat(nightcap): AW-283 suspect answer generation and contradiction detection" --body "Closes #237"
```

- [ ] **Step 4:** Report to the user: both AW-267 and AW-283 are now implemented, tested, sign-off recorded, and PR'd for review.
