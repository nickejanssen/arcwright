// Deterministic. No model calls. No network.
//
// buildAdoptionPlan measures an existing repo against the framework standard and
// writes a two-file plan: docs/adoption-plan.md (human-readable) and
// adoption-plan.yaml (schema-valid, machine-applied by `team-ai adopt --apply`).
// It writes nothing else and never edits the repo it is measuring.

import {
  mkdirSync,
  readdirSync,
  readFileSync,
  statSync,
  writeFileSync,
  type Dirent,
} from "node:fs";
import { join, relative } from "node:path";
import { fileURLToPath } from "node:url";

import Handlebars from "handlebars";
import { stringify as stringifyYaml } from "yaml";

import { CORE_SKILLS } from "../interview/gates.js";
import { scanPreflight } from "../interview/preflight.js";
import { parseFrontmatter } from "../kb/frontmatter.js";
import { slug } from "../kb/slugify.js";
import { validate } from "../schema/validate.js";
import { packageVersion } from "../version.js";
import { TEMPLATES_INSTANCE } from "../generator/entity-files.js";
import { renderTree } from "../generator/render.js";
import { detectSyncedSource, inferFrontmatter } from "./infer.js";
import { hasFrontmatter } from "./backfill.js";
import { getGitAuthorsMap, getLastModifiedMap } from "./git-owner.js";
import { proposeNamespaceMap } from "./namespaces.js";
import { PENDING_NAMESPACE } from "./types.js";
import type {
  AdoptionPlan,
  BackfillItem,
  NamespaceDecision,
  NamespaceMatch,
  RelabelItem,
} from "./types.js";
import { gapVsQualityBar } from "./gap.js";

const DEFAULT_PRESET_SHAPE = ["operating", "platform", "patterns", "playbooks", "decisions"];
const DOC_TEMPLATE = new URL("../../src/adopt/plan-doc.hbs", import.meta.url);

// Path segments `team-ai adopt` never measures: version control, dependencies,
// build output, and — unless `--include-archived` — archived or export-dump
// docs, which are not held to the current standard.
const NEVER_SCAN_SEGMENTS = new Set([".git", "node_modules", "dist"]);
const ARCHIVED_SEGMENTS = new Set(["archive", "archived", "_archive", "notion-export"]);

function hasSegment(relPosix: string, set: Set<string>): boolean {
  return relPosix.split("/").some((segment) => set.has(segment.toLowerCase()));
}

export interface BuildAdoptionPlanOptions {
  root: string;
  out: string;
  horizonDays: number;
  namespaceMap?: Record<string, string>;
  today?: Date;
  includeArchived?: boolean;
}

function isDir(target: string): boolean {
  try {
    return statSync(target).isDirectory();
  } catch {
    return false;
  }
}

function toPosix(path: string): string {
  return path.split(/[\\/]/).join("/");
}

function skipDir(relPosix: string, includeArchived: boolean): boolean {
  if (hasSegment(relPosix, NEVER_SCAN_SEGMENTS)) return true;
  return !includeArchived && hasSegment(relPosix, ARCHIVED_SEGMENTS);
}

function topLevelFolders(docsRoot: string, includeArchived: boolean): string[] {
  let entries: Dirent[];
  try {
    entries = readdirSync(docsRoot, { withFileTypes: true });
  } catch {
    return [];
  }
  return entries
    .filter((entry) => entry.isDirectory())
    .map((entry) => entry.name)
    .filter((name) => !skipDir(name, includeArchived))
    .sort((a, b) => (a < b ? -1 : a > b ? 1 : 0));
}

function markdownUnder(
  docsRoot: string,
  includeArchived: boolean,
): { files: string[]; archivedSkipped: number } {
  const out: string[] = [];
  let archivedSkipped = 0;
  const stack: string[] = [""];
  while (stack.length > 0) {
    const relDir = stack.pop();
    if (relDir === undefined) break;
    let entries: Dirent[];
    try {
      entries = readdirSync(join(docsRoot, relDir), { withFileTypes: true });
    } catch {
      continue;
    }
    for (const entry of entries.sort((a, b) => (a.name < b.name ? -1 : 1))) {
      const rel = relDir.length > 0 ? `${relDir}/${entry.name}` : entry.name;
      if (entry.isDirectory()) {
        if (hasSegment(rel, NEVER_SCAN_SEGMENTS)) continue;
        stack.push(rel);
      } else if (entry.isFile() && entry.name.endsWith(".md")) {
        if (!includeArchived && hasSegment(rel, ARCHIVED_SEGMENTS)) {
          archivedSkipped += 1;
          continue;
        }
        out.push(toPosix(rel));
      }
    }
  }
  return { files: out.sort((a, b) => (a < b ? -1 : a > b ? 1 : 0)), archivedSkipped };
}

function stubContext(root: string): Record<string, unknown> {
  const name = root.split(/[\\/]/).filter(Boolean).pop() ?? "team";
  return {
    team: { name, slug: slug(name).replace(/-/g, ""), mission: "", size: "4-8" },
    org_path: "your-org",
    namespaces: DEFAULT_PRESET_SHAPE,
    driver: "lexical",
    hosting: "no-server",
    server: false,
    roles: [],
    domains: [],
    personas: ["internal-technical"],
    skills: [...CORE_SKILLS],
    seed: false,
    reviewByDate: "2099-01-01",
    strictness: "refuse-log-gap",
    writeBack: "pr-only",
    sensitivity: "three-tiers",
    preset: "generic",
  };
}

async function detectCollisions(root: string): Promise<string[]> {
  const dry = await renderTree({
    templateDir: TEMPLATES_INSTANCE,
    destDir: root,
    context: stubContext(root),
    dryRun: true,
  });
  return [...dry.collisions].sort((a, b) => (a < b ? -1 : a > b ? 1 : 0));
}

// A backfill item is "already stale" when its inferred `review_by` (anchored
// on last git commit, see infer.ts) already fell before the day the plan was
// generated — i.e. the content is overdue for review NOW, on adoption,
// before anyone has looked at it under team-ai. Computed from `plan.created`
// rather than a separate `today` param so this stays a pure function of the
// plan, same as the other renderDoc-only summary stats below.
export function countAlreadyStale(plan: Pick<AdoptionPlan, "created" | "backfill">): number {
  const todayStr = plan.created.slice(0, 10);
  return plan.backfill.filter((item) => item.frontmatter.review_by < todayStr).length;
}

function renderDoc(plan: AdoptionPlan, assessment: string): string {
  const source = readFileSync(fileURLToPath(DOC_TEMPLATE), "utf8");
  const satisfied = plan.gap.filter((g) => g.satisfied).length;
  const todayStr = plan.created.slice(0, 10);
  return Handlebars.create().compile(source, { noEscape: true })({
    ...plan,
    backfill: plan.backfill.map((item) => ({
      ...item,
      namespaceLabel:
        item.namespace === PENDING_NAMESPACE ? "**(pending decision)**" : `\`${item.namespace}\``,
      staleLabel: item.frontmatter.review_by < todayStr ? " — ⚠ already due for review" : "",
    })),
    assessment,
    gapSatisfied: satisfied,
    gapTotal: plan.gap.length,
    backfillCount: plan.backfill.length,
    decisionCount: plan.namespace_map.decisions.length,
    collisionCount: plan.collisions.length,
    alreadyStale: countAlreadyStale(plan),
  });
}

export function writeAdoptionPlan(plan: AdoptionPlan, out: string, assessment = "unknown"): void {
  const check = validate("adoption-plan", plan);
  if (!check.ok) {
    throw new Error(`adoption plan is not schema-valid: ${check.errors.join("; ")}`);
  }
  mkdirSync(join(out, "docs"), { recursive: true });
  writeFileSync(join(out, "adoption-plan.yaml"), stringifyYaml(plan), "utf8");
  writeFileSync(join(out, "docs", "adoption-plan.md"), renderDoc(plan, assessment), "utf8");
}

export async function buildAdoptionPlan(opts: BuildAdoptionPlanOptions): Promise<AdoptionPlan> {
  const { root, out, horizonDays } = opts;
  const today = opts.today ?? new Date();
  const includeArchived = opts.includeArchived === true;

  const report = await scanPreflight(root);

  const docsRoot = isDir(join(root, "docs"))
    ? join(root, "docs")
    : isDir(join(root, "kb"))
      ? join(root, "kb")
      : null;
  if (docsRoot === null) {
    throw new Error(`team-ai adopt: no docs/ or kb/ directory under ${root}`);
  }

  const folders = topLevelFolders(docsRoot, includeArchived);
  const proposal = proposeNamespaceMap(folders, DEFAULT_PRESET_SHAPE);

  const matchedByFolder = new Map<string, string>();
  for (const entry of proposal.matched) matchedByFolder.set(entry.folder, entry.namespace);
  const decisionFolders = new Set(proposal.unmatched.map((u) => u.folder));

  for (const [folder, namespace] of Object.entries(opts.namespaceMap ?? {})) {
    matchedByFolder.set(folder, namespace);
    decisionFolders.delete(folder);
  }

  const matched: NamespaceMatch[] = [...matchedByFolder.entries()]
    .map(([folder, namespace]) => ({ folder, namespace }))
    .sort((a, b) => (a.folder < b.folder ? -1 : a.folder > b.folder ? 1 : 0));
  const decisions: NamespaceDecision[] = proposal.unmatched
    .filter((u) => decisionFolders.has(u.folder))
    .map((u) => ({ folder: u.folder, candidates: u.candidates, chosen: null }));

  // A folder with no preset match and no override carries PENDING_NAMESPACE
  // until `--interactive` records a `chosen` value; root-level docs (no folder)
  // stay `unmapped`.
  const namespaceForFolder = (folder: string): string => {
    const mapped = matchedByFolder.get(folder);
    if (mapped !== undefined) return mapped;
    if (folder.length > 0 && decisionFolders.has(folder)) return PENDING_NAMESPACE;
    return "unmapped";
  };

  const backfill: BackfillItem[] = [];
  const relabels: RelabelItem[] = [];

  // One git traversal for the whole docs tree, not one subprocess per file.
  const docsScope = toPosix(relative(root, docsRoot));
  const authorsByPath = getGitAuthorsMap(root, docsScope);
  // A second single traversal for last-modified dates, so `review_by` anchors
  // on when a doc was actually last touched rather than on "today" — see the
  // comment on `InferFrontmatterOptions.lastModified`.
  const lastModifiedByPath = getLastModifiedMap(root, docsScope);

  const { files: markdownFiles, archivedSkipped } = markdownUnder(docsRoot, includeArchived);
  for (const relFromDocs of markdownFiles) {
    const abs = join(docsRoot, relFromDocs);
    const relFromRoot = toPosix(relative(root, abs));
    const folder = relFromDocs.includes("/") ? (relFromDocs.split("/")[0] ?? "") : "";
    const namespace = namespaceForFolder(folder);
    const raw = readFileSync(abs, "utf8");

    if (!hasFrontmatter(raw)) {
      const fm = inferFrontmatter({
        relPath: relFromDocs,
        body: raw,
        namespace,
        gitAuthors: authorsByPath.get(relFromRoot) ?? [],
        horizonDays,
        today,
        lastModified: lastModifiedByPath.get(relFromRoot) ?? null,
      });
      backfill.push({
        path: relFromRoot,
        namespace,
        frontmatter: fm,
        approved: false,
        conflict: null,
      });
      continue;
    }

    // A real, hand-authored repo will contain front matter that some other
    // tool's YAML parser tolerated but this one doesn't (a folded scalar with
    // no fold indicator was found in the wild during dogfooding). Detecting
    // that a file HAS front matter (above) is not the same as it being valid
    // YAML — an unguarded parse here would crash the whole scan over one bad
    // file instead of flagging just that file, which is worse than any of
    // the outcomes a flag can lead to.
    let data: Record<string, unknown>;
    let body: string;
    try {
      ({ data, body } = parseFrontmatter(raw));
    } catch (err) {
      const reason =
        err instanceof Error ? (err.message.split("\n")[0] ?? err.message) : String(err);
      const fm = inferFrontmatter({
        relPath: relFromDocs,
        body: raw,
        namespace,
        gitAuthors: authorsByPath.get(relFromRoot) ?? [],
        horizonDays,
        today,
        lastModified: lastModifiedByPath.get(relFromRoot) ?? null,
      });
      backfill.push({
        path: relFromRoot,
        namespace,
        frontmatter: fm,
        approved: false,
        conflict: `existing front matter does not parse as YAML: ${reason}`,
      });
      continue;
    }

    const result = validate("frontmatter", data);
    if (!result.ok) {
      const fm = inferFrontmatter({
        relPath: relFromDocs,
        body,
        namespace,
        gitAuthors: authorsByPath.get(relFromRoot) ?? [],
        horizonDays,
        today,
        lastModified: lastModifiedByPath.get(relFromRoot) ?? null,
      });
      backfill.push({
        path: relFromRoot,
        namespace,
        frontmatter: fm,
        approved: false,
        conflict: result.errors[0] ?? "invalid front matter",
      });
    }

    const currentSource = typeof data.source === "string" ? data.source : null;
    const detected = detectSyncedSource(body);
    if ((currentSource === null || currentSource.length === 0) && detected !== null) {
      relabels.push({
        path: relFromRoot,
        current_source: currentSource,
        proposed_source: detected,
        approved: false,
      });
    }
  }

  const plan: AdoptionPlan = {
    generated_by: `team-ai adopt ${packageVersion()}`,
    root,
    created: today.toISOString(),
    namespace_map: { matched, decisions },
    backfill,
    relabels,
    gap: gapVsQualityBar(root),
    collisions: await detectCollisions(root),
    archived_skipped: archivedSkipped,
  };

  writeAdoptionPlan(plan, out, report.assessment);
  return plan;
}
