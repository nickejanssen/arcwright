import { join, resolve } from "node:path";
import { tmpdir } from "node:os";

import { describe, expect, it } from "vitest";

import { resolveWithin, withinDest } from "./contain.js";

const DEST = resolve(tmpdir(), "team-ai-contain-dest");

describe("withinDest", () => {
  it("accepts a nested child", () => {
    expect(withinDest(DEST, join(DEST, "personas", "a.md"))).toBe(true);
  });

  it("accepts a child whose name only starts with two dots", () => {
    expect(withinDest(DEST, join(DEST, "..foo.md"))).toBe(true);
  });

  it("rejects the destination itself", () => {
    expect(withinDest(DEST, DEST)).toBe(false);
  });

  it("rejects a parent traversal", () => {
    expect(withinDest(DEST, resolve(DEST, "..", "escape.md"))).toBe(false);
    expect(withinDest(DEST, resolve(DEST, "personas", "..", "..", "escape.md"))).toBe(false);
  });
});

describe("resolveWithin", () => {
  it("returns the absolute path for a contained relative path", () => {
    expect(resolveWithin(DEST, "agents/roles/pm.yaml")).toBe(
      resolve(DEST, "agents", "roles", "pm.yaml"),
    );
  });

  it("throws for a traversal that escapes through an entity directory", () => {
    expect(() => resolveWithin(DEST, "personas/../../docs/agents/probe.md")).toThrow(
      /refusing to write outside/,
    );
  });

  it("allows a traversal that stays inside", () => {
    expect(resolveWithin(DEST, "personas/../docs/agents/probe.md")).toBe(
      resolve(DEST, "docs", "agents", "probe.md"),
    );
  });

  it("throws for an absolute path elsewhere", () => {
    expect(() => resolveWithin(DEST, resolve(tmpdir(), "elsewhere.md"))).toThrow(
      /refusing to write outside/,
    );
  });
});
