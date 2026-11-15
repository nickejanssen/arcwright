---
id: productroadmap.roadmap.tasks.aw-296-fix-the-knowledge-base-agent-guard-in-worktree-sessions
namespace: product-roadmap
title: "AW-296: Fix The Knowledge-Base Agent Guard In Worktree Sessions"
owner: Nico Janssen
status: active
review_by: "2027-02-15"
sensitivity: internal
source: authored
x-scope-evidence: none
tags: []
supersedes: []
---

# AW-296: Fix The Knowledge-Base Agent Guard In Worktree Sessions

**Milestone / Epic:** M7 / M7-A  
**Size:** S  
**Product:** Shared (Arcwright and Nightcap)  
**Owner:** One AI build session (Claude or Codex)  
**Target date:** 2026-11-18

## Plain-English Summary

The specialist knowledge-base agents refuse every search when a session runs in a git worktree, which is how every desktop session runs. Fix the guard so the agents can read `docs/` again, and prove it with a test.

## Why This Matters

On 14 November 2026 three of three specialist-agent probes returned nothing. Every answer the agents should have given was instead read by hand, and work was duplicated because of it. Until this is fixed the knowledge base is not usable from the sessions that do the work.

## Technical Scope

- `scripts/hooks/guard_kb_agents.py`: `paths()` takes the repository root from the hook file's own location (`Path(__file__).resolve().parents[2]`). When the hook is registered from the main checkout and the agent's working directory is a worktree, `resolve(raw, cwd)` joins the relative path `docs` to the worktree, and `within(kb_root)` then fails because `kb_root` points at the main checkout.
- Observed refusal text: `Refused: search only under docs/. Pass path: "docs".`
- Ranked search in the same sessions reports `index not built - run 'team-ai reindex' first`. Decide in this task whether that has the same cause; if it does not, leave it to AW-297.
- Tests live in `scripts/hooks/tests/test_hooks.py`.

## Human Collaboration Contract

**Interaction profile:** Independent execution. This is a break-fix allowed under the tooling freeze (D-110, D-111). The founder's merge of the pull request is the approval gate.

## Acceptance Criteria

- [ ] A new test reproduces the refusal with the hook file in one checkout and the agent working directory in a worktree of the same repository, and fails before the fix.
- [ ] From a worktree, a specialist agent's Grep, Glob and Read under `docs` are allowed.
- [ ] A search or read outside the knowledge-base root is still refused, from the main checkout and from a worktree.
- [ ] Three specialist agents, asked one known-answer question each from a worktree session, each return an answer that cites a file.

## Tests/Verification

- `python -m pytest scripts/hooks/tests -q`
- Three live agent probes from a worktree session, results pasted into the pull request.

## Dependencies

- None
- Findings and evidence: `docs/product/2026-11-15-reset-audit.md`

## Must Not Do

- Do not add any new agent capability, tool or hook.
- Do not widen what the agents may read beyond the knowledge-base root.
- Do not hand-edit `.claude/agents/team-ai-*.md`; they are generated.

## Kickoff Prompt

> Read `AGENTS.md`, then `HANDOVER.md`. Task AW-296: fix `scripts/hooks/guard_kb_agents.py` so knowledge-base agents work when the session runs in a git worktree. Reproduce the refusal first with a failing test in `scripts/hooks/tests/test_hooks.py`, then fix it. This is a break-fix under D-110 and D-111: restore behaviour, add no capability. Open a pull request using the repository template and report exactly which checks ran.
