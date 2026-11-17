import { existsSync, mkdtempSync, readdirSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { afterEach, describe, expect, it } from "vitest";

import { renderEntityFiles } from "./entity-files.js";
import type { RenderResult } from "./render.js";

const dirs: string[] = [];

function tmp(): string {
  const dir = mkdtempSync(join(tmpdir(), "team-ai-entity-"));
  dirs.push(dir);
  return dir;
}

function emptyResult(): RenderResult {
  return {
    created: [],
    unchanged: [],
    updated: [],
    collisions: [],
    siblingsWritten: [],
    warnings: [],
    manifestEntries: [],
  };
}

afterEach(() => {
  for (const dir of dirs.splice(0)) rmSync(dir, { recursive: true, force: true });
});

describe("renderEntityFiles — path containment", () => {
  it("writes an ordinary persona under personas/", () => {
    const dir = tmp();
    renderEntityFiles(
      { namespaces: ["operating"], domains: [], roles: [], personas: ["support-desk"] },
      dir,
      new Map(),
      "siblings",
      emptyResult(),
    );
    expect(existsSync(join(dir, "personas", "support-desk.md"))).toBe(true);
  });

  it("refuses a persona name that traverses into another directory, before writing anything", () => {
    const dir = tmp();
    const result = emptyResult();
    expect(() =>
      renderEntityFiles(
        {
          namespaces: ["operating"],
          // A valid domain listed first proves validation runs before any write.
          domains: [{ slug: "billing", name: "Billing" }],
          roles: [],
          personas: ["../docs/agents/probe"],
        },
        dir,
        new Map(),
        "siblings",
        result,
      ),
    ).toThrow(/persona name/);
    expect(readdirSync(dir)).toEqual([]);
    expect(result.created).toEqual([]);
  });

  it("refuses a role name that traverses out of agents/roles/, before writing anything", () => {
    const dir = tmp();
    const role = { name: "../../escape", summary: "x", default_namespaces: [], default_skills: [] };
    expect(() =>
      renderEntityFiles(
        { namespaces: ["operating"], domains: [], roles: [role], personas: [] },
        dir,
        new Map(),
        "siblings",
        emptyResult(),
      ),
    ).toThrow(/role name/);
    expect(readdirSync(dir)).toEqual([]);
  });
});

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
    expect(readFileSync(join(dir, "agents/alpha-sme.yaml"), "utf8")).toContain(
      "kb_namespaces: [alpha]",
    );
    expect(readFileSync(join(dir, "agents/beta-sme.yaml"), "utf8")).toContain(
      "kb_namespaces: [beta]",
    );
  });
});
