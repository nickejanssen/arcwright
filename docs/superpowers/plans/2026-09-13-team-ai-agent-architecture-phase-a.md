---
id: engineeringpractice.superpowers.plans.2026-09-13-team-ai-agent-architecture-phase-a
namespace: engineering-practice
title: team-ai Agent Architecture — Phase A Implementation Plan
owner: Nico Janssen
status: draft
review_by: "2027-03-12"
sensitivity: internal
source: authored
tags: []
supersedes: []
---

# team-ai Agent Architecture — Phase A Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers-extended-cc:subagent-driven-development (recommended) or superpowers-extended-cc:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generate the three-tier agent topology into Arcwright — one router, three hand-authored group SMEs, thirteen generated specialists — emit them as usable Claude Code subagents, and migrate the KB from seven namespace values to fourteen Arcwright namespaces.

**Architecture:** Eleven framework tasks land in team-ai first and ship as 0.4.0. Arcwright then records the approved `.claude` exception, verifies the recorded decisions, runs a conflict-safe migration, generates into `team-ai/`, and emits committed subagents that search the KB with Claude Code's built-in file tools.

**Tech Stack:** TypeScript / Node 22 / ESM, Vitest, Ajv (JSON Schema 2020-12), Handlebars templates, `yaml`, GitHub Actions.

**User decisions (already made):**
- "Design all 3, build in order" — this plan is Phase A only.
- Domain shape: "It is 1, 2, and 3" — three tiers, 13 specialists, titles split per game.
- "Approve spec" — design approval of spec version 1.0 at commit `f11398e`. It authorizes planning, not the migration.
- Group SMEs: "Hand-author and register" (spec D5).
- Layout: "Approve, with .claude exception" — tracked source in `team-ai/`, gitignored state in `.team-ai/`, emitted subagents in `.claude/agents/team-ai-*.md` only.
- "Add semantic retrieval to this build" — Phase C, not here.

- D1 (2026-09-13): register, never regenerate, existing agents and skills.
- D2 (2026-09-13): archived Couch Race domain served by `title-sme`.
- D3 (2026-09-13): the founder is owner on every domain.
- D6 (2026-09-13): agents search the KB with Claude Code's built-in `Read`, `Grep`, `Glob` — no MCP server, no `.mcp.json`, no new dependency.

**Spec:** [`docs/specs/0089-team-ai-agent-architecture.md`](../../specs/0089-team-ai-agent-architecture.md) version 1.2. Its *Review Resolution* table maps every adversarial-review finding to the task below that resolves it.

**Framework design note (read before Tasks 1–11):** team-ai `docs/design/2026-09-13-agent-topology-design.md`. Nothing Arcwright-specific may enter team-ai; `node dist/cli.js check-agnostic` enforces that for shipped source (it deliberately does not scan docs, tests, or fixtures).

**Commit messages.** Commands below show the subject and body only. Add whatever attribution trailer your session requires when you commit; this document omits them because `docs/README.md` forbids model names and provider strings in docs.

---

## Repos and prerequisites

| Repo | Path | Branch | Tasks |
|---|---|---|---|
| team-ai | `C:/Users/nicke/OneDrive/Desktop/team-ai` | `feat/agent-topology-phase-a` off `main` | 1–11 |
| arcwright | a fresh worktree off `main` | `claude/team-ai-agent-topology` | 12–19 |

**Before Task 1:** team-ai PR #4 (install without `npx`) and PR #5 (path containment) must be merged. Confirm:

```bash
gh pr view 4 --repo nickejanssen/team-ai --json state -q .state
```

```bash
gh pr view 5 --repo nickejanssen/team-ai --json state -q .state
```

Both must print `MERGED`. If not, stop and ask the founder.

**In Arcwright tasks,** `$CLI` means the absolute path to the team-ai 0.4.0 build's `dist/cli.js`, e.g. `C:/Users/nicke/OneDrive/Desktop/team-ai/dist/cli.js`. Never run `npx team-ai`: the `team-ai` name on npm belongs to an unrelated package.

---

## File Structure

**team-ai — modified**

| File | Responsibility |
|---|---|
| `schemas/manifest.schema.json`, `src/schema/types.ts` | Domain fields; `agents` and `skills` sections |
| `src/manifest/assemble.ts` | Pass-through and ordering for the new fields |
| `src/generator/context.ts`, `src/generator/entity-files.ts` | Per-domain namespace |
| `src/interview/gates.ts`, `src/generator/init.ts`, `resume.ts`, `upgrade.ts`, `src/cli.ts` | Instance catalog option |
| `src/generator/init-answers.ts`, `src/interview/cli-runtime.ts` | Answers keyed by question id |
| `src/retrieval/index-lock.ts`, `src/kb/loader.ts`, `src/retrieval/factory.ts`, `src/retrieval/lexical.ts`, `src/commands/validate-kb.ts`, `src/commands/freshness-audit.ts` | KB root and exclusions; per-file parse failures |
| `src/emit/claude-code.ts`, `src/commands/emit.ts` | File prefix, plugin-manifest toggle, built-in search mode, tracked output |
| `templates/mcp-server/server.mjs.hbs`, `templates/instance/agents/_domain-sme.yaml.hbs` | No `npx`; Windows-safe root; only real tools |
| `.github/workflows/*.reusable.yml`, `templates/instance/.github/workflows/*.yml.hbs`, `src/ci-config.test.ts` | No `npx` in CI |

**team-ai — created**

| File | Responsibility |
|---|---|
| `src/manifest/invariants.ts`, `src/commands/validate-manifest.ts` | Topology invariants |
| `src/remap/plan.ts`, `src/remap/apply.ts`, `src/commands/remap-namespaces.ts` | Conflict-safe namespace migration |

**arcwright — created or modified**

| File | Responsibility |
|---|---|
| `AGENTS.md`, `.github/copilot-instructions.md` | The founder-approved `.claude` exception |
| `team-ai/catalog/namespaces/custom.yaml` | The 14 namespaces |
| `team-ai/answers.yaml` | Interview answers keyed by question id |
| `team-ai/index.lock` | Lexical driver plus KB root `../docs` and exclusions |
| `team-ai/namespace-remap.yaml`, `team-ai/inventory.txt`, `team-ai/remap-proposal.yaml` | Migration inputs and reviewed outputs |
| `team-ai/agents/*` | 14 generated and 3 hand-authored agents, manifest fragment |
| `team-ai/manifest.yaml` | Assembled manifest |
| `.claude/agents/team-ai-*.md` | 17 emitted subagents |
| `.github/workflows/team-ai.yml` | Validation, drift, and migration checks in CI |
| `.gitignore` | `.team-ai/` |
| `docs/**` | `namespace:` and `id:` lines only |

---

## Task 1: Manifest schema — domain fields, agents, skills

**Goal:** The manifest accepts `group`, `authority`, `not_owned`, `depends_on` on domains and optional `agents` and `skills` sections, and `assembleManifest` round-trips them.

**Files:**
- Modify: `schemas/manifest.schema.json`, `src/schema/types.ts`, `src/manifest/assemble.ts`
- Test: `src/schema/validate.test.ts`, `src/manifest/assemble.test.ts`

**Acceptance Criteria:**
- [ ] A domain with all four new fields validates; one with none still validates
- [ ] `authority` outside `canonical|provisional|archived` is rejected
- [ ] A manifest with `agents` and `skills` validates; one without them still validates
- [ ] `assembleManifest` passes both sections through, sorting agents by `name` and skills by `id`
- [ ] `serializeManifest` emits `domains`, then `agents`, then `skills`

**Verify:** `npx vitest run src/schema/ src/manifest/` → all pass

**Steps:**

- [ ] **Step 1: Write the failing tests.** Append to `src/schema/validate.test.ts`:

```typescript
describe("manifest — topology fields", () => {
  const domain = {
    id: "knowledge-graph",
    description: "Who knows what, when, and from whom.",
    keywords: ["knowledge state"],
    kb_namespace: "knowledge-graph",
    subagent: "knowledge-graph-sme",
    model_tier: "small",
    owner: "owner-a",
  };

  it("accepts group, authority, not_owned and depends_on", () => {
    const result = validate("manifest", {
      domains: [
        {
          ...domain,
          group: "engine",
          authority: "canonical",
          not_owned: ["character personality"],
          depends_on: ["arc-execution"],
        },
      ],
    });
    expect(result.ok).toBe(true);
  });

  it("rejects an authority outside the enum", () => {
    expect(validate("manifest", { domains: [{ ...domain, authority: "definitive" }] }).ok).toBe(
      false,
    );
  });

  it("accepts agents and skills sections, and still accepts neither", () => {
    expect(
      validate("manifest", {
        domains: [domain],
        agents: [
          { name: "sme", tier: 1, kind: "router", max_hops: 2, kb_namespaces: [], source: "generated" },
        ],
        skills: [{ id: "freshness-sweep", deterministic: true, script: "scripts/freshness" }],
      }).ok,
    ).toBe(true);
    expect(validate("manifest", { domains: [domain] }).ok).toBe(true);
  });
});
```

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
    owner: "owner-a",
  };

  it("passes agents and skills through, sorted", () => {
    const result = assembleManifest({
      fragment: {
        domains: [domain],
        agents: [
          { name: "safety-sme", tier: 3, kind: "subagent", max_hops: 0, kb_namespaces: ["safety"] },
          { name: "sme", tier: 1, kind: "router", max_hops: 2, kb_namespaces: [] },
        ],
        skills: [
          { id: "kb-contribute", deterministic: false },
          { id: "kb-answer", deterministic: false },
        ],
      },
      spokes: [],
    });
    expect(result.agents?.map((a) => a.name)).toEqual(["safety-sme", "sme"]);
    expect(result.skills?.map((s) => s.id)).toEqual(["kb-answer", "kb-contribute"]);
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

- [ ] **Step 2: Run to confirm failure.** `npx vitest run src/schema/ src/manifest/` → the new tests FAIL on `additionalProperties`.

- [ ] **Step 3: Extend the schema.** In `schemas/manifest.schema.json`, add to `$defs.manifestDomain.properties`:

```json
        "group": { "type": "string" },
        "authority": { "type": "string", "enum": ["canonical", "provisional", "archived"] },
        "not_owned": { "type": "array", "items": { "type": "string" } },
        "depends_on": { "type": "array", "items": { "type": "string" } }
```

Add to top-level `properties`:

```json
    "agents": { "type": "array", "items": { "$ref": "#/$defs/manifestAgent" } },
    "skills": { "type": "array", "items": { "$ref": "#/$defs/manifestSkill" } }
```

Add to `$defs`:

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
        "source": { "type": "string", "enum": ["generated", "authored"] },
        "path": { "type": "string" }
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

- [ ] **Step 4: Mirror in TypeScript.** In `src/schema/types.ts`, replace `ManifestDomain` and `Manifest`:

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
  path?: string;
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

- [ ] **Step 5: Pass the sections through.** In `src/manifest/assemble.ts`, import `ManifestAgent` and `ManifestSkill` alongside the existing types, and add after `stringOr`:

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

Replace the end of `assembleManifest` (from `const domains = collected.sort` to the final `return`) with:

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

Append `"group", "authority", "not_owned", "depends_on"` to `DOMAIN_KEY_ORDER`, and replace `serializeManifest`:

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

- [ ] **Step 6: Run and commit.** `npx vitest run src/schema/ src/manifest/` → PASS.

```bash
git add schemas/manifest.schema.json src/schema/types.ts src/manifest/ src/schema/validate.test.ts
git commit -m "feat(manifest): add topology fields and agents/skills sections"
```

---

## Task 2: `team-ai validate-manifest` — enforce topology invariants

**Goal:** A deterministic command that fails when the router, specialist, namespace, or reference invariants are broken, so the topology's properties are checked in CI rather than merely declared.

**Files:**
- Create: `src/manifest/invariants.ts`, `src/manifest/invariants.test.ts`, `src/commands/validate-manifest.ts`
- Modify: `src/cli.ts`

**Acceptance Criteria:**
- [ ] Fails unless exactly one agent has `kind: router`, and that agent's definition has `model_tier: none`
- [ ] Fails when a tier-3 agent has `max_hops` ≠ 0 or `kb_namespaces` length ≠ 1
- [ ] Fails when two tier-3 agents share a namespace
- [ ] Fails when a domain's `subagent` or any `escalate_to` (other than `unassigned`) names no manifest agent
- [ ] Fails when a manifest agent has no definition file, or its definition's `max_hops`/`kb_namespaces` disagree with the manifest
- [ ] Accepts an agent with `source: authored` and a `path` but no definition file: a registered contract is routable metadata, not an emitted subagent
- [ ] Passes a consistent manifest; a manifest without `agents` passes with a note

**Verify:** `npx vitest run src/manifest/invariants.test.ts` → all pass

**Steps:**

- [ ] **Step 1: Write the failing tests.** Create `src/manifest/invariants.test.ts`:

```typescript
import { describe, expect, it } from "vitest";

import type { AgentDef, Manifest } from "../schema/types.js";
import { checkManifestInvariants } from "./invariants.js";

function def(name: string, over: Partial<AgentDef> = {}): AgentDef {
  return {
    name,
    kind: "subagent",
    description: name,
    model_tier: "small",
    kb_namespaces: [name.replace(/-sme$/, "")],
    tools: [],
    max_hops: 0,
    instructions_file: `agents/${name}.md`,
    ...over,
  };
}

const base: Manifest = {
  domains: [
    {
      id: "safety",
      description: "d",
      keywords: [],
      kb_namespace: "safety",
      subagent: "safety-sme",
      model_tier: "small",
      owner: "o",
      escalate_to: "engine-sme",
    },
  ],
  agents: [
    { name: "sme", tier: 1, kind: "router", max_hops: 2, kb_namespaces: [] },
    { name: "engine-sme", tier: 2, kind: "subagent", group: "engine", max_hops: 1, kb_namespaces: ["safety"] },
    { name: "safety-sme", tier: 3, kind: "subagent", group: "engine", max_hops: 0, kb_namespaces: ["safety"] },
  ],
};

const defs = new Map<string, AgentDef>([
  ["sme", def("sme", { kind: "router", model_tier: "none", max_hops: 2, kb_namespaces: [] })],
  ["engine-sme", def("engine-sme", { max_hops: 1, kb_namespaces: ["safety"] })],
  ["safety-sme", def("safety-sme")],
]);

const rules = (m: Manifest, d = defs): string[] => checkManifestInvariants(m, d).map((v) => v.rule);

describe("checkManifestInvariants", () => {
  it("passes a consistent topology", () => {
    expect(rules(base)).toEqual([]);
  });

  it("requires the router definition to make no model call", () => {
    const d = new Map(defs);
    d.set("sme", def("sme", { kind: "router", model_tier: "small", max_hops: 2, kb_namespaces: [] }));
    expect(rules(base, d)).toContain("router-model-tier");
  });

  it("requires tier-3 agents to be terminal with one namespace", () => {
    const m: Manifest = {
      ...base,
      agents: base.agents!.map((a) => (a.tier === 3 ? { ...a, max_hops: 1 } : a)),
    };
    expect(rules(m)).toContain("specialist-terminal");
  });

  it("rejects two specialists sharing a namespace", () => {
    const m: Manifest = {
      ...base,
      agents: [
        ...base.agents!,
        { name: "other-sme", tier: 3, kind: "subagent", max_hops: 0, kb_namespaces: ["safety"] },
      ],
    };
    const d = new Map(defs);
    d.set("other-sme", def("other-sme", { kb_namespaces: ["safety"] }));
    expect(rules(m, d)).toContain("specialist-namespace-unique");
  });

  it("rejects unresolved subagent and escalate_to references", () => {
    const m: Manifest = {
      ...base,
      domains: [{ ...base.domains[0]!, subagent: "missing-sme", escalate_to: "nobody" }],
    };
    expect(rules(m)).toEqual(expect.arrayContaining(["domain-subagent", "escalate-to"]));
  });

  it("accepts a registered authored contract that has no definition file", () => {
    const m: Manifest = {
      ...base,
      agents: [
        ...base.agents!,
        { name: "planner", tier: 2, kind: "persona", max_hops: 0, kb_namespaces: [], source: "authored", path: "docs/agents/planner.md" },
      ],
    };
    expect(rules(m)).toEqual([]);
  });

  it("rejects a manifest agent whose definition disagrees", () => {
    const d = new Map(defs);
    d.set("safety-sme", def("safety-sme", { kb_namespaces: ["other"] }));
    expect(rules(base, d)).toContain("definition-mismatch");
  });
});
```

- [ ] **Step 2: Run to confirm failure.** `npx vitest run src/manifest/invariants.test.ts` → FAIL, module missing.

- [ ] **Step 3: Implement.** Create `src/manifest/invariants.ts`:

```typescript
// Deterministic. No model calls. No network.
//
// Checks the topology properties the manifest schema cannot express. team-ai has
// no agent runtime, so it cannot enforce hop limits while agents run; it can
// refuse to ship a configuration that violates them.

import type { AgentDef, Manifest } from "../schema/types.js";

export interface InvariantViolation {
  rule: string;
  subject: string;
  message: string;
}

const UNASSIGNED = "unassigned";

function sameList(a: string[], b: string[]): boolean {
  return a.length === b.length && a.every((value, i) => value === b[i]);
}

export function checkManifestInvariants(
  manifest: Manifest,
  definitions: Map<string, AgentDef>,
): InvariantViolation[] {
  const out: InvariantViolation[] = [];
  const agents = manifest.agents ?? [];
  if (agents.length === 0) return out;

  const names = new Set(agents.map((a) => a.name));
  const push = (rule: string, subject: string, message: string): void => {
    out.push({ rule, subject, message });
  };

  const routers = agents.filter((a) => a.kind === "router");
  if (routers.length !== 1) {
    push("one-router", "agents", `expected exactly one router, found ${routers.length}`);
  }
  for (const router of routers) {
    if (definitions.get(router.name)?.model_tier !== "none") {
      push("router-model-tier", router.name, "router definition must have model_tier: none");
    }
  }

  const specialistNamespaces = new Map<string, string>();
  for (const agent of agents.filter((a) => a.tier === 3)) {
    if (agent.max_hops !== 0 || agent.kb_namespaces.length !== 1) {
      push("specialist-terminal", agent.name, "tier-3 agents need max_hops 0 and exactly one namespace");
    }
    const ns = agent.kb_namespaces[0];
    if (ns !== undefined) {
      const owner = specialistNamespaces.get(ns);
      if (owner !== undefined) {
        push("specialist-namespace-unique", agent.name, `namespace '${ns}' is also owned by ${owner}`);
      } else {
        specialistNamespaces.set(ns, agent.name);
      }
    }
  }

  for (const domain of manifest.domains) {
    if (!names.has(domain.subagent)) {
      push("domain-subagent", domain.id, `subagent '${domain.subagent}' is not a manifest agent`);
    }
    if (domain.escalate_to !== undefined && domain.escalate_to !== UNASSIGNED && !names.has(domain.escalate_to)) {
      push("escalate-to", domain.id, `escalate_to '${domain.escalate_to}' is not a manifest agent`);
    }
  }

  for (const agent of agents) {
    if (agent.escalate_to !== undefined && agent.escalate_to !== UNASSIGNED && !names.has(agent.escalate_to)) {
      push("escalate-to", agent.name, `escalate_to '${agent.escalate_to}' is not a manifest agent`);
    }
    const definition = definitions.get(agent.name);
    if (definition === undefined) {
      // A registered authored contract (source: authored + path) is routable
      // metadata only; it has no definition and is never emitted.
      if (agent.source === "authored" && agent.path !== undefined) continue;
      push("definition-missing", agent.name, "no agents/<name>.yaml definition");
      continue;
    }
    if (definition.max_hops !== agent.max_hops || !sameList(definition.kb_namespaces, agent.kb_namespaces)) {
      push("definition-mismatch", agent.name, "definition max_hops or kb_namespaces disagree with the manifest");
    }
  }

  return out;
}
```

- [ ] **Step 4: Add the command.** Create `src/commands/validate-manifest.ts`:

```typescript
// Deterministic. No model calls. No network.

import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";

import { parse as parseYaml } from "yaml";

import { loadEmitInput } from "../emit/index.js";
import { checkManifestInvariants } from "../manifest/invariants.js";
import type { AgentDef } from "../schema/types.js";
import { validate } from "../schema/validate.js";

export interface ValidateManifestOptions {
  root?: string;
}

export async function run(opts: ValidateManifestOptions): Promise<number> {
  const root = opts.root ?? ".";
  const file = join(root, "manifest.yaml");
  if (!existsSync(file)) {
    console.error(`validate-manifest: no manifest.yaml under ${root}`);
    return 1;
  }
  const result = validate("manifest", parseYaml(readFileSync(file, "utf8")));
  if (!result.ok) {
    for (const error of result.errors) console.error(`manifest.yaml: ${error}`);
    return 1;
  }
  if ((result.value.agents ?? []).length === 0) {
    console.log("validate-manifest: OK (no agents section; topology invariants not checked)");
    return 0;
  }

  const input = await loadEmitInput(root);
  const definitions = new Map<string, AgentDef>(input.agents.map((a) => [a.def.name, a.def]));
  const violations = checkManifestInvariants(result.value, definitions);
  for (const v of violations) console.error(`${v.subject}: [${v.rule}] ${v.message}`);
  if (violations.length > 0) return 1;

  console.log(`validate-manifest: OK (${result.value.agents?.length ?? 0} agents)`);
  return 0;
}
```

Register it in `src/cli.ts` next to `validate-kb`, following the existing registration shape:

```typescript
  {
    name: "validate-manifest",
    description: "Check manifest topology invariants against agent definitions",
    configure: (command) => {
      command.option("--root <dir>", "instance root directory", ".");
    },
    run: validateManifest.run,
  },
```

with `import * as validateManifest from "./commands/validate-manifest.js";` alongside the other command imports.

- [ ] **Step 5: Run and commit.** `npx vitest run src/manifest/` → PASS.

```bash
git add src/manifest/invariants.ts src/manifest/invariants.test.ts src/commands/validate-manifest.ts src/cli.ts
git commit -m "feat(manifest): add validate-manifest for topology invariants"
```

---

## Task 3: Give each domain SME its own namespace

**Goal:** Stop scoping every generated domain SME to `namespaces[0]`, which would make all specialists read one namespace.

**Files:**
- Modify: `src/generator/context.ts` (domains mapping), `src/generator/entity-files.ts` (`asDomains`, domain loop)
- Test: `src/generator/entity-files.test.ts`

**Acceptance Criteria:**
- [ ] `buildContext` emits `namespace` on every domain; a slug matching a namespace owns it, otherwise it falls back to `namespaces[0]`
- [ ] Two domains with different namespaces produce SME YAMLs with different `kb_namespaces`
- [ ] Existing generator tests still pass

**Verify:** `npx vitest run src/generator/` → all pass

**Steps:**

- [ ] **Step 1: Write the failing test.** Append to `src/generator/entity-files.test.ts` (created by team-ai PR #5, which provides `tmp()` and `emptyResult()`):

```typescript
describe("renderEntityFiles — per-domain namespace", () => {
  it("scopes each domain SME to its own namespace", () => {
    const dir = tmp();
    renderEntityFiles(
      {
        namespaces: ["alpha", "beta"],
        domains: [
          { slug: "alpha", name: "Alpha", namespace: "alpha" },
          { slug: "beta", name: "Beta", namespace: "beta" },
        ],
        roles: [],
        personas: [],
      },
      dir,
      new Map(),
      "siblings",
      emptyResult(),
    );
    expect(readFileSync(join(dir, "agents/alpha-sme.yaml"), "utf8")).toContain("kb_namespaces: [alpha]");
    expect(readFileSync(join(dir, "agents/beta-sme.yaml"), "utf8")).toContain("kb_namespaces: [beta]");
  });
});
```

Add `readFileSync` to that file's `node:fs` import.

- [ ] **Step 2: Run to confirm failure.** `npx vitest run src/generator/entity-files.test.ts` → FAIL: both files show `[alpha]`.

- [ ] **Step 3: Carry the namespace through the context.** In `src/generator/context.ts`:

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
    return { slug: s, name: d, namespace: namespaces.includes(s) ? s : (namespaces[0] ?? "operating") };
  });
```

- [ ] **Step 4: Use it in the renderer.** In `src/generator/entity-files.ts`:

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

In the domain loop, replace `namespace: firstNamespace,` with `namespace: domain.namespace ?? firstNamespace,`.

- [ ] **Step 5: Run and commit.** `npx vitest run src/generator/` → PASS.

```bash
git add src/generator/context.ts src/generator/entity-files.ts src/generator/entity-files.test.ts
git commit -m "fix(generator): scope each domain SME to its own namespace"
```

---

## Task 4: Instance catalog through `init`, `resume`, `upgrade`

**Goal:** A repo-supplied catalog directory is layered over the framework catalog on every generation path, so an instance preset named `custom.yaml` actually resolves.

**Why required:** `kb.namespaces` is a `single_select`; the engine throws on any value outside its options, so `custom` is the only answer that can name a repo preset. Today `loadCatalog()` wires only the toolkit layer, and `init.ts:137`, `resume.ts:148`, and `upgrade.ts:88` all call `buildContext(engine)` with no catalog directory, so `custom` silently falls back to the five default namespaces.

**Files:**
- Modify: `src/interview/gates.ts`, `src/generator/context.ts`, `src/generator/init.ts`, `src/generator/resume.ts`, `src/generator/upgrade.ts`, `src/cli.ts`
- Test: `src/catalog/resolve.test.ts`, `src/generator/init.test.ts`

**Acceptance Criteria:**
- [ ] `loadCatalog(dir)` finds a preset defined only in `dir`, keyed by filename stem
- [ ] `loadCatalog()` with no argument is unchanged; a missing directory is ignored
- [ ] `init`, `resume`, and `upgrade` accept `--catalog <dir>` and pass it to `buildContext`
- [ ] Running `init` with `kb.namespaces: custom` and a catalog holding `namespaces/custom.yaml` generates domain SMEs scoped to that preset's namespaces

**Verify:** `npx vitest run src/catalog/ src/generator/` → all pass

**Steps:**

- [ ] **Step 1: Write the failing unit test.** Append to `src/catalog/resolve.test.ts`:

```typescript
describe("loadCatalog with an instance layer", () => {
  it("resolves a preset that exists only in the instance catalog, keyed by filename stem", () => {
    const dir = mkdtempSync(join(tmpdir(), "team-ai-cat-"));
    mkdirSync(join(dir, "namespaces"), { recursive: true });
    const seeds = ["a", "b", "c", "d", "e"]
      .map((n) => `  - path: ${n}.md\n    title: ${n}\n    purpose: seed ${n}`)
      .join("\n");
    writeFileSync(
      join(dir, "namespaces", "custom.yaml"),
      `name: named-differently\ndescription: x\nsecond_level:\n  - alpha\n  - beta\ndomain_dir: null\nseed_docs:\n${seeds}\n`,
      "utf8",
    );
    const catalog = loadCatalog(dir);
    expect(catalog?.namespaces.get("custom")?.value.second_level).toEqual(["alpha", "beta"]);
    expect(catalog?.namespaces.get("named-differently")).toBeUndefined();
    rmSync(dir, { recursive: true, force: true });
  });

  it("ignores a missing instance directory", () => {
    expect(loadCatalog(join(tmpdir(), "team-ai-no-such-catalog"))).not.toBeNull();
  });
});
```

Import `loadCatalog` from `../interview/gates.js` and `mkdirSync`, `mkdtempSync`, `rmSync`, `writeFileSync` from `node:fs` if not already imported.

- [ ] **Step 2: Run to confirm failure.** `npx vitest run src/catalog/resolve.test.ts` → FAIL.

- [ ] **Step 3: Wire the layer.** In `src/interview/gates.ts`:

```typescript
export function loadCatalog(instanceDir?: string): ResolvedCatalog | null {
  try {
    return resolveCatalog(
      instanceDir === undefined ? { toolkitDir: CATALOG_DIR } : { toolkitDir: CATALOG_DIR, instanceDir },
    );
  } catch {
    return null;
  }
}
```

In `src/generator/context.ts`, replace `const catalog = loadCatalog();` with:

```typescript
  const catalogDir = typeof extra.instanceCatalogDir === "string" ? extra.instanceCatalogDir : undefined;
  const catalog = loadCatalog(catalogDir);
```

- [ ] **Step 4: Thread the option.** Add `catalog?: string;` to `InitOptions` in `init.ts`, to resume's options interface in `resume.ts`, and to upgrade's options interface in `upgrade.ts`. At each of the three `buildContext(engine)` calls use:

```typescript
  const context = buildContext(engine, opts.catalog !== undefined ? { instanceCatalogDir: opts.catalog } : {});
```

In `init.ts`, where it delegates to `resume.run`, also copy `catalog` into `resumeOpts`. In `src/cli.ts`, add to the `configure` of `init`, `resume`, and `upgrade`:

```typescript
        .option("--catalog <dir>", "instance catalog directory layered over the framework catalog")
```

- [ ] **Step 5: Add the end-to-end test.** In `src/generator/init.test.ts`, copy the existing test "runs the interview and generates a working instance into an empty dir". In the copy: set the `kb.namespaces` answer to `custom` and `agents.domains` to `alpha, beta`; create `<dir>/cat/namespaces/custom.yaml` with the preset from Step 1; pass `catalog: join(dir, "cat")` to `init.run`; then assert:

```typescript
    expect(readFileSync(join(dir, "agents", "alpha-sme.yaml"), "utf8")).toContain("kb_namespaces: [alpha]");
    expect(readFileSync(join(dir, "agents", "beta-sme.yaml"), "utf8")).toContain("kb_namespaces: [beta]");
```

- [ ] **Step 6: Run and commit.** `npx vitest run src/catalog/ src/generator/` → PASS.

```bash
git add src/interview/gates.ts src/generator/ src/catalog/resolve.test.ts src/cli.ts
git commit -m "feat(catalog): layer an instance catalog through init, resume and upgrade"
```

---

## Task 5: Answers keyed by question id

**Goal:** Replace fragile positional replay with an answers file keyed by question id, so a changed question bank produces a loud error rather than a silently misconfigured setting.

**Files:**
- Modify: `src/generator/init-answers.ts`, `src/interview/cli-runtime.ts`, `src/generator/init.ts`, `src/generator/resume.ts`
- Test: `src/generator/init-answers.test.ts`

**Acceptance Criteria:**
- [ ] A YAML mapping is read as keyed answers; a YAML list still works positionally
- [ ] Keys are question ids, plus `gate.1`, `gate.2`, `gate.3` for the confirmation gates
- [ ] Requesting a key with no entry rejects with an error naming the key
- [ ] Requesting the same key twice in a row rejects — an answer the engine refused cannot loop forever
- [ ] Array values are joined with `,` for multi-select questions
- [ ] Control words `why`, `back`, `save` are rejected when the file is loaded
- [ ] After the run, entries never requested are reported as a warning, not an error, because pre-filled and `ask_if`-skipped questions are legitimately not asked

**Verify:** `npx vitest run src/generator/init-answers.test.ts src/interview/` → all pass

**Steps:**

- [ ] **Step 1: Write the failing tests.** Create `src/generator/init-answers.test.ts`:

```typescript
import { mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { afterEach, describe, expect, it } from "vitest";

import { loadAnswerFile } from "./init-answers.js";

const dirs: string[] = [];

function file(content: string): string {
  const dir = mkdtempSync(join(tmpdir(), "team-ai-answers-"));
  dirs.push(dir);
  const path = join(dir, "answers.yaml");
  writeFileSync(path, content, "utf8");
  return path;
}

afterEach(() => {
  for (const dir of dirs.splice(0)) rmSync(dir, { recursive: true, force: true });
});

describe("loadAnswerFile — keyed", () => {
  it("answers by key in any order and joins arrays", async () => {
    const answers = loadAnswerFile(file("team.name: Acme\nagents.personas: [a, b]\ngate.1: confirm\n"));
    expect(await answers.pull("gate.1")).toBe("confirm");
    expect(await answers.pull("agents.personas")).toBe("a,b");
    expect(await answers.pull("team.name")).toBe("Acme");
  });

  it("rejects a key with no entry, naming it", async () => {
    const answers = loadAnswerFile(file("team.name: Acme\n"));
    await expect(answers.pull("team.size")).rejects.toThrow(/team\.size/);
  });

  it("rejects a repeated request for the same key", async () => {
    const answers = loadAnswerFile(file("team.size: nonsense\n"));
    await answers.pull("team.size");
    await expect(answers.pull("team.size")).rejects.toThrow(/not accepted/);
  });

  it("rejects control words at load time", () => {
    expect(() => loadAnswerFile(file("team.name: back\n"))).toThrow(/control word/);
  });

  it("reports entries that were never requested", async () => {
    const answers = loadAnswerFile(file("team.name: Acme\nunused.key: x\n"));
    await answers.pull("team.name");
    expect(answers.unusedKeys()).toEqual(["unused.key"]);
  });
});

describe("loadAnswerFile — positional", () => {
  it("still replays a list in order", async () => {
    const answers = loadAnswerFile(file("- one\n- two\n"));
    expect(await answers.pull("anything")).toBe("one");
    expect(await answers.pull("anything")).toBe("two");
  });
});
```

- [ ] **Step 2: Run to confirm failure.** `npx vitest run src/generator/init-answers.test.ts` → FAIL.

- [ ] **Step 3: Implement the loader.** Replace `src/generator/init-answers.ts` with:

```typescript
// Deterministic. No model calls. No network. One disk read at construction time.
//
// Backs `team-ai init --answers <file>`. A YAML mapping is keyed by question id
// (plus `gate.1`–`gate.3`), which survives question-bank changes: a missing key
// fails loudly instead of shifting every later answer. A YAML list is the legacy
// positional form.

import { readFileSync } from "node:fs";

import { parse as parseYaml } from "yaml";

export type AnswerSource = (key: string) => Promise<string>;

export interface LoadedAnswers {
  pull: AnswerSource;
  unusedKeys: () => string[];
}

const CONTROL_WORDS = new Set(["why", "back", "save"]);

function coerce(value: unknown, where: string): string {
  if (typeof value === "string") return value;
  if (typeof value === "number" || typeof value === "boolean") return String(value);
  if (Array.isArray(value)) return value.map((v) => coerce(v, where)).join(",");
  throw new Error(`${where}: every answer must be a string, number, boolean, or list of them`);
}

export function loadAnswerFile(path: string): LoadedAnswers {
  let parsed: unknown;
  try {
    parsed = parseYaml(readFileSync(path, "utf8"));
  } catch (err) {
    throw new Error(`${path}: not valid YAML — ${err instanceof Error ? err.message : String(err)}`);
  }

  if (Array.isArray(parsed)) {
    const entries = parsed.map((entry, i) => coerce(entry, `${path} entry ${i}`));
    let index = 0;
    return {
      pull: () => {
        if (index >= entries.length) {
          return Promise.reject(new Error(`answer file exhausted: ${path} has ${entries.length} entries`));
        }
        const next = entries[index] ?? "";
        index += 1;
        return Promise.resolve(next);
      },
      unusedKeys: () => [],
    };
  }

  if (parsed === null || typeof parsed !== "object") {
    throw new Error(`${path}: expected a mapping of question id to answer, or a list`);
  }

  const keyed = new Map<string, string>();
  for (const [key, value] of Object.entries(parsed as Record<string, unknown>)) {
    const answer = coerce(value, `${path} key '${key}'`);
    if (CONTROL_WORDS.has(answer.trim().toLowerCase())) {
      throw new Error(`${path} key '${key}': '${answer}' is a control word, not an answer`);
    }
    keyed.set(key, answer);
  }

  const used = new Set<string>();
  let lastKey: string | undefined;
  return {
    pull: (key) => {
      if (key === lastKey) {
        return Promise.reject(new Error(`answer file ${path}: the answer for '${key}' was not accepted`));
      }
      lastKey = key;
      const answer = keyed.get(key);
      if (answer === undefined) {
        return Promise.reject(new Error(`answer file ${path} has no answer for '${key}'`));
      }
      used.add(key);
      return Promise.resolve(answer);
    },
    unusedKeys: () => [...keyed.keys()].filter((key) => !used.has(key)).sort(),
  };
}
```

- [ ] **Step 4: Pass keys from the runtime.** In `src/interview/cli-runtime.ts`, import `type AnswerSource` from `../generator/init-answers.js`, change `answers?: () => Promise<string>` to `answers?: AnswerSource`, and replace the `pull` helper:

```typescript
  const pull = async (key: string, question: Question | null): Promise<string> => {
    if (opts.answers) return opts.answers(key);
    return question ? inquireQuestion(question) : inquireGate();
  };
```

Update the two call sites: `await pull(question.id, question)` in `handleQuestion`, and `await pull(\`gate.${gate}\`, null)` in `handleGate`.

In `src/generator/init.ts`, change `answers?: () => Promise<string>` in `InitOptions` to `answers?: AnswerSource`, and in `chooseStrategy` call `answers("reconcile.strategy")`. In `src/generator/resume.ts`, change the options type the same way and make `promptRaw` call `pull(question.id)`. Existing tests that pass `() => Promise<string>` still type-check, because a function taking fewer parameters is assignable to `AnswerSource`.

- [ ] **Step 5: Report unused keys.** In `src/cli.ts`, where `init` builds `initOpts` from `--answers`, keep the `LoadedAnswers` object, pass `answers.pull`, and after `init.run` resolves print:

```typescript
      for (const key of loaded.unusedKeys()) {
        console.error(`WARNING: answers file entry '${key}' was never asked (pre-filled or skipped)`);
      }
```

- [ ] **Step 6: Run and commit.** `npx vitest run src/generator/ src/interview/` → PASS.

```bash
git add src/generator/init-answers.ts src/generator/init-answers.test.ts src/interview/cli-runtime.ts src/generator/init.ts src/generator/resume.ts src/cli.ts
git commit -m "feat(init): answers keyed by question id"
```

---

## Task 6: KB root and exclusions

**Goal:** An instance can declare that its KB lives outside `kb/` and which paths are not KB documents, and KB loading reports each broken file instead of aborting.

**Files:**
- Modify: `src/kb/frontmatter.ts`, `src/retrieval/index-lock.ts`, `src/kb/loader.ts`, `src/retrieval/factory.ts`, `src/retrieval/lexical.ts`, `src/commands/validate-kb.ts`, `src/commands/freshness-audit.ts`, `src/cli.ts`
- Test: `src/kb/frontmatter.test.ts`, `src/kb/loader.test.ts`, `src/retrieval/index-lock.test.ts`

**Acceptance Criteria:**
- [ ] `index.lock` accepts an optional `kb: { root, exclude }`; a lock without it parses exactly as before
- [ ] `resolveKbScope(instanceDir)` returns `root` resolved against the instance directory (default `<instance>/kb`) and `exclude` (default `[]`)
- [ ] Exclusion entries: a trailing `/` excludes a subtree; a leading `**/` matches that path at any depth; anything else is an exact relative path
- [ ] `loadKb` skips excluded files, and a file whose front matter does not parse becomes one failure entry instead of throwing
- [ ] `parseFrontmatter` normalizes CRLF and lone-CR line endings before parsing: on a Windows checkout (`core.autocrlf=true`) `tags: []` parses without throwing and no parsed value carries a trailing carriage return
- [ ] `validate-kb --instance <dir>`, `freshness-audit --instance <dir>`, `reindex`, and `search` all use the declared scope

**Verify:** `npx vitest run src/kb/ src/retrieval/ src/commands/` → all pass

**Steps:**

- [ ] **Step 1: Write the failing tests.** Append to `src/kb/loader.test.ts`:

```typescript
describe("loadKb — exclusions and parse failures", () => {
  const fm = (id: string): string =>
    `---\nid: operating.${id}\nnamespace: operating\ntitle: ${id}\nowner: o\nstatus: active\nreview_by: "2027-01-01"\nsensitivity: internal\nsource: authored\ntags: []\nsupersedes: []\n---\n\n# ${id}\n`;

  it("skips excluded subtrees and any-depth basenames", async () => {
    const root = mkdtempSync(join(tmpdir(), "team-ai-kbx-"));
    mkdirSync(join(root, "archive"), { recursive: true });
    mkdirSync(join(root, "skills", "x"), { recursive: true });
    writeFileSync(join(root, "keep.md"), fm("keep"), "utf8");
    writeFileSync(join(root, "archive", "old.md"), "no front matter", "utf8");
    writeFileSync(join(root, "skills", "x", "SKILL.md"), "---\nname: x\n---\n", "utf8");
    const docs = await loadKb(root, { exclude: ["archive/", "**/SKILL.md"] });
    expect(docs.map((d) => d.path)).toEqual(["keep.md"]);
    rmSync(root, { recursive: true, force: true });
  });

  it("reports an unparseable file as a failure instead of throwing a YAML error", async () => {
    const root = mkdtempSync(join(tmpdir(), "team-ai-kbp-"));
    writeFileSync(join(root, "keep.md"), fm("keep"), "utf8");
    writeFileSync(join(root, "bad.md"), "---\ndescription: a: b: c\n  nested: here\n---\n", "utf8");
    await expect(loadKb(root)).rejects.toSatisfy(
      (err: unknown) => err instanceof KbValidationError && err.failures.some((f) => f.file === "bad.md"),
    );
    rmSync(root, { recursive: true, force: true });
  });
});
```

Append to `src/retrieval/index-lock.test.ts`:

```typescript
describe("index.lock kb scope", () => {
  it("resolves the declared KB root and exclusions against the instance directory", () => {
    const dir = mkdtempSync(join(tmpdir(), "team-ai-lock-"));
    writeFileSync(
      join(dir, "index.lock"),
      "driver: lexical\nchunk:\n  split_on: [h2, h3]\n  target_tokens: 800\n  hard_cap: 1200\nembedding: null\nkb:\n  root: ../docs\n  exclude: [archive/]\n",
      "utf8",
    );
    const scope = resolveKbScope(dir);
    expect(scope.root).toBe(resolve(dir, "..", "docs"));
    expect(scope.exclude).toEqual(["archive/"]);
    rmSync(dir, { recursive: true, force: true });
  });

  it("defaults to <instance>/kb with no exclusions when the lock has no kb block", () => {
    const dir = mkdtempSync(join(tmpdir(), "team-ai-lock-"));
    writeIndexLock(dir, DEFAULT_INDEX_LOCK);
    expect(resolveKbScope(dir)).toEqual({ root: join(dir, "kb"), exclude: [] });
    rmSync(dir, { recursive: true, force: true });
  });
});
```

Import any missing helpers (`resolve`, `resolveKbScope`, `writeIndexLock`, `DEFAULT_INDEX_LOCK`, `KbValidationError`, fs functions) at the top of each file.

- [ ] **Step 2: Run to confirm failure.** `npx vitest run src/kb/loader.test.ts src/retrieval/index-lock.test.ts` → FAIL.

- [ ] **Step 3: Extend `index.lock`.** In `src/retrieval/index-lock.ts`:

```typescript
export interface IndexLockKb {
  root: string;
  exclude: string[];
}
```

Add `kb?: IndexLockKb;` to `IndexLock`. In `cloneLock`, copy it when present: `...(lock.kb ? { kb: { root: lock.kb.root, exclude: [...lock.kb.exclude] } } : {})`. In `parseLock`, after the existing checks:

```typescript
  if ("kb" in value && value.kb !== undefined) {
    const kb = value.kb;
    if (!isRecord(kb) || !isNonEmptyString(kb.root)) {
      throw new Error("kb must be an object with a non-empty root");
    }
    const exclude = kb.exclude ?? [];
    if (!Array.isArray(exclude) || !exclude.every((e) => isNonEmptyString(e))) {
      throw new Error("kb.exclude must be a list of non-empty strings");
    }
    lock.kb = { root: kb.root, exclude: [...exclude] };
  }
```

(adapt `lock` to whatever local name `parseLock` builds before returning). Add:

```typescript
export function resolveKbScope(instanceDir: string): { root: string; exclude: string[] } {
  const lock = readIndexLock(instanceDir);
  if (lock.kb === undefined) return { root: join(instanceDir, "kb"), exclude: [] };
  return { root: resolve(instanceDir, lock.kb.root), exclude: [...lock.kb.exclude] };
}
```

importing `resolve` from `node:path`. Make sure `writeIndexLock` serializes `kb` when present.

- [ ] **Step 4: Exclusions and per-file parse failures.** In `src/kb/loader.ts`:

```typescript
export interface LoadKbOptions {
  exclude?: string[];
}

export function isExcluded(relPath: string, exclude: string[]): boolean {
  return exclude.some((entry) => {
    if (entry.endsWith("/")) return relPath.startsWith(entry);
    if (entry.startsWith("**/")) {
      const tail = entry.slice(3);
      return relPath === tail || relPath.endsWith(`/${tail}`);
    }
    return relPath === entry;
  });
}
```

Change the signature to `export async function loadKb(root: string, opts: LoadKbOptions = {}): Promise<KbDoc[]>`, filter `markdown` with `.filter((rel) => !isExcluded(rel, opts.exclude ?? []))`, and wrap the parse:

```typescript
    let parsed: ReturnType<typeof parseFrontmatter>;
    try {
      parsed = parseFrontmatter(raw);
    } catch (err) {
      const reason = err instanceof Error ? (err.message.split("\n")[0] ?? err.message) : String(err);
      failures.push({ file: relPath, error: `front matter does not parse: ${reason}` });
      continue;
    }
    const { data, body } = parsed;
```

- [ ] **Step 5: Use the scope everywhere.** In `src/retrieval/factory.ts`, when `opts?.kbRoot` is undefined, use `resolveKbScope(dir)` for both `kbRoot` and a new `exclude` field; add `exclude?: string[]` to `LexicalAdapterOpts` and pass `{ exclude: this.exclude }` to both `loadKb` calls in `src/retrieval/lexical.ts`. In `src/commands/validate-kb.ts`, add `instance?: string` to the options; when set, take `root` and `exclude` from `resolveKbScope(instance)` and call `loadKb(root, { exclude })`. Do the same in `src/commands/freshness-audit.ts` wherever it loads the KB. In `src/cli.ts`, add to both commands' `configure`:

```typescript
        .option("--instance <dir>", "instance directory; KB root and exclusions come from its index.lock")
```

- [ ] **Step 5b: Normalize line endings when parsing front matter.** Windows checkouts with `core.autocrlf=true` have CRLF on every line. The `yaml` parser throws `Unexpected scalar at node end` on `tags: []` followed by a carriage return, and without a flow sequence it silently keeps a trailing carriage return on every value, so ids and namespaces would never match any mapping. Append to `src/kb/frontmatter.test.ts`:

```typescript
describe("parseFrontmatter — CRLF line endings", () => {
  it("parses flow sequences and leaves no carriage returns", () => {
    const { data, body } = parseFrontmatter(
      "---\r\nid: operating.docs.x\r\ntitle: X\r\ntags: []\r\n---\r\n\r\n# Body\r\n",
    );
    expect(data).toEqual({ id: "operating.docs.x", title: "X", tags: [] });
    expect(body).not.toContain("\r");
  });

  it("handles lone CR line endings", () => {
    expect(parseFrontmatter("---\rtitle: X\rtags: []\r---\r\rBody\r").data).toEqual({
      title: "X",
      tags: [],
    });
  });
});
```

In `src/kb/frontmatter.ts`, normalize before `gray-matter` sees the text:

```typescript
export function parseFrontmatter(raw: string): ParsedDoc {
  const parsed = matter(raw.replace(/\r\n?/g, "\n"), { engines });
```

Do not change writers: `applyRemapPlan` (Task 7) edits the raw file text and must keep CRLF, and `applyFrontmatter` serializes from the raw body.

- [ ] **Step 6: Run and commit.** `npx vitest run src/kb/ src/retrieval/ src/commands/` → PASS.

```bash
git add src/retrieval/ src/kb/ src/commands/validate-kb.ts src/commands/freshness-audit.ts src/cli.ts
git commit -m "feat(kb): configurable KB root and exclusions; per-file parse failures"
```

---

## Task 7: `team-ai remap-namespaces` — conflict-safe migration

**Goal:** Rewrite `namespace` and the first segment of `id` across an instance's KB from a mapping file, refusing to write anything unless every KB document is mapped and nothing is in conflict.

**Files:**
- Create: `src/remap/plan.ts`, `src/remap/plan.test.ts`, `src/remap/apply.ts`, `src/remap/apply.test.ts`, `src/commands/remap-namespaces.ts`
- Modify: `src/cli.ts`

**Acceptance Criteria:**
- [ ] Scope is the instance's KB root minus its exclusions (Task 6)
- [ ] A file with no front matter, or front matter with neither `id` nor `namespace`, is `skipped` and listed
- [ ] Unparseable front matter, a missing `namespace`, a namespace with no mapping rule, or a quoted/commented `id`/`namespace` line is a `conflict`
- [ ] A per-file override beats the namespace rule
- [ ] `applyRemapPlan` throws before writing anything if the plan has any conflict
- [ ] Apply rewrites only the two scalar values; other keys, the body, and CRLF line endings are byte-identical; applying twice is a no-op
- [ ] `--inventory <file>` writes one tab-separated line per item: `path`, `status`, `from`, `to`

**Verify:** `npx vitest run src/remap/` → all pass

**Steps:**

- [ ] **Step 1: Write the failing planner tests.** Create `src/remap/plan.test.ts`:

```typescript
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { afterEach, describe, expect, it } from "vitest";

import { writeIndexLock, DEFAULT_INDEX_LOCK } from "../retrieval/index-lock.js";
import { buildRemapPlan } from "./plan.js";

const dirs: string[] = [];

function kbDoc(ns: string, stem: string, idLine?: string): string {
  return [
    "---",
    idLine ?? `id: ${ns}.docs.${stem}`,
    `namespace: ${ns}`,
    `title: ${stem}`,
    "owner: o",
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

function instance(): { instance: string; kb: string } {
  const top = mkdtempSync(join(tmpdir(), "team-ai-remap-"));
  dirs.push(top);
  const inst = join(top, "team-ai");
  const kb = join(top, "docs");
  mkdirSync(inst, { recursive: true });
  mkdirSync(join(kb, "archive"), { recursive: true });
  writeIndexLock(inst, { ...DEFAULT_INDEX_LOCK, kb: { root: "../docs", exclude: ["archive/"] } });
  return { instance: inst, kb };
}

afterEach(() => {
  for (const dir of dirs.splice(0)) rmSync(dir, { recursive: true, force: true });
});

describe("buildRemapPlan", () => {
  it("rewrites namespace and the id's first segment, honouring per-file overrides", () => {
    const { instance: inst, kb } = instance();
    writeFileSync(join(kb, "a.md"), kbDoc("platform", "a"), "utf8");
    writeFileSync(join(kb, "b.md"), kbDoc("platform", "b"), "utf8");
    const plan = buildRemapPlan({
      instance: inst,
      mapping: { namespaces: { platform: "alpha" }, files: { "b.md": "beta" } },
    });
    expect(plan.items.find((i) => i.path === "a.md")).toMatchObject({ status: "remap", to_id: "alpha.docs.a" });
    expect(plan.items.find((i) => i.path === "b.md")).toMatchObject({ status: "remap", to_namespace: "beta" });
  });

  it("ignores excluded paths and skips files without KB front matter", () => {
    const { instance: inst, kb } = instance();
    writeFileSync(join(kb, "archive", "old.md"), "no front matter", "utf8");
    writeFileSync(join(kb, "notes.md"), "no front matter", "utf8");
    const plan = buildRemapPlan({ instance: inst, mapping: { namespaces: {}, files: {} } });
    expect(plan.items.map((i) => [i.path, i.status])).toEqual([["notes.md", "skipped"]]);
  });

  it("marks an unmapped namespace and a quoted id line as conflicts", () => {
    const { instance: inst, kb } = instance();
    writeFileSync(join(kb, "u.md"), kbDoc("unmapped", "u"), "utf8");
    writeFileSync(join(kb, "q.md"), kbDoc("platform", "q", 'id: "platform.docs.q"'), "utf8");
    const plan = buildRemapPlan({ instance: inst, mapping: { namespaces: { platform: "alpha" }, files: {} } });
    expect(plan.items.find((i) => i.path === "u.md")?.status).toBe("conflict");
    expect(plan.items.find((i) => i.path === "q.md")?.status).toBe("conflict");
  });
});
```

- [ ] **Step 2: Run to confirm failure.** `npx vitest run src/remap/plan.test.ts` → FAIL.

- [ ] **Step 3: Implement the planner.** Create `src/remap/plan.ts`:

```typescript
// Deterministic. No model calls. No network. Reads only; writes live in apply.ts.

import { readdirSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";

import { hasFrontmatter } from "../adopt/backfill.js";
import { parseFrontmatter } from "../kb/frontmatter.js";
import { isExcluded } from "../kb/loader.js";
import { resolveKbScope } from "../retrieval/index-lock.js";

export interface RemapMapping {
  namespaces: Record<string, string>;
  files: Record<string, string>;
}

export type RemapStatus = "remap" | "unchanged" | "skipped" | "conflict";

export interface RemapItem {
  path: string;
  status: RemapStatus;
  from_namespace: string;
  to_namespace: string;
  from_id: string;
  to_id: string;
  reason?: string;
}

export interface RemapPlan {
  kbRoot: string;
  items: RemapItem[];
}

const FRONT_MATTER = /^---\r?\n([\s\S]*?)\r?\n---(?:\r?\n|$)/;
const QUOTED_OR_COMMENTED = /^(id|namespace):[ \t]*(["']|[^\r\n]*[ \t]#)/m;

function walk(dir: string, prefix = ""): string[] {
  const out: string[] = [];
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const rel = prefix === "" ? entry.name : `${prefix}/${entry.name}`;
    if (entry.isDirectory()) out.push(...walk(join(dir, entry.name), rel));
    else if (entry.isFile() && entry.name.endsWith(".md")) out.push(rel);
  }
  return out;
}

export function rewriteId(id: string, toNamespace: string): string {
  const dot = id.indexOf(".");
  return dot === -1 ? toNamespace : `${toNamespace}${id.slice(dot)}`;
}

export function buildRemapPlan(opts: { instance: string; mapping: RemapMapping }): RemapPlan {
  const { root, exclude } = resolveKbScope(opts.instance);
  const items: RemapItem[] = [];
  const blank = { from_namespace: "", to_namespace: "", from_id: "", to_id: "" };

  for (const rel of walk(root).filter((r) => !isExcluded(r, exclude)).sort()) {
    const raw = readFileSync(join(root, rel), "utf8");
    if (!hasFrontmatter(raw)) {
      items.push({ path: rel, status: "skipped", ...blank, reason: "no front matter" });
      continue;
    }
    let data: Record<string, unknown>;
    try {
      ({ data } = parseFrontmatter(raw));
    } catch (err) {
      const reason = err instanceof Error ? (err.message.split("\n")[0] ?? err.message) : String(err);
      items.push({ path: rel, status: "conflict", ...blank, reason: `front matter does not parse: ${reason}` });
      continue;
    }
    if (data.id === undefined && data.namespace === undefined) {
      items.push({ path: rel, status: "skipped", ...blank, reason: "front matter is not KB front matter" });
      continue;
    }
    const fromNs = typeof data.namespace === "string" ? data.namespace : "";
    const fromId = typeof data.id === "string" ? data.id : "";
    const base = { path: rel, from_namespace: fromNs, from_id: fromId };
    if (fromNs === "" || fromId === "") {
      items.push({ ...base, status: "conflict", to_namespace: "", to_id: "", reason: "missing id or namespace" });
      continue;
    }
    if (QUOTED_OR_COMMENTED.test(FRONT_MATTER.exec(raw)?.[1] ?? "")) {
      items.push({ ...base, status: "conflict", to_namespace: "", to_id: "", reason: "quoted or commented id/namespace line" });
      continue;
    }
    const toNs = opts.mapping.files[rel] ?? opts.mapping.namespaces[fromNs];
    if (toNs === undefined) {
      items.push({ ...base, status: "conflict", to_namespace: "", to_id: "", reason: `no mapping rule for namespace '${fromNs}'` });
      continue;
    }
    items.push(
      toNs === fromNs
        ? { ...base, status: "unchanged", to_namespace: fromNs, to_id: fromId }
        : { ...base, status: "remap", to_namespace: toNs, to_id: rewriteId(fromId, toNs) },
    );
  }

  return { kbRoot: root, items };
}

export function writeInventory(plan: RemapPlan, file: string): void {
  const lines = plan.items.map((i) => [i.path, i.status, i.from_namespace, i.to_namespace].join("\t"));
  writeFileSync(file, `path\tstatus\tfrom\tto\n${lines.join("\n")}\n`, "utf8");
}
```

- [ ] **Step 4: Write the failing apply tests.** Create `src/remap/apply.test.ts`:

```typescript
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { afterEach, describe, expect, it } from "vitest";

import { applyRemapPlan } from "./apply.js";
import type { RemapPlan } from "./plan.js";

const dirs: string[] = [];
afterEach(() => {
  for (const dir of dirs.splice(0)) rmSync(dir, { recursive: true, force: true });
});

function fixture(content: string): string {
  const dir = mkdtempSync(join(tmpdir(), "team-ai-apply-"));
  dirs.push(dir);
  writeFileSync(join(dir, "a.md"), content, "utf8");
  return dir;
}

const remap = (kbRoot: string): RemapPlan => ({
  kbRoot,
  items: [
    { path: "a.md", status: "remap", from_namespace: "platform", to_namespace: "alpha", from_id: "platform.docs.a", to_id: "alpha.docs.a" },
  ],
});

describe("applyRemapPlan", () => {
  it("rewrites only the two values and preserves CRLF, other keys and body", () => {
    const original = "---\r\nid: platform.docs.a\r\nnamespace: platform\r\ntitle: Keep Me\r\n---\r\n\r\nBody stays.\r\n";
    const dir = fixture(original);
    applyRemapPlan(remap(dir));
    expect(readFileSync(join(dir, "a.md"), "utf8")).toBe(
      original.replace("id: platform.docs.a", "id: alpha.docs.a").replace("namespace: platform", "namespace: alpha"),
    );
  });

  it("is idempotent", () => {
    const dir = fixture("---\nid: platform.docs.a\nnamespace: platform\n---\n");
    applyRemapPlan(remap(dir));
    const once = readFileSync(join(dir, "a.md"), "utf8");
    applyRemapPlan(remap(dir));
    expect(readFileSync(join(dir, "a.md"), "utf8")).toBe(once);
  });

  it("refuses to write anything when the plan has a conflict", () => {
    const original = "---\nid: platform.docs.a\nnamespace: platform\n---\n";
    const dir = fixture(original);
    const plan = remap(dir);
    plan.items.push({ path: "b.md", status: "conflict", from_namespace: "", to_namespace: "", from_id: "", to_id: "", reason: "x" });
    expect(() => applyRemapPlan(plan)).toThrow(/conflict/);
    expect(readFileSync(join(dir, "a.md"), "utf8")).toBe(original);
  });
});
```

- [ ] **Step 5: Implement apply.** Create `src/remap/apply.ts`:

```typescript
// Deterministic. No model calls. No network.
//
// Rewrites only the `id` and `namespace` scalar values inside the front-matter
// block. The value pattern stops before `\r`, so CRLF files keep their line
// endings. Refuses to touch any file while the plan contains a conflict.

import { readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";

import type { RemapPlan } from "./plan.js";

const FRONT_MATTER = /^(---\r?\n)([\s\S]*?)(\r?\n---(?:\r?\n|$))/;

function setScalar(block: string, key: string, value: string): string {
  return block.replace(new RegExp(`^(${key}:[ \\t]*)[^\\r\\n]*`, "m"), `$1${value}`);
}

export function applyRemapPlan(plan: RemapPlan): { written: string[] } {
  const conflicts = plan.items.filter((i) => i.status === "conflict");
  if (conflicts.length > 0) {
    throw new Error(
      `refusing to apply: ${conflicts.length} conflict(s), first: ${conflicts[0]?.path} (${conflicts[0]?.reason ?? "conflict"})`,
    );
  }

  const written: string[] = [];
  for (const item of plan.items) {
    if (item.status !== "remap") continue;
    const abs = join(plan.kbRoot, item.path);
    const raw = readFileSync(abs, "utf8");
    const match = FRONT_MATTER.exec(raw);
    if (match === null) continue;
    const [whole, open, block, close] = match as unknown as [string, string, string, string];
    const next = setScalar(setScalar(block, "namespace", item.to_namespace), "id", item.to_id);
    if (next === block) continue;
    writeFileSync(abs, `${open}${next}${close}${raw.slice(whole.length)}`, "utf8");
    written.push(item.path);
  }
  return { written };
}
```

- [ ] **Step 6: Add the command.** Create `src/commands/remap-namespaces.ts`:

```typescript
// All file IO for `team-ai remap-namespaces`. Proposal by default; --apply writes.

import { readFileSync, writeFileSync } from "node:fs";

import { parse as parseYaml, stringify as stringifyYaml } from "yaml";

import { applyRemapPlan } from "../remap/apply.js";
import { buildRemapPlan, writeInventory, type RemapMapping } from "../remap/plan.js";

export interface RemapNamespacesOptions {
  instance?: string;
  mapping?: string;
  out?: string;
  inventory?: string;
  apply?: boolean;
}

export function run(opts: RemapNamespacesOptions): Promise<number> {
  if (opts.mapping === undefined) {
    console.error("remap-namespaces: --mapping is required");
    return Promise.resolve(1);
  }
  const mapping = parseYaml(readFileSync(opts.mapping, "utf8")) as RemapMapping;
  const plan = buildRemapPlan({ instance: opts.instance ?? ".", mapping: { namespaces: mapping.namespaces ?? {}, files: mapping.files ?? {} } });

  const counts = { remap: 0, unchanged: 0, skipped: 0, conflict: 0 };
  for (const item of plan.items) counts[item.status] += 1;

  const out = opts.out ?? "remap-proposal.yaml";
  writeFileSync(out, stringifyYaml(plan), "utf8");
  if (opts.inventory !== undefined) writeInventory(plan, opts.inventory);
  console.log(`remap proposal: ${out}`);
  console.log(`  remap ${counts.remap}  unchanged ${counts.unchanged}  skipped ${counts.skipped}  conflict ${counts.conflict}`);
  for (const item of plan.items.filter((i) => i.status === "conflict")) {
    console.error(`  conflict: ${item.path} — ${item.reason ?? ""}`);
  }

  if (opts.apply !== true) return Promise.resolve(counts.conflict > 0 ? 1 : 0);
  try {
    const { written } = applyRemapPlan(plan);
    console.log(`  applied to ${written.length} file(s)`);
    return Promise.resolve(0);
  } catch (err) {
    console.error(err instanceof Error ? err.message : String(err));
    return Promise.resolve(1);
  }
}
```

Register in `src/cli.ts`:

```typescript
  {
    name: "remap-namespaces",
    description: "Rewrite KB namespace and id values from a mapping file (proposal unless --apply)",
    configure: (command) => {
      command
        .option("--instance <dir>", "instance directory whose index.lock declares the KB scope", ".")
        .option("--mapping <file>", "YAML mapping: namespaces and per-file overrides")
        .option("--out <file>", "where to write the proposal", "remap-proposal.yaml")
        .option("--inventory <file>", "also write a tab-separated inventory")
        .option("--apply", "write the changes; refuses while any conflict exists", false);
    },
    run: remapNamespaces.run,
  },
```

- [ ] **Step 7: Run and commit.** `npm run check` → PASS.

```bash
git add src/remap/ src/commands/remap-namespaces.ts src/cli.ts
git commit -m "feat(remap): conflict-safe remap-namespaces command"
```

---

## Task 8: Emit committed Claude Code subagents

**Goal:** `team-ai emit --target claude-code` can write prefixed subagent files that are meant to be tracked, without a plugin manifest, searching the KB with Claude Code's built-in tools.

**Files:**
- Modify: `src/emit/claude-code.ts`, `src/commands/emit.ts`, `src/cli.ts`
- Test: `src/emit/claude-code.test.ts`

**Acceptance Criteria:**
- [ ] `--file-prefix team-ai-` writes `.claude/agents/team-ai-<name>.md`; the front-matter `name` stays unprefixed so delegation references resolve
- [ ] `--no-plugin-manifest` writes no `.claude-plugin/plugin.json`
- [ ] `--builtin-search` sets `tools` to `Read, Grep, Glob` and writes a *Search procedure* section (router or subagent variant, naming the agent's namespaces) **before** the original instructions, under a heading that marks their tool names as unavailable
- [ ] `tools` is written as a comma-separated string; no `model` key is written
- [ ] `--allow-tracked` suppresses the "not gitignored" warning
- [ ] Defaults are unchanged: no prefix, plugin manifest written, raw tool names

**Verify:** `npx vitest run src/emit/` → all pass

**Steps:**

- [ ] **Step 1: Write the failing test.** Append to `src/emit/claude-code.test.ts`:

```typescript
describe("emitClaudeCode — committed layout options", () => {
  it("prefixes file names, skips the plugin manifest, and uses built-in search", async () => {
    const input = await loadEmitInput(FIXTURE);
    const out = mkdtempSync(join(tmpdir(), "team-ai-emit-cc-opts-"));
    const written = emitClaudeCode(input, out, {
      filePrefix: "team-ai-",
      pluginManifest: false,
      builtinSearch: true,
    });
    expect(written.some((p) => p.endsWith("plugin.json"))).toBe(false);
    const agent = input.agents[0]!;
    const raw = readFileSync(join(out, ".claude/agents", `team-ai-${agent.name}.md`), "utf8");
    const front = parseYaml(/^---\n([\s\S]*?)\n---\n/.exec(raw)?.[1] ?? "") as {
      name: string;
      tools: string;
      model?: string;
    };
    expect(front.name).toBe(agent.def.name);
    expect(front.model).toBeUndefined();
    expect(front.tools).toBe("Read, Grep, Glob");
    for (const ns of agent.def.kb_namespaces) expect(raw).toContain(`^namespace: ${ns}`);
    expect(raw.indexOf("## Search procedure")).toBeGreaterThan(-1);
    expect(raw.indexOf("## Search procedure")).toBeLessThan(raw.indexOf("## Original instructions"));
  });
});
```

- [ ] **Step 2: Run to confirm failure.** `npx vitest run src/emit/claude-code.test.ts` → FAIL.

- [ ] **Step 3: Implement.** In `src/emit/claude-code.ts`:

```typescript
export interface EmitClaudeCodeOptions {
  filePrefix?: string;
  pluginManifest?: boolean;
  builtinSearch?: boolean;
}
```

Import `type AgentDef` from `../schema/types.js`. Change `frontMatter` to take the options, build `tools` as a string, and in built-in search mode put the search procedure before the original instructions:

```typescript
const BUILTIN_SEARCH_TOOLS = ["Read", "Grep", "Glob"];

// team-ai's agent templates describe team-ai MCP tools (kb_search and others).
// Built-in search mode puts a procedure for Claude Code's own tools first and
// marks the template text as secondary, so an agent never receives two
// conflicting procedures with equal weight.
function builtinProcedure(def: AgentDef): string {
  const lookup = def.kb_namespaces.map(
    (ns) => `- \`${ns}\`: search the KB root for \`^namespace: ${ns}\` to list your documents.`,
  );
  const steps =
    def.kind === "router"
      ? [
          "1. Read `team-ai/manifest.yaml` for the domain table.",
          "2. Match the question against each domain's `keywords` and `description`; rule out any domain whose `not_owned` covers it.",
          "3. If exactly one domain fits, hand off to its `subagent` and stop.",
          "4. If none fits, search the KB root once for the question's key terms. If the matching documents' namespace belongs to a domain, hand off to that domain's subagent.",
          "5. Otherwise say you do not know and name the most likely owner. Take at most one routing hop.",
        ]
      : [
          ...lookup,
          "",
          "1. Search only those documents for the question.",
          "2. Answer strictly from what they say, and cite every claim with the document path.",
          "3. If nothing in your namespaces answers it, say you do not know and name who owns the question. Do not answer from general knowledge.",
        ];
  return [
    "## Search procedure",
    "",
    "The knowledge base is the Markdown under the KB root declared in `team-ai/index.lock`. Use the Read, Grep, and Glob tools. Tool names under *Original instructions* are not available here; follow this procedure instead.",
    "",
    ...steps,
  ].join("\n");
}

function frontMatter(input: EmitInput["agents"][number], opts: EmitClaudeCodeOptions): string {
  const tools = opts.builtinSearch === true ? BUILTIN_SEARCH_TOOLS : input.def.tools;
  const meta = {
    name: input.def.name,
    description: input.def.description,
    tools: tools.join(", "),
    kind: input.def.kind,
    model_tier: input.def.model_tier,
    kb_namespaces: input.def.kb_namespaces,
    max_hops: input.def.max_hops,
  };
  const original = input.instructions.trim();
  const body =
    opts.builtinSearch === true
      ? `${builtinProcedure(input.def)}\n\n## Original instructions\n\n${original}`.trim()
      : original;
  return `---\n${stringifyYaml(meta)}---\n\n${body}${body.length > 0 ? "\n" : ""}`;
}
```

Change the signature to `emitClaudeCode(input: EmitInput, outDir: string, opts: EmitClaudeCodeOptions = {})`, write each agent to `` `.claude/agents/${opts.filePrefix ?? ""}${agent.name}.md` ``, and wrap the plugin block in `if (opts.pluginManifest !== false) { ... }`, using the prefixed paths in `plugin.agents`.

In `src/commands/emit.ts`, add `filePrefix?: string; pluginManifest?: boolean; builtinSearch?: boolean; allowTracked?: boolean;` to `EmitCommandOptions`, skip the gitignore warning when `opts.allowTracked === true`, and pass the three emitter options for the `claude-code` target. In `src/cli.ts`, add to `emit`'s `configure`:

```typescript
        .option("--file-prefix <prefix>", "prefix for emitted Claude Code agent file names", "")
        .option("--no-plugin-manifest", "do not write .claude-plugin/plugin.json")
        .option("--builtin-search", "give agents Read, Grep, Glob and a namespace lookup section", false)
        .option("--allow-tracked", "emitted output is intentionally committed; skip the gitignore warning", false)
```

- [ ] **Step 4: Run and commit.** `npx vitest run src/emit/` → PASS.

```bash
git add src/emit/claude-code.ts src/emit/claude-code.test.ts src/commands/emit.ts src/cli.ts
git commit -m "feat(emit): options for committed Claude Code subagents"
```

---

## Task 9: MCP server template without `npx`; real tools only

**Goal:** The generated knowledge server runs a pinned local team-ai build, computes its root correctly on Windows, reads the declared KB scope, and agent templates name only tools the server implements.

**Files:**
- Modify: `templates/mcp-server/server.mjs.hbs`, `templates/instance/agents/_domain-sme.yaml.hbs`
- Test: `src/generator/mcp-server-template.test.ts`, `src/generator/agent-templates.test.ts`

**Acceptance Criteria:**
- [ ] The rendered server contains no `npx`
- [ ] It runs `process.execPath` with the path in `TEAM_AI_CLI`, and returns a clear error when `TEAM_AI_CLI` is unset
- [ ] `ROOT` is computed with `fileURLToPath`, not `URL.pathname`
- [ ] Freshness tools call `freshness-audit --instance ROOT`
- [ ] Every tool named in any `templates/instance/agents/*.yaml.hbs` exists in the server's `TOOLS` (so `kb_list` is removed from the domain SME template)
- [ ] The rendered server still passes `node --check`

**Verify:** `npx vitest run src/generator/mcp-server-template.test.ts src/generator/agent-templates.test.ts` → all pass

**Steps:**

- [ ] **Step 1: Write the failing tests.** In `src/generator/mcp-server-template.test.ts`, inside the existing describe, add (reusing the file's rendered-server variable):

```typescript
  it("never shells out through npx and resolves the CLI from TEAM_AI_CLI", () => {
    expect(serverSource).not.toMatch(/\bnpx\b/);
    expect(serverSource).toContain("TEAM_AI_CLI");
    expect(serverSource).toContain("fileURLToPath");
    expect(serverSource).toContain('"--instance", ROOT');
  });
```

Append to `src/generator/agent-templates.test.ts`:

```typescript
it("names only tools the MCP server template implements", () => {
  const server = readFileSync("templates/mcp-server/server.mjs.hbs", "utf8");
  const implemented = new Set([...server.matchAll(/^\s{2}(kb_[a-z_]+):\s*\{/gm)].map((m) => m[1]));
  for (const file of ["templates/instance/agents/sme.yaml.hbs", "templates/instance/agents/_domain-sme.yaml.hbs"]) {
    const tools = /^tools:\s*\[([^\]]*)\]/m.exec(readFileSync(file, "utf8"))?.[1] ?? "";
    for (const tool of tools.split(",").map((t) => t.trim()).filter(Boolean)) {
      expect(implemented.has(tool), `${file}: ${tool}`).toBe(true);
    }
  }
});
```

Rename `serverSource` to whatever the existing test calls the rendered server text.

- [ ] **Step 2: Run to confirm failure.** Both new tests FAIL (`npx` present; `kb_list` not implemented).

- [ ] **Step 3: Fix the server.** In `templates/mcp-server/server.mjs.hbs`, add `import { dirname, resolve } from "node:path";` and `import { fileURLToPath } from "node:url";`, then replace the `ROOT` line, both freshness `argv` lines, and `callCli`, and replace the comment above `const TOOLS = {` with exactly:

```javascript
// tool name -> argv builder. Every command is read-only and emits JSON or text
// on stdout.
```

The template must not contain the token `npx` anywhere, including comments; the Step 1 test enforces this. Confirm with `grep -n npx templates/mcp-server/server.mjs.hbs`, which must print nothing. The replacements:

```javascript
// The instance directory this server was generated into.
const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");

// Absolute path to a local team-ai build's dist/cli.js. team-ai is not published
// to npm, and the package with that name there is unrelated, so this server
// only ever runs the local build.
const CLI = process.env.TEAM_AI_CLI;
```

```javascript
    argv: () => ["freshness-audit", "--instance", ROOT],
```

```javascript
async function callCli(argv) {
  if (!CLI) {
    return {
      ok: false,
      error: "TEAM_AI_CLI is not set: point it at a local team-ai build's dist/cli.js",
    };
  }
  try {
    const { stdout } = await run(process.execPath, [CLI, ...argv], {
      cwd: ROOT,
      maxBuffer: 8 * 1024 * 1024,
    });
    const text = stdout.trim();
    try {
      return { ok: true, data: JSON.parse(text) };
    } catch {
      return { ok: true, data: text };
    }
  } catch (err) {
    return { ok: false, error: err && err.message ? err.message : String(err) };
  }
}
```

- [ ] **Step 4: Remove the unimplemented tool.** In `templates/instance/agents/_domain-sme.yaml.hbs`, change the tools line to:

```yaml
tools: [kb_search, kb_get, kb_coverage_gap]
```

- [ ] **Step 5: Run and commit.** `npx vitest run src/generator/` → PASS.

```bash
git add templates/mcp-server/server.mjs.hbs templates/instance/agents/_domain-sme.yaml.hbs src/generator/mcp-server-template.test.ts src/generator/agent-templates.test.ts
git commit -m "fix(mcp-server): run a local team-ai build, never npx; name only real tools"
```

---

## Task 10: CI workflows without `npx`

**Goal:** No workflow shipped or generated by team-ai downloads the unrelated `team-ai` npm package.

**Files:**
- Modify: `.github/workflows/validate-kb.reusable.yml`, `.github/workflows/validate-spoke.reusable.yml`, `.github/workflows/evals.reusable.yml`, `templates/instance/.github/workflows/freshness.yml.hbs`, `templates/instance/.github/workflows/reindex.yml.hbs`, `templates/instance/README.md.hbs`, `templates/instance/SETUP.md.hbs`, `src/ci-config.test.ts`

**Acceptance Criteria:**
- [ ] The reusable workflows take a `team-ai-ref` input (default `v0`) instead of `team-ai-version`
- [ ] Each checks out `nickejanssen/team-ai` at that ref into `.team-ai-cli`, runs `npm ci` and `npm run build` there, and invokes `node .team-ai-cli/dist/cli.js`
- [ ] A test fails if any file under `.github/workflows/` or `templates/` contains `npx team-ai`
- [ ] The generated instance README and SETUP tell people to run `team-ai` built from source, and neither contains the phrase the test forbids, even inside a warning

**Verify:** `npx vitest run src/ci-config.test.ts` → all pass

**Steps:**

- [ ] **Step 1: Update the test first.** In `src/ci-config.test.ts`, change `DOCUMENTED_INPUTS` to:

```typescript
const DOCUMENTED_INPUTS: Record<string, string> = {
  "node-version": "22",
  root: ".",
  "team-ai-ref": "v0",
};
```

and append:

```typescript
describe("no workflow runs the unrelated npm package", () => {
  const files = [
    ...readdirSync(".github/workflows").map((f) => `.github/workflows/${f}`),
    ...readdirSync("templates", { recursive: true })
      .map(String)
      .filter((f) => f.endsWith(".hbs"))
      .map((f) => `templates/${f}`),
  ];
  it.each(files)("%s does not call npx team-ai", (file) => {
    expect(readFileSync(file, "utf8")).not.toMatch(/npx\s+(--yes\s+)?team-ai/);
  });
});
```

adding `readdirSync` to the `node:fs` import.

- [ ] **Step 2: Run to confirm failure.** `npx vitest run src/ci-config.test.ts` → FAIL.

- [ ] **Step 3: Rewrite the reusable workflows.** Replace `.github/workflows/validate-kb.reusable.yml` with:

```yaml
name: validate-kb (reusable)
on:
  workflow_call:
    inputs:
      node-version:
        description: Node.js version to run under
        type: string
        default: "22"
      root:
        description: Instance root directory to validate
        type: string
        default: "."
      team-ai-ref:
        description: team-ai git ref (tag or branch) to build and run
        type: string
        default: "v0"
permissions:
  contents: read
jobs:
  validate-kb:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/checkout@v4
        with:
          repository: nickejanssen/team-ai
          ref: ${{ inputs.team-ai-ref }}
          path: .team-ai-cli
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ inputs.node-version }}
      - run: npm ci && npm run build
        working-directory: .team-ai-cli
      - run: node .team-ai-cli/dist/cli.js validate-kb --instance ${{ inputs.root }}
      - run: node .team-ai-cli/dist/cli.js validate-citations --root ${{ inputs.root }}
```

Apply the same input rename and the same four checkout/setup/build steps to `validate-spoke.reusable.yml` and `evals.reusable.yml`, replacing each `npx team-ai@${{ inputs.team-ai-version }}` with `node .team-ai-cli/dist/cli.js`. In `evals.reusable.yml`, keep the existing `run-evals ... --json`, `if: always()`, and `actions/upload-artifact@v4` lines the test checks.

- [ ] **Step 4: Fix the instance workflow templates.** In `templates/instance/.github/workflows/freshness.yml.hbs` and `reindex.yml.hbs`, insert before the `npx` step:

```yaml
      - uses: actions/checkout@v4
        with:
          repository: nickejanssen/team-ai
          ref: v0
          path: .team-ai-cli
      - run: npm ci && npm run build
        working-directory: .team-ai-cli
```

and replace `npx team-ai` with `node .team-ai-cli/dist/cli.js` in the command step.

- [ ] **Step 4b: Fix the instance README and SETUP templates.** The Step 1 test scans every `.hbs` under `templates/`, so these fail it too. In `templates/instance/README.md.hbs`, replace the `## Day to day` section with:

````markdown
## Day to day

These commands use the team-ai CLI built from source. It is not published to
npm, so install it by cloning github.com/nickejanssen/team-ai and running
`npm ci`, `npm run build`, and `npm link` under Node 22. See that repository's
README.

```bash
team-ai validate-kb            # front matter + relations
team-ai assemble-manifest      # rebuild manifest.yaml from the fragment
team-ai reindex                # rebuild the retrieval index
team-ai run-evals              # replay the golden set against the gates
team-ai freshness-audit        # list stale / orphaned / unowned docs
```
````

In `templates/instance/SETUP.md.hbs`, change only the command text in the two references to `run-evals --help` and `validate-kb`, so each reads `team-ai <command>`. Do not write the forbidden phrase anywhere in either template, including in a warning, because the test pattern matches it. Leave `src/interview/fixtures/pf-extend/.mcp.json` alone: it is a test fixture imitating a user's existing MCP config. Confirm with `grep -rn "npx team-ai" templates .github/workflows`, which must print nothing.

- [ ] **Step 5: Run and commit.** `npm run check` → PASS.

```bash
git add .github/workflows/ templates/instance/.github/workflows/ templates/instance/README.md.hbs templates/instance/SETUP.md.hbs src/ci-config.test.ts
git commit -m "fix(ci): build team-ai from source in workflows, never npx"
```

---

## Task 11: Release team-ai 0.4.0

**Goal:** Tag and publish Tasks 1–10 so Arcwright consumes a fixed version.

**Files:**
- Modify: `package.json`, `package-lock.json`, `CHANGELOG.md`

**Acceptance Criteria:**
- [ ] `npm run check`, `npm run build`, and `node dist/cli.js check-agnostic` all pass
- [ ] Version `0.4.0` in `package.json` and `package-lock.json`; CHANGELOG `0.4.0` section with the PR #5 Security entry moved into it
- [ ] Tag `v0.4.0` pushed; GitHub Release created; `v0` branch fast-forwarded

**Verify:** `node dist/cli.js validate-manifest --help && node dist/cli.js remap-namespaces --help` → both print options

**Steps:**

- [ ] **Step 1:** Set `"version": "0.4.0"`, run `npm install --package-lock-only`, and write the CHANGELOG section with one entry per Task 1–10 plus the Security entry from PR #5.

- [ ] **Step 2: Verify.**

```bash
npm run check && npm run build && node dist/cli.js check-agnostic
```

- [ ] **Step 3: PR, then release after the founder merges.**

```bash
git add package.json package-lock.json CHANGELOG.md
git commit -m "chore(release): team-ai 0.4.0"
git push -u origin feat/agent-topology-phase-a
gh pr create --repo nickejanssen/team-ai --base main --title "feat: agent topology framework changes (0.4.0)" --body "Phase A framework changes for arcwright spec 0089 v1.2. See CHANGELOG."
```

After merge:

```bash
git checkout main && git pull
git tag -a v0.4.0 -m "team-ai 0.4.0"
git push origin v0.4.0
gh release create v0.4.0 --repo nickejanssen/team-ai --title "v0.4.0" --notes-from-tag
git push origin main:v0
```

---

## Task 12: Record the `.claude` exception in Arcwright

**Goal:** `AGENTS.md` and its Copilot mirror permit exactly the founder-approved generated subagent files and nothing else under `.claude/`.

**Files:**
- Modify: `AGENTS.md`, `.github/copilot-instructions.md`

**Acceptance Criteria:**
- [ ] Both files contain the exception paragraph, verbatim, directly after the rule "Do not create, modify, stage, commit, or delete files inside `.claude/`…"
- [ ] No other line in either file changes

**Verify:** `git diff --stat` → exactly two files, one paragraph added to each

**Steps:**

- [ ] **Step 1:** In both files, directly after the bullet beginning "Do not create, modify, stage, commit, or delete files inside `.claude/`", insert:

```markdown
- Exception, approved by the founder on 2026-09-13 (spec 0089): files matching `.claude/agents/team-ai-*.md` are generated from `team-ai/` by `team-ai emit` and are intentionally tracked. Do not edit them by hand; regenerate them. This exception covers no other path under `.claude/`.
```

- [ ] **Step 2: Verify and commit.**

```bash
git diff -U0 -- AGENTS.md .github/copilot-instructions.md
git add AGENTS.md .github/copilot-instructions.md
git commit -m "docs(agents): allow tracked team-ai subagents under .claude/agents"
```

---

## Task 13: Verify recorded decisions

**Goal:** Confirm the spec records every founder decision this plan depends on before the KB is touched.

**Files:**
- Read: `docs/specs/0089-team-ai-agent-architecture.md`

**Acceptance Criteria:**
- [ ] *Approved Decisions* contains D1, D2, D3, D5, D6, and the layout approval, each dated 2026-09-13
- [ ] No decision this plan depends on is still listed as proposed

**Verify:** `git grep -n -E "^\*\*D[12356] " -- docs/specs/0089-team-ai-agent-architecture.md` → five lines, all after the line number reported by `git grep -n "^# Approved Decisions" -- docs/specs/0089-team-ai-agent-architecture.md`

**Steps:**

- [ ] **Step 1:** Run both commands in Verify and compare line numbers. If any decision is missing or not under *Approved Decisions*, stop and ask the founder instead of continuing.

---

## Task 14: Instance inputs

**Goal:** Arcwright declares its namespaces, KB scope, interview answers, and migration mapping inside `team-ai/`.

**Files:**
- Create: `team-ai/catalog/namespaces/custom.yaml`, `team-ai/index.lock`, `team-ai/answers.yaml`, `team-ai/namespace-remap.yaml`
- Modify: `.gitignore`

**Acceptance Criteria:**
- [ ] `custom.yaml` lists the 14 namespaces with exactly 5 `seed_docs`
- [ ] `team-ai/index.lock` declares `kb.root: ../docs` and the exclusions from the spec
- [ ] The exclusions cover every non-archive Markdown file under `docs/` that lacks KB front matter: on `main` on 2026-09-14 that is the 15 line libraries, 9 `SKILL.md` files, `adoption-plan.md` (the adopt report), `decisions/0000-template.md` (the ADR template), and `specs/0041-aw-217-session-lifecycle-api-and-auth.md`, which carries its own non-KB front matter and is reconciled separately
- [ ] The mapping has a rule for every one of the seven current namespace values
- [ ] `init --dry-run` with the answers file completes with no missing-key error
- [ ] `.gitignore` ignores `.team-ai/`

**Verify:** `node $CLI init --dir . --answers team-ai/answers.yaml --catalog team-ai/catalog --on-conflict subdir --dry-run` → exits 0 and prints `Nothing was written.`

**Steps:**

- [ ] **Step 1: Namespaces.** Create `team-ai/catalog/namespaces/custom.yaml` (the filename must be `custom.yaml`: the catalog keys by filename stem, and `custom` is the only `kb.namespaces` answer an answers file can supply):

```yaml
name: custom
description: Arcwright's expertise domains — engine, titles, and practice.
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
    purpose: Records the reasoning for adopting team-ai.
```

- [ ] **Step 2: KB scope.** Create `team-ai/index.lock`:

```yaml
# Generated by team-ai. Changing any value forces a full reindex.
driver: lexical
chunk:
  split_on: [h2, h3]
  target_tokens: 800
  hard_cap: 1200
embedding: null
kb:
  root: ../docs
  exclude:
    - archive/
    - design/line-libraries/
    - "**/SKILL.md"
    - adoption-plan.md
    - decisions/0000-template.md
    - specs/0041-aw-217-session-lifecycle-api-and-auth.md
```

- [ ] **Step 3: Mapping.** Create `team-ai/namespace-remap.yaml`. Enumerate every per-file override from the live tree first:

```bash
ls docs/architecture/*.md docs/story-bibles/*.md docs/superpowers/*/*.md docs/skills/*/*/*.md
```

```yaml
namespaces:
  operating: product-roadmap
  patterns: engineering-practice
  custom: nightcap
  decisions: product-roadmap
  unmapped: engineering-practice
  platform: arc-execution
  playbooks: engineering-practice
files:
  architecture/03-arc-execution.md: arc-execution
  architecture/04-knowledge-graph.md: knowledge-graph
  architecture/05-session-persistence.md: session-runtime
  architecture/06-model-routing.md: model-routing
  architecture/07-character-behavior.md: character-behavior
  architecture/08-event-system.md: session-runtime
  architecture/09-developer-api.md: developer-api
  architecture/10-content-safety.md: safety
  architecture/11-telemetry.md: playtest-ops
  architecture/12-build-plan.md: product-roadmap
  architecture/13-cost-model.md: model-routing
  architecture/14-architecture-validation.md: engineering-practice
  architecture/15-development-guide.md: engineering-practice
  story-bibles/monster-rpg.md: monster-rpg
  story-bibles/daily-case.md: daily-case
  story-bibles/nightcap-couch-race.md: nightcap-couch-race
```

Paths are relative to the KB root `docs/`. Add a `files` entry routing each playtest-related document under `superpowers/` to `playtest-ops`; every other file follows its namespace rule. Architecture files 01, 02, README, and supplemental schemas follow `platform: arc-execution`.

- [ ] **Step 4: Answers.** Create `team-ai/answers.yaml` with the load-bearing answers:

```yaml
mode: instance
team.name: Arcwright
team.size: "1-3"
kb.namespaces: custom
kb.catalog_override: use-preset
arch.index_driver: lexical
arch.hosting: no-server
agents.domains: arc-execution, knowledge-graph, character-behavior, model-routing, session-runtime, safety, developer-api, nightcap, monster-rpg, daily-case, product-roadmap, engineering-practice, playtest-ops
gate.1: confirm
gate.2: confirm
gate.3: confirm
```

Then run the Verify command repeatedly. Each `has no answer for '<id>'` error names the next question the interview reached: read that id's options in the team-ai checkout's `src/interview/questions.yaml`, add the truthful Arcwright answer, and re-run. For `agents.seed` choose the option that does not seed starter docs. Stop when the dry run exits 0. Unused-entry warnings are expected for pre-filled questions.

- [ ] **Step 5: Ignore machine state and commit.**

```bash
printf '\n# team-ai machine state\n.team-ai/\n' >> .gitignore
git add team-ai/catalog team-ai/index.lock team-ai/answers.yaml team-ai/namespace-remap.yaml .gitignore
git commit -m "feat(team-ai): add Arcwright instance inputs"
```

---

## Task 15: Run the namespace migration

**Goal:** Rewrite `namespace` and `id` across the KB from seven values to fourteen namespaces, after founder approval of a zero-conflict proposal.

> **USER-ORDERED GATE — NON-SKIPPABLE.** This task was requested by the user in the current conversation. It MUST NOT be closed by walking around it, by declaring it "verified inline", or by substituting a cheaper check. Close only after every item in `acceptanceCriteria` has been re-validated independently, with output captured.

**Files:**
- Create: `team-ai/remap-proposal.yaml`, `team-ai/inventory.txt`
- Modify: `docs/**` — `namespace:` and `id:` lines only

**Acceptance Criteria:**
- [ ] The proposal reports `conflict 0`; every `skipped` file is listed to the founder and accepted as not-KB
- [ ] The founder explicitly approves the plain-language summary before `--apply`
- [ ] The diff changes only `namespace:` and `id:` lines
- [ ] `validate-kb --instance team-ai` exits 0
- [ ] `git grep -h '^namespace:' -- docs ':!docs/archive'` shows only the 14 target namespaces
- [ ] No token beginning with a prior namespace value survives outside `docs/archive/`
- [ ] Re-running the proposal reports `remap 0`

**Verify:** `git diff -U0 -- docs | grep '^[+-]' | grep -v '^[+-][+-]' | grep -vE '^[+-](namespace|id):'` → prints nothing

**Steps:**

- [ ] **Step 1: Propose.**

```bash
node $CLI remap-namespaces --instance team-ai --mapping team-ai/namespace-remap.yaml --out team-ai/remap-proposal.yaml --inventory team-ai/inventory.txt
```

Resolve every conflict by adding a mapping rule or an exclusion in `team-ai/index.lock`, then re-run until `conflict 0`. Do not edit any document's front matter in this task: Step 4 allows only `namespace:` and `id:` changes.

Every `skipped` item must also be excluded, because `validate-kb` fails on any file under the KB root without KB front matter. Before Step 2, run:

```bash
node $CLI validate-kb --instance team-ai
```

It must exit 0 on the pre-migration tree (it validates front-matter shape, not namespace values). If it fails, stop and report instead of summarizing for the founder.

- [ ] **Step 2: Summarize and STOP.** Present counts per target namespace, every judgement-call file, and every `skipped` file. Wait for explicit approval.

- [ ] **Step 3: Apply.**

```bash
node $CLI remap-namespaces --instance team-ai --mapping team-ai/namespace-remap.yaml --out team-ai/remap-proposal.yaml --inventory team-ai/inventory.txt --apply
```

- [ ] **Step 4: Prove it.**

```bash
git diff -U0 -- docs | grep '^[+-]' | grep -v '^[+-][+-]' | grep -vE '^[+-](namespace|id):'
node $CLI validate-kb --instance team-ai
git grep -h '^namespace:' -- docs ':!docs/archive' | sort | uniq -c
git grep -n -E "\b(operating|patterns|playbooks|custom|decisions|platform|unmapped)\.[a-z0-9-]+\.[a-z0-9._-]+" -- . ':!docs/archive' ':!adoption-plan.yaml' ':!docs/adoption-plan.md' ':!team-ai/remap-proposal.yaml' ':!team-ai/inventory.txt'
```

The first and last commands print nothing; `validate-kb` exits 0; the namespace list contains only the 14 targets.

- [ ] **Step 5: Commit.**

```bash
git add docs team-ai/remap-proposal.yaml team-ai/inventory.txt
git commit -m "refactor(kb): migrate to 14 Arcwright namespaces"
```

```json:metadata
{"userGate": true, "tags": ["user-gate"], "files": ["team-ai/remap-proposal.yaml", "team-ai/inventory.txt", "docs/"], "verifyCommand": "git diff -U0 -- docs | grep '^[+-]' | grep -v '^[+-][+-]' | grep -vE '^[+-](namespace|id):'", "acceptanceCriteria": ["proposal reports conflict 0", "founder explicitly approved before apply", "diff changes only namespace and id lines", "validate-kb --instance team-ai exits 0", "only 14 target namespaces remain outside archive", "no prior-namespace id survives outside archive", "re-run reports remap 0"], "gateScope": "all", "failurePolicy": "stop", "modelTier": "standard"}
```

---

## Task 16: Generate the router and 13 specialists

**Goal:** team-ai renders the instance into `team-ai/` and nothing outside it.

**Files:**
- Create: `team-ai/**` generated files, including `team-ai/agents/sme.*`, 13 `team-ai/agents/*-sme.*`

**Acceptance Criteria:**
- [ ] `git status --porcelain` shows new or changed paths only under `team-ai/`
- [ ] 14 agent YAMLs exist; each specialist has `max_hops: 0` and a single, unique `kb_namespaces` entry
- [ ] `team-ai/index.lock` still contains the `kb` block (the authored file was kept, not overwritten)

**Verify:** `git status --porcelain | grep -v ' team-ai/'` → prints nothing

**Steps:**

- [ ] **Step 1: Generate.**

```bash
node $CLI init --dir . --answers team-ai/answers.yaml --catalog team-ai/catalog --on-conflict subdir
```

- [ ] **Step 2: Check the boundary and invariants.**

```bash
git status --porcelain | grep -v ' team-ai/'
grep -h 'kb_namespaces:' team-ai/agents/*-sme.yaml | sort | uniq -d
grep -c '^kb:' team-ai/index.lock
```

The first two print nothing; the third prints `1`. Review any `*.team-ai-new` sibling by hand.

- [ ] **Step 3: Commit.**

```bash
git add team-ai
git commit -m "feat(team-ai): generate router and 13 specialists"
```

---

## Task 17: Group SMEs, manifest, invariants

**Goal:** The three group SMEs exist, the manifest describes all domains, agents, and skills, and `validate-manifest` passes.

**Files:**
- Create: `team-ai/agents/engine-sme.yaml`, `engine-sme.md`, `title-sme.yaml`, `title-sme.md`, `practice-sme.yaml`, `practice-sme.md`
- Modify: `team-ai/agents/manifest.fragment.yaml`
- Create: `team-ai/manifest.yaml`

**Acceptance Criteria:**
- [ ] Three group SMEs with `max_hops: 1`, their group's specialist namespaces, and one-line descriptions
- [ ] 14 domains with `group`, `authority`, `not_owned`, `owner`; `nightcap` canonical, `monster-rpg` and `daily-case` provisional, `nightcap-couch-race` archived with `subagent: title-sme`
- [ ] 17 generated or hand-authored agents with definition files
- [ ] Exactly the six role contracts in `docs/agents/` (`business-steward`, `planner`, `product-steward`, `scribe`, `spec-author`, `system-architect`) registered as `kind: persona`, `source: authored`, with `path` and **no** definition file; `README.md`, `USAGE.md`, `expert-personas.md`, and `road-to-live-playbook.md` are not registered
- [ ] Each directory in `docs/skills/` registered as a skill with `source: authored` and `path`
- [ ] `assemble-manifest --root team-ai` and `validate-manifest --root team-ai` exit 0

**Verify:** `node $CLI validate-manifest --root team-ai` → `validate-manifest: OK`

**Steps:**

- [ ] **Step 1: Author the group SMEs.** Create `team-ai/agents/engine-sme.yaml`:

```yaml
name: engine-sme
kind: subagent
description: "Answers engine questions that span specialists, delegating one hop to the owner."
model_tier: small
kb_namespaces: [arc-execution, knowledge-graph, character-behavior, model-routing, session-runtime, safety, developer-api]
tools: [kb_search, kb_get, kb_coverage_gap]
max_hops: 1
escalate_to: unassigned
instructions_file: agents/engine-sme.md
```

`title-sme.yaml` uses `kb_namespaces: [nightcap, monster-rpg, daily-case, nightcap-couch-race]` and a description noting that provisional and archived sources must be labelled as such. `practice-sme.yaml` uses `kb_namespaces: [product-roadmap, engineering-practice, playtest-ops]`. Each `.md` states: answer only from cited KB documents; delegate a single-domain question to that domain's specialist; refuse and name the owner when nothing in the group's namespaces answers it. Do not name `kb_*` tools; the emitter adds the search procedure.

- [ ] **Step 2: Write the fragment.** In `team-ai/agents/manifest.fragment.yaml`, replace the generated `TODO` entries with 14 domains in this shape:

```yaml
domains:
  - id: knowledge-graph
    description: "Who knows what, when they learned it, and from whom."
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
  - id: nightcap-couch-race
    description: "Archived Couch Race variant; answers explain it is superseded."
    keywords: [couch race]
    not_owned: [nightcap murder mystery]
    kb_namespace: nightcap-couch-race
    subagent: title-sme
    group: title
    authority: archived
    model_tier: small
    owner: Nico Janssen
```

Add `agents:` with the router (`tier: 1, kind: router, max_hops: 2, kb_namespaces: []`), the three group SMEs (`tier: 2`, `source: authored`), the 13 specialists (`tier: 3`, `source: generated`), and one `kind: persona, tier: 2, max_hops: 0, kb_namespaces: [], source: authored, path: docs/agents/<file>` entry for each of the six role contracts: `business-steward.md`, `planner.md`, `product-steward.md`, `scribe.md`, `spec-author.md`, `system-architect.md`. The other four files in `docs/agents/` are not agents and are not registered. Add `skills:` with `kb-answer`, `kb-contribute`, `sme-route`, `audit-summary` (`source: generated`) and one `source: authored, path: docs/skills/<dir>/SKILL.md` entry per directory from `ls -d docs/skills/*/`.

Do **not** create `team-ai/agents/<name>.yaml` files for the registered contracts. `validate-manifest` accepts `source: authored` entries that have a `path` (Task 2), and without a definition file the emitter never turns them into subagents, which is what D1 requires.

- [ ] **Step 3: Assemble and validate.**

```bash
node $CLI assemble-manifest --root team-ai
node $CLI validate-manifest --root team-ai
```

- [ ] **Step 4: Commit.**

```bash
git add team-ai/agents team-ai/manifest.yaml
git commit -m "feat(team-ai): group SMEs, manifest, and registered authored agents"
```

---

## Task 18: Emit subagents and add CI

**Goal:** The agents load in Claude Code, search the KB with built-in tools, and CI keeps everything consistent.

**Files:**
- Create: `.claude/agents/team-ai-*.md`, `.github/workflows/team-ai.yml`

**Acceptance Criteria:**
- [ ] Exactly 17 files at `.claude/agents/team-ai-*.md` (router, 13 specialists, 3 group SMEs), each with `tools: Read, Grep, Glob`, a *Search procedure* section before the original instructions, and no `model` key
- [ ] No other file under `.claude/` changes, and no `.mcp.json` is created
- [ ] CI builds team-ai `v0.4.0` from source and fails on invalid KB, broken invariants, emitted-agent drift, or a surviving prior-namespace id

**Verify:** `git status --porcelain .claude | grep -v 'agents/team-ai-'` → prints nothing

**Steps:**

- [ ] **Step 1: Emit.**

```bash
node $CLI emit --target claude-code --dir team-ai --out . --file-prefix team-ai- --no-plugin-manifest --builtin-search --allow-tracked
git status --porcelain .claude | grep -v 'agents/team-ai-'
```

- [ ] **Step 2: Add CI.** Create `.github/workflows/team-ai.yml`:

```yaml
name: team-ai
on:
  pull_request:
  push:
    branches: [main]
permissions:
  contents: read
jobs:
  team-ai:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/checkout@v4
        with:
          repository: nickejanssen/team-ai
          ref: v0.4.0
          path: .team-ai-cli
      - uses: actions/setup-node@v4
        with:
          node-version: "22"
      - run: npm ci && npm run build
        working-directory: .team-ai-cli
      - run: node .team-ai-cli/dist/cli.js validate-kb --instance team-ai
      - run: node .team-ai-cli/dist/cli.js validate-manifest --root team-ai
      - name: emitted subagents match regeneration
        run: |
          node .team-ai-cli/dist/cli.js emit --target claude-code --dir team-ai --out . --file-prefix team-ai- --no-plugin-manifest --builtin-search --allow-tracked
          git diff --exit-code -- .claude/agents
      - name: no prior-namespace ids survive
        run: |
          ! git grep -n -E "\b(operating|patterns|playbooks|custom|decisions|platform|unmapped)\.[a-z0-9-]+\.[a-z0-9._-]+" -- . ':!docs/archive' ':!adoption-plan.yaml' ':!docs/adoption-plan.md' ':!team-ai/remap-proposal.yaml' ':!team-ai/inventory.txt' ':!.team-ai-cli'
```

- [ ] **Step 3: Commit.**

```bash
git add .claude/agents/team-ai-*.md .github/workflows/team-ai.yml
git commit -m "feat(team-ai): emit subagents and add CI"
```

---

## Task 19: Verify end to end and open the PR

**Goal:** Prove the result stays inside the approved layout and hand it over as one reviewable PR.

**Files:** none created

**Acceptance Criteria:**
- [ ] Every path in `git diff --name-only origin/main` is in the spec's allowlist
- [ ] `docs/agents/`, `docs/skills/`, and every non-`team-ai-*` file under `.claude/` are unchanged
- [ ] No `engine/`, `api/`, `sdk/`, `dashboard/` changes
- [ ] No unresolved `*.team-ai-new` file
- [ ] The PR body states the migration is included and that `id` values changed

**Verify:** `git diff --name-only origin/main | grep -vE '^(team-ai/|\.claude/agents/team-ai-|docs/|AGENTS\.md$|\.github/copilot-instructions\.md$|\.github/workflows/team-ai\.yml$|\.gitignore$)'` → prints nothing

**Steps:**

- [ ] **Step 1: Run the checks.**

```bash
git diff --name-only origin/main | grep -vE '^(team-ai/|\.claude/agents/team-ai-|docs/|AGENTS\.md$|\.github/copilot-instructions\.md$|\.github/workflows/team-ai\.yml$|\.gitignore$)'
git diff --stat origin/main -- docs/agents docs/skills engine api sdk dashboard
find . -name '*.team-ai-new' -not -path './node_modules/*' -not -path './.team-ai-cli/*'
node $CLI validate-kb --instance team-ai
node $CLI validate-manifest --root team-ai
```

The first three print nothing; the last two exit 0. Any `docs/` change must be a `namespace:` or `id:` line (Task 15).

- [ ] **Step 2: Open the PR.**

```bash
git push -u origin claude/team-ai-agent-topology
gh pr create --repo nickejanssen/arcwright --base main --title "feat(agents): three-tier agent topology and namespace migration" --body "Implements Phase A of docs/specs/0089-team-ai-agent-architecture.md (v1.2).

- Namespace migration: seven prior values to 14 Arcwright namespaces; rewrites namespace and id front matter on every KB document. No body content changed.
- 17 agents: router and 13 specialists generated into team-ai/, three group SMEs hand-authored; validate-manifest passes.
- Emitted as .claude/agents/team-ai-*.md under the founder-approved exception; agents search the KB with built-in Read, Grep, and Glob.
- CI builds team-ai v0.4.0 from source and checks KB validity, invariants, emitted-agent drift, and surviving old ids.

Not included: Phase B (enforcement skills, hooks, workflows, golden questions) and Phase C (temporal graph, semantic retrieval)."
```

---

## Dependencies

```
Tasks 1, 3, 4, 5, 6, 8, 9, 10 are independent of each other.
Task 1 → Task 2
Task 6 → Task 7
Tasks 2, 7 and the rest of 1–10 → Task 11
Task 11 → Task 12 → Task 13 → Task 14 → Task 15 → Task 16 → Task 17 → Task 18 → Task 19
```
