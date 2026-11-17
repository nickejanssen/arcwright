import { cpSync, mkdirSync, mkdtempSync, renameSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { afterEach, describe, expect, it } from "vitest";

import { validateSpoke } from "./validate.js";

const GOOD = "src/spoke/fixtures/good-spoke";
const BAD_SERVER = "src/spoke/fixtures/bad-spoke-server";

const dirs: string[] = [];

function scratch(from: string): string {
  const dir = mkdtempSync(join(tmpdir(), "team-ai-spoke-"));
  dirs.push(dir);
  cpSync(from, dir, { recursive: true });
  return dir;
}

afterEach(() => {
  for (const dir of dirs.splice(0)) rmSync(dir, { recursive: true, force: true });
});

describe("validateSpoke", () => {
  it("passes a contract-compliant spoke with zero core edits", async () => {
    const result = await validateSpoke(GOOD);
    expect(result.errors).toEqual([]);
    expect(result.ok).toBe(true);
    expect(result.coreEditsRequired).toBe(0);
  });

  it("flags forbidden core-owned content and counts core edits", async () => {
    const result = await validateSpoke(BAD_SERVER);
    expect(result.ok).toBe(false);
    expect(result.coreEditsRequired).toBeGreaterThanOrEqual(2);
    const joined = result.errors.join("\n");
    expect(joined).toContain("server");
    expect(joined).toContain("index.lock");
  });

  it("errors when spoke.yaml is missing", async () => {
    const dir = mkdtempSync(join(tmpdir(), "team-ai-spoke-"));
    dirs.push(dir);
    const result = await validateSpoke(dir);
    expect(result.ok).toBe(false);
    expect(result.errors).toContain("spoke.yaml not found");
  });

  it("errors when kb/ is missing", async () => {
    const dir = scratch(GOOD);
    rmSync(join(dir, "kb"), { recursive: true, force: true });
    const result = await validateSpoke(dir);
    expect(result.ok).toBe(false);
    expect(result.errors).toContain("kb/ directory is required");
  });

  it("surfaces schema failures from an invalid spoke.yaml", async () => {
    const dir = scratch(GOOD);
    writeFileSync(join(dir, "spoke.yaml"), "name: broken-spoke\n", "utf8");
    const result = await validateSpoke(dir);
    expect(result.ok).toBe(false);
    expect(result.errors.some((e) => e.startsWith("spoke.yaml:"))).toBe(true);
  });

  it("surfaces front-matter failures from a broken kb doc", async () => {
    const dir = scratch(GOOD);
    writeFileSync(
      join(dir, "kb", "partners", "acme-widgets", "overview.md"),
      "---\nid: partners.acme-widgets.overview\n---\n\nbody\n",
      "utf8",
    );
    const result = await validateSpoke(dir);
    expect(result.ok).toBe(false);
    expect(result.errors.some((e) => e.startsWith("kb/"))).toBe(true);
  });

  it("validates agents/ when present and surfaces a bad agent def", async () => {
    const dir = scratch(GOOD);
    writeFileSync(
      join(dir, "agents", "acme-widgets-sme.yaml"),
      "name: acme-widgets-sme\nkind: wizard\n",
      "utf8",
    );
    const result = await validateSpoke(dir);
    expect(result.ok).toBe(false);
    expect(result.errors.some((e) => e.startsWith("agents/acme-widgets-sme.yaml:"))).toBe(true);
  });

  it("flags retrieval adapter code, schemas/ and templates/ as core edits", async () => {
    const dir = scratch(GOOD);
    writeFileSync(join(dir, "lexical.ts"), "export const x = 1;\n", "utf8");
    cpSync(join(dir, "kb"), join(dir, "schemas"), { recursive: true });
    cpSync(join(dir, "kb"), join(dir, "templates"), { recursive: true });
    const result = await validateSpoke(dir);
    expect(result.ok).toBe(false);
    expect(result.coreEditsRequired).toBeGreaterThanOrEqual(3);
    const joined = result.errors.join("\n");
    expect(joined).toContain("lexical.ts");
    expect(joined).toContain("schemas/");
    expect(joined).toContain("templates/");
  });

  it("validates the declared KB root and skips excluded documents", async () => {
    const dir = scratch(GOOD);
    renameSync(join(dir, "kb"), join(dir, "docs"));
    mkdirSync(join(dir, "docs", "archive"), { recursive: true });
    writeFileSync(join(dir, "docs", "archive", "bad.md"), "no front matter", "utf8");
    writeFileSync(
      join(dir, "index.lock"),
      "driver: lexical\nchunk:\n  split_on: [h2, h3]\n  target_tokens: 800\n  hard_cap: 1200\nembedding: null\nkb:\n  root: docs\n  exclude: [archive/]\n",
      "utf8",
    );

    const result = await validateSpoke(dir);
    expect(result.errors.some((e) => e.includes("index.lock"))).toBe(true);
    expect(result.errors.some((e) => e.includes("directory is required"))).toBe(false);
    expect(result.errors.some((e) => e.includes("bad.md"))).toBe(false);
  });
});
