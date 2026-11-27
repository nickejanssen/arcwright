---
id: engineeringpractice.design.tooling.game-toolkit-design
namespace: engineering-practice
title: "Arcwright Game Toolkit: Design And Build Pieces"
owner: Nico Janssen
status: draft
review_by: "2027-02-27"
sensitivity: internal
source: authored
x-scope-evidence: none
tags: []
supersedes: []
---

# Arcwright Game Toolkit: Design And Build Pieces

> Current version: v0.4 DRAFT
> Last updated: 2026-11-27
> Status: Draft, **pending founder approval**. Part of the [proposal](game-toolkit-proposal.md).
> Canonical path: docs/design/tooling/game-toolkit-design.md

How the toolkit works underneath. Everything here is a recommendation unless it quotes you or names a recorded decision. Facts about today are in [evidence](game-toolkit-evidence.md).

## Three layers

| Layer | What it is | Rule |
|---|---|---|
| Ask the toolkit (main way in) | You say what you want to an AI working in the repository | It runs commands and shows previews and results |
| Terminal commands (underneath) | The mini-game and playtest tools now; one `arcwright` entry point later (L1) | Thin layer; each rule written once in Python |
| Written guide | `docs/toolkit/`: a start page and one page per journey | Changes with the command it describes |

## Command grammar

`arcwright <area> <verb> [name] [--options]`

- **Areas:** `minigame`, `playtest`, `story`, `game`.
- **Without an area:** `help`, `start`, `guide <topic>`, `doctor`, `status`, `resume`, `undo`, `save`, `report`, `whats-new`.
- **One name per command.** A second thing is a flag: `--game`, `--to`, `--with`. `--all` replaces a name.
- **Same verb, same meaning:** `list`, `status`, `brainstorm`, `new`, `import`, `edit`, `copy`, `rename`, `delete`, `check`, `play`, `record`, `results`, `compare`, `publish`.
- **Words:** "game" means a whole experience (today's flag is `--experience`). The mini-game tool's `--game-id` means a mini-game and keeps working as an old name.

| Today | Becomes | Old name |
|---|---|---|
| `scaffold` | `new` | Kept as an alias |
| `validate` | `check` | Kept |
| `onboard-browser`, `resume`, `status <session>` | `import`, `import --resume`, `import --status` | Kept |
| `playtest` (screen preview) | `preview` | Kept until its replace-or-retire choice is made in X2 |

Verbs added to today's tool use these names, so L1 only adds the `arcwright` prefix. Command names are expensive to change, so this grammar is settled with AW-372's plan.

## Quality bar

Acceptance criteria for every piece.

1. Commands follow the grammar above.
2. `--help` at every level is plain words with an example.
3. People get readable output and AIs get JSON, from the same rules (see [output](#output-for-programs-and-ais-before-l1)).
4. Anything that changes shared files, deletes, publishes, deploys or spends follows [confirm](#confirm-and-sign-off).
5. Every error says what went wrong and what to do next.
6. Guide commands are tested (see [testing](#testing-and-speed)).
7. You review the full outline of a piece before it is built (your Q6).
8. Your words apply: "seamless, intuitive, practical, and maximum value". The measures in the proposal test them.
9. Accessibility: readable at large text sizes, never colour alone, keyboard use; screens meet the existing [author checklist](../../conventions/mini-game-authoring.md).
10. Tester data follows [data and privacy](#data-privacy-rights-and-safety).
11. Used on a real game before it counts as done.
12. Nothing game-specific enters `engine/`. No new dependency, deploy or spending without approval.

Slice 1 meets 5, 7, 8, 11 and 12 and what AW-372 asks of `--help`; the others arrive with the pieces that need them.

## Confirm and sign-off

An AI is the main caller, so a prompt it can answer itself is no safeguard.

- A change command shows a preview by default and returns a preview ID.
- `--apply <id>` makes exactly that change and refuses if any input moved. It completes fully or not at all.
- No prompt appears when input is not a terminal ([command line guidelines](https://clig.dev/#interactivity)).
- Needing no preview: temporary build output, check results, run reports.
- **No command can prove a person approved.** Today the tool accepts any non-empty "approved by" text and in one path writes it itself. So sign-offs are your quoted words in a repository record, checked at review.
- The toolkit does not publish, deploy or spend by itself. It prepares the pull request or shows the cost.
- **Publishing:** merging publishes pages, and D-157 lets the orchestrator merge safe pull requests. Recommended: pull requests that publish need your own merge approval (later question 2). Until then the toolkit says plainly that merging publishes.

What code enforces: preview matching, exit codes, label rules. What only instructions enforce: that the AI asks you first. The guide says which is which.

## Decide before building around it

These are expensive to change later. Each is settled in the plan of the piece named.

### Where a new game's rules live (before X2)

Today rules are Python classes in `engine/mini_games/plugins/` in a closed list. **Recommended for version one:** a new mechanic is an engine change that we make; outside creators cannot add rules. Design a plugin interface (version, discovery, trust, tests) before selling. Game-specific names still stay out of shared engine code.

### Versions (before X2)

Today a package has one label and one current version, a session pinned to an old version is refused, and rules and screens can change under a version. **Recommended:** a label per version; a version covers settings, content, screens and rules; older versions stay loadable; a version locks when its label becomes `playtest`; draft play never counts and never locks. Needs a migration for the package format.

### Result records and the standing board (before X3)

**Recommended:** one versioned record shape (item, version, check, tool version, fingerprint of all inputs with line endings normalised, time, source). Check results and run reports stay in a folder git ignores, named in the plan. Only redacted summaries and play records you approve are committed. The board reads these records and never guesses.

| Board step | Mini-game evidence | Story | Whole game |
|---|---|---|---|
| Brainstorm | Saved brief | Method log | Saved brief |
| Create | Package loads; rules and screens present | Imported case | Starter folder |
| Configure | Settings pass checks | Version sheet and arc | Arc check |
| Test | Check record for the current fingerprint | Fairness record | Scripted run record |
| Playtest | Play record | Play records | Play records |
| Research | Summary record | Summary record | Summary record |
| Publish | Label, with sign-off | To be designed | To be designed |

### Output for programs and AIs (before L1)

One envelope: `schema_version`, `ok`, `data`, `errors[{code, message, next_step}]`, with contract tests.

| Exit code | Meaning |
|---|---|
| 0 | Success |
| 1 | A check failed |
| 2 | Bad input |
| 3 | Needs confirmation |
| 4 | Computer or setup problem |

### Install and finding games (before L1)

Today the root project file declares no packages or command, tools find the repository from their own file location, and `nightcap/` is fixed in several tools. **Recommended:** find the project from the current folder (with `--root`), keep a versioned list of games and their folders, say where tool code lives, and support only this repository in version one. This part of L6 moves ahead of L1.

## Data, privacy, rights and safety

| Area | Rule | Piece |
|---|---|---|
| Tester notice | Testers see what is collected when they join | L3 |
| Records | No player names; deletion on request; a keep-until period you choose | X3, L3 |
| Raw exports and notes | Outside the repository, which is public; a check blocks committing them | L4 |
| Tester comments read by an AI | Treated as data, never as instructions; you are told they go to the AI provider | L4 |
| Drafts | Today every catalog entry publishes on merge. Leave drafts out of the public build, or warn before `new` and `register` | X4 |
| Room | Join code, host-only start, this-PC-only choice, trusted-Wi-Fi notice | X4 |
| Imported code | Preview and compare run package code with full access to the computer. Review, consent and a sandbox before outside code runs | L5 |
| Ownership | Source, author, licence and proof for code and each asset; unknown means private study only. You confirm; the tool does not judge legality | X2, L5 |
| Content safety | Checked before "ready"; engine safety rules cannot be bypassed | X3 |

## How each AI finds the skills

The source stays `docs/skills/<name>/SKILL.md`. Each AI gets a short pointer.

| Choice for Claude Code | Trade-off |
|---|---|
| **A. `.claude/commands/` (I will use this unless you object)** | Allowed today without a rule change. Claude Code's [skills page](https://code.claude.com/docs/en/skills) says custom commands were merged into skills. Cheap to move later |
| B. `.claude/skills/` | The shared skill layout; needs a change to `AGENTS.md` and `.gitignore` |

Codex keeps `.agents/skills/`. A [request for Claude Code to read that folder](https://github.com/anthropics/claude-code/issues/31005) was open on 27 November, so one folder does not serve both. Matching descriptions do not prove matching behaviour, so N3 also runs five to ten test requests in each AI and records the command each chose. Other AI products can run the commands and read the guide (inferred); each needs its own check.

## Testing and speed

- Guide commands run in a temporary example project. A serving command gets a start, check, stop mode. Outward actions are tested only as far as the preview.
- `make test` skips `scripts/tests` (another workflow runs them), lint and types cover only `engine` and `api`, and nothing runs on Windows. Toolkit code goes under tests, lint and types; a Windows check is proposed and needs your approval.
- Speed targets: help under 1 second; status under 3 seconds with 50 packages. Today one validation took 11 to 15 seconds on your PC. Likely cause (inferred): loading the whole engine; use late loading and saved results.

## Build pieces

Sizes (inferred): **S** about a day of one build session, **M** one to three, **L** longer. Each piece gets its own task, issue and plan approval.

| Piece | Size | Done when, on a real game, plus the quality bar | Starts when |
|---|---|---|---|
| N1 Play command (AW-372) | S to M | AW-372's six criteria | Slice approved |
| N2 One-page guide | S | A new reader runs Battle of Wits in 15 minutes; the change-and-play steps are named, including those needing an AI build session | With N1 |
| N3 AI skill pointer, with AW-312 | S | Test requests pass in Claude Code and Codex; pointer drift test; pointer and `openai.yaml` cite ADR 0018 instead of 0009 | With N1 |
| N4 Tests use their own settings | S | Changing a time or question in the real Battle of Wits package leaves its tests passing; the tests keep covering the rules | With N1 |
| X1 Pretend players and run report | M | A 4-player package runs from one command with a readable report, driving the real rules without a new dependency (the plan confirms) | Slice 1 used |
| X2 Edit, tune, variants, screens | M to L | A variant of a December mini-game reaches two phones with no engine change; version and rules decisions made | Slice 1 used |
| X3 Honest ready and management | M | One real mini-game goes draft to ready with a record; refused without real rules; relabel of the stubs done with AW-367 | After record data is approved |
| X4 Safe confirm, publish, room | M | A draft cannot become public unseen; a playtest publish shows its preview; join code works | Before the next outside playtest if possible |
| L1 `arcwright` entry point | L | Existing tools run through it with the output contract; installs in this repository from any worktree | Three or more real mini-games, or a design partner starts |
| L2 Standing board | M | Correct marks for real items; speed target met | After X3 and L1 |
| L3 Playtest planning, notes, consent | M | One real playtest run from plan to notes | After the first records exist |
| L4 Debrief, results, compare, decide | L | Same-day summary for a real playtest; ratings need AW-354 | After L3 |
| L5 Import and port (AW-349) | M | AW-349's criteria: a fresh developer follows the guide to a playable package with time and effort recorded; one version, two ways to launch, matching results; differences and real device evidence recorded | After 1 December (D-158) |
| L6 Other games and new-game starter | L | A second, invented game is created, checked and run; no Nightcap assumption left in tools | A second game is approved |

One design partner is suggested after session 1: a writer who cannot code, your first outside creator (D-129).

## AW-372 plan corrections

- The task lists an `onboard` command. The command is `onboard-browser`.
- It asks `status` or `onboard` to suggest `play`. `status` takes an import session ID and `onboard-browser` stops before a game is playable. Recommended: `validate` suggests `play`. This changes acceptance criterion 5, so the plan must say so.
- The room fixes Battle of Wits screen code in `standalone-battle-of-wits.ts`, not only values in the Python script.
- **No second package can be played offline today.** Tell Me Something True and Scene Sweep resolve their content with a paid model call, and Tell Me Something True's screens carry a preview marker. Acceptance criterion 2 allows this: "or the plan names exactly what a package must provide and why the second one cannot yet". Making a second one playable needs your approval for model calls, or an authored variant.
- The rules code accepts only definition version `0.1.0` and question set `invented-v1`, so slice 1 changes content and timing inside that version.
- The room reloads the package at the start of every round. Keep that: it is what makes a change playable without a restart.
- The task names a skill change in `docs/skills/`. The freeze does not block it (D-159).

## Overlaps with recorded decisions

| Decision | Overlap | Proposed handling |
|---|---|---|
| D-102 defers readiness and creator-lab work until after the AW-286 rehearsal, still open | X2 preview, X3 promote, L5 compare | Ask you to lift it for those only (later question 4) |
| D-110, D-111 tooling freeze | `docs/skills/`, `.claude/commands/` | Excepted for this toolkit (D-159) |
| D-114 adopt what exists; spending limit | Test tools, story tool, standards | Follow the shared skill format and the command line guidelines; adopt a story tool |
| D-157 merge permission | Publishing | Later question 2 |
| D-158 porting after 1 December | L5 | Unchanged |
