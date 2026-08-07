> Current version: v1.0
> Last updated: 2026-08-07
> Status: Active
> Canonical path: docs/agents/road-to-live-playbook.md

# Road to Live — Execution Playbook

Session-by-session prompts for resuming Nightcap work toward M6 (live). Each
prompt is one fresh session. Never continue past a prompt's STOP: the durable
file it writes is what makes the next session cheap.

**Entry point is the AW-290 track, not Stage 1.** Stage 0 (credentials) closed
2026-08-01. AW-285 shipped Phase 1 structural scope.

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
- Do not touch `run_seed` in `resolver.py` — known gap, needs cross-module approval.
- Do not create, modify, or delete anything in `.claude/` unless I ask.
```

## Run order

| # | Prompt | Model | Skills / commands | Produces | Stops at |
|---|---|---|---|---|---|
| 1 | **P0** Land AW-290 planning | Sonnet | `/review-pr` | Merged plan + issues 284–287 | Before merge |
| 2 | **P1** Record state | Sonnet | `/scribe`, Explore | `road-to-live/status.md` | Docs PR open |
| 3 | **P2** Hygiene + link repair | Sonnet | Explore | Fix PR + worktree report | PR open |
| 4 | **D2** Mini-game greenlight | Opus | `arcwright-sme`, `/scribe` | Decision, recorded | AskUserQuestion |
| 5 | **R1** ×4 (issues 284–287) | Sonnet | `subagent-driven-development`, `test-driven-development`, `using-git-worktrees` | Commit per task | Each task done |
| 6 | **R2** | Opus | `requesting-code-review`, `receiving-code-review`, `/review-pr`, `finishing-a-development-branch`, `/scribe` | Merged AW-290 | Before merge |
| 7 | **P4** AW-291 plan | Opus | `brainstorming`\*, `writing-plans` | Plan + `.tasks.json` | Plan approval |
| 8 | **R1** ×N → **R2** | Sonnet → Opus | as above | Merged AW-291 | Before merge |
| — | **▶ `make rehearsal`** | — | — | Vesper on the TV | **Founder plays it** |
| 9 | **P5** Mystery loop discovery | Opus | `brainstorming`, `arcwright-doc-bundler` | Design doc | Doc approval |
| 10 | **P6** Mystery loop plan | Opus | `writing-plans` | Plan + `.tasks.json` | Plan approval |
| 11 | **R1** ×N → **R2** | Sonnet → Opus | as above | Merged AW-277–280 | Before merge |
| — | **▶ `make rehearsal`** | — | — | Full mystery loop | **Founder plays it** |
| later | **D1** AW-289 brief | Opus | — | Decision | AskUserQuestion |

\* conditional — only if the task file's Human Collaboration Contract says
Creative Collaboration.

`R1` runs **once per plan task**, fresh session each. `R2` runs **once per branch**.

---

## P0 — Land the AW-290 planning branch

**Sonnet** · `/review-pr` · ~20 min

AW-290 is already specified and split. Branch `docs/aw-290-planning` holds two
unmerged commits; do not re-plan it.

```
Branch `docs/aw-290-planning` is 2 commits ahead of main:
- 70098c6 docs(specs): approve spec 0087, add migration design and AW-290 plan
- 7a397b3 docs(roadmap): split AW-290 four ways and create issues 284-287

Verify that branch state yourself (`git log main..docs/aw-290-planning`) before
acting. Read what it actually changes (`git diff main...docs/aw-290-planning --stat`
then the substantive files).

Confirm before recommending a merge:
- Spec 0087 (`docs/specs/0087-aw-290-narrator-slot-schema-and-wrapper-dressing.md`)
  Status and whether the branch changes it from Draft to Approved.
- ADR-0017 (narrator slot resolution and wrapper dressing) is Accepted.
- ADR-0022 (resolved case persistence) exists and the spec's dependency on it holds.
- Issues 284 (AW-290), 285 (AW-293), 286 (AW-294), 287 (AW-295) exist, are open,
  and their titles match what the branch's roadmap files claim.
- The branch is docs-only. If it touches engine/api/sdk, STOP and tell me.

APPROVAL GATE: spec 0087 involves a migration and case-persistence schema. Per
AGENTS.md Hard Rules that needs my explicit approval. Summarize the schema change
in plain language and what it costs to reverse. Do not assume prior approval
carries.

Run `/review-pr` against the branch. Open a PR. STOP before merge.
```

---

## P1 — Record verified state

**Sonnet** · `/scribe` + 1 Explore subagent · ~15 min

```
Act as Scribe (`/scribe`). Recording session, not an audit. Do not re-derive
what is already established below; make it durable.

Write `docs/product/road-to-live/status.md`, dated today, following the format of
the existing files in `docs/product/mini-game-readiness/`.

DONE since the 26 Jul "Road to Live" roadmap snapshot:
- Stage 0 credentials — issue #264 closed 2026-08-01. Live two-player rehearsal
  joins, starts, transitions pour -> scene on real devices; automated smoke passes.
  Hidden blockers fixed en route: wrong default arc, missing `rehearsal-start` make
  target, token leaking into a URL, Firebase preflight gaps.
- AW-287 Leverage payout — merged (PRs #251/#253). The "minigames don't pay
  Leverage" gap is CLOSED; win -> currency -> sabotage loop exists.
- AW-285 — Complete, accepted Phase 1 structural scope (PR #269). Shared-display
  projection layer exists. Six-beat integration, privacy/device checks, and
  audiovisual polish remain OPEN under AW-286.
- AW-281, AW-282, AW-283, AW-284 — all Complete. PR #277 corrected their task
  files, which were stale at Planned/In Progress.
- AW-276 Arc Voice Block Injection — done, unblocking AW-277 through AW-280.
- AW-290 — NO LONGER unplanned. ADR-0017 (Accepted, the charter), ADR-0022
  (resolved case persistence), and spec 0087 landed (PR #283, D-089/D-103, from a
  founder decision interview). AW-290 has been split four ways into issues 284
  (typed case anchors + evidence short form), 285 (AW-293 wrapper dressing pack),
  286 (AW-294 machine-readable slot registry), 287 (AW-295 resolved case
  persistence). Record the current merge state of `docs/aw-290-planning`.
- Parallel track: mini-game readiness program — Scene Sweep backend + design (PRs
  #273/#274), browser-first mini-game platform specs 0077-0080 partially
  implemented (PR #275). Capped at the browser golden path; further slices gated
  on founder execution approval.

STILL UNMOVED:
- AW-291 (the line reader): Planned. 468 authored lines remain docs-only prose
  under `docs/design/line-libraries/` with no engine reader.
- AW-288 / AW-289: Planned, blocked on founder creative approval.
- AW-277-280: Planned but UNBLOCKED (AW-276 done). Each carries a creative gate.
- AW-286 and Stage 6+ (art): untouched, correctly sequenced after the above.

OPEN FOUNDER DECISIONS (record as blocking, unresolved):
- Approve the AW-289 Interrogation Room creative brief.
- Greenlight (or not) the next slice of the mini-game readiness program.

Dispatch ONE Explore subagent to spot-check only these three:
1. AW-276 really is Complete (it unblocks AW-277-280).
2. `nightcap/content/` still does not exist and no engine reader for
   `docs/design/line-libraries/` exists.
3. `git status` clean, local main == origin/main.

Also record whether the "Nightcap" trademark blocker (fallback: Revel) is still
open — check `docs/product/` open-questions, don't guess.

Docs-only PR. STOP.
```

---

## P2 — Hygiene and link repair

**Sonnet** · 1 Explore subagent · ~30 min

```
Maintenance session. Verify before changing anything.

1. BROKEN RELATIVE LINKS. A partial scan found a systematic off-by-one: files in
   `docs/product/` link with `../../roadmap/...` which resolves outside the repo;
   correct is `../roadmap/...`. Confirmed instances in
   `docs/product/nightcap-leverage-advantages-sabotages.md` (8+ links).
   Also: `docs/decisions/0002-harness-scenario-execution-contract.md` contains
   absolute Windows paths (`/C:/Users/nicke/...`) instead of repo-relative links.
   Also: `docs/roadmap/epics/M5-C-second-arc-schema-validation.md` links to
   `../tasks/AW-256-remove-beat-id-hardcode-from-arc-transition-gate.md` which
   may have been renamed.

   Run a COMPLETE relative-link scan across `docs/` EXCLUDING
   `docs/archive/notion-export/` (non-canonical per AGENTS.md; its broken links
   are expected export artifacts — do not fix them). Fix only links where the
   correct target is unambiguous. List ambiguous ones for me; do not guess.

2. `docs/skills/arcwright-minigame/SKILL.md` frontmatter cites "the engine
   boundary from ADR 0009." Confirm ADR-0009 is superseded by ADR-0018. If so,
   update the skill to match what ADR-0018 actually says — read it first, don't
   just swap the number. Report other stale ADR-0009 references.

3. WORKTREES. `git worktree list` shows 9 registered, several abandoned under
   `.claude/worktrees/` with directories already deleted. Per AGENTS.md do NOT
   delete anything in `.claude/` yourself. Report per worktree: branch, last
   commit date, whether commits are ancestors of main (`git merge-base
   --is-ancestor`), and whether the directory still exists. Note that
   `docs/aw-290-planning`, `feat/aw-271-obligations`,
   `feat/live-loop-ai-dialogue`, and `codex/minigame-platform-planning` all hold
   UNMERGED commits — flag those as must-not-prune until reviewed. Give me a
   prune command with per-worktree safety assessment.

PR for items 1 and 2. Item 3 is a report. STOP before merge.
```

**Note on GitHub issue links:** issue and PR bodies in this repo reference docs as
bare backticked paths (`` `docs/architecture/03-arc-execution.md` ``), which
GitHub does not render as links. That is the existing convention, not a
regression. GitHub also does not resolve repo-relative markdown links inside
issue bodies. To make a doc clickable from an issue, use a full
`https://github.com/nickejanssen/arcwright/blob/main/<path>` URL.

---

## D2 — Mini-game program greenlight

**Opus** · `arcwright-sme`, `/scribe` · ~30 min

```
Invoke the `arcwright-sme` skill — this is an architecture-overlap judgment.

Read `docs/product/road-to-live/status.md` first.

The mini-game readiness program is capped at the browser golden path (PR #275,
specs 0077-0080). Further slices need my execution approval. Frame that decision.

Read specs 0077-0080, ADR-0018, `docs/specs/0086-scene-sweep-game-ready.md`, and
`docs/superpowers/plans/2026-08-03-scene-sweep-game-ready.md`. Use Explore to
locate; read the decisive ones yourself.

Tell me, with file-path evidence:
- What the next slice delivers, and its process overhead (that program runs heavy
  — multiple specs, worktrees, audit trails).
- Whether it OVERLAPS with AW-286 (remaining six-beat integration, privacy and
  device checks, polish). Name the specific surfaces, schemas, and components
  that collide.
- Whether the game-ready plan's dependencies (capability-and-trust platform,
  creator-and-readiness-labs) exist yet. Verify. Assume nothing.
- What the roadmap costs if I defer the whole program until after Rehearsal 1.

ONE AskUserQuestion, bounded options, your pick marked. Do not hedge across
options. After I answer, `/scribe` the decision into
`docs/product/decisions-log.csv` plus an ADR if it affects sequencing or
architecture. STOP.
```

---

## P4 — AW-291: the line reader

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
  it does not paraphrase.

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

## P5 — Mystery loop discovery

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
`docs/superpowers/specs/` with a "Locked design decisions" section, following the
format of `2026-08-02-nightcap-scene-sweep-mini-game-design.md`. Get my explicit
approval, commit, STOP.
```

---

## P6 — Mystery loop plan

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
criteria (private info never reaches the shared display).

Produce the plan and `.tasks.json`. Present for approval. STOP.
```

---

## R1 — Execute (reusable; once per task, fresh session)

**Sonnet** · `subagent-driven-development`, `test-driven-development`, `using-git-worktrees`

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

## R2 — Closeout (reusable; once per branch)

**Opus** · `requesting-code-review`, `receiving-code-review`, `finishing-a-development-branch`, `/review-pr`, `/scribe`

```
Close out `<branch>` for `<AW-NNN>` / issue `<#NN>`.

1. `superpowers-extended-cc:requesting-code-review`, then `/review-pr` for the
   repo's own checklist. Report findings; do not silently fix.
2. `superpowers-extended-cc:receiving-code-review` to address them. New commits,
   never amend.
3. Confirm every acceptance criterion passes with evidence, and that CI's required
   `verify` check is green — read the actual GitHub Actions log, not local runs
   only.
4. Open the PR with `Closes: #NN`. STOP before merge — I merge.

After I merge: `superpowers-extended-cc:finishing-a-development-branch`. Verify
the squash preserved content (`git diff <base>..<head> -- <paths>` empty) before
deleting anything. Then `/scribe` to update the task file Status with Closeout
Evidence in the style of AW-282/283/284, and update
`docs/product/road-to-live/status.md`.

Then remind me to run `make rehearsal` on real hardware.
```

For high-stakes PRs the founder runs `/code-review ultra` — multi-agent cloud
review, billed, founder-triggered only.

---

## D1 — AW-289 brief (defer until Stage 3 is next)

**Opus**

```
Frame the AW-289 Interrogation Room creative brief decision. Read the AW-289 task
file and any existing brief or discovery record. Do NOT write a new brief.

Tell me: what specifically needs my approval, what each option costs, what stays
blocked while it's unapproved, and what happens if I defer past Rehearsal 1.

ONE AskUserQuestion, your pick marked. STOP.
```

---

## Cost discipline

- **Sonnet** for P0, P1, P2, R1 — mechanical, evidence-gathering, execution.
- **Opus** for D1, D2, P4, P5, P6, R2 — judgment, creative gates, review.
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

- `docs/conventions/human-collaboration.md` — interaction profiles and gates
- `docs/agents/USAGE.md` — role contracts and operating model
- `docs/product/road-to-live/status.md` — current verified state (written by P1)
- `AGENTS.md` — always-on rules, Hard Rules requiring explicit approval
