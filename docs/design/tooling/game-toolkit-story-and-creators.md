---
id: engineeringpractice.design.tooling.game-toolkit-story-and-creators
namespace: engineering-practice
title: "Arcwright Game Toolkit: Stories And Creator Products"
owner: Nico Janssen
status: draft
review_by: "2027-02-27"
sensitivity: internal
source: authored
x-scope-evidence: none
tags: []
supersedes: []
---

# Arcwright Game Toolkit: Stories And Creator Products

> Current version: v0.4 DRAFT
> Last updated: 2026-11-27
> Status: Draft, **pending founder approval**. Part of the [proposal](game-toolkit-proposal.md).
> Canonical path: docs/design/tooling/game-toolkit-story-and-creators.md

## How stories fit earlier decisions

| Decision or task | What it settles | What it means for this toolkit |
|---|---|---|
| D-117, [AW-306](https://github.com/nickejanssen/arcwright/issues/359) | The second case is written in an adopted story tool, through an importer; the two cases are compared | The toolkit does not build a writing tool. AW-306 is its own task, with a target of 5 December |
| D-122 | Viewing, editing and building a story are one tool, adopted first; you must read and change stories graphically | Terminal commands are never the way you write |
| D-129 | Your first outside creator is a writer who cannot code; after session 1, that authoring path comes before a public API or outside developer kit | The story journey must work without a terminal |
| D-156 | Technology before story polish; you named the technology "for creating a story, calibrating a story, and runtime of a story" | Create, calibrate and play are the story proposal's core |
| D-114 | Adopt what exists; build what makes Arcwright unique | Arcwright keeps who-knows-what and fairness checks |

**What the toolkit does for stories:** import, check, calibrate, play and report. **Writing happens in the adopted tool.**

**One tension to settle (later question 1):** "mini-games first" puts the toolkit's story commands behind mini-game work, while the second case is needed for session 2. Recommended: let AW-306 run alongside on its own schedule.

## Story configurations (a separate product track)

Added at your request, relayed by the orchestrator session on 27 November 2026. Your words as relayed: "Consider what this should look like for story configurations as well. I consider that a different type of product for arcwright, but if there are learnings and cross-utilization needed, then we should flag that."

A **story configuration** here means a case plus one setup of how it is played, such as version 1a (inferred reading). This page does not design that product. You decided (Q6) that its proposal starts right after this one is approved and outlines everything before any story tool is built.

**Where it stands (verified).** Five versions, 1a to 1e, were approved on 20 November (D-148, [version sheets](../session-1-variants/README.md)). Only 1a has a game rules file registered (`nightcap/agency-race-1a.arc.json`, `config/arcs.json`). [AW-356](https://github.com/nickejanssen/arcwright/issues/465), which builds the setups, is open.

| Shared item | What should be shared | What stays with stories (inferred) | Label |
|---|---|---|---|
| Validation | One pass or fix answer to "does this load and is it fair" | Fairness rules and spoiler safety | Existing tools verified; sharing inferred |
| Play | Name a thing, get a running room and phone address (AW-372, AW-367) | Case, version and seats | Records verified; sharing inferred |
| Playtest harness | Scripted session runs (`engine/harness/`) and page checks serve both | Pretend players suited to a mystery | Verified; use inferred |
| Evidence | One record: game, case, version, group, mini-game version (AW-354 adds version tags and ratings) | Which questions compare versions | Records verified; shared report inferred |
| Guide shape | Goal, steps, commands that run, what is missing | Writing craft | Inferred |
| AI instructions | Same source-and-pointer rule and test | Who may read case files | Verified for Codex; story use inferred |
| Mini-game choice | A version picks mini-games by name and version | Which game fits which moment | Binding verified in the 1a file |

## How the toolkit grows into the creator products

**Committed (verified).** [Requirements](../../prd/02-requirements.md) line 94: at the first horizon a developer gets a web API, a TypeScript web SDK generated from the API description, a hosted dashboard with live knowledge graph inspection, documentation, and Nightcap as the public example. [Scope](../../prd/03-scope.md) line 46 and D-035 stage the visual creator tools in five phases: inspection; structured editing; live preview and debugging; a visual flow editor; asset libraries, a marketplace if there is demand, and AI-assisted authoring. The MVP definition in the [scope file](../../prd/03-scope.md) (line 26) ranks the developer dashboard and authoring interface lowest.

**Today.** No route for uploading a game rules file, no SDK generation step in its package file, and no knowledge graph inspection screen were found; [AW-236](https://github.com/nickejanssen/arcwright/issues/89) is open.

The mapping is a recommendation. It approves nothing in the last column.

| Pieces | Could grow into | Build it this way now | New product scope: needs your approval |
|---|---|---|---|
| N1, X1 play and pretend players | Live preview phase | Room logic apart from the command, driven by the package | Hosting rooms for outsiders |
| N2 guide | Developer documentation | Readable without any AI; tested | A public documentation site |
| N3 AI skills | No committed product | Plain procedures in the shared skill format | Shipping skills or plugins; an agent for outside authors |
| L1, L2 command and board | Documentation; dashboard | One grammar; same facts as text and JSON | A public command-line product; a customer status screen |
| X2, X3 mini-game work | Documentation | Label rules checked in Python | Outside packaging or submission |
| L5 port proof | Sample projects | Record real effort and limits | An import or porting service |
| X4, L3, L4 playtests | Dashboard; debugging | Reports on game-neutral play records | **A playtest lab, forms or research product for developers** |
| Story pieces | API input; character and arc editing phase | Structured check results | A public story product beyond the phases |
| L6 new games | API input; editing and flow phases | One rules check usable by a command, API or editor | Templates or a starter kit |

You said the toolkit "must be made availble once we start selling the engine" (Q4). That is recorded as intent. Selling or shipping anything in the last column needs its own approval.

**Not yet shown:** that anyone would pay for the toolkit. Revisit the idea of selling it if, by 31 May 2027, fewer than 3 of 5 outside creators finish a mini-game variant unaided in 60 minutes, or none would pay (proposed threshold).

**Do not copy from larger products yet:** a marketplace or revenue sharing; our own agent server or metered AI credits.
