---
id: productroadmap.roadmap.tasks.aw-318-rerun-the-roadmap-questions-in-a-fresh-session-and-close-the-citation-misses
namespace: product-roadmap
title: "AW-318: Rerun The Roadmap Questions In A Fresh Session And Close The Citation Misses"
owner: Nico Janssen
status: active
review_by: "2027-02-15"
sensitivity: internal
source: authored
x-scope-evidence: none
tags: []
supersedes: []
---

# AW-318: Rerun The Roadmap Questions In A Fresh Session And Close The Citation Misses

**Milestone / Epic:** M7 / M7-A
**Size:** S
**Product:** Shared (Arcwright and Nightcap)
**Owner:** One AI build session (Claude or Codex), started after 2026-11-15
**Target date:** 2026-11-21

## Plain-English Summary

The live accuracy check of 15 November 2026 scored 10 of 10 correct but only 7 of 10 with the right citation. All three misses were the roadmap specialist citing a summary page instead of the decision that owns the answer. Rerun those questions in a fresh session, find out whether the agent now opens the decisions log by itself, and fix or file whatever is left.

## Why This Matters

A correct answer with the wrong source cannot be trusted next month, when the summary page has gone stale. The founder's instruction of 15 November (D-120) was that agents reach for the decisions log on their own. The live check could not prove that, because the session running it had loaded the agent instructions before the D-120 change merged.

## Technical Scope

- Start a new session after pulling main. Rebuild the index in that checkout: `python scripts/team_ai_cli.py reindex --root team-ai`.
- Ask `product-roadmap-sme` questions 2, 3, 6 and 9 from `docs/conventions/knowledge-base-upkeep.md`, as written, with no hints. Record whether it opens `docs/product/decisions-log.csv` unprompted and what it cites.
- Add a dated row and the per-question detail to the Results section of that document.
- Count refused tool calls per agent (wrong root path, wrong Grep output mode). On 15 November the roadmap specialist lost five calls this way, two of them Reads at the main checkout's path instead of the session's worktree.
- Search noise: the line "Findings and evidence: `docs/product/2026-11-15-reset-audit.md`" is repeated in the Dependencies section of 26 task and epic files, so the ranked search `reset audit findings owner` returns eight task files and not the audit. Remove or shorten that line in those files (documentation only), re-copy the affected issue bodies, rebuild the index and show the audit in the top three results.

## Human Collaboration Contract

**Interaction profile:** Independent execution for the rerun, the scoring and the documentation fix. Decision interview for anything else: a change to an agent source under `team-ai/agents/`, to the guard's refusal text, or to any hook is new capability under the tooling freeze (D-110, D-111) and needs an explicit founder exception, recorded in the decisions log, before it is made.

## Acceptance Criteria

- [ ] Questions 2, 3, 6 and 9 are rerun in a session started after PR #376 merged, and the row is committed.
- [ ] The row states plainly whether the agent opened the decisions log without being told to.
- [ ] If any citation still misses, a proposal names the agent source or document to change and is put to the founder as one question.
- [ ] The count of refused tool calls per agent is recorded, with a proposed fix or a reason to leave it.
- [ ] The ranked search `reset audit findings owner` returns `docs/product/2026-11-15-reset-audit.md` in its top three results.

## Tests/Verification

- The score row in `docs/conventions/knowledge-base-upkeep.md`.
- `python scripts/team_ai_cli.py search --root team-ai --namespace product-roadmap --k 8 "reset audit findings owner"` output pasted into the pull request.
- The `team-ai` check passes on the pull request.

## Dependencies

- AW-297

## Must Not Do

- Do not edit `.claude/agents/team-ai-*.md` by hand; they are generated.
- Do not change the guard, the hooks or the agent sources without a founder exception to the freeze.
- Do not give the agent the answer or the name of the file to cite.

## Kickoff Prompt

> Read `AGENTS.md`, then `HANDOVER.md`. Task AW-318. Pull main, rebuild the search index, then ask `product-roadmap-sme` questions 2, 3, 6 and 9 from `docs/conventions/knowledge-base-upkeep.md` exactly as written. Score them by the rules in that document and add a dated row. Then do the documentation-only search-noise fix described in the task file. Do not change any agent, guard or hook file; if the scores say one should change, stop and put one question to the founder. Open a pull request using the repository template and report exactly which checks ran.
