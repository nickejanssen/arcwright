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
    {
      path: "a.md",
      status: "remap",
      from_namespace: "platform",
      to_namespace: "alpha",
      from_id: "platform.docs.a",
      to_id: "alpha.docs.a",
    },
  ],
});

describe("applyRemapPlan", () => {
  it("rewrites only the two values and preserves CRLF, other keys and body", () => {
    const original =
      "---\r\nid: platform.docs.a  \r\nnamespace: platform\t\r\ntitle: Keep Me\r\n---\r\n\r\nBody stays.\r\n";
    const dir = fixture(original);
    applyRemapPlan(remap(dir));
    expect(readFileSync(join(dir, "a.md"), "utf8")).toBe(
      original
        .replace("id: platform.docs.a", "id: alpha.docs.a")
        .replace("namespace: platform", "namespace: alpha"),
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
    plan.items.push({
      path: "b.md",
      status: "conflict",
      from_namespace: "",
      to_namespace: "",
      from_id: "",
      to_id: "",
      reason: "x",
    });
    expect(() => applyRemapPlan(plan)).toThrow(/conflict/);
    expect(readFileSync(join(dir, "a.md"), "utf8")).toBe(original);
  });

  it("precomputes every file and writes none when a later source is unsupported", () => {
    const originalA = "---\nid: platform.docs.a\nnamespace: platform\n---\n";
    const originalB = "---\nid : platform.docs.b\nnamespace: platform\n---\n";
    const dir = fixture(originalA);
    writeFileSync(join(dir, "b.md"), originalB, "utf8");
    const plan = remap(dir);
    plan.items.push({
      path: "b.md",
      status: "remap",
      from_namespace: "platform",
      to_namespace: "alpha",
      from_id: "platform.docs.b",
      to_id: "alpha.docs.b",
    });

    expect(() => applyRemapPlan(plan)).toThrow(/lexical form/);
    expect(readFileSync(join(dir, "a.md"), "utf8")).toBe(originalA);
    expect(readFileSync(join(dir, "b.md"), "utf8")).toBe(originalB);
  });
});
