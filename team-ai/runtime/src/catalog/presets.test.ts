import { readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";

import { describe, expect, it } from "vitest";
import { parse as parseYaml } from "yaml";

import { validate } from "../schema/validate.js";

function yamlFiles(dir: string): string[] {
  return readdirSync(dir)
    .filter((f) => f.endsWith(".yaml"))
    .map((f) => join(dir, f));
}

describe("shipped namespace presets", () => {
  const files = yamlFiles("catalog/namespaces");

  it("ships the expected four", () => {
    expect(files).toHaveLength(4);
  });

  it.each(files)("%s validates and has exactly 5 seed docs", (file) => {
    const parsed: unknown = parseYaml(readFileSync(file, "utf8"));
    const result = validate("namespace-preset", parsed);
    expect(result.ok, result.ok ? "" : JSON.stringify(result.errors)).toBe(true);
    if (result.ok) expect(result.value.seed_docs).toHaveLength(5);
  });

  it.each(files)("%s keeps every seed doc path inside a second_level dir", (file) => {
    const result = validate("namespace-preset", parseYaml(readFileSync(file, "utf8")));
    expect(result.ok).toBe(true);
    if (result.ok) {
      for (const doc of result.value.seed_docs) {
        const top = doc.path.split("/")[0];
        expect(result.value.second_level).toContain(top);
      }
    }
  });
});

describe("shipped role presets", () => {
  const files = yamlFiles("catalog/roles");

  it("ships the expected five", () => {
    expect(files).toHaveLength(5);
  });

  it.each(files)("%s validates against the role schema", (file) => {
    const result = validate("role", parseYaml(readFileSync(file, "utf8")));
    expect(result.ok, result.ok ? "" : JSON.stringify(result.errors)).toBe(true);
  });
});

describe("shipped skill presets", () => {
  const files = yamlFiles("catalog/skills");

  it("ships the expected nine", () => {
    expect(files).toHaveLength(9);
  });

  it.each(files)("%s validates against the skill-catalog schema", (file) => {
    const result = validate("skill-catalog", parseYaml(readFileSync(file, "utf8")));
    expect(result.ok, result.ok ? "" : JSON.stringify(result.errors)).toBe(true);
  });
});

describe("shipped persona presets", () => {
  const files = readdirSync("catalog/personas").filter((f) => f.endsWith(".md"));

  it("ships the expected three", () => {
    expect(files).toHaveLength(3);
  });

  it.each(files)("%s has front matter with kind: persona", (file) => {
    const text = readFileSync(join("catalog/personas", file), "utf8");
    const match = /^---\n([\s\S]*?)\n---/.exec(text);
    expect(match).not.toBeNull();
    const front = parseYaml(match?.[1] ?? "") as Record<string, unknown>;
    expect(front.kind).toBe("persona");
    expect(front.grants).toBe("none");
  });
});
