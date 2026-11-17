import { mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { afterEach, describe, expect, it } from "vitest";

import { loadAnswerFile } from "./init-answers.js";

const dirs: string[] = [];

function file(content: string): string {
  const dir = mkdtempSync(join(tmpdir(), "team-ai-answers-"));
  dirs.push(dir);
  const path = join(dir, "answers.yaml");
  writeFileSync(path, content, "utf8");
  return path;
}

afterEach(() => {
  for (const dir of dirs.splice(0)) rmSync(dir, { recursive: true, force: true });
});

describe("loadAnswerFile — keyed", () => {
  it("answers by key in any order and joins arrays", async () => {
    const answers = loadAnswerFile(
      file("team.name: Acme\nagents.personas: [a, b]\ngate.1: confirm\n"),
    );
    expect(await answers.pull("gate.1")).toBe("confirm");
    expect(await answers.pull("agents.personas")).toBe("a,b");
    expect(await answers.pull("team.name")).toBe("Acme");
  });

  it("rejects a key with no entry, naming it", async () => {
    const answers = loadAnswerFile(file("team.name: Acme\n"));
    await expect(answers.pull("team.size")).rejects.toThrow(/team\.size/);
  });

  it("rejects a repeated request for the same key", async () => {
    const answers = loadAnswerFile(file("team.size: nonsense\n"));
    await answers.pull("team.size");
    await expect(answers.pull("team.size")).rejects.toThrow(/not accepted/);
  });

  it.each(["why", "back", "save"])("rejects control word %s at load time", (word) => {
    expect(() => loadAnswerFile(file(`team.name: ${word}\n`))).toThrow(/control word/);
  });

  it("rejects a control word inside an array at load time", () => {
    expect(() => loadAnswerFile(file("team.name: [Acme, back, writer]\n"))).toThrow(/control word/);
  });

  it("reports entries that were never requested", async () => {
    const answers = loadAnswerFile(file("team.name: Acme\nunused.key: x\n"));
    await answers.pull("team.name");
    expect(answers.unusedKeys()).toEqual(["unused.key"]);
  });
});

describe("loadAnswerFile — positional", () => {
  it("still replays a list in order", async () => {
    const answers = loadAnswerFile(file("- one\n- two\n"));
    expect(await answers.pull("anything")).toBe("one");
    expect(await answers.pull("anything")).toBe("two");
  });
});
