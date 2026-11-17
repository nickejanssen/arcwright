import { existsSync, mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { afterEach, describe, expect, it, vi } from "vitest";

import { parseDenylist, run, scanAgnostic } from "./check-agnostic.js";

const log = vi.spyOn(console, "log").mockImplementation(() => undefined);
const error = vi.spyOn(console, "error").mockImplementation(() => undefined);

const dirs: string[] = [];

function makeTree(files: Record<string, string>): string {
  const dir = mkdtempSync(join(tmpdir(), "team-ai-agnostic-"));
  dirs.push(dir);
  for (const [rel, content] of Object.entries(files)) {
    const full = join(dir, rel);
    mkdirSync(join(full, ".."), { recursive: true });
    writeFileSync(full, content, "utf8");
  }
  return dir;
}

afterEach(() => {
  log.mockClear();
  error.mockClear();
  for (const dir of dirs.splice(0)) rmSync(dir, { recursive: true, force: true });
});

describe("parseDenylist", () => {
  it("splits denied and allowlisted terms, ignoring comments and blanks", () => {
    const { denied, allow } = parseDenylist(
      "# c\n\nArcwright\nMonster RPG\n!Nickejanssen/team-ai\n",
    );
    expect(denied).toEqual(["arcwright", "monster rpg"]);
    expect(allow).toEqual(["nickejanssen/team-ai"]);
  });
});

describe("scanAgnostic", () => {
  it("flags a denied token in a shipped source file with file:line:term", () => {
    const dir = makeTree({
      "src/thing.ts": "const a = 1;\n// built for Arcwright Studios\nexport const b = 2;\n",
    });
    const hits = scanAgnostic(dir);
    expect(hits).toEqual([{ file: "src/thing.ts", line: 2, term: "arcwright" }]);
  });

  it("does not flag an allowlisted token", () => {
    const dir = makeTree({
      "src/thing.ts": "// repo github.com/nickejanssen/team-ai owned by nickejanssen\n",
    });
    expect(scanAgnostic(dir)).toEqual([]);
  });

  it("skips *.test.ts and fixtures/ files", () => {
    const dir = makeTree({
      "src/thing.test.ts": "// Arcwright\n",
      "src/x/fixtures/sample.ts": "// Nightcap\n",
      "src/x/fixtures/deep/a.json": '{ "team": "Vesper" }\n',
    });
    expect(scanAgnostic(dir)).toEqual([]);
  });

  it("matches a multi-word denied term across the space", () => {
    const dir = makeTree({ "schemas/x.schema.json": '{ "title": "monster rpg profile" }\n' });
    expect(scanAgnostic(dir).map((h) => h.term)).toEqual(["monster rpg"]);
  });

  it("returns no hits for the real framework tree", () => {
    expect(scanAgnostic(process.cwd())).toEqual([]);
  });
});

describe("check-agnostic run", () => {
  it("exits 0 and reports a scan count on the current repo", async () => {
    const code = await run({});
    expect(code).toBe(0);
    expect(String(log.mock.calls[0]?.[0])).toMatch(
      /^check-agnostic: OK \(\d+ files scanned, 0 denied tokens\)$/,
    );
  });

  it("exits 1 when a planted token is present in src/", async () => {
    const probe = join(process.cwd(), "src", "__agnostic_probe__.ts");
    writeFileSync(probe, "// planted: arcwright\nexport const probe = true;\n", "utf8");
    try {
      const code = await run({});
      expect(code).toBe(1);
      const printed = error.mock.calls.map((c) => String(c[0])).join("\n");
      expect(printed).toContain("src/__agnostic_probe__.ts:1: contains denied token 'arcwright'");
    } finally {
      if (existsSync(probe)) rmSync(probe);
    }
  });
});
