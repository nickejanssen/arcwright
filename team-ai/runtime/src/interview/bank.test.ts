import { describe, expect, it } from "vitest";

import { loadBank, type Question } from "./bank.js";
import { validate } from "../schema/validate.js";

const bank = loadBank();
const byId = new Map(bank.map((q) => [q.id, q]));

const ACT_0_2_IDS = [
  "pre.assessment",
  "pre.overlap",
  "pre.probe_result",
  "mode",
  "ctx.org_path",
  "team.name",
  "team.mission",
  "team.size",
  "team.surfaces",
  "team.sources",
  "team.consumers",
  "kb.substrate",
  "kb.namespaces",
  "kb.catalog_override",
  "kb.sources_strategy",
  "kb.sensitivity",
  "kb.write_back",
].sort();

const ACT_3_4_IDS = [
  "arch.index_driver",
  "kb.graph_questions",
  "arch.hosting",
  "arch.language",
  "arch.ci",
  "arch.topology",
  "arch.model_tiers",
  "arch.cache",
  "agents.roles",
  "agents.domains",
  "agents.personas",
  "agents.skills",
  "agents.strictness",
  "agents.seed",
].sort();

const CITATION = /docs\/quality-bar\.md#q(1[0-7]|[1-9])\b/;

function idsForActs(min: number, max: number): string[] {
  return bank
    .filter((q) => q.act >= min && q.act <= max)
    .map((q) => q.id)
    .sort();
}

describe("loadBank", () => {
  it("parses, validates, and returns a plausible number of questions", () => {
    expect(bank.length).toBeGreaterThanOrEqual(24);
    expect(bank.length).toBeLessThanOrEqual(32);
  });

  it("has unique ids", () => {
    expect(byId.size).toBe(bank.length);
  });

  it("cites a real quality-bar item in every why", () => {
    for (const q of bank) {
      expect(q.why, `${q.id} why`).toMatch(CITATION);
    }
  });

  it("matches the Act 0-2 id set exactly", () => {
    expect(idsForActs(0, 2)).toEqual(ACT_0_2_IDS);
  });

  it("matches the Act 3-4 id set exactly", () => {
    expect(idsForActs(3, 4)).toEqual(ACT_3_4_IDS);
  });

  it("only implies 'warn' or a real question id", () => {
    for (const q of bank) {
      for (const option of q.options) {
        for (const key of Object.keys(option.implies ?? {})) {
          const known = key === "warn" || byId.has(key);
          expect(known, `${q.id} option ${option.value} implies ${key}`).toBe(true);
        }
      }
    }
  });

  it("gives select-type questions options and leaves text/confirm without them", () => {
    for (const q of bank) {
      if (q.type === "text" || q.type === "confirm") {
        expect(q.options, q.id).toEqual([]);
      } else {
        expect(q.options.length, q.id).toBeGreaterThan(0);
      }
    }
  });

  it("normalizes allow_defer to a boolean on every question", () => {
    for (const q of bank) {
      expect(typeof q.allow_defer, q.id).toBe("boolean");
    }
  });

  it("requires recommend_why wherever a recommendation is present", () => {
    for (const q of bank) {
      if (q.recommend !== undefined) {
        expect(typeof q.recommend_why, q.id).toBe("string");
        expect((q.recommend_why ?? "").length, q.id).toBeGreaterThan(0);
      }
    }
  });

  it("gates ctx.org_path on mode and agents.roles on team size", () => {
    const orgPath = byId.get("ctx.org_path");
    expect(orgPath).toBeDefined();
    expect(orgPath?.ask_if).toContain("mode");
    expect(orgPath?.ask_if).toContain("!=");

    const roles = byId.get("agents.roles");
    expect(roles?.ask_if).toContain("team.size");
    expect(roles?.ask_if).toContain("!=");
    expect(roles?.ask_if).toContain("1-3");
  });

  it("keeps kb.substrate implies pointing at real downstream questions", () => {
    const substrate = byId.get("kb.substrate");
    const mdGit = substrate?.options.find((o) => o.value === "md-git");
    expect(mdGit?.implies).toMatchObject({
      "arch.index_driver": "lexical",
      "kb.write_back": "pr-only",
    });
  });
});

describe("questions schema", () => {
  const base: Question = {
    id: "x.sample",
    act: 1,
    type: "text",
    prompt: "p",
    why: "see docs/quality-bar.md#q1 here",
    options: [],
    allow_defer: false,
    ask_if: "always",
  };

  it("rejects a why with no quality-bar citation", () => {
    const r = validate("questions", { questions: [{ ...base, why: "no citation here" }] });
    expect(r.ok).toBe(false);
    if (!r.ok) expect(r.errors.join("\n")).toMatch(/why|pattern/i);
  });

  it("rejects options on a text question", () => {
    const r = validate("questions", {
      questions: [{ ...base, options: [{ value: "a", label: "A" }] }],
    });
    expect(r.ok).toBe(false);
  });

  it("rejects a select question with no options", () => {
    const r = validate("questions", {
      questions: [{ ...base, type: "single_select" }],
    });
    expect(r.ok).toBe(false);
  });

  it("rejects recommend without recommend_why", () => {
    const r = validate("questions", {
      questions: [
        {
          id: "x.y",
          act: 0,
          type: "text",
          prompt: "p",
          why: base.why,
          ask_if: "always",
          recommend: "a",
        },
      ],
    });
    expect(r.ok).toBe(false);
    if (!r.ok) expect(r.errors.join("\n")).toContain("recommend_why");
  });

  it("accepts the shipped bank", () => {
    const r = validate("questions", {
      questions: bank.map((q) => ({ ...q })),
    });
    expect(r.ok, r.ok ? "" : JSON.stringify(r.errors)).toBe(true);
  });
});
