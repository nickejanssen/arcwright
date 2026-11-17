import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { afterEach, describe, expect, it } from "vitest";

import { gapVsQualityBar } from "./gap.js";

const dirs: string[] = [];

function makeRepo(files: Record<string, string>): string {
  const dir = mkdtempSync(join(tmpdir(), "team-ai-gap-"));
  dirs.push(dir);
  for (const [rel, content] of Object.entries(files)) {
    const full = join(dir, rel);
    mkdirSync(join(full, ".."), { recursive: true });
    writeFileSync(full, content, "utf8");
  }
  return dir;
}

afterEach(() => {
  for (const dir of dirs.splice(0)) rmSync(dir, { recursive: true, force: true });
});

describe("gapVsQualityBar", () => {
  it("returns exactly 17 entries, each with a non-empty closesWith", () => {
    const repo = makeRepo({ "docs/readme.md": "# Docs\n" });
    const gap = gapVsQualityBar(repo);

    expect(gap.map((g) => g.id)).toEqual(Array.from({ length: 17 }, (_, i) => `q${i + 1}`));
    for (const entry of gap) {
      expect(entry.closesWith.length).toBeGreaterThan(0);
      expect(entry.evidence.length).toBeGreaterThan(0);
    }
  });

  it("always marks q17 satisfied by the adopt run itself", () => {
    const repo = makeRepo({ "README.md": "empty\n" });
    const q17 = gapVsQualityBar(repo).find((g) => g.id === "q17");
    expect(q17?.satisfied).toBe(true);
  });

  it("detects docs/, evals/, scripts/, and an ADR file", () => {
    const repo = makeRepo({
      "docs/decisions/adr-0001-thing.md": "# ADR\n",
      "evals/golden/.keep": "",
      "scripts/build.sh": "echo hi\n",
    });
    const gap = gapVsQualityBar(repo);
    const by = (id: string): boolean => gap.find((g) => g.id === id)?.satisfied ?? false;

    expect(by("q1")).toBe(true);
    expect(by("q5")).toBe(true);
    expect(by("q6")).toBe(true);
    expect(by("q13")).toBe(true);
  });

  it("flags a hardcoded provider string for q15", () => {
    const repo = makeRepo({
      "docs/x.md": "# x\n",
      "src/client.ts": "const key = process.env.ANTHROPIC_API_KEY;\n",
    });
    const q15 = gapVsQualityBar(repo).find((g) => g.id === "q15");
    expect(q15?.satisfied).toBe(false);
  });
});
