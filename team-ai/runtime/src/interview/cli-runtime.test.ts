import { existsSync, mkdtempSync, readFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { describe, expect, it } from "vitest";

import { runInterviewCli } from "./cli-runtime.js";
import type { EngineState } from "./engine.js";

function tempCwd(): string {
  return mkdtempSync(join(tmpdir(), "team-ai-cli-"));
}

// A puller backed by a scripted list of lines, consumed in order.
function scripted(lines: string[], keys: string[] = []): (key: string) => Promise<string> {
  let i = 0;
  return (key) => {
    keys.push(key);
    const value = lines[i];
    i += 1;
    if (value === undefined) throw new Error(`puller exhausted after ${lines.length} lines`);
    return Promise.resolve(value);
  };
}

describe("runInterviewCli", () => {
  it("walks the whole interview, honouring why / back / defer and confirming every gate", async () => {
    const out: string[] = [];
    const keys: string[] = [];
    const lines = [
      "why", // pre.assessment: explain, then re-ask
      "extend", // pre.assessment
      "decide-later", // pre.overlap
      "continue", // pre.probe_result
      "instance", // mode
      "defer", // ctx.org_path (deferrable text)
      "Platform Team", // team.name
      "back", // at team.mission -> pop team.name
      "Platform Team", // team.name again
      "Runs the shared platform", // team.mission
      "4-8", // team.size
      "coding-agent", // team.surfaces
      "github", // team.sources
      "engineers", // team.consumers
      "md-git", // kb.substrate
      "generic", // kb.namespaces
      "use-preset", // kb.catalog_override
      "link-only", // kb.sources_strategy
      "three-tiers", // kb.sensitivity
      "pr-only", // kb.write_back
      "confirm", // GATE 1
      "lexical", // arch.index_driver
      "no-server", // arch.hosting
      "typescript", // arch.language
      "github-actions", // arch.ci
      "toolkit-plus-instance", // arch.topology
      "balanced", // arch.model_tiers
      "yes", // arch.cache
      "confirm", // GATE 2
      "architect", // agents.roles
      "payments, onboarding", // agents.domains
      "internal-technical", // agents.personas
      "kb-answer", // agents.skills
      "refuse-log-gap", // agents.strictness
      "yes-5-starter-docs", // agents.seed
      "confirm", // GATE 3
    ];

    const state: EngineState = await runInterviewCli({
      cwd: tempCwd(),
      answers: scripted(lines, keys),
      output: (line) => out.push(line),
    });

    expect(state.phase).toBe("done");
    expect(state.answers["ctx.org_path"]?.via).toBe("defer");
    expect(state.answers["team.name"]?.value).toBe("Platform Team");

    const joined = out.join("\n");
    // "why" surfaced the question's rationale, and the prompt was shown again.
    expect(joined).toContain("docs/quality-bar.md#q17");
    const promptCount = out.filter((l) =>
      l.startsWith("How should this setup relate to the AI infrastructure"),
    ).length;
    expect(promptCount).toBeGreaterThanOrEqual(2);
    expect(keys).toContain("pre.assessment");
    expect(keys).toContain("gate.1");
    expect(keys).toContain("gate.2");
    expect(keys).toContain("gate.3");
  });

  it("writes the resume file and returns partial state on 'save'", async () => {
    const cwd = tempCwd();
    const state = await runInterviewCli({
      cwd,
      answers: scripted(["extend", "save"]),
      output: () => undefined,
    });

    const resume = join(cwd, ".team-ai-interview-state.json");
    expect(existsSync(resume)).toBe(true);

    const parsed = JSON.parse(readFileSync(resume, "utf8")) as { phase?: unknown };
    expect(typeof parsed.phase).toBe("string");
    expect(state.phase).not.toBe("done");
    expect(state.answers["pre.assessment"]?.value).toBe("extend");
  });
});
