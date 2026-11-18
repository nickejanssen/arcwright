import { mkdtempSync, mkdirSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import { LexicalAdapter } from "./lexical.js";

interface Entry {
  id: string;
  path: string;
}
interface Fixture {
  root: string;
  kb: string;
  index: (entries: Entry[]) => void;
  entry: Entry;
}

function fixture(): Fixture {
  const root = mkdtempSync(join(tmpdir(), "roadmap-exact-"));
  const kb = join(root, "docs");
  mkdirSync(join(kb, "roadmap", "tasks"), { recursive: true });
  function doc(name: string, namespace: string, title: string, body: string): void {
    writeFileSync(
      join(kb, "roadmap", "tasks", `${name}.md`),
      `---\nid: ${namespace}.${name}\nnamespace: ${namespace}\ntitle: '${title}'\nowner: test\nstatus: active\nreview_by: '2027-01-01'\nsensitivity: internal\nsource: authored\ntags: []\nsupersedes: []\n---\n# ${title}\n\n${body}\n`,
    );
  }
  function index(entries: Entry[]): void {
    writeFileSync(join(kb, "roadmap", "index.json"), JSON.stringify({ tasks: entries }));
  }
  const entry = { id: "AW-216", path: "docs/roadmap/tasks/owner.md" };
  doc("owner", "product", "AW-216: Owner record", "A verified owner record.");
  for (let i = 0; i < 45; i++)
    doc(`noise${i}`, "engineering", `Dependency ${i}`, "AW-216 ".repeat(15));
  for (let i = 0; i < 100; i++)
    doc(`filler${i}`, "other", `Filler ${i}`, "Ordinary unrelated material.");
  index([entry]);
  return { root, kb, index, entry };
}

describe("canonical exact roadmap IDs", () => {
  it("prefers the indexed owner for a standalone ID while preserving namespace and exclusion", async () => {
    const f = fixture();
    const adapter = new LexicalAdapter({ kbRoot: f.kb, dbPath: join(f.root, "idx.sqlite") });
    try {
      await adapter.reindex();
      const global = await adapter.search("AW-216", { k: 8 });
      const forbidden = await adapter.search("AW-216", { namespace: "engineering", k: 8 });
      expect(global[0]?.path).toBe("roadmap/tasks/owner.md");
      expect(forbidden.every((hit) => hit.metadata.namespace === "engineering")).toBe(true);
      expect(forbidden.some((hit) => hit.path === "roadmap/tasks/owner.md")).toBe(false);
    } finally {
      adapter.close();
      rmSync(f.root, { recursive: true, force: true });
    }
  });
  it("leaves mixed text, unknown IDs and ambiguous mappings to ordinary search", async () => {
    const f = fixture();
    const adapter = new LexicalAdapter({ kbRoot: f.kb, dbPath: join(f.root, "idx.sqlite") });
    try {
      await adapter.reindex();
      const mixed = await adapter.search("AW-216 dependency", { k: 8 });
      const unknown = await adapter.search("AW-999", { k: 8 });
      f.index([]);
      expect(await adapter.search("AW-216 dependency", { k: 8 })).toEqual(mixed);
      expect(await adapter.search("AW-999", { k: 8 })).toEqual(unknown);
      const noMapping = await adapter.search("AW-216", { k: 8 });
      f.index([f.entry, { ...f.entry, path: "docs/roadmap/tasks/noise0.md" }]);
      expect(await adapter.search("AW-216", { k: 8 })).toEqual(noMapping);
      // A stale or hostile mapping must not turn an unrelated indexed file
      // into the canonical record, nor escape the task directory.
      f.index([{ ...f.entry, path: "docs/roadmap/tasks/noise0.md" }]);
      expect(await adapter.search("AW-216", { k: 8 })).toEqual(noMapping);
      f.index([{ ...f.entry, path: "docs/roadmap/tasks/../noise0.md" }]);
      expect(await adapter.search("AW-216", { k: 8 })).toEqual(noMapping);
    } finally {
      adapter.close();
      rmSync(f.root, { recursive: true, force: true });
    }
  });
  it("does not return an excluded owner", async () => {
    const f = fixture();
    const adapter = new LexicalAdapter({
      kbRoot: f.kb,
      dbPath: join(f.root, "idx.sqlite"),
      exclude: ["roadmap/tasks/owner.md"],
    });
    try {
      await adapter.reindex();
      const hits = await adapter.search("AW-216");
      expect(hits.some((h) => h.path === "roadmap/tasks/owner.md")).toBe(false);
    } finally {
      adapter.close();
      rmSync(f.root, { recursive: true, force: true });
    }
  });
});
