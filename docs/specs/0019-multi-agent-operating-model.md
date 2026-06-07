# Multi-Agent Operating Model and Cross-Client Wiring

**Status**: Draft

**Author**: Claude Code | **Date**: 2026-06-07

---

# References

- Related ADRs: `docs/decisions/0001-scaffolding-audit.md` (items 1.14, 2.7, 3.5, 3.6), `docs/decisions/0002-harness-scenario-execution-contract.md` (pre-existing `make type` failure, do not touch)
- Architecture sections: `docs/architecture/15-development-guide.md`
- Convention files: `docs/conventions/ai-contributions.md`, `docs/conventions/ai-cost-policy.md`, `docs/conventions/review-checklist.md`
- Related specs: `docs/specs/0018-github-task-implementer-skill.md` (precedent for an untracked, spec-numbered tooling change), `docs/specs/0005-scaffolding-remediation.md`, `docs/specs/0006-roadmap-organization.md`
- Existing skill: `docs/skills/github-task-implementer/` (reuse, do not recreate)
- Operating model reference: `docs/roadmap/operations/working-model.md` (AW-NNN handoff conventions)
- PRD sections: `docs/prd/01-overview.md` (development-process linkage only)

## Step 1 due diligence findings folded into this spec

- The four instruction surfaces currently diverge. `CLAUDE.md` and `AGENTS.md` are byte-identical and carry the workflow plus the five engine constraints. `.github/copilot-instructions.md` and `.cursorrules` are byte-identical to each other and carry eight architecture principles, but not the workflow, approval gates, agent-local-file rules, or ADR protocol. No single file is authoritative today. (ADR 0001 items 1.14, 3.5, 3.6.)
- The five non-negotiable engine constraints (ADR 0001 item 1.14) are: Python 3.11+ minimum; arc execution logic stays in Python (no arc logic in TypeScript); a knowledge-state query is mandatory before every AI character generation call; provider and model strings appear only in `config/routing_table.json` and `engine/routing/router.py`; safety is enforced at the engine layer and cannot be bypassed by arc configuration.
- `github-task-implementer` exists at `docs/skills/github-task-implementer/` with `SKILL.md`, `agents/openai.yaml`, and `references/response-contracts.md`. It is the Implementer contract and must be reused as-is.
- `arcwright-sme` and `arcwright-task-runner` are not present as files under `~/.claude` or `~/.codex`. They load through the `anthropic-skills:` plugin namespace. There is no local source file to copy, so the SME content must be captured from the running skill or supplied by the founder during Phase B. `arcwright-task-runner` overlaps the Implementer role already covered by `github-task-implementer` and is not mirrored separately.
- `review-checklist.md` exists at `docs/conventions/review-checklist.md` and is the source for the Reviewer skill.
- CI (`.github/workflows/ci.yml`), CodeQL (`.github/workflows/codeql.yml`), Evals (`.github/workflows/evals.yml`), and `.pre-commit-config.yaml` do not reference any instruction or skill file by path. Consolidation will not break them.
- Client mechanism verification (2026-06-07): Claude Code subagents at `.claude/agents/*.md` with YAML frontmatter (`name`, `description` required) are confirmed against `https://code.claude.com/docs/en/sub-agents`. Copilot repo instructions (`.github/copilot-instructions.md`), path instructions (`.github/instructions/*.instructions.md` with `applyTo`), `AGENTS.md` support, and VS Code `.github/agents/*.agent.md` are confirmed against current GitHub and an existing in-repo example (`.github/agents/Plan.agent.md`). All `developers.openai.com/codex/*` documentation URLs returned 404, and the `codex` binary is not on PATH in this environment, so Codex paths are taken from the founder's re-verified guidance (`.agents/skills/<name>` discovery scanned cwd-upward following symlinks, plus `AGENTS.md` as the always-on source) rather than from official docs.
- In-flight M1 work (AW-112 deterministic replay and batch runner, issue 24; M1-E harness epic, issue 25) touches only `engine/harness/` and `engine/tests/`. This spec touches no engine, api, sdk, dashboard, migrations, or nightcap code, so there is no overlap.

---

# Overview

Establish one canonical definition per development role plus thin per-client launchers so Claude Code, Codex, and GitHub Copilot behave consistently against the same role contracts and the same always-on rules. This consolidates the four competing instruction surfaces flagged in ADR 0001 into one authoritative source (`AGENTS.md`) with pointers, without losing any existing rule, and wires the Implementer and Reviewer roles into all three clients using formats each client reads natively.

---

# In Scope

- Make `AGENTS.md` the single authoritative always-on instruction file. Migrate every existing rule into it, especially the five non-negotiable engine constraints (ADR 0001 item 1.14) and the eight architecture principles currently in `.github/copilot-instructions.md` and `.cursorrules`. Reduce `CLAUDE.md`, `.github/copilot-instructions.md`, and `.cursorrules` to thin pointers.
- Canonical role contracts:
  - Implementer: reuse the existing `docs/skills/github-task-implementer` skill unchanged.
  - Reviewer: new `docs/skills/arcwright-reviewer/` skill derived from `docs/conventions/review-checklist.md`, with `SKILL.md` and `agents/openai.yaml` matching the github-task-implementer shape.
  - Architecture SME: ensure an `arcwright-sme` skill exists in-repo under `docs/skills/`, with content captured from the existing user-level skill (not re-authored from scratch).
  - Thinking roles (Product Steward, Planner, Spec Author, Scribe): contracts in `docs/agents/*.md`, used primarily in the Claude.ai Project chat.
  - `docs/agents/README.md` describing the operating model, the pipeline (Product Steward to Planner to Spec Author to Implementer to Reviewer, with SME consulted at every gate and Scribe recording outcomes), and the AW-NNN handoff key.
- Per-client launchers (thin; reference canonical contracts only, no role logic of their own):
  - Claude Code: `.claude/agents/implementer.md` and `.claude/agents/reviewer.md` thin subagents; `.claude/commands/` entries for `/implement`, `/review`, `/scribe`; a tracked `.claude/settings.json` granting the skills and the lint, type, test, and migrate command allowances (separate from the local-only, untracked `.claude/settings.local.json`).
  - Codex: expose each canonical skill to Codex via `.agents/skills/<name>` pointing at `docs/skills/<name>` so there is one source with two discovery paths; rely on `AGENTS.md` as the instruction source. The `.codex/agents/reviewer.toml` native custom agent is deferred (see Out of Scope) until its schema can be confirmed against the installed CLI.
  - Copilot: `.github/agents/implementer.agent.md`, `.github/agents/reviewer.agent.md`, and `.github/agents/arcwright-sme.agent.md` with an Implementer-to-Reviewer handoff; `.github/prompts/implement-task.prompt.md` and `.github/prompts/review-pr.prompt.md`; `.github/instructions/engine.instructions.md` scoped to `engine/**` and `api/**`.
- A migration diff documenting every rule moved, proving none were dropped.
- Cross-client verification that each client loads the roles.

---

# Out of Scope

- Any change to `engine`, `api`, `sdk`, `dashboard`, `migrations`, or `nightcap` code.
- Any M1 platform task in flight, including AW-112 and the M1-E harness work.
- The `.codex/agents/reviewer.toml` native Codex custom agent. The Codex documentation is unreachable and the CLI is not available to confirm the TOML schema, so this is recorded as a deferred follow-up rather than guessed at.
- Cost or Telemetry Watchdog, a standing QA or Test Strategist role, a narrative-authoring agent, and a DevOps or Infra agent. These were assessed as cost-exceeds-value at this stage and are deliberately not created.
- New runtime dependencies.
- Fixing the pre-existing `make type` failure (tracked in ADR 0002).
- Filling in the stub `docs/conventions/coding-style.md` and `docs/conventions/testing.md` (each is a five-line stub today; a separate task if desired).
- Creating an AW roadmap task ID or a `docs/roadmap/index.json` entry for this work (see Open Question 1, resolved).

---

# Acceptance Criteria

- [ ] `AGENTS.md` is the single authoritative always-on file and contains, verbatim or stronger, the five non-negotiable engine constraints (Python 3.11+, arc logic stays in Python, mandatory knowledge-state query before every AI generation call, provider and model strings only in `config/routing_table.json` and `engine/routing/router.py`, safety enforced at the engine layer).
- [ ] `AGENTS.md` also contains the eight architecture principles previously held only in `.github/copilot-instructions.md` and `.cursorrules`, plus the workflow, approval gates, agent-local-file rules, and ADR protocol previously held only in `CLAUDE.md` and `AGENTS.md`.
- [ ] `CLAUDE.md`, `.github/copilot-instructions.md`, and `.cursorrules` contain only a pointer to `AGENTS.md` and `docs/agents/`, with no independent rule or role logic. (If Open Question 2 resolves to retire Cursor, `.cursorrules` is deleted instead, and that deletion is recorded in the migration diff.)
- [ ] A migration diff in the Phase A PR lists every rule moved and confirms none were dropped.
- [ ] `docs/skills/arcwright-reviewer/SKILL.md` exists, derived from `review-checklist.md`, with `agents/openai.yaml` present.
- [ ] An `arcwright-sme` skill exists in-repo under `docs/skills/`, with content captured from the existing user-level skill rather than re-authored.
- [ ] `docs/agents/` contains contracts for Product Steward, Planner, Spec Author, and Scribe, plus a `README.md` defining the pipeline and the AW-NNN handoff protocol.
- [ ] Claude Code: `.claude/agents/implementer.md` and `.claude/agents/reviewer.md` exist as thin launchers; `/implement`, `/review`, and `/scribe` commands exist; `/agents` lists the subagents.
- [ ] Codex: the canonical skills are discoverable by Codex (via `.agents/skills/<name>`); `/skills` lists Implementer, Reviewer, and SME.
- [ ] Copilot: the three `.agent.md` files exist with an Implementer-to-Reviewer handoff; the two `.prompt.md` files exist; `engine.instructions.md` applies to `engine/**` and `api/**`.
- [ ] No client launcher file contains role logic; each references the canonical skill or `docs/agents` contract.
- [ ] Existing CI workflows (`ci.yml`, `codeql.yml`, `evals.yml`) and pre-commit still pass, and no reference to a moved or renamed file is broken.
- [ ] No em dashes appear in any created or modified file.
- [ ] Every acceptance criterion is verified with per-criterion evidence in the relevant phase PR.

---

# Implementation Phases

One PR per phase, in order. Each is independently reviewable and reversible. Each PR follows the github-task-implementer loop: branch, implement only that phase, run checks, open a PR with per-criterion evidence, then wait for review.

Phase A, Canonical consolidation. Build `AGENTS.md` as the authoritative file; migrate all rules from `CLAUDE.md`, `.github/copilot-instructions.md`, and `.cursorrules`; reduce those three to pointers (or delete `.cursorrules` per Open Question 2); include the migration diff and this spec file. No client behavior change yet. Lowest risk, unblocks everything.

Phase B, Role contracts. Create the `arcwright-reviewer` skill from `review-checklist.md`; bring `arcwright-sme` in-repo with content captured from the existing skill; write the `docs/agents/` contracts for the thinking roles and the `README.md` operating model. No client wiring yet.

Phase C, Claude Code wiring. Thin subagents, commands, and tracked `settings.json`, referencing Phase B contracts.

Phase D, Codex wiring. Expose skills via `.agents/skills/<name>`; confirm `/skills` discovery; confirm `AGENTS.md` is the instruction source. The native reviewer TOML stays deferred.

Phase E, Copilot wiring. Custom agents with the Implementer-to-Reviewer handoff, prompt files, and the path-scoped engine instructions.

Phase F, Cross-client verification. Run the load checks and the acceptance criteria end to end; route one no-op or real ticket through each client to confirm the Implementer and Reviewer roles load and reference the canonical contract.

---

# Test Plan

- Static: grep `AGENTS.md` for the five constraints and the eight principles; grep the pointer files to confirm no stray rule or role logic; grep all created and modified files for em dashes; run `.pre-commit-config.yaml` hooks and the CI command set locally (`python -m ruff check engine api`, `python -m ruff format --check engine api`, `pytest engine/tests`, SDK and dashboard typecheck and build).
- Migration integrity: diff the pre-change instruction files against the new `AGENTS.md` to prove no rule was lost; attach the diff to the Phase A PR.
- Client load: `/agents` (Claude Code), `/skills` (Codex), the Copilot agents picker plus the Implementer-to-Reviewer handoff.
- End to end: route one ticket (a no-op is acceptable) through each client to confirm the Implementer and Reviewer roles load and point at the canonical contract.

---

# Risks and Unknowns

**Risks**:
- Over-consolidation could silently drop a rule. Mitigated by the migration-diff acceptance criterion and a line-by-line diff in Phase A.
- Codex client mechanisms could not be confirmed against official docs (all `developers.openai.com/codex/*` URLs return 404) or against the CLI (the `codex` binary is not on PATH in this environment). The `.agents/skills/` discovery path is taken from founder guidance and must be confirmed empirically in Phase D before the phase is claimed done; if discovery differs, match the mechanism that already makes `github-task-implementer` work.
- The `.agents/skills/<name>` symlink approach depends on symlink support. On Windows, git symlink checkout requires `core.symlinks=true` and may need elevated privileges or Developer Mode. If symlinks are not viable in this repo, Phase D will fall back to a confirmed alternative (for example a copy kept in sync, or whatever mechanism already serves the existing skill) and record the choice.
- `arcwright-sme` has no local source file; its content lives in the `anthropic-skills:` plugin namespace. If the running skill cannot be captured faithfully, the founder must supply the canonical text so Phase B mirrors rather than re-invents it.
- Reducing `CLAUDE.md` to a pointer changes Claude Code's canonical instruction file from `CLAUDE.md` to `AGENTS.md`. Claude Code does load `AGENTS.md`, but this must be confirmed in Phase C so no always-on rule silently stops loading.

**Unknowns**:
- Whether VS Code Copilot in this environment treats `AGENTS.md` as always-on in addition to `.github/copilot-instructions.md`. Confirm during Phase E.
- Whether the founder still uses Cursor (see Open Question 2).

---

# Open Questions

1. Tracker placement. RESOLVED: ship as this numbered spec plus phased PRs, identified by the spec number. Do not create an AW roadmap task and do not add a `docs/roadmap/index.json` entry. Rationale: the AW and roadmap system is the execution layer for platform-build work tied to a milestone exit gate (M1 through M6); this is meta-tooling that belongs to no gate. The established pattern for infra and tooling work is a numbered spec plus PRs with no AW ID (specs 0001 through 0008 and 0018). This work is a sibling of 0018, so it matches that precedent. The Implementation Phases section is the tracking checklist; each phase PR references this spec file.
2. Retire or keep `.cursorrules`. Is Cursor still part of the toolchain? If yes, `.cursorrules` becomes a thin pointer in Phase A. If no, the pointer is replaced with deletion in Phase A, recorded in the migration diff. Recommendation: keep it as a thin pointer (non-destructive and reversible) unless the founder confirms Cursor is retired. This is the one decision still needed before Phase A begins.
