// Deterministic. No model calls. No network.
//
// renderTree walks a template directory and materializes it into a destination
// directory without ever destroying human work. Every output path is classified
// (created / unchanged / updated / collision) and only pristine prior renders
// are overwritten. Nothing is ever removed and nothing is written outside the
// destination. `dryRun` classifies without touching disk.

import { existsSync, readdirSync, readFileSync, type Dirent } from "node:fs";
import { mkdir, writeFile } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";

import Handlebars from "handlebars";

import { withinDest } from "./contain.js";
import { sha256Of, type GeneratedEntry } from "./generated-manifest.js";

export type CollisionMode = "report" | "siblings" | "skip";

export interface RenderResult {
  created: string[];
  unchanged: string[];
  updated: string[];
  collisions: string[];
  siblingsWritten: string[];
  warnings: string[];
  /** Entries for every created + updated path, whether or not writes happened. */
  manifestEntries: GeneratedEntry[];
}

export interface RenderTreeOptions {
  templateDir: string;
  destDir: string;
  context: Record<string, unknown>;
  dryRun?: boolean;
  priorManifest?: GeneratedEntry[];
  onCollision?: CollisionMode;
  /**
   * Template-relative path prefixes (POSIX, e.g. `"kb/"`) to skip entirely.
   * A prefix ending in `/` matches a subtree; otherwise it is an exact
   * template-relative match. Used by `init` to omit the `kb/` seed subtree
   * when the operator declined seeding.
   */
  exclude?: string[];
}

const HBS_EXT = ".hbs";
const SIBLING_SUFFIX = ".team-ai-new";
const KEEP_FILE = ".keep";

/** Block helpers that open a new data scope; keys inside them are unknowable here. */
const SCOPE_OPENERS = new Set(["each", "with"]);
const KNOWN_HELPERS = new Set([
  "kebab",
  "snake",
  "json",
  "yamlList",
  "default",
  "eq",
  "if",
  "unless",
  "each",
  "with",
  "lookup",
  "log",
  "else",
  "this",
]);

function toPosix(path: string): string {
  return path.split(/[\\/]/).join("/");
}

/** Codepoint order: deterministic across locales and ICU builds. */
function byPath(a: string, b: string): number {
  return a < b ? -1 : a > b ? 1 : 0;
}

function makeHandlebars(): typeof Handlebars {
  const hb = Handlebars.create();
  hb.registerHelper("kebab", (value: unknown): string => kebabCase(stringify(value)));
  hb.registerHelper("snake", (value: unknown): string => snakeCase(stringify(value)));
  hb.registerHelper("json", (value: unknown): string => JSON.stringify(value));
  hb.registerHelper("yamlList", (value: unknown): string =>
    Array.isArray(value) ? `[${value.map((v) => stringify(v)).join(", ")}]` : stringify(value),
  );
  hb.registerHelper("default", (value: unknown, fallback: unknown): unknown =>
    value === undefined || value === null || value === "" ? fallback : value,
  );
  hb.registerHelper("eq", (a: unknown, b: unknown): boolean => a === b);
  return hb;
}

function stringify(value: unknown): string {
  if (value === undefined || value === null) return "";
  if (typeof value === "string") return value;
  if (typeof value === "number" || typeof value === "boolean" || typeof value === "bigint") {
    return String(value);
  }
  return JSON.stringify(value);
}

export function kebabCase(text: string): string {
  return text
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

export function snakeCase(text: string): string {
  return text
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "_")
    .replace(/^_+|_+$/g, "");
}

/**
 * Best-effort scan for `{{key}}` / `{{key.path}}` interpolations whose leading
 * segment is not a helper and not present in `context`. Helper calls (anything
 * with a space), relative/data paths, and content inside `{{#each}}` /
 * `{{#with}}` scopes are skipped because their shape is not known here.
 */
function missingContextKeys(template: string, context: Record<string, unknown>): string[] {
  const found = new Set<string>();
  const mustache = /\{\{\{?\s*([#/]?)\s*([^{}]+?)\s*\}?\}\}/g;
  let scopeDepth = 0;
  let match: RegExpExecArray | null;

  while ((match = mustache.exec(template)) !== null) {
    const sigil = match[1] ?? "";
    const expr = (match[2] ?? "").trim();
    if (expr.length === 0 || expr.startsWith("!")) continue;

    const head = expr.split(/\s+/)[0] ?? "";

    if (sigil === "/") {
      if (SCOPE_OPENERS.has(head)) scopeDepth = Math.max(0, scopeDepth - 1);
      continue;
    }
    if (sigil === "#") {
      if (SCOPE_OPENERS.has(head)) scopeDepth += 1;
      continue;
    }
    if (scopeDepth > 0) continue;
    if (/\s/.test(expr)) continue; // helper invocation with arguments
    if (head.startsWith("@") || head.startsWith("~") || head.startsWith("../")) continue;

    const key = (head.split(".")[0] ?? "").replace(/^\[|\]$/g, "");
    if (key.length === 0 || key === "else") continue;
    if (KNOWN_HELPERS.has(key)) continue;
    if (!(key in context)) found.add(key);
  }

  return [...found].sort((a, b) => a.localeCompare(b));
}

export interface RenderedTemplate {
  output: string;
  warnings: string[];
}

/** Render one Handlebars template string against `context`. */
export function renderTemplate(
  source: string,
  context: Record<string, unknown>,
  label = "<template>",
): RenderedTemplate {
  const hb = makeHandlebars();
  const output = hb.compile(source, { noEscape: true })(context);
  const warnings = missingContextKeys(source, context).map(
    (key) => `${label}: missing context key '${key}'`,
  );
  return { output, warnings };
}

function walkFiles(root: string): string[] {
  const out: string[] = [];
  const stack: string[] = [""];
  while (stack.length > 0) {
    const relDir = stack.pop();
    if (relDir === undefined) break;
    let entries: Dirent[];
    try {
      entries = readdirSync(join(root, relDir), { withFileTypes: true });
    } catch {
      continue;
    }
    for (const entry of entries.sort((a, b) => byPath(a.name, b.name))) {
      const rel = relDir.length > 0 ? `${relDir}/${entry.name}` : entry.name;
      if (entry.isDirectory()) stack.push(rel);
      else if (entry.isFile()) out.push(toPosix(rel));
    }
  }
  return out.sort(byPath);
}

function outputRelPath(templateRel: string): string {
  return templateRel.endsWith(HBS_EXT) ? templateRel.slice(0, -HBS_EXT.length) : templateRel;
}

function isTemplatePartial(templateRel: string): boolean {
  return templateRel.split("/").some((segment) => segment.startsWith("_"));
}

export async function renderTree(opts: RenderTreeOptions): Promise<RenderResult> {
  const { templateDir, destDir, context } = opts;
  const dryRun = opts.dryRun ?? false;
  const onCollision: CollisionMode = opts.onCollision ?? "report";
  const exclude = opts.exclude ?? [];
  const isExcluded = (templateRel: string): boolean =>
    exclude.some((prefix) =>
      prefix.endsWith("/") ? templateRel.startsWith(prefix) : templateRel === prefix,
    );
  const destResolved = resolve(destDir);
  const priorByPath = new Map<string, string>();
  for (const entry of opts.priorManifest ?? []) priorByPath.set(entry.path, entry.sha256);

  const result: RenderResult = {
    created: [],
    unchanged: [],
    updated: [],
    collisions: [],
    siblingsWritten: [],
    warnings: [],
    manifestEntries: [],
  };

  const dirsEnsured = new Set<string>();
  const ensureDir = async (abs: string): Promise<void> => {
    if (dryRun || dirsEnsured.has(abs)) return;
    await mkdir(abs, { recursive: true });
    dirsEnsured.add(abs);
  };

  for (const templateRel of walkFiles(templateDir)) {
    if (isExcluded(templateRel)) continue;

    const base = templateRel.split("/").pop() ?? templateRel;

    if (base === KEEP_FILE) {
      // A `.keep` only asserts its directory should exist; the file is not copied.
      const dirRel = templateRel.slice(0, -(KEEP_FILE.length + 1));
      const dirAbs = resolve(destResolved, dirRel);
      if (!withinDest(destResolved, join(dirAbs, "x"))) {
        throw new Error(`renderTree: refusing to create dir outside destDir: ${dirRel}`);
      }
      await ensureDir(dirAbs);
      continue;
    }

    if (isTemplatePartial(templateRel)) continue;

    const outRel = outputRelPath(templateRel);
    const outAbs = resolve(destResolved, outRel);
    if (!withinDest(destResolved, outAbs)) {
      throw new Error(`renderTree: refusing to write outside destDir: ${outRel}`);
    }

    const templateAbs = join(templateDir, templateRel);
    const raw = readFileSync(templateAbs, "utf8");
    let rendered: string;
    if (templateRel.endsWith(HBS_EXT)) {
      const r = renderTemplate(raw, context, outRel);
      rendered = r.output;
      result.warnings.push(...r.warnings);
    } else {
      rendered = raw;
    }

    if (!existsSync(outAbs)) {
      result.created.push(outRel);
      result.manifestEntries.push({ path: outRel, sha256: sha256Of(rendered) });
      if (!dryRun) {
        await ensureDir(dirname(outAbs));
        await writeFile(outAbs, rendered, "utf8");
      }
      continue;
    }

    const current = readFileSync(outAbs, "utf8");
    if (current === rendered) {
      result.unchanged.push(outRel);
      continue;
    }

    const prior = priorByPath.get(outRel);
    if (prior !== undefined && prior === sha256Of(current)) {
      result.updated.push(outRel);
      result.manifestEntries.push({ path: outRel, sha256: sha256Of(rendered) });
      if (!dryRun) await writeFile(outAbs, rendered, "utf8");
      continue;
    }

    result.collisions.push(outRel);
    if (onCollision === "siblings") {
      const siblingRel = `${outRel}${SIBLING_SUFFIX}`;
      result.siblingsWritten.push(siblingRel);
      if (!dryRun) {
        await ensureDir(dirname(outAbs));
        await writeFile(`${outAbs}${SIBLING_SUFFIX}`, rendered, "utf8");
      }
    }
  }

  for (const key of ["created", "unchanged", "updated", "collisions", "siblingsWritten"] as const) {
    result[key].sort(byPath);
  }
  result.manifestEntries.sort((a, b) => byPath(a.path, b.path));
  return result;
}
