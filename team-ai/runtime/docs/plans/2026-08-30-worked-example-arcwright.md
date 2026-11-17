# Worked example: `team-ai init` against `github.com/nickejanssen/arcwright`

**Purpose:** Show, concretely, what the planned framework would do if run against a real,
mature repo — before we build it. Arcwright is a good stress test because it already has
most of what `team-ai` offers.

> This is an illustration derived from the plan
> (`docs/plans/2026-08-30-team-ai-framework.md`) and the current state of the Arcwright
> repo. No code has run; this is what the plan *specifies*.

---

## What preflight finds in Arcwright (Task 23)

`team-ai init` (run from the repo root) starts with `scanPreflight(".")`:

| Signal | Found in Arcwright | Consequence |
|---|---|---|
| Agent config | `AGENTS.md` (authoritative), `CLAUDE.md` (imports it), `.claude/` (`agents/implementer.md`, `agents/reviewer.md`, `commands/`, `settings.json`), `.github/copilot-instructions.md` (mirror), `.codex/`, `.agents/` | **Harness exists → EXTEND.** Adopt `AGENTS.md`; do not create a parallel config |
| Existing router / SME | `docs/skills/arcwright-sme/SKILL.md` — a full SME with its own source-of-truth hierarchy that already routes questions to `docs/` | `existingAssets.routerAgent` set → **no `sme` router generated**; reconciliation halt triggered |
| Role agents | `.claude/agents/{implementer,reviewer}.md` + `docs/agents/` (9 role contracts: product-steward, planner, spec-author, scribe, system-architect, business-steward, …) | Adopted as-is; no role subagents generated |
| Skills | `docs/skills/` (9: arcwright-sme, arcwright-reviewer, github-task-implementer, arcwright-doc-bundler, arcwright-playtest-\*, arcwright-minigame), `skills-lock.json`, `.claude/commands/` | Adopted; `agents.skills` catalog offered but pre-checked core skills only |
| Model routing | `config/routing_table.json` + `engine/routing/router.py` — task-type × quality-tier routing to Anthropic/Groq | Already matches `team-ai` architecture principle 8. **Not touched.** |
| MCP servers | No `.mcp.json`, `.cursor/mcp.json`, or `.vscode/mcp.json` in-repo | Nothing to register against; `arch.hosting` stays `no-server` |
| Vector store | `.env.example` has Postgres + Firebase + LiteLLM only — no `PINECONE_*`/`WEAVIATE_*`/`QDRANT_*` | `arch.index_driver` → `lexical` |
| Existing KB | `docs/` — 667 markdown files across `prd/ architecture/ story-bibles/ roadmap/ specs/ decisions/ product/ conventions/`, with a documented source-of-truth hierarchy and versioning policy in `docs/README.md` | **Overlap detected** → `pre.overlap` question fires |
| Existing eval harness | `evals/` (`cases/`, `runners/`, `reports/`, `continuity_thresholds.json`) | `team-ai`'s `evals/golden/` would be conceptually adjacent; flagged in the overlap note |

### Assessment: **EXTEND, with a strong overlap warning**

```
PREFLIGHT

Found
  ✓ Agent config: AGENTS.md (authoritative), CLAUDE.md, .claude/, .github/copilot-instructions.md
  ✓ Existing SME: docs/skills/arcwright-sme/SKILL.md  (routes questions to docs/ already)
  ✓ 9 role contracts under docs/agents/, 9 skills under docs/skills/
  ✓ Model routing already abstracted: config/routing_table.json
  ✗ No in-repo MCP server config
  ✗ No vector store
  ? docs/ is already a curated 667-file knowledge tree with its own
    source-of-truth hierarchy and an SME that routes to it

Assessment: EXTEND
  A compatible harness exists. Register alongside it and adopt AGENTS.md
  rather than creating a parallel config.

Overlap worth checking: docs/skills/arcwright-sme/SKILL.md already does the
routing job team-ai's `sme` router would do, over the same docs/. Standing up
a second router beside it is duplication. What Arcwright does NOT have:
  - per-file front matter (id / owner / review_by / sensitivity) on docs
  - a ranked retrieval index with enforced citations
  - a coverage-gap log fed by unanswered questions
  - a freshness audit keyed to review dates
  - CI gates on retrieval hit-rate / routing accuracy / refusal behaviour
Recommended: scale back to that deterministic quality layer only.
```

### Connector probe (Task 23)

No in-repo GitHub/Drive **connector** config, so the probe prints its manual-run
instructions into `docs/preflight.md` and records nothing. **No model call.**

---

## The interview, given those findings

- **Act 0:** `pre.assessment` pre-filled `extend`. `pre.overlap` fires → options:
  *build anyway* / *contribute to existing docs and skip the index* / *decide later*.
- **Act 1:** `mode = instance`, `ctx.org_path = nickejanssen`, `team.name = Arcwright`,
  `team.surfaces = [coding agent]`, `team.sources = [GitHub]`, `team.consumers = [engineers]`.
- **Act 2:** `kb.substrate = md-git` (already true). `kb.namespaces = custom` — Arcwright's
  `docs/` shape (`prd/ architecture/ story-bibles/ roadmap/ specs/ decisions/ product/
  conventions/`) matches none of the four presets, so the generator writes
  `catalog/namespaces/arcwright.yaml` **as a stub with `# TODO:` blocks** — it never
  guesses a mapping.
- Many Arcwright docs carry `> Source: … > Do not edit this file directly; edit in Notion
  and re-sync.` — these map to `source: synced:notion` in `team-ai` front matter:
  read-only here, fixed at the source. The interview's `kb.sources_strategy` question
  captures that.
- **Act 3:** `arch.index_driver = lexical`, `arch.hosting = no-server`,
  `arch.language = —` (n/a; the instance carries no code), `arch.ci = GitHub Actions`,
  `arch.topology = single repo for now`.
- **Act 4:** `agents.roles` is **suppressed** (existing role contracts adopted).
  `agents.domains` — operator could name 1–3 (e.g. `engine`, `nightcap`); each becomes a
  manifest entry, **not** a new SME. `agents.strictness = refuse-log-gap`.
  `agents.seed = "I will write my own"` (docs already exist).

---

## Reconciliation — the part that protects existing work (design §18, Task 32)

Before writing **anything**, `init` computes a dry render plan against an empty
`generated_paths` manifest (first run) and finds collisions:

```
RECONCILE — existing work detected, nothing written yet

Adopting (extend — kept exactly as-is):
  AGENTS.md
  CLAUDE.md
  .claude/agents/implementer.md, .claude/agents/reviewer.md
  .github/copilot-instructions.md
  docs/skills/arcwright-sme/SKILL.md      ← your SME. No parallel router generated.
  docs/agents/*                            ← your 9 role contracts
  config/routing_table.json                ← your model routing

Collisions (differ from templates — will NOT be overwritten):
  README.md   docs/README.md
  .github/pull_request_template.md
  .github/workflows/ci.yml   (+ others)

New files team-ai would add:
  schemas/frontmatter.schema.json, schemas/agent.schema.json, …
  .team-ai.yaml
  catalog/namespaces/arcwright.yaml         (TODO stub — you map docs/ folders)
  kb/_backlog/coverage-gaps.md
  evals/golden/                              (question stubs)
  docs/preflight.md, docs/strategy.md, docs/architecture.md (team-ai's), docs/agent-plan.md
  docs/decisions/adr-0001-scaffold-choices.md

How do you want to proceed?
  [adopt-existing]  keep everything above, add only the new files          ← recommended here
  [siblings]        also write README.md.team-ai-new etc. for you to diff
  [subdir]          put the whole generated instance in ./team-ai/ to merge by hand
  [abort]           write nothing
```

`init` will not proceed past this screen without a choice (or `--on-conflict`). There is
**no overwrite option**, and nothing is ever deleted.

### If the operator picks `adopt-existing`

`team-ai` writes **only** the net-new deterministic layer:

- `schemas/*.schema.json`
- `.team-ai.yaml` + `team-profile.yaml` + `index.lock`
- `catalog/namespaces/arcwright.yaml` (TODO stub)
- `kb/_backlog/coverage-gaps.md`
- `evals/golden/*.yaml` (stubs — no real questions)
- `docs/preflight.md`, `docs/strategy.md`, `docs/agent-plan.md`,
  `docs/decisions/adr-0001-scaffold-choices.md`
- `docs/architecture.md` gains an appended **"coexistence boundary"** paragraph:
  *"team-ai operates in extend mode. Adopted: `AGENTS.md`, `.claude/`,
  `docs/skills/arcwright-sme/SKILL.md`, `docs/agents/*`, `config/routing_table.json`.
  team-ai adds only the deterministic KB-quality layer (schema validation, lexical index,
  gap log, freshness audit, eval gates). The `arcwright-sme` skill remains the router."*

It does **not** write: `AGENTS.md`, `CLAUDE.md`, workflows, `README.md`, a `sme` router,
role subagents, or personas.

---

## What `doctor` reports right after

```
DOCTOR
  ✓ Repo structure valid (extend mode)
  ✓ Adopted AGENTS.md, .claude/, arcwright-sme SKILL.md, docs/agents/*, routing_table.json
  ✗ Namespace mapping incomplete — catalog/namespaces/arcwright.yaml has 8 TODO blocks
  ✗ Front matter absent — 0 of 667 docs/*.md have id / owner / review_by / sensitivity
  ✗ Index not built (blocked on namespace mapping + front matter)
  ✗ 20 golden eval answers not filled in
  → 4 items remaining. See SETUP.md.
```

The remaining work is real and `team-ai` cannot do it: deciding how `docs/` folders map
to namespaces, and adding front matter to 667 files (or a subset). Until then the index,
citations, gap log, and freshness audit have nothing to act on.

---

## Honest bottom line for Arcwright

| `team-ai` capability | Arcwright already has it? |
|---|---|
| Owned markdown KB in git | **Yes** — `docs/`, with a versioning policy |
| An SME that routes questions to the KB | **Yes** — `docs/skills/arcwright-sme/SKILL.md` |
| Role agents / contracts | **Yes** — `.claude/agents/` + `docs/agents/` |
| Task-type × quality-tier model routing | **Yes** — `config/routing_table.json` |
| An eval harness | **Yes** — `evals/` (routing/continuity) |
| Front-matter schema + validator on docs | **No** |
| Ranked retrieval index + enforced citations | **No** |
| Coverage-gap log from unanswered questions | **No** |
| Freshness audit keyed to `review_by` | **No** |
| CI gates on retrieval / routing / refusal | **No** |

So against Arcwright, the planned `team-ai` would **adopt everything and stand down to a
thin deterministic quality layer** — exactly the outcome the README calls "a legitimate
and much cheaper success." It would not generate a competing SME, and it would not modify
a single existing file.

---

## The better entry point for Arcwright: `team-ai adopt`

For a repo this mature, `init` is the wrong command. `team-ai adopt` (design §18.1,
Tasks 41–44) is built for it — **fully deterministic, no model calls**:

```
$ team-ai adopt --root . --out .

Wrote docs/adoption-plan.md and adoption-plan.yaml. Nothing else changed.

NAMESPACE MAPPING
  matched   architecture/  → architecture      decisions/ → decisions
            conventions/   → operating          roadmap/  → playbooks (candidate)
  decide    prd/           → [operating | patterns | custom]
            story-bibles/  → [patterns | custom]
            product/       → [operating | decisions | custom]
            specs/         → [patterns | playbooks | custom]

FRONT-MATTER BACKFILL   (612 of 667 docs; blocks pre-filled, approved: false)
  docs/architecture/01-overview.md
    id: architecture.architecture.01-overview
    title: System Architecture Overview
    owner: <top git author for this file>
    review_by: 2027-02-26
    source: synced:notion        ← detected "edit in Notion and re-sync" header
  … 611 more

GAP VS QUALITY BAR
  q1  substrate choice + index      ~ partial — docs in git; no index yet → team-ai reindex
  q5  adversarially reviewed         ✓ docs/decisions + review-checklist.md
  q6  running cost measured          ✓ config/routing_table.json + evals/
  q8  setup tells you what's missing ✗ → add team-ai doctor
  q13 scripts where a script would do ✓ scripts/ + Makefile
  q15 model/platform agnostic        ✓ routing_table.json is the only provider surface
  q17 detect existing AI infra       ✗ → this adopt run is the detection
  … full 17-line table in adoption-plan.md

COLLISIONS (init would generate these; adopt will not touch them)
  README.md  docs/README.md  .github/pull_request_template.md  .github/workflows/*
```

Then `team-ai adopt --interactive` walks each item (approve / skip / edit) and each
namespace decision. `team-ai adopt --apply` writes **only** the approved front-matter
blocks and namespace entries — every other file untouched — and runs `validate-kb`
afterward.

For the one question the framework can't answer — *does this folder structure actually
serve the team?* — the plan says: ask your `arcwright-sme`.

This is what the plan now specifies (design §18 + §18.1; Tasks 23, 27, 32, 41–44; the
`adopt` run is exercised against the real Arcwright repo in Task 39, read-only, asserting
the repo tree is byte-for-byte unchanged).
