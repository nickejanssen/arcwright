// Deterministic. No model calls. No network.
//
// applyPlan writes the approved parts of an adoption plan into the repo:
// front-matter backfill for un-annotated docs, `source:` relabels for docs a
// sync pipeline owns, and namespace decisions into `.team-ai-namespaces.yaml`.
// It never deletes, never touches an un-approved item, and is idempotent — a
// second run over the same plan reports everything as already applied.

import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";

import { parse as parseYaml, stringify as stringifyYaml } from "yaml";

import * as validateKb from "../commands/validate-kb.js";
import { parseFrontmatter, serializeFrontmatter } from "../kb/frontmatter.js";
import type { FrontMatter } from "../schema/types.js";
import { validate } from "../schema/validate.js";
import { applyFrontmatter } from "./backfill.js";
import { inferId } from "./infer.js";
import { PENDING_NAMESPACE } from "./types.js";
import type { AdoptionPlan, BackfillItem } from "./types.js";

export interface ApplyPlanOptions {
  root: string;
}

export interface ApplyPlanResult {
  applied: string[];
  skipped: string[];
  conflicts: string[];
}

const NS_FILE = ".team-ai-namespaces.yaml";

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

// A backfill item's path is repo-relative (`docs/<folder>/...`); the namespace
// decision is keyed by `<folder>`.
function folderOf(itemPath: string): string {
  const parts = itemPath.split("/");
  return parts.length >= 3 ? (parts[1] ?? "") : "";
}

// The namespace to write, or `null` when the folder's decision is still open.
function resolvedNamespace(plan: AdoptionPlan, item: BackfillItem): string | null {
  if (item.namespace !== PENDING_NAMESPACE) return item.namespace;
  const decision = plan.namespace_map.decisions.find((d) => d.folder === folderOf(item.path));
  const chosen = decision?.chosen;
  return typeof chosen === "string" && chosen.length > 0 ? chosen : null;
}

function frontmatterFor(item: BackfillItem, namespace: string): FrontMatter {
  if (namespace === item.frontmatter.namespace) return item.frontmatter;
  const relFromDocs = item.path.replace(/^(docs|kb)\//, "");
  return { ...item.frontmatter, namespace, id: inferId(relFromDocs, namespace) };
}

function applyBackfill(plan: AdoptionPlan, root: string, out: ApplyPlanResult): void {
  for (const item of plan.backfill) {
    if (item.approved !== true) {
      out.skipped.push(item.path);
      continue;
    }
    const namespace = resolvedNamespace(plan, item);
    if (namespace === null) {
      out.skipped.push(item.path);
      console.log(`skipped ${item.path} — namespace decision not made`);
      continue;
    }
    const abs = join(root, item.path);
    const result = applyFrontmatter(abs, frontmatterFor(item, namespace), {});
    if (result.ok) {
      out.applied.push(item.path);
    } else if (result.reason === "already has front matter") {
      out.skipped.push(item.path);
    } else {
      out.conflicts.push(item.path);
    }
  }
}

function applyRelabels(plan: AdoptionPlan, root: string, out: ApplyPlanResult): void {
  for (const item of plan.relabels) {
    if (item.approved !== true) {
      out.skipped.push(item.path);
      continue;
    }
    const abs = join(root, item.path);
    let raw: string;
    try {
      raw = readFileSync(abs, "utf8");
    } catch {
      out.conflicts.push(item.path);
      continue;
    }
    if (!raw.startsWith("---\n")) {
      out.skipped.push(item.path);
      continue;
    }
    const { data, body } = parseFrontmatter(raw);
    if (data.source === item.proposed_source) {
      out.skipped.push(item.path);
      continue;
    }
    const next: Record<string, unknown> = { ...data, source: item.proposed_source };
    const check = validate("frontmatter", next);
    if (!check.ok) {
      out.conflicts.push(item.path);
      continue;
    }
    writeFileSync(abs, serializeFrontmatter(next, body), "utf8");
    out.applied.push(item.path);
  }
}

function applyNamespaceDecisions(plan: AdoptionPlan, root: string): void {
  const chosen = plan.namespace_map.decisions.filter(
    (d) => d.chosen !== null && d.chosen.length > 0,
  );
  if (chosen.length === 0) return;

  const abs = join(root, NS_FILE);
  let current: Record<string, unknown> = {};
  if (existsSync(abs)) {
    const parsed: unknown = parseYaml(readFileSync(abs, "utf8"));
    if (parsed !== null && typeof parsed === "object" && !Array.isArray(parsed)) {
      current = parsed as Record<string, unknown>;
    }
  }
  for (const decision of chosen) current[decision.folder] = decision.chosen;
  writeFileSync(abs, stringifyYaml(current), "utf8");
}

function docsRootFor(root: string): string {
  return existsSync(join(root, "docs")) ? join(root, "docs") : join(root, "kb");
}

export async function applyPlan(
  planPath: string,
  opts: ApplyPlanOptions,
): Promise<ApplyPlanResult> {
  const plan = loadPlan(planPath);
  const out: ApplyPlanResult = { applied: [], skipped: [], conflicts: [] };

  applyBackfill(plan, opts.root, out);
  applyRelabels(plan, opts.root, out);
  applyNamespaceDecisions(plan, opts.root);

  const kbExit = await validateKb.run({ root: docsRootFor(opts.root), schemaOnly: true });
  console.log(`validate-kb (schema-only) exit ${kbExit}`);

  return out;
}
