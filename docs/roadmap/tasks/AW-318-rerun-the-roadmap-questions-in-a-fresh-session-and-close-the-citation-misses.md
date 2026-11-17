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

## Investigation update, 2026-11-17

On main at `07c1985`, a fresh index returned no reset audit in the first eight results for the specified search. Removing the repeated dependency reference from 27 roadmap documents in a local experiment placed the audit fourth; the first three results were sections of this task itself. Shortening the references left the audit outside the first eight. Both changes were discarded because neither met the top-three criterion and removing references also loses useful context.

A further run with the original references retained and `--k 64` did not return the owning audit at all. The lexical retriever ranks sections using BM25 and applies the namespace filter after limiting candidates; the Arcwright wrapper then truncates the widened results to eight lines. Deduplicating sections alone would still leave many distinct task documents ahead of the audit. Adding a descriptive heading to the audit did not put it in the first eight. These are diagnostics, not a validated remedy.\n\nOn the unmodified corpus, the alternative search `founder reset audit 2026-11-15` returned the owning audit first. `reset audit original record` also returned it first; `founder audit findings F29` did not return it in the first three. These are specific observed examples, not proof of general retrieval quality. A trial moving the repeated links to the introductions of the 27 documents still left the audit outside the first eight, so it was discarded.\n\nThe live specialist rerun has not been performed, so there is no new citation score or count of refused calls. Next, investigate a retrieval improvement that preserves useful source links and check it against additional queries, then rerun the four questions in a fresh specialist session. The task remains open.

## Dependencies

- AW-297

## Must Not Do

- Do not edit `.claude/agents/team-ai-*.md` by hand; they are generated.
- Do not change the guard, the hooks or the agent sources without a founder exception to the freeze.
- Do not give the agent the answer or the name of the file to cite.

## Kickoff Prompt

> Read `AGENTS.md`, then `HANDOVER.md`. Task AW-318. Pull main, rebuild the search index, then ask `product-roadmap-sme` questions 2, 3, 6 and 9 from `docs/conventions/knowledge-base-upkeep.md` exactly as written. Score them by the rules in that document and add a dated row. Then do the documentation-only search-noise fix described in the task file. Do not change any agent, guard or hook file; if the scores say one should change, stop and put one question to the founder. Open a pull request using the repository template and report exactly which checks ran.

### Measurement and ownership correction

On 2026-11-17 Nico set a minimum 80% retrieval target and directed that team-ai should serve as a scaffold for Arcwright's own AI infrastructure. PR #407 brought the pinned CLI into Arcwright and moved CI to the local runtime. Inventory its remaining footprint and source authority, preserving namespace isolation, generated agent validation and existing checks. Do not claim that removing the dependency alone improves retrieval.

The 37-question golden report contains 33 answerable questions and four refusal cases. Its hit rate is the fraction of the 33 for which an unscoped deterministic search returns an expected path in the top eight. It is not live agent answer accuracy. Its 100% citation-validity measure checks whether the expected paths resolve, not whether an agent cited the correct source. Its coverage metric checks literal evidence in the source corpus. The 33 answerable questions include two cross-domain questions; each scoped replay below uses the one namespace named in the fixture, so it does not measure full cross-domain behavior.

On the current committed fixtures, a separate replay used each fixture's expected namespace, searched with k=16, removed hits below the CLI's 0.2 score floor and kept the first eight, matching the specialist wrapper's retrieval behavior. Baseline v0.6.6 found the expected path for 27/33 (81.8%); the local retrieval candidate found it for 29/33 (87.9%). The candidate's unscoped golden result was 17/33 (51.5%), below the 80% target. Four scoped misses remain. These are development-set results and must not be treated as independent validation; source files for many fixtures have changed since their question dates and require review.

Acceptance for this work is at least 80% on the existing unscoped and specialist-scoped evaluations, measured separately; 80% or higher on a newly authored independent set that covers the intended use cases; no lowered thresholds or altered expected paths to inflate scores; namespace and refusal safeguards; and repeated measurement with the thresholds ratcheted upward when stable. The current threshold of 45% is historical and should only be raised when the verified implementation reaches the target. Live SME answering and owning-source citation accuracy require separate measured checks.

### Retrieval candidate, 2026-11-17

On main `3f20389` with the candidate retrieval change, a fresh index and the task’s specified search did not return the owning reset audit in the first eight. The namespace-filter change does not close this task: live specialist answers, owning citations, refused calls, independent evaluation and the unscoped 80% target remain outstanding. The oracle-scoped development replay found 29 of 33 expected documents, compared with 27 of 33 on the baseline; the unscoped development replay found 16 of 33, unchanged from the baseline. These are development results, not live specialist or independent accuracy.
