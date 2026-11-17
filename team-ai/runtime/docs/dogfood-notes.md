# Dogfood notes

> Task 39. The framework run against itself three ways: `team-ai init` with the
> real Arcwright repo as the preflight target (Run A), `team-ai adopt` against
> the real Arcwright repo (Run A-adopt, read-only), and `team-ai init` for a
> Partner Solutions profile (Run B). Generated output went to `.tmp-dogfood/`
> and was deleted; nothing team-specific is committed. This file is prose only.
>
> Reproduce: `npm run build && bash test/dogfood.sh` (convenience) or
> `npx vitest run src/generator/dogfood.test.ts` (CI-durable; Run A and
> Run A-adopt skip when the Arcwright repo is not on disk).
>
> Answer sets: `test/fixtures/answers/dogfood-arcwright.yaml` and
> `test/fixtures/answers/dogfood-partner-solutions.yaml`. Each is an ordered
> list, one entry per interview question reached plus `confirm` at each gate,
> built by walking `new Engine(loadBank())` and recording the token per step.

---

## Run A — `team-ai init`, Arcwright as the preflight target

Command: `init.run({ dir: ".tmp-dogfood/arcwright", answers: loadAnswerFile(...arcwright.yaml), preflightTarget: "…/arcwright", onConflict: "adopt-existing" })`

### Preflight report (captured verbatim)

```
PREFLIGHT

Found
  ✗ No MCP config detected
  ✓ Agent config present: CLAUDE.md, AGENTS.md, .github/copilot-instructions.md, .claude, .codex, .agents
  ✗ No existing vector store detected
  ✗ No org enterprise-search marker detected
  ✓ Skill / plugin directories: .claude/commands

Assessment: EXTEND
  A compatible agent harness already exists (CLAUDE.md, AGENTS.md,
  .github/copilot-instructions.md, .claude, .codex, .agents); team-ai will
  register alongside it rather than creating a parallel config.

  Adopt AGENTS.md — register alongside it, do not create a parallel config.

Existing assets
  agent config file: AGENTS.md
  router / SME agent: none
  agent definitions: 2
  KB documents: 0
  skills: none
```

`report.assessment === "extend"` and `report.existingAssets.agentConfigFile === "AGENTS.md"`, as required.

### What worked

- Preflight assessment `extend`, rationale names `AGENTS.md` / `CLAUDE.md` /
  `.claude` / `.codex` / `.agents` / `.github/copilot-instructions.md`.
- All six instance checks pass on the generated tree:
  `validate-kb --schema-only` (5 docs), `validate-citations` (0 unresolved),
  `reindex` (5 docs, 16 chunks), `search "charter"` (1 cited hit,
  `arcwright.operating.charter`), `assemble-manifest` (2 domains), `doctor`
  (3 remaining manual items, exit 0).
- `.github/workflows/validate.yml` is valid YAML and references
  `nickejanssen/team-ai/.github/workflows/validate-kb.reusable.yml@v0`.
- `onConflict: "adopt-existing"` appended a `## Coexistence boundary` paragraph
  to `docs/architecture.md` naming `AGENTS.md`.

### Awkward / ambiguous / wrong

1. **`ns: <domain>` in the agent plan was a lie.** — WRONG. Gate 3 and
   `docs/agent-plan.md` printed `engine-sme … ns: engine` / `nightcap-sme … ns:
   nightcap`, but every domain SME yaml is generated with
   `kb_namespaces: [operating]` (the preset's first namespace). The render now
   reports that actual namespace via a shared `domainNamespace()` helper.
   **FIXED in 878b2c1.** (The deeper question — *should* each domain subagent
   get its own isolated namespace? — is left for the framework owners; the
   generator's current behaviour is one shared namespace.)

2. **Coexistence note claimed a router that does not exist.** — WRONG. The
   appended paragraph hardcoded "The existing router remains authoritative" even
   though preflight reported `router / SME agent: none`. Now the router clause is
   only added when a router was actually detected, and it names it.
   **FIXED in 878b2c1.**

3. **Idempotent re-run reports two phantom collisions.** — AWKWARD. Running
   `init` a second time into the already-generated dir prints
   `2 collision(s) … kept your version, skipped: index.lock, manifest.yaml`.
   Those two files are written by `writeOutputs` / `assemble-manifest` *after*
   the render manifest is snapshotted, so the next render classifies them as
   hand-authored. Harmless (the run re-generates them at the end anyway) but the
   line reads like a warning. **Won't fix in this pass** — the clean fix is to
   record `index.lock` + `manifest.yaml` in the generated manifest (or exclude
   them from the collision scan), which is an `init`/`render` change beyond a
   dogfood polish. No data is lost.

4. **Arcwright's real SME is invisible to preflight.** — AWKWARD. Arcwright's
   subject-matter expert is a Claude *skill* (`.agents/skills/…`,
   `.claude/skills` convention), not an `agents/*.yaml` with `kind: router`, so
   `router / SME agent: none`. Preflight's skill scan also only checks `skills/`
   and `.claude/skills/`, not `.agents/skills/` (it does pick `.agents` up as an
   agent-config dir). **Won't fix now** — recommend teaching preflight the
   `.agents/skills/` location and, optionally, flagging an SME-style skill.

5. **`pre.overlap` / `pre.probe_result` prompts assume a positive detection.**
   — AWKWARD. Both Act 0 questions are asked unconditionally
   (`ask_if: always`), with prompts that read "Existing search already covers
   some of these sources" and "The connector probe answered most sample
   questions" — neither true for Arcwright. The yaml comments say the runtime
   should only show them on a real detection, but no such gate exists. **Won't
   fix now** — needs `ask_if` wired to preflight-derived facts, which the engine
   does not model yet. The answer file passes the harmless `decide-later` /
   `continue`.

6. **The AC text said Arcwright has `.mcp.json`; it does not.** — NOT A BUG.
   Preflight correctly reports "No MCP config detected". Noting it so the next
   reader does not treat the missing `.mcp.json` line as a regression.

### Run A reconciliation

- `adopt-existing`: a hand-authored `AGENTS.md` (copied from the real repo) and
  `agents/sme.yaml` (`# HAND AUTHORED SENTINEL`) are **byte-identical (sha256)
  before and after**. No `agents/sme.yaml.team-ai-new` written.
  `docs/architecture.md` gains the `Coexistence boundary` paragraph naming
  `AGENTS.md`.
- `siblings`: `agents/sme.yaml.team-ai-new` is written, the sentinel
  `agents/sme.yaml` is untouched.
- Note: a root `AGENTS.md` is never itself a collision — the instance template
  generates `agents/*.yaml`, not a root `AGENTS.md` — so "adopting" it is really
  "leave it alone + write the coexistence note". Works as intended; there is no
  merge step.

---

## Run A-adopt — `team-ai adopt` against the real Arcwright repo (read-only)

Command: `adopt.run({ root: "…/arcwright", out: ".tmp-dogfood/arcwright-adopt", horizonDays: 180 })`

### What worked

- Writes exactly `adoption-plan.yaml` + `docs/adoption-plan.md` and nothing
  else. **team-ai wrote no artifact into the Arcwright tree** — `adopt` only ever
  writes under `--out` (`.tmp-dogfood/arcwright-adopt`). (An unrelated parallel
  process on the machine edited `playtests/…` in Arcwright during the session;
  none of it produced by a `team-ai` command. The guard is "no `adoption-plan`
  / `.team-ai` / `team-profile.yaml` / `index.lock` entry appears in Arcwright's
  git status", not "the repo is frozen".)
- `adoption-plan.yaml` is schema-valid (`validate("adoption-plan", …).ok`).
- Quality-bar gap table: **17 rows, 7 satisfied** (q1, q2, q5, q6, q13, q15,
  q17).
- Namespace decisions (after the archive-skip fix): **12 folders** with no
  preset match need a human pick — `agents`, `architecture`, `conventions`,
  `design`, `gdd`, `prd`, `product`, `roadmap`, `skills`, `specs`,
  `story-bibles`, `superpowers`. Only `decisions/` preset-matched. (Was 13
  before the fix — `archive/` is no longer measured.)
- Front-matter backfill: **470 items** (was 705; **235 archived/generated docs
  skipped**). `docs/architecture/*` (19 files) correctly labelled
  `source: synced:notion`. Undecided-folder rows carry `namespace: __pending__`
  and render as **(pending decision)**.
- 3 template collisions: `.github/workflows/evals.yml`, `.gitignore`,
  `README.md`.

### Rendered `adoption-plan.md` (trimmed excerpt)

```
# Adoption plan

- **Repo measured:** `C:/Users/nicke/OneDrive/Desktop/arcwright`
- **Preflight assessment:** extend
- **Front-matter backfill items:** 470
- **Namespace decisions needing a human pick:** 12
- **Quality-bar gap:** 7/17 satisfied
- **Template collisions:** 3
- **Archived / generated docs skipped:** 235 (`--include-archived` to measure them too)

## Namespace map
### Matched
- `decisions/` → `decisions`
### Needs a decision
- `prd/` — candidates: `patterns` `platform` `operating` `custom`
- `story-bibles/` — candidates: `playbooks` `decisions` `operating` `custom`
- `conventions/` — candidates: `decisions` `operating` `patterns` `custom`
  … (9 more)

## Front-matter backfill
- `docs/agents/planner.md` → id `pending.agents.planner`, namespace **(pending decision)**, source `authored`
- `docs/architecture/01-overview.md` → id `pending.architecture.01-overview`, namespace **(pending decision)**, source `synced:notion`
  … (468 more)

## Quality-bar gap
- **q1** — satisfied: markdown docs in docs/ · closes with: add front matter + `team-ai reindex`
- **q3** — gap: no .team-ai.yaml · closes with: `team-ai attach`
- **q8** — gap: no SETUP.md or doctor script · closes with: `team-ai doctor`
  … (14 more)

## Template collisions
- `.gitignore` already exists and differs from what `team-ai init` would generate
- `.github/workflows/evals.yml` already exists and differs …
- `README.md` already exists and differs …
```

### Awkward / ambiguous / wrong

1. **`team-ai adopt` did not finish in two minutes.** — WRONG. `buildAdoptionPlan`
   ran `git log --format=%an -- <file>` once per markdown file. Arcwright's
   `docs/` has ~670 markdown files, so that is ~670 `git` subprocesses; on this
   machine the command ran for minutes with no output. Replaced with a single
   `git log --name-only` traversal parsed into a path→authors map. Same owner
   inference; **~5 seconds** now. **FIXED in 71da247.**

2. **`docs/architecture/*` labelled `synced:external`, not `synced:notion`.** —
   WRONG. Those files lead with `> Source: …` then, on line 3,
   `Do not edit this file directly; edit in Notion and re-sync.`
   `detectSyncedSource` returned on the first matching line (`> Source:` →
   `synced:external`) before ever reaching the line that names Notion. Now it
   scans the whole header window for a named system first, then falls back to
   the generic markers. **FIXED in 97c1141.** 19 files now resolve to
   `synced:notion`.

3. **Every backfill row said `namespace: unmapped`.** — AWKWARD. Because all of
   Arcwright's folders are undecided at plan-build time (only `decisions/`
   matched), the doc showed `namespace unmapped` for all 705 rows — it read as
   if the tool had no idea where anything goes, when it actually meant "pending
   your pick in `team-ai adopt --interactive`". Undecided-folder backfill items
   now carry the explicit `__pending__` namespace, the plan doc renders it as
   **(pending decision)**, and `team-ai adopt --apply` refuses such an item —
   `skipped <path> — namespace decision not made` — so nothing is ever written
   with a placeholder namespace. `--interactive` records the folder's `chosen`
   value; `--apply` then resolves it (re-inferring the doc id) and writes.
   **FIXED** in `fix(adopt): skip archived exports; clearer pending-decision labels`.

4. **`docs/archive/**` was measured in full.** — AWKWARD. 235 of the 705 backfill
   items were under `docs/archive/` — a raw Notion export dump and archived
   Nightcap story bibles — and `archive/` showed up as its own namespace
   decision. Arcwright's `AGENTS.md` explicitly says "Do not read or compare
   archived exports by default. That wastes AI credits." `buildAdoptionPlan` now
   skips any doc whose path has a segment `archive` / `archived` / `_archive` /
   `notion-export` (plus `.git` / `node_modules` / `dist`), reports the count
   (`skipped 235 archived/generated docs (--include-archived to include)`), and
   takes a `--include-archived` flag to turn the skip off. Arcwright's plan drops
   from **705 → 470 backfill items** and **13 → 12 namespace decisions**.
   **FIXED** in `fix(adopt): skip archived exports; clearer pending-decision labels`.

---

## Run B — `team-ai init`, Partner Solutions profile

Command: `init.run({ dir: ".tmp-dogfood/partner-solutions", answers: loadAnswerFile(...partner-solutions.yaml) })`
(no preflight target → scans the empty dir → `coexist`)

Profile: `generic-partner-facing` preset, team size **1–3**, surfaces
`coding-agent` + `chat-apps` + `read-only-stakeholders`, consumers
`customer-partner-facing` + `outside-company`, `arch.hosting` left at
`no-server`.

### What worked

- All six instance checks pass (same as Run A).
- **Team size 1–3 suppresses role subagents.** `agents/roles/` contains no
  `*.yaml` / `*.md` files. Only domain agents (`widgets-api-sme`,
  `payments-api-sme`) plus the router `sme` are generated. Gate 3 render and
  `docs/agent-plan.md` both say "Role subagents … None. Team of 3 or fewer, so
  domain agents alone are the honest choice."
- `docs/architecture.md` carries **both** server gate-condition lines:
  - "**Local stdio server:** when a 2nd coding client appears."
  - "**Remote server:** after 2 asks from people who cannot clone the repo."
- External consumers held `kb.sensitivity` at `three-tiers`.

### Awkward / ambiguous / wrong

1. **Custom domains render as `ns: <preset first namespace>`.** — Same finding
   as Run A #1; **FIXED in 878b2c1**. The domain *label* ("widgets api") is now
   distinct from the namespace it is scoped to (`operating`).

2. **Custom-domain manifest entries are TODO stubs.** — NOT A BUG. `widgets-api`
   / `payments-api` get `description: "TODO: what questions does the widgets api
   domain own?"` and `keywords: []`. That is the documented behaviour for
   free-text domains (quality-bar q11 — never guess). Noting that the operator
   must fill these in before the domain agents are useful.

3. Same `pre.overlap` / `pre.probe_result` prompt-mismatch as Run A #5.

---

## Cross-cutting

- **`check-agnostic` stays green.** The answer fixtures under
  `test/fixtures/answers/` contain `arcwright` / `nightcap` tokens, but
  `test/` is not in the scanned set, and `src/generator/dogfood.test.ts` is a
  `*.test.ts` (excluded). `test/` is also outside `package.json` `files`, so
  nothing team-specific ships.
- **team-ai wrote nothing into Arcwright.** `preflight` and `adopt` only read
  `--root`; every artifact goes under `--out` / `--dir`. During the session an
  unrelated parallel process on the machine edited Arcwright (`playtests/…`,
  untracked `.tmp-chrome-playtest*/` / `.tmp-edge-playtest/`), so the guard is
  "no `adoption-plan` / `.team-ai` / `team-profile.yaml` / `index.lock` entry
  appears in Arcwright's git status", not "the repo is frozen".
- Both `.tmp-dogfood/` trees were deleted after verification.

### Fix commits

| Commit    | Fix |
|-----------|-----|
| `71da247` | `team-ai adopt` owner inference: one `git log` pass, not one per file (perf) |
| `97c1141` | `detectSyncedSource` prefers a named system over a generic `> Source:` line |
| `878b2c1` | agent-plan namespace + coexistence-note wording made honest |
| `fix(adopt): skip archived exports…` | `adopt` skips archived/generated docs (`--include-archived` to opt in); undecided-folder backfill carries `__pending__` and `--apply` refuses it |
