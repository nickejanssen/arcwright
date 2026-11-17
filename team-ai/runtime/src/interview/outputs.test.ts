import { mkdtempSync, readdirSync, readFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { parse as parseYaml } from "yaml";
import { afterAll, describe, expect, it } from "vitest";

import { validate } from "../schema/validate.js";
import { loadBank } from "./bank.js";
import { Engine } from "./engine.js";
import { writeOutputs } from "./outputs.js";
import type { Question } from "./types.js";

const bank = loadBank();
const tempDirs: string[] = [];

function tempDir(): string {
  const dir = mkdtempSync(join(tmpdir(), "team-ai-outputs-"));
  tempDirs.push(dir);
  return dir;
}

function pick(q: Question): unknown {
  if (q.type === "multi_select") {
    if (Array.isArray(q.default)) return q.default;
    const first = q.options[0];
    return first ? [first.value] : [];
  }
  return q.default ?? q.options[0]?.value ?? "x";
}

function fullRun(overrides: Record<string, unknown> = {}): Engine {
  const engine = new Engine(bank);
  for (let guard = 0; guard < 500; guard += 1) {
    const step = engine.next();
    if (step === null) break;
    if (step.kind === "gate") {
      engine.confirmGate(step.gate);
      continue;
    }
    const forced = overrides[step.question.id];
    engine.answer(step.question.id, forced ?? pick(step.question));
  }
  return engine;
}

function stopAt(phase: string): Engine {
  const engine = new Engine(bank);
  for (let guard = 0; guard < 500; guard += 1) {
    const step = engine.next();
    if (engine.save().phase === phase) return engine;
    if (step === null) break;
    if (step.kind === "gate") {
      engine.confirmGate(step.gate);
      continue;
    }
    engine.answer(step.question.id, pick(step.question));
  }
  return engine;
}

afterAll(() => undefined);

describe("writeOutputs", () => {
  it("writes the seven files, and team-profile.yaml validates", async () => {
    const dir = tempDir();
    const engine = fullRun({
      "arch.index_driver": "vector-embedded",
      "agents.domains": "payments, onboarding",
    });
    const { written } = await writeOutputs(engine, dir);

    expect(written).toEqual([
      "docs/agent-plan.md",
      "docs/architecture.md",
      "docs/decisions/adr-0001-scaffold-choices.md",
      "docs/preflight.md",
      "docs/strategy.md",
      "index.lock",
      "team-profile.yaml",
    ]);
    for (const rel of written) {
      expect(readFileSync(join(dir, rel), "utf8").length).toBeGreaterThan(0);
    }

    const profile: unknown = parseYaml(readFileSync(join(dir, "team-profile.yaml"), "utf8"));
    expect(validate("team-profile", profile).ok).toBe(true);

    expect(readFileSync(join(dir, "index.lock"), "utf8")).toContain("driver: vector-embedded");
    expect(readFileSync(join(dir, "docs/architecture.md"), "utf8")).toContain("Server gates");
    expect(
      readFileSync(join(dir, "docs/decisions/adr-0001-scaffold-choices.md"), "utf8"),
    ).toContain("Status:** Accepted");
  });

  it("maps a decide-later driver to lexical in index.lock", async () => {
    const dir = tempDir();
    const engine = fullRun({ "kb.substrate": "db-native", "arch.index_driver": "decide-later" });
    await writeOutputs(engine, dir);
    expect(readFileSync(join(dir, "index.lock"), "utf8")).toContain("driver: lexical");
  });

  it("is idempotent: a second run rewrites exactly the same file set", async () => {
    const dir = tempDir();
    const engine = fullRun();
    const first = await writeOutputs(engine, dir);
    const second = await writeOutputs(engine, dir);
    expect(second.written).toEqual(first.written);

    const onDisk = readdirSync(join(dir, "docs")).sort();
    expect(onDisk).toEqual([
      "agent-plan.md",
      "architecture.md",
      "decisions",
      "preflight.md",
      "strategy.md",
    ]);
  });

  it("refuses to write before all three gates are confirmed", async () => {
    const engine = stopAt("gate:2");
    expect(engine.save().phase).toBe("gate:2");
    await expect(writeOutputs(engine, tempDir())).rejects.toThrow(/gate/);
  });
});
