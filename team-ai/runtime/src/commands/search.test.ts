import { cpSync, mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { afterEach, describe, expect, it, vi } from "vitest";

import { run as reindex } from "./reindex.js";
import { run as search } from "./search.js";
import type { Hit } from "../retrieval/types.js";

const log = vi.spyOn(console, "log").mockImplementation(() => undefined);
const error = vi.spyOn(console, "error").mockImplementation(() => undefined);

const dirs: string[] = [];

function makeInstance(): string {
  const root = mkdtempSync(join(tmpdir(), "team-ai-search-"));
  dirs.push(root);
  cpSync("src/kb/fixtures/kb", join(root, "kb"), { recursive: true });
  return root;
}

async function indexed(): Promise<string> {
  const root = makeInstance();
  await reindex({ root });
  log.mockClear();
  return root;
}

afterEach(() => {
  log.mockClear();
  error.mockClear();
  for (const dir of dirs.splice(0)) rmSync(dir, { recursive: true, force: true });
});

describe("search", () => {
  it("returns 1 with a hint when the index is not built", async () => {
    const root = makeInstance();
    const code = await search("429 rate limit errors", { root });

    expect(code).toBe(1);
    expect(error).toHaveBeenCalledWith("index not built — run 'team-ai reindex' first");
  });

  it("prints ranked lines for a relevant query", async () => {
    const root = await indexed();
    const code = await search("429 rate limit errors", { root, k: 5, json: true });

    expect(code).toBe(0);
    const relevant = JSON.parse(String(log.mock.calls[0]?.[0])) as Hit[];
    expect(relevant.length).toBeGreaterThan(0);

    log.mockClear();
    const nonsenseCode = await search("kubernetes helm chart", { root, k: 5, json: true });
    expect(nonsenseCode).toBe(0);
    const nonsense = JSON.parse(String(log.mock.calls[0]?.[0])) as Hit[];
    const nonsenseTop = nonsense[0]?.score ?? 0;
    expect(relevant[0]!.score).toBeGreaterThan(nonsenseTop);
  });

  it("emits a parseable Hit[] with --json", async () => {
    const root = await indexed();
    const code = await search("429 rate limit errors", { root, json: true });

    expect(code).toBe(0);
    const payload: unknown = JSON.parse(String(log.mock.calls[0]?.[0]));
    expect(Array.isArray(payload)).toBe(true);
    const hits = payload as Hit[];
    expect(hits[0]?.path).toBe("platform/rate-limits.md");
    expect(typeof hits[0]?.score).toBe("number");
  });

  it("refuses with 'no results above threshold' for an irrelevant query", async () => {
    const root = await indexed();
    const code = await search("kubernetes helm chart", { root });

    expect(code).toBe(0);
    expect(log).toHaveBeenCalledWith("no results above threshold");
  });

  it("filters by namespace", async () => {
    const root = await indexed();

    const miss = await search("429 rate limit errors", { root, namespace: ["operating"] });
    expect(miss).toBe(0);
    expect(log).toHaveBeenCalledWith("no results above threshold");

    log.mockClear();
    const hit = await search("429 rate limit errors", { root, namespace: ["platform"] });
    expect(hit).toBe(0);
    const lines = log.mock.calls.map((c) => String(c[0]));
    expect(lines.some((l) => l.includes("platform/rate-limits.md"))).toBe(true);
  });
});
