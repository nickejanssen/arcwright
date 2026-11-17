// Deterministic. No model calls. No network. No disk I/O — pure planning.
//
// `init` never overwrites human work. When a dry render finds collisions, or the
// preflight says "extend" an existing harness that already has a router or an
// agent config file, the operator has to choose how team-ai should lay itself
// down alongside what is there. `planReconcile` decides whether that choice is
// needed and renders the 4-option screen; it does not apply anything.

import type { PreflightReport } from "../interview/preflight.js";
import type { RenderResult } from "./render.js";

export interface ReconcilePlan {
  strategy: "adopt-existing" | "siblings" | "subdir" | "abort";
  collisions: string[];
  existingRouter?: string;
  existingAgentConfig?: string;
}

export interface ReconcileDecision {
  needsPrompt: boolean;
  plan?: ReconcilePlan;
  promptText: string;
}

const DEFAULT_STRATEGY: ReconcilePlan["strategy"] = "adopt-existing";

export const RECONCILE_STRATEGIES: ReconcilePlan["strategy"][] = [
  "adopt-existing",
  "siblings",
  "subdir",
  "abort",
];

function buildPromptText(
  collisions: string[],
  router: string | undefined,
  agentConfig: string | undefined,
): string {
  const lines: string[] = [
    "RECONCILE",
    "",
    "This directory already holds files team-ai would generate, or an agent setup",
    "team-ai should not duplicate. Nothing has been written yet.",
    "",
  ];

  if (collisions.length > 0) {
    lines.push(`Collisions (${collisions.length}):`);
    for (const path of collisions) lines.push(`  - ${path}`);
  } else {
    lines.push("No file collisions, but preflight wants to extend an existing harness.");
  }

  const adopted: string[] = [];
  if (agentConfig !== undefined) adopted.push(`agent config file: ${agentConfig}`);
  if (router !== undefined) adopted.push(`router / SME agent: ${router}`);
  if (adopted.length > 0) {
    lines.push("", "Would adopt (kept in place, registered alongside):");
    for (const item of adopted) lines.push(`  - ${item}`);
  }

  lines.push(
    "",
    "Choose:",
    "  1) adopt-existing — keep your files; skip every collision; register alongside them",
    "  2) siblings       — write team-ai's version beside each as <name>.team-ai-new",
    "  3) subdir         — generate the whole instance into ./team-ai/ instead",
    "  4) abort          — write only the interview profile and gate docs, nothing else",
  );

  return lines.join("\n");
}

export function planReconcile(
  dryRender: RenderResult,
  preflight: PreflightReport | undefined,
  chosen: ReconcilePlan["strategy"] | undefined,
): ReconcileDecision {
  const collisions = [...dryRender.collisions].sort((a, b) => (a < b ? -1 : a > b ? 1 : 0));
  const router = preflight?.existingAssets.routerAgent;
  const agentConfig = preflight?.existingAssets.agentConfigFile;

  const extendConflict =
    preflight?.assessment === "extend" && (router !== undefined || agentConfig !== undefined);

  const needsPrompt = (collisions.length > 0 || extendConflict) && chosen === undefined;
  const promptText = buildPromptText(collisions, router, agentConfig);

  if (needsPrompt) {
    return { needsPrompt: true, promptText };
  }

  const plan: ReconcilePlan = {
    strategy: chosen ?? DEFAULT_STRATEGY,
    collisions,
  };
  if (router !== undefined) plan.existingRouter = router;
  if (agentConfig !== undefined) plan.existingAgentConfig = agentConfig;

  return { needsPrompt: false, plan, promptText };
}

/** Parse an operator's reply to the reconcile screen: a number, or the name. */
export function parseStrategy(raw: string): ReconcilePlan["strategy"] | undefined {
  const token = raw.trim().toLowerCase();
  const byNumber: Record<string, ReconcilePlan["strategy"]> = {
    "1": "adopt-existing",
    "2": "siblings",
    "3": "subdir",
    "4": "abort",
  };
  if (token in byNumber) return byNumber[token];
  return RECONCILE_STRATEGIES.find((s) => s === token);
}
