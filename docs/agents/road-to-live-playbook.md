> Current version: v1.0
> Last updated: 2026-08-07
> Status: Active
> Canonical path: docs/agents/road-to-live-playbook.md

# Road to Live — Execution Playbook

Session-by-session prompts for resuming Nightcap work toward M6 (live). Each
prompt is one fresh session. Never continue past a prompt's STOP: the durable
file it writes is what makes the next session cheap.

**Entry point is executing the AW-290 plan.** Planning is done and merged.

## Current position (verify before relying on it)

| Item | State | Evidence |
|---|---|---|
| Stage 0 credentials | Done | Issue #264 closed 2026-08-01 |
| AW-285 | Complete, Phase 1 structural scope | PR #269 |
| AW-281–284, AW-287, AW-276 | Complete | PR #277 reconciled stale statuses |
| Road to Live status record | Written | PR #278 → `docs/product/road-to-live/status.md` |
| Mini-game readiness program | **Deferred in full until after Rehearsal 1** | D-102, PR #281; see also D-100/D-101, PR #280 |
| Spec 0087 (AW-290 narrator slot schema) | **Approved** v0.2 | PR #283, PR #288 |
| AW-290 split four ways | Issues #284, #285, #286, #287 — all open | PR #288 |
| AW-290 implementation plan | Merged, 14 tasks, all pending | `docs/superpowers/plans/2026-08-05-aw-290-narrator-slot-schema.md` |
| AW-291, AW-288/289, AW-277–280, AW-286 | Planned, not started | — |

D-102 means the Scene Sweep game-ready track and further mini-game platform
slices are **out of scope until after Rehearsal 1**. Do not pick them up.

## How to run it

Paste the standing rules at the top of every session, then the prompt.

```
STANDING RULES:
- Never state a status (spec, plan, task, PR, issue) without checking it against
  actual repo/gh state in this session. No status from memory or summary.
- Use Explore subagents for all searching. Keep your own context clean.
- Stop at every gate. Never infer my approval from silence, a PR existing, or
  prior general approval.
- Implement only what's in scope. Note unrelated bugs; don't fix them.
- The mini-game readiness program is deferred until after Rehearsal 1 (D-102).
  Do not start Scene Sweep game-ready or further platform slices.
- Do not create, modify, or delete anything in `.claude/` unless I ask.
```

## Run order

| # | Prompt | Model | Skills / commands | Produces | Stops at |
|---|---|---|---|---|---|
| 1 | **H** Hygiene: links + worktrees | Sonnet | Explore | Fix PR + worktree report | PR open |
| 2 | **E** Execute AW-290 plan ×14 | Sonnet\* | `executing-plans`, `test-driven-development`, `using-git-worktrees` | Commit per task | Every task; hard stop at 5, 10, 11 |
| 3 | **R2** Close out AW-290 | Opus | `requesting-code-review`, `receiving-code-review`, `/review-pr`, `finishing-a-development-branch`, `/scribe` | Merged, issues #284–287 closed | Before merge |
| 4 | **P1** AW-291 plan | Opus | `brainstorming`†, `writing-plans` | Plan + `.tasks.json` | Plan approval |
| 5 | **R1** ×N → **R2** | Sonnet → Opus | as above | Merged AW-291 | Before merge |
| — | **▶ `make rehearsal`** | — | — | Vesper on the TV | **Founder plays it** |
| 6 | **P2** Mystery loop discovery | Opus | `brainstorming`, `arcwright-doc-bundler` | Design doc | Doc approval |
| 7 | **P3** Mystery loop plan | Opus | `writing-plans` | Plan + `.tasks.json` | Plan approval |
| 8 | **R1** ×N → **R2** | Sonnet → Opus | as above | Merged AW-277–280 | Before merge |
| — | **▶ `make rehearsal`** | — | — | Full mystery loop | **Founder plays it** |
| later | **D1** AW-289 brief | Opus | — | Decision | AskUserQuestion |

\* Opus for the three GATE tasks (5, 10, 11) — they need judgment, not execution.
† conditional — only if the task file's Human Collaboration Contract says Creative
Collaboration.

---

## H — Hygiene: broken links and worktrees

**Sonnet** · 1 Explore subagent · ~30 min

```
Maintenance session. Verify before changing anything.

1. BROKEN RELATIVE LINKS. A partial scan found a systematic off-by-one: files in
   `docs/product/` link with `../../roadmap/...`, which resolves outside the repo;
   correct is `../roadmap/...`. Confirmed in
   `docs/product/nightcap-leverage-advantages-sabotages.md` (8+ links).
   Also: `docs/decisions/0002-harness-scenario-execution-contract.md` contains
   absolute Windows paths (`/C:/Users/nicke/...`) instead of repo-relative links.
   Also: `docs/roadmap/epics/M5-C-second-arc-schema-validation.md` links to
   `../tasks/AW-256-remove-beat-id-hardcode-from-arc-transition-gate.md`, which
   may have been renamed.

   Run a COMPLETE relative-link scan across `docs/` EXCLUDING
   `docs/archive/notion-export/` (non-canonical per AGENTS.md; its broken links
   are expected export artifacts — do not fix them). Scope the scan so it
   finishes; a naive recursive grep over the whole tree times out.

   Fix only links whose correct target is unambiguous. List ambiguous ones for
   me; do not guess.

2. WORKTREES. `git worktree list` shows 9 registered; several under
   `.claude/worktrees/` have deleted directories but live registrations. Per
   AGENTS.md do NOT delete anything in `.claude/` yourself.

   Report per worktree: branch, last commit date, whether its commits are
   ancestors of main (`git merge-base --is-ancestor`), and whether the directory
   exists. `feat/aw-271-obligations`, `feat/live-loop-ai-dialogue`, and
   `codex/minigame-platform-planning` held UNMERGED commits as of 2026-08-07 —
   re-verify and flag any that still do as must-not-prune. `docs/aw-290-planning`
   merged via PR #288 (squashed, so its commits are not ancestors — confirm
   content parity with `git diff` before treating it as safe).

   Give me a prune command with per-worktree safety assessment. Do not run it.

PR for item 1 only. Item 2 is a report. STOP before merge.
```

**Note on GitHub issue links:** issue and PR bodies here reference docs as bare
backticked paths (`` `docs/architecture/03-arc-execution.md` ``), which GitHub
renders as code, not links. That is the existing convention, not a regression.
GitHub also does not resolve repo-relative markdown links inside issue bodies. To
make a doc clickable from an issue, use a full
`https://github.com/nickejanssen/arcwright/blob/main/<path>` URL.

---

## E — Execute the AW-290 plan

**Sonnet** for build tasks, **Opus** for gate tasks · `executing-plans`,
`test-driven-development`, `using-git-worktrees`

The plan has **14 tasks across four issues**. Three are founder gates that must
not be auto-resolved:

- **Task 5** — GATE: present dressing vocabulary for founder approval
- **Task 10** — GATE: prove no Vesper refrain line was edited
- **Task 11** — GATE: founder approval of the migration design

Issue mapping: #284 AW-290 typed case anchors · #285 AW-293 wrapper dressing pack ·
#286 AW-294 slot registry · #287 AW-295 resolved case persistence.

Run one session per task, or per small batch between gates.

```
Execute Task <N> of `docs/superpowers/plans/2026-08-05-aw-290-narrator-slot-schema.md`
using `superpowers-extended-cc:executing-plans` with
`superpowers-extended-cc:test-driven-development`.

Read the plan and its `.tasks.json` first. Confirm every prior task is marked
completed AND its verify command still passes. If one fails, STOP and tell me —
do not work around it.

Ground in spec 0087 (`docs/specs/0087-aw-290-narrator-slot-schema-and-wrapper-dressing.md`,
Status: Approved) and ADR-0017. Read what the plan actually says this task is; my
summary of it is not authoritative.

GATE TASKS — 5, 10, and 11 are founder gates. If this is one of them: produce the
artifact, present it for my review, and STOP. Do not mark it complete, do not
proceed to the next task, do not infer approval. Task 11 covers a migration and
case-persistence schema, which AGENTS.md Hard Rules require me to approve
explicitly.

Use `superpowers-extended-cc:using-git-worktrees`. Implement only this task's
acceptance criteria. Note unrelated bugs; do not fix them.

Tasks 13-14 touch Alembic migration 0008 and case_store. Verify the migration
applies AND rolls back cleanly before claiming done.

DONE = task verify command passes, `make lint` and `make type` pass, each
acceptance criterion reported with evidence. Update `.tasks.json`. Commit. STOP.
```

---

## R2 — Closeout (reusable; once per branch)

**Opus** · `requesting-code-review`, `receiving-code-review`,
`finishing-a-development-branch`, `/review-pr`, `/scribe`

```
Close out `<branch>` for `<AW-NNN>` / issue(s) `<#NN>`.

1. `superpowers-extended-cc:requesting-code-review`, then `/review-pr` for the
   repo's own checklist. Report findings; do not silently fix.
2. `superpowers-extended-cc:receiving-code-review` to address them. New commits,
   never amend.
3. Confirm every acceptance criterion passes with evidence, and that CI's required
   `verify` check is green — read the actual GitHub Actions log, not local runs
   only.
4. Open the PR with `Closes: #NN` for every issue it closes. STOP before merge —
   I merge.

After I merge: `superpowers-extended-cc:finishing-a-development-branch`. Verify
the squash preserved content (`git diff <base>..<head> -- <paths>` empty) before
deleting anything. Then `/scribe` to update each task file's Status with Closeout
Evidence in the style of AW-282/283/284, and update
`docs/product/road-to-live/status.md`.

Then remind me to run `make rehearsal` on real hardware.
```

For high-stakes PRs the founder runs `/code-review ultra` — multi-agent cloud
review, billed, founder-triggered only.

---

## R1 — Execute a generic plan task (reusable)

**Sonnet** · `subagent-driven-development`, `test-driven-development`,
`using-git-worktrees`

Use for plans without founder gates. For gated plans use **E** above.

```
Execute Task <N> from `<plan path>` using
`superpowers-extended-cc:subagent-driven-development` with
`superpowers-extended-cc:test-driven-development`.

Read the plan and its `.tasks.json`. Confirm every prior task is marked completed
AND its verify command still passes before starting. If one fails, STOP and tell
me — do not work around it.

Use `superpowers-extended-cc:using-git-worktrees`. Implement only this task's
acceptance criteria. Note unrelated bugs in your report; do not fix them.

DONE = task verify command passes, `make lint` and `make type` pass, each
acceptance criterion reported with evidence. Update `.tasks.json`. Commit. STOP
and let me decide whether to continue or play it first.
```

For a well-specified GitHub issue, `/implement AW-NNN` is equivalent and carries
the repo's own scope contract via the `implementer` subagent.

---

## P1 — AW-291: the line reader

**Opus** · `brainstorming` (conditional), `writing-plans` · ~45 min

```
AW-291 — the reader that pulls Vesper's authored lines and fills in tonight's
specifics.

Confirm the AW-290 track (issues 284-287) is merged and its verify commands pass
before starting.

Read the AW-291 task file plus the content model AW-290 ACTUALLY LANDED — read
merged source, not the AW-290 plan. Plans drift from what ships. Spec 0087 is the
design of record; verify what shipped against it.

Her ~468 lines live across ~15 markdown files under `docs/design/line-libraries/`.
Confirm the count and structure yourself.

HARD CONSTRAINTS — verify each against the actual docs before relying on it:
- `the-host.md` states Vesper never fires as text-to-speech in v1. She is text on
  screen. Reject any design assuming audio.
- Line selection is deterministic. AI composes from resolved state; it does not
  decide which line fires or what is true.
- Authored line text renders as written — substitution fills tonight's specifics,
  it does not paraphrase. AW-290 Task 10 gated on proving no refrain line was
  edited; hold the same bar here.

Check the collaboration contract; if Creative Collaboration, invoke
`superpowers-extended-cc:brainstorming` and interview me first, one question at a
time, recommendation marked.

Then `superpowers-extended-cc:writing-plans`. Self-review the plan against real
source — every class, ORM model, and function it references must exist; verify by
reading, not assuming. A prior planning session invented a `KnowledgeFact` ORM
class that did not exist.

Present the plan. STOP.

STAGE DONE MEANS: Vesper's real written lines appear on the TV at the right
beats, naming tonight's actual suspects and rooms.
```

---

## P2 — Mystery loop discovery

**Opus** · `brainstorming`, `arcwright-doc-bundler` · ~60–90 min

The expensive one. Do not compress it.

```
AW-277, AW-278, AW-279, AW-280 — narrator beat transitions, detective identity
delivery, clue releases, and the Truth reveal with scoring accounting. AW-276 is
done, so these are unblocked.

Invoke `superpowers-extended-cc:brainstorming`. ALL FOUR carry formal creative
collaboration contracts. Do not write code or a plan this session.

Read all four task files, `docs/story-bibles/nightcap-couch-race.md`, and
`docs/conventions/human-collaboration.md`. Use Explore subagents to locate things.
If context gets heavy, invoke `arcwright-doc-bundler` and work from the bundle.

FIRST, before any creative questions: tell me whether these four should be one
combined effort or sequenced separately, with evidence from their Dependencies
sections. Recommend one. I decide.

THEN interview me. AskUserQuestion, ONE question at a time, recommendation
marked, free-form always available. Do not batch questions to save turns. AW-267
and AW-281 both skipped this step; it is a known failure mode in M5-I, not a
formality.

ENFORCE and call out any violation:
- The AI never decides case truth. Who did it is deterministic.
- Private information never renders on the shared TV.
- Per D-070, narrative moments are staged audiovisual sequences — content events
  carry presentation hints, not raw values.

Use cheap artifacts I can react to, one at a time. Ask what's wrong with each.

END BY writing the approved direction to a design doc under
`docs/superpowers/specs/` with a "Locked design decisions" section. Get my
explicit approval, commit, STOP.
```

---

## P3 — Mystery loop plan

**Opus** · `writing-plans` · ~30 min

```
Invoke `superpowers-extended-cc:writing-plans` to plan AW-277 through AW-280.

Input: the founder-approved mystery-loop design doc from the prior session (most
recent under `docs/superpowers/specs/`), plus each task file's Acceptance Criteria
— plan tasks must map to those criteria.

Self-review against real source before presenting: every class, ORM model, schema,
and function referenced must actually exist. Verify by reading, not assuming.

Each task needs a concrete verify command and must be completable by one subagent
in one session. Any task touching a surface needs a leak test in its acceptance
criteria (private info never reaches the shared display). Mark any task needing
founder judgment as an explicit GATE task, following the AW-290 plan's precedent.

Produce the plan and `.tasks.json`. Present for approval. STOP.
```

---

## D1 — AW-289 brief (defer until Stage 3 is next)

**Opus**

```
Frame the AW-289 Interrogation Room creative brief decision. Read the AW-289 task
file and any existing brief or discovery record. Do NOT write a new brief.

Tell me: what specifically needs my approval, what each option costs, what stays
blocked while it's unapproved, and what happens if I defer past Rehearsal 1.
Note that D-102 defers the mini-game readiness program until after Rehearsal 1 —
check whether that already answers this.

ONE AskUserQuestion, your pick marked. STOP.
```

---

## Cost discipline

- **Sonnet** for H, R1, and non-gate E tasks — mechanical execution.
- **Opus** for D1, P1, P2, P3, R2, and E gate tasks — judgment and creative gates.
- Search always through `Explore` subagents; their context dies with them instead
  of filling the main session.
- If a session feels heavy, invoke `arcwright-doc-bundler` and work from the
  bundle.
- Never continue past a STOP. The durable file exists so the next session starts
  cold and cheap.

Two play checkpoints are non-negotiable: after AW-291 (Vesper on screen) and
after AW-277–280 (loop closes). Those are where the founder finds out whether it
is fun — not at Rehearsal 1.

## References

- `docs/product/road-to-live/status.md` — current verified state
- `docs/conventions/human-collaboration.md` — interaction profiles and gates
- `docs/agents/USAGE.md` — role contracts and operating model
- `AGENTS.md` — always-on rules, Hard Rules requiring explicit approval
