# Arcwright Doc Bundler Skill

**Status**: Done

**Author**: Codex | **Date**: 2026-06-13

---

# References

- Related docs: `AGENTS.md`, `docs/README.md`
- Architecture sections: `docs/architecture/13-cost-model.md`, `docs/architecture/15-development-guide.md`
- Related specs: `docs/specs/0029-docs-organization.md`
- PRD sections: `docs/prd/01-overview.md`, `docs/prd/03-scope.md`
- Related conventions: `docs/conventions/ai-cost-policy.md`, `docs/conventions/ai-contributions.md`

---

# Overview

Add a repo-tracked, platform-neutral skill for generating compact, task-specific Arcwright documentation bundles for AI agents and humans without treating generated bundles as source of truth.

---

# In Scope

- Add a canonical skill at `docs/skills/arcwright-doc-bundler/`
- Add a thin Codex launcher at `.agents/skills/arcwright-doc-bundler/`
- Support bundle modes for product, architecture, narrative, live-code, persona, all, and custom task brief
- Define source selection rules that prefer canonical current docs and skip archived Notion exports by default
- Require generated bundles to include date, source commit, intended use, manifest, source-of-truth warning, compact cited summaries, open questions, unresolved risks, and explicit exclusions
- Add reusable script support for bundle scaffolding and validation
- Keep the skill usable by Codex, Claude Code, GitHub Copilot, or another coding agent that can read repository files and run local commands

---

# Out of Scope

- Committing generated files under `docs-bundles/`
- Replacing canonical docs with generated summaries
- Reading `docs/archive/notion-export/` by default
- Adding dependencies
- Running external AI services from the helper script
- Changing product scope, architecture, schemas, prompts, routing, or eval behavior

---

# Acceptance Criteria

- [x] Repo contains `docs/skills/arcwright-doc-bundler/SKILL.md`
- [x] The skill is platform-neutral and directly usable by Codex, Claude Code, and GitHub Copilot
- [x] The skill requires `AGENTS.md` and `docs/README.md` before bundle generation
- [x] The skill supports product, architecture, narrative, live-code, persona, all, and custom task brief modes
- [x] The skill directs custom mode to ask for task goal and token budget before selecting sources
- [x] The skill directs persona mode to use `docs/agents/expert-personas.md` and persona-specific canonical docs
- [x] The skill tells agents to use the smallest relevant canonical docs and skip `docs/archive/notion-export/` by default
- [x] Generated bundle requirements include date, commit, purpose, manifest, source warning, cited compact summaries, open questions, risks, and exclusions
- [x] Validation covers stale Notion paths, stale story bible filenames, archive manifest references, secrets, provider or model strings, local agent files, and canonical-doc reminders
- [x] A reusable helper script exists under `docs/skills/arcwright-doc-bundler/scripts/`
- [x] A thin launcher exists at `.agents/skills/arcwright-doc-bundler/SKILL.md`
- [x] No new dependencies are added

---

# Test Plan

- Validate the skill with `python C:\Users\nicke\.codex\skills\.system\skill-creator\scripts\quick_validate.py docs\skills\arcwright-doc-bundler`
- Run the helper script for at least one representative mode
- Run helper validation against the generated bundle
- Inspect generated output for canonical source warnings, manifest paths, exclusions, and provider or model redaction
- Run `rg` checks against the skill files for stale story bible filenames and old root Notion export paths

---

# Risks and Unknowns

**Risks**:
- Generated summaries can drift if agents treat bundles as canonical instead of disposable snapshots.
- A fully verbatim bundle can become too large and can reintroduce stale context when reused after docs change.
- Live-code state can drift quickly and must always be regenerated from the current branch.

**Unknowns**:
- Whether future docs will need a separate business or investor bundle mode.
- Whether generated bundles should ever be committed, or remain local generated artifacts only.

---

# Open Questions

- Should `docs-bundles/` be gitignored once the generated-output policy is finalized?
