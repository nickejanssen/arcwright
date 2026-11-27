---
id: engineeringpractice.design.tooling.game-toolkit-outline
namespace: engineering-practice
title: "Arcwright Game Toolkit: Capability Outline"
owner: Nico Janssen
status: draft
review_by: "2027-02-27"
sensitivity: internal
source: authored
x-scope-evidence: none
tags: []
supersedes: []
---

# Arcwright Game Toolkit: Capability Outline

> Current version: v0.4 DRAFT
> Last updated: 2026-11-27
> Status: Draft, **pending founder approval**. Part of the [proposal](game-toolkit-proposal.md).
> Canonical path: docs/design/tooling/game-toolkit-outline.md

Everything you will be able to do. Listing a row here approves nothing.

## How to read it

- **When** gives the stage and piece: `N` now, `X` next, `L` later, `S` stories. **Idea** means no piece yet; each needs your approval.
- **Command** shows the final form. Nothing starting with `arcwright` exists. Until piece L1, a command is the same words after `python docs/skills/arcwright-minigame/scripts/minigame_tool.py` (or `scripts/playtest_tool.py`), without `arcwright minigame`.
- Names are invented: mini-games `lantern-dash` and `paper-kites`, story `orchard-case`, game `tidepool`.
- Every row also follows the [quality bar](game-toolkit-design.md#quality-bar).

## Start and get help

| When | You say to the AI | Command | You see | It checks or refuses |
|---|---|---|---|---|
| N2 | "How do I use this?" | `arcwright guide minigame` | One page: steps, examples, what does not work yet. In slice 1 you open the file or ask the AI | Examples are tested |
| N3 | "I want to change a mini-game" | None; you ask | The AI follows the skill, one question at a time | Changes nothing until you say yes |
| N3 | "Show me the command so I can run it" | Any | The exact command and what it changes | |
| L1 | "Get me started" | `arcwright start` | Checks the computer, plays a sample, shows a code to scan with a phone | Says what is missing and how to fix it |
| L1 | "What can the toolkit do?" | `arcwright help` | Areas, verbs, examples, what is not built | Unknown command suggests the closest |
| L1 | "Is my computer set up?" / "My phone will not connect" | `arcwright doctor`, `doctor --phones` | Installed, missing, firewall and Wi-Fi checks | Changes nothing |
| L1 | "What was I doing?" | `arcwright resume` | Half-finished work and the safe next step | Warns if someone else changed the same thing |
| L1 | "Undo that" | `arcwright undo` | The last change, how it is reversed, what cannot be (published pages) | Preview first |
| L1 | "Save and share my work" | `arcwright save` | What will be shared, then a proposed change for review | Never merges for you |
| X4 | "What will this cost?" | Shown before any paid step | Estimate and your limit | No paid call without your yes |
| Idea | Report a toolkit problem; see what changed in a new version | `arcwright report`, `arcwright whats-new` | | |

## Mini-games

### Play and try

| When | You say to the AI | Command | You see | It checks or refuses |
|---|---|---|---|---|
| N1 | "Let us play Battle of Wits" | Today after AW-372: `python docs/skills/arcwright-minigame/scripts/minigame_tool.py play nightcap/mini_games/battle-of-wits`. Later: `arcwright minigame play battle-of-wits` | Addresses for this PC and phones, and how to stop | One plain line naming what is missing |
| N1 | "Use another port" | `... play <package> --port 8800` | New addresses | Says if the port is taken |
| N1 | In the room: join, start, answer, rejoin, play again | Browser buttons | Names, game, results, standings | Player limits come from the package; no late joining; hidden answers stay private |
| N1 | "Stop the room" | Ctrl+C | Room closed | |
| N1 | "Use my change" | Press Play again in the room | The next round uses the edited questions and timing, with no restart (the room does this today for Battle of Wits) | A change that does not fit is refused |
| X1 | "Try it with three pretend players" | `arcwright minigame play lantern-dash --simulate 3` | The game running on the real rules, plus a run report the AI can read | Marked as pretend; never counts as a playtest |
| X1 | "Restart when I save" | `... play lantern-dash --reload` | Room restarts and keeps seats | |
| X4 | "Only let my group join" | `... play lantern-dash --join-code` | A code to enter; only the host can start | |
| X4 | "Keep it on this PC" | `... play lantern-dash --local` | No phone address | |
| Idea | Play with people outside your Wi-Fi, or send a build to someone remote | | | Needs hosting approval |

### Make and change

| When | You say to the AI | Command | You see | It checks or refuses |
|---|---|---|---|---|
| N2 | "Change the questions" / "Give 15 seconds to choose" | The AI edits the package files as the guide shows | Before and after; you supply the final text | Slice 1 relies on the AI for the timing sum |
| N4 | "Keep this change" | The AI prepares a pull request | Passing tests | Tests no longer expect the old times |
| X2 | "Change the questions" | `arcwright minigame edit lantern-dash content` | Before and after | Refuses content the rules cannot use |
| X2 | "Give people 15 seconds to choose" | `arcwright minigame edit lantern-dash --set choice-seconds=15` | Every adjustable setting in plain words | Refuses values that do not fit the total time or player limits |
| X2 | "Make a version of this with new questions" | `arcwright minigame variant lantern-dash lantern-night` | A new package: content and settings only | No code; validated and simulated |
| X2 | "Add the picture and sound" | `arcwright minigame add-asset lantern-dash horn.wav --source <where> --licence <which>` | The saved record | Unknown ownership means it cannot be published |
| X2 | "Make a new version" | `arcwright minigame new-version lantern-dash` | A copy with the next number | Needs the version design decided first |
| X2 | "Add the screens" | An AI build session | A plan you approve, then a preview on phone and TV | Failure is reported with what is left |
| X2 | "Add the rules" (a new mechanic) | An AI build session | A plan you approve, then tested rules | Engine change in version one |
| X2 | "Preview the screens" | `arcwright minigame preview lantern-dash` | Phone and TV with pretend states, marked | Never counts as a playtest; runs the package's code, so only trusted packages |
| Idea | "Brainstorm a two-player observation game" | `arcwright minigame brainstorm --players 2` | Options, a recommendation, a saved brief | Flags a repeated mechanic |
| Idea | "Create Lantern Dash" | `arcwright minigame new lantern-dash` | Preview of new files, then a draft (the tool's `scaffold` does this today) | Refuses a taken or badly formed name |
| Idea | Other languages; a one-command rules builder; a visual editor | | | |

### Check, label and manage

| When | You say to the AI | Command | You see | It checks or refuses |
|---|---|---|---|---|
| N2 | "Check it" | `... validate <package>` (exists today) | Loads or does not | Does not check timing, privacy or readiness |
| X3 | "Check it" / "Check them all" | `arcwright minigame check lantern-dash`, `check --all` | Pass or fix, in plain words, for every label | Loads, rules exist, timing, privacy, player limits, fallback, tests, accessibility, content safety, asset ownership, size |
| X3 | "Record how that round went" | `arcwright minigame record lantern-dash` | Version, date, player count, verdict, your note | No player names. Needs your data approval |
| X3 | "Mark it ready for playtest" / "ready for use" | `arcwright minigame promote lantern-dash --to playtest` | What changes and the evidence | Ready needs passing checks, a record and your sign-off |
| X3 | "Take it back to draft" | `arcwright minigame demote lantern-dash --to draft` | What depends on it | |
| X3 | "Add it to a game" / "Remove it" | `arcwright minigame add lantern-dash --game tidepool`, `remove` | The change to that game | Test setups may use drafts with a warning; released games need ready |
| X3 | "Retire it" | `arcwright minigame retire paper-kites` | Games that use it, and how to remove it | Refuses while in use |
| X3 | "Copy, rename or delete it" | `arcwright minigame copy\|rename\|delete paper-kites` | Preview | Deletes only drafts never played |
| Idea | List and search; version history and differences; play an older version | `arcwright minigame list`, `history`, `compare` | | |

### Import an existing game

| When | You say to the AI | Command | You see | It checks or refuses |
|---|---|---|---|---|
| L5 | "Import this browser game" | `arcwright minigame import ./kites-source` (today `onboard-browser`) | What was found, what is uncertain, questions | Asks source, author, licence and proof; keeps the original; stops at "Imported" |
| L5 | "Continue that import" / "Where is it?" | `... import --resume <id>`, `import --status <id>` | The saved import | Unknown ID refused |
| L5 | "Port it" | AI build sessions (AW-349) | A baseline of the original, a plan, a playable package | You choose the source and approve the plan |
| L5 | "Compare it with the original" | Written comparison (AW-349 defines no command) | Differences and time spent | Same package version, standalone and in a game, gives matching results |
| Idea | Automatic porting | | | One port proves nothing general |

## Playtests

| When | You say to the AI | Command | You see | It checks or refuses |
|---|---|---|---|---|
| L3 | "Plan a test" | `arcwright playtest plan tidepool-test-1` | Question, who, what success looks like | One question at a time |
| L1 | "List our playtests" | `arcwright playtest list` (exists as a script today) | Current, draft, archived | |
| L1 | "Start a new test page" | `arcwright playtest new tidepool-test-1` | The AI asks for or fills the nine values today's script needs | Warns that a merged draft is public (until X4 changes this) |
| L1 | "Add the page we already approved" | `arcwright playtest register tidepool-test-1` | Preview, then registered | Never rewrites those files |
| L3 | "Write the page" / "Link the survey" | AI with you | Your wording on the page; the survey ID | Final text is yours |
| L1 | "Is it ready for testers?" | `arcwright playtest check tidepool-test-1` | Page, survey link, telemetry; what only a real device proves | Never claims a check it did not do |
| L3 | "Walk me through before we start" | `arcwright playtest preflight tidepool-test-1` | Setup and a rehearsal list | Stops at each point for you |
| L3 | "Note that" / "That is a bug" | `arcwright playtest note "..."`, `--bug` | Time-stamped note; a bug keeps version and screen state | No player names |
| L3 | "Show testers what we collect" | Shown when they join | A short notice | No recording without it |
| L3 | "Delete this tester's data" | `arcwright playtest forget <tester>` | What is removed | Preview first |
| L4 | "Debrief" | `arcwright playtest debrief tidepool-test-1` | Prompts for what you saw | |
| L4 | "What did testers tell us?" | `arcwright playtest results tidepool-test-1` | Counts, themes, evidence strength | Reads a survey file you provide, kept outside the repository; names removed |
| L4 | "Compare versions" | `arcwright playtest compare tidepool-test-1 --with tidepool-test-2` | Side by side | Says when the sample is too small |
| L4 | "Decide" | `arcwright playtest decide tidepool-test-1` | Keep, change or cut, in your words | Offers a decision record and a task |
| X4 | "Build the pages" | `arcwright playtest build` | A local copy, served so links work | Says it replaces the previous local build |
| X4 | "Publish it" | `arcwright playtest publish tidepool-test-1` | What becomes public and the pull request | Nothing is public until merged; your merge approval if you agree to later question 2 |
| X4 | "Cancel" / "Take it down" | `arcwright playtest cancel\|take-down` | What stays public and for how long | |
| X4 | "Make this the current test" / "Go back to the earlier one" | `arcwright playtest set-current <test>` | Before and after | Needs your approval |
| L1 | "Archive the old one" | `arcwright playtest archive tidepool-test-0` | Preview, then archived | Keeps pages and history |
| Idea | Read the survey service directly; a results dashboard; a playtest lab for customers; build or edit survey forms | | | Each needs approval |

## Stories (preview only)

Story **writing** happens in the story tool you adopt (D-117, D-122), which you can read and change as a picture. The toolkit imports, checks, calibrates and plays. The full outline comes in the story proposal, before anything is built.

| When | You say to the AI | Command | You see | It checks or refuses |
|---|---|---|---|---|
| S | "Brainstorm with me" | `arcwright story brainstorm orchard-case` | Questions and options | Final story text stays yours |
| S (AW-306) | "Import my story" | `arcwright story import <export>` | What came across and what did not | Fairness failures in your terms |
| S | "Is it fair?" / "Why did it fail?" | `arcwright story check orchard-case` | Pass or fix, with plain reasons | Spoiler-safe unless you ask for spoilers |
| S | "Calibrate it" | To be designed | Difficulty and pacing against targets | |
| S | "Read it through as a player" | To be designed | What each player learns, in order | |
| S (AW-367) | "Play it" | `arcwright story play orchard-case` | A running game | |
| S | "How did it play?" | `arcwright story results orchard-case` | Spoiler-safe summary | |

## Whole games

| When | You say to the AI | Command | You see | It checks or refuses |
|---|---|---|---|---|
| L6 | "I have an idea for a game" | `arcwright game brainstorm tidepool` | Options and a saved brief | Your design choices stay yours |
| L6 | "Create it" | `arcwright game new tidepool` | Preview, then a starter folder and rules file | Refuses a taken name |
| L6 | "Change rounds, players or mini-game order" | `arcwright game edit tidepool` | Before and after | |
| L6 | "Check its setup" | `arcwright game check tidepool` | Pass or fix per rule | Missing mini-games, player counts, dead ends |
| L6 | "Run it with pretend players" | `arcwright game play tidepool --simulate 4` | Where it reached and stuck | Not a human playtest |
| L6 | "Play it" | `arcwright game play tidepool` | TV and phone addresses | Lists what is missing |
| L6 | "Show how it played" | `arcwright game results tidepool` | Summary by version | |
| L6 | "Only show Tidepool" | `arcwright status --game tidepool` | That game's board | |
| Idea | Release a game to players; a visual flow editor; templates for customers | | | |

Today only Nightcap has a mini-game template folder, so `--game` for another game starts working in L6.

## Where does it stand?

Piece L2. "Where does Lantern Dash stand?" or `arcwright minigame status lantern-dash`. `arcwright status` shows everything. Invented example:

```text
Lantern Dash  (mini-game 0.1.0)   Stage: DRAFT   Next stage: PLAYTEST

 1 Brainstorm  DONE     brief saved 27 Nov
 2 Create      DONE     rules, screens and content present
 3 Configure   DONE     2 to 4 players, 90 seconds
 4 Test        FIX      scores show on the TV too early
 5 Playtest    TO DO    0 recorded plays
 6 Research    UNKNOWN  no record
 7 Publish     LOCKED   needs steps 4 and 5 and your sign-off

 Say:  "fix the failing check"
 Type: arcwright minigame check lantern-dash
```

**Stage is the label. The lines are evidence.**

| Mark | Meaning |
|---|---|
| DONE | Saved evidence says so |
| FIX | A check failed, or evidence is out of date because something changed |
| TO DO | Known not to have happened |
| UNKNOWN | Nothing saved either way |
| LOCKED | Waiting for earlier steps |

An imported game shows "imported from" under Create.

## Not in version one

| Item | Needs before it starts |
|---|---|
| Dashboard pages, including a status board on screen | Your approval; committed creator work is staged separately |
| Survey and form builder | Your approval |
| AI plugins or skills shipped to customers | Your approval |
| Public documentation site | Your approval |
| Hosting rooms beyond your Wi-Fi | Hosting and spending approval |
| Other languages | Your approval |
