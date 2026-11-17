import { mkdtempSync, readdirSync, readFileSync, statSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { afterEach, describe, expect, it, vi } from "vitest";

import { generateInstance } from "./fixtures/instance-fixture.js";
import { run } from "./review.js";

const log = vi.spyOn(console, "log").mockImplementation(() => undefined);
const error = vi.spyOn(console, "error").mockImplementation(() => undefined);
afterEach(() => {
  log.mockClear();
  error.mockClear();
});

function snapshot(dir: string): Record<string, string> {
  const out: Record<string, string> = {};
  for (const rel of readdirSync(dir, { recursive: true }) as string[]) {
    const abs = join(dir, rel);
    const st = statSync(abs);
    if (st.isFile()) out[rel] = `${st.size}:${st.mtimeMs}:${readFileSync(abs, "utf8").length}`;
  }
  return out;
}

describe("team-ai review", () => {
  it("prints the three gate summaries and writes nothing", async () => {
    const dir = mkdtempSync(join(tmpdir(), "team-ai-review-"));
    expect(await generateInstance(dir)).toBe(0);

    const before = snapshot(dir);
    const lines: string[] = [];
    const code = await run({ dir, output: (s) => lines.push(s) });
    expect(code).toBe(0);
    expect(snapshot(dir)).toEqual(before);

    const text = lines.join("\n");
    expect(text).toMatch(/atlasdata/);
    expect(text.length).toBeGreaterThan(0);
  });

  it("returns 1 when there is no team-profile.yaml", async () => {
    const dir = mkdtempSync(join(tmpdir(), "team-ai-review-"));
    const code = await run({ dir, output: () => undefined });
    expect(code).toBe(1);
  });
});
