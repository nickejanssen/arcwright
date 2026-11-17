import { describe, expect, it } from "vitest";

import { chunkDoc, estimateTokens, slug } from "./chunk.js";
import type { KbDoc } from "./types.js";

function doc(body: string, title = "Rate limits"): KbDoc {
  return {
    id: "x.platform.rl",
    path: "platform/rl.md",
    frontmatter: {
      id: "x.platform.rl",
      namespace: "platform",
      title,
      owner: "o",
      status: "active",
      review_by: "2027-01-01",
      sensitivity: "internal",
      source: "authored",
      tags: [],
      supersedes: [],
    },
    body,
    headings: [],
    isBacklog: false,
  };
}

describe("chunkDoc", () => {
  it("emits a preamble chunk then one per H2/H3", () => {
    const chunks = chunkDoc(
      doc("Intro para.\n\n## Auth\nAuth text.\n\n### 429s\nWhat to do about 429s.\n"),
    );
    expect(chunks.map((c) => c.heading_path)).toEqual([
      "Rate limits",
      "Rate limits > Auth",
      "Rate limits > Auth > 429s",
    ]);
    expect(chunks[0]?.metadata.namespace).toBe("platform");
    expect(chunks[1]?.text.startsWith("## Auth")).toBe(true);
  });

  it("has no empty preamble when body starts with a heading", () => {
    const chunks = chunkDoc(doc("## Auth\ntext\n"));
    expect(chunks).toHaveLength(1);
    expect(chunks[0]?.heading_path).toBe("Rate limits > Auth");
  });

  it("roots an H3 with no preceding H2 directly under the title", () => {
    const chunks = chunkDoc(doc("Intro.\n\n### 429s\ny\n"));
    expect(chunks.map((c) => c.heading_path)).toEqual(["Rate limits", "Rate limits > 429s"]);
  });

  it("keeps #### and deeper headings as content within the current chunk", () => {
    const chunks = chunkDoc(doc("## Auth\nbody\n\n#### Deep\nmore\n"));
    expect(chunks).toHaveLength(1);
    expect(chunks[0]?.text).toContain("#### Deep");
  });

  it("preamble chunk has no heading line", () => {
    const chunks = chunkDoc(doc("Just intro.\n\n## Auth\nx\n"));
    expect(chunks[0]?.text).toBe("Just intro.");
  });

  it("estimateTokens is words * 1.3 rounded up", () => {
    expect(estimateTokens("one two three")).toBe(4);
  });

  it("slug lowercases and collapses non-alphanumerics", () => {
    expect(slug("Rate limits > Auth > 429s")).toBe("rate-limits-auth-429s");
  });

  it("chunk_id is stable across runs", () => {
    const a = chunkDoc(doc("## Auth\ntext"));
    const b = chunkDoc(doc("## Auth\ntext"));
    expect(a.map((c) => c.chunk_id)).toEqual(b.map((c) => c.chunk_id));
    expect(a[0]?.chunk_id).toBe("x.platform.rl::rate-limits-auth::0");
  });

  it("ignores headings inside fenced code blocks", () => {
    const chunks = chunkDoc(doc("intro\n\n## Real\n```\n## fake heading\n```\nmore\n"));
    expect(chunks.map((c) => c.heading_path)).toEqual(["Rate limits", "Rate limits > Real"]);
  });

  it("splits an oversized section at paragraph boundaries", () => {
    const para = Array.from({ length: 250 }, () => "word").join(" "); // ~325 tokens
    const body = `## Big\n${para}\n\n${para}\n\n${para}\n\n${para}\n`; // ~1300 tokens total > 1200
    const chunks = chunkDoc(doc(body));
    const big = chunks.filter((c) => c.heading_path === "Rate limits > Big");
    expect(big.length).toBeGreaterThan(1);
    expect(
      big.every((c) => estimateTokens(c.text) <= 1200 || c.text.split(/\n\n+/).length === 1),
    ).toBe(true);
    // ordinals reset per heading_path
    expect(big.map((c) => c.chunk_id.split("::").at(-1))).toEqual(big.map((_, i) => String(i)));
  });

  it("does not split a section that fits under the cap", () => {
    const chunks = chunkDoc(doc("## Small\nshort body\n"));
    const small = chunks.filter((c) => c.heading_path === "Rate limits > Small");
    expect(small).toHaveLength(1);
    expect(small[0]?.chunk_id.endsWith("::0")).toBe(true);
  });

  it("keeps a single over-cap paragraph whole", () => {
    const huge = Array.from({ length: 1200 }, () => "word").join(" "); // ~1560 tokens
    const chunks = chunkDoc(doc(`## Big\n${huge}\n`));
    const big = chunks.filter((c) => c.heading_path === "Rate limits > Big");
    expect(big).toHaveLength(1);
  });

  it("disambiguates chunk_id when distinct heading paths slug to the same value", () => {
    const chunks = chunkDoc(doc("## A / B\nfirst\n\n## A B\nsecond\n"));
    const ids = chunks.map((c) => c.chunk_id);
    expect(new Set(ids).size).toBe(ids.length);
    expect(ids).toEqual(["x.platform.rl::rate-limits-a-b::0", "x.platform.rl::rate-limits-a-b::1"]);
    expect(chunks.map((c) => c.heading_path)).toEqual(["Rate limits > A / B", "Rate limits > A B"]);
  });

  it("detects headings in a CRLF body", () => {
    const chunks = chunkDoc(doc("intro\r\n\r\n## Auth\r\ntext\r\n"));
    expect(chunks.map((c) => c.heading_path)).toEqual(["Rate limits", "Rate limits > Auth"]);
    expect(chunks[1]?.text.startsWith("## Auth")).toBe(true);
    expect(chunks[1]?.text).not.toContain("\r");
  });

  it("skips a heading section whose body is empty", () => {
    const chunks = chunkDoc(doc("## A\n## B\ntext\n"));
    expect(chunks).toHaveLength(1);
    expect(chunks[0]?.heading_path).toBe("Rate limits > B");
  });

  it("carries full front matter as metadata", () => {
    const chunks = chunkDoc(doc("## Auth\nx\n"));
    expect(chunks[0]?.metadata.id).toBe("x.platform.rl");
    expect(chunks[0]?.doc_id).toBe("x.platform.rl");
    expect(chunks[0]?.path).toBe("platform/rl.md");
  });
});
