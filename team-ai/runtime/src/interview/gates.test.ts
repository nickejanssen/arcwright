import { describe, expect, it } from "vitest";

import { loadBank } from "./bank.js";
import { Engine } from "./engine.js";
import { collectDeferred, renderGate } from "./gates.js";
import type { Question } from "./types.js";

const bank = loadBank();

function pick(q: Question): unknown {
  if (q.type === "multi_select") {
    if (Array.isArray(q.default)) return q.default;
    const first = q.options[0];
    return first ? [first.value] : [];
  }
  return q.default ?? q.options[0]?.value ?? "x";
}

// Scripts a full run to `phase: "done"`, deferring `arch.index_driver` so the
// deferred list has a stable entry, and naming two domains for gate 3.
function scriptedEngine(): Engine {
  const engine = new Engine(bank);
  for (let guard = 0; guard < 500; guard += 1) {
    const step = engine.next();
    if (step === null) break;
    if (step.kind === "gate") {
      engine.confirmGate(step.gate);
      continue;
    }
    const id = step.question.id;
    if (id === "arch.index_driver") {
      engine.answer(id, "__defer__");
    } else if (id === "agents.domains") {
      engine.answer(id, "payments, onboarding");
    } else if (id === "team.size") {
      engine.answer(id, "4-8");
    } else {
      engine.answer(id, pick(step.question));
    }
  }
  return engine;
}

describe("renderGate", () => {
  const engine = scriptedEngine();

  it("gate 1 fits one page and states the strategy", () => {
    const out = renderGate(1, engine);
    expect(out.split("\n").length).toBeLessThanOrEqual(45);
    expect(out).toContain("STRATEGY SUMMARY");
    expect(out).toContain("Write-back");
    expect(out).toContain("Namespaces");
  });

  it("gate 1 lists a deferred answer with its revisit checkpoint", () => {
    const out = renderGate(1, engine);
    expect(out).toContain("DEFERRED (defaults applied, revisit later)");
    expect(out).toContain(
      "arch.index_driver → lexical (defer), revisit: phase-8 checkpoint with eval data",
    );
    expect(collectDeferred(engine.save().answers).some((e) => e.id === "arch.index_driver")).toBe(
      true,
    );
  });

  it("gate 2 shows the fixed cost preview and both server gates", () => {
    const out = renderGate(2, engine);
    expect(out.split("\n").length).toBeLessThanOrEqual(45);
    expect(out).toContain("COST PREVIEW");
    expect(out).toContain("~40  cache hits           no model");
    expect(out).toContain("~40  retrieve + cite       small model");
    expect(out).toContain("Gate: local stdio server  when a 2nd coding client appears");
    expect(out).toContain("Gate: remote server       after 2 asks from non-repo users");
    expect(out).toContain("telemetry at phase 4");
  });

  it("gate 3 lays out the agent plan", () => {
    const out = renderGate(3, engine);
    expect(out.split("\n").length).toBeLessThanOrEqual(45);
    expect(out).toContain("AGENT PLAN");
    expect(out).toContain("ROUTER");
    expect(out).toContain("sme  tier: none → small on ambiguity  refuses + logs a gap");
    expect(out).toContain("payments-sme   ns: operating   small   hops 0");
    expect(out).toContain("core: kb-answer, kb-contribute, audit-summary, sme-route");
    expect(out).toContain("reindex, validate-kb, validate-citations");
    expect(out).toMatch(/20 golden questions stubbed across \d+ namespaces/);
  });

  it("gate 3 suppresses role subagents for a team of 3 or fewer", () => {
    const small = new Engine(bank);
    for (let guard = 0; guard < 500; guard += 1) {
      const step = small.next();
      if (step === null) break;
      if (step.kind === "gate") {
        small.confirmGate(step.gate);
        continue;
      }
      small.answer(
        step.question.id,
        step.question.id === "team.size" ? "1-3" : pick(step.question),
      );
    }
    expect(renderGate(3, small)).toContain("none (team of 3 or fewer — domain agents only)");
  });
});
