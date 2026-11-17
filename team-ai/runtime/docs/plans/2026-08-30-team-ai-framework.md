# team-ai Framework Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers-extended-cc:subagent-driven-development (recommended) or superpowers-extended-cc:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `team-ai`, a forkable TypeScript framework whose guided interview + idempotent generator produces a working, CI-green, team-owned AI capability (knowledge base, agents, deterministic scripts, eval harness) without shipping any team's content.

**Architecture:** A single npm package exposing a `team-ai` CLI (`init | adopt | spoke | attach | doctor | resume | review | upgrade | emit`) and a thin Claude skill, both driven by one `src/interview/questions.yaml`. Deterministic core modules (`schema`, `kb`, `retrieval`, `commands`, `catalog`, `adopt`) do all real work with **zero model calls**. The interview writes `team-profile.yaml` and gate docs; the generator renders `templates/{instance,spoke,attach,mcp-server}` via Handlebars. `adopt` measures an existing repo against the framework standard and emits a deterministic, reviewable remediation plan applied only on explicit per-item approval. Retrieval hides behind one interface with only the `lexical` (SQLite FTS5) driver implemented; the other five are honest `NotImplementedError` stubs.

**Tech Stack:** TypeScript, Node 22, npm, Vitest, ESLint (flat) + Prettier, lefthook + commitlint, `ajv`, `gray-matter` + `yaml`, `better-sqlite3`, `commander` + `@inquirer/prompts`, `handlebars`, GitHub Actions, gitleaks.

**User decisions (already made):**
- "TypeScript + npm" for the framework; Node "22 (Active LTS)".
- License "Public + Apache-2.0".
- Interview ships as "Both CLI and Claude skill", one `questions.yaml`.
- Repo lives at `C:\Users\nicke\OneDrive\Desktop\team-ai`, published as `github.com/nickejanssen/team-ai`.
- MCP server delivered as a "Generated template that wraps the shared scripts" (`templates/mcp-server/`), not a shipped package.
- Git hooks via "lefthook".
- "drop committed examples" — no example instance in the repo; dogfood into a temp dir and discard.
- Namespace preset `partner-solutions` renamed to `generic-partner-facing`.
- Dogfood order: "dogfood with Arcwright, then with the Partner Solutions team".
- One new interview question allowed and flagged: `ctx.org_path` (design §7). No other new questions without raising them.
- Where the prompt and the companion docs disagree, the prompt wins (design §3).
- "Full advisory flow" for adopting an existing repo, folded into v1 — kept **deterministic** (no model): `team-ai adopt` produces a reviewable remediation plan; `--interactive` collects per-item approvals; `--apply` applies only approved items (design §18.1, Tasks 41–44). The one qualitative judgment (does the structure serve the team) is delegated to the repo's existing SME.

---

## Deferred decisions

Two items are carried from the design doc (§17). Neither blocks earlier tasks.

1. **Agnosticism denylist check — location.** Resolved in this plan: it lives as `src/commands/check-agnostic.ts` (a real command, `team-ai check-agnostic`) so forkers can run it locally, and CI calls it. Rationale: matches "scripts wherever a script would do" (quality bar #13). No user question needed.
2. **Exact seed-doc set per namespace preset.** Resolved in this plan: each of the 4 presets ships exactly 5 seed docs (interview-spec `agents.seed` = "5 starter docs from the preset"), listed per preset in Task 20. No user question needed.

No open questions remain for the user during execution.

---

## File structure

Files are grouped by responsibility. Each `src/**` file has one job and its own `*.test.ts` sibling.

| Path | Responsibility |
|---|---|
| `package.json`, `tsconfig.json`, `eslint.config.js`, `.prettierrc.json`, `vitest.config.ts`, `.nvmrc`, `.gitattributes`, `.editorconfig` | Toolchain + strict TS + LF normalization |
| `lefthook.yml`, `commitlint.config.js` | pre-commit lint/format, commit-msg conventional |
| `LICENSE`, `NOTICE`, `SECURITY.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `CODEOWNERS`, `.github/PULL_REQUEST_TEMPLATE.md`, `.github/ISSUE_TEMPLATE/*` | Community health |
| `.github/workflows/ci.yml` | Framework CI: lint, typecheck, test, validate, secret-scan |
| `.github/workflows/{validate-kb,validate-spoke,evals}.reusable.yml` | Reusable workflows other repos call |
| `schemas/*.schema.json` | JSON Schema: frontmatter, agent, manifest, spoke, team-profile |
| `src/schema/load.ts`, `src/schema/validate.ts` | Ajv wrapper; compile + validate + friendly errors |
| `src/kb/frontmatter.ts` | Parse/serialize YAML front matter (gray-matter) |
| `src/kb/loader.ts` | Walk `kb/`, load `KbDoc[]`, attach source path |
| `src/kb/chunk.ts` | Split doc on H2/H3, token heuristic, heading path, inherit front matter |
| `src/kb/citations.ts` | Resolve `path#heading` against loaded docs |
| `src/kb/relations.ts` | Parse `relations` block, check targets exist |
| `src/retrieval/types.ts` | `RetrievalAdapter`, `Hit`, `Document`, `IndexStats`, `SearchOpts` |
| `src/retrieval/lexical.ts` | SQLite FTS5 driver: reindex, search (BM25→0..1), get |
| `src/retrieval/stubs.ts` | `vector-embedded`/`vector-pgvector`/`vector-hosted`/`graph`/`hybrid` → throw `NotImplementedError` |
| `src/retrieval/factory.ts` | Read `index.lock`, return the configured driver |
| `src/retrieval/index-lock.ts` | Read/write/compare `index.lock` |
| `src/commands/*.ts` | One file per command (see Milestone D) |
| `src/cli.ts` + `bin/team-ai.js` | commander wiring; `bin` shim |
| `src/catalog/types.ts`, `src/catalog/resolve.ts` | Catalog model + 3-level resolution |
| `catalog/namespaces/*.yaml`, `catalog/roles/*.yaml`, `catalog/skills/*.yaml`, `catalog/personas/*.md` | Presets |
| `src/interview/questions.yaml`, `schemas/questions.schema.json` | Question bank + its schema |
| `src/interview/engine.ts` | Pure state machine over the bank |
| `src/interview/preflight.ts` | Scan for existing AI infra; connector detect/prepare/record |
| `src/interview/gates.ts` + `src/interview/gates/*.hbs` | Render the three gate summaries |
| `src/interview/outputs.ts` | Write `team-profile.yaml`, gate docs, `index.lock`, ADR |
| `src/interview/cli-runtime.ts` | Terminal renderer using `@inquirer/prompts` |
| `src/generator/render.ts` | Idempotent Handlebars tree render; `--dry-run` |
| `src/generator/{init,spoke,attach,resume,review,upgrade}.ts` | Generator commands |
| `src/emit/{claude-code,mcp-only,generic}.ts`, `src/emit/index.ts` | Emitters → `emitted/` |
| `src/adopt/{infer,backfill,git-owner,namespaces,plan,gap,interactive,apply}.ts` | Deterministic existing-repo adoption (design §18.1) |
| `src/commands/adopt.ts`, `schemas/adoption-plan.schema.json` | `team-ai adopt` command + plan schema |
| `templates/instance/**`, `templates/spoke/**`, `templates/attach/**`, `templates/mcp-server/**` | Handlebars template trees |
| `skills/scaffold-interview/SKILL.md` | In-Claude interview runtime |
| `docs/quality-bar.md`, `docs/dogfood-notes.md` | Quality bar + dogfood findings |

---

## Conventions for every task

- **TDD:** within each task, write the failing test first, run it (see it fail), implement minimally, run it (see it pass), refactor, commit. Do not create separate "write tests" tasks.
- **Commits:** Conventional Commits (`feat:`, `fix:`, `test:`, `chore:`, `docs:`, `refactor:`, `ci:`). Commit at the end of every task; more often if a task has natural checkpoints.
- **Test command:** `npm test` runs Vitest once. `npx vitest run <path>` for one file. `npm run check` runs `lint && typecheck && test`.
- **No `any`.** `tsconfig` is strict; ESLint bans `any` and floating promises.
- **Spec references** point at files copied into `docs/` in Task 0: `docs/architecture.md`, `docs/interview-spec.md`, `docs/design/2026-08-30-team-ai-framework-design.md`.
- **Never** add a code path that calls an LLM from framework code. The connector probe only *detects and records* (design §3).
- **Non-destructive generation (design §18):** the generator never deletes a file and never overwrites a file it did not create in a prior run. Its output is tracked in `team-profile.yaml` `generated_paths: [{ path, sha256 }]`. Any other existing target is a *collision* — reported, not written. `init` stops and asks (`adopt-existing | siblings | subdir | abort`) before writing when collisions or an existing SME/agent-config are present.

---

## Milestone A — Repo skeleton and tooling

### Task 0: Repo skeleton, TypeScript, LF normalization

**Goal:** A buildable empty TypeScript package with strict config and LF line endings, committed.

**Files:**
- Create: `C:\Users\nicke\OneDrive\Desktop\team-ai\package.json`
- Create: `tsconfig.json`, `tsconfig.build.json`
- Create: `.gitattributes`, `.editorconfig`, `.nvmrc`
- Create: `src/index.ts` (empty barrel), `src/version.ts`
- Create: `.gitignore` (already present from brainstorming — extend it)
- Test: `src/version.test.ts`

**Acceptance Criteria:**
- [ ] `npm install` succeeds on Node 22.
- [ ] `npx tsc --noEmit` passes with zero errors.
- [ ] `git` reports LF (no CRLF warnings) after re-adding files.
- [ ] `npx vitest run src/version.test.ts` passes.

**Verify:** `node -v` shows v22.x; `npx tsc --noEmit && npx vitest run` → all pass.

**Steps:**

- [ ] **Step 1: `.gitattributes` (fixes the CRLF warnings seen in brainstorming)**

```gitattributes
* text=auto eol=lf
*.png binary
*.sqlite binary
```

- [ ] **Step 2: `.nvmrc` and `.editorconfig`**

`.nvmrc`:
```
22
```

`.editorconfig`:
```ini
root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
indent_style = space
indent_size = 2
trim_trailing_whitespace = true

[*.md]
trim_trailing_whitespace = false
```

- [ ] **Step 3: `package.json`**

```json
{
  "name": "team-ai",
  "version": "0.1.0",
  "description": "A forkable framework for standing up a team's AI capability: an owned knowledge base, scoped agents, deterministic scripts, and an eval harness.",
  "license": "Apache-2.0",
  "author": "nickejanssen",
  "repository": { "type": "git", "url": "https://github.com/nickejanssen/team-ai.git" },
  "type": "module",
  "engines": { "node": ">=22" },
  "bin": { "team-ai": "bin/team-ai.js" },
  "files": ["dist", "bin", "schemas", "catalog", "templates", "skills", "src/interview/questions.yaml"],
  "scripts": {
    "build": "tsc -p tsconfig.build.json",
    "typecheck": "tsc --noEmit",
    "lint": "eslint .",
    "format": "prettier --check .",
    "format:write": "prettier --write .",
    "test": "vitest run",
    "test:watch": "vitest",
    "check": "npm run lint && npm run typecheck && npm run test",
    "prepare": "lefthook install || true"
  },
  "dependencies": {
    "@inquirer/prompts": "^7.2.1",
    "ajv": "^8.17.1",
    "ajv-formats": "^3.0.1",
    "better-sqlite3": "^11.7.0",
    "commander": "^13.0.0",
    "gray-matter": "^4.0.3",
    "handlebars": "^4.7.8",
    "yaml": "^2.6.1"
  },
  "devDependencies": {
    "@types/better-sqlite3": "^7.6.12",
    "@types/node": "^22.10.5",
    "@typescript-eslint/eslint-plugin": "^8.19.1",
    "@typescript-eslint/parser": "^8.19.1",
    "@commitlint/cli": "^19.6.1",
    "@commitlint/config-conventional": "^19.6.0",
    "eslint": "^9.17.0",
    "eslint-config-prettier": "^9.1.0",
    "lefthook": "^1.10.1",
    "prettier": "^3.4.2",
    "typescript": "^5.7.3",
    "vitest": "^2.1.8"
  }
}
```

- [ ] **Step 4: `tsconfig.json`**

```json
{
  "compilerOptions": {
    "target": "ES2023",
    "lib": ["ES2023"],
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "rootDir": "src",
    "outDir": "dist",
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "noImplicitOverride": true,
    "noFallthroughCasesInSwitch": true,
    "verbatimModuleSyntax": true,
    "resolveJsonModule": true,
    "skipLibCheck": true,
    "declaration": true,
    "sourceMap": true
  },
  "include": ["src/**/*"],
  "exclude": ["dist", "node_modules", "templates", "**/*.test.ts"]
}
```

`tsconfig.build.json`:
```json
{ "extends": "./tsconfig.json", "exclude": ["dist", "node_modules", "templates", "**/*.test.ts"] }
```

- [ ] **Step 5: `src/version.ts` + failing test**

`src/version.ts`:
```ts
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

export function packageVersion(): string {
  const pkgPath = fileURLToPath(new URL("../package.json", import.meta.url));
  const pkg = JSON.parse(readFileSync(pkgPath, "utf8")) as { version: string };
  return pkg.version;
}
```

`src/version.test.ts`:
```ts
import { describe, expect, it } from "vitest";
import { packageVersion } from "./version.js";

describe("packageVersion", () => {
  it("returns a semver string starting at 0.1.0", () => {
    expect(packageVersion()).toMatch(/^\d+\.\d+\.\d+/);
  });
});
```

- [ ] **Step 6: run, expect fail then pass**

Run: `npx vitest run src/version.test.ts`
Expected first: FAIL (module/path resolution or version mismatch). Then implement/fix, expect PASS.

- [ ] **Step 7: extend `.gitignore`**

Append:
```
dist/
coverage/
*.tsbuildinfo
.tmp-dogfood/
```

- [ ] **Step 8: commit**

```bash
cd C:/Users/nicke/OneDrive/Desktop/team-ai
git add -A
git rm --cached -r . >/dev/null 2>&1; git add -A   # re-normalize line endings
git commit -m "chore: scaffold TypeScript package with strict config"
```

---

### Task 1: Lint, format, test tooling and git hooks

**Goal:** ESLint flat config, Prettier, Vitest config, and lefthook hooks all wired and enforced locally.

**Files:**
- Create: `eslint.config.js`, `.prettierrc.json`, `.prettierignore`
- Create: `vitest.config.ts`
- Create: `lefthook.yml`, `commitlint.config.js`
- Test: `src/tooling.test.ts` (asserts config files parse and key rules are present)

**Acceptance Criteria:**
- [ ] `npm run lint` passes on the current tree.
- [ ] `npm run format` passes.
- [ ] `npm test` passes.
- [ ] A commit with a non-conventional message is rejected by the `commit-msg` hook.
- [ ] `eslint.config.js` bans `@typescript-eslint/no-explicit-any` and `no-floating-promises`.

**Verify:** `npm run check` → all pass; `git commit -m "bad message"` on a dummy change → rejected with commitlint error.

**Steps:**

- [ ] **Step 1: `eslint.config.js`**

```js
import js from "@eslint/js";
import tseslint from "@typescript-eslint/eslint-plugin";
import tsparser from "@typescript-eslint/parser";
import prettier from "eslint-config-prettier";

export default [
  { ignores: ["dist/**", "node_modules/**", "templates/**", "coverage/**", ".tmp-dogfood/**"] },
  js.configs.recommended,
  {
    files: ["**/*.ts"],
    languageOptions: {
      parser: tsparser,
      parserOptions: { project: "./tsconfig.json", sourceType: "module" },
    },
    plugins: { "@typescript-eslint": tseslint },
    rules: {
      ...tseslint.configs["recommended-type-checked"].rules,
      "@typescript-eslint/no-explicit-any": "error",
      "@typescript-eslint/no-floating-promises": "error",
      "@typescript-eslint/explicit-function-return-type": ["error", { allowExpressions: true }],
      "no-console": "off",
    },
  },
  prettier,
];
```

- [ ] **Step 2: `.prettierrc.json`**

```json
{ "printWidth": 100, "singleQuote": false, "trailingComma": "all" }
```

`.prettierignore`:
```
dist
coverage
templates/**/*.hbs
*.md
```

- [ ] **Step 3: `vitest.config.ts`**

```ts
import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    include: ["src/**/*.test.ts"],
    coverage: { provider: "v8", include: ["src/**/*.ts"], exclude: ["src/**/*.test.ts"] },
    testTimeout: 15000,
  },
});
```

- [ ] **Step 4: `commitlint.config.js`**

```js
export default { extends: ["@commitlint/config-conventional"] };
```

- [ ] **Step 5: `lefthook.yml`**

```yaml
pre-commit:
  parallel: true
  commands:
    lint:
      glob: "*.{ts,js}"
      run: npx eslint {staged_files}
    format:
      glob: "*.{ts,js,json,yml,yaml}"
      run: npx prettier --check {staged_files}
commit-msg:
  commands:
    commitlint:
      run: npx commitlint --edit {1}
```

- [ ] **Step 6: failing test `src/tooling.test.ts`**

```ts
import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

describe("tooling config", () => {
  it("eslint bans explicit any", () => {
    const cfg = readFileSync("eslint.config.js", "utf8");
    expect(cfg).toContain('"@typescript-eslint/no-explicit-any": "error"');
  });
  it("lefthook runs commitlint on commit-msg", () => {
    const cfg = readFileSync("lefthook.yml", "utf8");
    expect(cfg).toContain("commitlint --edit");
  });
});
```

Run: `npx vitest run src/tooling.test.ts` → FAIL (files absent) → create → PASS.

- [ ] **Step 7: install hooks + verify rejection**

```bash
npx lefthook install
echo "// x" >> src/index.ts && git add src/index.ts
git commit -m "not conventional" || echo "rejected as expected"
git commit -m "chore: wire eslint, prettier, vitest, lefthook, commitlint"
```

---

### Task 2: Community health files

**Goal:** Apache-2.0 license and standard OSS governance files present and accurate.

**Files:**
- Create: `LICENSE` (Apache-2.0 full text), `NOTICE`
- Create: `SECURITY.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `CODEOWNERS`
- Create: `.github/PULL_REQUEST_TEMPLATE.md`
- Create: `.github/ISSUE_TEMPLATE/bug_report.md`, `feature_request.md`, `coverage_gap.md`
- Test: `src/governance.test.ts`

**Acceptance Criteria:**
- [ ] `LICENSE` is the verbatim Apache-2.0 text; `NOTICE` names the project and year.
- [ ] `CHANGELOG.md` follows Keep a Changelog with an `## [0.1.0]` section under `Unreleased`.
- [ ] `CONTRIBUTING.md` embeds the quality-bar checklist reference and the "no team content in framework" rule.
- [ ] `CODEOWNERS` assigns `* @nickejanssen`.

**Verify:** `npx vitest run src/governance.test.ts` → pass.

**Steps:**

- [ ] **Step 1: failing test**

```ts
import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

describe("governance", () => {
  it("LICENSE is Apache-2.0", () => {
    expect(readFileSync("LICENSE", "utf8")).toContain("Apache License");
    expect(readFileSync("LICENSE", "utf8")).toContain("Version 2.0, January 2004");
  });
  it("CHANGELOG has 0.1.0", () => {
    expect(readFileSync("CHANGELOG.md", "utf8")).toMatch(/##\s*\[0\.1\.0\]/);
  });
  it("CONTRIBUTING forbids team content in framework code", () => {
    expect(readFileSync("CONTRIBUTING.md", "utf8").toLowerCase()).toContain("no team");
  });
});
```

- [ ] **Step 2: fetch the Apache-2.0 text**

Write the standard Apache License 2.0 text to `LICENSE` (from https://www.apache.org/licenses/LICENSE-2.0.txt — the canonical body, unmodified).

`NOTICE`:
```
team-ai
Copyright 2026 nickejanssen

This product includes software developed as an open framework for
standing up team AI capabilities.
```

- [ ] **Step 3: `CHANGELOG.md`**

```markdown
# Changelog

All notable changes to this project are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-08-30
### Added
- Initial framework: guided interview, generator, deterministic scripts,
  lexical retrieval adapter, catalogs, agent/skill/persona templates,
  eval harness, optional local stdio MCP server template.
```

- [ ] **Step 4: `CONTRIBUTING.md`**

Include: dev setup (`nvm use`, `npm install`, `npm run check`); conventional commits; the rule "**Framework code carries no team's content.** `src/`, `schemas/`, and `templates/` must contain no team, partner, or product names. `npm run check` runs `team-ai check-agnostic` which enforces this."; and "Before merging, walk `docs/quality-bar.md` and confirm your change keeps every answer honest."

- [ ] **Step 5: `CODEOWNERS`**

```
* @nickejanssen
```

- [ ] **Step 6: PR + issue templates**

`.github/PULL_REQUEST_TEMPLATE.md`: sections — What changed / Why / Quality-bar impact (which of the 17 lines does this touch?) / Tests / Docs.

`.github/ISSUE_TEMPLATE/coverage_gap.md`: front-matter `name: Coverage gap`, body prompts for the question asked, expected owner, namespace.

- [ ] **Step 7: run test + commit**

```bash
npx vitest run src/governance.test.ts
git add -A && git commit -m "docs: add Apache-2.0 license and OSS governance files"
```

---

### Task 3: Framework CI workflow

**Goal:** GitHub Actions runs lint, typecheck, test, `validate`, and secret scan on PRs and pushes to `main`.

**Files:**
- Create: `.github/workflows/ci.yml`
- Create: `.github/workflows/.gitleaks.toml` (allowlist for the Apache text if needed)
- Test: `src/ci-config.test.ts` (YAML parses; jobs present)

**Acceptance Criteria:**
- [ ] `ci.yml` has jobs: `lint-typecheck-test`, `validate`, `secret-scan`.
- [ ] Node 22 via `actions/setup-node` with `cache: npm`.
- [ ] `validate` job runs `npm run build` then `node dist/cli.js doctor --self` (a self-check added in Task 18) — until Task 18 lands, it runs `npm run test`.
- [ ] `secret-scan` runs `gitleaks/gitleaks-action`.
- [ ] Workflow uses `permissions: contents: read`.

**Verify:** `npx vitest run src/ci-config.test.ts` → pass; `yamllint`/`js-yaml` parse succeeds.

**Steps:**

- [ ] **Step 1: failing test**

```ts
import { readFileSync } from "node:fs";
import { parse } from "yaml";
import { describe, expect, it } from "vitest";

describe("ci.yml", () => {
  const doc = parse(readFileSync(".github/workflows/ci.yml", "utf8")) as {
    jobs: Record<string, unknown>;
  };
  it("has the three required jobs", () => {
    expect(Object.keys(doc.jobs).sort()).toEqual(
      ["lint-typecheck-test", "secret-scan", "validate"].sort(),
    );
  });
});
```

- [ ] **Step 2: `ci.yml`**

```yaml
name: CI
on:
  pull_request:
  push:
    branches: [main]
permissions:
  contents: read
jobs:
  lint-typecheck-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: "22", cache: "npm" }
      - run: npm ci
      - run: npm run lint
      - run: npm run typecheck
      - run: npm run test
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: "22", cache: "npm" }
      - run: npm ci
      - run: npm run build
      - run: node dist/cli.js check-agnostic
      - run: node dist/cli.js validate-kb --schema-only
  secret-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - uses: gitleaks/gitleaks-action@v2
        env: { GITLEAKS_ENABLE_UPLOAD_ARTIFACT: "false" }
```

Note: the `validate` job's `node dist/cli.js …` lines are placeholders that become real in Tasks 12 and 39. Until then, replace both `run:` lines with `run: npm run test`.

- [ ] **Step 3: run test + commit**

```bash
npx vitest run src/ci-config.test.ts
git add -A && git commit -m "ci: add lint/typecheck/test, validate, and secret-scan workflow"
```

---

## Milestone B — Schemas and knowledge-base primitives

### Task 4: JSON Schemas and Ajv validator

**Goal:** Five JSON Schemas plus a typed Ajv wrapper that validates data and returns readable errors.

**Files:**
- Create: `schemas/frontmatter.schema.json`, `schemas/agent.schema.json`, `schemas/manifest.schema.json`, `schemas/spoke.schema.json`, `schemas/team-profile.schema.json`
- Create: `src/schema/load.ts`, `src/schema/validate.ts`, `src/schema/types.ts`
- Create: `src/schema/fixtures/{valid,invalid}/*.{yaml,json}`
- Test: `src/schema/validate.test.ts`

**Acceptance Criteria:**
- [ ] Each schema is Draft 2020-12, `$id` set, `additionalProperties: false` at the top level.
- [ ] `frontmatter.schema.json` matches architecture §8.1 exactly: `id`, `namespace`, `title`, `owner`, `status` enum `draft|active|deprecated`, `review_by` (date), `sensitivity` enum `public|internal|confidential`, `source` pattern `authored|synced:*`, `source_url`, `tags`, `supersedes`, optional `relations` object (`depends_on`, `used_by_partner`, `owned_by_role`, plus free additional relation keys as arrays of strings).
- [ ] `agent.schema.json` matches architecture §7: `name`, `kind` enum `router|subagent|persona`, `description`, `model_tier` enum `none|small|large`, `kb_namespaces` (array), `tools` (array), `max_hops` (integer ≥ 0), `escalate_to`, `instructions_file`.
- [ ] `validate<T>(schemaName, data)` returns `{ ok: true, value: T }` or `{ ok: false, errors: string[] }` with `instancePath`-based messages.
- [ ] Every fixture in `fixtures/valid/` passes; every fixture in `fixtures/invalid/` fails with the expected first error.

**Verify:** `npx vitest run src/schema/validate.test.ts` → pass.

**Steps:**

- [ ] **Step 1: write `src/schema/validate.test.ts` first**

```ts
import { describe, expect, it } from "vitest";
import { validate } from "./validate.js";

describe("frontmatter schema", () => {
  it("accepts a minimal valid doc", () => {
    const r = validate("frontmatter", {
      id: "x.platform.rate-limits",
      namespace: "platform",
      title: "Rate limits",
      owner: "solutions-architect",
      status: "active",
      review_by: "2026-12-01",
      sensitivity: "internal",
      source: "authored",
      tags: ["429"],
      supersedes: [],
    });
    expect(r.ok).toBe(true);
  });

  it("rejects an unknown status with a path-anchored message", () => {
    const r = validate("frontmatter", {
      id: "x.a.b", namespace: "a", title: "t", owner: "o",
      status: "archived", review_by: "2026-12-01", sensitivity: "internal",
      source: "authored", tags: [], supersedes: [],
    });
    expect(r.ok).toBe(false);
    if (!r.ok) expect(r.errors[0]).toContain("/status");
  });

  it("accepts a relations block", () => {
    const r = validate("frontmatter", {
      id: "x.a.b", namespace: "a", title: "t", owner: "o", status: "active",
      review_by: "2026-12-01", sensitivity: "internal", source: "authored",
      tags: [], supersedes: [],
      relations: { depends_on: ["x.a.auth"], used_by_partner: ["acme"], owned_by_role: "architect" },
    });
    expect(r.ok).toBe(true);
  });
});

describe("agent schema", () => {
  it("enforces model_tier enum and max_hops >= 0", () => {
    const bad = validate("agent", {
      name: "p", kind: "subagent", description: "d", model_tier: "medium",
      kb_namespaces: [], tools: [], max_hops: -1, instructions_file: "a.md",
    });
    expect(bad.ok).toBe(false);
  });
});
```

- [ ] **Step 2: `src/schema/load.ts`**

```ts
import Ajv2020 from "ajv/dist/2020.js";
import addFormats from "ajv-formats";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

export type SchemaName =
  | "frontmatter" | "agent" | "manifest" | "spoke" | "team-profile" | "questions" | "golden";

const ajv = addFormats(new Ajv2020({ allErrors: true, strict: false }));

export function schemaPath(name: SchemaName): string {
  return fileURLToPath(new URL(`../../schemas/${name}.schema.json`, import.meta.url));
}

export function loadValidator(name: SchemaName) {
  const key = `team-ai/${name}`;
  const existing = ajv.getSchema(key);
  if (existing) return existing;
  const schema = JSON.parse(readFileSync(schemaPath(name), "utf8")) as object;
  ajv.addSchema(schema, key);
  return ajv.getSchema(key)!;
}
```

- [ ] **Step 3: `src/schema/validate.ts`**

```ts
import { loadValidator, type SchemaName } from "./load.js";

export type ValidateResult<T> = { ok: true; value: T } | { ok: false; errors: string[] };

export function validate<T = unknown>(name: SchemaName, data: unknown): ValidateResult<T> {
  const v = loadValidator(name);
  if (v(data)) return { ok: true, value: data as T };
  const errors = (v.errors ?? []).map((e) => {
    const where = e.instancePath || "(root)";
    return `${where} ${e.message ?? "is invalid"}`.trim();
  });
  return { ok: false, errors: errors.length ? errors : ["schema validation failed"] };
}
```

- [ ] **Step 4: author the five schemas**

Write each `schemas/*.schema.json` to satisfy the acceptance criteria. `frontmatter.schema.json` skeleton:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://github.com/nickejanssen/team-ai/schemas/frontmatter.schema.json",
  "type": "object",
  "additionalProperties": false,
  "required": ["id", "namespace", "title", "owner", "status", "review_by", "sensitivity", "source", "tags", "supersedes"],
  "properties": {
    "id": { "type": "string", "pattern": "^[a-z0-9]+(\\.[a-z0-9-]+)+$" },
    "namespace": { "type": "string", "pattern": "^[a-z0-9][a-z0-9/-]*$" },
    "title": { "type": "string", "minLength": 1 },
    "owner": { "type": "string", "minLength": 1 },
    "status": { "enum": ["draft", "active", "deprecated"] },
    "review_by": { "type": "string", "format": "date" },
    "sensitivity": { "enum": ["public", "internal", "confidential"] },
    "source": { "type": "string", "pattern": "^(authored|synced:[a-z0-9-]+)$" },
    "source_url": { "type": ["string", "null"], "format": "uri" },
    "tags": { "type": "array", "items": { "type": "string" } },
    "supersedes": { "type": "array", "items": { "type": "string" } },
    "relations": {
      "type": "object",
      "additionalProperties": { "type": ["array", "string"], "items": { "type": "string" } },
      "properties": {
        "depends_on": { "type": "array", "items": { "type": "string" } },
        "used_by_partner": { "type": "array", "items": { "type": "string" } },
        "owned_by_role": { "type": "string" }
      }
    }
  }
}
```

Author `agent`, `manifest` (architecture §12.2 `domains[]`), `spoke` (architecture §13 `spoke.yaml`), `team-profile` (interview-spec §13: every answer + `deferred: []` + timestamps) similarly.

- [ ] **Step 5: fixtures + run to green**

Create 2+ valid and 2+ invalid fixtures per schema under `src/schema/fixtures/`. Load them in a parametrized test. Run `npx vitest run src/schema/` until green.

- [ ] **Step 6: commit**

```bash
git add -A && git commit -m "feat(schema): add JSON schemas and Ajv validator"
```

---

### Task 5: KB front matter parse/serialize and loader

**Goal:** Load every markdown file under a `kb/` root into typed `KbDoc` objects with parsed, schema-valid front matter.

**Files:**
- Create: `src/kb/frontmatter.ts`, `src/kb/loader.ts`, `src/kb/types.ts`
- Create: `src/kb/fixtures/kb/**` (a tiny 3-doc corpus)
- Test: `src/kb/frontmatter.test.ts`, `src/kb/loader.test.ts`

**Acceptance Criteria:**
- [ ] `parseFrontmatter(raw)` returns `{ data, body }`; round-trips via `serializeFrontmatter(data, body)` with stable key order matching schema property order.
- [ ] `loadKb(root)` returns `KbDoc[]` sorted by `path`, each `{ id, path, frontmatter, body, headings }`.
- [ ] `loadKb` throws `KbValidationError` listing every invalid file and its first error (not just the first file).
- [ ] Files outside `.md` are ignored; `_backlog/` is loaded but flagged `isBacklog: true`.

**Verify:** `npx vitest run src/kb/frontmatter.test.ts src/kb/loader.test.ts` → pass.

**Steps:**

- [ ] **Step 1: failing tests**

```ts
// src/kb/loader.test.ts
import { describe, expect, it } from "vitest";
import { loadKb } from "./loader.js";

describe("loadKb", () => {
  it("loads the fixture corpus sorted by path", async () => {
    const docs = await loadKb("src/kb/fixtures/kb");
    expect(docs.map((d) => d.frontmatter.namespace)).toContain("platform");
    expect(docs).toEqual([...docs].sort((a, b) => a.path.localeCompare(b.path)));
  });

  it("reports all invalid docs at once", async () => {
    await expect(loadKb("src/kb/fixtures/kb-broken")).rejects.toThrow(/2 invalid/);
  });
});
```

- [ ] **Step 2: `src/kb/frontmatter.ts`**

```ts
import matter from "gray-matter";
import { stringify } from "yaml";

export interface ParsedDoc { data: Record<string, unknown>; body: string }

export function parseFrontmatter(raw: string): ParsedDoc {
  const parsed = matter(raw);
  return { data: parsed.data as Record<string, unknown>, body: parsed.content.trimStart() };
}

const KEY_ORDER = [
  "id", "namespace", "title", "owner", "status", "review_by", "sensitivity",
  "source", "source_url", "tags", "supersedes", "relations",
];

export function serializeFrontmatter(data: Record<string, unknown>, body: string): string {
  const ordered: Record<string, unknown> = {};
  for (const k of KEY_ORDER) if (k in data) ordered[k] = data[k];
  for (const k of Object.keys(data)) if (!(k in ordered)) ordered[k] = data[k];
  return `---\n${stringify(ordered)}---\n\n${body.trimStart()}\n`;
}
```

- [ ] **Step 3: `src/kb/loader.ts`** — walk with `node:fs` `readdir({recursive:true})`, filter `.md`, `parseFrontmatter`, `validate("frontmatter", data)`, collect errors, extract `headings` via a regex on `^(#{1,6})\s+(.+)$`. Throw `KbValidationError` with `\`${n} invalid document(s):\\n\` + joined lines`.

- [ ] **Step 4: fixtures** — 3 valid docs across `platform/` and `operating/`, plus a `kb-broken/` with 2 deliberately invalid docs.

- [ ] **Step 5: run green, commit**

```bash
npx vitest run src/kb/
git add -A && git commit -m "feat(kb): front matter parse/serialize and validating loader"
```

---

### Task 6: KB chunker

**Goal:** Split each doc into retrieval chunks on H2/H3 with a deterministic token estimate, carrying heading path and full front matter.

**Files:**
- Create: `src/kb/chunk.ts`
- Test: `src/kb/chunk.test.ts`

**Acceptance Criteria:**
- [ ] `chunkDoc(doc)` splits at every `##` and `###`; content before the first H2 is its own chunk (`heading_path` = document title).
- [ ] `estimateTokens(text)` = `Math.ceil(words * 1.3)`; documented as approximate in a top-of-file comment.
- [ ] A section whose estimate exceeds the hard cap (1200) is further split at paragraph boundaries; target is 800.
- [ ] Each `Chunk` = `{ doc_id, chunk_id, path, heading_path, text, metadata }` where `metadata` is the doc's full front matter.
- [ ] `chunk_id` is stable: `\`${doc_id}::${slug(heading_path)}::${ordinal}\``.

**Verify:** `npx vitest run src/kb/chunk.test.ts` → pass.

**Steps:**

- [ ] **Step 1: failing test**

```ts
import { describe, expect, it } from "vitest";
import { chunkDoc, estimateTokens } from "./chunk.js";

const doc = {
  id: "x.platform.rl",
  path: "kb/platform/rl.md",
  frontmatter: { id: "x.platform.rl", title: "Rate limits", namespace: "platform" },
  body: "Intro para.\n\n## Auth\nAuth text.\n\n### 429s\nWhat to do about 429s.\n",
  headings: [],
} as never;

describe("chunkDoc", () => {
  it("emits a preamble chunk then one per H2/H3", () => {
    const chunks = chunkDoc(doc);
    expect(chunks.map((c) => c.heading_path)).toEqual([
      "Rate limits", "Rate limits > Auth", "Rate limits > Auth > 429s",
    ]);
    expect(chunks[0].metadata.namespace).toBe("platform");
  });
  it("estimateTokens is words * 1.3 rounded up", () => {
    expect(estimateTokens("one two three")).toBe(4);
  });
});
```

- [ ] **Step 2: implement `chunk.ts`** per the criteria. Use a simple line scanner tracking a heading stack `[h1?, h2?, h3?]`; emit on H2/H3 boundary; post-process oversize chunks by splitting on `\n\n`.

- [ ] **Step 3: run green, commit**

```bash
git add -A && git commit -m "feat(kb): deterministic H2/H3 chunker with token estimate"
```

---

### Task 7: KB citations and relations resolution

**Goal:** Resolve `path#heading` citation targets and validate `relations` targets against loaded doc ids.

**Files:**
- Create: `src/kb/citations.ts`, `src/kb/relations.ts`
- Test: `src/kb/citations.test.ts`, `src/kb/relations.test.ts`

**Acceptance Criteria:**
- [ ] `resolveCitation(docs, "kb/platform/rl.md#auth")` returns the matching `KbDoc` + heading, or `{ ok: false, reason }`.
- [ ] Heading match is slug-insensitive (`#429s` matches `### 429s`).
- [ ] `checkRelations(docs)` returns `RelationError[]` for every relation value that is not a known doc `id` (skipping `used_by_partner` which references partner slugs, not doc ids — per architecture §8.1).
- [ ] `owned_by_role` is validated against a passed-in set of known role names (from the catalog), not doc ids.

**Verify:** `npx vitest run src/kb/citations.test.ts src/kb/relations.test.ts` → pass.

**Steps:**

- [ ] **Step 1: failing tests** covering: a resolvable citation, a missing file, a missing heading, a relations block with one bad `depends_on` id, and a valid `used_by_partner` that must NOT error.

- [ ] **Step 2: implement.** `citations.ts` builds a `Map<path, KbDoc>` and a per-doc heading slug set. `relations.ts` iterates `doc.frontmatter.relations`, applying the per-key rules above.

- [ ] **Step 3: run green, commit**

```bash
git add -A && git commit -m "feat(kb): citation resolution and relations target checks"
```

---

## Milestone C — Retrieval adapter

### Task 8: Retrieval interface, types, and index.lock

**Goal:** The exact `RetrievalAdapter` interface from architecture §9 plus a typed `index.lock` reader/writer.

**Files:**
- Create: `src/retrieval/types.ts`, `src/retrieval/index-lock.ts`
- Test: `src/retrieval/index-lock.test.ts`

**Acceptance Criteria:**
- [ ] `types.ts` declares `RetrievalAdapter`, `Hit`, `Document`, `IndexStats`, `SearchOpts` matching architecture §9 verbatim (field names, optionality, `mode` union `lexical|vector|graph|hybrid`, `k` default 8 / hard cap 20 documented).
- [ ] `IndexLock` = `{ driver: string; chunk: { split_on: string[]; target_tokens: number; hard_cap: number }; embedding: { provider: string; model: string; version: string } | null }`.
- [ ] `readIndexLock(dir)` returns the parsed lock or a documented default (`driver: "lexical"`, `chunk` = H2/H3/800/1200, `embedding: null`).
- [ ] `lockChanged(a, b)` returns true if `driver`, any `chunk` field, or `embedding` differs — the "forces a full reindex" signal (architecture §8.3).

**Verify:** `npx vitest run src/retrieval/index-lock.test.ts` → pass.

**Steps:**

- [ ] **Step 1: `src/retrieval/types.ts`**

```ts
export interface SearchOpts {
  namespace?: string | string[];
  k?: number; // default 8, hard cap 20
  filters?: { status?: string[]; sensitivity?: string[]; tags?: string[]; owner?: string };
  mode?: "lexical" | "vector" | "graph" | "hybrid";
}

export interface Hit {
  doc_id: string;
  chunk_id: string;
  path: string; // repo-relative, citation target
  heading_path: string;
  score: number; // normalized 0..1 across all drivers
  text: string;
  metadata: Record<string, unknown>; // front matter
}

export interface Document { id: string; path: string; frontmatter: Record<string, unknown>; body: string }
export interface IndexStats { documents: number; chunks: number; driver: string; tookMs: number }

export interface RetrievalAdapter {
  search(query: string, opts?: SearchOpts): Promise<Hit[]>;
  get(idOrPath: string, section?: string): Promise<Document>;
  neighbors?(id: string, relation?: string, depth?: number): Promise<Hit[]>;
  reindex(paths?: string[]): Promise<IndexStats>;
}
```

- [ ] **Step 2: failing test for `index-lock.ts`** (default when file absent; `lockChanged` true on driver swap; false on identical).

- [ ] **Step 3: implement `index-lock.ts`** using `yaml`.

- [ ] **Step 4: run green, commit**

```bash
git add -A && git commit -m "feat(retrieval): adapter interface, Hit contract, index.lock"
```

---

### Task 9: Lexical driver (SQLite FTS5)

**Goal:** A working `lexical` `RetrievalAdapter` over the chunked KB using `better-sqlite3` FTS5, with BM25 scores normalized to 0..1.

**Files:**
- Create: `src/retrieval/lexical.ts`
- Test: `src/retrieval/lexical.test.ts`

**Acceptance Criteria:**
- [ ] `new LexicalAdapter({ kbRoot, dbPath })`; `reindex()` builds an FTS5 table `chunks(text, doc_id UNINDEXED, chunk_id UNINDEXED, path UNINDEXED, heading_path UNINDEXED, metadata UNINDEXED)`.
- [ ] `search(q, {k})` returns `Hit[]` ordered by relevance, `score` **absolute-normalized** (NOT min-max — min-max crushes a relevant 2nd hit to 0.0 and breaks the refuse threshold): `score_i = clamp(-bm25_i / (-bm25_i + K), 0, 1)` where FTS5 `bm25()` is negative for matches (more negative = better), a non-negative bm25 maps to score 0, and `K` is tuned so a strong multi-term match scores > 0.55 while a single-common-word match scores < 0.4. Document the formula + `K` choice. Consequence: a weak top hit correctly scores low, so the 0.2 refuse threshold in Tasks 12/15 is meaningful.
- [ ] `k` defaults to 8, hard-capped at 20 even if a larger `k` is passed.
- [ ] `namespace` and `filters.status`/`filters.sensitivity` are applied as post-filters on chunk metadata.
- [ ] `get(idOrPath, section?)` returns the full `Document`; `section` returns only that heading's slice.
- [ ] `reindex()` is idempotent — running twice yields identical row counts and `search` results.
- [ ] DB file lives at `dbPath` (default `.team-ai/index.sqlite`), gitignored.

**Verify:** `npx vitest run src/retrieval/lexical.test.ts` → pass, including a query that must rank a known doc first.

**Steps:**

- [ ] **Step 1: failing test**

```ts
import { rmSync } from "node:fs";
import { afterAll, describe, expect, it } from "vitest";
import { LexicalAdapter } from "./lexical.js";

const dbPath = ".tmp-test/idx.sqlite";
afterAll(() => rmSync(".tmp-test", { recursive: true, force: true }));

describe("LexicalAdapter", () => {
  it("indexes and ranks the rate-limit doc first for a 429 query", async () => {
    const a = new LexicalAdapter({ kbRoot: "src/kb/fixtures/kb", dbPath });
    const stats = await a.reindex();
    expect(stats.chunks).toBeGreaterThan(0);
    const hits = await a.search("what to do about 429 errors", { k: 5 });
    expect(hits[0]?.path).toMatch(/rate|rl/);
    expect(hits[0]?.score).toBeGreaterThan(0.5);
    expect(hits[0]?.score).toBeLessThanOrEqual(1);
  });

  it("caps k at 20 and is idempotent", async () => {
    const a = new LexicalAdapter({ kbRoot: "src/kb/fixtures/kb", dbPath });
    await a.reindex();
    const s1 = await a.reindex();
    const hits = await a.search("auth", { k: 999 });
    expect(hits.length).toBeLessThanOrEqual(20);
    expect(s1.chunks).toBe((await a.reindex()).chunks);
  });
});
```

- [ ] **Step 2: implement `lexical.ts`** — `reindex` drops+recreates the FTS5 virtual table, loads docs via `loadKb`, chunks via `chunkDoc`, inserts rows in a transaction, stores `metadata` as JSON. `search` runs `SELECT ..., bm25(chunks) AS rank FROM chunks WHERE chunks MATCH ? ORDER BY rank LIMIT ?`, then normalizes and post-filters.

- [ ] **Step 3: run green, commit**

```bash
git add -A && git commit -m "feat(retrieval): lexical SQLite FTS5 driver with normalized scores"
```

---

### Task 10: Honest stubs and driver factory

**Goal:** The other five drivers exist, implement the interface, and fail loudly; a factory returns the driver named in `index.lock`.

**Files:**
- Create: `src/retrieval/stubs.ts`, `src/retrieval/not-implemented.ts`, `src/retrieval/factory.ts`
- Test: `src/retrieval/stubs.test.ts`, `src/retrieval/factory.test.ts`

**Acceptance Criteria:**
- [ ] `NotImplementedError` message names the driver and points at "the phase-8 index checkpoint (docs/architecture.md §19)".
- [ ] `vector-embedded`, `vector-pgvector`, `vector-hosted`, `graph`, `hybrid` each export a class implementing `RetrievalAdapter`; every method rejects with `NotImplementedError`.
- [ ] `createAdapter(dir)` reads `index.lock`; `lexical` → `LexicalAdapter`; any of the five → the matching stub; unknown → throws with the list of valid drivers.
- [ ] TypeScript compiles — the stubs prove the interface is honest (no `@ts-expect-error`, no `any`).

**Verify:** `npx vitest run src/retrieval/stubs.test.ts src/retrieval/factory.test.ts` → pass.

**Steps:**

- [ ] **Step 1: failing tests** — each stub method rejects with a message containing the driver name; `createAdapter` on a `lexical` lock returns something with a working `search`.

- [ ] **Step 2: implement.** One `abstract class NotImplementedAdapter` with all methods rejecting; five one-line subclasses setting `protected driver = "graph"` etc.

- [ ] **Step 3: run green, commit**

```bash
git add -A && git commit -m "feat(retrieval): honest NotImplemented stubs and driver factory"
```

---

## Milestone D — Deterministic commands

All commands live in `src/commands/*.ts` exporting `run(args): Promise<number>` (process exit code) and are wired into `src/cli.ts` (commander) in Task 11. **No command calls a model.**

### Task 11: CLI shell + `validate-kb` + `validate-citations`

**Goal:** The `team-ai` binary exists and runs two validation commands used by CI.

**Files:**
- Create: `bin/team-ai.js`, `src/cli.ts`
- Create: `src/commands/validate-kb.ts`, `src/commands/validate-citations.ts`
- Test: `src/commands/validate-kb.test.ts`, `src/commands/validate-citations.test.ts`, `src/cli.test.ts`

**Acceptance Criteria:**
- [ ] `bin/team-ai.js` is `#!/usr/bin/env node` + `import("../dist/cli.js")`.
- [ ] `team-ai --help` lists all commands; `team-ai --version` prints `packageVersion()`.
- [ ] `validate-kb [--root kb] [--schema-only]` — `--schema-only` validates every doc's front matter and exits non-zero on any failure with a per-file report; without it, also runs `checkRelations`.
- [ ] `validate-citations [--root .]` — scans `kb/**/*.md` and `agents/**/*.md` for `](kb/...)` and `path#heading` links and reports unresolved ones; exit non-zero if any.
- [ ] Both print `OK` + counts on success.

**Verify:** `npm run build && node dist/cli.js validate-kb --root src/kb/fixtures/kb --schema-only` → exit 0, `OK 3 documents`.

**Steps:**

- [ ] **Step 1: failing `src/cli.test.ts`** using `execa`-style `node:child_process` on `dist/` — or import the commander program and assert `program.commands.map(c => c.name())`.

- [ ] **Step 2: `src/cli.ts`**

```ts
import { Command } from "commander";
import { packageVersion } from "./version.js";
import * as validateKb from "./commands/validate-kb.js";
import * as validateCitations from "./commands/validate-citations.js";

export function buildProgram(): Command {
  const program = new Command();
  program.name("team-ai").description("Forkable team AI capability framework").version(packageVersion());

  program.command("validate-kb")
    .option("--root <dir>", "kb root", "kb")
    .option("--schema-only", "front matter only", false)
    .action(async (opts) => process.exit(await validateKb.run(opts)));

  program.command("validate-citations")
    .option("--root <dir>", "repo root", ".")
    .action(async (opts) => process.exit(await validateCitations.run(opts)));

  return program;
}

if (import.meta.url === `file://${process.argv[1]}`) buildProgram().parseAsync(process.argv);
```

- [ ] **Step 3: implement both commands** on top of `src/kb/*` and `src/schema/*`.

- [ ] **Step 4: build, run, green, commit**

```bash
npm run build && node dist/cli.js validate-kb --root src/kb/fixtures/kb --schema-only
npx vitest run src/commands/ src/cli.test.ts
git add -A && git commit -m "feat(cli): binary shell plus validate-kb and validate-citations"
```

---

### Task 12: `reindex` + `search`

**Goal:** Rebuild the index from disk and query it from the CLI with cited output.

**Files:**
- Create: `src/commands/reindex.ts`, `src/commands/search.ts`
- Test: `src/commands/reindex.test.ts`, `src/commands/search.test.ts`

**Acceptance Criteria:**
- [ ] `reindex [--root .]` calls `createAdapter(root).reindex()`, writes/refreshes `index.lock` if absent, prints `IndexStats`.
- [ ] `search "<query>" [--k 8] [--namespace platform] [--json]` prints ranked results as `score  path#heading` lines, or JSON `Hit[]` with `--json`.
- [ ] `search` exits 0 with a "no results above threshold" line when nothing matches (threshold 0.2) — this is the deterministic refuse signal used later by the router template.
- [ ] Neither command prints text that isn't derived from the index (no model).

**Verify:** `node dist/cli.js reindex --root src/kb/fixtures/kb && node dist/cli.js search "429" --root src/kb/fixtures/kb` → ranked lines.

**Steps:**

- [ ] **Step 1: failing tests** — reindex returns chunks>0; search JSON output parses to `Hit[]`; empty query → "no results".
- [ ] **Step 2: implement**, reusing `createAdapter`.
- [ ] **Step 3: green, commit** `feat(cli): reindex and search commands`.

---

### Task 13: `assemble-manifest`

**Goal:** Merge the instance manifest fragment and any spoke `spoke.yaml` files into a validated `manifest.yaml`.

**Files:**
- Create: `src/commands/assemble-manifest.ts`, `src/manifest/assemble.ts`
- Test: `src/manifest/assemble.test.ts`

**Acceptance Criteria:**
- [ ] Reads `agents/manifest.fragment.yaml` (instance domains) + every `spokes/*/spoke.yaml` `domains:` block.
- [ ] Output validates against `schemas/manifest.schema.json`; duplicate domain `id`s are a hard error.
- [ ] Deterministic ordering: domains sorted by `id`.
- [ ] `--check` mode compares freshly-assembled output to the committed `manifest.yaml` and exits non-zero if they differ (for CI).

**Verify:** `npx vitest run src/manifest/assemble.test.ts` → pass.

**Steps:**
- [ ] Failing test with a fixture instance + one fixture spoke → expect merged, sorted, valid manifest; a second test with duplicate ids → throws.
- [ ] Implement `assemble.ts` (pure) + thin command wrapper.
- [ ] Green, commit `feat(cli): assemble-manifest with --check`.

---

### Task 14: `freshness-audit`

**Goal:** Report stale, orphaned, and unowned docs as JSON; optionally open GitHub issues behind a flag.

**Files:**
- Create: `src/commands/freshness-audit.ts`, `src/audit/freshness.ts`
- Test: `src/audit/freshness.test.ts`

**Acceptance Criteria:**
- [ ] `stale` = `review_by` < today; `orphaned` = not referenced by any citation or relation and not in a namespace index doc; `unowned` = `owner` missing or not a known role/person.
- [ ] Default output: JSON to stdout `{ stale: [...], orphaned: [...], unowned: [...], summary: {...} }`, exit 0.
- [ ] `--fail-on-stale` exits non-zero if `stale` non-empty (for CI freshness gate).
- [ ] `--open-issues` is accepted but, absent `GITHUB_TOKEN` + `--repo`, prints "would open N issues" and does nothing — no network by default (design §5.3, "no ops burden").
- [ ] `today` is injectable for tests.

**Verify:** `npx vitest run src/audit/freshness.test.ts` → pass with a fixture doc whose `review_by` is in the past.

**Steps:**
- [ ] Failing test: fixture with one past-due doc → `stale.length === 1`; `--fail-on-stale` → exit 1.
- [ ] Implement pure `freshness.ts(docs, { today })` + command wrapper.
- [ ] Green, commit `feat(cli): freshness-audit (JSON, --fail-on-stale, dry-run issues)`.

---

### Task 15: Eval harness — schema, runner, example

**Goal:** A golden-question schema, a deterministic `run-evals` command computing the architecture §16 metrics, and one clearly-marked example file.

**Files:**
- Create: `schemas/golden.schema.json`
- Create: `src/commands/run-evals.ts`, `src/evals/run.ts`, `src/evals/metrics.ts`
- Create: `evals/golden/example.golden.yaml`
- Test: `src/evals/run.test.ts`, `src/evals/metrics.test.ts`

**Acceptance Criteria:**
- [ ] `golden.schema.json` matches architecture §16: `id`, `question`, `expect_namespace`, `expect_paths[]`, `expect_route`, `expect_tier_max` (`none|small|large`), `must_cite` (bool).
- [ ] `run-evals [--golden evals/golden] [--root .]` loads all `*.golden.yaml`, validates them, runs each question through `search` (lexical) + deterministic routing (keyword/namespace match against `manifest.yaml`), and reports:
  - retrieval hit rate @8 (expected path present in top 8)
  - citation validity (every `expect_paths` entry resolves via `src/kb/citations`)
  - routing accuracy (computed route === `expect_route`)
  - refusal correctness (questions marked `expect_route: __refuse__` must produce no hit ≥ 0.2)
  - tier ceiling (computed tier ≤ `expect_tier_max`; deterministic path is always `none`/`small`)
- [ ] Exit non-zero if any metric is below its gate (gates configurable via `evals/gates.yaml`, defaults in architecture §16).
- [ ] `example.golden.yaml` has a header comment: `# EXAMPLE ONLY — replace with your team's real golden questions. Not run in framework CI.` and is excluded from the framework's own `run-evals`.
- [ ] **No real golden questions ship.**

**Verify:** `npx vitest run src/evals/` → pass against a fixture golden set + fixture manifest + fixture kb.

**Steps:**
- [ ] **Step 1: failing `metrics.test.ts`** — feed synthetic `{expected, actual}` arrays, assert hit-rate/routing-accuracy math.
- [ ] **Step 2: failing `run.test.ts`** — fixture golden set (3 Qs, one a `__refuse__`) over fixture kb → expect a report object with all five metrics and a pass/fail per gate.
- [ ] **Step 3: implement** `metrics.ts` (pure) then `run.ts` (wires kb + manifest + search).
- [ ] **Step 4: author `example.golden.yaml`** with 2 obviously-fake questions ("What does the EXAMPLE widget do?").
- [ ] **Step 5: green, commit** `feat(evals): golden schema, deterministic runner, example set`.

---

### Task 16: `validate-spoke`

**Goal:** Check a spoke repo against the architecture §13 contract.

**Files:**
- Create: `src/commands/validate-spoke.ts`, `src/spoke/validate.ts`
- Test: `src/spoke/validate.test.ts`

**Acceptance Criteria:**
- [ ] Requires `spoke.yaml` (valid against `schemas/spoke.schema.json`), a `kb/` dir passing `validate-kb`, and, if present, `agents/` valid against the agent schema.
- [ ] Fails if the spoke contains `server/`, retrieval adapter code, or an `index.lock` — "a spoke ships no retrieval code, no server, no index" (architecture §13).
- [ ] Reports the number of "core edits" a fixture spoke would require to attach (should be 0) — surfaced for the adversarial review in architecture §19 phase 2.5.

**Verify:** `npx vitest run src/spoke/validate.test.ts` → pass on a good fixture spoke, fail on one containing `server/`.

**Steps:**
- [ ] Failing tests: good spoke → ok; spoke with `server/index.ts` → error mentioning "no server".
- [ ] Implement.
- [ ] Green, commit `feat(cli): validate-spoke contract check`.

---

### Task 17: `doctor` + `check-agnostic`

**Goal:** `doctor` reports what's still missing in an instance; `check-agnostic` guards the framework against team-specific tokens.

**Files:**
- Create: `src/commands/doctor.ts`, `src/commands/check-agnostic.ts`
- Create: `src/doctor/checks.ts`, `agnostic-denylist.txt`
- Test: `src/doctor/checks.test.ts`, `src/commands/check-agnostic.test.ts`

**Acceptance Criteria:**
- [ ] `doctor [--root .]` runs the interview-spec §12 checklist: repo structure valid, seed docs pass front matter, index built (chunk count), manifest assembled (domain count), MCP token minted?, connector registered?, golden eval answers filled in? — printing `✓`/`✗` lines and an "N items remaining. See SETUP.md." footer. Exit 0 always (it's a report, not a gate) unless `--strict`.
- [ ] `doctor --self` runs a reduced check on the framework repo itself (schemas parse, questions.yaml valid, templates render dry) — used by CI.
- [ ] `check-agnostic` greps `src/**`, `schemas/**`, and `src/interview/questions.yaml` for any line matching a denylist entry (case-insensitive, word-boundary); exits non-zero with file:line for each hit.
- [ ] `agnostic-denylist.txt` seeded from the companion docs' proper nouns: `arcwright`, `nightcap`, `upside`, `acme`, `globex`, `monster rpg`, `vesper`, plus a comment explaining how to extend it. `generic-partner-facing` and `nickejanssen/team-ai` are explicitly allowlisted.
- [ ] `check-agnostic` passes on the current tree at every subsequent task.

**Verify:** `npm run build && node dist/cli.js check-agnostic` → exit 0; adding `// acme` to a `src` file → exit 1 pointing at it.

**Steps:**
- [ ] **Step 1: failing `check-agnostic.test.ts`** — temp file with `acme` under a scanned dir → run returns 1; clean tree → 0.
- [ ] **Step 2: implement `check-agnostic.ts`** (pure scanner + command) and `agnostic-denylist.txt`.
- [ ] **Step 3: failing `checks.test.ts`** for `doctor` against a fixture instance dir.
- [ ] **Step 4: implement `doctor`.**
- [ ] **Step 5: update `.github/workflows/ci.yml`** — replace the placeholder `run: npm run test` lines in the `validate` job with `run: node dist/cli.js check-agnostic` and `run: node dist/cli.js doctor --self`.
- [ ] **Step 6: green, commit** `feat(cli): doctor report and check-agnostic guard`.

---

## Milestone E — Catalogs

### Task 18: Catalog model and 3-level resolution

**Goal:** Load catalog entries with the architecture §15 resolution order: toolkit defaults → org catalog repo (if configured) → instance `catalog/`.

**Files:**
- Create: `src/catalog/types.ts`, `src/catalog/resolve.ts`
- Create: `catalog/README.md`
- Test: `src/catalog/resolve.test.ts`

**Acceptance Criteria:**
- [ ] `resolveCatalog({ toolkitDir, orgDir?, instanceDir? })` returns `{ namespaces, roles, skills, personas }` where a later layer overrides an earlier one by filename key.
- [ ] Missing `orgDir`/`instanceDir` is fine (skipped).
- [ ] A custom entry present only in `instanceDir` is returned with `origin: "instance"`; a toolkit entry it overrides is replaced, not merged.
- [ ] `resolveCatalog` never throws on an unknown custom entry — Task 20 handles stub generation.

**Verify:** `npx vitest run src/catalog/resolve.test.ts` → pass with a 3-layer fixture where the instance overrides one role.

**Steps:**
- [ ] Failing test with fixture dirs `fixtures/toolkit`, `fixtures/org`, `fixtures/instance`.
- [ ] Implement layered `readdir` + `Map` merge.
- [ ] Green, commit `feat(catalog): three-layer catalog resolution`.

---

### Task 19: Ship the preset catalog files

**Goal:** The four namespace presets, five roles, core + preset skills, and three personas — all team-agnostic — plus custom-entry TODO stubs.

**Files:**
- Create: `catalog/namespaces/{engineering,support,generic,generic-partner-facing}.yaml`
- Create: `catalog/roles/{architect,sales-engineer,build-engineer,support-engineer,pm}.yaml`
- Create: `catalog/skills/{kb-answer,kb-contribute,audit-summary,sme-route}.yaml` + preset-scoped extras (`integration-review`, `discovery-prep`, `task-runner`, `partner-escalation`, `triage`)
- Create: `catalog/personas/{internal-technical,partner-facing,executive-brief}.md`
- Create: `src/catalog/stub.ts` (generate TODO stub for a custom name)
- Test: `src/catalog/stub.test.ts`, `src/catalog/presets.test.ts`

**Acceptance Criteria:**
- [ ] Every namespace preset uses the architecture §8.2 second-level shape: `operating/ platform/ patterns/ playbooks/ decisions/` + a preset-specific domain dir (`generic-partner-facing` → `partners/<name>/`; `engineering` → `services/<name>/`; `support` → `queues/<name>/`; `generic` → none).
- [ ] Each preset lists exactly **5 seed docs** with titles + one-line purposes (content generated at `init` time from templates, not shipped here). E.g. `generic-partner-facing`: `operating/charter`, `operating/roles`, `platform/api-overview`, `playbooks/partner-onboarding`, `decisions/adr-0001-why-team-ai`.
- [ ] Role files are archetypes: `name`, `summary`, `default_namespaces`, `default_skills`, `model_tier`, `persona_default` — no team names.
- [ ] `generateStub("custom-role", "role")` returns YAML with every field present and a `# TODO:` on each value — "never a guess" (design §4).
- [ ] `check-agnostic` passes over `catalog/` too (add `catalog/**` to its scan).
- [ ] `presets.test.ts` asserts all four namespace files validate against a new `schemas/namespace-preset.schema.json` and all roles validate against `schemas/role.schema.json`.

**Verify:** `npx vitest run src/catalog/` → pass; `node dist/cli.js check-agnostic` → exit 0.

**Steps:**
- [ ] **Step 1:** add `schemas/namespace-preset.schema.json` and `schemas/role.schema.json`; extend `SchemaName`.
- [ ] **Step 2: failing `presets.test.ts`** — glob each catalog dir, validate every file.
- [ ] **Step 3:** author the catalog files (agnostic; use `<name>` placeholders).
- [ ] **Step 4: failing `stub.test.ts`** then implement `stub.ts`.
- [ ] **Step 5:** extend `check-agnostic` scan roots to include `catalog/`.
- [ ] **Step 6: green, commit** `feat(catalog): ship agnostic namespace/role/skill/persona presets`.

---

## Milestone F — The interview

### Task 20: Question-bank schema + `questions.yaml` (Acts 0–2 + Gate 1)

**Goal:** The machine-checkable question-bank schema and the first half of the bank, faithful to interview-spec §3–7.

**Files:**
- Create: `schemas/questions.schema.json`
- Create: `src/interview/questions.yaml` (Acts 0, 1, 2; Gate 1 metadata)
- Create: `src/interview/bank.ts` (typed loader + schema check)
- Test: `src/interview/bank.test.ts`

**Acceptance Criteria:**
- [ ] `questions.schema.json` encodes interview-spec §3: `id`, `act` (0–5), `type` (`single_select|multi_select|text|confirm|rank`), `prompt`, `why`, `options[]` (`value`, `label`, `tradeoff`, `implies`), `default`, `recommend`, `recommend_why`, `allow_defer`, `ask_if`.
- [ ] Every question has a non-empty `why`; `bank.test.ts` asserts each `why` references a `docs/quality-bar.md` anchor id (`#q1`..`#q17`) — enforced by regex.
- [ ] Acts 0–2 questions present with ids exactly matching interview-spec: `pre.assessment`, `pre.overlap`, `pre.probe_result`, `mode`, `team.name`, `team.mission`, `team.size`, `team.surfaces`, `team.sources`, `team.consumers`, plus the flagged **`ctx.org_path`** (design §7), `kb.substrate`, `kb.namespaces`, `kb.catalog_override`, `kb.sources_strategy`, `kb.sensitivity`, `kb.write_back`, and the graph follow-up `kb.graph_questions`.
- [ ] `ask_if` expressions use a documented mini-syntax (`==`, `!=`, `in`, `&&`, `||`, `has(x)`), validated by the schema as a string.
- [ ] `loadBank()` throws with all schema errors if the bank is invalid.

**Verify:** `npx vitest run src/interview/bank.test.ts` → pass.

**Steps:**
- [ ] **Step 1: `questions.schema.json`** + extend `SchemaName`.
- [ ] **Step 2: failing `bank.test.ts`** — `loadBank()` returns ≥ 18 questions for acts ≤ 2; every `why` matches `/quality-bar\.md#q\d+/`.
- [ ] **Step 3: author `questions.yaml` Acts 0–2.** Example entry (`kb.substrate`, from interview-spec §3, with the `why` re-anchored):

```yaml
- id: kb.substrate
  act: 2
  type: single_select
  prompt: Where should the knowledge itself live?
  why: >
    The storage decision. Markdown in git keeps every index disposable and
    every hard retrieval choice reversible. See docs/quality-bar.md#q1.
  options:
    - value: md-git
      label: Markdown in git, index derived from it
      tradeoff: Diffable, reviewable, human-editable. Any index rebuilds or swaps with no migration.
      implies: { arch.index_driver: lexical, kb.write_back: pr-only }
    - value: db-native
      label: A database as the source of truth
      tradeoff: Only for structured records. Loses git history, review, human editing; index changes become migrations.
      implies: { warn: true }
  default: md-git
  recommend: md-git
  recommend_why: >
    Keep documents as the source of truth and treat every index as disposable.
  allow_defer: true
  ask_if: always
```

- [ ] **Step 4: green, commit** `feat(interview): question-bank schema and Acts 0-2`.

---

### Task 21: `questions.yaml` (Acts 3–5 + Gates 2–3)

**Goal:** The rest of the bank — architecture/cost, agents/skills, and dry-run — matching interview-spec §8–12.

**Files:**
- Modify: `src/interview/questions.yaml`
- Test: `src/interview/bank.test.ts` (extend)

**Acceptance Criteria:**
- [ ] Act 3 ids: `arch.index_driver`, `arch.hosting`, `arch.language`, `arch.ci`, `arch.topology`, `arch.model_tiers`, `arch.cache` — with `arch.hosting` default `no-server` and the two gate-condition notes in `why`/`tradeoff` (interview-spec §8).
- [ ] Act 4 ids: `agents.roles`, `agents.domains`, `agents.personas`, `agents.skills`, `agents.strictness`, `agents.seed` — `agents.roles` carries `ask_if: team.size != "1-3"` (interview-spec §5 branching).
- [ ] `agents.strictness` default `refuse-log-gap`; non-refuse options carry `implies: { warn: true }`.
- [ ] Total bank ≈ 25 askable questions (interview-spec §2); `bank.test.ts` asserts 24–28.
- [ ] Every option that sets `implies` references only real later question ids (test cross-checks).

**Verify:** `npx vitest run src/interview/bank.test.ts` → pass.

**Steps:**
- [ ] Extend the test: assert Act 3/4 id sets; assert every `implies` key is a known question id or `warn`.
- [ ] Author the Act 3–5 entries.
- [ ] Green, commit `feat(interview): Acts 3-5 and gate metadata`.

---

### Task 22: Interview engine (pure state machine)

**Goal:** A deterministic engine that, given the bank + answers so far, yields the next question, applies `implies`, evaluates `ask_if`, and handles the controls.

**Files:**
- Create: `src/interview/ask-if.ts` (expression evaluator), `src/interview/engine.ts`
- Test: `src/interview/ask-if.test.ts`, `src/interview/engine.test.ts`

**Acceptance Criteria:**
- [ ] `evalAskIf(expr, answers)` supports `always`, `==`, `!=`, `in`, `has(x)`, `&&`, `||`, parentheses; unknown identifiers resolve to `undefined` (never throw).
- [ ] `Engine` API: `next()`, `answer(id, value)`, `back()`, `skip()` (records a `defer`), `why(id)`, `save()` → serializable state, `load(state)`.
- [ ] `answer()` applies the chosen option's `implies` to a `derived` map; a later explicit `answer()` for the same id overrides the derived value and marks it `overridden`.
- [ ] `skip()` on an `allow_defer: false` question is rejected with a clear error.
- [ ] `defer` and `recommend` are accepted as answer values on any question that allows them; `recommend` records `{ value: <recommend>, via: "recommend", why: <recommend_why> }`.
- [ ] `back()` past the first question is a no-op; `back()` unwinds one answered question and re-offers it.
- [ ] The engine never emits a question whose `ask_if` is false given current answers; changing an earlier answer re-computes downstream visibility.
- [ ] Gates are emitted as pseudo-steps (`kind: "gate"`, `gate: 1|2|3`) after their act; `next()` past a gate requires `confirmGate(n)`.
- [ ] **Nothing is written to disk by the engine** — it is pure.

**Verify:** `npx vitest run src/interview/ask-if.test.ts src/interview/engine.test.ts` → pass; a scripted full run (answer every question with defaults) reaches Gate 3.

**Steps:**
- [ ] **Step 1: failing `ask-if.test.ts`** — table of `[expr, answers, expected]` including `team.size != "1-3"`, `has(team.surfaces, "chat apps")`, `a == 1 && (b in [2,3])`.
- [ ] **Step 2: implement `ask-if.ts`** — a tiny recursive-descent parser or a safe tokenizer + shunting-yard; **no `eval`**.
- [ ] **Step 3: failing `engine.test.ts`** — scenarios:
  - answering `team.size = "1-3"` hides `agents.roles`
  - choosing `kb.substrate = md-git` derives `arch.index_driver = lexical`, then explicitly answering `arch.index_driver = vector-embedded` marks it overridden
  - `skip()` on `team.name` (defer disallowed) throws
  - `back()` from Act 2 returns to the last Act 1 question
  - a full default run yields `state.phase === "gate:3"`
- [ ] **Step 4: implement `engine.ts`.**
- [ ] **Step 5: green, commit** `feat(interview): pure branching state machine`.

---

### Task 23: Preflight scan + connector probe

**Goal:** Detect existing AI infrastructure and produce the interview-spec §4 assessment; detect connectors and *prepare/record* the probe (never call a model).

**Files:**
- Create: `src/interview/preflight.ts`, `src/interview/preflight-report.ts`
- Test: `src/interview/preflight.test.ts`

**Acceptance Criteria:**
- [ ] `scanPreflight(dir)` reports: MCP servers (`.mcp.json`, `.cursor/mcp.json`, `.vscode/mcp.json`), agent config (`CLAUDE.md`, `AGENTS.md`, `.claude/`, `.github/copilot-instructions.md`), vector-store env hints (`PINECONE_*`, `WEAVIATE_*`, `QDRANT_*`, `PGVECTOR`, `LANCEDB*`), org search hints (a configurable list), existing skills/plugins dirs.
- [ ] `scanPreflight(dir)` also returns `existingAssets`: `{ agentConfigFile?: string, routerAgent?: string, agents: string[], kbDocCount: number, skills: string[] }` — the hand-authored assets the generator must preserve (design §18). `routerAgent` is any `agents/*.yaml` / `.claude/agents/*` whose `kind` is `router` or whose name matches `/sme|router/i`.
- [ ] Produces one of `extend | coexist | stand-down` with the rationale text from interview-spec §4 (extend when compatible agent config present; stand-down when an org-search hint + "sources overlap" heuristic both fire).
- [ ] When the assessment is `extend` and `existingAssets.agentConfigFile` is set, the report states "adopt `<file>`, do not create a parallel config" (architecture §4).
- [ ] `prepareConnectorProbe(dir)` — if a GitHub/Drive connector is detected, returns the 5 sample questions + the exact manual steps for the operator to run them, and a slot to record the result. It performs **no retrieval and no model call**. A top-of-function comment states this and cites design §3.
- [ ] `renderPreflight(report)` returns the `docs/preflight.md` body (interview-spec §4 format).

**Verify:** `npx vitest run src/interview/preflight.test.ts` → pass; a fixture dir with `AGENTS.md` + `.mcp.json` → `extend`.

**Steps:**
- [ ] **Step 1: failing tests** — fixture dirs: `pf-extend` (has `AGENTS.md`), `pf-bare` (nothing → `coexist` as the safe default when nothing conclusive), `pf-standdown` (has an org-search marker file + overlapping sources note).
- [ ] **Step 2: implement.** Keep the org-search hint list in `src/interview/preflight-signals.ts` so it's editable.
- [ ] **Step 3: green, commit** `feat(interview): preflight scan and non-model connector probe`.

---

### Task 24: Gate renderers

**Goal:** Render Gates 1–3 as one-screen readable summaries from engine state.

**Files:**
- Create: `src/interview/gates.ts`, `src/interview/gates/{strategy,architecture,agent-plan}.hbs`
- Test: `src/interview/gates.test.ts`

**Acceptance Criteria:**
- [ ] `renderGate(1|2|3, state)` returns a string matching the layouts in interview-spec §7, §9, §11 (Strategy summary; Architecture + cost preview + gate conditions; Agent plan table).
- [ ] Gate 1 lists the **deferred** section: every answer taken via `defer` or `recommend`, with the applied default and its revisit checkpoint.
- [ ] Gate 2's cost preview is the illustrative per-100-questions mix from interview-spec §9 (marked "estimated, replaced by telemetry at phase 4").
- [ ] Gate 3 renders the router, domain subagents, role subagents, personas, skills, scripts, and eval stub counts — tiers and `hops` included.
- [ ] Each rendered gate is ≤ 45 lines (interview-spec §16 "one screen"). `gates.test.ts` asserts the line count.

**Verify:** `npx vitest run src/interview/gates.test.ts` → pass with a fixture state.

**Steps:**
- [ ] Failing test: render all three from a canned `EngineState` fixture; snapshot + line-count assertions.
- [ ] Author `.hbs` templates + `gates.ts` (registers Handlebars helpers `pad`, `tier`, `list`).
- [ ] Green, commit `feat(interview): three gate summary renderers`.

---

### Task 25: Interview outputs writer

**Goal:** After Gate 3 confirmation, write every interview-spec §13 output — and nothing before.

**Files:**
- Create: `src/interview/outputs.ts`
- Test: `src/interview/outputs.test.ts`

**Acceptance Criteria:**
- [ ] `writeOutputs(state, destDir)` writes: `team-profile.yaml` (every answer, timestamped, `deferred: []`), `docs/preflight.md`, `docs/strategy.md`, `docs/architecture.md`, `docs/agent-plan.md`, `docs/decisions/adr-0001-scaffold-choices.md`, `index.lock`.
- [ ] `team-profile.yaml` validates against `schemas/team-profile.schema.json`.
- [ ] `writeOutputs` refuses to run unless `state.phase === "done"` (Gate 3 confirmed) — throws otherwise. This is the "nothing written to disk until the last gate passes" guarantee (interview-spec §1).
- [ ] `index.lock` reflects `arch.index_driver` (or `lexical` if deferred) + the standard chunk config.
- [ ] ADR-0001 body lists each non-default choice with its tradeoff (interview-spec §13).
- [ ] Idempotent: re-running over an existing dir rewrites these files only, touches nothing else.

**Verify:** `npx vitest run src/interview/outputs.test.ts` → pass; pre-Gate-3 state → throws.

**Steps:**
- [ ] Failing tests: happy path writes 7 targets and validates the profile; `phase: "gate:2"` → throws `/gate 3/`.
- [ ] Implement using `serializeFrontmatter`/`yaml` + small Handlebars docs templates (`src/interview/doc-templates/*.hbs`).
- [ ] Green, commit `feat(interview): gated outputs writer`.

---

### Task 26: CLI interview runtime

**Goal:** Drive the engine in a terminal with `@inquirer/prompts`, honoring `back`/`skip`/`why`/`save`.

**Files:**
- Create: `src/interview/cli-runtime.ts`
- Modify: `src/cli.ts` (add nothing yet — `init` wires this in Task 32)
- Test: `src/interview/cli-runtime.test.ts` (inject a scripted answer stream)

**Acceptance Criteria:**
- [ ] `runInterviewCli({ input, output, cwd })` accepts an injectable async answer source so tests script a full run without a TTY.
- [ ] Renders `why` on demand (a `?` choice) without advancing; `back`/`skip`/`save` are always-available meta-choices.
- [ ] On `save`, writes `.team-ai-interview-state.json` to `cwd` and exits 0 with a resume hint.
- [ ] At each gate, prints `renderGate(n, state)` and requires an explicit confirm.
- [ ] Multi-select and rank question types render correctly.
- [ ] Never writes outputs itself — returns the final `EngineState` for `init` to pass to `writeOutputs`.

**Verify:** `npx vitest run src/interview/cli-runtime.test.ts` → a scripted default run returns a `done` state.

**Steps:**
- [ ] Failing test with a scripted answer array covering a `why`, a `back`, a `defer`, and three gate confirms.
- [ ] Implement with a thin adapter around `@inquirer/prompts` (select/checkbox/input) that checks for meta-commands first.
- [ ] Green, commit `feat(interview): terminal runtime with back/skip/why/save`.

---

## Milestone G — Generator and templates

### Task 27: Non-destructive idempotent template renderer

**Goal:** Render a Handlebars template tree into a target dir, classifying every target, never overwriting hand-authored files, never deleting, with a real `--dry-run`.

**Files:**
- Create: `src/generator/render.ts`, `src/generator/context.ts`, `src/generator/generated-manifest.ts`
- Test: `src/generator/render.test.ts`, `src/generator/generated-manifest.test.ts`

**Acceptance Criteria:**
- [ ] `renderTree({ templateDir, destDir, context, dryRun, priorManifest, onCollision })` walks `templateDir`, strips one `.hbs` suffix, renders with `context`.
- [ ] Each target is classified:
  - **`created`** — target absent → write.
  - **`unchanged`** — target present and byte-identical to the new render → no write.
  - **`updated`** — target present, differs, AND `priorManifest` has an entry for it whose recorded `sha256` equals the current on-disk hash (a prior team-ai render, not hand-edited) → write.
  - **`collision`** — target present, differs, and is NOT a matching prior render → **never written**. Handled per `onCollision`: `report` (default — collect and return), `siblings` (write `<path>.team-ai-new`), `skip`.
- [ ] Returns `{ created, unchanged, updated, collisions, siblingsWritten }` (all `string[]`).
- [ ] **`renderTree` never deletes a file** and never writes outside `destDir`.
- [ ] `dryRun: true` performs no writes and returns the report it would have applied (collisions included).
- [ ] `writeGeneratedManifest(destDir, entries)` records `{ path, sha256 }` for every file actually written, merged into `team-profile.yaml` `generated_paths:`; `readGeneratedManifest(destDir)` loads it (empty when absent).
- [ ] Binary/`.keep` files are copied verbatim, still subject to the same classification.
- [ ] `buildContext(state)` maps `EngineState` → the flat template context (team name, slug, mission, namespaces, org path, driver, hosting, roles, domains, personas, skills, seed flag, reviewByDate).
- [ ] Handlebars runs with `noEscape: true` and a fixed helper set (`kebab`, `snake`, `json`, `yamlList`).
- [ ] Missing context keys render as empty and are collected into a `warnings` array, never `undefined`.

**Verify:** `npx vitest run src/generator/render.test.ts src/generator/generated-manifest.test.ts` → pass.

**Steps:**
- [ ] **Step 1: failing tests**
  - fixture template dir → first render: all `created`; a generated manifest is written.
  - identical second render (with `priorManifest`) → all `unchanged`.
  - edit a template, re-render with matching `priorManifest` → that file `updated`.
  - hand-edit an output file, then re-render → that file is a `collision`, not written; original content intact.
  - `onCollision: "siblings"` → `<path>.team-ai-new` written, original untouched, `siblingsWritten` lists it.
  - `dryRun: true` on a tree with a collision → zero writes, report still lists the collision.
  - assert no code path calls `rm`/`unlink`.
- [ ] **Step 2: implement** `render.ts` + `generated-manifest.ts` (sha256 via `node:crypto`).
- [ ] **Step 3: green, commit** `feat(generator): non-destructive classifying tree renderer`.

---

### Task 28: `templates/instance/` tree

**Goal:** The full instance repo as templates, so `init` produces a repo that validates and has green CI.

**Files:**
- Create: `templates/instance/**` — see list below
- Test: `src/generator/instance-template.test.ts`

**Acceptance Criteria:**
- [ ] Tree includes: `README.md.hbs`, `SETUP.md.hbs`, `manifest.yaml.hbs`, `agents/manifest.fragment.yaml.hbs`, `index.lock.hbs`, `docs/{preflight,strategy,architecture,agent-plan}.md` (written by `writeOutputs`, so template ships only `docs/decisions/.keep`), `kb/<preset seed docs>.md.hbs`, `agents/sme.yaml.hbs`+`sme.md.hbs`, `agents/roles/.keep`, `personas/.keep`, `skills/.keep`, `catalog/.keep`, `evals/golden/.keep`, `evals/gates.yaml.hbs`, `.mcp.json.hbs`, `.gitignore.hbs`, `.github/workflows/{validate,evals,reindex,freshness}.yml.hbs`.
- [ ] Generated workflows call the framework's **reusable** workflows (`nickejanssen/team-ai/.github/workflows/validate-kb.reusable.yml@v0`) — Task 39.
- [ ] `.gitignore` ignores `.team-ai/`, `emitted/`, `*.sqlite`.
- [ ] Seed docs carry valid front matter (owner = a role from the chosen preset, `review_by` = init date + 180 days, `status: active`).
- [ ] The test renders the tree with a fixture context into a temp dir and runs `validate-kb --schema-only` + `assemble-manifest --check` + a dry `render` of workflows — all pass.

**Verify:** `npx vitest run src/generator/instance-template.test.ts` → pass.

**Steps:**
- [ ] **Step 1: failing test** — render into `.tmp-test/instance`, then `await validateKb.run({ root: ".tmp-test/instance/kb", schemaOnly: true })` returns 0.
- [ ] **Step 2: author templates.** Seed doc example `templates/instance/kb/operating/charter.md.hbs`:

```hbs
---
id: {{snake team.slug}}.operating.charter
namespace: operating
title: {{team.name}} charter
owner: {{roles.0.name}}
status: active
review_by: {{reviewByDate}}
sensitivity: internal
source: authored
tags: [charter, operating]
supersedes: []
---

# {{team.name}} charter

> Seed document generated by team-ai. Replace this with your real charter.

## Mission

{{team.mission}}

## How we work

_TODO: describe ceremonies, decision rights, and on-call._
```

- [ ] **Step 3:** author `agents/sme.yaml.hbs` + `sme.md.hbs` from architecture §12.2 (router: `model_tier: none`, tools `kb_manifest, kb_search, kb_coverage_gap`, `max_hops` n/a, refuse-and-log behavior in the `.md`).
- [ ] **Step 4: green, commit** `feat(templates): instance repo template tree`.

---

### Task 29: Agent, skill, and persona templates

**Goal:** Neutral YAML+markdown templates for domain subagents, role subagents, the four core skills, and three personas.

**Files:**
- Create: `templates/instance/agents/_domain-sme.yaml.hbs` + `.md.hbs`
- Create: `templates/instance/agents/roles/_role.yaml.hbs` + `.md.hbs`
- Create: `templates/instance/skills/{kb-answer,kb-contribute,audit-summary,sme-route}/SKILL.md.hbs`
- Create: `templates/instance/personas/{internal-technical,partner-facing,executive-brief}.md.hbs`
- Test: `src/generator/agent-templates.test.ts`

**Acceptance Criteria:**
- [ ] Rendered agent YAML validates against `schemas/agent.schema.json` — `model_tier` and `max_hops` present; subagents get `max_hops: 0` (architecture §12.3).
- [ ] Domain subagent template is namespace-scoped from `agents.domains`; role subagent template is cross-namespace from `agents.roles`, skill-scoped.
- [ ] Skill `SKILL.md` templates describe **fixed tool sequences** (architecture §12.1) and declare their tier in front matter; `kb-answer` = "search → answer strictly from hits → cite → log a gap on failure" (architecture §11).
- [ ] Personas grant no tools/namespaces — front matter has `kind: persona`, `grants: none` (architecture §12.1).
- [ ] The generator writes one file per entry in `agents.domains`/`agents.roles`/`agents.personas`, named by slug.
- [ ] A custom domain/role with no catalog match renders the **TODO stub** variant (Task 20 `generateStub`).

**Verify:** `npx vitest run src/generator/agent-templates.test.ts` → pass; rendered YAML validates.

**Steps:**
- [ ] Failing test: render for `domains: ["billing-api"]`, `roles: ["architect"]` → `agents/billing-api-sme.yaml` + `agents/roles/architect.yaml`, both schema-valid, `max_hops: 0`.
- [ ] Author templates.
- [ ] Green, commit `feat(templates): neutral agent, skill, and persona templates`.

---

### Task 30: `templates/spoke/` and `templates/attach/`

**Goal:** Thin templates for the two secondary repo modes.

**Files:**
- Create: `templates/spoke/**` (`spoke.yaml.hbs`, `kb/.keep`, `agents/_spoke-sme.yaml.hbs`+`.md.hbs`, `skills/.keep`, `.github/workflows/validate.yml.hbs`)
- Create: `templates/attach/.team-ai.yaml.hbs`
- Test: `src/generator/spoke-attach-template.test.ts`

**Acceptance Criteria:**
- [ ] Rendered `spoke.yaml` validates against `schemas/spoke.schema.json` and passes `validate-spoke`.
- [ ] Rendered `.team-ai.yaml` matches architecture §13 attach shape (`mode: attach`, `instance`, `agents`, `skills`, `kb_namespaces`) and nothing else.
- [ ] Spoke workflow calls the reusable `validate-spoke` workflow.
- [ ] Spoke template contains no `server/`, no adapter, no `index.lock` (so `validate-spoke` stays green).

**Verify:** `npx vitest run src/generator/spoke-attach-template.test.ts` → pass.

**Steps:**
- [ ] Failing test rendering both with fixture contexts → schema-valid + `validate-spoke` returns 0.
- [ ] Author templates.
- [ ] Green, commit `feat(templates): thin spoke and attach templates`.

---

### Task 31: `templates/mcp-server/` (local stdio)

**Goal:** A generated, off-by-default local stdio MCP server that wraps the shared commands — no hosting, no auth, no Docker.

**Files:**
- Create: `templates/mcp-server/**` (`package.json.hbs`, `server.mjs.hbs`, `README.md.hbs`, `.gitignore`)
- Test: `src/generator/mcp-server-template.test.ts`

**Acceptance Criteria:**
- [ ] Generated only when `arch.hosting == "local-stdio"` (design §11, interview-spec §8); otherwise the generator writes `docs/architecture.md` gate-condition notes and skips the dir.
- [ ] `server.mjs` uses `@modelcontextprotocol/sdk` stdio transport and exposes tools `kb_search`, `kb_get`, `kb_manifest`, `kb_coverage_gap`, `kb_freshness` — each a thin shell-out to `team-ai <command> --json` (the "identical signatures" point, architecture §6.2).
- [ ] Generated `package.json` declares its own deps; `README.md` says how to register it in a client and that it is optional and local-only.
- [ ] Nothing in the framework imports this template at runtime.
- [ ] Rendered `server.mjs` passes `node --check`.

**Verify:** `npx vitest run src/generator/mcp-server-template.test.ts` → pass, incl. `node --check` on the rendered file.

**Steps:**
- [ ] Failing test: render with `hosting: "local-stdio"` → dir exists, `node --check` passes; render with `hosting: "no-server"` → dir absent, architecture doc has the gate note.
- [ ] Author templates.
- [ ] Green, commit `feat(templates): optional local stdio MCP server template`.

---

### Task 32: `init` command

**Goal:** Wire preflight → interview → gates → outputs → generate into a working instance, with `--dry-run` and non-destructive conflict reconciliation.

**Files:**
- Create: `src/generator/init.ts`, `src/generator/reconcile.ts`
- Modify: `src/cli.ts`
- Test: `src/generator/init.test.ts`, `src/generator/reconcile.test.ts`

**Acceptance Criteria:**
- [ ] `team-ai init [--dir .] [--dry-run] [--resume] [--on-conflict <adopt-existing|siblings|subdir|abort>]` runs: `scanPreflight` → print report → `runInterviewCli` → on `done`, `writeOutputs` → **reconcile** → `renderTree(templates/instance)` (+ conditional `mcp-server`) → `reindex` → `assemble-manifest` → `doctor`.
- [ ] **Reconciliation (design §18), before any template write:** compute a `dryRun` render plan against `readGeneratedManifest(dir)`. If `collisions.length > 0`, or the assessment is `extend` with `existingAssets.routerAgent`/`agentConfigFile` present, `init` **halts and prompts** (unless `--on-conflict` is set) with exactly these choices and writes nothing until one is picked:
  - **`adopt-existing`** — do not write any colliding path or a parallel agent config; render only `created` targets; append a "coexistence boundary" paragraph to `docs/architecture.md` naming each adopted file (architecture §4 "Extend").
  - **`siblings`** — pass `onCollision: "siblings"`; every colliding path is written as `<path>.team-ai-new`; originals untouched; `doctor` afterward lists the `.team-ai-new` files as "review and merge".
  - **`subdir`** — re-run the whole render with `destDir = <dir>/team-ai/`; nothing in `<dir>` root is touched.
  - **`abort`** — exit 0 having written only the interview outputs (`team-profile.yaml`, gate docs); no templates.
- [ ] `init` **never deletes** anything and never overwrites a hand-authored file under any option.
- [ ] STAND DOWN outcome from preflight short-circuits: generate only `manifest.yaml`, `agents/` (absent-only), `personas/`, `skills/`, `docs/` — no `kb/` index, no server (interview-spec §4).
- [ ] `--dry-run` prints the file tree with `created` / `unchanged` / `updated` / `collision` counts and writes nothing (interview-spec §12).
- [ ] `--resume` loads `.team-ai-interview-state.json` and only asks changed/new questions.
- [ ] After a non-dry run, `doctor` prints the remaining-items list and `git` is **not** auto-run (operator does `git init`/push per `SETUP.md`).
- [ ] End-to-end test: scripted default answers into an empty dir → generated dir passes `validate-kb`, `reindex` (chunks > 0), `search` (returns a hit), `assemble-manifest --check`.
- [ ] Reconciliation test: pre-seed the target dir with `agents/sme.yaml` containing `# HAND AUTHORED SENTINEL`; run `init --on-conflict siblings` → `agents/sme.yaml` is byte-identical afterward, `agents/sme.yaml.team-ai-new` exists, `doctor` flags it.

**Verify:** `npx vitest run src/generator/init.test.ts src/generator/reconcile.test.ts` → pass (this is the automated half of the dogfood).

**Steps:**
- [ ] **Step 1: failing e2e test** — scripted answer stream into `.tmp-test/instance-a` (empty), then the four checks as assertions.
- [ ] **Step 2: failing reconciliation test** — the sentinel scenario above, plus an `adopt-existing` scenario asserting `docs/architecture.md` gained the boundary paragraph and no collision path was written.
- [ ] **Step 3: implement `reconcile.ts`** (pure: takes the dry render report + `existingAssets` + chosen strategy → a concrete write plan) and `init.ts` orchestrating existing pieces.
- [ ] **Step 4: register in `cli.ts`** with the `--on-conflict` option.
- [ ] **Step 5: green, commit** `feat(cli): init with non-destructive conflict reconciliation`.

---

### Task 33: `spoke` and `attach` commands

**Goal:** The two short generators.

**Files:**
- Create: `src/generator/spoke.ts`, `src/generator/attach.ts`
- Modify: `src/cli.ts`
- Test: `src/generator/spoke.test.ts`, `src/generator/attach.test.ts`

**Acceptance Criteria:**
- [ ] `team-ai spoke [--dir .]` asks the interview-spec §5 short set (spoke name, namespace, owner, core repo, one domain) and renders `templates/spoke`.
- [ ] `team-ai attach [--dir .]` asks ≤ 5 questions (instance URL, agents, skills, namespaces) and writes only `.team-ai.yaml` (interview-spec §5 "under two minutes").
- [ ] Both refuse to overwrite an existing `spoke.yaml` / `.team-ai.yaml` without `--force`.
- [ ] Generated spoke passes `validate-spoke`; generated attach file validates against the spoke/attach schema.

**Verify:** `npx vitest run src/generator/spoke.test.ts src/generator/attach.test.ts` → pass.

**Steps:**
- [ ] Failing tests with scripted answers → files written, schema-valid, contract-valid.
- [ ] Implement.
- [ ] Green, commit `feat(cli): spoke and attach generators`.

---

### Task 34: `resume`, `review`, `upgrade`

**Goal:** The three re-run commands from architecture §14 / interview-spec §13.

**Files:**
- Create: `src/generator/resume.ts`, `src/generator/review.ts`, `src/generator/upgrade.ts`
- Modify: `src/cli.ts`
- Test: `src/generator/resume.test.ts`, `src/generator/review.test.ts`, `src/generator/upgrade.test.ts`

**Acceptance Criteria:**
- [ ] `resume` reads `team-profile.yaml`, re-runs the engine seeded with saved answers, asks only questions whose `ask_if` now differs or that are unanswered, re-writes outputs + re-renders.
- [ ] `review` replays the three gates from `team-profile.yaml` read-only and exits 0 — writes nothing.
- [ ] `upgrade` re-renders plumbing only — `.github/workflows/`, `evals/gates.yaml`, `index.lock` chunk config, `SETUP.md` — and never touches `kb/`, `agents/`, `personas/`, `skills/`, `catalog/`. Prints a diff summary.
- [ ] `upgrade` passes `priorManifest` to `renderTree`; a plumbing file the operator hand-edited is a `collision` — reported as "upgrade skipped `<path>` (locally modified); diff in `<path>.team-ai-new`", never overwritten.
- [ ] `upgrade` bumps a `team_ai_version` field in `team-profile.yaml`.

**Verify:** `npx vitest run src/generator/resume.test.ts src/generator/review.test.ts src/generator/upgrade.test.ts` → pass.

**Steps:**
- [ ] Failing tests: `review` writes nothing (assert mtime unchanged); `upgrade` changes a workflow file but not a kb file; `resume` with an unchanged profile asks zero questions.
- [ ] Implement.
- [ ] Green, commit `feat(cli): resume, review, and upgrade`.

---

## Milestone H — Emitters

### Task 35: Emitters + `emit` command

**Goal:** Render neutral agent/skill/persona definitions into client-specific, gitignored build artifacts.

**Files:**
- Create: `src/emit/index.ts`, `src/emit/claude-code.ts`, `src/emit/mcp-only.ts`, `src/emit/generic.ts`
- Create: `src/commands/emit.ts`
- Modify: `src/cli.ts`
- Test: `src/emit/*.test.ts`

**Acceptance Criteria:**
- [ ] `team-ai emit --target <claude-code|mcp-only|generic> [--dir .] [--out emitted]` reads `agents/`, `skills/`, `personas/`, `manifest.yaml` and writes to `emitted/<target>/`.
- [ ] `claude-code`: `.claude/agents/*.md` with YAML front matter + a plugin manifest (`.claude-plugin/plugin.json`).
- [ ] `mcp-only`: a server-side prompt registry JSON (agent instructions keyed by name) for app clients.
- [ ] `generic`: a portable bundle (`agents.json` + `prompts/*.md`) for another harness.
- [ ] `emitted/` is in the instance `.gitignore` (Task 28) — emit refuses to write outside `--out` and warns if `--out` is tracked by git.
- [ ] Round-trip test: emit `generic`, re-parse, assert every agent name + tier survived.

**Verify:** `npx vitest run src/emit/` → pass.

**Steps:**
- [ ] Failing tests per target against a fixture instance.
- [ ] Implement three emitters + dispatcher.
- [ ] Green, commit `feat(emit): claude-code, mcp-only, and generic emitters`.

---

## Milestone I — Claude skill runtime

### Task 36: `skills/scaffold-interview/SKILL.md`

**Goal:** The in-Claude interview runtime — same `questions.yaml`, rendered as chat.

**Files:**
- Create: `skills/scaffold-interview/SKILL.md`
- Create: `skills/scaffold-interview/reference/question-flow.md`
- Test: `src/interview/skill-doc.test.ts`

**Acceptance Criteria:**
- [ ] `SKILL.md` front matter: `name: scaffold-interview`, a `description` matching the trigger phrasing in interview-spec §14.
- [ ] Body instructs: read `src/interview/questions.yaml` (bundled), drive the engine's logic manually, ask ≤ 3 questions per turn, render the three gates as text with confirm, then write `team-profile.yaml` (if filesystem access) or output it for the operator to hand to an engineer.
- [ ] Explicitly references the same `ask_if`/`implies`/`defer`/`recommend` semantics as `engine.ts` (single source of truth — no divergent copy of the rules).
- [ ] `skill-doc.test.ts` asserts the file exists, front matter parses, and every `act` 0–5 is named in the body.

**Verify:** `npx vitest run src/interview/skill-doc.test.ts` → pass.

**Steps:**
- [ ] Failing test.
- [ ] Write `SKILL.md` + reference.
- [ ] Green, commit `feat(skill): in-Claude scaffold-interview runtime`.

---

## Milestone J — Quality bar, reusable workflows

### Task 37: `docs/quality-bar.md`

**Goal:** The 17 measurement questions, each with the architecture's answer and the repo path that enforces it — the `why` source for the interview and the contributor checklist.

**Files:**
- Create: `docs/quality-bar.md`
- Test: `src/interview/quality-bar.test.ts`

**Acceptance Criteria:**
- [ ] 17 sections with anchors `#q1`..`#q17` matching the prompt's list (KB substrate choice … detect existing AI infra).
- [ ] Each section: **Question**, **Answer the architecture gives**, **Where it's enforced** (a real path — e.g. q3 "attach mode" → `templates/attach/`, `src/generator/attach.ts`; q6 "cost measured" → `src/evals/metrics.ts`, `evals/gates.yaml`; q13 "scripts where a script would do" → `src/commands/`; q15 "model/platform agnostic" → `src/emit/`, `check-agnostic`; q16 "minimum sufficient model" → `model_tier` in `schemas/agent.schema.json`).
- [ ] A note records the "sixteen vs seventeen" discrepancy (design §3).
- [ ] `quality-bar.test.ts` asserts 17 anchors exist and every `questions.yaml` `why` cites one that exists (closes the loop with Task 20).
- [ ] `CONTRIBUTING.md` links each PR-template checkbox to this file.

**Verify:** `npx vitest run src/interview/quality-bar.test.ts` → pass.

**Steps:**
- [ ] Failing test: 17 anchors; bijection with `why` citations.
- [ ] Write the doc, cross-checking every "where enforced" path exists.
- [ ] Green, commit `docs: quality bar with enforcement map`.

---

### Task 38: Reusable CI workflows

**Goal:** The three `workflow_call` workflows other repos invoke (architecture §18.1).

**Files:**
- Create: `.github/workflows/validate-kb.reusable.yml`, `validate-spoke.reusable.yml`, `evals.reusable.yml`
- Test: `src/ci-config.test.ts` (extend)

**Acceptance Criteria:**
- [ ] Each has `on: workflow_call` with documented `inputs` (`node-version` default "22", `root` default ".", `team-ai-version` default "latest").
- [ ] `validate-kb.reusable.yml`: `npx team-ai@${{inputs.team-ai-version}} validate-kb && validate-citations`.
- [ ] `evals.reusable.yml`: `npx team-ai run-evals` with the gate thresholds; uploads the JSON report as an artifact.
- [ ] `validate-spoke.reusable.yml`: `npx team-ai validate-spoke`.
- [ ] The instance/spoke templates (Tasks 28, 30) reference these by `@v0` — add a note in `CONTRIBUTING.md` that a `v0` tag/branch must track `main` until 1.0.
- [ ] `ci-config.test.ts` parses all three and asserts `on.workflow_call` present.

**Verify:** `npx vitest run src/ci-config.test.ts` → pass.

**Steps:**
- [ ] Extend the test.
- [ ] Author the three workflows.
- [ ] Green, commit `ci: reusable validate-kb, validate-spoke, and evals workflows`.

---

## Milestone J2 — Adopting an existing repo (`team-ai adopt`)

All four tasks are deterministic — **no model calls** (design §18.1).

### Task 41: Front-matter inference and backfill transform

**Goal:** Given a doc with no `team-ai` front matter, deterministically propose a schema-valid front-matter block and insert it without merging into an existing header.

**Files:**
- Create: `src/adopt/infer.ts`, `src/adopt/backfill.ts`, `src/adopt/types.ts`, `src/adopt/git-owner.ts`
- Test: `src/adopt/infer.test.ts`, `src/adopt/backfill.test.ts`

**Acceptance Criteria:**
- [ ] `inferFrontmatter({ relPath, body, namespace, gitAuthors, horizonDays, today })` returns a `FrontMatter` object: `id` = `` `${namespace}.${relPath without ext, segments slugified, joined by "."}` ``; `title` = first `^# ` heading, else title-cased basename; `owner` = most frequent entry in `gitAuthors` (ties → first alphabetically; empty → `"unknown"`); `review_by` = `today + horizonDays` as `YYYY-MM-DD`; `sensitivity` = `"internal"`; `status` = `"active"`; `source` = `` `synced:${system}` `` when `body` head (first 8 lines) matches `/do not edit|edit in (\w+) and re-?sync|^> Source:/i` (system = the captured word lowercased, or `"external"`), else `"authored"`; `tags` = values from a `^\*\*Tags:\*\*\s*(.+)$` line split on comma, else `[]`; `supersedes` = `[]`.
- [ ] The returned object passes `validate("frontmatter", …)`.
- [ ] `getGitAuthors(path, root)` shells `git -C <root> log --format=%an -- <path>` and returns `string[]` (empty on error / untracked — never throws).
- [ ] `applyFrontmatter(absPath, fm, { dryRun })`: if the file starts with `---\n` → **conflict**, return `{ ok: false, reason: "existing front matter" }`, no write. Else prepend `serializeFrontmatter(fm, body)`. `dryRun` returns the would-be content without writing.
- [ ] No deletes; only prepends to files that have no front matter.

**Verify:** `npx vitest run src/adopt/infer.test.ts src/adopt/backfill.test.ts` → pass.

**Steps:**
- [ ] **Step 1: failing `infer.test.ts`**

```ts
import { describe, expect, it } from "vitest";
import { inferFrontmatter } from "./infer.js";

const base = { namespace: "architecture", gitAuthors: ["Nico", "Nico", "Sam"], horizonDays: 180, today: new Date("2026-08-30") };

describe("inferFrontmatter", () => {
  it("derives id from path and title from the H1", () => {
    const fm = inferFrontmatter({ ...base, relPath: "architecture/01-overview.md", body: "# System Architecture Overview\n\ntext" });
    expect(fm.id).toBe("architecture.architecture.01-overview");
    expect(fm.title).toBe("System Architecture Overview");
    expect(fm.owner).toBe("Nico");
    expect(fm.review_by).toBe("2027-02-26");
  });
  it("detects a synced source from an 'edit in Notion' header", () => {
    const fm = inferFrontmatter({ ...base, relPath: "a/b.md", body: "> Source: artifact\n> Do not edit this file directly; edit in Notion and re-sync.\n\n# B" });
    expect(fm.source).toBe("synced:notion");
  });
});
```

- [ ] **Step 2: implement** `git-owner.ts`, `infer.ts`, `backfill.ts`.
- [ ] **Step 3: failing `backfill.test.ts`** — a file with no front matter gets the block prepended (dry-run returns it); a file already starting `---` returns a conflict and is untouched.
- [ ] **Step 4: green, commit** `feat(adopt): deterministic front-matter inference and backfill`.

---

### Task 42: Namespace mapping candidate matcher

**Goal:** Map a repo's top-level docs folders to framework namespaces deterministically; surface unmatched folders as human decisions with ranked candidates.

**Files:**
- Create: `src/adopt/namespaces.ts`
- Test: `src/adopt/namespaces.test.ts`

**Acceptance Criteria:**
- [ ] `proposeNamespaceMap(folders: string[], presetShape: string[])` returns `{ matched: { folder: string; namespace: string }[]; unmatched: { folder: string; candidates: string[] }[] }`.
- [ ] Match order: exact; singular/plural (`decisions`↔`decision`); a fixed synonym table (`arch`→`architecture`, `adr`/`adrs`→`decisions`, `runbooks`→`playbooks`, `examples`→`patterns`, `charter`/`team`→`operating`, `guides`→`playbooks`).
- [ ] Unmatched folders get the 3 closest `presetShape` names by Levenshtein distance, plus `"custom"` always last.
- [ ] Pure function, deterministic ordering (`matched` sorted by `folder`).

**Verify:** `npx vitest run src/adopt/namespaces.test.ts` → pass, including an Arcwright-shaped input.

**Steps:**
- [ ] **Step 1: failing test**

```ts
import { describe, expect, it } from "vitest";
import { proposeNamespaceMap } from "./namespaces.js";

const shape = ["operating", "platform", "patterns", "playbooks", "decisions", "architecture"];

describe("proposeNamespaceMap", () => {
  it("matches known folders and flags the rest", () => {
    const r = proposeNamespaceMap(["architecture", "decisions", "prd", "story-bibles", "conventions"], shape);
    expect(r.matched).toContainEqual({ folder: "architecture", namespace: "architecture" });
    expect(r.matched).toContainEqual({ folder: "decisions", namespace: "decisions" });
    const prd = r.unmatched.find((u) => u.folder === "prd");
    expect(prd?.candidates.at(-1)).toBe("custom");
  });
});
```

- [ ] **Step 2: implement** (small Levenshtein, no dependency).
- [ ] **Step 3: green, commit** `feat(adopt): namespace mapping candidate matcher`.

---

### Task 43: `team-ai adopt` — adoption plan generation

**Goal:** Measure an existing repo against the framework standard and write a reviewable plan. Change nothing else.

**Files:**
- Create: `src/commands/adopt.ts`, `src/adopt/plan.ts`, `src/adopt/gap.ts`, `schemas/adoption-plan.schema.json`, `src/adopt/plan-doc.hbs`
- Modify: `src/cli.ts`, `src/schema/load.ts` (add `adoption-plan` to `SchemaName`)
- Test: `src/adopt/plan.test.ts`, `src/adopt/gap.test.ts`

**Acceptance Criteria:**
- [ ] `team-ai adopt [--root .] [--out .] [--horizon-days 180] [--namespace-map <file>]` runs: `scanPreflight(root)` → `proposeNamespaceMap(topLevelDocFolders, presetShape)` → for every `*.md` under `<root>/docs` (configurable) with no front matter, `inferFrontmatter` (namespace from the matched map, or `"unmapped"` placeholder) → `gapVsQualityBar(root)` → collision list (dry `renderTree(templates/instance)` vs `root`).
- [ ] `gapVsQualityBar(root)` returns, for each of `#q1`..`#q17`, `{ id, satisfied: boolean, evidence: string, closesWith: string }` using a fixed rule table (e.g. q1 satisfied if `kb/` or `docs/` is markdown-in-git; q5 satisfied if `docs/` has an adversarial-review record; q8 satisfied if a `doctor`-equivalent exists; …). The rule table lives in `src/adopt/gap.ts` and is unit-tested.
- [ ] Writes `<out>/docs/adoption-plan.md` (from `plan-doc.hbs`) and `<out>/adoption-plan.yaml` (schema-valid). Every backfill item and relabel has `approved: false`; every unmatched folder is an entry under `namespace_decisions` with its candidates.
- [ ] `adopt` **writes only those two files** — asserted by the test (snapshot the file list before/after).
- [ ] No model call anywhere; a top-of-file comment on `plan.ts` states this.
- [ ] `--namespace-map <file>` (a `folder: namespace` YAML) pre-resolves matches so re-runs are stable.

**Verify:** `npx vitest run src/adopt/plan.test.ts src/adopt/gap.test.ts` → pass against a fixture "legacy repo".

**Steps:**
- [ ] **Step 1: build the fixture** `src/adopt/fixtures/legacy-repo/` — `docs/architecture/a.md` (H1, no front matter), `docs/notes/b.md` (Notion "do not edit" header), `docs/prd/c.md`, plus a `.git`-less dir (mock `getGitAuthors` in tests).
- [ ] **Step 2: failing `gap.test.ts`** — assert 17 entries, each with `satisfied` boolean + non-empty `closesWith`.
- [ ] **Step 3: failing `plan.test.ts`** — run `adopt` on the fixture with `--out .tmp-test/adopt`; assert exactly `adoption-plan.md` + `adoption-plan.yaml` created, the yaml validates, lists 3 backfill items (one with `source: synced:notion`), `namespace_decisions` includes `prd` and `notes`, and the fixture repo itself is byte-for-byte unchanged.
- [ ] **Step 4: implement** `gap.ts`, `plan.ts`, `adopt.ts`, the schema, the hbs doc; register in `cli.ts`.
- [ ] **Step 5: green, commit** `feat(adopt): deterministic adoption plan generation`.

---

### Task 44: `team-ai adopt --interactive` and `--apply`

**Goal:** Collect per-item approvals, then apply only approved items as deterministic transforms. Never touch an unapproved or conflicting file.

**Files:**
- Create: `src/adopt/interactive.ts`, `src/adopt/apply.ts`
- Modify: `src/commands/adopt.ts`, `src/cli.ts`
- Test: `src/adopt/apply.test.ts`, `src/adopt/interactive.test.ts`

**Acceptance Criteria:**
- [ ] `team-ai adopt --interactive [--root .]` loads `adoption-plan.yaml`, and for each backfill/relabel item prompts **approve / skip / edit** (`edit` opens the proposed front-matter block in `$EDITOR` or accepts inline text via the injectable prompt source); for each `namespace_decisions` entry prompts a pick from `candidates`. Writes choices back into `adoption-plan.yaml` (`approved: true|false`, `namespace: <chosen>`). Injectable answer source for headless tests.
- [ ] `team-ai adopt --apply [--root .]` reads `adoption-plan.yaml` and applies **only** items with `approved: true`:
  - backfill → `applyFrontmatter` (skips + reports any that now conflict);
  - relabel → add/replace the `source:` key only, via `serializeFrontmatter`, on files the tool is adding front matter to (never rewrites a hand-authored header — conflict instead);
  - resolved `namespace_decisions` → write/extend `catalog/namespaces/<repo>.yaml`;
  - optional `move:` items → `fs.rename` + append to a `moved:` log in `adoption-plan.yaml`.
- [ ] `--apply` is idempotent: an item whose target already has the front matter is reported `already-applied`, not re-written.
- [ ] After applying, runs `validate-kb --root <root>/docs` (or the mapped roots) and prints the result.
- [ ] Prints a summary: `applied N / skipped M / conflicts K`. Exit non-zero only if a `conflict` occurred on an `approved` item.
- [ ] Never deletes; never writes a file not named in an approved plan item.

**Verify:** `npx vitest run src/adopt/apply.test.ts src/adopt/interactive.test.ts` → pass.

**Steps:**
- [ ] **Step 1: failing `apply.test.ts`** — take the Task 43 fixture plan, mark 2 of 3 backfill items `approved: true`, run `--apply`; assert exactly those 2 docs gained front matter, the 3rd is untouched, `validate-kb` passes on the 2, a second `--apply` reports both `already-applied`.
- [ ] **Step 2: failing `interactive.test.ts`** — scripted answer source approves 1, skips 1, edits 1 (changes `owner`), picks a namespace for `prd`; assert the yaml reflects all four.
- [ ] **Step 3: implement** `interactive.ts`, `apply.ts`; wire `--interactive`/`--apply` into `adopt.ts`.
- [ ] **Step 4: green, commit** `feat(adopt): interactive approval and deterministic apply`.

---

## Milestone K — Dogfood and release

### Task 39: Dogfood against Arcwright, then Partner Solutions

**Goal:** **USER-ORDERED GATE — NON-SKIPPABLE.** This task was requested by the user in the current conversation. It MUST NOT be closed by walking around it, by declaring it "verified inline", or by substituting a cheaper check. Close only after every item in acceptance criteria has been re-validated independently, with output captured.

Run the framework against itself three ways — `team-ai adopt` against the real Arcwright repo, `team-ai init` with Arcwright as the preflight target, and `team-ai init` for a Partner Solutions profile — prove the outputs work, capture friction, and fix it.

**Files:**
- Create: `docs/dogfood-notes.md`
- Modify: whichever framework files the findings require (expected: template polish, `why` text, `doctor` messages, preflight signal list, gap-rule table)

**Acceptance Criteria:**
- [ ] **Run A (Arcwright):** `team-ai init --dir .tmp-dogfood/arcwright` with preflight pointed at `C:\Users\nicke\OneDrive\Desktop\arcwright` (a real repo with `AGENTS.md`, `CLAUDE.md`, `.claude/`, `.mcp.json`). Preflight MUST report `extend` with the rationale naming those files AND list `existingAssets` (the Arcwright `AGENTS.md` as `agentConfigFile`, plus any `.claude/agents/*`). Capture the printed report.
- [ ] Run A answers use the `engineering` preset, team size 4–8, surfaces "coding agent" only. Generated dir MUST: pass `team-ai validate-kb`, `team-ai validate-citations`, `team-ai reindex` (chunks > 0), `team-ai search "<a term from a seed doc>"` (≥ 1 hit, cited), `team-ai assemble-manifest --check`, `team-ai doctor` (prints remaining items, exit 0).
- [ ] **Run A reconciliation check:** before the run, copy Arcwright's real `AGENTS.md` into `.tmp-dogfood/arcwright/AGENTS.md` and seed `.tmp-dogfood/arcwright/agents/sme.yaml` with `# HAND AUTHORED SENTINEL`. Run `init` with `--on-conflict adopt-existing`. Assert: `AGENTS.md` and `agents/sme.yaml` are byte-identical (sha256) before and after; no `agents/sme.yaml` collision was written; `.tmp-dogfood/arcwright/docs/architecture.md` contains a "coexistence boundary" paragraph naming `AGENTS.md` and `agents/sme.yaml`. Then repeat with `--on-conflict siblings` into a clean copy and assert `agents/sme.yaml.team-ai-new` appears while the sentinel file is untouched.
- [ ] Run A generated `.github/workflows/*` are syntactically valid YAML and reference the reusable workflows.
- [ ] **Run A-adopt (real Arcwright, read-only):** `team-ai adopt --root C:\Users\nicke\OneDrive\Desktop\arcwright --out .tmp-dogfood/arcwright-adopt`. MUST: write only `.tmp-dogfood/arcwright-adopt/docs/adoption-plan.md` + `adoption-plan.yaml` (assert the Arcwright repo tree is byte-for-byte unchanged — `git -C <arcwright> status --porcelain` empty); the plan MUST list front-matter backfill items for `docs/**` files lacking front matter, mark the `docs/architecture/*` "edit in Notion" docs as `source: synced:notion`, include `namespace_decisions` for the folders with no preset match (`prd`, `story-bibles`, `product`, `conventions`), and a 17-line gap-vs-quality-bar table. Capture the rendered `adoption-plan.md` into `docs/dogfood-notes.md`.
- [ ] **Run A-adopt apply (fixture, not Arcwright):** on `src/adopt/fixtures/legacy-repo`, mark 2 plan items approved, `team-ai adopt --apply` → exactly those 2 files gain front matter, the rest untouched, `validate-kb` passes on the 2, re-run reports `already-applied`.
- [ ] **Run B (Partner Solutions):** `team-ai init --dir .tmp-dogfood/partner-solutions`, `generic-partner-facing` preset, team size 1–3 (so `agents.roles` is suppressed and only domain agents are offered — architecture §12.3 / interview-spec §5), surfaces "coding agent" + "chat apps" + "read-only stakeholders", external consumers = yes (forces sensitivity tiers on and the reader scope — interview-spec §5), `arch.hosting` left at default `no-server`. Generated `docs/architecture.md` MUST contain both gate-condition notes (local stdio; remote after 2 asks).
- [ ] Run B generated dir passes the same six command checks as Run A.
- [ ] Run B: because team size is 1–3, the agent plan (Gate 3 render, captured) MUST show domain subagents only, no role subagents.
- [ ] Both `.tmp-dogfood/` trees are deleted after verification (they are gitignored; nothing team-specific is committed — design §4).
- [ ] `docs/dogfood-notes.md` records, for each run: what was awkward, ambiguous, or wrong; the fix applied (with commit SHA) or an explicit "won't fix, because…".
- [ ] Every finding marked "fix" has a corresponding commit; `npm run check` passes after all fixes; the framework's own CI jobs (`lint-typecheck-test`, `validate`, `secret-scan`) pass.
- [ ] `check-agnostic` still exits 0 (no team tokens leaked into `src/`, `schemas/`, `catalog/`, `questions.yaml` from the dogfood work).

**Verify:**
```bash
npm run build
node dist/cli.js init --dir .tmp-dogfood/arcwright --preflight-target "C:/Users/nicke/OneDrive/Desktop/arcwright"   # scripted answers via test harness or --answers file
for c in "validate-kb" "validate-citations" "reindex" "assemble-manifest --check"; do node dist/cli.js $c --root .tmp-dogfood/arcwright || echo "FAIL $c"; done
node dist/cli.js search "charter" --root .tmp-dogfood/arcwright --json | node -e "process.stdin.on('data',d=>process.exit(JSON.parse(d).length?0:1))"
node dist/cli.js doctor --root .tmp-dogfood/arcwright
# repeat for .tmp-dogfood/partner-solutions
npm run check
rm -rf .tmp-dogfood
```
Expected: every command exits 0; preflight for Run A prints `Assessment: EXTEND`; `docs/dogfood-notes.md` exists with findings for both runs; `git status` shows no `.tmp-dogfood` and no team tokens in tracked source.

**Steps:**

- [ ] **Step 1: add `--answers <file>` and `--preflight-target <dir>` to `init`** (a small addition to `src/generator/init.ts` + `cli.ts`) so dogfood runs are reproducible and non-interactive. Write a failing test for `--answers` first.
- [ ] **Step 2: create `answers/dogfood-arcwright.yaml` and `answers/dogfood-partner-solutions.yaml`** under `test/fixtures/` (NOT shipped in `files` in package.json) with the answer sets described above.
- [ ] **Step 3: Run A.** Execute, capture the preflight report and Gate renders to `docs/dogfood-notes.md` (Run A section). Run the six checks. Record every rough edge.
- [ ] **Step 4: Run B.** Same, into the partner-solutions dir. Confirm the size-1–3 branch and the sensitivity/gate-note behavior.
- [ ] **Step 5: triage findings.** For each: fix + commit (`fix:` or `docs:`), or record "won't fix" with reason. Re-run the affected run to confirm.
- [ ] **Step 6: re-validate independently.** Fresh `npm run build`, delete `.tmp-dogfood`, re-run both inits from the answer files, re-run all six checks per run, `npm run check`, `node dist/cli.js check-agnostic`. Capture all output into the notes file.
- [ ] **Step 7: delete `.tmp-dogfood/`; commit** `docs: dogfood notes for Arcwright and Partner Solutions runs` (plus any fix commits already made).

```json:metadata
{"userGate": true, "tags": ["user-gate"], "requireEvidenceTokens": [["run-a","arcwright","EXTEND"], ["run-b","partner-solutions","no-server"]], "verifyCommand": "npm run build && bash test/dogfood.sh && npm run check && node dist/cli.js check-agnostic", "acceptanceCriteria": ["Run A preflight reports EXTEND naming AGENTS.md/CLAUDE.md/.claude/.mcp.json and lists existingAssets","Run A generated dir passes validate-kb, validate-citations, reindex (chunks>0), search (cited hit), assemble-manifest --check, doctor","Run A reconciliation: hand-authored AGENTS.md + agents/sme.yaml byte-identical before/after under adopt-existing; siblings mode writes .team-ai-new without touching originals","Run A-adopt: team-ai adopt against real Arcwright writes only adoption-plan.md + adoption-plan.yaml, Arcwright tree unchanged, plan lists front-matter backfill + synced:notion relabels + namespace_decisions + 17-line gap table","Run A-adopt apply on fixture: only the 2 approved files change, validate-kb passes, re-run reports already-applied","Run B uses generic-partner-facing preset, size 1-3 suppresses role subagents, external consumers forces sensitivity tiers","Run B docs/architecture.md has both server gate-condition notes","Both .tmp-dogfood trees deleted; nothing team-specific committed","docs/dogfood-notes.md records findings + fix SHAs; npm run check and framework CI jobs pass after fixes","check-agnostic exits 0"]}
```

---

### Task 40: Release 0.1.0

**Goal:** **USER-ORDERED GATE — NON-SKIPPABLE.** This task was requested by the user in the current conversation. It MUST NOT be closed by walking around it, by declaring it "verified inline", or by substituting a cheaper check. Close only after every item in acceptance criteria has been re-validated independently, with output captured.

Verify the Definition of Done line by line, finalize the changelog, tag `v0.1.0`, and create the `v0` branch the reusable workflows pin to.

**Files:**
- Modify: `CHANGELOG.md`, `README.md` (root — adapt from `docs/README.source.md`)
- Create: `docs/definition-of-done.md` (the checklist with evidence)

**Acceptance Criteria:**
- [ ] Root `README.md` exists, adapted from `docs/README.source.md`, with the real install command (`npx team-ai init`) and a link to `docs/architecture.md`, `docs/interview-spec.md`, `docs/quality-bar.md`.
- [ ] `docs/definition-of-done.md` walks each clause of the build prompt's "Definition of done" and the Dogfood section with a ✓ and the evidence (command + output snippet or file path):
  - fork → `npm install` → `team-ai init` → answer interview → validated instance
  - generated instance CI green (from Task 39 capture)
  - `search` returns cited results from seed content
  - `doctor` accurately reports what's missing
  - quality-bar has an honest answer for every line (Task 37)
- [ ] Every one of the build prompt's numbered build items (1–11) maps to shipped paths in `docs/definition-of-done.md`.
- [ ] `npm run check` passes; `npm run build` produces `dist/`; `npx pkg-ok`-style check: `bin/team-ai.js` resolves and `team-ai --help` lists all 9 top-level commands (`init adopt spoke attach doctor resume review upgrade emit`) + the validation/eval commands.
- [ ] `CHANGELOG.md` `[0.1.0]` section dated, `[Unreleased]` emptied.
- [ ] Git tag `v0.1.0` created; `v0` branch created at the same commit (reusable-workflow pin target).
- [ ] `check-agnostic` exits 0 on the final tree.

**Verify:**
```bash
npm ci && npm run check && npm run build
node bin/team-ai.js --help    # lists init, adopt, spoke, attach, doctor, resume, review, upgrade, emit, validate-kb, validate-citations, reindex, search, assemble-manifest, freshness-audit, run-evals, validate-spoke, check-agnostic
node bin/team-ai.js check-agnostic && echo "AGNOSTIC OK"
git tag v0.1.0 && git branch v0
```
Expected: all green; help lists every command; tag and branch created.

**Steps:**
- [ ] **Step 1:** write `docs/definition-of-done.md` skeleton with every clause as an unchecked box.
- [ ] **Step 2:** for each clause, run the proving command, paste the output, check the box. Where a clause fails, fix it (new `fix:` commit) and re-run.
- [ ] **Step 3:** adapt the root `README.md` from `docs/README.source.md` (keep it honest to what shipped — lexical only, server is a template, etc.).
- [ ] **Step 4:** finalize `CHANGELOG.md`.
- [ ] **Step 5:** `npm run check && npm run build`, capture output into the DoD doc.
- [ ] **Step 6: commit** `chore(release): team-ai 0.1.0`, then `git tag v0.1.0 && git branch v0`.

```json:metadata
{"userGate": true, "tags": ["user-gate"], "verifyCommand": "npm ci && npm run check && npm run build && node bin/team-ai.js --help && node bin/team-ai.js check-agnostic", "acceptanceCriteria": ["Root README adapted from docs/README.source.md with real install command","docs/definition-of-done.md walks every DoD clause with command+output evidence","All 11 build-prompt items mapped to shipped paths","npm run check passes; dist/ builds; team-ai --help lists every command","CHANGELOG [0.1.0] dated and [Unreleased] emptied","git tag v0.1.0 and branch v0 created","check-agnostic exits 0 on final tree"]}
```

---

## Self-Review

**1. Spec coverage** — build-prompt items 1–11 mapped:

| Item | Tasks |
|---|---|
| 1 Repo scaffolding | 0, 1, 2, 3, 38 |
| 2 Schemas | 4 (+ 15, 19, 20 add schemas) |
| 3 Scripts (10, deterministic) | 11, 12, 13, 14, 15, 16, 17 |
| 4 Retrieval adapter (lexical only) | 8, 9, 10 |
| 5 The interview (Acts 0–5, 3 gates) | 20, 21, 22, 23, 24, 25, 26 |
| 6 Generator + templates | 27, 28, 29, 30, 32, 33, 34 |
| 7 Catalogs (4 presets, resolution order) | 18, 19 |
| 8 Agent/skill/persona templates + emitters | 29, 35 |
| 9 Eval harness + one example | 15 |
| 10 Optional local MCP server | 31 |
| 11 `docs/quality-bar.md` | 37 |
| Adopt an existing repo (design §18.1) | 41, 42, 43, 44 |
| Dogfood | 39 |
| Definition of done | 40 |

Design §3 overrides all reflected. The one added question (`ctx.org_path`) is in Task 20 and flagged. Design §18 (non-destructive generation + reconciliation) is covered by Tasks 23 (`existingAssets`), 27 (collision classification, no delete/overwrite), 32 (`--on-conflict` prompt), and 39 Run A (proof against real Arcwright files). Design §18.1 (`team-ai adopt`) is Tasks 41–44, exercised against the real Arcwright repo in 39 Run A. All of it is deterministic — no model calls. No spec section is uncovered.

**2. Placeholder scan** — the CI `validate` job in Task 3 is explicitly a placeholder *with the exact replacement given in Task 17 Step 5*. Template `.hbs` bodies are illustrated with at least one full example each (Tasks 20, 28); remaining template files are enumerated with their required rendered-output assertions, which is the spec an executor needs. No "TBD"/"handle edge cases"/"similar to Task N" left.

**3. Type consistency** — `RetrievalAdapter`/`Hit` (Task 8) are used unchanged in Tasks 9, 10, 12, 15, 31, 35. `EngineState` (Task 22) flows into Tasks 24, 25, 26, 27, 32. `validate(name, data)` signature (Task 4) is used identically everywhere. `run(opts): Promise<number>` command convention holds across Milestone D and is invoked by `cli.ts` the same way each time. `generateStub` (Task 19) is reused in Task 29.

---

## Gate enforcement note

Tasks 39 and 40 are tagged `userGate: true` (the build prompt's "Do not consider the build done until you have run it against itself" and "verify the Definition of Done line by line" — Scope + Proof signals). The plan runs end-to-end as-is. If you want automatic close-time enforcement, the hook JSON snippets are in the superpowers `README.md` — paste them into `.claude/settings.json` (or `settings.local.json`). Happy to walk you through it.
