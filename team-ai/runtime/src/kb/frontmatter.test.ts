import { describe, expect, it } from "vitest";
import { parse as parseYaml } from "yaml";

import { parseFrontmatter, serializeFrontmatter } from "./frontmatter.js";

const CANONICAL = `---
id: kb.platform.rate-limits
namespace: platform
title: Rate Limits
owner: solutions-architect
status: active
review_by: "2027-06-30"
sensitivity: internal
source: authored
tags:
  - throttling
supersedes: []
---

## Defaults

Body text.
`;

describe("parseFrontmatter", () => {
  it("parses YAML front matter and trims leading body whitespace", () => {
    const { data, body } = parseFrontmatter(CANONICAL);
    expect(data.id).toBe("kb.platform.rate-limits");
    expect(data.tags).toEqual(["throttling"]);
    expect(body.startsWith("## Defaults")).toBe(true);
  });

  it("keeps date-like scalars as strings", () => {
    const { data } = parseFrontmatter(CANONICAL);
    expect(typeof data.review_by).toBe("string");
    expect(data.review_by).toBe("2027-06-30");
  });

  it("keeps a BARE (unquoted) date scalar as a string, not a Date", () => {
    // Protects the custom `engines.yaml` config: gray-matter's default js-yaml
    // engine would coerce this to a Date object.
    const raw = "---\nreview_by: 2027-03-15\n---\nbody\n";
    const { data } = parseFrontmatter(raw);
    expect(typeof data.review_by).toBe("string");
    expect(data.review_by instanceof Date).toBe(false);
    expect(data.review_by).toBe("2027-03-15");
  });

  it("normalizes CRLF before parsing front matter", () => {
    const raw = "---\r\nid: operating.docs.x\r\ntitle: X\r\ntags: []\r\n---\r\n\r\n# Body\r\n";
    const { data, body } = parseFrontmatter(raw);
    expect(data).toEqual({ id: "operating.docs.x", title: "X", tags: [] });
    expect(body).not.toContain("\r");
  });

  it("normalizes bare CR line endings before parsing front matter", () => {
    const raw = "---\rtitle: X\rtags: []\r---\r\rBody\r";
    const { data, body } = parseFrontmatter(raw);
    expect(data).toEqual({ title: "X", tags: [] });
    expect(body).not.toContain("\r");
  });

  it("returns empty data for a doc with no front matter", () => {
    const { data, body } = parseFrontmatter("# Just a heading\n");
    expect(data).toEqual({});
    expect(body).toBe("# Just a heading\n");
  });
});

describe("serializeFrontmatter", () => {
  it("emits keys in schema order, then remaining keys in insertion order", () => {
    const out = serializeFrontmatter(
      {
        status: "active",
        id: "kb.a.b",
        extra: "z",
        title: "T",
        namespace: "a",
        another: "y",
      },
      "Body\n",
    );
    const keys = out
      .split("\n")
      .filter((l) => /^[a-z_]+:/.test(l))
      .map((l) => l.split(":")[0]);
    expect(keys).toEqual(["id", "namespace", "title", "status", "extra", "another"]);
  });

  it("emits the --- fences and a blank line before the body", () => {
    const out = serializeFrontmatter({ id: "kb.a.b" }, "Body\n");
    expect(out.startsWith("---\n")).toBe(true);
    expect(out).toContain("---\n\nBody\n");
    expect(out.endsWith("\n")).toBe(true);
  });

  it("force-quotes ISO-date string scalars so YAML-1.1 consumers keep them strings", () => {
    const out = serializeFrontmatter(
      {
        id: "kb.a.b",
        review_by: "2027-01-01",
        created_at: "2027-01-01T09:30:00Z",
        title: "Not a date",
      },
      "body\n",
    );
    expect(out).toContain('review_by: "2027-01-01"');
    expect(out).toContain('created_at: "2027-01-01T09:30:00Z"');
    expect(out).toContain("title: Not a date");

    // A YAML-1.1 consumer (js-yaml, GitHub) reads the quoted scalars as strings.
    const body = out.split("---\n")[1] ?? "";
    const reparsed = parseYaml(body, { schema: "yaml-1.1" }) as Record<string, unknown>;
    expect(typeof reparsed.review_by).toBe("string");
    expect(reparsed.review_by).toBe("2027-01-01");
    expect(reparsed.created_at instanceof Date).toBe(false);
  });
});

describe("round-trip", () => {
  it("parse -> serialize -> parse yields deep-equal data", () => {
    const first = parseFrontmatter(CANONICAL);
    const reserialized = serializeFrontmatter(first.data, first.body);
    const second = parseFrontmatter(reserialized);
    expect(second.data).toEqual(first.data);
  });
});
