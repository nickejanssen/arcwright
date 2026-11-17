// Deterministic. No model calls. No network.
//
// writeOutputs turns a completed interview into the seven files listed in
// interview-spec.md §13: team-profile.yaml, the four docs, the first ADR, and
// index.lock. It refuses to write anything until all three gates are confirmed
// (`phase === "done"`). Re-running rewrites exactly this set and nothing else.

import { readFileSync } from "node:fs";
import { mkdir, writeFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import Handlebars from "handlebars";
import { stringify as stringifyYaml } from "yaml";

import { DEFAULT_INDEX_LOCK, writeIndexLock } from "../retrieval/index-lock.js";
import { validate } from "../schema/validate.js";
import { packageVersion } from "../version.js";
import { loadBank } from "./bank.js";
import type { AnswerRecord, Engine } from "./engine.js";
import {
  CORE_SKILLS,
  collectDeferred,
  domainNamespace,
  evalNamespaceCount,
  formatAnswer,
  loadCatalog,
  parseDomains,
  slug,
} from "./gates.js";
import type { PreflightReport } from "./preflight.js";
import { renderPreflight } from "./preflight-report.js";
import type { Question } from "./types.js";

const TEMPLATE_BASE = new URL("../../src/interview/doc-templates/", import.meta.url);

export interface WriteOutputsOptions {
  preflight?: PreflightReport;
}

function render(template: string, context: Record<string, unknown>): string {
  const source = readFileSync(fileURLToPath(new URL(template, TEMPLATE_BASE)), "utf8");
  return Handlebars.create().compile(source, { noEscape: true })(context);
}

function strings(value: unknown): string[] {
  return Array.isArray(value) ? value.filter((v): v is string => typeof v === "string") : [];
}

function driverForLock(value: unknown): string {
  if (typeof value !== "string" || value.length === 0) return "lexical";
  return value === "decide-later" ? "lexical" : value;
}

function bullets(lines: string[], empty: string): string {
  return lines.length > 0 ? lines.map((l) => `- ${l}`).join("\n") : empty;
}

function nonDefaultDecisions(
  bank: readonly Question[],
  answers: Record<string, AnswerRecord>,
): string[] {
  const out: string[] = [];
  for (const q of bank) {
    if (q.type !== "single_select" && q.type !== "multi_select") continue;
    const record = answers[q.id];
    if (!record || record.via !== "direct") continue;
    if (JSON.stringify(record.value) === JSON.stringify(q.default)) continue;
    const chosen = formatAnswer(record.value, "(blank)");
    let tradeoff = "";
    if (q.type === "single_select") {
      const option = q.options.find((o) => o.value === record.value);
      if (option?.tradeoff) tradeoff = ` — ${option.tradeoff.replace(/\s+/g, " ").trim()}`;
    }
    out.push(`**${q.id}**: ${chosen}${tradeoff}`);
  }
  return out;
}

function strategyContext(
  engine: Engine,
  created: string,
  preflight: PreflightReport | undefined,
): Record<string, unknown> {
  const eff = engine.effectiveAnswers();
  const deferred = collectDeferred(engine.save().answers);
  return {
    created,
    teamName: formatAnswer(eff["team.name"], "unnamed"),
    teamSize: formatAnswer(eff["team.size"]),
    mission: formatAnswer(eff["team.mission"], "(not given)"),
    surfaces: formatAnswer(eff["team.surfaces"], "(none selected)"),
    substrate: formatAnswer(eff["kb.substrate"]),
    namespaces: formatAnswer(eff["kb.namespaces"]),
    catalog: formatAnswer(eff["kb.catalog_override"]),
    sourcesStrategy: formatAnswer(eff["kb.sources_strategy"]),
    sensitivity: formatAnswer(eff["kb.sensitivity"]),
    writeBack: formatAnswer(eff["kb.write_back"]),
    driver: formatAnswer(eff["arch.index_driver"]),
    preflight: preflight
      ? `Assessment: ${preflight.assessment.toUpperCase()}. ${preflight.rationale}`
      : "Preflight was not captured for this run.",
    deferredList: bullets(
      deferred.map(
        (d) =>
          `${d.id} → ${formatAnswer(d.value, "(default)")} (${d.via}), revisit ${d.checkpoint}`,
      ),
      "Nothing was deferred.",
    ),
  };
}

function architectureContext(engine: Engine, created: string): Record<string, unknown> {
  const eff = engine.effectiveAnswers();
  const hosting = formatAnswer(eff["arch.hosting"], "no-server");
  const rawDriver = formatAnswer(eff["arch.index_driver"], "lexical");
  const deferred = collectDeferred(engine.save().answers);
  const table =
    deferred.length > 0
      ? [
          "| Decision | Applied default | Revisit |",
          "|---|---|---|",
          ...deferred.map(
            (d) => `| ${d.id} | ${formatAnswer(d.value, "(default)")} | ${d.checkpoint} |`,
          ),
        ].join("\n")
      : "No decisions were deferred.";
  return {
    created,
    driver: rawDriver === "decide-later" ? "lexical (deferred)" : rawDriver,
    hosting,
    topology: formatAnswer(eff["arch.topology"]),
    language: formatAnswer(eff["arch.language"]),
    ci: formatAnswer(eff["arch.ci"]),
    modelTiers: formatAnswer(eff["arch.model_tiers"]),
    cache: formatAnswer(eff["arch.cache"]),
    fileTreeNote:
      hosting === "no-server"
        ? "`kb/`, `docs/`, `agents/`, `scripts/`, `evals/` — scripts and a repo, no server directory."
        : `\`kb/\`, \`docs/\`, \`agents/\`, \`scripts/\`, \`evals/\`, \`server/\` — ${hosting}.`,
    deferredTable: table,
  };
}

function agentPlanContext(engine: Engine, created: string): Record<string, unknown> {
  const eff = engine.effectiveAnswers();
  const catalog = loadCatalog();

  const domains = parseDomains(eff["agents.domains"]);
  const domainNs = domainNamespace(catalog, eff["kb.namespaces"]);
  const domainList = bullets(
    domains.map((d) => `\`${slug(d)}-sme\` — ns: ${domainNs}, tier small, hops 0`),
    "No domains were named yet. Add them before the first reindex.",
  );

  const roles = strings(eff["agents.roles"]);
  const rolesSuppressed = roles.length === 0 || eff["team.size"] === "1-3";
  const roleList = rolesSuppressed
    ? "None. Team of 3 or fewer, so domain agents alone are the honest choice."
    : bullets(
        roles.map((role) => {
          const tier = catalog?.roles.get(role)?.value.model_tier ?? "small";
          return `\`${role}\` — ns: all, tier ${tier}, hops 0`;
        }),
        "None.",
      );

  const personas = strings(eff["agents.personas"]);
  const personaList = bullets(
    (personas.length > 0 ? personas : ["internal-technical"]).map((p) => p),
    "- internal-technical",
  );

  const extras = strings(eff["agents.skills"]).filter(
    (s) => !CORE_SKILLS.includes(s as (typeof CORE_SKILLS)[number]),
  );
  const skillList =
    `- core: ${CORE_SKILLS.join(", ")}` +
    (extras.length > 0 ? `\n- team: ${extras.join(", ")}` : "");

  return {
    created,
    domainList,
    roleList,
    personaList,
    skillList,
    evalNamespaces: evalNamespaceCount(catalog, eff["kb.namespaces"], domains.length),
  };
}

export async function writeOutputs(
  engine: Engine,
  destDir: string,
  opts?: WriteOutputsOptions,
): Promise<{ written: string[] }> {
  const state = engine.save();
  if (state.phase !== "done") {
    throw new Error(
      `writeOutputs: interview not complete (phase '${state.phase}') — confirm all 3 gates first`,
    );
  }

  const created = new Date().toISOString();
  const createdDate = created.slice(0, 10);
  const eff = engine.effectiveAnswers();
  const bank = loadBank();

  const profile = {
    team_ai_version: packageVersion(),
    created,
    answers: eff,
    deferred: collectDeferred(state.answers).map((d) => ({
      question: d.id,
      applied_default: d.value,
      revisit: d.checkpoint,
    })),
    generated_paths: [] as { path: string; sha256: string }[],
  };
  const check = validate("team-profile", profile);
  if (!check.ok) {
    throw new Error(
      `writeOutputs: team-profile.yaml failed validation: ${check.errors.join("; ")}`,
    );
  }

  const preflightDoc = opts?.preflight
    ? renderPreflight(opts.preflight)
    : "# Preflight\n\n(preflight not captured for this run)\n";

  const files: Record<string, string> = {
    "team-profile.yaml": stringifyYaml(profile),
    "docs/preflight.md": preflightDoc,
    "docs/strategy.md": render(
      "strategy.md.hbs",
      strategyContext(engine, created, opts?.preflight),
    ),
    "docs/architecture.md": render("architecture.md.hbs", architectureContext(engine, created)),
    "docs/agent-plan.md": render("agent-plan.md.hbs", agentPlanContext(engine, created)),
    "docs/decisions/adr-0001-scaffold-choices.md": render("adr-0001.md.hbs", {
      createdDate,
      decisionList: bullets(
        nonDefaultDecisions(bank, state.answers),
        "No choices departed from the defaults.",
      ),
    }),
  };

  await mkdir(destDir, { recursive: true });
  for (const [rel, body] of Object.entries(files)) {
    const abs = join(destDir, rel);
    await mkdir(dirname(abs), { recursive: true });
    await writeFile(abs, body.endsWith("\n") ? body : `${body}\n`, "utf8");
  }

  writeIndexLock(destDir, {
    ...DEFAULT_INDEX_LOCK,
    driver: driverForLock(eff["arch.index_driver"]),
  });

  const written = [...Object.keys(files), "index.lock"].sort((a, b) => a.localeCompare(b));
  return { written };
}
