// Deterministic. No model calls. No network.
//
// The per-entity instance files `renderTree` does not itself emit: one YAML +
// markdown pair per domain SME and per role subagent, and one markdown file per
// persona. Extracted from `init` so `resume` can re-render the same set without
// importing `init` (which would cycle).

import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import type { RoleArchetype } from "../catalog/types.js";
import { generateStub } from "../catalog/stub.js";
import { resolveWithin } from "./contain.js";
import { sha256Of } from "./generated-manifest.js";
import { renderTemplate, type RenderResult } from "./render.js";

export const TEMPLATES_INSTANCE = fileURLToPath(
  new URL("../../templates/instance", import.meta.url),
);

export type EntityCollisionMode = "siblings" | "skip";

function readTemplate(rel: string): string {
  return readFileSync(join(TEMPLATES_INSTANCE, rel), "utf8");
}

function asDomains(value: unknown): { slug: string; name: string; namespace?: string }[] {
  if (!Array.isArray(value)) return [];
  const out: { slug: string; name: string; namespace?: string }[] = [];
  for (const item of value) {
    if (item !== null && typeof item === "object") {
      const rec = item as Record<string, unknown>;
      if (typeof rec.slug === "string" && typeof rec.name === "string") {
        out.push({
          slug: rec.slug,
          name: rec.name,
          ...(typeof rec.namespace === "string" ? { namespace: rec.namespace } : {}),
        });
      }
    }
  }
  return out;
}

function asRoles(value: unknown): RoleArchetype[] {
  return Array.isArray(value) ? (value as RoleArchetype[]) : [];
}

function asStrings(value: unknown): string[] {
  return Array.isArray(value) ? value.filter((v): v is string => typeof v === "string") : [];
}

// Role and persona names become path segments. They can come from a
// hand-edited team-profile.yaml or a catalog file, neither of which is checked
// against the interview's fixed options, so they are validated before anything
// is written.
const SAFE_NAME = /^[A-Za-z0-9][A-Za-z0-9._-]*$/;

function assertSafeName(kind: "role" | "persona", name: string): void {
  if (!SAFE_NAME.test(name)) {
    throw new Error(
      `invalid ${kind} name '${name}': must be a single path segment of letters, digits, '.', '_' or '-'`,
    );
  }
}

/**
 * Classify one generated file against what is on disk and the prior manifest,
 * then write it unless doing so would clobber human work. Mirrors `renderTree`'s
 * non-destructive semantics for the per-entity files it does not itself emit.
 */
function writeIfSafe(
  outRel: string,
  content: string,
  renderDir: string,
  priorByPath: Map<string, string>,
  onCollision: EntityCollisionMode,
  result: RenderResult,
): void {
  const outAbs = resolveWithin(renderDir, outRel);

  if (!existsSync(outAbs)) {
    result.created.push(outRel);
    result.manifestEntries.push({ path: outRel, sha256: sha256Of(content) });
    mkdirSync(dirname(outAbs), { recursive: true });
    writeFileSync(outAbs, content, "utf8");
    return;
  }

  const current = readFileSync(outAbs, "utf8");
  if (current === content) {
    result.unchanged.push(outRel);
    return;
  }

  const prior = priorByPath.get(outRel);
  if (prior !== undefined && prior === sha256Of(current)) {
    result.updated.push(outRel);
    result.manifestEntries.push({ path: outRel, sha256: sha256Of(content) });
    writeFileSync(outAbs, content, "utf8");
    return;
  }

  result.collisions.push(outRel);
  if (onCollision === "siblings") {
    const siblingRel = `${outRel}.team-ai-new`;
    result.siblingsWritten.push(siblingRel);
    mkdirSync(dirname(outAbs), { recursive: true });
    writeFileSync(`${outAbs}.team-ai-new`, content, "utf8");
  }
}

export function renderEntityFiles(
  context: Record<string, unknown>,
  renderDir: string,
  priorByPath: Map<string, string>,
  onCollision: EntityCollisionMode,
  result: RenderResult,
): void {
  // Validate every name before writing anything, so one bad entry cannot leave a
  // half-generated tree behind.
  for (const role of asRoles(context.roles)) assertSafeName("role", role.name);
  for (const persona of asStrings(context.personas)) assertSafeName("persona", persona);

  const namespaces = asStrings(context.namespaces);
  const firstNamespace = namespaces[0] ?? "operating";

  const domainYaml = readTemplate("agents/_domain-sme.yaml.hbs");
  const domainMd = readTemplate("agents/_domain-sme.md.hbs");
  for (const domain of asDomains(context.domains)) {
    const ctx = {
      ...context,
      slug: domain.slug,
      name: domain.name,
      namespace: domain.namespace ?? firstNamespace,
      escalate_to: "unassigned",
    };
    const yaml = renderTemplate(domainYaml, ctx, `agents/${domain.slug}-sme.yaml`);
    const md = renderTemplate(domainMd, ctx, `agents/${domain.slug}-sme.md`);
    result.warnings.push(...yaml.warnings, ...md.warnings);
    writeIfSafe(
      `agents/${domain.slug}-sme.yaml`,
      yaml.output,
      renderDir,
      priorByPath,
      onCollision,
      result,
    );
    writeIfSafe(
      `agents/${domain.slug}-sme.md`,
      md.output,
      renderDir,
      priorByPath,
      onCollision,
      result,
    );
  }

  const roleYaml = readTemplate("agents/roles/_role.yaml.hbs");
  const roleMd = readTemplate("agents/roles/_role.md.hbs");
  for (const role of asRoles(context.roles)) {
    const ctx = { ...context, ...role };
    const yaml = renderTemplate(roleYaml, ctx, `agents/roles/${role.name}.yaml`);
    const md = renderTemplate(roleMd, ctx, `agents/roles/${role.name}.md`);
    result.warnings.push(...yaml.warnings, ...md.warnings);
    writeIfSafe(
      `agents/roles/${role.name}.yaml`,
      yaml.output,
      renderDir,
      priorByPath,
      onCollision,
      result,
    );
    writeIfSafe(
      `agents/roles/${role.name}.md`,
      md.output,
      renderDir,
      priorByPath,
      onCollision,
      result,
    );
  }

  for (const persona of asStrings(context.personas)) {
    const templateRel = `personas/${persona}.md.hbs`;
    let content: string;
    if (existsSync(join(TEMPLATES_INSTANCE, templateRel))) {
      const rendered = renderTemplate(readTemplate(templateRel), context, `personas/${persona}.md`);
      result.warnings.push(...rendered.warnings);
      content = rendered.output;
    } else {
      content = generateStub(persona, "persona");
    }
    writeIfSafe(`personas/${persona}.md`, content, renderDir, priorByPath, onCollision, result);
  }
}

export function computeExclude(seed: boolean, standDown: boolean): string[] {
  // `renderTree` matches these against the template-relative path (the `.hbs` is
  // still attached); a trailing `/` matches a subtree, otherwise it is exact.
  const exclude = ["mcp-server/"];
  if (!seed || standDown) exclude.push("kb/");
  if (standDown) exclude.push("index.lock.hbs", ".mcp.json.hbs", "evals/");
  return exclude;
}
