import { describe, expect, it } from "vitest";

import { loadBank } from "./bank.js";
import { Engine, type EngineState } from "./engine.js";
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

function runToDone(
  engine: Engine,
  overrides: Record<string, unknown> = {},
): {
  emitted: string[];
  state: EngineState;
} {
  const emitted: string[] = [];
  for (let guard = 0; guard < 500; guard++) {
    const step = engine.next();
    if (step === null) break;
    if (step.kind === "gate") {
      engine.confirmGate(step.gate);
      continue;
    }
    emitted.push(step.question.id);
    const forced = overrides[step.question.id];
    engine.answer(step.question.id, forced ?? pick(step.question));
  }
  return { emitted, state: engine.save() };
}

describe("Engine", () => {
  it("suppresses agents.roles for a team of 1-3", () => {
    const engine = new Engine(bank);
    const { emitted, state } = runToDone(engine, { "team.size": "1-3" });
    expect(emitted).not.toContain("agents.roles");
    expect(state.phase).toBe("done");
  });

  it("derives arch.index_driver from kb.substrate and an explicit answer overrides it", () => {
    const engine = new Engine(bank);
    engine.answer("kb.substrate", "md-git");
    expect(engine.effectiveAnswers()["arch.index_driver"]).toBe("lexical");

    engine.answer("arch.index_driver", "vector-embedded");
    expect(engine.effectiveAnswers()["arch.index_driver"]).toBe("vector-embedded");
    expect(engine.save().derived["arch.index_driver"]?.overridden).toBe(true);
  });

  it("refuses to skip a question that does not allow defer", () => {
    const engine = new Engine(bank);
    expect(() => engine.skip("team.name")).toThrow(/does not allow defer/);
  });

  it("records a deferred answer as the question default", () => {
    const engine = new Engine(bank);
    engine.answer("kb.substrate", "__defer__");
    const rec = engine.save().answers["kb.substrate"];
    expect(rec?.via).toBe("defer");
    expect(rec?.value).toBe("md-git");
  });

  it("records a recommended answer with its rationale", () => {
    const engine = new Engine(bank);
    engine.answer("kb.substrate", "__recommend__");
    const rec = engine.save().answers["kb.substrate"];
    expect(rec?.via).toBe("recommend");
    expect(rec?.value).toBe("md-git");
    expect(typeof rec?.why).toBe("string");
    expect((rec?.why ?? "").length).toBeGreaterThan(0);
  });

  it("re-answers consistently: new derivations replace old, history stays single, one back undoes it", () => {
    const engine = new Engine(bank);

    engine.answer("kb.substrate", "md-git");
    expect(engine.effectiveAnswers()["arch.index_driver"]).toBe("lexical");
    expect(engine.effectiveAnswers()["kb.write_back"]).toBe("pr-only");

    engine.answer("kb.substrate", "db-native");
    // db-native implies only `warn` — every prior derivation is retracted.
    expect(engine.effectiveAnswers()["arch.index_driver"]).toBeUndefined();
    expect(engine.effectiveAnswers()["kb.write_back"]).toBeUndefined();
    expect(engine.save().derived).toEqual({});
    expect(engine.warnings()).toContain("kb.substrate");

    const state = engine.save();
    expect(state.history.filter((h) => h === "kb.substrate")).toEqual(["kb.substrate"]);

    engine.back();
    const after = engine.save();
    expect(after.answers["kb.substrate"]).toBeUndefined();
    expect(after.derived).toEqual({});
    expect(after.history).toEqual([]);
  });

  it("keeps the graph follow-up in act 3 so a confirmed gate 1 is never jumped back over", () => {
    const engine = new Engine(bank);
    const phases: string[] = [];
    for (let guard = 0; guard < 500; guard++) {
      const step = engine.next();
      phases.push(engine.save().phase);
      if (step === null) break;
      if (step.kind === "gate") {
        engine.confirmGate(step.gate);
        continue;
      }
      // Force the graph driver so kb.graph_questions becomes askable.
      engine.answer(
        step.question.id,
        step.question.id === "arch.index_driver" ? "graph" : pick(step.question),
      );
    }

    const emitted = engine.save().history;
    expect(emitted).toContain("kb.graph_questions");
    // The follow-up is asked inside act 3, before gate 2.
    const graphIdx = emitted.indexOf("kb.graph_questions");
    const driverIdx = emitted.indexOf("arch.index_driver");
    expect(graphIdx).toBeGreaterThan(driverIdx);
    // Phase never regresses to act:2 once gate:1 has been seen.
    const gate1At = phases.indexOf("gate:1");
    expect(gate1At).toBeGreaterThanOrEqual(0);
    expect(phases.slice(gate1At + 1)).not.toContain("act:2");
    expect(engine.save().phase).toBe("done");
  });

  it("validates option values on direct answers", () => {
    const engine = new Engine(bank);
    expect(() => engine.answer("kb.substrate", "nope")).toThrow(/not a valid option/);
    expect(() => engine.answer("team.surfaces", "chat-apps")).toThrow(/expects an array/);
    expect(() => engine.answer("team.surfaces", ["chat-apps", "nope"])).toThrow(
      /not a valid option/,
    );
  });

  it("steps back over the last answer and re-offers it, and no-ops on empty history", () => {
    const engine = new Engine(bank);
    engine.back(); // empty history: no throw

    let step = engine.next();
    const seen: string[] = [];
    while (step && step.kind === "question" && step.question.act <= 2) {
      seen.push(step.question.id);
      engine.answer(step.question.id, pick(step.question));
      step = engine.next();
    }
    const last = seen.at(-1)!;
    engine.back();

    const reoffered = engine.next();
    expect(reoffered?.kind).toBe("question");
    if (reoffered?.kind === "question") expect(reoffered.question.id).toBe(last);
    expect(engine.save().answers[last]).toBeUndefined();
  });

  it("un-confirms a gate when back() reopens one of its act's questions", () => {
    const engine = new Engine(bank);
    let step = engine.next();
    while (step && step.kind === "question") {
      engine.answer(step.question.id, pick(step.question));
      step = engine.next();
      if (step && step.kind === "gate") break;
    }
    engine.confirmGate(1);
    expect(engine.save().confirmedGates).toContain(1);

    engine.back(); // pops the last act-2 answer
    expect(engine.save().confirmedGates).not.toContain(1);
    expect(engine.next()?.kind).toBe("question");
  });

  it("emits gate 1 after act 2, advances on confirm, and rejects the wrong gate number", () => {
    const engine = new Engine(bank);
    let step = engine.next();
    while (step && step.kind === "question") {
      engine.answer(step.question.id, pick(step.question));
      step = engine.next();
      if (step && step.kind === "gate") break;
    }
    expect(step).toEqual({ kind: "gate", gate: 1 });
    expect(() => engine.confirmGate(2)).toThrow(/gate 2 is not the current step/);

    engine.confirmGate(1);
    const afterGate = engine.next();
    expect(afterGate?.kind).toBe("question");
    if (afterGate?.kind === "question") expect(afterGate.question.act).toBe(3);
  });

  it("completes a full scripted run and then returns null", () => {
    const engine = new Engine(bank);
    const { state } = runToDone(engine);
    expect(state.phase).toBe("done");
    expect(engine.next()).toBeNull();
  });

  it("round-trips through save/load to the same step", () => {
    const engine = new Engine(bank);
    engine.answer("mode", "instance");
    engine.answer("team.name", "Acme");
    const saved = engine.save();
    const before = engine.next();

    const reloaded = Engine.load(bank, saved);
    expect(reloaded.next()).toEqual(before);
  });

  it("reports a warning for an option that surfaces implies.warn", () => {
    const engine = new Engine(bank);
    engine.answer("arch.model_tiers", "no-constraints");
    expect(engine.warnings()).toContain("arch.model_tiers");
  });

  it("does not mutate answers when next() is called repeatedly", () => {
    const engine = new Engine(bank);
    engine.answer("mode", "instance");
    const a = engine.next();
    const b = engine.next();
    expect(a).toEqual(b);
    expect(Object.keys(engine.save().answers)).toEqual(["mode"]);
  });
});
