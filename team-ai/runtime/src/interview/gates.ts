// Deterministic. No model calls. No network.
//
// renderGate turns interview engine state into the one-page confirmation summary
// for one of the three gates (interview-spec.md §7, §9, §11). Each gate reads
// `engine.effectiveAnswers()` for the resolved answer view, `engine.save().answers`
// for how each answer was reached (`via`), and `engine.warnings()` for surfaced
// tradeoffs, then renders the matching Handlebars template. Nothing is written.

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

import Handlebars from "handlebars";

import { resolveCatalog } from "../catalog/resolve.js";
import type { ResolvedCatalog } from "../catalog/types.js";
import type { AnswerRecord, Engine } from "./engine.js";
import type { PreflightReport } from "./preflight.js";

export const CORE_SKILLS = ["kb-answer", "kb-contribute", "audit-summary", "sme-route"] as const;

const TEMPLATE_BASE = new URL("../../src/interview/gates/", import.meta.url);
const CATALOG_DIR = fileURLToPath(new URL("../../catalog", import.meta.url));

export interface DeferredEntry {
  id: string;
  value: unknown;
  via: "defer" | "recommend";
  checkpoint: string;
}

/** Where a deferred or recommended answer gets revisited (interview-spec.md §7). */
export function revisitCheckpoint(id: string): string {
  if (id === "arch.index_driver" || id === "kb.graph_questions") {
    return "phase-8 checkpoint with eval data";
  }
  if (id === "arch.hosting") {
    return "when a 2nd coding client or 2 non-repo asks appear";
  }
  return "after the first month";
}

/** Every answer reached by defer or recommend, sorted by id for stable output. */
export function collectDeferred(answers: Record<string, AnswerRecord>): DeferredEntry[] {
  const out: DeferredEntry[] = [];
  for (const [id, record] of Object.entries(answers)) {
    if (record.via === "defer" || record.via === "recommend") {
      out.push({ id, value: record.value, via: record.via, checkpoint: revisitCheckpoint(id) });
    }
  }
  return out.sort((a, b) => a.id.localeCompare(b.id));
}

function newHandlebars(): typeof Handlebars {
  const hb = Handlebars.create();
  hb.registerHelper("upper", (value: unknown) => String(value).toUpperCase());
  hb.registerHelper("join", (value: unknown, separator: unknown) =>
    Array.isArray(value)
      ? value.join(typeof separator === "string" ? separator : ", ")
      : String(value),
  );
  return hb;
}

function render(template: string, context: Record<string, unknown>): string {
  const source = readFileSync(fileURLToPath(new URL(template, TEMPLATE_BASE)), "utf8");
  return newHandlebars().compile(source, { noEscape: true })(context);
}

/** Render an answer value for a summary line: arrays joined, blanks shown as a fallback. */
export function formatAnswer(value: unknown, fallback = "decide later"): string {
  if (Array.isArray(value)) return value.length > 0 ? value.join(", ") : fallback;
  if (value === null || value === undefined || value === "") return fallback;
  if (typeof value === "object") return JSON.stringify(value);
  if (typeof value === "string") return value;
  if (typeof value === "number" || typeof value === "boolean") return String(value);
  return fallback;
}

const str = formatAnswer;

function asArray(value: unknown): string[] {
  return Array.isArray(value) ? value.filter((v): v is string => typeof v === "string") : [];
}

export function slug(text: string): string {
  return text
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

export function parseDomains(value: unknown): string[] {
  if (typeof value !== "string") return [];
  return value
    .split(/[,\n]/)
    .map((part) => part.trim())
    .filter((part) => part.length > 0);
}

function deferredBlock(entries: DeferredEntry[]): string {
  if (entries.length === 0) return "  (nothing deferred)";
  return entries
    .map((e) => `  ${e.id} → ${str(e.value, "(default)")} (${e.via}), revisit: ${e.checkpoint}`)
    .join("\n");
}

function warningsBlock(ids: string[]): string {
  if (ids.length === 0) return "";
  return `\nWARNINGS\n${ids.map((id) => `  ${id} — tradeoff acknowledged`).join("\n")}\n`;
}

function preflightLine(report: PreflightReport | undefined): string {
  if (!report) return "not scanned";
  const config = report.found.agentConfig;
  const suffix = config.length > 0 ? ` (${config.join(", ")})` : "";
  return `${report.assessment.toUpperCase()}${suffix}`;
}

function renderGate1(engine: Engine, preflight: PreflightReport | undefined): string {
  const eff = engine.effectiveAnswers();
  return render("strategy.hbs", {
    preflight: preflightLine(preflight),
    teamName: str(eff["team.name"], "unnamed"),
    teamSize: str(eff["team.size"]),
    mission: str(eff["team.mission"], "(not given)"),
    surfaces: str(eff["team.surfaces"], "(none selected)"),
    substrate: `${str(eff["kb.substrate"])} substrate`,
    driver: str(eff["arch.index_driver"]),
    namespaces: str(eff["kb.namespaces"]),
    catalog: str(eff["kb.catalog_override"]),
    sourcesStrategy: str(eff["kb.sources_strategy"]),
    sensitivity: str(eff["kb.sensitivity"]),
    writeBack: str(eff["kb.write_back"]),
    warningsBlock: warningsBlock(engine.warnings()),
    deferredBlock: deferredBlock(collectDeferred(engine.save().answers)),
  });
}

function renderGate2(engine: Engine): string {
  const eff = engine.effectiveAnswers();
  const rawDriver = str(eff["arch.index_driver"], "lexical");
  const driver = rawDriver === "decide-later" ? "lexical (deferred)" : rawDriver;
  const hosting = str(eff["arch.hosting"], "no-server");
  const fileTreeNote =
    hosting === "no-server"
      ? "kb/ docs/ agents/ scripts/ evals/ — scripts and a repo, no server dir"
      : `kb/ docs/ agents/ scripts/ evals/ server/ — ${hosting}`;
  return render("architecture.hbs", { driver, hosting, fileTreeNote });
}

export function loadCatalog(instanceDir?: string): ResolvedCatalog | null {
  try {
    return resolveCatalog(
      instanceDir === undefined
        ? { toolkitDir: CATALOG_DIR }
        : { toolkitDir: CATALOG_DIR, instanceDir },
    );
  } catch {
    return null;
  }
}

export function evalNamespaceCount(
  catalog: ResolvedCatalog | null,
  nsAnswer: unknown,
  domains: number,
): number {
  if (catalog && typeof nsAnswer === "string") {
    const preset = catalog.namespaces.get(nsAnswer);
    if (preset) return preset.value.second_level.length;
  }
  return domains > 0 ? domains : 3;
}

// The namespace every domain subagent is scoped to. Matches the generator:
// `src/generator/entity-files.ts` writes `kb_namespaces: [<preset first level>]`
// for each domain SME, so the plan renders must report that same namespace, not
// the free-text domain label.
export function domainNamespace(catalog: ResolvedCatalog | null, nsAnswer: unknown): string {
  if (catalog && typeof nsAnswer === "string") {
    const preset = catalog.namespaces.get(nsAnswer);
    const first = preset?.value.second_level[0];
    if (typeof first === "string" && first.length > 0) return first;
  }
  return "operating";
}

function renderGate3(engine: Engine): string {
  const eff = engine.effectiveAnswers();
  const catalog = loadCatalog();

  const domains = parseDomains(eff["agents.domains"]);
  const ns = domainNamespace(catalog, eff["kb.namespaces"]);
  const domainBlock =
    domains.length > 0
      ? domains.map((d) => `  ${slug(d)}-sme   ns: ${ns}   small   hops 0`).join("\n")
      : "  (none named yet — add before the first reindex)";

  const roles = asArray(eff["agents.roles"]);
  const rolesSuppressed = roles.length === 0 || eff["team.size"] === "1-3";
  const roleBlock = rolesSuppressed
    ? "  none (team of 3 or fewer — domain agents only)"
    : roles
        .map((role) => {
          const tier = catalog?.roles.get(role)?.value.model_tier ?? "small";
          return `  ${role}   ns: all   ${tier}   hops 0`;
        })
        .join("\n");

  const extras = asArray(eff["agents.skills"]).filter(
    (s) => !CORE_SKILLS.includes(s as (typeof CORE_SKILLS)[number]),
  );
  const skills =
    `core: ${CORE_SKILLS.join(", ")}` + (extras.length > 0 ? `\n  team: ${extras.join(", ")}` : "");

  const personas = asArray(eff["agents.personas"]);

  return render("agent-plan.hbs", {
    domainBlock,
    roleBlock,
    personas: personas.length > 0 ? personas.join(", ") : "internal-technical",
    skills,
    evalNamespaces: evalNamespaceCount(catalog, eff["kb.namespaces"], domains.length),
  });
}

export function renderGate(n: 1 | 2 | 3, engine: Engine, preflight?: PreflightReport): string {
  if (n === 1) return renderGate1(engine, preflight);
  if (n === 2) return renderGate2(engine);
  return renderGate3(engine);
}
