import { describe, expect, it } from "vitest";

import type { PreflightReport } from "../interview/preflight.js";
import { planReconcile } from "./reconcile.js";
import type { RenderResult } from "./render.js";

function renderResult(collisions: string[] = []): RenderResult {
  return {
    created: [],
    unchanged: [],
    updated: [],
    collisions,
    siblingsWritten: [],
    warnings: [],
    manifestEntries: [],
  };
}

function preflight(overrides: Partial<PreflightReport> = {}): PreflightReport {
  return {
    found: { mcpServers: [], agentConfig: [], vectorStore: [], orgSearch: [], skillsPlugins: [] },
    existingAssets: { agents: [], kbDocCount: 0, skills: [] },
    assessment: "coexist",
    rationale: "nothing conclusive",
    ...overrides,
  };
}

describe("planReconcile", () => {
  it("asks the operator to choose when a dry render found collisions", () => {
    const decision = planReconcile(
      renderResult(["agents/sme.yaml", "manifest.yaml"]),
      preflight(),
      undefined,
    );
    expect(decision.needsPrompt).toBe(true);
    expect(decision.plan).toBeUndefined();
    for (const word of ["adopt-existing", "siblings", "subdir", "abort"]) {
      expect(decision.promptText).toContain(word);
    }
  });

  it("does not prompt once a strategy has been supplied", () => {
    const decision = planReconcile(renderResult(["agents/sme.yaml"]), preflight(), "siblings");
    expect(decision.needsPrompt).toBe(false);
    expect(decision.plan?.strategy).toBe("siblings");
    expect(decision.plan?.collisions).toEqual(["agents/sme.yaml"]);
  });

  it("prompts on an extend assessment with an existing router even with zero collisions", () => {
    const decision = planReconcile(
      renderResult([]),
      preflight({
        assessment: "extend",
        existingAssets: {
          agents: ["agents/sme.yaml"],
          kbDocCount: 0,
          skills: [],
          routerAgent: "agents/sme.yaml",
        },
      }),
      undefined,
    );
    expect(decision.needsPrompt).toBe(true);
    expect(decision.promptText).toContain("extend an existing harness");
  });

  it("defaults to adopt-existing when nothing conflicts", () => {
    const decision = planReconcile(renderResult([]), preflight(), undefined);
    expect(decision.needsPrompt).toBe(false);
    expect(decision.plan?.strategy).toBe("adopt-existing");
  });
});
