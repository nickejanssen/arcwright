import { rmSync } from "node:fs";
import { afterEach, describe, expect, it } from "vitest";
import { LexicalAdapter, sanitizeQuery, scoreFromBm25 } from "./lexical.js";

const DB = ".tmp-test/lex.sqlite";
afterEach(() => rmSync(".tmp-test", { recursive: true, force: true }));

function adapter(): LexicalAdapter {
  return new LexicalAdapter({ kbRoot: "src/kb/fixtures/kb", dbPath: DB });
}

describe("sanitizeQuery", () => {
  it("keeps every token when the query has at least one content word", () => {
    expect(sanitizeQuery("the 429 errors")).toBe('"the" OR "429" OR "errors"');
  });

  it("returns null when every token is a stopword", () => {
    expect(sanitizeQuery("how does the of a to and it")).toBeNull();
  });

  it("returns null for empty input", () => {
    expect(sanitizeQuery("   ")).toBeNull();
  });

  it("keeps hyphenated and numeric terms", () => {
    expect(sanitizeQuery("the 429 rate-limit errors")).toBe(
      '"the" OR "429" OR "rate-limit" OR "errors"',
    );
  });
});

describe("scoreFromBm25", () => {
  it("scores a non-match as zero", () => {
    expect(scoreFromBm25(0, 3)).toBe(0);
    expect(scoreFromBm25(1.5, 3)).toBe(0);
  });

  it("does not reward accumulation across more terms", () => {
    expect(scoreFromBm25(-6, 3)).toBeCloseTo(scoreFromBm25(-12, 6), 10);
  });

  it("scores stronger per-term relevance higher", () => {
    expect(scoreFromBm25(-12, 3)).toBeGreaterThan(scoreFromBm25(-6, 3));
  });
});

describe("LexicalAdapter", () => {
  it("indexes and ranks the rate-limits doc first for a 429 query", async () => {
    const a = adapter();
    const stats = await a.reindex();
    expect(stats.chunks).toBeGreaterThan(0);
    expect(stats.driver).toBe("lexical");
    const hits = await a.search("what to do about 429 rate limit errors", { k: 5 });
    a.close();
    expect(hits[0]?.path).toMatch(/rate/);
    expect(hits[0]?.score).toBeGreaterThan(0.2);
    expect(hits[0]?.score).toBeLessThanOrEqual(1);
    expect(hits.every((h) => h.score >= 0 && h.score <= 1)).toBe(true);
  });

  it("scores a single common-word query low (absolute, not min-anchored)", async () => {
    const a = adapter();
    await a.reindex();
    const hits = await a.search("team");
    a.close();
    expect(hits.length).toBeGreaterThan(0);
    expect(hits[0]?.score).toBeLessThan(0.5);
  });

  it("returns nothing (or a very low score) for content absent from the KB", async () => {
    const a = adapter();
    await a.reindex();
    const hits = await a.search("kubernetes helm chart deployment");
    a.close();
    expect(hits.length === 0 || (hits[0]?.score ?? 1) < 0.2).toBe(true);
  });

  it("keeps a genuinely-relevant 2nd hit above the refuse floor", async () => {
    const a = adapter();
    await a.reindex();
    const hits = await a.search("token rotation revocation rate limit 429 backoff", { k: 10 });
    a.close();
    expect(hits.length).toBeGreaterThanOrEqual(2);
    expect(hits[1]?.score).toBeGreaterThan(0.1);
  });

  it("caps k at 20", async () => {
    const a = adapter();
    await a.reindex();
    const hits = await a.search("auth token", { k: 999 });
    a.close();
    expect(hits.length).toBeLessThanOrEqual(20);
  });

  it("reindex is idempotent: identical hits and scores after a second build", async () => {
    const a = adapter();
    await a.reindex();
    const first = await a.search("rate limit 429 backoff escalation", { k: 10 });
    const s1 = await a.reindex();
    const s2 = await a.reindex();
    const second = await a.search("rate limit 429 backoff escalation", { k: 10 });
    a.close();
    expect(s2.chunks).toBe(s1.chunks);
    expect(second).toEqual(first);
  });

  it("post-filters by namespace", async () => {
    const a = adapter();
    await a.reindex();
    const hits = await a.search("charter mission auth rate", { namespace: "operating", k: 10 });
    a.close();
    expect(hits.length).toBeGreaterThan(0);
    expect(hits.every((h) => h.metadata.namespace === "operating")).toBe(true);
  });

  it("post-filters by status and tags", async () => {
    const a = adapter();
    await a.reindex();
    const hits = await a.search("rate limit token charter", {
      k: 10,
      filters: { status: ["active"], tags: ["429"] },
    });
    a.close();
    expect(hits.length).toBeGreaterThan(0);
    expect(hits.every((h) => h.path === "platform/rate-limits.md")).toBe(true);
  });

  it("returns [] for a query that sanitizes to empty", async () => {
    const a = adapter();
    await a.reindex();
    const hits = await a.search("!!! ??? ...");
    a.close();
    expect(hits).toEqual([]);
  });

  it("never throws on adversarial queries and the index survives", async () => {
    const a = adapter();
    await a.reindex();
    const nasty = [
      '"',
      "foo AND OR NEAR",
      "col:val",
      "a* b(",
      "x); DROP TABLE chunks;--",
      "",
      "   ",
    ];
    for (const q of nasty) {
      await expect(a.search(q)).resolves.toBeInstanceOf(Array);
    }
    const ok = await a.search("auth token");
    a.close();
    expect(ok.length).toBeGreaterThan(0);
  });

  it("throws a clear error when search runs before reindex", async () => {
    const a = adapter();
    await expect(a.search("anything")).rejects.toThrow(/index not built/);
    a.close();
  });

  it("get() returns a document and resolves by path", async () => {
    const a = adapter();
    await a.reindex();
    const doc = await a.get("platform/rate-limits.md");
    expect(doc.frontmatter.namespace).toBe("platform");
    a.close();
  });

  it("get() resolves by front matter id and slices a section", async () => {
    const a = adapter();
    await a.reindex();
    const doc = await a.get("kb.platform.auth", "rotation");
    a.close();
    expect(doc.path).toBe("platform/auth.md");
    expect(doc.body).toMatch(/^## Rotation/);
    expect(doc.body).toContain("Rotate service keys every 90 days.");
    expect(doc.body).not.toContain("## Token Types");
  });

  it("get() throws for unknown id", async () => {
    const a = adapter();
    await a.reindex();
    await expect(a.get("nope/missing.md")).rejects.toThrow(/no document/);
    a.close();
  });

  it("get() throws for an unknown section", async () => {
    const a = adapter();
    await a.reindex();
    await expect(a.get("platform/auth.md", "nope")).rejects.toThrow(
      /no section 'nope' in platform\/auth\.md/,
    );
    a.close();
  });
});
