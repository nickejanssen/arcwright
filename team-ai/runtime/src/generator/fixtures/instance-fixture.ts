// Test support (imported only by *.test.ts). Drives `init.run` with a scripted
// answer puller to produce a complete generated instance on disk, so the
// resume / review / upgrade / emit tests have a realistic tree to operate on.
// Not wired into the CLI.

import { loadBank } from "../../interview/bank.js";
import { Engine } from "../../interview/engine.js";
import type { Question } from "../../interview/types.js";
import { run as initRun } from "../init.js";

const OVERRIDES: Record<string, unknown> = {
  "pre.assessment": "coexist",
  "pre.overlap": "decide-later",
  "pre.probe_result": "continue",
  mode: "instance",
  "ctx.org_path": "testorg",
  "team.name": "atlasdata",
  "team.mission": "Own the customer data platform",
  "team.size": "4-8",
  "team.surfaces": ["coding-agent"],
  "team.sources": ["github"],
  "team.consumers": ["engineers"],
  "kb.substrate": "md-git",
  "kb.namespaces": "engineering",
  "kb.catalog_override": "use-preset",
  "kb.sources_strategy": "link-only",
  "kb.sensitivity": "three-tiers",
  "kb.write_back": "pr-only",
  "arch.index_driver": "lexical",
  "arch.hosting": "no-server",
  "arch.language": "typescript",
  "arch.ci": "github-actions",
  "arch.topology": "single-repo",
  "arch.model_tiers": "balanced",
  "arch.cache": "yes",
  "agents.roles": ["architect"],
  "agents.domains": "billing api",
  "agents.personas": ["internal-technical"],
  "agents.skills": [],
  "agents.strictness": "refuse-log-gap",
  "agents.seed": "yes-5-starter-docs",
};

function scriptedAnswers(overrides: Record<string, unknown>): string[] {
  const engine = new Engine(loadBank());
  const out: string[] = [];
  for (let guard = 0; guard < 500; guard += 1) {
    const step = engine.next();
    if (step === null) break;
    if (step.kind === "gate") {
      out.push("confirm");
      engine.confirmGate(step.gate);
      continue;
    }
    const q: Question = step.question;
    let value: unknown;
    if (q.id in overrides) value = overrides[q.id];
    else if (q.type === "multi_select") value = Array.isArray(q.default) ? q.default : [];
    else if (q.default !== undefined) value = q.default;
    else if (q.type === "single_select") value = q.options[0]?.value;
    else value = `${q.id}-value`;
    out.push(Array.isArray(value) ? value.join(",") : String(value));
    engine.answer(q.id, value);
  }
  return out;
}

function puller(queue: string[]): () => Promise<string> {
  let idx = 0;
  return () => Promise.resolve(queue[idx++] ?? "");
}

export async function generateInstance(
  dir: string,
  overrides: Record<string, unknown> = {},
): Promise<number> {
  const merged = { ...OVERRIDES, ...overrides };
  return initRun({ dir, answers: puller(scriptedAnswers(merged)), output: () => undefined });
}
