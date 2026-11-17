import { readdirSync, readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

import { type SchemaName } from "./load.js";
import type { Manifest, ModelTier } from "./types.js";
import { validate } from "./validate.js";

const MINIMAL_FRONTMATTER = {
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
};

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

  it("allows instance extension fields under the x- prefix", () => {
    const r = validate("frontmatter", {
      ...MINIMAL_FRONTMATTER,
      "x-scope-evidence": "none",
    });
    expect(r.ok).toBe(true);
  });

  it("still rejects a misspelled core field", () => {
    const r = validate("frontmatter", {
      ...MINIMAL_FRONTMATTER,
      reviewby: "2027-01-01",
    });
    expect(r.ok).toBe(false);
  });

  it("rejects an unknown status with a path-anchored message", () => {
    const r = validate("frontmatter", {
      id: "x.a.b",
      namespace: "a",
      title: "t",
      owner: "o",
      status: "archived",
      review_by: "2026-12-01",
      sensitivity: "internal",
      source: "authored",
      tags: [],
      supersedes: [],
    });
    expect(r.ok).toBe(false);
    if (!r.ok) expect(r.errors[0]).toContain("/status");
  });

  it("returns the exact input object as value on success", () => {
    const input = { ...MINIMAL_FRONTMATTER };
    const r = validate("frontmatter", input);
    expect(r.ok).toBe(true);
    if (r.ok) expect(r.value).toBe(input);
  });

  it("accepts a relations block", () => {
    const r = validate("frontmatter", {
      id: "x.a.b",
      namespace: "a",
      title: "t",
      owner: "o",
      status: "active",
      review_by: "2026-12-01",
      sensitivity: "internal",
      source: "authored",
      tags: [],
      supersedes: [],
      relations: {
        depends_on: ["x.a.auth"],
        used_by_partner: ["acme"],
        owned_by_role: "architect",
      },
    });
    expect(r.ok).toBe(true);
  });
});

describe("golden schema provenance fields", () => {
  const base = {
    id: "eval.kg.example",
    question: "Where is second-hand knowledge recorded?",
    expect_namespace: "knowledge-graph",
    expect_paths: ["architecture/04-knowledge-graph.md"],
    expect_route: "knowledge-graph-sme",
    expect_tier_max: "small",
    must_cite: true,
  };

  it("accepts the original seven fields alone", () => {
    expect(validate("golden", base).ok).toBe(true);
  });

  it("accepts provenance and answer evidence", () => {
    const withProvenance = {
      ...base,
      source_path: "architecture/04-knowledge-graph.md",
      generated_on: "2026-09-20",
      answer_evidence: "who knows what, when they learned it, and from whom",
    };
    expect(validate("golden", withProvenance).ok).toBe(true);
  });

  it("still rejects an unknown field", () => {
    expect(validate("golden", { ...base, sorce_path: "x" }).ok).toBe(false);
  });
});

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
          {
            name: "sme",
            tier: 1,
            kind: "router",
            max_hops: 2,
            kb_namespaces: [],
            source: "generated",
          },
        ],
        skills: [{ id: "freshness-sweep", deterministic: true, script: "scripts/freshness" }],
      }).ok,
    ).toBe(true);
    expect(validate("manifest", { domains: [domain] }).ok).toBe(true);
  });
});

describe("agent schema", () => {
  it("enforces model_tier enum and max_hops >= 0", () => {
    const bad = validate("agent", {
      name: "p",
      kind: "subagent",
      description: "d",
      model_tier: "medium",
      kb_namespaces: [],
      tools: [],
      max_hops: -1,
      instructions_file: "a.md",
    });
    expect(bad.ok).toBe(false);
  });

  it("accepts a valid subagent", () => {
    const ok = validate("agent", {
      name: "platform-sme",
      kind: "subagent",
      description: "d",
      model_tier: "small",
      kb_namespaces: ["platform"],
      tools: ["kb_search"],
      max_hops: 0,
      instructions_file: "agents/platform-sme.md",
    });
    expect(ok.ok).toBe(true);
  });
});

describe("schema name to result type binding", () => {
  it("infers the value type from the schema name", () => {
    const r = validate("manifest", { domains: [] });
    expect(r.ok).toBe(true);
    if (r.ok) {
      const domains: Manifest["domains"] = r.value.domains;
      expect(Array.isArray(domains)).toBe(true);
    }
  });

  it("rejects a mismatched explicit type parameter at compile time", () => {
    // @ts-expect-error Manifest does not satisfy `N extends SchemaName`
    const r = validate<Manifest>("agent", {});
    expect(r.ok).toBe(false);
  });
});

const MODEL_TIERS = ["none", "small", "large"] as const;

describe("model_tier enum consistency", () => {
  it("matches the ModelTier type members exactly", () => {
    const everyTier: Record<ModelTier, true> = { none: true, small: true, large: true };
    const fromArray: readonly ModelTier[] = MODEL_TIERS;
    expect(Object.keys(everyTier).sort()).toEqual([...fromArray].sort());
  });

  it.each([
    { schema: "agent", path: ["properties", "model_tier", "enum"] },
    { schema: "manifest", path: ["$defs", "manifestDomain", "properties", "model_tier", "enum"] },
    { schema: "spoke", path: ["$defs", "spokeDomain", "properties", "model_tier", "enum"] },
    { schema: "golden", path: ["properties", "expect_tier_max", "enum"] },
  ])("$schema uses the canonical model_tier enum", ({ schema, path }) => {
    expect(nodeAt(readSchema(schema), path)).toEqual([...MODEL_TIERS]);
  });
});

function readSchema(name: string): Record<string, unknown> {
  const path = fileURLToPath(new URL(`../../schemas/${name}.schema.json`, import.meta.url));
  return JSON.parse(readFileSync(path, "utf8")) as Record<string, unknown>;
}

function nodeAt(root: Record<string, unknown>, path: string[]): unknown {
  let node: unknown = root;
  for (const key of path) {
    if (typeof node !== "object" || node === null) return undefined;
    node = (node as Record<string, unknown>)[key];
  }
  return node;
}

const SCHEMA_NAMES: SchemaName[] = [
  "team-profile",
  "frontmatter",
  "agent",
  "manifest",
  "spoke",
  "golden",
  "namespace-preset",
  "role",
  "skill-catalog",
];

function schemaFromFilename(file: string): SchemaName {
  const base = file.replace(/\.(json|ya?ml)$/, "");
  const match = SCHEMA_NAMES.find((n) => base === n || base.startsWith(`${n}-`));
  if (!match) throw new Error(`cannot infer schema from fixture name: ${file}`);
  return match;
}

function readFixture(dir: "valid" | "invalid", file: string): unknown {
  const path = fileURLToPath(new URL(`./fixtures/${dir}/${file}`, import.meta.url));
  return JSON.parse(readFileSync(path, "utf8"));
}

function listFixtures(dir: "valid" | "invalid"): string[] {
  const path = fileURLToPath(new URL(`./fixtures/${dir}/`, import.meta.url));
  return readdirSync(path).filter((f) => /\.(json|ya?ml)$/.test(f));
}

describe("valid fixtures", () => {
  const files = listFixtures("valid");

  it("covers every schema at least twice", () => {
    for (const name of SCHEMA_NAMES) {
      const count = files.filter((f) => schemaFromFilename(f) === name).length;
      expect(count, `valid fixtures for ${name}`).toBeGreaterThanOrEqual(2);
    }
  });

  it.each(files)("%s passes its schema", (file) => {
    const r = validate(schemaFromFilename(file), readFixture("valid", file));
    expect(r.ok, r.ok ? "" : JSON.stringify(r.errors)).toBe(true);
  });
});

const INVALID_CASES: { file: string; schema: SchemaName; expect: string }[] = [
  { file: "frontmatter-bad-status.json", schema: "frontmatter", expect: "/status" },
  {
    file: "frontmatter-missing-owner.json",
    schema: "frontmatter",
    expect: "must have required property 'owner'",
  },
  { file: "agent-bad-tier.json", schema: "agent", expect: "/model_tier" },
  { file: "agent-negative-hops.json", schema: "agent", expect: "/max_hops" },
  {
    file: "frontmatter-bad-date.json",
    schema: "frontmatter",
    expect: 'must match format "date"',
  },
  { file: "frontmatter-bad-source.json", schema: "frontmatter", expect: "must match pattern" },
  {
    file: "team-profile-bad-datetime.json",
    schema: "team-profile",
    expect: 'must match format "date-time"',
  },
  {
    file: "manifest-domain-missing-owner.json",
    schema: "manifest",
    expect: "must have required property 'owner'",
  },
  {
    file: "manifest-domain-extra-key.json",
    schema: "manifest",
    expect: "must NOT have additional properties",
  },
  {
    file: "spoke-missing-toolkit-version.json",
    schema: "spoke",
    expect: "must have required property 'toolkit_version'",
  },
  { file: "spoke-domain-bad-tier.json", schema: "spoke", expect: "/domains/0/model_tier" },
  {
    file: "team-profile-missing-created.json",
    schema: "team-profile",
    expect: "must have required property 'created'",
  },
  {
    file: "team-profile-deferred-missing-revisit.json",
    schema: "team-profile",
    expect: "must have required property 'revisit'",
  },
  { file: "golden-bad-tier.json", schema: "golden", expect: "/expect_tier_max" },
  {
    file: "golden-missing-question.json",
    schema: "golden",
    expect: "must have required property 'question'",
  },
  {
    file: "namespace-preset-missing-name.json",
    schema: "namespace-preset",
    expect: "must have required property 'name'",
  },
  {
    file: "namespace-preset-four-seed-docs.json",
    schema: "namespace-preset",
    expect: "/seed_docs",
  },
  { file: "role-bad-tier.json", schema: "role", expect: "/model_tier" },
  {
    file: "role-missing-summary.json",
    schema: "role",
    expect: "must have required property 'summary'",
  },
  { file: "skill-catalog-bad-presets.json", schema: "skill-catalog", expect: "/presets" },
  {
    file: "skill-catalog-missing-tier.json",
    schema: "skill-catalog",
    expect: "must have required property 'tier'",
  },
];

describe("invalid fixtures", () => {
  it("covers every schema at least twice", () => {
    for (const name of SCHEMA_NAMES) {
      const count = INVALID_CASES.filter((c) => c.schema === name).length;
      expect(count, `invalid cases for ${name}`).toBeGreaterThanOrEqual(2);
    }
  });

  it("references every file in fixtures/invalid", () => {
    const referenced = new Set(INVALID_CASES.map((c) => c.file));
    for (const file of listFixtures("invalid")) {
      expect(referenced.has(file), `unreferenced invalid fixture: ${file}`).toBe(true);
    }
  });

  it.each(INVALID_CASES)("$file fails with expected first error", (testCase) => {
    const r = validate(testCase.schema, readFixture("invalid", testCase.file));
    expect(r.ok).toBe(false);
    if (!r.ok) expect(r.errors[0]).toContain(testCase.expect);
  });
});
