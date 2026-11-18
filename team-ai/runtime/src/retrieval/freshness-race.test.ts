import { cpSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { describe, expect, it, vi } from "vitest";

const race = vi.hoisted(() => ({ target: "", next: "", armed: false }));
vi.mock("node:fs/promises", async (importOriginal) => {
  const fs = await importOriginal<typeof import("node:fs/promises")>();
  return {
    ...fs,
    readFile: async (path: string, encoding: BufferEncoding) => {
      const content = await fs.readFile(path, encoding);
      if (race.armed && path === race.target) {
        race.armed = false;
        writeFileSync(path, race.next);
      }
      return content;
    },
  };
});
import { LexicalAdapter } from "./lexical.js";

describe("index rebuild snapshot", () => {
  it("does not replace a valid generation when a source changes during rebuild", async () => {
    const dir = mkdtempSync(join(tmpdir(), "arc-reindex-race-"));
    const kb = join(dir, "kb");
    cpSync("src/kb/fixtures/kb", kb, { recursive: true });
    const adapter = new LexicalAdapter({ kbRoot: kb, dbPath: join(dir, "index.sqlite") });
    const doc = join(kb, "platform/rate-limits.md");
    const original = readFileSync(doc, "utf8");
    try {
      await adapter.reindex();
      const before = await adapter.search("rate limit");
      race.target = doc;
      race.next = original + "\nmodified while rebuilding\n";
      race.armed = true;
      await expect(adapter.reindex()).rejects.toThrow(/source changed while rebuilding/i);
      expect(race.armed).toBe(false);
      writeFileSync(doc, original);
      expect(await adapter.search("rate limit")).toEqual(before);
    } finally {
      race.armed = false;
      adapter.close();
      rmSync(dir, { recursive: true, force: true });
    }
  });
});
