import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { describe, expect, it } from "vitest";

import { KbValidationError, loadKb } from "./loader.js";

describe("loadKb", () => {
  it("loads the fixture corpus sorted by path", async () => {
    const docs = await loadKb("src/kb/fixtures/kb");
    expect(docs).toHaveLength(3);
    expect(docs.map((d) => d.path)).toEqual([...docs.map((d) => d.path)].sort());
    expect(docs.some((d) => d.frontmatter.namespace === "platform")).toBe(true);
    expect(docs.some((d) => d.frontmatter.namespace === "operating")).toBe(true);
    expect(docs.every((d) => d.isBacklog === false)).toBe(true);
  });

  it("uses POSIX separators and derives id from front matter", async () => {
    const docs = await loadKb("src/kb/fixtures/kb");
    expect(docs.every((d) => !d.path.includes("\\"))).toBe(true);
    const charter = docs.find((d) => d.path === "operating/charter.md");
    expect(charter?.id).toBe("kb.operating.charter");
  });

  it("reports every invalid doc at once", async () => {
    await expect(loadKb("src/kb/fixtures/kb-broken")).rejects.toThrow(KbValidationError);
    await expect(loadKb("src/kb/fixtures/kb-broken")).rejects.toThrow(/2 invalid document\(s\)/);
    const error = await loadKb("src/kb/fixtures/kb-broken").catch((e: unknown) => e);
    expect(error).toBeInstanceOf(KbValidationError);
    if (error instanceof KbValidationError) {
      expect(error.failures.map((f) => f.file).sort()).toEqual([
        "operating/missing-owner.md",
        "platform/bad-status.md",
      ]);
      expect(error.message).toContain("owner");
      expect(error.message).toContain("/status");
    }
  });

  it("flags _backlog docs", async () => {
    const docs = await loadKb("src/kb/fixtures/kb-backlog");
    expect(docs.some((d) => d.isBacklog)).toBe(true);
    expect(docs.filter((d) => d.isBacklog).every((d) => d.path.includes("_backlog/"))).toBe(true);
    expect(docs.filter((d) => !d.isBacklog).every((d) => !d.path.includes("_backlog/"))).toBe(true);
  });

  it("extracts headings in document order", async () => {
    const docs = await loadKb("src/kb/fixtures/kb");
    const rateLimits = docs.find((d) => d.path === "platform/rate-limits.md");
    expect(rateLimits?.headings).toEqual(["Defaults", "Handling 429s", "Backoff", "Escalation"]);
  });

  it("does not capture heading-looking lines inside fenced code blocks", async () => {
    const docs = await loadKb("src/kb/fixtures/kb");
    const auth = docs.find((d) => d.path === "platform/auth.md");
    expect(auth?.headings).toEqual(["Token Types", "Rotation", "Schedule", "Revocation"]);
    expect(auth?.headings.some((h) => h.includes("shell comment"))).toBe(false);
  });

  it("keeps a bare (unquoted) front matter date as a string through the loader", async () => {
    const docs = await loadKb("src/kb/fixtures/kb");
    // src/kb/fixtures/kb/platform/auth.md uses `review_by: 2027-03-15` (bare).
    const auth = docs.find((d) => d.path === "platform/auth.md");
    expect(typeof auth?.frontmatter.review_by).toBe("string");
    expect(auth?.frontmatter.review_by).toBe("2027-03-15");
  });

  it("ignores non-markdown files", async () => {
    const docs = await loadKb("src/kb/fixtures/kb");
    expect(docs.every((d) => d.path.endsWith(".md"))).toBe(true);
  });

  it("throws a friendly error when the root does not exist", async () => {
    await expect(loadKb("src/kb/fixtures/does-not-exist")).rejects.toThrow(
      /KB root not found: src[\\/]kb[\\/]fixtures[\\/]does-not-exist/,
    );
  });

  it("returns an empty array for an existing but empty root", async () => {
    const docs = await loadKb("src/kb/fixtures/kb-empty");
    expect(docs).toEqual([]);
  });
});

describe("loadKb — exclusions and parse failures", () => {
  const fm = (id: string): string =>
    `---\nid: operating.${id}\nnamespace: operating\ntitle: ${id}\nowner: o\nstatus: active\nreview_by: "2027-01-01"\nsensitivity: internal\nsource: authored\ntags: []\nsupersedes: []\n---\n\n# ${id}\n`;

  it("skips excluded subtrees and any-depth basenames", async () => {
    const root = mkdtempSync(join(tmpdir(), "team-ai-kbx-"));
    mkdirSync(join(root, "archive"), { recursive: true });
    mkdirSync(join(root, "skills", "x"), { recursive: true });
    writeFileSync(join(root, "keep.md"), fm("keep"), "utf8");
    writeFileSync(join(root, "archive", "old.md"), "no front matter", "utf8");
    writeFileSync(join(root, "skills", "x", "SKILL.md"), "---\nname: x\n---\n", "utf8");
    const docs = await loadKb(root, { exclude: ["archive/", "**/SKILL.md"] });
    expect(docs.map((d) => d.path)).toEqual(["keep.md"]);
    rmSync(root, { recursive: true, force: true });
  });

  it("reports an unparseable file as a failure instead of throwing a YAML error", async () => {
    const root = mkdtempSync(join(tmpdir(), "team-ai-kbp-"));
    writeFileSync(join(root, "keep.md"), fm("keep"), "utf8");
    writeFileSync(join(root, "bad.md"), "---\ndescription: a: b: c\n  nested: here\n---\n", "utf8");
    await expect(loadKb(root)).rejects.toSatisfy(
      (err: unknown) =>
        err instanceof KbValidationError && err.failures.some((f) => f.file === "bad.md"),
    );
    rmSync(root, { recursive: true, force: true });
  });
});
