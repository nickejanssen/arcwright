// Fully deterministic — no model calls. Measures an existing repo against the framework standard.
//
// `team-ai adopt` has three modes:
//   (default)       build and write the adoption plan, print a summary
//   --interactive   walk the written plan and record approvals into it
//   --apply         write the approved parts of the plan into the repo

import { readFileSync } from "node:fs";
import { join } from "node:path";

import { parse as parseYaml } from "yaml";

import { applyPlan } from "../adopt/apply.js";
import { runInteractive } from "../adopt/interactive.js";
import { buildAdoptionPlan, countAlreadyStale } from "../adopt/plan.js";

export interface AdoptCommandOptions {
  root?: string;
  out?: string;
  horizonDays?: number | string;
  namespaceMap?: string;
  interactive?: boolean;
  apply?: boolean;
  includeArchived?: boolean;
}

const PLAN_FILE = "adoption-plan.yaml";

function horizon(value: number | string | undefined): number {
  if (typeof value === "number") return value;
  if (typeof value === "string") {
    const n = Number.parseInt(value, 10);
    if (Number.isFinite(n) && n > 0) return n;
  }
  return 180;
}

function readNamespaceMap(file: string): Record<string, string> {
  const parsed: unknown = parseYaml(readFileSync(file, "utf8"));
  if (parsed === null || typeof parsed !== "object" || Array.isArray(parsed)) return {};
  const out: Record<string, string> = {};
  for (const [key, value] of Object.entries(parsed as Record<string, unknown>)) {
    if (typeof value === "string") out[key] = value;
  }
  return out;
}

export async function run(opts: AdoptCommandOptions): Promise<number> {
  const root = opts.root ?? ".";
  const out = opts.out ?? ".";
  const planPath = join(out, PLAN_FILE);

  if (opts.interactive === true) {
    await runInteractive(planPath);
    console.log(
      `Recorded your choices in ${planPath}. Run \`team-ai adopt --apply\` to write them.`,
    );
    return 0;
  }

  if (opts.apply === true) {
    const result = await applyPlan(planPath, { root });
    console.log(
      `applied ${result.applied.length} / skipped ${result.skipped.length} / ` +
        `conflicts ${result.conflicts.length}`,
    );
    return result.conflicts.length > 0 ? 1 : 0;
  }

  const namespaceMap =
    opts.namespaceMap !== undefined ? readNamespaceMap(opts.namespaceMap) : undefined;

  const plan = await buildAdoptionPlan({
    root,
    out,
    horizonDays: horizon(opts.horizonDays),
    includeArchived: opts.includeArchived === true,
    ...(namespaceMap !== undefined ? { namespaceMap } : {}),
  });

  const satisfied = plan.gap.filter((g) => g.satisfied).length;
  console.log(
    `${plan.backfill.length} backfill items, ${plan.namespace_map.decisions.length} ` +
      `namespace decisions, gap: ${satisfied}/17 satisfied, ${plan.collisions.length} collisions`,
  );
  console.log(
    `skipped ${plan.archived_skipped} archived/generated docs (--include-archived to include)`,
  );
  console.log(
    `${countAlreadyStale(plan)} of those backfill items are already due for review on arrival ` +
      "(anchored on last git edit, not on today)",
  );
  console.log(
    "review docs/adoption-plan.md, then `team-ai adopt --interactive` and `team-ai adopt --apply`",
  );
  return 0;
}
