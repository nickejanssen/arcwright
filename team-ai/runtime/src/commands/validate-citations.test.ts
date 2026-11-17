import { cpSync, mkdirSync, mkdtempSync, renameSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { afterEach, describe, expect, it, vi } from "vitest";

import { run } from "./validate-citations.js";

const log = vi.spyOn(console, "log").mockImplementation(() => undefined);
const error = vi.spyOn(console, "error").mockImplementation(() => undefined);

const dirs: string[] = [];

afterEach(() => {
  log.mockClear();
  error.mockClear();
  for (const dir of dirs.splice(0)) rmSync(dir, { recursive: true, force: true });
});

describe("validate-citations", () => {
  it("passes when every citation resolves", async () => {
    const code = await run({ root: "src/commands/fixtures/cited-repo-ok" });
    expect(code).toBe(0);
    expect(String(log.mock.calls[0]?.[0])).toMatch(/^OK \d+ citation\(s\) across \d+ file\(s\)$/);
  });

  it("reports an unresolved citation", async () => {
    const code = await run({ root: "src/commands/fixtures/cited-repo" });
    expect(code).toBe(1);
    const printed = error.mock.calls.map((c) => String(c[0])).join("\n");
    expect(printed).toContain("platform/nope.md");
    expect(printed).toMatch(/kb\/platform\/y\.md: platform\/nope\.md — /);
  });

  it("fails when neither kb/ nor agents/ exists under the root", async () => {
    const code = await run({ root: "src/commands/fixtures/does-not-exist" });
    expect(code).toBe(1);
    expect(error).toHaveBeenCalledWith(
      "no kb/ or agents/ under src/commands/fixtures/does-not-exist",
    );
  });

  it("does not throw on front-matter-invalid KB docs, but returns 1 with a note", async () => {
    const code = await run({ root: "src/commands/fixtures/cited-repo-broken" });
    expect(code).toBe(1);
    const printed = error.mock.calls.map((c) => String(c[0])).join("\n");
    expect(printed.toLowerCase()).toContain("front matter");
  });

  it("checks the declared KB root and skips excluded documents", async () => {
    const dir = mkdtempSync(join(tmpdir(), "team-ai-citations-"));
    dirs.push(dir);
    cpSync("src/commands/fixtures/cited-repo-ok", dir, { recursive: true });
    renameSync(join(dir, "kb"), join(dir, "docs"));
    mkdirSync(join(dir, "docs", "archive"), { recursive: true });
    writeFileSync(join(dir, "docs", "archive", "bad.md"), "no front matter", "utf8");
    writeFileSync(
      join(dir, "index.lock"),
      "driver: lexical\nchunk:\n  split_on: [h2, h3]\n  target_tokens: 800\n  hard_cap: 1200\nembedding: null\nkb:\n  root: docs\n  exclude: [archive/]\n",
      "utf8",
    );

    expect(await run({ root: dir })).toBe(0);
  });

  it("labels citation failures with the declared KB root", async () => {
    const dir = mkdtempSync(join(tmpdir(), "team-ai-citations-"));
    dirs.push(dir);
    cpSync("src/commands/fixtures/cited-repo", dir, { recursive: true });
    renameSync(join(dir, "kb"), join(dir, "docs"));
    writeFileSync(
      join(dir, "index.lock"),
      "driver: lexical\nchunk:\n  split_on: [h2, h3]\n  target_tokens: 800\n  hard_cap: 1200\nembedding: null\nkb:\n  root: docs\n  exclude: []\n",
      "utf8",
    );

    expect(await run({ root: dir })).toBe(1);
    const printed = error.mock.calls.map((c) => String(c[0])).join("\n");
    expect(printed).toMatch(/docs\/platform\/y\.md: platform\/nope\.md/);
  });

  it("reports a malformed index.lock instead of rejecting", async () => {
    const dir = mkdtempSync(join(tmpdir(), "team-ai-citations-"));
    dirs.push(dir);
    writeFileSync(join(dir, "index.lock"), "driver: ''\n", "utf8");

    await expect(run({ root: dir })).resolves.toBe(1);
    expect(error.mock.calls.map((c) => String(c[0])).join("\n")).toMatch(/invalid index\.lock/);
  });
});
