# team-ai Framework — Design of Record

**Date:** 2026-08-30
**Status:** Approved (brainstorming), pending implementation plan
**Repo:** `github.com/nickejanssen/team-ai`
**Companions:** [`docs/architecture.md`](../architecture.md), [`docs/interview-spec.md`](../interview-spec.md), [`docs/quality-bar.md`](../quality-bar.md)

---

## 1. What this is

`team-ai` is a **forkable framework**, not one team's knowledge base. Any team forks or
installs it, runs a guided interview, and gets a working AI capability tailored to how
they work: a knowledge base they own, agents scoped to their roles and domains,
deterministic scripts, and an eval harness.

The framework ships **structure and questions**. It never ships another team's content.

The build deliverable is a **guided interview + idempotent generator**. Everything the
framework itself runs is deterministic — **zero model calls anywhere in framework code**.

## 2. Toolchain

| Decision | Choice | Rationale |
|---|---|---|
| Language | TypeScript | Matches `npx team-ai`, the all-`.ts` file tree in architecture §18.1, MCP SDK ecosystem |
| Package manager | npm | One less tool for forkers to install |
| Node | 22 (Active LTS), pinned via `.nvmrc` + `engines` | Supported through 2025; `better-sqlite3` prebuilds available |
| License | Apache-2.0, public | Explicit patent grant + `NOTICE` |
| Interview runtimes | CLI **and** Claude skill | Both driven by one `questions.yaml` (architecture §14) |
| Lint / format / types | ESLint flat config + Prettier + `tsc --noEmit` strict | Enforced in CI |
| Tests | Vitest | Real tests alongside code |
| Git hooks | lefthook | Single binary, one YAML config, no `postinstall` surprises for forkers |
| Commits | Conventional Commits via commitlint (commit-msg hook) | |
| CI | GitHub Actions | Framework also ships reusable workflows other repos call |
| Secret scan | gitleaks in CI | |
| Versioning | SemVer from 0.1.0, Keep a Changelog | |

### Key libraries

- `gray-matter` + `yaml` — front matter / YAML
- `ajv` — JSON Schema validation against hand-written schemas in `schemas/`
- `better-sqlite3` — the one native dependency; backs the lexical retrieval driver (FTS5).
  Approved as an acceptable single heavy dep.
- `commander` + `@inquirer/prompts` — CLI and interview prompts
- `handlebars` — generated files and the three gate summaries

## 3. Where this design overrides the architecture docs

The build prompt scopes deliberately and wins where it disagrees with the companion docs.

| Topic | Docs say | This design does |
|---|---|---|
| Repo strategy | Start one repo, extract toolkit at phase 7 | Build the framework now, fully |
| MCP server | `server/` package inside the toolkit (§18.1) | `templates/mcp-server/` — generated **into the instance**, off by default, enabled by an interview answer. The instance owns and runs it; the framework carries no runtime |
| Retrieval drivers | Six drivers | `lexical` only (SQLite FTS5). The other five implement the interface but every method throws `NotImplementedError` referencing the phase-8 checkpoint — an honest interface, so adding one later touches no callers |
| Model use | Some "skills" use a small model (§11) | Framework code calls **no models**. `kb-answer`, `kb-contribute`, `audit-summary`, `sme-route` are `SKILL.md` **templates shipped to the instance**, not framework code |
| Connector probe | Runs five golden questions through a live connector | Framework **detects** connectors, **prepares** the five questions + instructions, and **records** the outcome the operator reports (`pre.probe_result`). It never calls a model itself. Documented as such in `docs/preflight.md` output |
| Question count | quality-bar prose says "sixteen questions" | The prompt lists 17. Implement all 17; note the discrepancy in `docs/quality-bar.md` |
| Org path | Examples hardcode `github.com/upside/...` | Framework's own references use `nickejanssen/team-ai`. Generated instances get their org from a new interview question `ctx.org_path` (the one added question — see §7) |

## 4. Team-agnosticism guarantees

This is a framework. No team's name, content, or specifics may live in framework logic.

- `src/`, `schemas/`, `templates/` contain **zero** team names and zero hardcoded
  domain content. Everything flows from `questions.yaml` → catalog presets →
  `team-profile.yaml` produced at generation time.
- Catalog namespace presets are **structural shapes**, not organizations:
  `engineering`, `support`, `generic`, `generic-partner-facing`
  (the last renamed from architecture's `partner-solutions` to keep it structural).
- Custom roles, domains, and namespaces generate a **stub with a TODO block**, never a guess.
- **No example instance is committed.** Dogfood runs generate into a throwaway directory,
  are verified, then discarded. Only `docs/dogfood-notes.md` (prose findings) survives.
- CI runs a denylist grep over `src/` and `schemas/` for instance-flavored tokens
  (team names, partner names, product names from the companion docs) to catch regressions.

## 5. Architecture of the framework

### 5.1 Modules (`src/`)

| Module | Responsibility | Depends on |
|---|---|---|
| `schema/` | Load + validate against JSON Schema (Ajv) | `schemas/*.json` |
| `kb/` | Front matter parse/serialize, chunker, loader, citation resolution, relations parsing | `schema/` |
| `retrieval/` | `RetrievalAdapter` interface; `lexical` driver (FTS5); five honest stubs; driver factory reading `index.lock` | `kb/` |
| `commands/` | The deterministic scripts (see 5.3) | `kb/`, `retrieval/`, `schema/` |
| `interview/` | `questions.yaml`, pure branching engine, preflight scan + probe, three gates, output writers | `schema/`, `catalog/` |
| `generator/` | Idempotent template rendering; `init/spoke/attach/resume/review/upgrade` | `interview/`, `catalog/` |
| `emit/` | Neutral agent/skill definitions → `claude-code` / `mcp-only` / `generic` | `catalog/` |
| `catalog/` | Preset resolution: toolkit defaults → org catalog repo (if configured) → instance `catalog/` | — |

### 5.2 Retrieval adapter

Interface exactly as architecture §9: `search`, `get`, optional `neighbors`, `reindex`;
`Hit` carries `doc_id`, `chunk_id`, `path`, `heading_path`, `score` (normalized 0–1),
`text`, `metadata`.

- **`lexical`** — SQLite FTS5 over chunked markdown; BM25 → normalized 0–1 so the score
  contract holds for future drivers. The only implemented driver.
- **`vector-embedded`, `vector-pgvector`, `vector-hosted`, `graph`, `hybrid`** — classes
  that implement the interface; every method throws `NotImplementedError` with a message
  pointing at the phase-8 index checkpoint.
- `index.lock` pins `driver`, `chunk` config (`split_on`, `target_tokens`, `hard_cap`),
  and `embedding` (`provider`, `model`, `version`) or `null`. Changing any forces a full reindex.

### 5.3 Deterministic commands (no model calls)

`validate-kb`, `validate-citations`, `reindex`, `search`, `freshness-audit`,
`assemble-manifest`, `run-evals`, `validate-spoke`, `emit`, `doctor`.

- `freshness-audit` emits JSON by default; opening issues is behind an explicit flag
  (no ops burden by default).
- `run-evals` computes hit rate @k, routing accuracy (from manifest keyword/namespace
  matching — the zero-model path), refusal rate (no hit above threshold), citation
  validity, and cost fields. Emits a JSON report + CI exit code.
- `doctor` re-runs preflight and prints the setup-completeness checklist.

### 5.4 Chunking

Split on H2/H3, target 800 tokens, hard cap 1200. Each chunk inherits the document's
full front matter and stores its heading path (`path#heading` citation target). Token
count is an **approximate deterministic heuristic** (~1.3 tokens/word), documented as
approximate. Config pinned in `index.lock`.

## 6. The interview

`src/interview/questions.yaml` is the **single source of truth**, driving both the CLI
and the Claude skill.

- **Acts 0–5** and the **three gates** from `interview-spec.md`:
  Act 0 Preflight (+ possible STAND DOWN early exit) · Act 1 Mode & team context ·
  Act 2 Knowledge model · **Gate 1 strategy** · Act 3 Architecture & cost ·
  **Gate 2 architecture** · Act 4 Agents & skills · **Gate 3 agent plan** ·
  Act 5 dry run / write / doctor.
- **Preflight scan** (`.mcp.json`, `.claude/`, `CLAUDE.md`, `AGENTS.md`, env vars for
  vector stores, connector config) → `extend` / `coexist` / `stand down`.
- **Connector probe** — detect + prepare + record (see §3); never calls a model.
- **Branching engine** (`engine.ts`) — a pure state machine over `questions.yaml`:
  `ask_if` evaluation, `implies` pre-fill, and working `back`, `skip` (defer), `why`, `save`.
- **`defer` and `recommend one`** are first-class answers on every question that allows them.
  `recommend one` always prints `recommend_why`.
- **Three gates** render readable summaries. **Nothing is written to disk until gate 3 passes.**
- **Outputs** (interview-spec §13): `team-profile.yaml`, `docs/preflight.md`,
  `docs/strategy.md`, `docs/architecture.md`, `docs/agent-plan.md`,
  `docs/decisions/adr-0001-scaffold-choices.md`, `index.lock`.
- Every question's `why` text traces to a numbered item in `docs/quality-bar.md`.

## 7. New question (flagged)

One question is added beyond the interview spec's bank:

```yaml
- id: ctx.org_path
  act: 1
  type: text
  prompt: "What GitHub org or user will own the generated repos? (e.g. your-org)"
  why: >
    Manifest entries, spoke configs, and reusable-workflow references need a real
    namespace. The framework ships a placeholder; your instance needs yours.
  default: your-org
  allow_defer: true
  ask_if: "mode != attach"
```

All other questions derive from `interview-spec.md`. No other new questions without
raising them first.

## 8. Catalogs

| Catalog | Ships | Override |
|---|---|---|
| `catalog/namespaces/*.yaml` | `engineering`, `support`, `generic`, `generic-partner-facing` | Add a file, or edit after generation |
| `catalog/roles/*.yaml` | `architect`, `sales-engineer`, `build-engineer`, `support-engineer`, `pm` | Custom roles → TODO stub, never a guess |
| `catalog/skills/*.yaml` | Core KB skills + per-preset extras | Filtered by chosen preset |
| `catalog/personas/*.md` | `internal-technical`, `partner-facing`, `executive-brief` | Freely added |

Resolution order: toolkit defaults → org catalog repo (if configured) → instance `catalog/`.

## 9. Templates

- `templates/instance/` — full instance repo as a Handlebars tree (README, SETUP.md,
  `manifest.yaml`, `index.lock`, `docs/`, seed `kb/`, `agents/`, `personas/`, `skills/`,
  `evals/golden/example.golden.yaml`, `.mcp.json`, `.gitignore`,
  `.github/workflows/{validate,evals,reindex,freshness}.yml`).
- `templates/spoke/` — `spoke.yaml`, `kb/`, `agents/`, `skills/`, `.github/workflows/validate.yml`.
- `templates/attach/` — `.team-ai.yaml` only.
- `templates/mcp-server/` — local stdio server wrapping `src/commands`, off by default.

Agent / skill / persona templates are **neutral YAML + markdown** (architecture §7), with
`model_tier` (`none|small|large`) and `max_hops` enforced by schema. Router, domain
subagent, and role subagent templates. Emitters write **gitignored** build artifacts to `emitted/`.

## 10. Eval harness

`evals/golden.schema.json` + the `run-evals` runner. Ships **one** worked example
(`evals/golden/example.golden.yaml`), clearly marked EXAMPLE. **No golden questions for
any team.** CI gates per architecture §16: retrieval hit rate @8, citation validity 100%,
routing accuracy, refusal on out-of-KB questions, front matter validation, cost-per-answer
no-regression.

## 11. Optional local MCP server

`templates/mcp-server/` generates a local **stdio** server that wraps the same
`src/commands`. Off by default; enabled by an interview answer. No remote hosting, no
auth, no deployment, no Docker.

## 12. `docs/quality-bar.md`

The 17 questions from the build prompt, each with: the answer the architecture gives, and
where in the repo that answer is enforced (file path). Used as the `why` source for
interview questions and as a checklist contributors run before merging. Notes the
"sixteen" vs 17 discrepancy.

## 13. File tree

See the approved tree in the brainstorming transcript; summarized:

```
team-ai/
├── root config (package.json, tsconfig, eslint, prettier, lefthook, commitlint, vitest)
├── LICENSE NOTICE SECURITY.md CHANGELOG.md CONTRIBUTING.md CODEOWNERS .nvmrc .editorconfig .gitignore
├── docs/            architecture.md interview-spec.md quality-bar.md dogfood-notes.md design/
├── bin/cli.ts
├── src/             schema/ kb/ retrieval/ commands/ interview/ generator/ emit/ catalog/
├── schemas/         frontmatter agent manifest spoke team-profile (.schema.json)
├── catalog/         namespaces/ roles/ skills/ personas/
├── templates/       instance/ spoke/ attach/ mcp-server/
├── skills/          scaffold-interview/SKILL.md
├── evals/           golden.schema.json  golden/example.golden.yaml
└── .github/         workflows/ (ci + 3 reusable)  PULL_REQUEST_TEMPLATE.md  ISSUE_TEMPLATE/
```

No `examples/` directory. No committed instance.

## 14. Build order

1. Repo skeleton + all root config + empty CI. First commit.
2. Schemas + Ajv validator, with valid/invalid fixtures.
3. KB primitives (`src/kb/`) — frontmatter, chunker, loader, citations, relations.
4. Retrieval adapter — `types.ts`, `lexical.ts`, five stubs, `factory.ts`, `index.lock`.
5. Deterministic commands + eval runner + `evals/` schema and example.
6. Catalogs + `resolve.ts` (3-level order); custom → TODO stubs.
7. Interview — `questions.yaml`, `questions.schema.json`, `engine.ts` (heavily tested),
   preflight scan + probe, `cli-runtime.ts`, three gate templates, `outputs.ts`.
8. Generator + templates — `render.ts` (idempotent, `--dry-run`), commands,
   `templates/{instance,spoke,attach,mcp-server}`, agent/skill/persona templates.
9. Emitters — claude-code, mcp-only, generic → `emitted/`.
10. `skills/scaffold-interview/SKILL.md` — thin runtime over `engine.ts`.
11. CI — `ci.yml` + three reusable workflows; write `docs/quality-bar.md` with real
    "where enforced" references; add the agnosticism denylist grep.
12. Dogfood — run `init` against **Arcwright** (real preflight scan → expect `extend`),
    then against a **Partner Solutions** profile. Generate into a temp dir, run the
    generated CI locally, discard both. Write `docs/dogfood-notes.md`; fix findings.
13. Final pass — CHANGELOG 0.1.0, tag, verify Definition of Done line by line.

## 15. Definition of done

Someone can fork the repo, run one install command and `init`, answer the interview, and
end up with a validated instance whose CI is green and whose search returns cited results
from seed content. `doctor` accurately reports what is still missing. `docs/quality-bar.md`
has an honest answer for every line.

## 16. Out of scope

Remote/hosted MCP server, auth, token issuance, deployment. Vector and graph driver
implementations. Any team's actual knowledge content or golden questions.

## 18. Non-destructive generation and reconciliation

The generator runs against repos that may already contain hand-authored AI
infrastructure. It must never cause loss of that work.

**Hard guarantees:**

- The generator **never deletes a file.**
- The generator **never overwrites a file it did not itself create in a prior
  run.** Its own output is tracked in `team-profile.yaml` under `generated_paths:`
  as `{ path, sha256 }` entries. A target is writable only if it is absent,
  byte-identical to the new render, or a recorded prior render whose on-disk hash
  still matches (i.e. not hand-edited since).
- Any other existing target is a **collision**: not written, reported.

**Preflight reports what to preserve.** `scanPreflight` returns `existingAssets`:
an existing agent-config file (`AGENTS.md` / `CLAUDE.md` / `.claude/`), an
existing router or SME agent (`agents/*.yaml`, `.claude/agents/*`), existing
`kb/**`, existing skills. On an `extend` assessment the architecture's rule
(§4) applies: adopt the existing agent config, do not create a parallel one.

**`init` stops and asks on conflict.** After preflight and the interview, and
before writing anything, `init` computes a dry render plan. If there are
collisions, or an existing SME / agent-config is present under `extend`, it
presents these options and writes nothing until the operator chooses:

| Option | Effect |
|---|---|
| `adopt-existing` | Keep every existing file. Generate only absent paths. Record the boundary in `docs/architecture.md`. |
| `siblings` | Write generated versions as `<path>.team-ai-new` beside the originals for manual diff/merge. Nothing overwritten. |
| `subdir` | Generate the whole instance into `./team-ai/` for the operator to merge. |
| `abort` | Write nothing. |

There is no "overwrite" option and deletion is never offered. `--on-conflict
<adopt-existing|siblings|subdir|abort>` pre-answers this for non-interactive runs.

`upgrade` already refuses to touch `kb/`, `agents/`, `personas/`, `skills/`,
`catalog/` and only re-renders plumbing — unchanged.

### 18.1 Adopting an existing repo: `team-ai adopt`

When a repo already has a documentation tree (like Arcwright's `docs/`), `init`'s
"generate an instance" model is the wrong tool. `team-ai adopt` instead measures the
existing repo against the framework's own standard and produces a concrete,
reviewable remediation plan. **It is fully deterministic — no model calls.** The
framework defines the standard, so the gap is mechanical to compute.

**`team-ai adopt [--root .] [--out .] [--horizon-days 180] [--namespace-map <file>]`**
produces two files and changes nothing else:

- `docs/adoption-plan.md` — human-readable.
- `adoption-plan.yaml` — machine-applyable, schema-validated, every item
  `approved: false` by default.

The plan contains:

| Section | How it's derived (all deterministic) |
|---|---|
| **Namespace mapping** | Each top-level docs folder matched to a namespace by exact / singular-plural / synonym-table match. Unmatched folders get 2–3 ranked candidates + `custom` — a **human decision**, never a guess. |
| **Front-matter backfill** | For every doc with no `team-ai` front matter, the exact block to insert: `id` from path slug, `title` from the first `# H1` (or title-cased filename), `owner` from the most frequent `git log` author, `review_by` = today + `--horizon-days`, `sensitivity: internal`, `status: active`, `source: synced:<system>` when the body header matches an "edit at source" pattern else `authored`, `tags`/`supersedes` empty. |
| **Relabels** | Docs whose current header indicates a synced source but that lack `source:`. |
| **Gap vs quality bar** | Each of the 17 `docs/quality-bar.md` lines mapped to a detectable condition: satisfied / not, and the exact command or file that closes each gap. |
| **Collisions** | Files `init` would generate that already exist (dry render vs `templates/instance`). |
| **Qualitative review pointer** | "For whether this structure serves the team, ask your existing SME" — the one judgment call the framework does not make. |

**`team-ai adopt --interactive`** walks each plan item (approve / skip / edit) and each
unmatched namespace folder, writing the choices back into `adoption-plan.yaml`.

**`team-ai adopt --apply`** applies only `approved: true` items — each a deterministic
transform (insert a front-matter block, add a namespace to `catalog/`, optionally
`fs.rename` a file with a recorded `moved:` log). It never touches an unapproved file
or one whose existing header conflicts; it is idempotent (applied items are skipped on
re-run); it runs `validate-kb` afterward and reports.

The non-destructive guarantees of §18 hold throughout: no deletes, no overwrite of a
file the framework did not create, nothing written without explicit approval.

## 19. Open items carried into planning

- Whether the agnosticism denylist grep lives in `ci.yml` or as a `src/commands` check
  invoked by CI (leaning: a small script so forkers can run it locally too).
- Exact seed-doc set per namespace preset (5 docs each per interview-spec `agents.seed`).
