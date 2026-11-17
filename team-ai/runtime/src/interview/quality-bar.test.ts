import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

// Repo root: this file lives at src/interview/, two segments below the root.
const ROOT = fileURLToPath(new URL("../../", import.meta.url));

const qualityBar = readFileSync(join(ROOT, "docs/quality-bar.md"), "utf8");
const questions = readFileSync(join(ROOT, "src/interview/questions.yaml"), "utf8");

const ANCHOR_IDS = new Set(
  [...qualityBar.matchAll(/id="q(\d+)"/g)].map((m) => Number.parseInt(m[1] as string, 10)),
);

const CITATIONS = [...questions.matchAll(/docs\/quality-bar\.md#q(\d+)/g)].map((m) =>
  Number.parseInt(m[1] as string, 10),
);

// Path tokens that look like a repo path, harvested from the enforcement lines.
const ENFORCEMENT_PATHS = [...qualityBar.matchAll(/\*\*Where it's enforced:\*\*(.+)/g)].flatMap(
  (m) =>
    [...(m[1] as string).matchAll(/`([^`]+)`/g)]
      .map((b) => (b[1] as string).replace(/\/$/, ""))
      .filter((p) => /^(src|schemas|catalog|templates|evals)\//.test(p)),
);

describe("docs/quality-bar.md", () => {
  it("has an explicit anchor for all 17 questions", () => {
    for (let n = 1; n <= 17; n += 1) {
      expect(ANCHOR_IDS.has(n), `missing id="q${n}"`).toBe(true);
    }
    expect([...ANCHOR_IDS].sort((a, b) => a - b)).toEqual(
      Array.from({ length: 17 }, (_, i) => i + 1),
    );
  });

  it("notes the sixteen-versus-seventeen discrepancy", () => {
    expect(qualityBar.toLowerCase()).toMatch(/sixteen/);
    expect(qualityBar).toMatch(/authoritative/i);
  });

  it("has a contributor checklist", () => {
    expect(qualityBar).toMatch(/Contributor checklist/i);
  });

  it("resolves every quality-bar citation in questions.yaml", () => {
    expect(CITATIONS.length).toBeGreaterThan(0);
    for (const n of CITATIONS) {
      expect(n, `citation #q${n} out of range`).toBeGreaterThanOrEqual(1);
      expect(n, `citation #q${n} out of range`).toBeLessThanOrEqual(17);
      expect(ANCHOR_IDS.has(n), `citation #q${n} has no anchor in quality-bar.md`).toBe(true);
    }
  });

  it("every 'Where it's enforced' repo path exists", () => {
    expect(ENFORCEMENT_PATHS.length).toBeGreaterThan(10);
    for (const p of ENFORCEMENT_PATHS) {
      expect(existsSync(join(ROOT, p)), `enforcement path missing: ${p}`).toBe(true);
    }
  });
});
