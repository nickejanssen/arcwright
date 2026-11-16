---
id: engineeringpractice.conventions.knowledge-base-upkeep
namespace: engineering-practice
title: Knowledge Base Upkeep And Accuracy Check
owner: Nico Janssen
status: active
review_by: "2027-02-15"
sensitivity: internal
source: authored
tags: []
supersedes: []
---

> Current version: v1.1
> Last updated: 2026-11-15
> Status: Current
> Canonical path: docs/conventions/knowledge-base-upkeep.md

# Knowledge Base Upkeep And Accuracy Check

How knowledge gets into the right place, and how we check that the specialist agents answer from it correctly. This is a routine and a manual check. It adds no tooling, so it is allowed under the tooling freeze (D-110, D-111). Owner: the Scribe role (`docs/agents/scribe.md`).

## Where each kind of knowledge goes

One home per kind. If the home already has a document on the topic, fold the new material into it; do not add a parallel document.

| Kind of knowledge | Home | Who can read it |
| --- | --- | --- |
| A founder decision | `docs/product/decisions-log.csv`; an ADR in `docs/decisions/` when it shapes architecture | Every agent and the specialist agents |
| A question not yet answered | `docs/product/open-questions-log.csv` | Same |
| Work to be done | `docs/roadmap/tasks/` plus a GitHub issue (D-119) | Same |
| Whether work is open or closed | GitHub only (D-109) | `python scripts/roadmap_status.py` |
| The stack and what we adopt | `docs/architecture/02-technology-stack.md` | Same |
| Game design | `docs/gdd/nightcap/` | Same |
| What a play session showed | The GDD validation pages | Same |
| What every session must know before starting | `HANDOVER.md` | Every agent |
| How the founder wants to be worked with | `docs/conventions/human-collaboration.md` | Every agent |
| A tool's private notes (for example Claude's memory) | Only preferences about that tool. Project facts do not belong there; move them to `HANDOVER.md` or the docs | That tool only |

A document enters the knowledge base when it is under `docs/`, carries the standard front matter (`id`, `namespace`, `owner`, `status`, `review_by`) and is merged to main. The `team-ai` check validates the front matter on every pull request.

## The routine

- **After every merged pull request:** one dated line in the `HANDOVER.md` log.
- **After every founder decision:** a row in the decisions log, recorded with explicit approval evidence.
- **After every play session:** findings go into the GDD validation pages, not chat.
- **After any change to how docs are organised, and after the agent guard is fixed (AW-296):** run the ten-question check below (AW-297).

## The ten-question check

Each question has an answer verified from a source on 2026-11-14 or 15. One session asks the owning specialist agent and scores four things per question: answered, correct, cited the right file, and flagged a known conflict where one exists.

How to run it so runs can be compared:

1. Pull main in the checkout the session uses, then rebuild the index there: `python scripts/team_ai_cli.py reindex --root team-ai`. The index is per checkout and not in git.
2. Use a session started after the last change to the agent files. A session keeps the agent instructions it loaded when it started (observed 2026-11-15).
3. Ask each owning agent its questions as written, with no hints, and ask for the answer, the owning file or decision ID, any conflict found, and anything it could not open.
4. **Right citation** means the agent cited the record that owns the answer (the decision, spec, GDD ledger or architecture section). Citing a page that only summarises that record is a miss, even when the answer is correct.

| # | Question | Verified answer | Owning agent | Owning record |
| --- | --- | --- | --- | --- |
| 1 | Is spec 0092 approved? | Only for the thin version, since 2026-11-15 (D-123); that permits the inventory and no building. Before that date the answer was "No. Draft" | `nightcap-sme` | The status line of `docs/specs/0092-nightcap-gdd-rebuild.md` |
| 2 | When does the tooling freeze end? | At the rebuild's first TV session (D-111) | `product-roadmap-sme` | D-111 in `docs/product/decisions-log.csv` |
| 3 | Has Gate 1 passed? | No | `product-roadmap-sme` | D-111; `docs/gdd/nightcap/02-validation/98-validation-state-and-remaining-plan.md` |
| 4 | What is the two-player rule? | Two players is mandatory and first-class | `nightcap-sme` | `docs/gdd/nightcap/00-governance/00-decision-ledger.md`, Player count |
| 5 | Who decides a state transition? | Deterministic rules, never a model | `arc-execution-sme` | `docs/architecture/01-overview.md` 1.6; `docs/architecture/03-arc-execution.md` |
| 6 | Which source owns task status? | GitHub (D-109) | `product-roadmap-sme` | D-109; `docs/roadmap/README.md`, Status |
| 7 | Is contradiction-catching a current Nightcap mechanic? | Parked | `nightcap-sme` | The GDD decision ledger |
| 8 | What breaks ties among solvers? | Mini-game performance | `nightcap-sme` | The GDD decision ledger |
| 9 | Which second game do the docs name? | Two candidates; the agent should flag the conflict | `product-roadmap-sme` | D-056 and the task files that name each game |
| 10 | Is Couch Race the current design? | No. Superseded | `nightcap-couch-race-sme` | `docs/story-bibles/nightcap-couch-race.md`; ADR-0023; D-108 |

**Target:** at least eight of ten correct with the right citation. Every miss becomes a GitHub issue naming the document or agent to fix.

## Results

| Date | Answered | Correct | Right citation | Conflict flagged | Notes |
| --- | --- | --- | --- | --- | --- |
| 2026-11-14 | 0 of 3 probes | Does not apply | Does not apply | Does not apply | All three probes were refused access to `docs/` from a worktree session. Cause and fix: AW-296. The ten questions have not been run yet |
| 2026-11-15, isolated copy | 8 of 10 | 7 of 10 | 6 of 10 | 0 of 1 | Run by a separate session in an isolated copy of the repository carrying the AW-296 fix, before agents could read the decisions log. Scored afterwards from that session's report. Questions 1 and 3 were refused: the roadmap specialist could not open spec 0092 or the decisions log. Question 9 named one game and flagged no conflict. This run led to D-120 |
| 2026-11-15, live | 10 of 10 | 10 of 10 | 7 of 10 | 1 of 1 | First live run from a worktree session, main at `e2b1471`, index rebuilt in the main checkout and the worktree (501 documents). Target missed by one on citations. All three misses are `product-roadmap-sme` citing a summary page (questions 2, 3 and 9). Follow-up: AW-318 |

### The live run of 2026-11-15, question by question

| # | Agent asked | Answered | Correct | Right citation | What it cited |
| --- | --- | --- | --- | --- | --- |
| 1 | `nightcap-sme` | Yes | Yes | Yes | The status line of spec 0092. It also said the front matter `status: active` is not an approval |
| 2 | `product-roadmap-sme` | Yes | Yes | No | `docs/product/nightcap-status.md`, which names D-110 and D-111. It did not open the decisions log |
| 3 | `product-roadmap-sme` | Yes | Yes | No | The same status page. It did not open D-111 or the GDD validation page |
| 4 | `nightcap-sme` | Yes | Yes | Yes | The GDD decision ledger, Player count |
| 5 | `arc-execution-sme` | Yes | Yes | Yes | Architecture 1.6 and 3.1 to 3.8 |
| 6 | `product-roadmap-sme` | Yes | Yes | Yes | D-109 by ID and `docs/roadmap/README.md`, Status |
| 7 | `nightcap-sme` | Yes | Yes | Yes | The GDD decision ledger and the Last Call page |
| 8 | `nightcap-sme` | Yes | Yes | Yes | The GDD decision ledger and the Last Call page |
| 9 | `product-roadmap-sme` | Yes | Yes, conflict flagged | No | The reset audit, finding F21. It did not open the documents that name each game |
| 10 | `nightcap-couch-race-sme` | Yes | Yes | Yes | The archived stub. It named ADR-0023 without opening it |

What the run showed beyond the scores:

- **Reading the decisions log works live (D-120).** Asked directly, `product-roadmap-sme` opened `docs/product/decisions-log.csv` and quoted D-109 and D-111 with no refusal.
- **The agent did not open the log on its own.** The session that ran the check started before the D-120 change merged, and the agent reported that its instructions had no "Decisions log" paragraph. The file on disk has it. So whether agents open the log unprompted is still untested. AW-318 reruns questions 2, 3, 6 and 9 in a fresh session.
- **Agents lose tool calls to path guesses.** The roadmap specialist had five calls refused: two Reads at the main checkout's path instead of the session's worktree, and three Grep or Glob calls with the wrong path or output mode. Each agent recovered. AW-318 counts these and proposes a fix; any change to the guard needs a founder exception to the freeze.
- **Time to a cited answer:** 14 to 50 seconds per agent, four agents in parallel.
- **Ranked search has a noise problem of our own making.** The line "Findings and evidence: `docs/product/2026-11-15-reset-audit.md`" is repeated in 26 task and epic files, so a search for the reset audit returns eight task files and not the audit. AW-318.

## Measures

| Measure | How |
| --- | --- |
| Citation accuracy | The score on the ten questions |
| Time to a useful answer | Minutes from question to a cited answer, on the same ten |
| Repeated rework | The founder's weekly tally of things explained twice, plus pull requests reopened |
