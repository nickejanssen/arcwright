// Deterministic control flow. No model calls. No network. The only disk write is
// the plan file itself, re-serialized with the operator's approvals folded in.
//
// runInteractive walks a written adoption-plan.yaml and asks the operator to
// approve / skip / edit each backfill and relabel item and to pick a namespace
// for each undecided folder, then writes the choices back into the same file.
// Tests inject a string puller via `opts.answers`; without one it falls back to
// @inquirer/prompts.

import { readFileSync, writeFileSync } from "node:fs";

import { input, select } from "@inquirer/prompts";
import { parse as parseYaml, stringify as stringifyYaml } from "yaml";

import { validate } from "../schema/validate.js";
import type { AdoptionPlan } from "./types.js";
import type { FrontMatter } from "../schema/types.js";

export interface RunInteractiveOptions {
  answers?: () => Promise<string>;
}

const VALID_STATUSES = new Set<FrontMatter["status"]>(["draft", "active", "deprecated"]);

function isValidStatus(value: string): value is FrontMatter["status"] {
  return VALID_STATUSES.has(value as FrontMatter["status"]);
}

type Decision = "approve" | "skip" | "edit";

function parseDecision(token: string): Decision {
  const t = token.trim().toLowerCase();
  if (t === "approve" || t === "a" || t === "yes" || t === "y") return "approve";
  if (t === "edit" || t === "e") return "edit";
  return "skip";
}

function loadPlan(planPath: string): AdoptionPlan {
  const raw: unknown = parseYaml(readFileSync(planPath, "utf8"));
  const result = validate("adoption-plan", raw);
  if (!result.ok) {
    throw new Error(
      `team-ai adopt: ${planPath} is not a valid adoption plan: ${result.errors[0] ?? ""}`,
    );
  }
  return result.value;
}

export async function runInteractive(
  planPath: string,
  opts: RunInteractiveOptions = {},
): Promise<void> {
  const plan = loadPlan(planPath);
  const pull = opts.answers;

  const askDecision = async (label: string): Promise<Decision> => {
    if (pull) return parseDecision(await pull());
    return select<Decision>({
      message: label,
      choices: [
        { value: "approve", name: "approve" },
        { value: "skip", name: "skip" },
        { value: "edit", name: "edit (owner, status)" },
      ],
    });
  };

  const askValue = async (label: string): Promise<string> => {
    if (pull) return (await pull()).trim();
    return (await input({ message: label })).trim();
  };

  const askPick = async (label: string, choices: string[]): Promise<string> => {
    if (pull) {
      const answer = (await pull()).trim();
      const byIndex = /^\d+$/.test(answer) ? choices[Number.parseInt(answer, 10) - 1] : undefined;
      return byIndex ?? answer;
    }
    return select<string>({
      message: label,
      choices: choices.map((value) => ({ value, name: value })),
    });
  };

  for (const item of plan.backfill) {
    const decision = await askDecision(`Backfill ${item.path}?`);
    if (decision === "approve") {
      item.approved = true;
    } else if (decision === "edit") {
      const owner = await askValue(
        `New owner for ${item.path} (blank to keep "${item.frontmatter.owner}")`,
      );
      if (owner.length > 0) item.frontmatter.owner = owner;

      // A backfilled doc always starts life as "active" (infer.ts has no way
      // to know a doc is a placeholder awaiting real content). Editing status
      // here is how a human corrects that — e.g. a story-bible placeholder
      // that should read `draft` until its real GDD lands, not `active`
      // alongside content that's actually authoritative.
      const status = await askValue(
        `Status for ${item.path} — draft | active | deprecated ` +
          `(blank to keep "${item.frontmatter.status}")`,
      );
      if (status.length > 0) {
        if (isValidStatus(status)) {
          item.frontmatter.status = status;
        } else {
          console.error(
            `"${status}" is not draft | active | deprecated — keeping "${item.frontmatter.status}" for ${item.path}`,
          );
        }
      }
      item.approved = true;
    } else {
      item.approved = false;
    }
  }

  for (const item of plan.relabels) {
    const decision = await askDecision(`Relabel ${item.path} source -> ${item.proposed_source}?`);
    item.approved = decision === "approve" || decision === "edit";
  }

  for (const decision of plan.namespace_map.decisions) {
    const pick = await askPick(`Namespace for ${decision.folder}/`, decision.candidates);
    decision.chosen = pick.length > 0 ? pick : null;
  }

  writeFileSync(planPath, stringifyYaml(plan), "utf8");
}
