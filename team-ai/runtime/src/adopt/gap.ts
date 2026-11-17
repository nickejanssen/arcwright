// Deterministic. No model calls. No network.
//
// gapVsQualityBar scores an existing repo against the 17 quality-bar questions
// (docs/quality-bar.md) using fixed filesystem checks. Nine of the seventeen
// lines cannot be proven from a repo scan alone; those return an honest
// `satisfied: false` with a `closesWith` that names the team-ai feature which
// would close the gap. Nothing here reads a model or the network.

import { existsSync, readdirSync, readFileSync, statSync, type Dirent } from "node:fs";
import { join } from "node:path";

import type { GapEntry } from "./types.js";

interface CheckResult {
  satisfied: boolean;
  evidence: string;
}

type Check = (root: string) => CheckResult;

const SKIP_DIRS = new Set([".git", "node_modules", "dist", "build", "coverage", ".team-ai"]);
const SCAN_EXT = /\.(ts|js|mjs|cjs|py|json)$/;
const PROVIDER_TOKEN = /(?:^|[^a-z])(anthropic|openai)(?:[^a-z]|$)/i;
const MAX_SCAN_FILES = 2000;

function isDir(target: string): boolean {
  try {
    return statSync(target).isDirectory();
  } catch {
    return false;
  }
}

function walk(absDir: string, limit: number): string[] {
  const out: string[] = [];
  const stack: string[] = [absDir];
  while (stack.length > 0 && out.length < limit) {
    const current = stack.pop();
    if (current === undefined) break;
    let entries: Dirent[];
    try {
      entries = readdirSync(current, { withFileTypes: true });
    } catch {
      continue;
    }
    for (const entry of entries) {
      if (entry.isDirectory()) {
        if (!SKIP_DIRS.has(entry.name)) stack.push(join(current, entry.name));
      } else if (entry.isFile()) {
        out.push(join(current, entry.name));
      }
    }
  }
  return out;
}

function fileMatchingUnder(dir: string, pattern: RegExp): string | null {
  if (!isDir(dir)) return null;
  for (const abs of walk(dir, MAX_SCAN_FILES)) {
    if (pattern.test(abs.split(/[/\\]/).pop() ?? "")) return abs;
  }
  return null;
}

function firstExisting(root: string, candidates: string[]): string | null {
  for (const rel of candidates) {
    if (existsSync(join(root, rel))) return rel;
  }
  return null;
}

const NOT_DETECTABLE = "not detectable from the repo";

// id -> [check, closesWith]. Order is q1..q17.
const CHECKS: Record<string, { check: Check; closesWith: string }> = {
  q1: {
    check: (root) => {
      const dir = isDir(join(root, "kb")) ? "kb/" : isDir(join(root, "docs")) ? "docs/" : null;
      return dir === null
        ? { satisfied: false, evidence: "no kb/ or docs/ directory" }
        : { satisfied: true, evidence: `markdown docs in ${dir}` };
    },
    closesWith: "add front matter + `team-ai reindex`",
  },
  q2: {
    check: (root) => {
      const dir = firstExisting(root, ["agents", ".claude/agents"]);
      return dir === null
        ? { satisfied: false, evidence: "no agents/ or .claude/agents/ directory" }
        : { satisfied: true, evidence: `${dir}/ present` };
    },
    closesWith: "define agents in `agents/*.yaml`",
  },
  q3: {
    check: (root) =>
      existsSync(join(root, ".team-ai.yaml"))
        ? { satisfied: true, evidence: ".team-ai.yaml present" }
        : { satisfied: false, evidence: "no .team-ai.yaml" },
    closesWith: "`team-ai attach`",
  },
  q4: {
    check: () => ({ satisfied: false, evidence: NOT_DETECTABLE }),
    closesWith:
      "`team-ai init` lays down the toolkit + instance split; `team-ai spoke` when a domain outgrows the core",
  },
  q5: {
    check: (root) => {
      const hit = fileMatchingUnder(join(root, "docs"), /adr|decision/i);
      return hit === null
        ? { satisfied: false, evidence: "no ADR/decision file under docs/" }
        : {
            satisfied: true,
            evidence: `decision record: ${hit.split(/[/\\]/).slice(-2).join("/")}`,
          };
    },
    closesWith: "record an adversarial review",
  },
  q6: {
    check: (root) =>
      isDir(join(root, "evals"))
        ? { satisfied: true, evidence: "evals/ present" }
        : { satisfied: false, evidence: "no evals/ directory" },
    closesWith: "`team-ai run-evals` + gates",
  },
  q7: {
    check: () => ({ satisfied: false, evidence: NOT_DETECTABLE }),
    closesWith: "`team-ai init` resolves catalog presets per team (toolkit -> org -> instance)",
  },
  q8: {
    check: (root) => {
      const setup = existsSync(join(root, "SETUP.md"));
      const doctor = fileMatchingUnder(join(root, "scripts"), /doctor/i);
      if (setup) return { satisfied: true, evidence: "SETUP.md present" };
      if (doctor !== null) {
        return { satisfied: true, evidence: `setup script: ${doctor.split(/[/\\]/).pop() ?? ""}` };
      }
      return { satisfied: false, evidence: "no SETUP.md or doctor script" };
    },
    closesWith: "`team-ai doctor`",
  },
  q9: {
    check: () => ({ satisfied: false, evidence: NOT_DETECTABLE }),
    closesWith: "this adopt gap report + `docs/quality-bar.md`",
  },
  q10: {
    check: () => ({ satisfied: false, evidence: NOT_DETECTABLE }),
    closesWith: "`team-ai init` records demand gates instead of building ahead of them",
  },
  q11: {
    check: () => ({ satisfied: false, evidence: NOT_DETECTABLE }),
    closesWith:
      "lexical retrieval via `team-ai reindex`; revisit vector/graph against the golden set",
  },
  q12: {
    check: () => ({ satisfied: false, evidence: NOT_DETECTABLE }),
    closesWith: "deterministic work in `team-ai` commands, model work in `SKILL.md` templates",
  },
  q13: {
    check: (root) => {
      const dir = isDir(join(root, "scripts"));
      const make = existsSync(join(root, "Makefile"));
      if (dir) return { satisfied: true, evidence: "scripts/ present" };
      if (make) return { satisfied: true, evidence: "Makefile present" };
      return { satisfied: false, evidence: "no scripts/ or Makefile" };
    },
    closesWith: "use scripts for deterministic work",
  },
  q14: {
    check: () => ({ satisfied: false, evidence: NOT_DETECTABLE }),
    closesWith: "generation is non-destructive; review the diff in a PR",
  },
  q15: {
    check: (root) => {
      const routing = fileMatchingUnder(join(root, "config"), /^routing.*\.json$/i);
      if (routing !== null) {
        return {
          satisfied: true,
          evidence: `routing config: config/${routing.split(/[/\\]/).pop() ?? ""}`,
        };
      }
      for (const abs of walk(root, MAX_SCAN_FILES)) {
        if (!SCAN_EXT.test(abs)) continue;
        let content: string;
        try {
          content = readFileSync(abs, "utf8");
        } catch {
          continue;
        }
        if (PROVIDER_TOKEN.test(content)) {
          return {
            satisfied: false,
            evidence: `provider string in ${abs.split(/[/\\]/).slice(-2).join("/")}`,
          };
        }
      }
      return {
        satisfied: true,
        evidence: "no routing config and no hardcoded provider strings found",
      };
    },
    closesWith: "route models through one config",
  },
  q16: {
    check: () => ({ satisfied: false, evidence: NOT_DETECTABLE }),
    closesWith: "every agent carries a `model_tier`; evals fail on a tier-ceiling breach",
  },
  q17: {
    check: () => ({ satisfied: true, evidence: "this `team-ai adopt` run" }),
    closesWith: "—",
  },
};

export function gapVsQualityBar(root: string): GapEntry[] {
  const out: GapEntry[] = [];
  for (let n = 1; n <= 17; n += 1) {
    const id = `q${n}`;
    const spec = CHECKS[id];
    if (spec === undefined) continue;
    const { satisfied, evidence } = spec.check(root);
    out.push({ id, satisfied, evidence, closesWith: spec.closesWith });
  }
  return out;
}
