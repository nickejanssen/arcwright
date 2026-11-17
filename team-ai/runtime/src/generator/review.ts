// Deterministic. No model calls. No network. Read-only: writes nothing.
//
// `team-ai review` replays the three interview gate summaries from a saved
// `team-profile.yaml`. It is the way to re-read what was decided without
// re-running the interview or regenerating anything.

import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";

import { parse as parseYaml } from "yaml";

import { loadBank } from "../interview/bank.js";
import { Engine } from "../interview/engine.js";
import { renderGate } from "../interview/gates.js";
import { stateFromProfile, type ProfileShape } from "./state-from-profile.js";

export interface ReviewOptions {
  dir?: string;
  output?: (s: string) => void;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function readProfile(dir: string): ProfileShape | null {
  const file = join(dir, "team-profile.yaml");
  if (!existsSync(file)) return null;
  let parsed: unknown;
  try {
    parsed = parseYaml(readFileSync(file, "utf8"));
  } catch {
    return null;
  }
  if (!isRecord(parsed)) return null;
  const answers = isRecord(parsed.answers) ? parsed.answers : {};
  const deferred = Array.isArray(parsed.deferred)
    ? (parsed.deferred as ProfileShape["deferred"])
    : [];
  return { answers, deferred };
}

export function run(opts: ReviewOptions): Promise<number> {
  const output = opts.output ?? ((s: string): void => console.log(s));
  const dir = opts.dir ?? ".";

  const profile = readProfile(dir);
  if (!profile) {
    output("review: no team-profile.yaml found; run 'team-ai init' first");
    return Promise.resolve(1);
  }

  const bank = loadBank();
  const engine = Engine.load(bank, stateFromProfile(bank, profile));

  output(renderGate(1, engine));
  output(renderGate(2, engine));
  output(renderGate(3, engine));

  return Promise.resolve(0);
}
