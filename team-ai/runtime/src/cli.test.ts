import { mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { afterEach, describe, expect, it, vi } from "vitest";

import { buildProgram, main } from "./cli.js";
import * as init from "./generator/init.js";
import { packageVersion } from "./version.js";

describe("cli module", () => {
  it("exports main as a function", () => {
    expect(typeof main).toBe("function");
  });
});

describe("buildProgram", () => {
  const dirs: string[] = [];

  afterEach(() => {
    vi.restoreAllMocks();
    for (const dir of dirs.splice(0)) rmSync(dir, { recursive: true, force: true });
  });

  it("registers every command", () => {
    const program = buildProgram();
    const names = program.commands.map((c) => c.name()).sort();
    expect(names).toContain("validate-kb");
    expect(names).toContain("validate-citations");
    expect(names).toContain("validate-spoke");
    expect(names).toContain("reindex");
    expect(names).toContain("search");
    expect(names).toContain("assemble-manifest");
    expect(names).toContain("freshness-audit");
    expect(names).toContain("check-agnostic");
    expect(names).toContain("doctor");
    expect(names).toContain("init");
    expect(names).toContain("adopt");
  });

  it("declares the search positional argument", () => {
    const searchCommand = buildProgram().commands.find((c) => c.name() === "search");
    expect(searchCommand?.usage()).toContain("<query>");
  });

  it("reports the package version", () => {
    expect(buildProgram().version()).toBe(packageVersion());
  });

  it("gives every registered command a description", () => {
    for (const command of buildProgram().commands) {
      expect(command.description().length).toBeGreaterThan(0);
    }
  });

  it("advertises keyed answers and legacy positional lists", () => {
    const command = buildProgram().commands.find((c) => c.name() === "init");
    const help = command?.helpInformation();
    expect(help).toContain("keyed YAML mapping by question id");
    expect(help).toContain("lists also supported");
  });

  it("prints a warning for an answers entry that init never asks", async () => {
    const dir = mkdtempSync(join(tmpdir(), "team-ai-cli-answers-"));
    dirs.push(dir);
    const answers = join(dir, "answers.yaml");
    writeFileSync(answers, "unused.key: x\n", "utf8");
    vi.spyOn(init, "run").mockResolvedValue(0);
    const error = vi.spyOn(console, "error").mockImplementation(() => undefined);
    vi.spyOn(process, "exit").mockImplementation((() => undefined) as never);

    const command = buildProgram().commands.find((c) => c.name() === "init");
    await command?.parseAsync(["node", "team-ai", "--answers", answers]);

    expect(error).toHaveBeenCalledWith(
      "WARNING: answers file entry 'unused.key' was never asked (pre-filled or skipped)",
    );
  });
});
