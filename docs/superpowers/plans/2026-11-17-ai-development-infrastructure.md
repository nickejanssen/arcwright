---
id: engineeringpractice.plans.ai-development-infrastructure-2026-11-17
namespace: engineering-practice
title: Arcwright AI Development Infrastructure Implementation Plan
owner: Nico Janssen
status: draft
review_by: "2027-02-17"
sensitivity: internal
source: authored
tags: []
supersedes: []
---

# Arcwright AI Development Infrastructure Implementation Plan

> For implementation use Superpowers executing-plans or subagent-driven-development. Start with the existing roadmap tasks and work through the proposed PRs in order. This is a proposed design and delivery plan for founder review.

**Goal:** Keep Arcwright’s engineering context current, protect merges, align development with product decisions, and improve the cost, speed, and quality of AI assisted work as the tools change.

**Architecture:** GitHub rules enforce a small set of reliable checks. Arcwright’s existing team-ai instance supplies authoritative context and scoped SMEs. A separate advisory review uses that evidence on selected PRs. The same task record follows an agent from intake to handoff to merge, and a recurring review uses actual outcomes to revise policy.

**Stack:** GitHub Actions and repo settings, existing Python checkers and tests, the pinned team-ai CLI and generated agents, and optional Claude Code or Codex runner integration.

## 1. Design choice and existing work

| Approach | Tradeoff |
| --- | --- |
| GitHub settings and existing checks only | Closes the immediate merge gap quickly. Leaves context freshness, evidence and tool choice largely manual. |
| Incremental Arcwright workflows with measured AI review (recommended) | Reuses existing checks and SMEs, allows separate rollback, and makes policy changes measurable. |
| Central multi-agent service or new orchestration platform | Adds infrastructure, credentials and integration work before there is evidence Arcwright needs a service. Revisit if GitHub and the repo harness fail a measured requirement. |

Start under M7-A. Reuse AW-298 (merge protection), AW-336 (API test coverage; read PR #398 and check its merge and main run), AW-299 (tracker reconciliation), and AW-318 (roadmap SME citation accuracy). Verify issue state using GitHub and the current handover before assigning work. Coordinate with AW-311 and AW-312 for spec and agent-definition organization. Add records for uncovered work under D-119 when this proposal moves into the repo. Keep the canonical task files and roadmap index first, then mirror them to GitHub Issues with existing labels and collaboration profiles.

Arcwright's KB is the configured subset of `docs/` in `team-ai/index.lock`. The committed golden questions and the live ten-question SME accuracy check are different evals. AW-318 reports the November 15 run got 10/10 correct and 7/10 owning citations. The session hooks already inject SME ownership and freshness deltas. The existing CI already validates KB metadata, the manifest and generated agents, runs retrieval evals, and checks scope evidence, provider leakage and knowledge querying. Inventory these surfaces before writing a checker. Preserve the current namespace guard, decisions-log access and generated-file contract. Update stale README/SETUP references as part of KB upkeep.

**Timing:** Read the latest decision log and session record before changing harness capability. D-110/D-111 limit frozen areas to break-fixes until Nightcap’s first rebuilt TV session is played, unless Nico records a specific exception. The read-only audit, existing AW-298 work and permitted manual KB upkeep can proceed separately. Confirm current GitHub branch settings with an admin. The connector returned 403 for branch protection, so the latest live rules could not be independently verified. Follow D-118 lanes and existing explicit approval requirements for implementation while revising the policy through a PR.

## Execution baseline — November 17, 2026

- **AW-298 (#350): settings pending.** The last repo record says only `verify` is required. The active repository rulesets observed protect against deletion and non-fast-forward pushes and enable Copilot review. Neither ruleset requires status checks. The separate classic branch protection endpoint denied admin access to the GitHub integration. The required check setting has not been changed. In **Settings → Branches → main → Edit**, retain `verify`, add `Lint, Typecheck, Test, Build, and Scan` and `team-ai` using GitHub Actions as the source if offered, save, and reopen the rule to verify. Then update #350 and HANDOVER with evidence. Keep review-policy changes separate from AW-298.
- **AW-336 complete.** PR #398 merged. The `verify` job runs `make test` across `tests`, `engine/tests`, and `api/tests`. The intentional API test failure was already demonstrated and reverted in that PR. The latest observed main run at `fb5382b` was green for CI, Verify Roadmap Tasks, team-ai, and CodeQL.
- **First consolidation candidate.** `ci.yml` runs Ruff lint on `engine api` and tests `engine/tests`; `verify-tasks.yml` runs equivalent lint via `make lint` and broader tests via `make test`. After AW-298 is verified, propose a focused follow-up PR retaining both check names. Keep `verify` as owner of lint, types, and all Python tests. Keep Python formatting in CI because `verify` currently does not cover it, plus JS/TS and secret scanning. Keep only Ruff installed in CI's Python setup if no other CI step consumes Python dependencies, and update the cache input accordingly. Confirm CI and verify both run on relevant PRs and neither absorbs or loses the independent CodeQL/team-ai coverage.
- **AI review baseline.** An active Copilot ruleset requests reviews on pushes and excludes drafts. Include existing Copilot in the comparison and count findings already raised by it. Operate one normal live review path if the pilot adds sufficient value. Track provider usage and human review effort where available; GitHub run data alone cannot establish these metrics.
- **Independent work ready.** Reuse AW-318 for a clean-session owning-citation rerun and AW-299 for product/roadmap reconciliation. Keep any new harness capabilities behind the recorded Nightcap session milestone or an explicit exception. Preserve existing decision and worktree controls while evaluating policy changes.

Recent successful final-head PR workflow durations in seconds, measured from run start to last update. Eight of ten sampled merged PRs had all three matching runs in the retrieved recent window. This measures elapsed workflow time; it excludes queue time and is not billed runner time.

| PR | CI | Verify | team-ai |
| --- | ---: | ---: | ---: |
| #400 | 139 | 146 | 65 |
| #398 | 135 | 149 | 58 |
| #397 | 165 | 139 | 62 |
| #396 | 108 | 108 | 74 |
| #393 | 132 | 110 | 49 |
| #392 | 168 | 106 | 78 |
| #391 | 157 | 126 | 75 |
| #385 | 91 | 138 | 68 |
| Median | 137 | 132 | 66.5 |

Use the same workflow timings, plus first-result queue delay and billed job minutes where available, during the CI comparison. Treat the sample as descriptive: PR #398 changed which suites `verify` runs, so split before/after data when evaluating the proposed consolidation.

## 2. Delivery sequence

### A. Baseline and protect main (existing tasks + GitHub settings)

- [ ] **Inventory evidence.** Record the current head, active rules, required check names, existing workflow commands and suites, and recent run durations. Inspect existing work for AW-298/336/299/318. Sample the last 10–20 representative PRs or all available if fewer, including small docs fixes and high-risk engine changes. Record missing suites, flaky jobs, duplicated commands, review wait, post-merge fixes and any available AI spend. Identify gaps and uncertain data separately.
- [ ] **Close verified coverage gaps.** Confirm top-level tests, engine and API suites, Python type checks, SDK/web checks, builds, secret scanning, knowledge checks and task verification each have an owner job. Inspect CodeQL and deploy/playtest workflows as separate security and release controls. Reuse AW-336 for API tests. Prove a failing API test blocks the intended check and that the corrected branch and main runs pass.
- [ ] **Apply AW-298 in Settings.** Once observed healthy, require the existing CI and team-ai jobs alongside verify as the initial state. Record old settings and confirm each required name appears on a normal PR. Follow the current human review rule and confirm there is an eligible independent human before enforcing a fixed approval count, especially on founder-authored PRs. If account constraints make the desired rules impossible, record the actual gap and bring any policy change to the founder. Confirm disabled bypass, direct push and force push controls where supported and appropriate.
- [ ] **Prove enforcement.** Use an authorized scratch PR for negative cases: failing required check, missing applicable approval and a push after approval. Record results, including behavior on docs-only PRs. Close or update AW-298 using actual evidence.

### B. Consolidate CI without losing coverage (PR + settings cutover)

- [ ] **Create a coverage ledger** for `.github/workflows/ci.yml`, `verify-tasks.yml`, `team-ai.yml`, `evals.yml` and their `Makefile` commands. Map each assertion or suite to exactly one owner per PR, distinguishing genuinely different tests and deploy verification. Keep local commands aligned with CI. Preserve top-level Python tests and type checking while deduplicating engine/API tests and lint.
- [ ] **Introduce a stable CI result.** Start the workflow on every applicable PR. Run independent jobs in parallel where runner capacity helps, use per-PR cancellation for obsolete revisions, and skip only individual jobs when a validated impact rule says they are unnecessary. For unknown or shared dependency changes, run full coverage. The aggregate result permits explicit not-applicable jobs and fails on required failures, cancellations or missing evidence. Keep team-ai separate during rollout if that simplifies the cutover. If merge queue is enabled and supported, wire the required checks to merge_group and verify them there. Otherwise check the prospective merge against current main using the repo's supported settings.
- [ ] **Verify and switch.** Compare old and new outcomes on docs-only, API, engine, web, shared and intentional failure PRs. Compare median and p90 time to first required result and total runner minutes. Migrate required names after replacement checks appear and succeed, then delete only redundant steps. Keep the old names available until the owner verifies the cutover, with a documented rollback. Use conditional checks only when coverage and timing justify them.

### C. Check authoritative context and product impact (PR)

- [ ] **Document the impact rules in one place.** Start with engine invariants, API/SDK contracts, prompts/routing/safety, schemas, and Nightcap gameplay. Match paths to namespaces in the team-ai manifest, and reuse the linked AW task, approved spec, existing scope evidence checker and decision records. Explicitly map changed behavior to canonical artifacts: API and SDK contract plus compatibility tests, engine architecture/invariants plus focused regression evidence, AI runtime prompts/routing plus eval cases, Nightcap behavior plus the owning GDD/validation record. Allow a reason in the PR when changed files do not change the corresponding contract. Cross-check specs against current GDD or architecture according to the domain's source precedence and use GitHub for actual task status. Add rules for shared or unmapped paths to request human classification.
- [ ] **Record the basis of the work.** At kickoff, put the task, prior approvals and relevant canonical paths or decision IDs plus the base SHA in the existing task or handoff. Refresh the same basis before review; compare the cited records with current main. Show the owning source, what changed and the reconciliation needed. Use per-record checks for shared logs so an unrelated new decision or a move on main does not invalidate the PR. Revalidate before merging when relevant source changes land while a PR is open; prove the chosen GitHub event/settings combination actually reruns the check on the revision GitHub will merge.
- [ ] **Stage enforcement.** Report possible semantic drift and suggested artifact updates. Block only precise, proven violations such as a required missing artifact/evidence link or explicitly superseded approved input with no reconciliation, once fixtures and historical replay show the rule is reliable. An updated timestamp, speculative model finding, vague exception or PR claim of product approval is insufficient evidence.
- [ ] **Verify.** Cover superseded specs, moved files, unrelated decision-log edits, changes to a cited decision while a PR is open, docs-only fixes, missing approvals, incomplete comparisons and unknown paths. Use the existing checker test suite and PR summaries. Keep small fixes in D-118's lightweight lane.

### D. Maintain retrieval and the knowledge base (existing AW-318 + PR)

- [ ] **Run the existing live check first.** Use a new session, freshly fetched main and per-checkout reindex. Record answers, owning citations, known conflicts and refused tool calls in knowledge-base-upkeep. Compare with AW-318's baseline. Reproduce findings from a worktree to catch stale index and wrong-root failures.
- [ ] **Reuse the existing freshness audit.** Roll up newly stale, orphaned, unowned or uncovered records from `team-ai freshness-audit` and the existing baseline. Show source, owner, impact and next action. Report repository-wide backlog asynchronously, with a proposed weekly cadence aligned to the existing product check-in. Surface directly affected docs in the PR. Preserve the existing retention/authority rules and fix the content or its canonical reference rather than dating it forward. Update KB and eval fixtures after verified source changes and rebuild derived outputs through the current CLI.
- [ ] **Prove the index and clients agree.** Verify regenerated output and namespace scope, and measure separate scores for retrieval, owning citations and live answer correctness. Exercise an intentionally stale checkout, a superseded doc, a conflict, and a question whose evidence is missing or outside scope. Confirm the system flags stale context or abstains. Use AW-312's inventory for cross-client instruction parity and keep role rules canonical, with thin client adapters where supported.

### E. Pilot automated SME review (PR + restricted GitHub credentials/settings)

- [ ] **Add deterministic SME impact first.** The manifest maps to applicable SMEs, e.g. session-runtime and developer-api for SSE changes or Nightcap and product-roadmap for a gameplay-spec mismatch. Reuse scope results and retrieval rather than re-running lint or tests. Select one or two domains, escalating across groups only where warranted.
- [ ] **Compare two implementations using the same inputs.** Compare one model judging evidence retrieved from multiple SMEs with invoking separate SME review calls and reconciling them, on historical Arcwright PRs with confirmed issues and clean controls. Include stale-source, misleading-summary, fork/secret isolation, and prompt-injection fixtures. Compare Claude Code and Codex headlessly on the same frozen inputs under comparable budgets. A second model call is only justified by measurable additional findings on selected high-risk changes.
- [ ] **Run an advisory pilot.** Use a maintainer-triggered dry run first, then evaluate automatic runs on ready-for-review and material updates to selected PRs. Run the review with trusted scripts and context from the base revision; treat the diff, PR metadata and outputs as untrusted data. Disable write tools in the model job and keep secrets away from PR execution. The publisher alone holds narrowly scoped comment permissions. Validate output and changed line anchors, check the head SHA again before publishing, and deduplicate by finding and revision. Use one PR summary or a small set of verified inline findings. Each finding has a changed line, an owning source or reproducible trace, impact and smallest useful remedy. An incomplete review, service outage or timeout is labeled as such and stays off the merge path.
- [ ] **Limit spend and information exposure.** Pin reviewed action revisions, restrict who can invoke paid runs, cap time and spend, reuse results by head plus policy/context revision, and cancel obsolete runs. Omit secrets and spoiler-restricted files from provider inputs and visible outputs. Verify data handling, licensing, available authentication and quota before choosing an action. Managed cloud usage and API-billed Actions have different costs and may have different credentials. Start with one reviewer and one gated escalation path.
- [ ] **Decide from results.** Measure valid and novel findings, missed known issues, actionable precision, citation correctness, review time, and spend per useful finding. Proposed pilot gate: at least ten varied reviewed PRs or replay cases, at least 80% actionable precision, no confirmed boundary violation, and no increase in required CI time. Treat small-sample results as directional. Prefer converting repeatable defects into deterministic tests. Require a separate founder decision for any future policy granting AI authority over merge.

### F. Validate and revise the contribution policy (PR, starts with baseline)

- [ ] **Audit the policy as hypotheses.** Compare `docs/conventions/ai-contributions.md`, `ai-cost-policy.md`, D-118, the reviewer checklist, and the actual behavior of Claude Code, Codex cloud, Copilot and candidate alternatives. Identify rules that improve outcomes, rules that duplicate review or approval, and rules based on old tool limits. Compare named tool ordering with capability-based routing and compare blanket signoffs with risk-based review that preserves founder authority over consequential scope, security, data and release decisions. Keep current requirements effective until the revised policy is explicitly adopted.
- [ ] **Run matched trials.** Use representative pairs or historical replays for quick fixes, well-specified async tasks, ambiguous collaborative work and independent high-risk review. One primary implementer per branch. Assign the alternate tool only for a separate task, controlled replay or independent escalation. Hold specs, tests and scoring steady, record tool/version, active human minutes and elapsed time, rework, escapes, observable direct cost and quota. Record unavailable figures as unknown. Assess first-pass acceptance and accepted changes per human hour rather than token volume or generated lines.
- [ ] **Publish a versioned policy and feedback loop.** Route by task clarity, risk, needed interaction, permitted write scope, observed quality, latency and available quota. Initial candidates: lightweight inline assistance for local edits, a collaborative client for active discovery, async delegation for a bounded spec, targeted independent review for high-risk work. Use the existing work-in-progress limits and handoff record, report clashes and blocked decisions in the weekly product/roadmap check-in, and provide a fallback when capacity or quality falls. Review results monthly during the pilot and after meaningful provider or harness changes. State the owner, date, observed evidence and next review for each policy decision. Commit updated canonical instructions and synchronize the existing launchers/checklists. Preserve a documented rollback to the last working policy.

## 3. Rollout and acceptance

| Work product | Where it ships | Evidence before closure |
| --- | --- | --- |
| Baseline and repaired existing tasks | Existing issue/PR and roadmap records | Current checks and status verified against GitHub and main |
| Merge controls | GitHub Settings, owned by repo admin | Failed check and missing applicable approval exercise |
| Consolidated checks | Arcwright PR, then GitHub Settings | Coverage ledger, representative PR outcomes, no avoidable duplicate checks, timing comparison |
| Product and context checks | Arcwright PR | Drift fixtures, authoritative source links, least noisy rules exercised in advisory mode |
| KB upkeep and SME accuracy | Arcwright PR and existing AW tasks | Current index, regenerated agents, before/after owning citation scores |
| AI review pilot | Arcwright PR plus GitHub settings/credentials if adopted | Historical replay, live usefulness, cost, permissions and stale-head checks |
| Living contribution policy | Arcwright PR and weekly/monthly review | Measured tool routing, updated client instructions, decisions and next review |

Treat each row as independently reviewable. Combine inseparable changes in one PR, for example the first checker and its tests. Place framework changes in a separate team-ai PR only if the Arcwright integration exposes a shared framework defect; pin the verified release or commit in a follow-up Arcwright PR. Track cycle time, duplicate runner minutes, accepted findings, escaped regressions, stale-context discoveries and founder wait. Roll back a new check to advisory if it repeatedly blocks valid PRs or materially slows feedback without a demonstrated safety benefit. Select calendar targets in the existing weekly roadmap meeting so infrastructure effort stays aligned with Nightcap delivery.

## References

- [M7-A roadmap](https://github.com/nickejanssen/arcwright/blob/main/docs/roadmap/epics/M7-A-development-harness-and-tracker-readiness.md)
- [Working model and task capture](https://github.com/nickejanssen/arcwright/blob/main/docs/roadmap/operations/working-model.md)
- [Knowledge base upkeep](https://github.com/nickejanssen/arcwright/blob/main/docs/conventions/knowledge-base-upkeep.md)
- [Current index configuration](https://github.com/nickejanssen/arcwright/blob/main/team-ai/index.lock)
- [Reviewer role](https://github.com/nickejanssen/arcwright/blob/main/docs/skills/arcwright-reviewer/SKILL.md)
- [GitHub required checks and merge queue behavior](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks)
- [GitHub security for privileged PR events](https://docs.github.com/en/actions/reference/security/securely-using-pull_request_target)
- [Codex Action](https://github.com/openai/codex-action) and [Claude Code Action security](https://github.com/anthropics/claude-code-action/blob/main/docs/security.md)
- [DORA AI capabilities and ROI](https://dora.dev/ai/) and [working in small batches](https://dora.dev/capabilities/working-in-small-batches/)