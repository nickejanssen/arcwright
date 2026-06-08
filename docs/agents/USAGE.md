# Using the Arcwright Agents and Skills

A beginner-friendly guide to the roles wired up by spec 0019 and spec 0021, and how to use them in Claude Code, Codex, GitHub Copilot, and the Claude.ai Project chat.

## The one rule that fixes most "I do not see it" problems

These files load when the tool starts. After you `git pull` on `main`, reload or restart the tool (close and reopen, or run "Developer: Reload Window" in VS Code). If a role, command, or skill does not appear, this is almost always the reason.

## Mental model

There are two kinds of role:

- **Doing roles** run inside coding tools (Claude Code, Codex, Copilot): Implementer and Reviewer, plus the Architecture SME for questions.
- **Thinking roles** run in the Claude.ai Project chat: Product Steward, Business Steward, System Architect, Planner, Spec Author, Scribe.

The role logic lives once in `docs/skills/` and `docs/agents/`. Every tool-specific file is a thin launcher that points at those canonical contracts, so all three tools behave the same. To change how a role behaves, edit the canonical file, never the per-tool launcher.

The workflow the roles encode:

```
Intent gate (Product Steward + Business Steward + System Architect agree on a go)
  -> Planner (selects and sequences the next task, assigns an AW-NNN id)
  -> Spec Author (writes docs/specs/NNNN with acceptance criteria)
  -> Implementer (branch, code, PR)
  -> Reviewer (gates the PR)
Scribe records decisions and outcomes throughout.
```

### Which role gets the next task before the Implementer

The **Planner** selects and sequences the next task and assigns its AW-NNN id, after the intent gate has approved a go. The **Spec Author** then ensures the task has a spec, and only then does the **Implementer** pick it up. For a quick "what is next" lookup without full sequencing, the **Architecture SME** can answer from `docs/roadmap/index.json`.

---

## Claude Code

Wired: subagents `implementer` and `reviewer`; commands `/implement`, `/review-pr`, `/scribe`; a shared `.claude/settings.json` that pre-approves lint, test, type, and migrate commands.

First time: pull `main`, then restart Claude Code.

Check it loaded:
- Type `/agents`. You should see `implementer` and `reviewer`.
- Type `/`. You should see `/implement`, `/review-pr`, `/scribe`.

How to use it:
- Implement a task: `/implement AW-123` (or an issue number, or a description). It reads `docs/skills/github-task-implementer/SKILL.md` and runs the branch, plan, code, PR loop. It pauses for plan approval before coding.
- Review a change or PR: `/review-pr` (not `/review`, which is a Claude Code built-in). Or say "Use the reviewer subagent to review my current changes."
- Record a decision: `/scribe we decided X because Y`. It follows the Scribe contract to write or update an ADR.
- Ask architecture questions: the SME loads from `docs/skills/arcwright-sme`. Ask "what does the architecture say about the knowledge graph" and it grounds the answer in `docs/`.

Why permissions do not nag you: `.claude/settings.json` pre-allows ruff, pytest, mypy, make lint/type/test, alembic, and the npm typecheck and build commands.

---

## Codex

Wired: three skills exposed at `.agents/skills/<name>/SKILL.md` (thin pointers into `docs/skills/`): `github-task-implementer`, `arcwright-reviewer`, `arcwright-sme`. Rules come from `AGENTS.md`, which Codex reads automatically.

First time: pull `main`, restart Codex.

Check it loaded: run `/skills`. You should see the three skills.

How to use it:
- Reference a skill with `$name`, for example: "Use $github-task-implementer to implement issue #123", "Use $arcwright-reviewer to review this PR", or "Use $arcwright-sme: which component owns killer assignment?"
- Each skill body tells Codex to open the canonical `docs/skills/.../SKILL.md` and follow it, so behavior matches Claude Code.
- `AGENTS.md` is always on, so the engine constraints and approval gates apply automatically.

---

## GitHub Copilot (VS Code)

Wired: custom agents Implementer, Reviewer, and Arcwright SME (`.github/agents/*.agent.md`); prompts `/implement-task` and `/review-pr` (`.github/prompts/*.prompt.md`); auto-applied path instructions for `engine/**` and `api/**` (`.github/instructions/engine.instructions.md`); and `.github/copilot-instructions.md`, a full mirror of `AGENTS.md` that applies repo-wide including Copilot code review.

First time: pull `main`, use a recent VS Code with GitHub Copilot Chat, then run "Developer: Reload Window".

Check it loaded:
- Open Copilot Chat. The mode or agent dropdown at the top of the Chat view should list Implementer, Reviewer, and Arcwright SME alongside the built-in modes.
- Type `/` in Copilot Chat. You should see `implement-task` and `review-pr`.

How to use it:
- Implement: pick the Implementer agent from the dropdown (or run `/implement-task`), then describe the task. When a PR is ready, use the "Hand off to Reviewer" action the Implementer exposes; it switches you to the Reviewer agent.
- Review: pick Reviewer (or run `/review-pr`). It is read-only by design and reports pass or block with evidence.
- Ask architecture questions: pick Arcwright SME.
- Engine guardrails are automatic: when you edit anything under `engine/` or `api/`, Copilot loads the five engine constraints from `engine.instructions.md`. You do not invoke it.
- Copilot code review on PRs automatically uses `.github/copilot-instructions.md` (the AGENTS.md mirror), which is why that file is kept as a full copy.

---

## Claude.ai Project chat (the thinking roles)

These have no buttons. You invoke them by name in the Project chat, and they read their contract from the repo:

- "Act as the Product Steward (`docs/agents/product-steward.md`): is feature X in MVP scope?"
- "Act as the Business Steward (`docs/agents/business-steward.md`): is X worth building now?"
- "Act as the System Architect (`docs/agents/system-architect.md`): decide the approach for X and draft the ADR."
- "Act as the Planner (`docs/agents/planner.md`): what is the next task and how should it be sequenced?"
- "Act as the Spec Author (`docs/agents/spec-author.md`): write the spec for AW-NNN."
- "Act as the Scribe (`docs/agents/scribe.md`): record this decision as an ADR."

The Architecture SME skill is available here too for grounding. The three deciding roles (Product, Business, Architect) form the intent gate: get their shared go before planning. The System Architect decides design and owns the ADR; the SME only informs.

---

## End-to-end example (one new feature)

1. Project chat: Product Steward confirms scope, Business Steward confirms it is worth it, System Architect approves the approach and notes an ADR. Planner gives it `AW-130` and sequences it. Spec Author writes `docs/specs/00NN-aw-130-...md` with acceptance criteria.
2. Pick one client and implement AW-130, approving its plan before it codes. The command differs per client:
   - Claude Code: `/implement AW-130`
   - Codex: "Use $github-task-implementer to implement AW-130"
   - Copilot: select the Implementer agent (or run `/implement-task`), then describe AW-130
   It branches, codes, runs checks, and opens a PR with per-criterion evidence.
3. Review the PR. Again the command differs per client:
   - Claude Code: `/review-pr`
   - Codex: "Use $arcwright-reviewer to review the PR"
   - Copilot: use the Implementer's "Hand off to Reviewer" action, or select the Reviewer agent, or run `/review-pr`
   It gates against the checklist and `AGENTS.md`.
4. You merge. Scribe records the ADR or outcome.

---

## Troubleshooting

- I do not see the agents or commands: restart the tool after pulling `main`; they load at startup.
- `/review` does the wrong thing in Claude Code: use `/review-pr`. `/review` is a built-in.
- Copilot code review seems to ignore the rules: it reads `.github/copilot-instructions.md` (the mirror), not `AGENTS.md`. The mirror is kept in sync; if you edit `AGENTS.md`, re-sync the mirror.
- Codex skill not found: confirm `.agents/skills/<name>/SKILL.md` exists on your branch and restart Codex. Rules still apply via `AGENTS.md` regardless.
- Golden rule: to change how a role behaves, edit the canonical file in `docs/skills/` or `docs/agents/`, never the per-tool launcher. One edit updates all tools.
