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
    expect(plan.items.find((i) => i.path === "a.md")).toMatchObject({
      status: "remap",
      to_id: "alpha.docs.a",
    });
    expect(plan.items.find((i) => i.path === "b.md")).toMatchObject({
      status: "remap",
      to_namespace: "beta",
    });
  });

  it.each([
    ["hyphenated", "new-ns", "newns.docs.a"],
    ["slash-separated", "partners/acme-widgets", "partnersacmewidgets.docs.a"],
  ])("accepts a %s destination and normalizes its id segment", (_label, destination, toId) => {
    const { instance: inst, kb } = instance();
    writeFileSync(join(kb, "a.md"), kbDoc("platform", "a"), "utf8");

    const plan = buildRemapPlan({
      instance: inst,
      mapping: { namespaces: { platform: destination }, files: {} },
    });

    expect(plan.items).toMatchObject([
      {
        path: "a.md",
        status: "remap",
        to_namespace: destination,
        to_id: toId,
      },
    ]);
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
    const plan = buildRemapPlan({
      instance: inst,
      mapping: { namespaces: { platform: "alpha" }, files: {} },
    });
    expect(plan.items.find((i) => i.path === "u.md")?.status).toBe("conflict");
    expect(plan.items.find((i) => i.path === "q.md")?.status).toBe("conflict");
  });

  it("does not treat inherited mapping properties as namespace rules", () => {
    const { instance: inst, kb } = instance();
    writeFileSync(join(kb, "constructor.md"), kbDoc("constructor", "constructor"), "utf8");

    const plan = buildRemapPlan({
      instance: inst,
      mapping: { namespaces: {}, files: {} },
    });

    expect(plan.items).toMatchObject([
      {
        path: "constructor.md",
        status: "conflict",
        reason: "no mapping rule for namespace 'constructor'",
      },
    ]);
  });

  it("marks YAML key-spacing variants as conflicts before apply", () => {
    const { instance: inst, kb } = instance();
    writeFileSync(
      join(kb, "spaced.md"),
      kbDoc("platform", "spaced").replace("id: platform.docs.spaced", "id : platform.docs.spaced"),
      "utf8",
    );

    const plan = buildRemapPlan({
      instance: inst,
      mapping: { namespaces: { platform: "alpha" }, files: {} },
    });

    expect(plan.items).toMatchObject([
      {
        path: "spaced.md",
        status: "conflict",
        reason: "unsupported id/namespace lexical form",
      },
    ]);
  });

  it.each([
    ["a non-object mapping", null],
    ["a non-object namespaces section", { namespaces: [], files: {} }],
    ["a non-object files section", { namespaces: {}, files: [] }],
    ["an unknown top-level key", { namespace: { platform: "alpha" } }],
    ["a non-string target", { namespaces: { platform: 42 }, files: {} }],
    ["an invalid file target", { namespaces: {}, files: { "a.md": "Alpha" } }],
    ["an empty target", { namespaces: { platform: "" }, files: {} }],
    ["a newline-containing target", { namespaces: { platform: "alpha\nbeta" }, files: {} }],
    ["a grammar-invalid target", { namespaces: { platform: "Alpha" }, files: {} }],
  ])("rejects %s before reading the KB", (_label, mapping) => {
    expect(() =>
      buildRemapPlan({
        instance: join(tmpdir(), "team-ai-remap-missing"),
        mapping,
      }),
    ).toThrow(/invalid remap mapping/);
  });
});
