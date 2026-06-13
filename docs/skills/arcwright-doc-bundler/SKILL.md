---
name: arcwright-doc-bundler
description: Generate compact, task-specific or persona-targeted Arcwright documentation bundles for AI agents and humans from canonical repo docs. Use when Codex, Claude Code, GitHub Copilot, ChatGPT, Claude chat, or another agent needs product, architecture, narrative, live-code, persona, all-docs, or custom task brief context optimized for token cost, source freshness, and implementation safety.
---

# Arcwright Doc Bundler

## Overview

Create generated Markdown bundles under `docs-bundles/` that help agents load the smallest useful Arcwright context. Bundles are snapshots and never source of truth. Canonical docs remain under `docs/` plus `AGENTS.md`.

Use compact cited summaries by default. Do not concatenate full docs unless the user explicitly asks for verbatim source text.

## Required Reads

Before generating any bundle:

- Read `AGENTS.md`
- Read `docs/README.md`
- For mode-specific synthesis, read only the smallest canonical files needed
- Do not read `docs/archive/notion-export/` unless the user explicitly asks for source recovery or canonical docs are silent

## Modes

Use these output paths:

| Mode | Output | Primary use |
|---|---|---|
| `product` | `docs-bundles/bundle-A-product-strategy.md` | PRD, product logs, roadmap, decisions, business and strategy |
| `architecture` | `docs-bundles/bundle-B-architecture-specs.md` | Architecture, specs, ADRs, conventions, implementation contracts |
| `narrative` | `docs-bundles/bundle-C-narrative.md` | Story bibles, Nightcap, Monster RPG, narrative rules |
| `live-code` | `docs-bundles/live-code-state.md` | Current branch, code health, blockers, tests, CI, schema snapshot |
| `persona` | `docs-bundles/persona-<persona-slug>.md` | Persona-targeted brief for an AI agent or real-world counterpart |
| `all` | all four standard outputs | Full regenerated standard bundle set |
| custom task brief | user-named output under `docs-bundles/` | Smallest context for one task |

Persona mode supports these persona slugs and common aliases:

| Persona slug | Aliases | Primary use |
|---|---|---|
| `product-lead` | `product`, `product-lead` | Product strategy, portfolio, scope, proof signals |
| `storyteller` | `story`, `narrative`, `storyteller` | Narrative craft, story quality, narrative primitives |
| `developer-stakeholder` | `developer`, `customer-engineer`, `devrel` | API, SDK, integrations, adoption friction |
| `engineering-architecture` | `engineering`, `architecture`, `cto`, `architect` | Technical architecture, determinism, cost, blockers |
| `business-ceo-advisor` | `business`, `ceo`, `advisor`, `investor` | Business strategy, GTM, wedge, proof-gated roadmap |

For custom mode, ask for:

- Task goal
- Token budget or desired bundle size

Then select only the smallest relevant canonical docs. Prefer `docs/roadmap/index.json` to locate roadmap tasks instead of scanning every roadmap file.

## Bundle Requirements

Every generated bundle must include:

- Generated date
- Source git commit
- Purpose and intended AI use
- Manifest of source files used, with repo paths
- Source-of-truth warning that points agents back to canonical docs before implementation
- Compact summaries with file-path citations
- Open questions and unresolved risks
- Explicit exclusions, including `docs/archive/notion-export/`
- Validation results or commands to run

Keep summaries concise. Cite the canonical file path in every summary bullet. Do not copy provider names, concrete model strings, secrets, API key values, local agent state, or archived export paths into the bundle.

## Source Selection

Always include `AGENTS.md` and `docs/README.md` in the source manifest because they define repo rules and doc routing.

Use these default canonical source sets:

- Product: `docs/prd/`, `docs/product/`, `docs/roadmap/00-overview.md`, `docs/roadmap/index.json`, `docs/roadmap/milestones/`, `docs/decisions/`
- Architecture: `docs/architecture/`, `docs/specs/`, `docs/decisions/`, `docs/conventions/`, `docs/skills/`
- Narrative: `docs/story-bibles/`, `docs/prd/03-scope.md`, `docs/product/decisions-log.csv`, `docs/product/open-questions-log.csv`, `docs/decisions/0006-nightcap-continuity-v11.md`
- Live-code: `git status`, current branch, current commit, relevant tests, current blockers, schema files, migration files, specs for active tasks, CI state when available
- Persona: `docs/agents/expert-personas.md` plus the smallest canonical docs mapped to the requested persona

Never use these as bundle sources by default:

- `docs/archive/notion-export/`
- `docs-bundles/`
- `.claude/`, `.codex/`, `.cursor/`, `.vscode/`, `.agents/`, or other local agent state
- Binary files, images, generated caches, dependency folders

## Workflow

1. Confirm the requested mode and output path.
2. Read required docs and mode-specific canonical sources.
3. Run the helper script to generate a safe bundle scaffold and manifest:

   ```bash
   python docs/skills/arcwright-doc-bundler/scripts/doc_bundle_tool.py build --mode product
   ```

4. Replace or tighten scaffolded summary cues with compact synthesis from the selected docs. Preserve file-path citations.
5. For live-code mode, run current repo checks where possible and record exact commands and outcomes. If checks cannot run, state the blocker.
6. Validate the generated bundle:

   ```bash
   python docs/skills/arcwright-doc-bundler/scripts/doc_bundle_tool.py validate docs-bundles/bundle-A-product-strategy.md
   ```

7. Fix validation failures before reporting done.

For all mode:

```bash
python docs/skills/arcwright-doc-bundler/scripts/doc_bundle_tool.py build --mode all
python docs/skills/arcwright-doc-bundler/scripts/doc_bundle_tool.py validate docs-bundles/bundle-A-product-strategy.md docs-bundles/bundle-B-architecture-specs.md docs-bundles/bundle-C-narrative.md docs-bundles/live-code-state.md
```

For custom mode:

```bash
python docs/skills/arcwright-doc-bundler/scripts/doc_bundle_tool.py build --mode custom --task-goal "AW-212 dialogue pipeline implementation" --token-budget 3000
```

For persona mode:

```bash
python docs/skills/arcwright-doc-bundler/scripts/doc_bundle_tool.py build --mode persona --persona storyteller --task-goal "Nightcap narrative critique" --token-budget 4000
```

For a real-world counterpart, add their intended use in `--task-goal`; do not add private or personal data to the bundle.

## Validation Rules

Run validation before completion. Confirm:

- Bundle manifest does not reference old root Notion export paths
- Bundle content does not reference stale story bible filenames such as old murder mystery or monster exports
- Manifest does not include `docs/archive/notion-export/`
- Manifest does not include local agent files or generated bundles
- Bundle does not include secret-looking values or API key assignments
- Bundle does not include concrete provider or model strings
- Bundle points agents back to canonical docs before implementation
- Bundle states generated date and source git commit

Use `rg` for spot checks when not using the helper:

```bash
rg "07-Story-Bible-Murder-Mystery|09-Story-Bible-Monster|docs[\\/]07-|docs[\\/]09-" docs-bundles
rg "(model|provider)\\s*[:=]\\s*['\\\"][^'\\\"]+['\\\"]" docs-bundles
rg "(^|[^A-Za-z0-9])sk-[A-Za-z0-9_-]{16,}|api[_-]?key\\s*[:=]" docs-bundles
```

The generic words "provider", "model", "API key", and agent names such as Claude Code can appear in warnings or validation descriptions. Concrete provider names, model slugs, and secret values cannot.

## Reporting

When complete, report:

- Bundle files created or updated
- Source commit used
- Validation commands and results
- Acceptance criteria satisfied
- Any skipped checks or unresolved risks

Do not claim bundles are authoritative. Tell the next agent to return to canonical docs before implementation.
