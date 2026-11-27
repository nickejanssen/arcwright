---
id: engineeringpractice.design.tooling.game-toolkit-proposal
namespace: engineering-practice
title: "Arcwright Game Toolkit: Inventory, Journeys And Draft Proposal"
owner: Nico Janssen
status: draft
review_by: "2027-02-27"
sensitivity: internal
source: authored
x-scope-evidence: none
tags: []
supersedes: []
---

# Arcwright Game Toolkit: Inventory, Journeys And Draft Proposal

> Current version: v0.1 DRAFT
> Last updated: 2026-11-27
> Status: Draft, **pending founder approval**. Nothing here is approved build scope.
> Canonical path: docs/design/tooling/game-toolkit-proposal.md
> Task: AW-373, [issue #523](https://github.com/nickejanssen/arcwright/issues/523), steps 1 and 2. The task record arrives with [pull request #524](https://github.com/nickejanssen/arcwright/pull/524).

## The short answer

- **Mini-games are furthest along.** You can create and check a package. One game (Battle of Wits) can be played on phones over Wi-Fi. There is no general "play this game" command.
- **Playtest pages are well covered** for building and publishing. Turning what testers did into findings is mostly manual.
- **Stories have a fairness checker and early writing guides**, but no guided way to start, no blank starting file and no publish step.
- **Making a whole new game has no tool.** Several tools only look in the Nightcap folders.
- **The Codex "copies" are short pointers, on purpose.** The task record calls this drift. The real drift is small: some descriptions differ and one still cites a replaced decision record. The bigger problem is that Claude Code has no pointers at all.
- **Recommendation:** one front door that you ask in plain words, one start page, one source for every skill, and small build pieces starting with AW-372. No new all-in-one program.

## How to read this

| Word | Meaning |
|---|---|
| **Built** | A tool or written procedure for the step exists. This does not mean anyone has used it in a real game. |
| **Partly** | Something exists, but it covers only some cases or needs hand work. |
| **Missing** | No tool or procedure was found. |
| **Verified** | Read in the file, or run, on 27 November 2026 at `main` commit `848bed6`. |
| **Inferred** | A conclusion drawn from what was read. Not directly proven. |

**Run on 27 November:** `pytest engine/tests/test_minigame_tool.py scripts/tests/test_playtest_tool.py scripts/tests/test_playtest_skill_contract.py` (26 passed); `playtest_tool.py --json validate` (ok) and `list`; `minigame_tool.py validate` on all six package folders under `nightcap/mini_games/` other than `_fixtures` (all load); `--help` for the tool commands and the case checker.

**Not run:** the Wi-Fi room, `scaffold`, `onboard-browser`, the preview command, the rehearsal stack, any dashboard test, anything on a TV or phone. Nothing was observed in Codex. No file under `nightcap/cases/` was opened.

## Part 1: Inventory

### Skills (instructions an AI agent follows)

| Skill | Source | What it covers | Codex pointer | Claude Code |
|---|---|---|---|---|
| Mini-game | [`docs/skills/arcwright-minigame/SKILL.md`](../../skills/arcwright-minigame/SKILL.md) (450 lines), `scripts/minigame_tool.py`, `agents/openai.yaml` | Design intake, scaffold or import, validate, fit-check, test, promote | `.agents/skills/arcwright-minigame/` | none |
| Playtest steward | [`docs/skills/arcwright-playtest-steward/SKILL.md`](../../skills/arcwright-playtest-steward/SKILL.md) | Front desk for Playtest Lab work; routes to the three below | `.agents/skills/arcwright-playtest-steward/` | none |
| Playtest harness | [`docs/skills/arcwright-playtest-harness/SKILL.md`](../../skills/arcwright-playtest-harness/SKILL.md) | Checks a test page before testers use it | `.agents/skills/arcwright-playtest-harness/` | none |
| Playtest research | [`docs/skills/arcwright-playtest-research/SKILL.md`](../../skills/arcwright-playtest-research/SKILL.md) | Survey versions, tester feedback, evidence limits | `.agents/skills/arcwright-playtest-research/` | none |
| Playtest publishing | [`docs/skills/arcwright-playtest-publishing/SKILL.md`](../../skills/arcwright-playtest-publishing/SKILL.md) | Catalogue, site build, archive, public pages | `.agents/skills/arcwright-playtest-publishing/` | none |

Claude Code: `.claude/commands/` holds only `doc-review`, `implement`, `review-pr` and `scribe`, and there is no `.claude/skills/` folder (verified). None of the five skills appeared in this Claude session's skill list (verified). The `playtest-ops-sme` and `nightcap-sme` helpers in `.claude/agents/` answer questions from documents; they do not run these workflows.

### Exactly how the two copies differ

- Each `.agents/skills/<name>/SKILL.md` is 8 or 9 lines: a name, a description and "read the file under `docs/skills/`". [`.agents/skills/README.md`](../../../.agents/skills/README.md) says this is deliberate, to prevent drift. So the missing `scripts/` and `agents/` folders are expected (verified).
- All five pointers have the right name and point to the right source (verified).
- **Mini-game description differs:** the pointer cites decision record ADR 0009. The source cites ADR 0018, which replaced it. The pointer was last changed 22 June 2026; the source on 18 November 2026.
- **All four playtest descriptions differ:** pointers say "Use when ...", sources describe what the skill does. Both read as correct, but nothing keeps them in step.
- [`scripts/tests/test_playtest_skill_contract.py`](../../../scripts/tests/test_playtest_skill_contract.py) checks that the four playtest pointers stay short. It does not compare descriptions, and it does not cover the mini-game skill.
- `docs/skills/arcwright-minigame/agents/openai.yaml` still cites ADR 0009 and the archived "story bible". The playtest skills have no `openai.yaml`.
- The other pointers (`arcwright-reviewer`, `arcwright-sme`, `arcwright-doc-bundler`) match their sources.

### Mini-game tools

| Tool | What it does | Limits (verified) |
|---|---|---|
| `minigame_tool.py scaffold` | New package from `<experience>/mini_games/_template/` | Only Nightcap has a template folder |
| `minigame_tool.py validate` | Loads a package or catalogue through the engine | Catalogue mode loads only `active` packages |
| `minigame_tool.py onboard-browser`, `resume`, `status` | Imports a browser game into a private workspace and analyses it | Stops at "Imported". `status` takes an import session ID, not a package path |
| `minigame_tool.py playtest` | Runs [`playtest-mini-game.mjs`](../../../nightcap-web/scripts/playtest-mini-game.mjs) | A preview with scripted states, not the real rules; reads only Nightcap; default points at the superseded Couch Race design |
| [`scripts/play_battle_of_wits.py`](../../../scripts/play_battle_of_wits.py) with `dashboard/src/standalone-battle-of-wits.ts` | Real rules on phones over Wi-Fi, 1 to 8 players ([pull request #506](https://github.com/nickejanssen/arcwright/pull/506)) | Battle of Wits only: package, version, player limit and screen code are fixed in the code |
| [`discover-mini-games.mjs`](../../../nightcap-web/scripts/discover-mini-games.mjs), `dashboard/src/mini-games/registry-bindings.ts` | Find and bundle each package's screen code | Only `nightcap/mini_games/` |
| `engine/mini_games/` | Loader, rules runtime, privacy-safe views, import service | Five rule sets registered; two are empty stubs (below) |
| [`mini-game-authoring.md`](../../conventions/mini-game-authoring.md) | Author guide, mostly screen code | Out of date: names `engine/mini_games/schemas.py` (does not exist), points to `nightcap-web` and ADR 0009, never mentions the mini-game tool |
| [Idea bank](../../gdd/nightcap/04-supporting-design/minigame-idea-bank.md) | Ranked ideas with a first playtest question | Lives in Nightcap's design folder |

### Where each Nightcap mini-game package stands (verified)

| Package | Label | Real rules | Screen code | Could the Wi-Fi room play it? (inferred) |
|---|---|---|---|---|
| battle-of-wits | draft | yes | yes | Yes, today |
| tell-me-something-true | draft | yes | yes | Likely second game; 4 to 8 players |
| scene-sweep | draft | yes | none | Not until it has screen code |
| crime-scene-smash | **active** | **no, stub** | prototype page only | No |
| evidence-locker-402 | **active** | **no, stub** | prototype page only | No |

The two stubs raise "not implemented" when asked to resolve a game (`engine/mini_games/plugins/_match_3_clue_race.py`, `_evidence_locker_breach.py`), yet their packages are labelled ready for new sessions. The old Couch Race arc (`nightcap/couch-race.arc.json`) binds both, and `make rehearsal` starts that arc (verified in files; the failure in play is inferred, not run).

### Playtest tools

| Tool | What it does | Limits (verified) |
|---|---|---|
| [`scripts/playtest_tool.py`](../../../scripts/playtest_tool.py) | `list`, `validate`, `new`, `archive`, `build` | No command to make a draft the current test |
| `scripts/playtest_catalog.py`, `scripts/build_playtest_site.py`, `playtests/` | Catalogue checks and static test pages; three Nightcap entries (one archived, one current, one draft) | The site build needs a current Nightcap test and writes only Nightcap's game page |
| `.github/workflows/nightcap-playtest-pages.yml` | **Publishes the pages automatically** when matching files merge to `main`, including edits to playtest skills and their pointers | A merge is a publish |
| `scripts/rehearsal.py`, `rehearsal_start.py`, `rehearsal_smoke.py` (`make rehearsal`) | Starts the whole game stack locally | Always creates the old Couch Race game. [AW-367](https://github.com/nickejanssen/arcwright/issues/511) already covers this |
| `engine/telemetry/play_records.py` | Answers four questions from saved sessions, for any game | No command or web route found that shows the answers |
| `engine/harness/` | Scripted and batch runs of a session | A code library used by tests; no command found |

### Story and game tools

| Tool | What it does |
|---|---|
| `python -m engine.case.authored <case> --arc-id <id>` | Checks a written case is fair. The default summary shows counts only, so it avoids spoilers; `--full` does not |
| `engine/tests/fixtures/authored_case/valid_case.json` | An example case used by tests. No blank starting file for authors was found |
| [Writing for living stories](../authoring/writing-for-living-stories.md), [story to arc example](../authoring/story-to-arc-exemplar.md) | Draft craft guides, awaiting your review |
| [Case method logs](../authoring/case-method-logs/README.md) | One log per case of how it was written |
| `nightcap/case_skeletons/`, `engine/case/resolver.py` | Generated-case building blocks made for Couch Race |
| `config/arcs.json`, `nightcap/*.arc.json`, [version sheets](../session-1-variants/README.md) | How a game's rounds and versions are set up, edited by hand |
| `.github/workflows/deploy-api.yml`, `deploy-web.yml` | Deploy on merge to `main` when their folders change. Whether they succeed was not checked |

`scripts/roadmap_status.py`, `verify_tasks.py`, `team_ai_cli.py` and `scripts/checks/` serve development in general, so they are outside this toolkit (inferred).

### Related tasks (live status, 27 November)

| Task | Status | Relationship |
|---|---|---|
| [AW-312](https://github.com/nickejanssen/arcwright/issues/365) Map where agent and skill definitions live | open | Overlaps the one-source piece |
| [AW-322](https://github.com/nickejanssen/arcwright/issues/382) Prove a mini-game can be played on its own | open | Source of the preview and standalone gaps |
| [AW-348](https://github.com/nickejanssen/arcwright/issues/443) Play a mini-game with Nightcap offline | open on GitHub; narrowed to Battle of Wits and merged (D-158 calls it done) | AW-372 depends on it |
| [AW-349](https://github.com/nickejanssen/arcwright/issues/444) Port a browser game and reuse it | open; after 1 December (D-158) | The "port" step |
| [AW-372](https://github.com/nickejanssen/arcwright/issues/520) One play command | open; GitHub has no milestone, the task file says M7 | First build piece |
| [AW-367](https://github.com/nickejanssen/arcwright/issues/511) Safe one-command case start | open | Fixes the rehearsal default |
| [AW-354](https://github.com/nickejanssen/arcwright/issues/463) Ratings and version tags | open | Feeds playtest findings |
| [Spec 0052](../../specs/0052-arcwright-minigame-skill.md) Mini-game skill | done | Still describes ADR 0009 and an unbuilt runtime |
| [Spec 0080](../../specs/0080-mini-game-onboarding-preview-and-certification.md) Onboarding, local lab, certification | approved; later work deferred by D-102 ([ADR 0021](../../decisions/0021-minigame-readiness-program-deferred-until-after-rehearsal-1.md)) | This proposal does not restart it |

## Part 2: Journeys

### Mini-game

| Step | State | What exists, and the gap | Evidence | Label |
|---|---|---|---|---|
| Brainstorm | Partly | Idea bank and a design interview in the skill; both aimed at Nightcap | idea bank; skill Phase 0 | Verified |
| Create | Partly | Package scaffold exists. New rules need engine code, with no guide for writing it | `minigame_tool.py`; `engine/mini_games/plugins/` | Scaffold verified; guide gap inferred |
| Port | Partly | Import and analysis only; adapting is by hand, unproven | skill capability list; AW-349 | Verified |
| Configure | Partly | Hand-edit the definition, then validate | `definitions/<version>.json` | Verified |
| Test | Built | Validate plus automated tests | tool; `engine/tests/` | Verified |
| Playtest | Partly | One game live; preview for others | `play_battle_of_wits.py` | Verified in code, not run |
| Research | Missing | No way to save or compare results of standalone rounds; the room forgets them when stopped | script docstring and code | Inferred |
| Publish | Partly | Promotion is a hand edit of the label and the arc file; nothing checks that a ready game has real rules | skill Phase 5; stub finding | Verified |

### Story (a case)

| Step | State | What exists, and the gap | Evidence | Label |
|---|---|---|---|---|
| Brainstorm | Partly | One case's method log; no guided session | `case-method-logs/` | Verified |
| Create | Partly | Draft craft guides and an agreed file format; no blank starting file | spec 0093 Part A; test example | Verified; search for a blank file was limited |
| Port | Missing | Converting a prose draft into the format is hand work | AW-305 scope | Inferred |
| Configure | Partly | Version sheets and arc files, edited by hand | `docs/design/session-1-variants/` | Verified |
| Test | Built | Fairness check with spoiler-safe summary | `engine/case/authored/` | Verified in code; not run on a case |
| Playtest | Partly | Local stack and manual steps; wrong default game | AW-367 | Verified |
| Research | Partly | Play records are saved; no report command | `play_records.py` | Verified by search |
| Publish | Missing | No step for releasing a story to players | search | Inferred |

### Game (a whole experience)

| Step | State | What exists, and the gap | Evidence | Label |
|---|---|---|---|---|
| Brainstorm | Missing | Nothing in the repository for a new game | search | Inferred |
| Create | Missing | No starter folder; register by hand in `config/arcs.json` | `config/arcs.json` | Inferred |
| Port | Missing | Nothing | search | Inferred |
| Configure | Partly | Arc files are checked when loaded; no command to check one on its own | `engine/arc/` | Verified by search |
| Test | Partly | Automated tests and a scripted-run library, set up by developers | `engine/harness/` | Verified |
| Playtest | Partly | Playtest Lab pages and a local stack, both leaning on Nightcap | tables above | Verified |
| Research | Partly | Survey and feedback procedure; reading results is manual | research skill; no survey reader found | Verified by search |
| Publish | Partly | Test pages publish on merge; server and web deploy on merge; no game release checklist | workflows | Verified in config; results not checked |

## Part 3: Draft proposal

Everything below is a recommendation waiting for your decision.

### 1. One front door

| Option | What you would do | Trade-off |
|---|---|---|
| **A. Ask the toolkit (recommended)** | Type `/toolkit` in Claude Code, or ask Codex for the Arcwright toolkit, and say what you want to make or test. It names the next step, runs the right tool and says what it cannot do yet. A start page lists the same map for reading | Smallest build; reuses what exists |
| B. One new terminal program | Type commands such as `arcwright play` | More code to maintain, and you would need to remember commands |
| C. A written guide only | Read, then run tools yourself | Cheapest, but agents still would not offer the tools |

Behind `/toolkit` sit two more commands, `/minigame` and `/playtest`. The playtest steward already routes to the other three playtest skills, so `/playtest` needs no new logic. A `/story` command follows when the story piece is built.

### 2. Guide set

A new folder, `docs/toolkit/`, each guide one or two pages, with commands that were run when written:

| Guide | Contents |
|---|---|
| Start here | What you want to do, then the command and the guide; what does not work yet |
| Make a mini-game | Brainstorm to publish. Replaces the out-of-date parts of the current author guide, which keeps the screen-code reference |
| Make a story | Brainstorm, write, check without spoilers, try it |
| Playtest and learn | Set up, run, collect, read results, decide |
| Make a game | Written only once the new-game piece exists |

Each fact lives in one place: guides tell a person what to do, skills tell an agent how, and both link instead of repeating.

### 3. One source for Claude Code and Codex

The source stays `docs/skills/<name>/SKILL.md`. Each agent gets a short pointer.

| Option | Trade-off |
|---|---|
| **A. Claude commands plus the existing Codex pointers, checked by a test (recommended)** | `.claude/commands/*.md` is already an allowed tracked path, and this session lists those commands as skills Claude can pick up. The test fails if a pointer's description or target differs from its source |
| B. Claude pointers in `.claude/skills/` | Mirrors Codex exactly, but needs a change to `AGENTS.md` and `.gitignore` |
| C. Generate pointers with a script | No hand editing, but more machinery for a handful of 8-line files |

### 4. Build pieces, in order

Sizes (inferred): **S** about a day of one build session, **M** one to three, **L** longer. Each piece gets its own task, issue and plan approval **after** this proposal is approved. Builds start after the 1 December test (AW-373 task record, which cites D-156).

| # | Piece | Size | Done when |
|---|---|---|---|
| 1 | **AW-372**: `minigame_tool.py play <package>` | S to M | Battle of Wits and one more game start with the same command; a package that cannot play says why in one line |
| 2 | One source for both agents: Claude commands, drift test, ADR 0018 text fixed. Do with AW-312 | S | Both agents offer the skills; the test catches a changed description |
| 3 | Front door and start-here guide | S | You can say what you want and get the right next step |
| 4 | Mini-game guide and honest labels: refresh the guide, brainstorm prompts, stop a game without rules being marked ready, settle the old preview command | S | Guide commands run as written; a check fails on a ready package with stub rules |
| 5 | **AW-349** (already filed): port one browser game | M | Port time measured and written into the guide |
| 6 | Story kit: guide, blank starting case, check and scripted play-through in one command | M | A made-up case goes from blank file to passing check by following the guide |
| 7 | Playtest results report from play records and survey answers (after AW-354) | M | One command gives a spoiler-safe summary by game and version |
| 8 | Remove Nightcap-only assumptions from the tools (package discovery, scaffold, preview, site build) | M | An invented second game passes the same steps |
| 9 | New-game starter and arc check command, then the game guide | M to L | A made-up game is created, checked and run headless |

**AW-372 plan notes (verified):** the task says `status` or `onboard` should suggest `play`, but the command is `onboard-browser` and `status` takes an import session ID, so the plan must say where the suggestion appears. The room also fixes Battle of Wits screen code in `standalone-battle-of-wits.ts`, not only values in the Python script. Tell Me Something True is the only other package with both real rules and screen code.

**Rules for every piece:** nothing game-specific enters `engine/`; no new dependency, deploy or spending without approval; no editor with menus and no restart of the deferred spec 0080 program unless you decide that.

## Open questions for your interview

One at a time. Each is yours because it turns on priority or taste.

| # | Question | Recommendation |
|---|---|---|
| Q1 | After the play command, what matters most? | Mini-games, then stories, then playtest results, then whole new games. This follows your D-156 wish to improve story technology once playtesting can start (inferred reading) |
| Q2 | Is "ask the toolkit in plain words" the front door you want? | Yes, option A, with the start page |
| Q3 | In brainstorming and story writing, how much should the tools write? | They ask, offer options and check; you choose, and final story text stays yours |
| Q4 | Who is version one for, and what does "publish" mean? | You and your agents. Publish means playtest pages and marking something ready. Outside creators later |
| Q5 | Two games are labelled ready but have no rules. Relabel them as drafts? | Yes. Both are used only by the old Couch Race arc, so the same change must say what that arc does without them |

## What happens next

1. You answer the questions and approve, change or reject the proposal in your own words.
2. Each approved piece is filed as a task and GitHub issue.
3. Each build gets its own plan approval.
