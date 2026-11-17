import { cpSync, existsSync, mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { afterEach, describe, expect, it, vi } from "vitest";

import { run } from "./reindex.js";

const log = vi.spyOn(console, "log").mockImplementation(() => undefined);
const error = vi.spyOn(console, "error").mockImplementation(() => undefined);

const dirs: string[] = [];

function makeInstance(withKb: boolean): string {
  const dir = mkdtempSync(join(tmpdir(), "team-ai-reindex-"));
  dirs.push(dir);
  if (withKb) cpSync("src/kb/fixtures/kb", join(dir, "kb"), { recursive: true });
  return dir;
}

afterEach(() => {
  log.mockClear();
  error.mockClear();
  for (const dir of dirs.splice(0)) rmSync(dir, { recursive: true, force: true });
});

describe("reindex", () => {
  it("creates index.lock, writes the index under the instance dir, and reports stats", async () => {
    const dir = makeInstance(true);
    const code = await run({ root: dir });

    expect(code).toBe(0);
    expect(existsSync(join(dir, "index.lock"))).toBe(true);
    expect(existsSync(join(dir, ".team-ai", "index.sqlite"))).toBe(true);

    const printed = log.mock.calls.map((c) => String(c[0])).join("\n");
    expect(printed).toContain("wrote index.lock");
    expect(printed).toMatch(/indexed 3 document\(s\), \d+ chunk\(s\) via lexical in \d+ms/);
  });

  it("does not re-note index.lock when it already exists", async () => {
    const dir = makeInstance(true);
    await run({ root: dir });
    log.mockClear();

    const code = await run({ root: dir });
    expect(code).toBe(0);
    const printed = log.mock.calls.map((c) => String(c[0])).join("\n");
    expect(printed).not.toContain("wrote index.lock");
  });

  it("returns 1 when the instance has no kb/ directory", async () => {
    const dir = makeInstance(false);
    const code = await run({ root: dir });

    expect(code).toBe(1);
    const printed = error.mock.calls.map((c) => String(c[0])).join("\n");
    expect(printed).toMatch(/KB root not found/);
  });
});
