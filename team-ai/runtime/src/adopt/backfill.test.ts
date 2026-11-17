import { mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { afterEach, describe, expect, it } from "vitest";

import { validate } from "../schema/validate.js";
import { applyFrontmatter, hasFrontmatter } from "./backfill.js";
import { inferFrontmatter } from "./infer.js";

const dirs: string[] = [];

function tmpFile(name: string, content: string): string {
  const dir = mkdtempSync(join(tmpdir(), "team-ai-backfill-"));
  dirs.push(dir);
  const path = join(dir, name);
  writeFileSync(path, content, "utf8");
  return path;
}

const fm = inferFrontmatter({
  relPath: "operating/charter.md",
  body: "# Charter\n",
  namespace: "operating",
  gitAuthors: ["Ada"],
  horizonDays: 180,
  today: new Date("2026-08-31T00:00:00Z"),
});

afterEach(() => {
  for (const dir of dirs.splice(0)) rmSync(dir, { recursive: true, force: true });
});

describe("applyFrontmatter", () => {
  it("dry-run returns a content string that opens with a front-matter block", () => {
    const path = tmpFile("charter.md", "# Charter\n\nBody.\n");
    const result = applyFrontmatter(path, fm, { dryRun: true });

    expect(result.ok).toBe(true);
    expect(result.content?.startsWith("---\n")).toBe(true);
    // Nothing was written.
    expect(readFileSync(path, "utf8")).toBe("# Charter\n\nBody.\n");
    const parsed = result.content ?? "";
    expect(parsed).toContain("# Charter");
  });

  it("writes the front matter when not a dry run and it re-parses as valid", async () => {
    const path = tmpFile("charter.md", "# Charter\n\nBody.\n");
    const result = applyFrontmatter(path, fm, {});
    expect(result.ok).toBe(true);

    const written = readFileSync(path, "utf8");
    expect(written.startsWith("---\n")).toBe(true);

    const { parseFrontmatter } = await import("../kb/frontmatter.js");
    expect(validate("frontmatter", parseFrontmatter(written).data).ok).toBe(true);
  });

  it("refuses a file that already has front matter and leaves it untouched", () => {
    const original = "---\ntitle: Existing\n---\n\n# Charter\n";
    const path = tmpFile("charter.md", original);
    const result = applyFrontmatter(path, fm, {});

    expect(result.ok).toBe(false);
    expect(result.reason).toMatch(/already/);
    expect(readFileSync(path, "utf8")).toBe(original);
  });

  it("detects CRLF-fronted front matter that an exact '---\\n' prefix check would miss", () => {
    // A real file can legitimately open with "---\r\n" (CRLF). Confirmed against
    // a real Arcwright file during dogfooding: an exact "---\n" prefix check
    // reads this as having NO front matter, which would make apply prepend a
    // second block on top of the real one.
    const original = "---\r\ntitle: Existing\r\n---\r\n\r\n# Charter\r\n";
    const path = tmpFile("charter.md", original);

    expect(hasFrontmatter(original)).toBe(true);

    const result = applyFrontmatter(path, fm, {});
    expect(result.ok).toBe(false);
    expect(result.reason).toMatch(/already/);
    expect(readFileSync(path, "utf8")).toBe(original);
  });

  it("hasFrontmatter is false for a file with no front matter at all", () => {
    expect(hasFrontmatter("# Charter\n\nBody.\n")).toBe(false);
  });
});
