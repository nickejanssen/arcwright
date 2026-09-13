# team-ai Agent Architecture — Phase A Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers-extended-cc:subagent-driven-development (recommended) or superpowers-extended-cc:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generate the three-tier agent topology into Arcwright — one deterministic router, three group SMEs, thirteen terminal specialists — and migrate the KB from five generic namespaces to fourteen real Arcwright ones.

**Architecture:** Four framework changes land in `team-ai` first (manifest schema extension, per-domain namespace fix, instance-catalog wiring, a namespace remap command), released as 0.4.0. Arcwright then supplies its own namespace preset and answers file, runs the gated migration, and generates the topology. Generation is non-destructive throughout: existing hand-authored agents and skills are registered in the manifest, never overwritten.

**Tech Stack:** TypeScript / Node 22 / ESM, Vitest, Ajv (JSON Schema 2020-12), Handlebars templates, `yaml`.

**User decisions (already made):**
- "Design all 3, build in order" — this plan is Phase A only; B and C get their own plans.
- Domain shape: "It is 1, 2, and 3" — keep 12+ narrow domains, group them under tier-2 leads, and split titles per game. Resolved as 3 tiers / 13 specialists / 14 namespaces.
- "Topology approved — remap before merge" — superseded by events: PR #308 merged during design, so the remap is now a migration (Task 8), not a pre-merge fix.
- "Approved as designed" for the two-file manifest split (declared vs observed).
- "Everything" — enforcement skills, hooks, workflows, and golden questions are all in scope, but land in **Phase B**, not here.
- "Add semantic retrieval to this build" with local embeddings — **Phase C**, not here.
- Spec D1: existing agents/skills are registered, never regenerated.
- Spec D2: `nightcap-couch-race` is an `authority: archived` domain served by `title-sme`, not a specialist.
- Spec D3: the founder is `owner` on every domain.

**Spec:** [`docs/specs/0089-team-ai-agent-architecture.md`](../../specs/0089-team-ai-agent-architecture.md) (Approved 2026-09-13)

**Framework design note (read before Tasks 1–6):** [team-ai `docs/design/2026-09-13-agent-topology-design.md`](https://github.com/nickejanssen/team-ai/blob/main/docs/design/2026-09-13-agent-topology-design.md) is the design of record for the team-ai half of this plan. The spec above is Arcwright-specific. The design note is the generic version that belongs in the framework. Code in team-ai must match the note, and nothing Arcwright-specific may enter team-ai. `node dist/cli.js check-agnostic` enforces that for shipped source.

---

## Repos

Two working trees. Tasks 1–6 are in **team-ai**, Tasks 7–11 are in **arcwright**.

| Repo | Path | Branch to create |
|---|---|---|
| team-ai | `C:/Users/nicke/OneDrive/Desktop/team-ai` | `feat/agent-topology-phase-a` |
| arcwright | a fresh worktree off `main` | `claude/team-ai-agent-topology` |

`team-ai` 0.4.0 must be released (Task 6) before Task 9 can consume it.

---

## File Structure

**team-ai — modified**

| File | Responsibility |
|---|---|
| `schemas/manifest.schema.json` | Adds `group`, `authority`, `not_owned`, `depends_on` to a domain; adds top-level `agents` and `skills` arrays |
| `src/schema/types.ts` | Hand-written mirrors — `ManifestDomain`, new `ManifestAgent` / `ManifestSkill`, `Manifest` |
| `src/manifest/assemble.ts` | Key ordering and pass-through for the new fields and sections |
| `src/generator/context.ts` | Emits `domains[].namespace` so each domain carries its own |
| `src/generator/entity-files.ts` | Uses `domain.namespace` instead of `namespaces[0]` |
| `src/interview/gates.ts` | `loadCatalog()` accepts an instance catalog directory |

**team-ai — created**

| File | Responsibility |
|---|---|
| `src/remap/plan.ts` | Pure: given a mapping + scanned docs, produce a per-file remap proposal |
| `src/remap/apply.ts` | Pure-ish: apply an approved proposal, rewriting `namespace` and `id` |
| `src/commands/remap-namespaces.ts` | CLI wrapper — all file IO |
| `schemas/remap-plan.schema.json` | Shape of the proposal file |

**arcwright — created**

| File | Responsibility |
|---|---|
| `catalog/namespaces/custom.yaml` | The 14 Arcwright namespaces (instance catalog layer) |
| `.team-ai/answers.yaml` | Deterministic interview answers for regeneration |
| `.team-ai/namespace-remap.yaml` | The 5→14 mapping, including per-file one-to-many decisions |
| `agents/manifest.fragment.yaml` | 14 domains, 17 agents, registered skills |

---

## Task 1: Extend the manifest schema for domains

**Goal:** `manifest.schema.json` accepts `group`, `authority`, `not_owned`, and `depends_on` on a domain, and rejects an invalid `authority`.

**Files:**
- Modify: `schemas/manifest.schema.json`
- Modify: `src/schema/types.ts:47-58` (`ManifestDomain`)
- Test: `src/schema/validate.test.ts`

**Acceptance Criteria:**
- [ ] A domain with all four new fields validates
- [ ] A domain with `authority: "canonical"`, `"provisional"`, or `"archived"` validates; any other value fails
- [ ] A domain omitting all four still validates (they are optional — existing manifests keep working)
- [ ] `additionalProperties: false` still rejects an unknown key

**Verify:** `npx vitest run src/schema/` → all pass

**Steps:**

- [ ] **Step 1: Write the failing tests**

Append to `src/schema/validate.test.ts`:

```typescript
describe("manifest domain — topology fields", () => {
  const base = {
    id: "knowledge-graph",
    description: "Who knows what, when, and from whom.",
    keywords: ["knowledge state"],
    kb_namespace: "knowledge-graph",
    subagent: "knowledge-graph-sme",
    model_tier: "small",
    owner: "Nico Janssen",
  };

  it("accepts group, authority, not_owned and depends_on", () => {
    const result = validate("manifest", {
      domains: [
        {
          ...base,
          group: "engine",
          authority: "canonical",
          not_owned: ["character personality"],
          depends_on: ["arc-execution"],
        },
      ],
    });
    expect(result.ok).toBe(true);
  });

  it("rejects an authority value outside the enum", () => {
    const result = validate("manifest", {
      domains: [{ ...base, authority: "definitive" }],
    });
    expect(result.ok).toBe(false);
  });

  it("still accepts a domain with none of the new fields", () => {
    expect(validate("manifest", { domains: [base] }).ok).toBe(true);
  });
});
```

- [ ] **Step 2: Run to confirm failure**

Run: `npx vitest run src/schema/validate.test.ts -t "topology fields"`
Expected: the first test FAILS — `additionalProperties` rejects `group`.

- [ ] **Step 3: Extend the schema**

In `schemas/manifest.schema.json`, inside `$defs.manifestDomain.properties`, add after `"escalate_to"`:

```json
        "group": { "type": "string" },
        "authority": {
          "type": "string",
          "enum": ["canonical", "provisional", "archived"]
        },
        "not_owned": {
          "type": "array",
          "items": { "type": "string" }
        },
        "depends_on": {
          "type": "array",
          "items": { "type": "string" }
        }
```

- [ ] **Step 4: Mirror in TypeScript**

In `src/schema/types.ts`, replace the `ManifestDomain` interface with:

```typescript
export type DomainAuthority = "canonical" | "provisional" | "archived";

export interface ManifestDomain {
  id: string;
  description: string;
  keywords: string[];
  kb_namespace: string;
  subagent: string;
  model_tier: ModelTier;
  owner: string;
  repo?: string;
  escalate_to?: string;
  group?: string;
  authority?: DomainAuthority;
  not_owned?: string[];
  depends_on?: string[];
}
```

- [ ] **Step 5: Run tests**

Run: `npx vitest run src/schema/`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add schemas/manifest.schema.json src/schema/types.ts src/schema/validate.test.ts
git commit -m "feat(manifest): add group, authority, not_owned and depends_on to domains

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

## Task 2: Add `agents` and `skills` manifest sections

**Goal:** The manifest carries the full agent roster and skill registry alongside domains, and `assembleManifest` round-trips both.

**Files:**
- Modify: `schemas/manifest.schema.json`
- Modify: `src/schema/types.ts` (`Manifest`)
- Modify: `src/manifest/assemble.ts`
- Test: `src/manifest/assemble.test.ts`, `src/schema/validate.test.ts`

**Acceptance Criteria:**
- [ ] A manifest with `agents` and `skills` validates
- [ ] A manifest with neither still validates (both optional)
- [ ] A skill with `deterministic: true` and a `script` validates
- [ ] `assembleManifest` passes both sections through unchanged and sorts agents by name
- [ ] `serializeManifest` emits `domains`, then `agents`, then `skills`

**Verify:** `npx vitest run src/manifest/ src/schema/` → all pass

**Steps:**

- [ ] **Step 1: Write the failing tests**

Append to `src/manifest/assemble.test.ts`:

```typescript
describe("assembleManifest — agents and skills", () => {
  const domain = {
    id: "safety",
    description: "Engine-layer content safety.",
    keywords: ["safety"],
    kb_namespace: "safety",
    subagent: "safety-sme",
    model_tier: "small" as const,
    owner: "Nico Janssen",
  };

  it("passes agents and skills through and sorts agents by name", () => {
    const result = assembleManifest({
      fragment: {
        domains: [domain],
        agents: [
          { name: "safety-sme", tier: 3, kind: "subagent", max_hops: 0, kb_namespaces: ["safety"] },
          { name: "sme", tier: 1, kind: "router", max_hops: 2, kb_namespaces: [] },
        ],
        skills: [{ id: "kb-answer", deterministic: false }],
      },
      spokes: [],
    });

    expect(result.agents?.map((a) => a.name)).toEqual(["safety-sme", "sme"]);
    expect(result.skills?.[0]?.id).toBe("kb-answer");
  });

  it("serializes domains, then agents, then skills", () => {
    const yaml = serializeManifest({
      domains: [domain],
      agents: [{ name: "sme", tier: 1, kind: "router", max_hops: 2, kb_namespaces: [] }],
      skills: [{ id: "kb-answer", deterministic: false }],
    });
    expect(yaml.indexOf("domains:")).toBeLessThan(yaml.indexOf("agents:"));
    expect(yaml.indexOf("agents:")).toBeLessThan(yaml.indexOf("skills:"));
  });
});
```

- [ ] **Step 2: Run to confirm failure**

Run: `npx vitest run src/manifest/assemble.test.ts -t "agents and skills"`
Expected: FAIL — `agents` is not a known property.

- [ ] **Step 3: Extend the schema**

In `schemas/manifest.schema.json`, add to top-level `properties` (alongside `domains`):

```json
    "agents": {
      "type": "array",
      "items": { "$ref": "#/$defs/manifestAgent" }
    },
    "skills": {
      "type": "array",
      "items": { "$ref": "#/$defs/manifestSkill" }
    }
```

And add to `$defs`:

```json
    "manifestAgent": {
      "type": "object",
      "additionalProperties": false,
      "required": ["name", "tier", "kind", "max_hops", "kb_namespaces"],
      "properties": {
        "name": { "type": "string" },
        "tier": { "type": "integer", "minimum": 1, "maximum": 3 },
        "kind": { "type": "string", "enum": ["router", "subagent", "persona"] },
        "group": { "type": "string" },
        "max_hops": { "type": "integer", "minimum": 0 },
        "kb_namespaces": { "type": "array", "items": { "type": "string" } },
        "skills": { "type": "array", "items": { "type": "string" } },
        "escalate_to": { "type": "string" },
        "source": { "type": "string", "enum": ["generated", "authored"] }
      }
    },
    "manifestSkill": {
      "type": "object",
      "additionalProperties": false,
      "required": ["id", "deterministic"],
      "properties": {
        "id": { "type": "string" },
        "description": { "type": "string" },
        "deterministic": { "type": "boolean" },
        "script": { "type": "string" },
        "used_by": { "type": "array", "items": { "type": "string" } },
        "path": { "type": "string" },
        "source": { "type": "string", "enum": ["generated", "authored"] }
      }
    }
```

- [ ] **Step 4: Mirror in TypeScript**

In `src/schema/types.ts`, replace `Manifest` and add the two interfaces:

```typescript
export interface ManifestAgent {
  name: string;
  tier: 1 | 2 | 3;
  kind: AgentKind;
  max_hops: number;
  kb_namespaces: string[];
  group?: string;
  skills?: string[];
  escalate_to?: string;
  source?: "generated" | "authored";
}

export interface ManifestSkill {
  id: string;
  deterministic: boolean;
  description?: string;
  script?: string;
  used_by?: string[];
  path?: string;
  source?: "generated" | "authored";
}

export interface Manifest {
  domains: ManifestDomain[];
  agents?: ManifestAgent[];
  skills?: ManifestSkill[];
}
```

- [ ] **Step 5: Pass both sections through `assembleManifest`**

In `src/manifest/assemble.ts`, add near the other helpers:

```typescript
function readAgents(fragment: unknown): ManifestAgent[] | undefined {
  if (!isRecord(fragment) || !Array.isArray(fragment.agents)) return undefined;
  return [...(fragment.agents as ManifestAgent[])].sort((a, b) => a.name.localeCompare(b.name));
}

function readSkills(fragment: unknown): ManifestSkill[] | undefined {
  if (!isRecord(fragment) || !Array.isArray(fragment.skills)) return undefined;
  return [...(fragment.skills as ManifestSkill[])].sort((a, b) => a.id.localeCompare(b.id));
}
```

Then in `assembleManifest`, replace the final block with:

```typescript
  const domains = collected.sort((a, b) => a.id.localeCompare(b.id));
  const assembled: Manifest = { domains };

  const agents = readAgents(input.fragment);
  if (agents !== undefined) assembled.agents = agents;
  const skills = readSkills(input.fragment);
  if (skills !== undefined) assembled.skills = skills;

  const guard = validate("manifest", assembled);
  if (!guard.ok) {
    throw new Error(`assembled manifest is invalid: ${firstError(guard.errors)}`);
  }
  return guard.value;
```

Add the new field names to `DOMAIN_KEY_ORDER` after `escalate_to`:

```typescript
  "group",
  "authority",
  "not_owned",
  "depends_on",
```

And update `serializeManifest`:

```typescript
export function serializeManifest(manifest: Manifest): string {
  const domains = [...manifest.domains]
    .sort((a, b) => a.id.localeCompare(b.id))
    .map((domain) => orderDomainKeys(domain));
  const out: Record<string, unknown> = { domains };
  if (manifest.agents !== undefined) out.agents = manifest.agents;
  if (manifest.skills !== undefined) out.skills = manifest.skills;
  return `${MANIFEST_HEADER}\n${stringifyYaml(out)}`;
}
```

Import `ManifestAgent` and `ManifestSkill` in the existing type import.

- [ ] **Step 6: Run tests**

Run: `npx vitest run src/manifest/ src/schema/`
Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add schemas/manifest.schema.json src/schema/types.ts src/manifest/
git commit -m "feat(manifest): add agents and skills sections

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

## Task 3: Give each domain SME its own namespace

**Goal:** Fix the bug where every generated domain SME is scoped to `namespaces[0]`, which would make all thirteen specialists read the same namespace and defeat context bounding.

**Files:**
- Modify: `src/generator/context.ts:78-82` (the `domains` mapping)
- Modify: `src/generator/entity-files.ts:32-39` (`asDomains`), `:105-120` (the render loop)
- Test: `src/generator/instance-template.test.ts`

**Acceptance Criteria:**
- [ ] `buildContext` emits a `namespace` on every entry of `domains`
- [ ] When a domain's slug matches a namespace name, that namespace is used
- [ ] When it does not match, it falls back to the first namespace (existing behaviour preserved)
- [ ] Two domains with different namespaces generate two SME YAMLs with different `kb_namespaces`
- [ ] Every generated domain SME still validates against `agent.schema.json`

**Verify:** `npx vitest run src/generator/` → all pass

**Steps:**

- [ ] **Step 1: Write the failing test**

Append to `src/generator/instance-template.test.ts`:

```typescript
it("scopes each domain SME to its own namespace, not the first one", () => {
  const context = {
    namespaces: ["arc-execution", "knowledge-graph"],
    domains: [
      { slug: "arc-execution", name: "Arc Execution", namespace: "arc-execution" },
      { slug: "knowledge-graph", name: "Knowledge Graph", namespace: "knowledge-graph" },
    ],
    roles: [],
    personas: [],
  };
  const dir = mkdtempSync(join(tmpdir(), "team-ai-ns-"));
  const result = emptyRenderResult();
  renderEntityFiles(context, dir, new Map(), "siblings", result);

  const a = readFileSync(join(dir, "agents/arc-execution-sme.yaml"), "utf8");
  const b = readFileSync(join(dir, "agents/knowledge-graph-sme.yaml"), "utf8");
  expect(a).toContain("kb_namespaces: [arc-execution]");
  expect(b).toContain("kb_namespaces: [knowledge-graph]");
  rmSync(dir, { recursive: true, force: true });
});
```

Reuse whatever the file already uses to build an empty `RenderResult`; if there is no helper, construct one inline with empty arrays for `created`, `unchanged`, `updated`, `collisions`, `siblingsWritten`, `manifestEntries`, and `warnings`.

- [ ] **Step 2: Run to confirm failure**

Run: `npx vitest run src/generator/instance-template.test.ts -t "own namespace"`
Expected: FAIL — both files contain `kb_namespaces: [arc-execution]`.

- [ ] **Step 3: Carry the namespace through the context**

In `src/generator/context.ts`, change the `DomainBlock` interface and the `domains` mapping:

```typescript
interface DomainBlock {
  slug: string;
  name: string;
  namespace: string;
}
```

```typescript
  const domains: DomainBlock[] = parseDomains(eff["agents.domains"]).map((d) => {
    const s = slug(d);
    // A domain owns the namespace of the same name when one exists; otherwise
    // it falls back to the first namespace, which is the pre-existing
    // behaviour for presets whose namespaces are not per-domain.
    return {
      slug: s,
      name: d,
      namespace: namespaces.includes(s) ? s : (namespaces[0] ?? "operating"),
    };
  });
```

- [ ] **Step 4: Use it in the renderer**

In `src/generator/entity-files.ts`, update `asDomains` to carry the field:

```typescript
function asDomains(value: unknown): { slug: string; name: string; namespace?: string }[] {
  if (!Array.isArray(value)) return [];
  const out: { slug: string; name: string; namespace?: string }[] = [];
  for (const item of value) {
    if (item !== null && typeof item === "object") {
      const rec = item as Record<string, unknown>;
      if (typeof rec.slug === "string" && typeof rec.name === "string") {
        out.push({
          slug: rec.slug,
          name: rec.name,
          ...(typeof rec.namespace === "string" ? { namespace: rec.namespace } : {}),
        });
      }
    }
  }
  return out;
}
```

And in the domain loop, replace `namespace: firstNamespace` with:

```typescript
      namespace: domain.namespace ?? firstNamespace,
```

- [ ] **Step 5: Run tests**

Run: `npx vitest run src/generator/`
Expected: PASS, including the pre-existing tests (the fallback keeps them green).

- [ ] **Step 6: Commit**

```bash
git add src/generator/context.ts src/generator/entity-files.ts src/generator/instance-template.test.ts
git commit -m "fix(generator): scope each domain SME to its own namespace

Every generated domain SME was scoped to namespaces[0], so a multi-domain
instance produced N agents all reading the same namespace -- which defeats
the per-specialist context bound the topology depends on.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

## Task 4: Let an instance supply its own catalog

**Goal:** `loadCatalog()` resolves an instance-level catalog directory, so a repo can define its own namespace preset without adding team-specific content to the framework.

**Why this is required, not optional.** `kb.namespaces` is a `single_select`, and `Engine.answer` throws `'<value>' is not a valid option` for anything outside the declared options (`src/interview/engine.ts:110-114`). So an answers file *cannot* name a preset called `arcwright`. The one selectable escape hatch is `custom` — but `buildContext` looks the answer up with `catalog.namespaces.get("custom")`, finds nothing, and silently falls back to the five generic `DEFAULT_NAMESPACES`. Wiring the instance layer is what makes a repo-supplied preset named `custom.yaml` actually resolve. Note also that `kb.catalog_override`'s `org-catalog-repo` option is recorded into the profile but consumed by nothing (`src/interview/gates.ts:131`, `src/interview/outputs.ts:95`) — there is no existing mechanism to reuse.

**Files:**
- Modify: `src/interview/gates.ts:152-158`
- Test: `src/catalog/resolve.test.ts`

**Acceptance Criteria:**
- [ ] `loadCatalog(instanceDir)` returns a catalog containing a preset defined only in `instanceDir`
- [ ] An instance preset replaces a toolkit preset of the same name and is stamped with instance origin
- [ ] `loadCatalog()` with no argument behaves exactly as before
- [ ] A non-existent instance dir is ignored rather than throwing

**Verify:** `npx vitest run src/catalog/ src/interview/` → all pass

**Steps:**

- [ ] **Step 1: Write the failing test**

Append to `src/catalog/resolve.test.ts`:

```typescript
describe("loadCatalog with an instance layer", () => {
  it("finds a preset that exists only in the instance catalog", () => {
    const dir = mkdtempSync(join(tmpdir(), "team-ai-cat-"));
    mkdirSync(join(dir, "namespaces"), { recursive: true });
    writeFileSync(
      join(dir, "namespaces", "custom.yaml"),
      [
        "name: arcwright",
        "description: Arcwright domains.",
        "second_level:",
        "  - arc-execution",
        "  - knowledge-graph",
        'domain_dir: "domains/<name>"',
        "seed_docs:",
        ...["a", "b", "c", "d", "e"].map(
          (n) => `  - path: ${n}.md\n    title: ${n}\n    purpose: seed ${n}`,
        ),
      ].join("\n"),
      "utf8",
    );

    const catalog = loadCatalog(dir);
    // Keyed by FILENAME STEM, not by the `name:` field — which is exactly why
    // an instance preset must be called custom.yaml to be selectable as the
    // `custom` answer to kb.namespaces.
    expect(catalog?.namespaces.get("custom")?.value.second_level).toContain("knowledge-graph");
    expect(catalog?.namespaces.get("arcwright")).toBeUndefined();
    rmSync(dir, { recursive: true, force: true });
  });

  it("ignores an instance dir that does not exist", () => {
    expect(loadCatalog(join(tmpdir(), "definitely-not-here"))).not.toBeNull();
  });
});
```

Import `loadCatalog` from `../interview/gates.js` and the `node:fs` helpers at the top of the file.

- [ ] **Step 2: Run to confirm failure**

Run: `npx vitest run src/catalog/resolve.test.ts -t "instance layer"`
Expected: FAIL — `loadCatalog` takes no arguments, so the preset is not found.

- [ ] **Step 3: Wire the layer**

In `src/interview/gates.ts`:

```typescript
export function loadCatalog(instanceDir?: string): ResolvedCatalog | null {
  try {
    return resolveCatalog(
      instanceDir === undefined
        ? { toolkitDir: CATALOG_DIR }
        : { toolkitDir: CATALOG_DIR, instanceDir },
    );
  } catch {
    return null;
  }
}
```

`resolveCatalog` already tolerates a missing directory — `listFiles` catches the `readdirSync` failure and returns `[]` — so no extra guard is needed.

- [ ] **Step 4: Pass it from the generator**

In `src/generator/context.ts`, accept and forward an instance catalog dir:

```typescript
  const catalog = loadCatalog(asString(extra.instanceCatalogDir) || undefined);
```

`extra` is already `BuildContextExtra` with an index signature, so no interface change is needed. Callers that pass nothing keep the old behaviour.

- [ ] **Step 5: Run tests**

Run: `npx vitest run src/catalog/ src/interview/ src/generator/`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/interview/gates.ts src/generator/context.ts src/catalog/resolve.test.ts
git commit -m "feat(catalog): resolve an instance-level catalog layer

Lets a repo define its own namespace preset without adding team-specific
content to the framework catalog.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

## Task 5: `team-ai remap-namespaces` — proposal and apply

**Goal:** A deterministic command that rewrites `namespace` and `id` front-matter values across a KB according to a supplied mapping, producing a reviewable proposal first and only writing when explicitly applied.

**Files:**
- Create: `src/remap/plan.ts`, `src/remap/plan.test.ts`
- Create: `src/remap/apply.ts`, `src/remap/apply.test.ts`
- Create: `src/commands/remap-namespaces.ts`
- Modify: `src/cli.ts` (register the command)

**Acceptance Criteria:**
- [ ] Given a mapping `{ platform: "knowledge-graph" }`, a doc with `namespace: platform` and `id: platform.architecture.x` is proposed as `namespace: knowledge-graph`, `id: knowledge-graph.architecture.x`
- [ ] A per-file override in the mapping beats the namespace-level rule (this is how one-to-many splits are expressed)
- [ ] A doc whose namespace is not in the mapping is reported as `unchanged`, never rewritten
- [ ] Running without `--apply` writes only the proposal file and leaves every doc byte-identical
- [ ] `--apply` rewrites only `namespace` and `id`; every other front-matter key and the entire body are byte-identical
- [ ] Applying twice is idempotent
- [ ] A doc whose front matter fails to parse is reported as a conflict, not a crash

**Verify:** `npx vitest run src/remap/` → all pass

**Steps:**

- [ ] **Step 1: Write the failing tests for the planner**

Create `src/remap/plan.test.ts`:

```typescript
import { mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { afterEach, describe, expect, it } from "vitest";

import { buildRemapPlan } from "./plan.js";

const dirs: string[] = [];

function repo(): string {
  const dir = mkdtempSync(join(tmpdir(), "team-ai-remap-"));
  dirs.push(dir);
  mkdirSync(join(dir, "docs", "architecture"), { recursive: true });
  return dir;
}

function doc(ns: string, id: string): string {
  return [
    "---",
    `id: ${id}`,
    `namespace: ${ns}`,
    "title: A Doc",
    "owner: Nico Janssen",
    "status: active",
    'review_by: "2027-01-01"',
    "sensitivity: internal",
    "source: authored",
    "tags: []",
    "supersedes: []",
    "---",
    "",
    "# Body",
    "",
  ].join("\n");
}

afterEach(() => {
  for (const d of dirs.splice(0)) rmSync(d, { recursive: true, force: true });
});

describe("buildRemapPlan", () => {
  it("rewrites both namespace and the id's first segment", () => {
    const dir = repo();
    writeFileSync(
      join(dir, "docs/architecture/04.md"),
      doc("platform", "platform.architecture.04"),
      "utf8",
    );

    const plan = buildRemapPlan({
      root: dir,
      mapping: { namespaces: { platform: "knowledge-graph" }, files: {} },
    });

    const item = plan.items.find((i) => i.path === "docs/architecture/04.md");
    expect(item?.to_namespace).toBe("knowledge-graph");
    expect(item?.to_id).toBe("knowledge-graph.architecture.04");
    expect(readFileSync(join(dir, "docs/architecture/04.md"), "utf8")).toContain(
      "namespace: platform",
    );
  });

  it("lets a per-file override beat the namespace rule", () => {
    const dir = repo();
    writeFileSync(
      join(dir, "docs/architecture/06.md"),
      doc("platform", "platform.architecture.06"),
      "utf8",
    );

    const plan = buildRemapPlan({
      root: dir,
      mapping: {
        namespaces: { platform: "knowledge-graph" },
        files: { "docs/architecture/06.md": "model-routing" },
      },
    });

    expect(plan.items[0]?.to_namespace).toBe("model-routing");
  });

  it("reports an unmapped namespace as unchanged", () => {
    const dir = repo();
    writeFileSync(join(dir, "docs/architecture/x.md"), doc("decisions", "decisions.x.y"), "utf8");

    const plan = buildRemapPlan({ root: dir, mapping: { namespaces: {}, files: {} } });
    expect(plan.items[0]?.status).toBe("unchanged");
  });
});
```

- [ ] **Step 2: Run to confirm failure**

Run: `npx vitest run src/remap/plan.test.ts`
Expected: FAIL — `./plan.js` does not exist.

- [ ] **Step 3: Implement the planner**

Create `src/remap/plan.ts`:

```typescript
// Deterministic. No model calls. No network.
//
// Builds a per-file proposal for rewriting KB namespace values. Reads only;
// every write lives in apply.ts. A one-to-many split (one old namespace
// becoming several new ones) is expressed as per-file overrides, because only
// a human can decide which file goes where.

import { readFileSync } from "node:fs";
import { join, relative } from "node:path";

import { parseFrontmatter } from "../kb/frontmatter.js";
import { hasFrontmatter } from "../adopt/backfill.js";
import { walkMarkdown } from "../kb/loader.js";

export interface RemapMapping {
  namespaces: Record<string, string>;
  files: Record<string, string>;
}

export type RemapStatus = "remap" | "unchanged" | "conflict";

export interface RemapItem {
  path: string;
  status: RemapStatus;
  from_namespace: string;
  to_namespace: string;
  from_id: string;
  to_id: string;
  conflict?: string;
}

export interface RemapPlan {
  root: string;
  items: RemapItem[];
}

export interface BuildRemapPlanOptions {
  root: string;
  mapping: RemapMapping;
}

// An id is `<namespace>.<rest>`; only the first segment carries the namespace.
export function rewriteId(id: string, toNamespace: string): string {
  const dot = id.indexOf(".");
  return dot === -1 ? toNamespace : `${toNamespace}${id.slice(dot)}`;
}

export function buildRemapPlan(opts: BuildRemapPlanOptions): RemapPlan {
  const items: RemapItem[] = [];

  for (const abs of walkMarkdown(join(opts.root, "docs"))) {
    const rel = relative(opts.root, abs).split("\\").join("/");
    const raw = readFileSync(abs, "utf8");

    if (!hasFrontmatter(raw)) {
      items.push({
        path: rel,
        status: "conflict",
        from_namespace: "",
        to_namespace: "",
        from_id: "",
        to_id: "",
        conflict: "no front matter",
      });
      continue;
    }

    let data: Record<string, unknown>;
    try {
      ({ data } = parseFrontmatter(raw));
    } catch (err) {
      items.push({
        path: rel,
        status: "conflict",
        from_namespace: "",
        to_namespace: "",
        from_id: "",
        to_id: "",
        conflict: `front matter does not parse: ${err instanceof Error ? err.message.split("\n")[0] : String(err)}`,
      });
      continue;
    }

    const fromNs = typeof data.namespace === "string" ? data.namespace : "";
    const fromId = typeof data.id === "string" ? data.id : "";
    const toNs = opts.mapping.files[rel] ?? opts.mapping.namespaces[fromNs];

    if (toNs === undefined || toNs === fromNs) {
      items.push({
        path: rel,
        status: "unchanged",
        from_namespace: fromNs,
        to_namespace: fromNs,
        from_id: fromId,
        to_id: fromId,
      });
      continue;
    }

    items.push({
      path: rel,
      status: "remap",
      from_namespace: fromNs,
      to_namespace: toNs,
      from_id: fromId,
      to_id: rewriteId(fromId, toNs),
    });
  }

  items.sort((a, b) => a.path.localeCompare(b.path));
  return { root: opts.root, items };
}
```

If `walkMarkdown` is not exported from `src/kb/loader.ts`, export the existing internal directory walker there rather than writing a second one; if none exists, add:

```typescript
export function* walkMarkdown(dir: string): Generator<string> {
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const abs = join(dir, entry.name);
    if (entry.isDirectory()) yield* walkMarkdown(abs);
    else if (entry.isFile() && entry.name.endsWith(".md")) yield abs;
  }
}
```

- [ ] **Step 4: Run planner tests**

Run: `npx vitest run src/remap/plan.test.ts`
Expected: PASS.

- [ ] **Step 5: Write the failing tests for apply**

Create `src/remap/apply.test.ts`:

```typescript
import { mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { afterEach, describe, expect, it } from "vitest";

import { buildRemapPlan } from "./plan.js";
import { applyRemapPlan } from "./apply.js";

const dirs: string[] = [];

function fixture(): string {
  const dir = mkdtempSync(join(tmpdir(), "team-ai-remap-apply-"));
  dirs.push(dir);
  mkdirSync(join(dir, "docs", "architecture"), { recursive: true });
  writeFileSync(
    join(dir, "docs/architecture/04.md"),
    [
      "---",
      "id: platform.architecture.04",
      "namespace: platform",
      "title: Knowledge Graph",
      "owner: Nico Janssen",
      "status: active",
      'review_by: "2027-01-01"',
      "sensitivity: internal",
      "source: authored",
      "tags: []",
      "supersedes: []",
      "---",
      "",
      "# Knowledge Graph",
      "",
      "Body text that must not change.",
      "",
    ].join("\n"),
    "utf8",
  );
  return dir;
}

afterEach(() => {
  for (const d of dirs.splice(0)) rmSync(d, { recursive: true, force: true });
});

describe("applyRemapPlan", () => {
  it("rewrites only namespace and id, preserving everything else", () => {
    const dir = fixture();
    const plan = buildRemapPlan({
      root: dir,
      mapping: { namespaces: { platform: "knowledge-graph" }, files: {} },
    });

    applyRemapPlan(plan);

    const out = readFileSync(join(dir, "docs/architecture/04.md"), "utf8");
    expect(out).toContain("namespace: knowledge-graph");
    expect(out).toContain("id: knowledge-graph.architecture.04");
    expect(out).toContain("title: Knowledge Graph");
    expect(out).toContain("owner: Nico Janssen");
    expect(out).toContain("Body text that must not change.");
  });

  it("is idempotent", () => {
    const dir = fixture();
    const mapping = { namespaces: { platform: "knowledge-graph" }, files: {} };
    applyRemapPlan(buildRemapPlan({ root: dir, mapping }));
    const once = readFileSync(join(dir, "docs/architecture/04.md"), "utf8");
    applyRemapPlan(buildRemapPlan({ root: dir, mapping }));
    expect(readFileSync(join(dir, "docs/architecture/04.md"), "utf8")).toBe(once);
  });
});
```

- [ ] **Step 6: Run to confirm failure**

Run: `npx vitest run src/remap/apply.test.ts`
Expected: FAIL — `./apply.js` does not exist.

- [ ] **Step 7: Implement apply**

Create `src/remap/apply.ts`:

```typescript
// Deterministic. No model calls. No network.
//
// Applies an approved remap plan. Rewrites the `namespace` and `id` lines in
// place with a line-scoped regex rather than re-serializing the front matter,
// so key order, comments, quoting style, and line endings all survive
// untouched. Only items with status "remap" are written.

import { readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";

import type { RemapPlan } from "./plan.js";

export interface ApplyRemapResult {
  written: string[];
  skipped: string[];
}

function replaceScalar(block: string, key: string, value: string): string {
  const pattern = new RegExp(`^(${key}:[ \\t]*)(.*)$`, "m");
  return pattern.test(block) ? block.replace(pattern, `$1${value}`) : block;
}

export function applyRemapPlan(plan: RemapPlan): ApplyRemapResult {
  const written: string[] = [];
  const skipped: string[] = [];

  for (const item of plan.items) {
    if (item.status !== "remap") {
      skipped.push(item.path);
      continue;
    }

    const abs = join(plan.root, item.path);
    const raw = readFileSync(abs, "utf8");

    // Split off the front-matter block so the body can never be touched.
    const close = raw.indexOf("\n---", 3);
    if (close === -1) {
      skipped.push(item.path);
      continue;
    }
    const head = raw.slice(0, close);
    const tail = raw.slice(close);

    let next = replaceScalar(head, "namespace", item.to_namespace);
    next = replaceScalar(next, "id", item.to_id);

    if (next === head) {
      skipped.push(item.path);
      continue;
    }

    writeFileSync(abs, next + tail, "utf8");
    written.push(item.path);
  }

  return { written, skipped };
}
```

- [ ] **Step 8: Run apply tests**

Run: `npx vitest run src/remap/`
Expected: PASS.

- [ ] **Step 9: Add the CLI command**

Create `src/commands/remap-namespaces.ts`:

```typescript
// All file IO for `team-ai remap-namespaces`. The pure logic lives in
// src/remap/. Without --apply this writes only the proposal.

import { readFileSync, writeFileSync } from "node:fs";

import { parse as parseYaml, stringify as stringifyYaml } from "yaml";

import { applyRemapPlan } from "../remap/apply.js";
import { buildRemapPlan, type RemapMapping } from "../remap/plan.js";

export interface RemapOptions {
  root: string;
  mapping: string;
  out: string;
  apply?: boolean;
  output?: (s: string) => void;
}

export function runRemapNamespaces(opts: RemapOptions): number {
  const say = opts.output ?? ((s: string) => console.log(s));
  const mapping = parseYaml(readFileSync(opts.mapping, "utf8")) as RemapMapping;
  const plan = buildRemapPlan({ root: opts.root, mapping });

  const counts = { remap: 0, unchanged: 0, conflict: 0 };
  for (const item of plan.items) counts[item.status] += 1;

  writeFileSync(opts.out, stringifyYaml(plan), "utf8");
  say(`remap proposal: ${opts.out}`);
  say(`  remap ${counts.remap}  unchanged ${counts.unchanged}  conflict ${counts.conflict}`);

  if (opts.apply !== true) {
    say("  (proposal only — re-run with --apply to write)");
    return counts.conflict > 0 ? 1 : 0;
  }

  const result = applyRemapPlan(plan);
  say(`  applied to ${result.written.length} files`);
  return counts.conflict > 0 ? 1 : 0;
}
```

Register it in `src/cli.ts` following the shape of the existing `adopt` registration:

```typescript
  program
    .command("remap-namespaces")
    .description("Rewrite KB namespace and id values according to a mapping file")
    .requiredOption("--root <dir>", "repo root containing docs/")
    .requiredOption("--mapping <file>", "YAML mapping file")
    .option("--out <file>", "where to write the proposal", "remap-plan.yaml")
    .option("--apply", "write the changes (default is proposal only)", false)
    .action((opts: { root: string; mapping: string; out: string; apply: boolean }) => {
      process.exitCode = runRemapNamespaces(opts);
    });
```

- [ ] **Step 10: Full check and commit**

Run: `npm run check`
Expected: all pass.

```bash
git add src/remap/ src/commands/remap-namespaces.ts src/cli.ts
git commit -m "feat(remap): add remap-namespaces command

Rewrites KB namespace and id values from a mapping file. Proposal by
default; --apply writes. Rewrites only the two scalar lines so key order,
quoting, and line endings survive.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

## Task 6: Release team-ai 0.4.0

**Goal:** Tag and publish the framework changes so Arcwright can consume a fixed version.

**Files:**
- Modify: `package.json`, `package-lock.json`, `CHANGELOG.md`

**Acceptance Criteria:**
- [ ] `npm run check` green, `npm run build` succeeds, `node dist/cli.js check-agnostic` reports 0 denied tokens
- [ ] Version is `0.4.0` in both `package.json` and `package-lock.json`
- [ ] CHANGELOG has a `0.4.0` section covering Tasks 1–5
- [ ] Tag `v0.4.0` pushed and a GitHub Release created
- [ ] The `v0` branch is fast-forwarded to include the release commit

**Verify:** `node dist/cli.js remap-namespaces --help` → prints the command's options

**Steps:**

- [ ] **Step 1: Confirm PR #1 is merged first**

```bash
gh pr view 1 --repo nickejanssen/team-ai --json state,title
```

If it is still open, merge it before releasing — 0.4.0 must contain the 0.3.1 fixes.

- [ ] **Step 2: Bump and changelog**

Set `"version": "0.4.0"` in `package.json`, run `npm install --package-lock-only`, and add a `## [0.4.0] - <today>` section to `CHANGELOG.md` with an `### Added` entry per Task 1–5 and a `### Fixed` entry for Task 3. Update the link refs at the bottom.

- [ ] **Step 3: Verify and commit**

```bash
npm run check && npm run build && node dist/cli.js check-agnostic
git add package.json package-lock.json CHANGELOG.md
git commit -m "chore(release): team-ai 0.4.0

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

- [ ] **Step 4: Open the PR, merge, tag, release**

```bash
git push -u origin feat/agent-topology-phase-a
gh pr create --repo nickejanssen/team-ai --base main --title "feat: agent topology framework changes (0.4.0)" --body "Phase A framework changes for arcwright spec 0089. See CHANGELOG.

🤖 Generated with [Claude Code](https://claude.com/claude-code)"
```

After the founder merges:

```bash
git checkout main && git pull
git tag -a v0.4.0 -m "team-ai 0.4.0"
git push origin v0.4.0
gh release create v0.4.0 --title "v0.4.0" --notes-from-tag
git push origin main:v0
```

---

## Task 7: Author Arcwright's namespace preset and answers file

**Goal:** Arcwright declares its own fourteen namespaces and a deterministic answers file, so generation is reproducible and needs no interactive interview.

**Files:**
- Create: `catalog/namespaces/custom.yaml`
- Create: `.team-ai/answers.yaml`
- Create: `.team-ai/namespace-remap.yaml`

**Acceptance Criteria:**
- [ ] `catalog/namespaces/custom.yaml` validates against `namespace-preset.schema.json` (exactly 5 `seed_docs`, ≥1 `second_level`)
- [ ] `second_level` lists all fourteen namespaces
- [ ] `.team-ai/namespace-remap.yaml` maps every one of the five current namespaces
- [ ] Every `docs/architecture/*.md` file has an explicit per-file entry (the one-to-many split)

**Verify:** `node <team-ai>/dist/cli.js remap-namespaces --root . --mapping .team-ai/namespace-remap.yaml --out /tmp/proposal.yaml` → `conflict 0`

**Steps:**

- [ ] **Step 1: Write the namespace preset**

Create `catalog/namespaces/custom.yaml`. **The filename must be `custom.yaml`** — the catalog keys entries by filename stem, and `custom` is the only `kb.namespaces` option that is not a shipped preset, so it is the one value an answers file can legally supply (see Task 4). The `name:` field is metadata and is set to `custom` to match the key.

```yaml
name: custom
description: Arcwright's real expertise domains — engine, titles, and practice.
second_level:
  - arc-execution
  - knowledge-graph
  - character-behavior
  - model-routing
  - session-runtime
  - safety
  - developer-api
  - nightcap
  - monster-rpg
  - daily-case
  - nightcap-couch-race
  - product-roadmap
  - engineering-practice
  - playtest-ops
domain_dir: null
seed_docs:
  - path: product-roadmap/charter.md
    title: What Arcwright is responsible for
    purpose: States the platform's scope and what it deliberately does not do.
  - path: engineering-practice/roles.md
    title: Who does what
    purpose: Maps each role to the decisions and systems it owns.
  - path: arc-execution/overview.md
    title: The arc execution layer
    purpose: Explains how authored arcs resolve deterministically at runtime.
  - path: playtest-ops/onboarding.md
    title: Running a playtest
    purpose: Walks a new operator through preparing and running a session.
  - path: product-roadmap/adr-0001-why-team-ai.md
    title: Why Arcwright stood up team-ai
    purpose: Records the reasoning for adopting team-ai to run this team's AI capability.
```

`seed_docs` must be exactly five (schema `minItems: 5, maxItems: 5`). They are **not** written during Task 9 because generation runs with seeding off — Arcwright already has content.

- [ ] **Step 2: Write the remap mapping**

Create `.team-ai/namespace-remap.yaml`. The `namespaces` block holds the one-to-one rules; the `files` block holds every per-file decision for the two one-to-many splits.

```yaml
# One-to-one: these old namespaces map wholesale.
namespaces:
  operating: product-roadmap
  patterns: engineering-practice
  custom: nightcap

# One-to-many: every file that must not follow its namespace rule.
# docs/architecture/* splits across the seven engine domains.
files:
  docs/architecture/01-overview.md: arc-execution
  docs/architecture/02-technology-stack.md: arc-execution
  docs/architecture/03-arc-execution.md: arc-execution
  docs/architecture/04-knowledge-graph.md: knowledge-graph
  docs/architecture/05-session-persistence.md: session-runtime
  docs/architecture/06-model-routing.md: model-routing
  docs/architecture/07-character-behavior.md: character-behavior
  docs/architecture/08-event-system.md: session-runtime
  docs/architecture/09-developer-api.md: developer-api
  docs/architecture/10-content-safety.md: safety
  docs/architecture/11-telemetry.md: playtest-ops
  docs/architecture/12-build-plan.md: product-roadmap
  docs/architecture/13-cost-model.md: model-routing
  docs/architecture/14-architecture-validation.md: engineering-practice
  docs/architecture/15-development-guide.md: engineering-practice
  docs/architecture/README.md: arc-execution
  docs/architecture/supplemental-schemas.md: arc-execution
  # story bibles split per title
  docs/story-bibles/monster-rpg.md: monster-rpg
  docs/story-bibles/daily-case.md: daily-case
  docs/story-bibles/nightcap-couch-race.md: nightcap-couch-race
  docs/story-bibles/nightcap-murder-mystery.md: nightcap
  docs/story-bibles/README.md: nightcap
```

Before finalising, enumerate the real file list and confirm no `docs/architecture/*.md` or `docs/story-bibles/*.md` file is missing an entry:

```bash
ls docs/architecture/*.md docs/story-bibles/*.md
```

Add an entry for anything not listed above. For `playbooks` (currently `docs/skills/` and `docs/superpowers/`), add per-file entries routing playtest-related skills to `playtest-ops` and the rest to `engineering-practice`:

```bash
ls docs/skills/ docs/superpowers/
```

- [ ] **Step 3: Write the answers file**

`.team-ai/answers.yaml` is a **positional** list of answer strings, consumed in the order the interview asks (`src/generator/init-answers.ts`). The bank holds 31 questions but `ask_if` gating means only a subset is reached, so the order must be confirmed empirically rather than assumed.

First, capture the actual sequence:

```bash
node <team-ai>/dist/cli.js init --dir . --dry-run 2>&1 | tee .team-ai/interview-transcript.txt
```

`--dry-run` writes nothing. Answer interactively once, then transcribe into `.team-ai/answers.yaml` in the same order.

These answers are load-bearing for this design and must be exactly these values:

| Question id | Answer | Why it matters |
|---|---|---|
| `kb.namespaces` | `custom` | The only option that can resolve the instance preset from Step 1. Any shipped preset gives five generic namespaces. |
| `kb.catalog_override` | `use-preset` | The `org-catalog-repo` option is recorded but consumed by nothing. |
| `agents.domains` | the 13 specialist domains, comma-separated | Drives one SME per domain. Exclude `nightcap-couch-race` — per D2 it has no specialist. |
| `team.name` | `Arcwright` | Becomes the doc-id prefix; must stay one lowercase token after slugging. |
| `team.size` | `1-3` | Suppresses generated role subagents, which is correct — D1 keeps the existing hand-authored roles instead. |
| `arch.index_driver` | `lexical` | Semantic retrieval is Phase C. Choosing a vector driver now would generate an index.lock the code cannot serve. |
| `agents.seed` | no | Arcwright already has 459 docs; seeding would write starter content over a real KB. |

The exact `agents.domains` string:

```
arc-execution, knowledge-graph, character-behavior, model-routing, session-runtime, safety, developer-api, nightcap, monster-rpg, daily-case, product-roadmap, engineering-practice, playtest-ops
```

Remaining questions (`team.mission`, `team.surfaces`, `kb.sensitivity`, `arch.*`, `agents.personas`, `agents.skills`, `agents.strictness`) do not affect the topology — answer them truthfully for Arcwright and record what you chose in the transcript file.

- [ ] **Step 3a: Verify the answers file replays cleanly**

```bash
node <team-ai>/dist/cli.js init --dir . --answers .team-ai/answers.yaml --dry-run
```

Expected: completes with no `answer file exhausted` error and reports a generation summary. If it throws `'X' is not a valid option`, an entry is out of position — re-check against the transcript.

- [ ] **Step 4: Verify the mapping produces no conflicts**

```bash
node <team-ai>/dist/cli.js remap-namespaces --root . --mapping .team-ai/namespace-remap.yaml --out .team-ai/remap-proposal.yaml
```

Expected: `conflict 0`, and `remap` roughly equal to the number of docs (459 minus any already-correct).

- [ ] **Step 5: Commit**

```bash
git add catalog/namespaces/custom.yaml .team-ai/
git commit -m "feat(team-ai): add Arcwright namespace preset and remap mapping

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

## Task 8: Run the namespace migration

**Goal:** Rewrite `namespace` and `id` across the KB from five generic namespaces to fourteen Arcwright ones, after founder approval of the proposal.

> **USER-ORDERED GATE — NON-SKIPPABLE.** This task was requested by the user in the current conversation. It MUST NOT be closed by walking around it, by declaring it "verified inline", or by substituting a cheaper check. Close only after every item in `acceptanceCriteria` has been re-validated independently, with output captured.

**Files:**
- Create: `.team-ai/remap-proposal.yaml` (the reviewed artifact)
- Modify: ~459 files under `docs/` — front matter only

**Acceptance Criteria:**
- [ ] The proposal is presented to the founder in plain language and explicitly approved **before** `--apply` runs
- [ ] After apply, `git diff` shows changes only on `namespace:` and `id:` lines — zero body lines changed
- [ ] `node <team-ai>/dist/cli.js validate-kb --root .` passes
- [ ] `node <team-ai>/dist/cli.js validate-citations --root .` passes, proving no cross-reference broke
- [ ] Re-running the remap reports `remap 0` (idempotent)
- [ ] No file outside `docs/` is modified

**Verify:** `git diff --stat && git diff -U0 -- docs/ | grep '^[+-]' | grep -v '^[+-][+-]' | grep -vE '^[+-](namespace|id):' | head` → the final grep prints nothing

**Steps:**

- [ ] **Step 1: Generate the proposal**

```bash
node <team-ai>/dist/cli.js remap-namespaces --root . --mapping .team-ai/namespace-remap.yaml --out .team-ai/remap-proposal.yaml
```

- [ ] **Step 2: Summarise it for the founder — STOP HERE**

Produce a plain-language summary: how many files move to each new namespace, and the full list of any file whose destination was a judgement call. Present it and **wait for explicit approval**. Do not proceed on silence.

- [ ] **Step 3: Apply only after approval**

```bash
node <team-ai>/dist/cli.js remap-namespaces --root . --mapping .team-ai/namespace-remap.yaml --out .team-ai/remap-proposal.yaml --apply
```

- [ ] **Step 4: Prove only the two lines changed**

```bash
git diff -U0 -- docs/ | grep '^[+-]' | grep -v '^[+-][+-]' | grep -vE '^[+-](namespace|id):'
```

Expected: no output. Any line printed is a body change and must be investigated before committing.

- [ ] **Step 5: Validate**

```bash
node <team-ai>/dist/cli.js validate-kb --root .
node <team-ai>/dist/cli.js validate-citations --root .
```

Both expected to exit 0.

- [ ] **Step 6: Commit**

```bash
git add docs/ .team-ai/remap-proposal.yaml
git commit -m "refactor(kb): migrate to 14 Arcwright namespaces

Rewrites namespace and id front-matter values only; no body content
changed. Proposal reviewed and approved before apply.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

```json:metadata
{"userGate": true, "tags": ["user-gate"], "files": [".team-ai/remap-proposal.yaml", "docs/"], "verifyCommand": "git diff -U0 -- docs/ | grep '^[+-]' | grep -v '^[+-][+-]' | grep -vE '^[+-](namespace|id):'", "acceptanceCriteria": ["founder approved the proposal before apply", "git diff shows only namespace: and id: line changes", "validate-kb exits 0", "validate-citations exits 0", "re-running reports remap 0"], "gateScope": "all", "modelTier": "standard"}
```

---

## Task 9: Generate the agent topology

**Goal:** Produce one router, three group SMEs, and thirteen specialists, plus their instruction files and the four base skills — without touching any hand-authored file.

**Files:**
- Create: `agents/*.yaml`, `agents/*.md` (17 pairs)
- Create: `skills/kb-answer/`, `skills/kb-contribute/`, `skills/sme-route/`, `skills/audit-summary/`
- Create: `personas/*.md`

**Acceptance Criteria:**
- [ ] 17 agent YAML files exist and each validates against `agent.schema.json`
- [ ] The router has `model_tier: none` and `kind: router`
- [ ] All thirteen specialists have `max_hops: 0` and exactly one entry in `kb_namespaces`
- [ ] No two specialists share a `kb_namespace`
- [ ] Nothing under `docs/agents/` or `docs/skills/` is modified — `git status` shows them clean
- [ ] Any collision produced a `.team-ai-new` sibling rather than an overwrite

**Verify:** `node <team-ai>/dist/cli.js doctor --root .` → exits 0

**Steps:**

- [ ] **Step 1: Generate**

```bash
node <team-ai>/dist/cli.js init --dir . --answers .team-ai/answers.yaml --on-conflict siblings
```

- [ ] **Step 2: Confirm hand-authored content is untouched**

```bash
git status --porcelain docs/agents docs/skills
```

Expected: no output. If anything appears, stop — D1 says these are never regenerated.

- [ ] **Step 3: Check for collision siblings**

```bash
git status --porcelain | grep 'team-ai-new' || echo "no collisions"
```

Any sibling must be reviewed and either merged by hand or deleted; never blindly copied over the original.

- [ ] **Step 4: Assert the topology invariants**

```bash
for f in agents/*-sme.yaml; do
  echo "$f: $(grep -E '^(max_hops|kb_namespaces|model_tier):' "$f" | tr '\n' ' ')"
done
```

Expected: every specialist shows `max_hops: 0` with a single-entry `kb_namespaces`. Confirm no namespace appears twice:

```bash
grep -h 'kb_namespaces:' agents/*-sme.yaml | sort | uniq -d
```

Expected: no output.

- [ ] **Step 5: Commit**

```bash
git add agents/ skills/ personas/ team-profile.yaml index.lock
git commit -m "feat(agents): generate three-tier agent topology

One deterministic router, three group SMEs, thirteen terminal specialists.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

## Task 10: Author the manifest fragment and assemble

**Goal:** The manifest describes all fourteen domains, all seventeen generated agents, the four generated skills, and the existing hand-authored agents and skills registered as `source: authored`.

**Files:**
- Modify: `agents/manifest.fragment.yaml`
- Create: `manifest.yaml` (generated)

**Acceptance Criteria:**
- [ ] Fourteen domains, each with `group`, `authority`, `not_owned`, `owner: Nico Janssen`
- [ ] `nightcap` is `authority: canonical`; `monster-rpg` and `daily-case` are `provisional`; `nightcap-couch-race` is `archived` with `subagent: title-sme`
- [ ] Every existing file in `docs/agents/` and `docs/skills/` appears in `agents` or `skills` with `source: authored` and a `path`
- [ ] `assemble-manifest` exits 0 and `manifest.yaml` validates
- [ ] Every domain's `subagent` names an agent present in the `agents` section

**Verify:** `node <team-ai>/dist/cli.js assemble-manifest --root .` → exits 0

**Steps:**

- [ ] **Step 1: Write the fragment**

Edit `agents/manifest.fragment.yaml`. One domain entry per namespace. Example showing every required field:

```yaml
domains:
  - id: knowledge-graph
    description: "Who knows what, when they learned it, and from whom; knowledge-state queries."
    keywords: [knowledge state, knows, learned, epistemic, knowledge graph]
    not_owned: [character personality, arc transitions]
    kb_namespace: knowledge-graph
    subagent: knowledge-graph-sme
    group: engine
    authority: canonical
    depends_on: [arc-execution, character-behavior]
    model_tier: small
    owner: Nico Janssen
    escalate_to: engine-sme

  - id: nightcap
    description: "Nightcap's canonical narrative, backed by the Master GDD."
    keywords: [nightcap, murder mystery, gdd, case, suspect]
    not_owned: [monster rpg, daily case]
    kb_namespace: nightcap
    subagent: nightcap-sme
    group: title
    authority: canonical
    model_tier: small
    owner: Nico Janssen
    escalate_to: title-sme

  - id: monster-rpg
    description: "Monster RPG — placeholder story bible only, pending a real GDD."
    keywords: [monster rpg, monster]
    not_owned: [nightcap]
    kb_namespace: monster-rpg
    subagent: monster-rpg-sme
    group: title
    authority: provisional
    model_tier: small
    owner: Nico Janssen
    escalate_to: title-sme

  - id: nightcap-couch-race
    description: "Archived Couch Race variant. Answers explain it is superseded."
    keywords: [couch race]
    not_owned: [nightcap murder mystery]
    kb_namespace: nightcap-couch-race
    subagent: title-sme
    group: title
    authority: archived
    model_tier: small
    owner: Nico Janssen
```

Repeat for the remaining ten domains. `daily-case` mirrors `monster-rpg`. The six other engine domains mirror `knowledge-graph` with their own keywords and `not_owned`. `product-roadmap`, `engineering-practice`, and `playtest-ops` use `group: practice` and `escalate_to: practice-sme`.

- [ ] **Step 2: Register the agents**

```yaml
agents:
  - name: sme
    tier: 1
    kind: router
    max_hops: 2
    kb_namespaces: []
    skills: [sme-route]
    source: generated
  - name: engine-sme
    tier: 2
    kind: subagent
    group: engine
    max_hops: 1
    kb_namespaces: [arc-execution, knowledge-graph, character-behavior, model-routing, session-runtime, safety, developer-api]
    skills: [kb-answer]
    source: generated
  - name: knowledge-graph-sme
    tier: 3
    kind: subagent
    group: engine
    max_hops: 0
    kb_namespaces: [knowledge-graph]
    skills: [kb-answer, kb-contribute]
    escalate_to: engine-sme
    source: generated
```

Continue for `title-sme`, `practice-sme`, and the remaining specialists. Then register the existing hand-authored agents (D1) — one entry each for every file in `docs/agents/`:

```yaml
  - name: product-steward
    tier: 2
    kind: persona
    max_hops: 1
    kb_namespaces: [product-roadmap]
    source: authored
```

- [ ] **Step 3: Register the skills**

```yaml
skills:
  - id: kb-answer
    description: "Answer strictly from retrieved KB chunks, with citations."
    deterministic: false
    used_by: [engine-sme, title-sme, practice-sme]
    source: generated
  - id: arcwright-sme
    description: "Existing Arcwright SME skill."
    deterministic: false
    path: docs/skills/arcwright-sme/SKILL.md
    source: authored
```

One `source: authored` entry per directory under `docs/skills/`. Enumerate them:

```bash
ls -d docs/skills/*/
```

- [ ] **Step 4: Assemble and validate**

```bash
node <team-ai>/dist/cli.js assemble-manifest --root .
```

Expected: exit 0, `manifest.yaml` written.

- [ ] **Step 5: Check every subagent reference resolves**

```bash
node -e "
const y=require('yaml');const fs=require('fs');
const m=y.parse(fs.readFileSync('manifest.yaml','utf8'));
const names=new Set((m.agents||[]).map(a=>a.name));
const bad=(m.domains||[]).filter(d=>!names.has(d.subagent));
console.log(bad.length?'UNRESOLVED: '+bad.map(d=>d.id+'->'+d.subagent).join(', '):'all subagent refs resolve');
"
```

Expected: `all subagent refs resolve`.

- [ ] **Step 6: Commit**

```bash
git add agents/manifest.fragment.yaml manifest.yaml
git commit -m "feat(manifest): describe 14 domains, 17 agents and registered skills

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

## Task 11: Verify end to end and open the PR

**Goal:** Prove the whole Phase A result is coherent and non-destructive, then hand it to the founder as one reviewable PR.

**Files:** none created — verification and PR only

**Acceptance Criteria:**
- [ ] `validate-kb`, `validate-citations`, and `doctor` all exit 0
- [ ] `git diff --stat origin/main` shows no changes under `engine/`, `api/`, `sdk/`, or `dashboard/`
- [ ] `docs/agents/` and `docs/skills/` contain no modified files
- [ ] No `.team-ai-new` sibling remains uncommitted or unresolved
- [ ] The PR body states the namespace migration is included and that `id` values changed

**Verify:** `git diff --stat origin/main -- engine api sdk dashboard` → prints nothing

**Steps:**

- [ ] **Step 1: Run the full validation set**

```bash
node <team-ai>/dist/cli.js validate-kb --root .
node <team-ai>/dist/cli.js validate-citations --root .
node <team-ai>/dist/cli.js doctor --root .
```

All expected to exit 0.

- [ ] **Step 2: Prove runtime code is untouched**

```bash
git diff --stat origin/main -- engine api sdk dashboard
```

Expected: no output.

- [ ] **Step 3: Confirm no unresolved siblings**

```bash
find . -name '*.team-ai-new' -not -path './node_modules/*'
```

Expected: no output.

- [ ] **Step 4: Open the PR**

```bash
git push -u origin claude/team-ai-agent-topology
gh pr create --repo nickejanssen/arcwright --base main \
  --title "feat(agents): three-tier agent topology and namespace migration" \
  --body "Implements Phase A of docs/specs/0089-team-ai-agent-architecture.md.

## What changed
- **Namespace migration**: KB moves from 5 generic namespaces to 14 Arcwright domains. Rewrites \`namespace\` and \`id\` front matter on ~459 docs. No body content changed.
- **Agent topology**: 1 deterministic router (\`model_tier: none\`), 3 group SMEs, 13 terminal specialists (\`max_hops: 0\`, one namespace each).
- **Manifest**: 14 domains with group/authority/not_owned/depends_on, 17 agents, and existing hand-authored agents and skills registered as \`source: authored\`.

## Not included
Enforcement skills, hooks, workflows, golden questions (Phase B) and the temporal graph plus semantic retrieval (Phase C).

## Test plan
- [x] validate-kb, validate-citations, doctor all exit 0
- [x] diff confined to docs/, agents/, skills/, personas/, manifest
- [x] no changes under engine/, api/, sdk/, dashboard/
- [x] docs/agents/ and docs/skills/ untouched

🤖 Generated with [Claude Code](https://claude.com/claude-code)"
```

---

## Dependencies

```
Task 1 → Task 2 → Task 6
Task 3 → Task 6
Task 4 → Task 6
Task 5 → Task 6
Task 6 → Task 7 → Task 8 → Task 9 → Task 10 → Task 11
```

Tasks 1, 3, 4, and 5 are independent of each other and can run in parallel. Everything from Task 7 onward is strictly sequential.
