---
id: engineeringpractice.design.tooling.game-toolkit-evidence
namespace: engineering-practice
title: "Arcwright Game Toolkit: Evidence"
owner: Nico Janssen
status: draft
review_by: "2027-02-27"
sensitivity: internal
source: authored
x-scope-evidence: none
tags: []
supersedes: []
---

# Arcwright Game Toolkit: Evidence

> Current version: v0.4 DRAFT
> Last updated: 2026-11-27
> Status: Draft. Supports the [proposal](game-toolkit-proposal.md).
> Canonical path: docs/design/tooling/game-toolkit-evidence.md

What exists today, how it was checked, and your exact words.

## How to read this

| Word | Meaning |
|---|---|
| **Built** | A tool or written procedure for the step exists. This does not mean anyone has used it in a real game. |
| **Partly** | Something exists, but it covers only some cases or needs hand work. |
| **Missing** | No tool or procedure was found. |
| **Verified** | Read in the file, or run, on 27 November 2026 at `main` commit `848bed6`; facts added in v0.4 at `4118aaa`. |
| **Inferred** | A conclusion drawn from what was read. Not directly proven. |

**Run on 27 November:** `pytest engine/tests/test_minigame_tool.py scripts/tests/test_playtest_tool.py scripts/tests/test_playtest_skill_contract.py` (26 passed); `playtest_tool.py --json validate` (ok) and `list`; `minigame_tool.py validate` on all six package folders under `nightcap/mini_games/` other than `_fixtures` (all load); `--help` for the tool commands and the case checker.

**Run for v0.4:** `engine/tests/test_battle_of_wits.py` with one changed timing, described below.

**Not run:** the Wi-Fi room, `scaffold`, `onboard-browser`, the preview command, the rehearsal stack, any dashboard test, anything on a TV or phone. Nothing was observed in Codex. No file under `nightcap/cases/` was opened.

## Inventory

### Skills (instructions an AI agent follows)

| Skill | Source | What it covers | Codex pointer | Claude Code |
|---|---|---|---|---|
| Mini-game | [`docs/skills/arcwright-minigame/SKILL.md`](../../skills/arcwright-minigame/SKILL.md) (450 lines), [`docs/skills/arcwright-minigame/scripts/minigame_tool.py`](../../skills/arcwright-minigame/scripts/minigame_tool.py), `agents/openai.yaml` | Design intake, scaffold or import, validate, fit-check, test, promote | `.agents/skills/arcwright-minigame/` | none |
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
- `arcwright-sme` also differs (the pointer drops the list of trigger phrases), and so does `github-task-implementer` (shorter than its source). `arcwright-reviewer` and `arcwright-doc-bundler` showed no difference in the part compared.

### Mini-game tools

`minigame_tool.py` below means `docs/skills/arcwright-minigame/scripts/minigame_tool.py`.

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
| tell-me-something-true | draft | yes | yes | Not offline: needs a paid model call; screens carry a preview marker; 4 to 8 players |
| scene-sweep | draft | yes | none | Not until it has screen code; also needs a model call |
| crime-scene-smash | **active** | **no, stub** | prototype page only | No |
| evidence-locker-402 | **active** | **no, stub** | prototype page only | No |

The two stubs raise "not implemented" when asked to resolve a game (`engine/mini_games/plugins/_match_3_clue_race.py`, `_evidence_locker_breach.py`), yet their packages are labelled ready for new sessions. Both `nightcap/arc.json` and the old Couch Race arc (`nightcap/couch-race.arc.json`) bind them, `make rehearsal` starts the Couch Race arc, and `engine/tests/test_mini_game_models.py` expects the active catalog to be exactly these two (verified in files; the failure in play is inferred, not run).

### More facts about mini-games (verified, added in v0.4)

| Fact | Where |
|---|---|
| `crime-scene-smash`, `scene-sweep` and `tell-me-something-true` are `hybrid`: resolving them calls a model. `battle-of-wits` and `evidence-locker-402` are `authored` | `nightcap/mini_games/*/definitions/`, `engine/mini_games/resolver.py` |
| Tell Me Something True's screens add a `NON_AUTHORITATIVE_PREVIEW` shell. Whether it shows visibly was not checked | its `client/renderer.ts` |
| Battle of Wits phase times are in `rules`; its three questions need 59 of the 65 second cap; too much is refused when the room starts a round. Rules accept only version `0.1.0` and question set `invented-v1` | definition, questions file, `engine/mini_games/plugins/_battle_of_wits.py` |
| Rules are Python classes in a closed list | `engine/mini_games/plugins/__init__.py` |
| One label and one current version per package; a session pinned to another version gets `version_mismatch`; unknown fields are refused | `engine/mini_games/models.py`, `loader.py`, `engine/session/mini_game_phase.py` |
| The room reloads the package at the start of each round, so an edit applies on Play again | `scripts/play_battle_of_wits.py`, `tests/test_play_battle_of_wits.py` |
| Changing `choice_seconds` from 12 to 15 made 9 of 17 tests in `engine/tests/test_battle_of_wits.py` fail. Run 27 November, then restored. Other test files were not tried with the change | the test run |
| Version 1a binds draft Battle of Wits five times | `nightcap/agency-race-1a.arc.json` |
| A definition may not be edited once it is labelled `playtest` | mini-game skill |
| Any non-empty "approved by" text is accepted; one path writes `interactive-user` | `minigame_tool.py` |
| The screen preview bundles a package's screen code and imports it in Node | `nightcap-web/scripts/playtest-mini-game.mjs` |
| The Wi-Fi room listens on all network interfaces over plain HTTP; joining needs a name only; any seated player can start | `scripts/play_battle_of_wits.py` |
| One `validate` run took about 11 to 15 seconds on this PC; the cause was not measured | timed twice |
| The author guide has an accessibility checklist and size budgets | [mini-game authoring](../../conventions/mini-game-authoring.md), sections 4 and 5 |

### Playtest tools

| Tool | What it does | Limits (verified) |
|---|---|---|
| [`scripts/playtest_tool.py`](../../../scripts/playtest_tool.py) | `list`, `validate`, `new`, `archive`, `build` | No command to make a draft the current test |
| `scripts/playtest_catalog.py`, `scripts/build_playtest_site.py`, `playtests/` | Catalogue checks and static test pages; three Nightcap entries (one archived, one current, one draft) | The site build needs a current Nightcap test, writes only Nightcap's game page, copies **every** catalog entry (drafts included) into the public site, deletes its output folder first, and links pages under `/arcwright/` |
| `.github/workflows/nightcap-playtest-pages.yml` | **Publishes the pages automatically** when matching files merge to `main`, including edits to playtest skills, their pointers and `scripts/tests/` | A merge is a publish. The repository is public |
| `scripts/rehearsal.py`, `rehearsal_start.py`, `rehearsal_smoke.py` (`make rehearsal`) | Starts the whole game stack locally | Always creates the old Couch Race game. [AW-367](https://github.com/nickejanssen/arcwright/issues/511) already covers this |
| `engine/telemetry/play_records.py` | Answers four questions from saved sessions, for any game | No command or web route found that shows the answers |
| `engine/harness/` | Scripted and batch runs of a session | A code library used by tests; no command found |

**Further facts (verified, added in v0.4).** `playtest_tool.py new` needs nine values. The root `pyproject.toml` declares no packages or command. `make test` does not run `scripts/tests` (the `team-ai` workflow does); lint and type checks cover `engine` and `api`; workflows run on Linux only.

### Story and game tools

| Tool | What it does |
|---|---|
| `python -m engine.case.authored <case> --arc-id <id>` | Checks a written case is fair. The default summary shows counts only, so it avoids spoilers; `--full` does not |
| `engine/tests/fixtures/authored_case/valid_case.json` | An example case used by tests. No blank starting file for authors was found in `engine/tests/fixtures/`, `scripts/` or `docs/design/` |
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
| [Spec 0080](../../specs/0080-mini-game-onboarding-preview-and-certification.md) Onboarding, local lab, certification | approved; later work deferred by D-102 ([ADR 0021](../../decisions/0021-minigame-readiness-program-deferred-until-after-rehearsal-1.md)) | Where this proposal comes close to it is listed in the [design page](game-toolkit-design.md#overlaps-with-recorded-decisions) |

## Journeys

### Mini-game journey

| Step | State | What exists, and the gap | Evidence | Label |
|---|---|---|---|---|
| Brainstorm | Partly | Idea bank and a design interview in the skill; both aimed at Nightcap | `docs/gdd/nightcap/04-supporting-design/minigame-idea-bank.md`; `docs/skills/arcwright-minigame/SKILL.md` Phase 0 | Verified |
| Create | Partly | Package scaffold exists. New rules need engine code, with no guide for writing it | `minigame_tool.py`; `engine/mini_games/plugins/` | Scaffold verified; guide gap inferred |
| Import | Partly | Import and analysis only; adapting is by hand, unproven | mini-game `SKILL.md`; `docs/roadmap/tasks/AW-349-*.md` | Verified |
| Configure | Partly | Hand-edit the definition, then validate | `definitions/<version>.json` | Verified |
| Test | Built | Validate plus automated tests | `minigame_tool.py`; `engine/tests/` | Verified |
| Playtest | Partly | One game live; preview for others | `scripts/play_battle_of_wits.py` | Verified in code, not run |
| Research | Missing | No way to save or compare results of standalone rounds; the room forgets them when stopped | `scripts/play_battle_of_wits.py` | Inferred |
| Publish | Partly | Promotion is a hand edit of the label and the arc file; nothing checks that a ready game has real rules | `docs/skills/arcwright-minigame/SKILL.md` Phase 5; package table above | Verified |

### Story (a case)

| Step | State | What exists, and the gap | Evidence | Label |
|---|---|---|---|---|
| Brainstorm | Partly | One case's method log; no guided session | `docs/design/authoring/case-method-logs/` | Verified |
| Create | Partly | Draft craft guides and an agreed file format; no blank starting file | `docs/specs/0093-*`; `engine/tests/fixtures/authored_case/valid_case.json` | Verified; search for a blank file was limited |
| Import | Missing | Converting a prose draft into the format is hand work | `docs/roadmap/tasks/AW-305-*.md` | Inferred |
| Configure | Partly | Version sheets and arc files, edited by hand | `docs/design/session-1-variants/` | Verified |
| Test | Built | Fairness check with spoiler-safe summary | `engine/case/authored/` | Verified in code; not run on a case |
| Playtest | Partly | Local stack and manual steps; wrong default game | `docs/roadmap/tasks/AW-367-*.md`; `scripts/rehearsal.py` | Verified |
| Research | Partly | Play records are saved; no report command | `engine/telemetry/play_records.py` | Verified by search of `engine/`, `api/`, `scripts/` |
| Publish | Missing | No step for releasing a story to players | none found in `scripts/` or `.github/workflows/` | Inferred |

### Game (a whole experience)

| Step | State | What exists, and the gap | Evidence | Label |
|---|---|---|---|---|
| Brainstorm | Missing | No new-game procedure found | `docs/skills/`, `scripts/` | Inferred |
| Create | Missing | No starter folder; register by hand in `config/arcs.json` | `config/arcs.json` | Inferred |
| Import | Missing | Nothing for a whole game | `docs/skills/`, `scripts/` | Inferred |
| Configure | Partly | Arc files are checked when loaded; no command to check one on its own | `engine/arc/` | Verified by search |
| Test | Partly | Automated tests and a scripted-run library, set up by developers | `engine/harness/` | Verified |
| Playtest | Partly | Playtest Lab pages and a local stack, both leaning on Nightcap | `playtests/`, `scripts/rehearsal.py`, `scripts/build_playtest_site.py` | Verified |
| Research | Partly | Survey and feedback procedure; reading results is manual | `docs/skills/arcwright-playtest-research/SKILL.md`; no survey reader in `scripts/` | Verified by search |
| Publish | Partly | Test pages publish on merge; server and web deploy on merge; no game release checklist | `.github/workflows/` | Verified in config; results not checked |

## Your answers, word for word

Quoted word for word from [issue #523](https://github.com/nickejanssen/arcwright/issues/523), 27 November 2026. "What it means here" is this proposal's reading.

| # | Question | Your words | What it means here |
|---|---|---|---|
| Q1 | After the play command, which piece comes first? | "Mini-games first" | Mini-game work before stories and whole games. Which pieces, and in what order, is a recommendation |
| Q2 | What is the front door? | "Written guide explains how to use the tool kit. Ask the toolkit is the main way through any AI. Having back up options through terminal is good considering the AI toolkit likely needs these for deterministic operation and the human can use it if that is there preference or if they want to customize their flows" | Three layers: guide, AI, terminal (inferred reading) |
| Q2 follow-up | One terminal entry point, or the separate tools? | "Im cool with one entry point, but make sure whatever direction this takes, it is the highest quality, the industry's best standards, what a billion dollar video game company would do at this stage, and makes for a seamless, intuitive, practical, and maximum value experience." | One entry point, a thin layer over existing tools. The quality bar applies to everything |
| Q3 | How much should the tools write? | "the tools ask, offer options and check, while final story text stays yours. That being said, the bar is the same: the highest quality, the industry's best standards, what a billion dollar video game company would do at this stage, and makes for a seamless, intuitive, practical, and maximum value experience. This should be easy to visualize too. IT should be extremely easy to understand as well." | No tool writes final story text. Pictures and plain examples are required |
| Q4 | Who is version one for? | "Just us right now, but this must be made availble once we start selling the engine. Thats why its important to build tools we love right now because others using arcwright to build will love them too. Also, we must build with scale in mind. I am relying on you to do a lot, but a lot if things under the hood are still lost on me. Dont cut corners now just because we are making this aviable to purchasers yet. It must be great for my use and I should love it so that when we sell our products, the customer has somethign that has been tested thoroughly and they can trust that I love the tools, dashboards, forms, CLI, AI plugins/skills/etc, and our documentaition is world class and makes it effortless to get started with Arcwright, fall in love with it, and want to use it with all of your games." | You and your AI helpers, built to a sellable standard and with scale in mind. Opening it to customers is intent, not yet approved scope |
| Q5 | Relabel the two "ready" games with stub rules as drafts, with AW-367? | "Yes, relabel" | `crime-scene-smash` and `evidence-locker-402` become drafts, together with [AW-367](https://github.com/nickejanssen/arcwright/issues/511). Its task file does not mention this yet. Both `nightcap/arc.json` and `nightcap/couch-race.arc.json` use them, and a test expects them in the active catalog, so that change must handle all three |
| Q6 | Start the story proposal right after this one is approved? | "Yes, right after. PLease outline everything we will be able to do with the story tools prior to building. Smae goes for any tools. I want to make sure the features are al availble and usable in the right way" | Story proposal follows approval. Every tool gets a full outline for your review before it is built |

A seventh statement, 27 November 2026, in the session reviewing pull request #525, recorded as D-159: "The freeze can be ignored as I am asking for this because it is making play testing and iterating more difficult"
