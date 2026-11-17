import { describe, expect, it } from "vitest";

import { findCitationsInText, resolveCitation } from "./citations.js";
import type { KbDoc } from "./types.js";

function doc(path: string, headings: string[], id = "x.platform.rl"): KbDoc {
  return {
    id,
    path,
    frontmatter: {
      id,
      namespace: "platform",
      title: "Rate limits",
      owner: "o",
      status: "active",
      review_by: "2027-01-01",
      sensitivity: "internal",
      source: "authored",
      tags: [],
      supersedes: [],
    },
    body: "",
    headings,
    isBacklog: false,
  };
}

describe("resolveCitation", () => {
  const docs = [doc("platform/rl.md", ["Auth", "429s", "Retry After"])];

  it("resolves a citation with no fragment", () => {
    const result = resolveCitation(docs, "platform/rl.md");
    expect(result).toEqual({ ok: true, doc: docs[0] });
  });

  it("resolves a citation with a matching heading fragment", () => {
    const result = resolveCitation(docs, "platform/rl.md#auth");
    expect(result.ok).toBe(true);
    if (result.ok) {
      expect(result.doc).toBe(docs[0]);
      expect(result.heading).toBe("Auth");
    }
  });

  it("strips a leading kb/ segment before matching the path", () => {
    const result = resolveCitation(docs, "kb/platform/rl.md#auth");
    expect(result.ok).toBe(true);
    if (result.ok) expect(result.heading).toBe("Auth");
  });

  it("matches headings slug-insensitively and returns the original heading text", () => {
    const result = resolveCitation(docs, "platform/rl.md#429s");
    expect(result.ok).toBe(true);
    if (result.ok) expect(result.heading).toBe("429s");

    const spaced = resolveCitation(docs, "platform/rl.md#retry-after");
    expect(spaced.ok).toBe(true);
    if (spaced.ok) expect(spaced.heading).toBe("Retry After");
  });

  it("fails when no document matches the path", () => {
    const result = resolveCitation(docs, "platform/missing.md");
    expect(result).toEqual({ ok: false, reason: "no document at platform/missing.md" });
  });

  it("fails when the fragment matches no heading", () => {
    const result = resolveCitation(docs, "platform/rl.md#nope");
    expect(result).toEqual({ ok: false, reason: "no heading 'nope' in platform/rl.md" });
  });

  it("rejects a bare fragment citation with no path", () => {
    const result = resolveCitation(docs, "#auth");
    expect(result.ok).toBe(false);
    if (!result.ok) expect(result.reason).toContain("no document path");
  });
});

describe("findCitationsInText", () => {
  it("extracts KB link targets and excludes external links", () => {
    const text = [
      "See [rate limits](platform/rl.md) and [auth](kb/platform/rl.md#auth).",
      "External [docs](https://example.com/guide) should be ignored.",
      "Also [again](platform/rl.md) is a duplicate.",
    ].join("\n");
    expect(findCitationsInText(text)).toEqual(["platform/rl.md", "kb/platform/rl.md#auth"]);
  });

  it("returns an empty array when there are no KB links", () => {
    expect(findCitationsInText("no links here, just [text](https://x.com).")).toEqual([]);
  });

  it("extracts the target from titled inline links, discarding the title", () => {
    const text = [
      'A [double](platform/rl.md#auth "Auth section") link.',
      "A [single](platform/other.md 'Other doc') link.",
    ].join("\n");
    expect(findCitationsInText(text)).toEqual(["platform/rl.md#auth", "platform/other.md"]);
  });

  it("strips angle brackets from inline link targets", () => {
    expect(findCitationsInText("See [x](<platform/rl.md#auth>) here.")).toEqual([
      "platform/rl.md#auth",
    ]);
  });

  it("scans reference-style link definitions", () => {
    const text = [
      "Text with a [ref link][a] and another [b].",
      "",
      "  [a]: platform/rl.md#auth",
      '[b]: <platform/other.md> "titled"',
    ].join("\n");
    expect(findCitationsInText(text)).toEqual(["platform/rl.md#auth", "platform/other.md"]);
  });

  it("excludes external links in titled and angle-bracket forms", () => {
    const text = [
      'External [a](https://example.com/guide "Guide").',
      "External [b](<https://example.com/x.md>).",
      "[c]: https://example.com/ref.md",
    ].join("\n");
    expect(findCitationsInText(text)).toEqual([]);
  });
});
