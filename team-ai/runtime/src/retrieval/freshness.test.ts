import {
  cpSync,
  mkdtempSync,
  readFileSync,
  rmSync,
  writeFileSync,
  mkdirSync,
  statSync,
  utimesSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import Database from "better-sqlite3";
import { LexicalAdapter } from "./lexical.js";
import { createAdapter } from "./factory.js";

describe("index freshness", () => {
  it("refuses a stale index after an indexed document changes and recovers after rebuilding", async () => {
    const dir = mkdtempSync(join(tmpdir(), "arc-index-fresh-"));
    const kb = join(dir, "kb");
    cpSync("src/kb/fixtures/kb", kb, { recursive: true });
    const adapter = new LexicalAdapter({ kbRoot: kb, dbPath: join(dir, "index.sqlite") });
    try {
      await adapter.reindex();
      const doc = join(kb, "platform/rate-limits.md");
      writeFileSync(doc, readFileSync(doc, "utf8") + "\nuniquefreshnessterm\n");
      await expect(adapter.search("uniquefreshnessterm")).rejects.toThrow(/index stale/i);
      await adapter.reindex();
      const results = await adapter.search("uniquefreshnessterm");
      expect(results.some((hit) => hit.path === "platform/rate-limits.md")).toBe(true);
    } finally {
      adapter.close();
      rmSync(dir, { recursive: true, force: true });
    }
  });
  it("fails a retrieval batch if a source changes during the batch", async () => {
    const dir = mkdtempSync(join(tmpdir(), "arc-index-batch-"));
    const kb = join(dir, "kb");
    cpSync("src/kb/fixtures/kb", kb, { recursive: true });
    const adapter = new LexicalAdapter({ kbRoot: kb, dbPath: join(dir, "index.sqlite") });
    try {
      await adapter.reindex();
      const doc = join(kb, "platform/rate-limits.md");
      const queries = ["rate limit"];
      Object.defineProperty(queries, "0", {
        get: () => {
          writeFileSync(doc, readFileSync(doc, "utf8") + "\nchanged during batch\n");
          return "rate limit";
        },
      });
      await expect(adapter.searchBatch(queries)).rejects.toThrow(/index stale/i);
    } finally {
      adapter.close();
      rmSync(dir, { recursive: true, force: true });
    }
  });

  it("ignores changes to excluded files but rejects added and deleted included documents", async () => {
    const dir = mkdtempSync(join(tmpdir(), "arc-index-scope-"));
    const kb = join(dir, "kb");
    cpSync("src/kb/fixtures/kb", kb, { recursive: true });
    mkdirSync(join(kb, "excluded"));
    const adapter = new LexicalAdapter({
      kbRoot: kb,
      dbPath: join(dir, "index.sqlite"),
      exclude: ["excluded/"],
    });
    try {
      await adapter.reindex();
      writeFileSync(join(kb, "excluded", "ignore.md"), "ignored unvalidated content");
      expect((await adapter.search("rate limit")).length).toBeGreaterThan(0);
      const original = join(kb, "platform", "rate-limits.md");
      const added = join(kb, "platform", "added.md");
      cpSync(original, added);
      await expect(adapter.search("rate limit")).rejects.toThrow(/index stale/i);
      rmSync(added);
      expect((await adapter.search("rate limit")).length).toBeGreaterThan(0);
      rmSync(original);
      await expect(adapter.search("rate limit")).rejects.toThrow(/index stale/i);
    } finally {
      adapter.close();
      rmSync(dir, { recursive: true, force: true });
    }
  });

  it("refuses a search if an indexed source changes after the precheck", async () => {
    const dir = mkdtempSync(join(tmpdir(), "arc-index-midquery-"));
    const kb = join(dir, "kb");
    cpSync("src/kb/fixtures/kb", kb, { recursive: true });
    const adapter = new LexicalAdapter({ kbRoot: kb, dbPath: join(dir, "index.sqlite") });
    try {
      await adapter.reindex();
      const doc = join(kb, "platform/rate-limits.md");
      let changed = false;
      const options = {
        get namespace(): string {
          if (!changed) {
            changed = true;
            writeFileSync(doc, readFileSync(doc, "utf8") + "\nchanged after precheck\n");
          }
          return "platform";
        },
      };
      await expect(adapter.search("rate limit", options)).rejects.toThrow(/index stale/i);
    } finally {
      adapter.close();
      rmSync(dir, { recursive: true, force: true });
    }
  });

  it("never combines provenance from one SQLite generation with another's chunks", async () => {
    const dir = mkdtempSync(join(tmpdir(), "arc-index-generation-"));
    const kb = join(dir, "kb");
    const dbPath = join(dir, "index.sqlite");
    cpSync("src/kb/fixtures/kb", kb, { recursive: true });
    const adapter = new LexicalAdapter({ kbRoot: kb, dbPath });
    let writer: Database.Database | undefined;
    try {
      await adapter.reindex();
      const before = await adapter.search("rate limit", { namespace: "platform" });
      writer = new Database(dbPath);
      let changed = false;
      const options = {
        get namespace(): string {
          if (!changed) {
            changed = true;
            writer!.transaction(() => {
              writer!.prepare("DELETE FROM chunks").run();
              writer!
                .prepare("UPDATE index_provenance SET fingerprint = ? WHERE id = 1")
                .run("0".repeat(64));
            })();
          }
          return "platform";
        },
      };
      const during = await adapter.search("rate limit", options);
      expect(during).toEqual(before);
      await expect(adapter.search("rate limit", { namespace: "platform" })).rejects.toThrow(
        /index stale/i,
      );
    } finally {
      writer?.close();
      adapter.close();
      rmSync(dir, { recursive: true, force: true });
    }
  });

  it("rejects an old index after effective index.lock configuration changes", async () => {
    const dir = mkdtempSync(join(tmpdir(), "arc-index-config-"));
    cpSync("src/kb/fixtures/kb", join(dir, "kb"), { recursive: true });
    const lockPath = join(dir, "index.lock");
    const adapter = createAdapter(dir);
    try {
      await adapter.reindex();
      writeFileSync(
        lockPath,
        JSON.stringify({
          driver: "lexical",
          chunk: { split_on: ["h2"], target_tokens: 800, hard_cap: 1200 },
          embedding: null,
        }),
      );
      await expect(adapter.search("rate limit")).rejects.toThrow(/index stale/i);
      (adapter as LexicalAdapter).close();
      const reopened = createAdapter(dir);
      try {
        await expect(reopened.search("rate limit")).rejects.toThrow(/index stale/i);
        await reopened.reindex();
        expect((await reopened.search("rate limit")).length).toBeGreaterThan(0);
      } finally {
        (reopened as LexicalAdapter).close();
      }
    } finally {
      (adapter as LexicalAdapter).close();
      rmSync(dir, { recursive: true, force: true });
    }
  });

  it("treats legacy or unreadable indexes as unknown, not fresh", async () => {
    const dir = mkdtempSync(join(tmpdir(), "arc-index-legacy-"));
    const kb = join(dir, "kb");
    cpSync("src/kb/fixtures/kb", kb, { recursive: true });
    const dbPath = join(dir, "index.sqlite");
    const legacy = new Database(dbPath);
    legacy.exec("CREATE TABLE chunks (text TEXT)");
    legacy.close();
    const adapter = new LexicalAdapter({ kbRoot: kb, dbPath });
    try {
      await expect(adapter.search("rate limit")).rejects.toThrow(/index freshness unknown/i);
    } finally {
      adapter.close();
    }
    writeFileSync(dbPath, "not a SQLite database");
    const corrupted = new LexicalAdapter({ kbRoot: kb, dbPath });
    try {
      await expect(corrupted.search("rate limit")).rejects.toThrow(/index freshness unknown/i);
    } finally {
      corrupted.close();
      rmSync(dir, { recursive: true, force: true });
    }
  });

  it("detects content changes even when size and mtime are preserved", async () => {
    const dir = mkdtempSync(join(tmpdir(), "arc-index-timestamp-"));
    const kb = join(dir, "kb");
    cpSync("src/kb/fixtures/kb", kb, { recursive: true });
    const doc = join(kb, "platform", "rate-limits.md");
    const adapter = new LexicalAdapter({ kbRoot: kb, dbPath: join(dir, "index.sqlite") });
    try {
      await adapter.reindex();
      const stat = statSync(doc);
      const original = readFileSync(doc, "utf8");
      const changed = original.replace("429", "428");
      expect(changed.length).toBe(original.length);
      expect(changed).not.toBe(original);
      writeFileSync(doc, changed);
      utimesSync(doc, stat.atime, stat.mtime);
      await expect(adapter.search("rate limit")).rejects.toThrow(/index stale/i);
    } finally {
      adapter.close();
      rmSync(dir, { recursive: true, force: true });
    }
  });

  it("reports freshness unknown when corpus inputs cannot be read", async () => {
    const dir = mkdtempSync(join(tmpdir(), "arc-index-unreadable-"));
    const kb = join(dir, "kb");
    cpSync("src/kb/fixtures/kb", kb, { recursive: true });
    const adapter = new LexicalAdapter({ kbRoot: kb, dbPath: join(dir, "index.sqlite") });
    try {
      await adapter.reindex();
      rmSync(kb, { recursive: true });
      await expect(adapter.search("rate limit")).rejects.toThrow(/index freshness unknown/i);
    } finally {
      adapter.close();
      rmSync(dir, { recursive: true, force: true });
    }
  });
});
