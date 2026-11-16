---
id: productroadmap.product.2026-11-15-reset-audit
namespace: product-roadmap
title: Founder Reset Audit, 2026-11-15
owner: Nico Janssen
status: active
review_by: "2027-02-15"
sensitivity: internal
source: authored
tags: []
supersedes: []
---

> Current version: v1.0
> Last updated: 2026-11-15
> Status: Current (a dated record; it is not updated as work closes)
> Canonical path: docs/product/2026-11-15-reset-audit.md

# Founder Reset Audit, 2026-11-15

A dated record of the founder reset of 14 and 15 November 2026: what was checked, what was found, and which task now owns each thing. It answers "why does this task exist". Whether a task is open or closed is on GitHub (`python scripts/roadmap_status.py`).

- **Snapshot:** main at `14f12e2`.
- **Method:** read-only audit of code, tests, docs, git history and GitHub, plus a founder interview.
- **Labels:** *verified* means checked against code, tests or GitHub on the stated date. *Inferred* is an estimate. Anything else is a proposal.

## 1. Findings

A **finding** is something the audit checked and found wrong, missing, stale or risky. **Owner** is the task, decision or document that now carries it. Every finding has one; none is left only in a conversation.

| # | Finding, in plain words | How it was checked | Owner |
| --- | --- | --- | --- |
| F1 | The game that runs today is the old Couch Race design. The Master GDD game is not built | Code | Milestone M7; issue #303; AW-300 onward |
| F2 | Nothing is deployed to the cloud. The deploy jobs run green but skip the deploy step | GitHub Actions | AW-269 (issue #188), needed before session 3 |
| F3 | The Nightcap status page was stale within hours of being written | Docs | Fixed in the reset pull request: `docs/product/nightcap-status.md` v2.0 |
| F4 | Another session held an unsaved edit to spec 0092 and an untracked case folder | Disk, 14 and 15 Nov | Founder step 2 on the status page; AW-305 |
| F5 | The tracker described Couch Race; the rebuild had one issue and no tasks | GitHub | Labels and comments applied 15 Nov; the rest is AW-299 |
| F6 | The rebuild had no tasks or IDs; AW-288, AW-291 and AW-292 had no issue | GitHub, roadmap index | AW-296 to AW-317 created 15 Nov; AW-291 issue created; AW-288 and AW-292 in AW-299 |
| F7 | Duplicate task IDs, milestone mismatches, an issue with no ID | `scripts/roadmap_status.py` | AW-299 |
| F8 | Four issues are open although their work is merged (#284, #202, #201, #123) | Git history | AW-299: check criteria, then close |
| F9 | The host's 468 written lines have no code that reads them | Code, 15 Nov | AW-291; open question on whether it is built for session 1 |
| F10 | The specialist agents fail in every worktree session: 0 of 3 probes answered | Reproduced | AW-296 |
| F11 | Ranked search is weak and the index predates the freeze decisions | One query; index dated 21 Sep | AW-297 |
| F12 | Project facts sat in one tool's private notes, which other agents cannot read | Disk | Fixed in the reset pull request: `HANDOVER.md`, "Working facts every session needs" |
| F13 | There was no start-of-session handover file | Disk | Fixed in the reset pull request: `HANDOVER.md` |
| F14 | Mini-games never start, time out or return to the story in a real session | Code | AW-303 |
| F15 | Spec 0092 is wrong about arc loops and about the notebook record | Code and an existing test | Fixed in the reset pull request: corrections section of spec 0092 |
| F16 | Spec 0092 asks for about twelve separate approvals | Spec | D-118; AW-302 |
| F17 | Two sets of screen code exist (`dashboard/`, `nightcap-web/`) | Code | AW-300 picks one |
| F18 | The Nightcap web client, about 5,300 lines, uses no third-party libraries | Code | ADR-0026; AW-309 |
| F19 | The engine's default arc is named for Nightcap; other game words exist in `engine/` | Code | AW-274 (issue #220); AW-300 lists them |
| F20 | One story per session; no world that persists between sessions | Code (`engine/db/orm.py`), docs | Recorded as later work in `docs/roadmap/00-overview.md`; open question on the second game |
| F21 | The docs name two different second games (Daily Case, the monster game) | Docs | Open question; issues #88, #114, #50 labelled `needs-decision` |
| F22 | PRD and architecture files said "edit in Notion", which nobody has done since August | Docs | Fixed in the reset pull request: 21 files |
| F23 | Play records use one game's words (accusation, contradiction) | Code | D-115; AW-304 |
| F24 | "Players want one more game" was not a stated goal | Docs | D-116; AW-307 |
| F25 | The "orphaned" freshness number counts 438 of 449 documents, so it says nothing | Knowledge-base files | AW-313, after the freeze |
| F26 | Specs and plans live in two places | Disk | AW-311 |
| F27 | Agent and skill definitions live in seven places | Disk | AW-312 |
| F28 | 27 remote branches and 14 worktrees | Git | AW-310 |
| F29 | Only one check is required to merge; no review is required | GitHub API, 15 Nov | AW-298 (founder action) |
| F30 | No issue template for tasks; 8 open issues unlabelled; no product label; no rebuild milestone | GitHub | Done 15 Nov: template, labels, milestone M7 |
| F31 | The Nightcap name has unresolved trademark conflicts | Docs (August) | Already in `docs/product/open-questions-log.csv`; counsel before any public launch |
| F32 | A pass bar already exists and was approved on 2026-09-28 | Docs, 15 Nov | Reused for session 1 on the status page |

## 2. Founder answers and where each is recorded

| Answer | Recorded as |
| --- | --- |
| Thin, complete Nightcap on the 30-day date, as much as fits; three sessions | D-112 |
| In Nightcap a beat is one round ending in a story-wrapped mini-game; "round" is not an engine idea | D-113; architecture 1.6 and 1.7 |
| Build only what is unique, adopt the rest; free first, $50 a month ceiling | D-114; ADR-0026; technology stack 2.11 |
| Play data is captured at engine level for every game | D-115; architecture 1.7 |
| Players should want one more game after every session | D-116 |
| A human defines structure and truth; AI writes within it | Already architecture principles 2 and 3; noted in D-116 |
| Connect a story tool before session 1; write case two in it; compare | D-117 |
| Three lanes; three combined specs | D-118; working model |
| Capture all work in one standard format; do the GitHub improvements | D-119; working model; `AGENTS.md` |
| Arcwright is the dungeon master for any game built on it | Architecture 1.6 (PR #346) |
| How the founder wants to be worked with | `docs/conventions/human-collaboration.md` (PR #346) |
| 10 to 15 hours a week, dependent on usage limits and harness quality | Planning assumption on the status page; not a decision |
| The GDD design is the target; paper tests are instruments, not the game | Already D-108; confirmed |

## 3. The founder's inspirations

Fourteen works, with the first lesson drawn from each. The founder called this mapping accurate but simplistic: he values each for its mechanics, stories, gameplay, story management, genre, artistry, expandability, immersion and game type. The deeper study is AW-315.

| Inspiration | First lesson | Where it lands |
| --- | --- | --- |
| Jackbox | Phones as controllers, a room code, humour | Nightcap already has this shape |
| Mario Party | A mini-game after every round, with big swings | The beat rule (D-113) |
| It Takes Two, Split Fiction, Unravel 2 | Built for two from the start; each mechanic belongs to its scene | The two-player floor |
| Murdle | Solo, daily, pure deduction | The one-player idea; Daily Case |
| Dungeon Crawler Carl | The system itself as a showrunner with a voice | Vesper, the host |
| Skyrim, No Man's Sky, Pokemon | Worlds, quests, companions | The second game and beyond |
| Civilization V, RollerCoaster Tycoon | "One more turn" | The replay goal (D-116) |
| Roblox, Minecraft | Players make things | Arcwright's creator platform |

Two points are documented by the makers; the rest is inference. It Takes Two was written for two players from the start, because adding a player count afterwards limits the design. Its director used most mechanics for one scene only, because repetition is why story games go unfinished. That second point is the caution against using one mini-game mechanic three times in session 1.

On one player: the GDD's floor is two. Solo would be its own design, not a setting, and the docs already describe one, Daily Case. Solo stays out of the first three sessions.

## 4. Is Arcwright already solved elsewhere?

A first pass from one search and four pricing pages. The proper comparison was done the same day and corrects this section: [competitor and prior-art comparison](2026-11-15-competitor-and-prior-art.md). In particular, the last paragraph below is wrong: Hidden Door sells something close to "a dungeon master for any world".

| Piece | Who already does it | Position |
| --- | --- | --- |
| Choosing which model to call | Open-source routing libraries | Already adopted |
| Talking characters and voices | Inworld, Convai, Nvidia ACE | Crowded. Do not compete; take voices, not brains |
| Writer-controlled branching story | Charisma.ai, Ink, Yarn Spinner | Mature. Import from one (AW-306) |
| Visual story editors | articy:draft, Twine, narrative graph tools | Do not build a general editor. Build only a view of what Arcwright alone knows (AW-317) |
| TV-plus-phones rooms | Standard web infrastructure | Already adopted |
| Mini-game packaging | Any game or web engine | Not what makes Arcwright special. Keep it minimal |

Where Arcwright may be different, all unproven with players: the truth is fixed by rules and a model only voices it, so fairness can be checked; each character speaks only from what it knows, with a record of who told whom; it directs a group of real people in a room, not one player talking to one character; every game records play in one shape, so learning carries across games.

Nobody was found selling exactly "a dungeon master for any game". That is either a gap or a warning. The only real proof is whether Nightcap is fun.

## 5. What the audit did not do

| Not done | Now owned by |
| --- | --- |
| A TV-and-phones walkthrough of the running build (Docker was not running) | AW-301 |
| Reading the PRD's full five-phase visual editor plan | AW-317 |
| Deeper competitor research | AW-316 |
| A deeper study of the fourteen inspirations | AW-315 |
| A full build-versus-adopt review | AW-309 |
| Testing the acceptance criteria of the merged-but-open issues; reading each "blocked" reason; more than four of 100 closed issues | AW-299 |
| Verifying reconnect and private-information handling in code | AW-308 |
| Measuring the time estimates | Marked inferred on the status page |
| Two interview questions: what players should feel and do; Arcwright's first outside creator | `docs/product/open-questions-log.csv` |

## 6. Issue audit: all 44 open issues on 2026-11-14

Dispositions: **revise** (keep the ID, rewrite for the Master GDD game), **needs a decision**, **defer**, **superseded**, **close with evidence**, **keep**.

| Disposition | Count |
| --- | --- |
| Revise | 12 |
| Needs a decision | 10 |
| Defer | 9 |
| Superseded by the rebuild | 5 |
| Close with evidence | 4 |
| Keep | 4 |
| **Total** | **44** |

**Applied on GitHub on 2026-11-15:** every open issue received a product label, its disposition label where one exists (`superseded`, `deferred`, `needs-decision`) and a comment stating the disposition and linking this record. Nothing was closed and no issue body was rewritten; both need checking or founder wording and belong to AW-299.

**How deep the checking went.** Every issue on the launch path and the four close-with-evidence rows were checked against code and merged commits. Everything else was checked by searching main for the task ID and reading the issue; "not started" means no commit on main names the task ID and no code was found for it. Acceptance criteria were not tested one by one.

### Launch path: the first invited TV-and-phones session

| Issue | AW ID | Serves | GitHub | Verified state | Proposal | Evidence and reason |
|---|---|---|---|---|---|---|
| #303 | none | Nightcap | Open, no milestone | No rebuild code exists | Revise | Make it the parent for the rebuild and link spec 0092. It is the only rebuild item in the tracker. |
| #240 | AW-286 | Nightcap | Open | Not run as a full session | Superseded by spec 0092, work package 15 | It owns the Couch Race rehearsal. The rebuild's first TV session replaces it. Keep the history. |
| #234 | epic M5-I | Nightcap | Open | Children AW-281 to 285 and 287 are merged | Superseded by spec 0092 | The epic is the Couch Race arc. Its remaining children are superseded or deferred below. |
| #229 | AW-279 | Nightcap | Open | Not started | Revise | The GDD game still needs detective identity and an opening briefing. |
| #227 | AW-277 | Nightcap | Open | Not started | Revise | Host lines between beats are still needed, written for the loop. |
| #228 | AW-278 | Nightcap | Open | Not started | Superseded by spec 0092, work package 11 | It accounts for points at the reveal. The GDD ending has no points. |
| #230 | AW-280 | Nightcap | Open | Not started | Superseded by the first authored case | It generates clue text. The first case is hand-written. |
| #254 | none | Nightcap | Open | Not started | Superseded by spec 0092, work packages 7 and 10 | It breaks ties on contradiction flags, a mechanic the GDD parks. The GDD breaks ties on mini-game results. |
| #258 | AW-289 | Nightcap | Open | Draft brief, not built | Defer | A new Last Call mini-game awaiting your creative approval. Not needed for a thin first version. |
| #186 | epic M5-F | Nightcap | Open | Built (AW-262 to 265), never played by people | Needs a decision | Is "Tell Me Something True" one of the first version's mini-games? |
| #183 | AW-266 | Nightcap | Open | Not run | Needs a decision | A separate rehearsal for that mini-game. Fold it into the first TV session, or keep it apart? |
| #223 | AW-275 | Shared | Open | Not started | Keep | Mini-game colour tokens and visible focus states. Small, and mini-games are in the first version. |
| #220 | AW-274 | Arcwright | Open | Draft spec 0070 only | Keep | Removes game-specific words such as "killer" from platform vocabulary. Directly serves agnosticism. |
| #284 | AW-290 | Shared | Open | Merged 8 Aug as `e316718`, 17 files | Close with evidence | Code and tests are on main. Check its criteria first. |
| #287 | AW-295 | Shared | Open | Not started | Defer | Six database tables for generated cases. The authored case format should settle first. |
| #270 | none | Nightcap | Open, blocked | Not started | Defer | A cleanup inside the Couch Race screen code that the rebuild will replace. |
| #188 | AW-269 | Shared | Open | Automation merged; nothing deployed | Keep, sequenced before session 3 | The last deploy runs skipped the deploy job. Sessions 1 and 2 at your house can run from your PC through a tunnel. Session 3, friends at their house without you, needs real hosting. (Updated after your session plan.) |
| #185 | AW-268 | Nightcap | Open | Not started | Defer | Art pipeline and motion. Spec 0092 excludes production polish. |
| #187 | epic M5-G | Nightcap | Open | Not started | Defer | Visual identity and polish. Same reason. |
| #138 | none (titled "AW-NNN") | Arcwright | Open | Not started | Defer | AI takes over a dropped player. Reconnect matters more for 2 to 4 supported players. It also needs a real ID. |

### The invited sessions themselves (milestone M6)

These describe "qualifying sessions" for the old design, but they are the right homes for your invited session.

| Issue | AW ID | Serves | GitHub | Verified state | Proposal | Evidence and reason |
|---|---|---|---|---|---|---|
| #93 | AW-240 | Nightcap | Open, blocked | Not started | Revise | Session runbook. Rewrite for the GDD game. |
| #94 | AW-241 | Shared | Open, blocked | Not started | Revise | Checklist of what each session must record. Should use generic engine data. |
| #95 | AW-242 | Nightcap | Open, blocked | Not started | Revise | Your own final rehearsal. Maps to the first founder TV run. |
| #96 | AW-243 | Nightcap | Open, blocked | Not started | Revise | Five outside sessions. Maps to invited play; the number needs your call. |
| #97 | AW-244 | Nightcap | Open, blocked | Not started | Revise | Analysis and next-step decision after the sessions. |
| #52 | epic M6-A | Nightcap | Open | Not started | Revise | Parent of #93 and #94. |
| #53 | epic M6-B | Nightcap | Open | Not started | Revise | Parent of #95 and #96. |
| #54 | epic M6-C | Nightcap | Open | Not started | Revise | Parent of #97. |

### Safety, cost and platform proof

| Issue | AW ID | Serves | GitHub | Verified state | Proposal | Evidence and reason |
|---|---|---|---|---|---|---|
| #85 | AW-232 | Shared | Open, blocked | Not started | Revise | Safety test protocol. Rewrite for the GDD screens and decide the minimum check before invited players. |
| #86 | AW-233 | Shared | Open, blocked | Not started | Keep | Fixes for whatever #85 finds. |
| #48 | epic M5-A | Shared | Open | Not started | Keep | Parent of #85 and #86. |
| #87 | AW-234 | Arcwright | Open, blocked | Not started | Defer | Margin per player count. It needs real session cost data first. |
| #49 | epic M5-B | Arcwright | Open | Not started | Defer | Parent of #87. |

### Visual editor (Visual Storyworld, phase 1)

| Issue | AW ID | Serves | GitHub | Verified state | Proposal | Evidence and reason |
|---|---|---|---|---|---|---|
| #89 | AW-236 | Arcwright | Open, blocked | Not started | Needs a decision | Live knowledge-graph view. The one view the roadmap requires. |
| #90 | AW-237 | Arcwright | Open, blocked | Not started | Needs a decision | Read-only view of the story structure. The most useful view for understanding the engine. |
| #91 | AW-238 | Arcwright | Open, blocked | Not started | Needs a decision | Live event stream view. |
| #92 | AW-239 | Arcwright | Open, blocked | Not started | Needs a decision | Character state view. |
| #51 | epic M5-D | Arcwright | Open | Not started | Needs a decision | Should a minimal viewer be pulled into the rebuild because you would use it now? |

### Second game

| Issue | AW ID | Serves | GitHub | Verified state | Proposal | Evidence and reason |
|---|---|---|---|---|---|---|
| #88 | AW-235 | Arcwright | Open | Design docs merged in June | Needs a decision | It names Daily Case as the second game. You described a Pokémon-type game as the real test. |
| #114 | AW-245 | Arcwright | Open | Not started | Needs a decision | Builds the second game. Its GitHub milestone says M5; the task file says after M6. |
| #50 | epic M5-C | Arcwright | Open | Partly done | Needs a decision | Parent of #88, #114 and #220. |

### Merged work with open issues

| Issue | AW ID | Serves | GitHub | Verified state | Proposal | Evidence and reason |
|---|---|---|---|---|---|---|
| #202 | AW-270 | Arcwright | Open | Merged 13 Jul in PR #214 | Close with evidence | The intent block and its telemetry are in the engine code. Check its criteria first. |
| #201 | epic M5-H | Arcwright | Open | Other children closed | Close with evidence | Close after #202. |
| #123 | epic M5-E | Arcwright | Open | No open child task found | Close with evidence | Confirm every child is closed, then close. |

### Problems in the tracker itself

- **Missing issues.** Spec 0092's 16 work packages and the first case have no issues and no task IDs. Tasks AW-288, AW-291 and AW-292 exist in the roadmap files with no issue.
- **AW-291 may matter for launch.** The host's 468 written lines have no code that reads them. AW-291 is the planned reader. It needs a decision for the thin version.
- **Duplicate IDs.** AW-270 names both closed #190 and open #202. AW-218 names both #132 and #71.
- **Milestone mismatches.** #114 and #202 sit in M5 on GitHub; their task files say after M6. #303 has no milestone.
- **Stale milestones.** M5 and M6 exit criteria were written for Couch Race.
- **"Blocked" labels.** Thirteen issues carry the label. I did not verify each stated blocker.
- **Index gaps.** The roadmap index lists three M1 epics as having no issue, although closed issues #12, #17 and #25 exist for them.
- **Stale status page.** `docs/product/nightcap-status.md` still says spec 0092 is not on GitHub. It merged in PR #345.


Reproduce the snapshot with `gh issue list --repo nickejanssen/arcwright --state open --limit 200` and `python scripts/roadmap_status.py --json`.
