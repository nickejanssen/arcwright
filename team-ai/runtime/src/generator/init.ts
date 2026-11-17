// Deterministic orchestration. No model calls. No network.
//
// `team-ai init` is the generator's keystone: it runs the preflight scan, walks
// the interview, builds the render context, then lays the instance down over the
// target directory WITHOUT ever overwriting human work. A dry render classifies
// every output path first; `planReconcile` decides whether the operator has to
// choose a coexistence strategy; only pristine prior renders are ever replaced.
//
// Ordering matters: templates render first, then per-entity agent files, then
// `writeOutputs` writes the profile + gate docs, then the generated-file
// manifest is merged, then reindex / assemble-manifest / doctor run as reports.

import { appendFileSync, existsSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

import { select } from "@inquirer/prompts";

import * as assembleManifest from "../commands/assemble-manifest.js";
import * as doctor from "../commands/doctor.js";
import * as reindex from "../commands/reindex.js";
import { loadBank } from "../interview/bank.js";
import { runInterviewCli } from "../interview/cli-runtime.js";
import { Engine } from "../interview/engine.js";
import { scanPreflight } from "../interview/preflight.js";
import { renderPreflight } from "../interview/preflight-report.js";
import { writeOutputs } from "../interview/outputs.js";
import { buildContext } from "./context.js";
import { computeExclude, renderEntityFiles, TEMPLATES_INSTANCE } from "./entity-files.js";
import {
  mergeGeneratedManifest,
  readGeneratedManifest,
  type GeneratedEntry,
} from "./generated-manifest.js";
import * as resume from "./resume.js";
import {
  parseStrategy,
  planReconcile,
  RECONCILE_STRATEGIES,
  type ReconcilePlan,
} from "./reconcile.js";
import { renderTree, type RenderResult } from "./render.js";
import type { AnswerSource } from "./init-answers.js";

type Strategy = ReconcilePlan["strategy"];

export interface InitOptions {
  dir?: string;
  catalog?: string;
  dryRun?: boolean;
  resume?: boolean;
  onConflict?: Strategy;
  answers?: AnswerSource;
  preflightTarget?: string;
  output?: (s: string) => void;
}

const TEMPLATES_MCP = fileURLToPath(new URL("../../templates/mcp-server", import.meta.url));

const STAND_DOWN_NOTE = [
  "",
  "Preflight assessment is STAND-DOWN: an org enterprise-search deployment already",
  'answers "where is the doc". team-ai will generate only the deterministic layer —',
  "agents, personas, skills, docs, and the manifest — and will skip the kb/ seed,",
  "the retrieval index, the MCP config, and the eval suite.",
  "",
].join("\n");

function str(value: unknown, fallback = ""): string {
  return typeof value === "string" && value.length > 0 ? value : fallback;
}

function summary(result: RenderResult, output: (s: string) => void): void {
  output("");
  output(
    `${result.created.length} file(s) created, ${result.unchanged.length} unchanged, ` +
      `${result.updated.length} updated, ${result.collisions.length} collision(s).`,
  );
  if (result.siblingsWritten.length > 0) {
    output(
      `Wrote ${result.siblingsWritten.length} sibling file(s) — review each *.team-ai-new ` +
        "against the file it sits beside, then delete or merge it.",
    );
  }
  for (const collision of result.collisions) {
    if (!result.siblingsWritten.some((s) => s === `${collision}.team-ai-new`)) {
      output(`  kept your version, skipped: ${collision}`);
    }
  }
}

async function chooseStrategy(
  promptText: string,
  answers: AnswerSource | undefined,
  output: (s: string) => void,
): Promise<Strategy> {
  output(promptText);
  if (answers) {
    return parseStrategy(await answers("reconcile.strategy")) ?? "adopt-existing";
  }
  const picked = await select<Strategy>({
    message: "How should team-ai lay itself down here?",
    choices: RECONCILE_STRATEGIES.map((value) => ({ value, name: value })),
  });
  return picked;
}

export async function run(opts: InitOptions): Promise<number> {
  const output = opts.output ?? ((s: string): void => console.log(s));
  const dir = opts.dir ?? ".";

  if (opts.resume === true) {
    if (existsSync(join(dir, "team-profile.yaml"))) {
      const resumeOpts: Parameters<typeof resume.run>[0] = { dir };
      if (opts.catalog !== undefined) resumeOpts.catalog = opts.catalog;
      if (opts.answers !== undefined) resumeOpts.answers = opts.answers;
      if (opts.output !== undefined) resumeOpts.output = opts.output;
      return resume.run(resumeOpts);
    }
    output("no team-profile.yaml to resume; run 'team-ai init'");
    return 1;
  }

  const report = await scanPreflight(opts.preflightTarget ?? dir);
  output(renderPreflight(report));

  const standDown = report.assessment === "stand-down";
  if (standDown) output(STAND_DOWN_NOTE);

  const interviewOpts: Parameters<typeof runInterviewCli>[0] = { cwd: dir };
  if (opts.answers !== undefined) interviewOpts.answers = opts.answers;
  if (opts.output !== undefined) interviewOpts.output = opts.output;
  const state = await runInterviewCli(interviewOpts);
  if (state.phase !== "done") {
    output("Interview not complete. Resume where you left off with:  team-ai init --resume");
    return 0;
  }

  const engine = Engine.load(loadBank(), state);
  const context = buildContext(
    engine,
    opts.catalog !== undefined ? { instanceCatalogDir: opts.catalog } : {},
  );
  const seed = context.seed === true;
  const hosting = str(context.hosting, "no-server");
  const exclude = computeExclude(seed, standDown);

  const dry = await renderTree({
    templateDir: TEMPLATES_INSTANCE,
    destDir: dir,
    context,
    priorManifest: readGeneratedManifest(dir),
    dryRun: true,
    exclude,
  });

  const rc = planReconcile(dry, report, opts.onConflict);
  const strategy: Strategy =
    rc.needsPrompt && opts.onConflict === undefined
      ? await chooseStrategy(rc.promptText, opts.answers, output)
      : (rc.plan?.strategy ?? opts.onConflict ?? "adopt-existing");

  if (opts.dryRun === true) {
    output("");
    output(
      `Dry run: ${dry.created.length} would be created, ${dry.unchanged.length} unchanged, ` +
        `${dry.updated.length} updated, ${dry.collisions.length} collision(s).`,
    );
    output(`Strategy: ${strategy}. Nothing was written.`);
    return 0;
  }

  if (strategy === "abort") {
    await writeOutputs(engine, dir, { preflight: report });
    output("");
    output("Wrote the interview profile and gate docs only. No templates were generated.");
    return 0;
  }

  const renderDir = strategy === "subdir" ? join(dir, "team-ai") : dir;
  const onCollision: "siblings" | "skip" = strategy === "siblings" ? "siblings" : "skip";
  const priorManifest = readGeneratedManifest(renderDir);
  const priorByPath = new Map<string, string>(priorManifest.map((e) => [e.path, e.sha256]));

  const result = await renderTree({
    templateDir: TEMPLATES_INSTANCE,
    destDir: renderDir,
    context,
    priorManifest,
    onCollision,
    exclude,
  });

  renderEntityFiles(context, renderDir, priorByPath, onCollision, result);

  await writeOutputs(engine, renderDir, { preflight: report });

  const entityEntries: GeneratedEntry[] = result.manifestEntries;
  mergeGeneratedManifest(renderDir, entityEntries);

  if (
    strategy === "adopt-existing" &&
    (report.existingAssets.agentConfigFile !== undefined ||
      report.existingAssets.routerAgent !== undefined)
  ) {
    const adopted = [report.existingAssets.agentConfigFile, report.existingAssets.routerAgent]
      .filter((v): v is string => v !== undefined)
      .join(", ");
    const routerClause =
      report.existingAssets.routerAgent !== undefined
        ? ` The existing router (${report.existingAssets.routerAgent}) remains authoritative; team-ai did not generate a second one.`
        : "";
    appendFileSync(
      join(renderDir, "docs/architecture.md"),
      `\n\n## Coexistence boundary\n\nteam-ai runs in extend mode. Adopted (kept as-is): ${adopted}. ` +
        "team-ai added only the deterministic layer (schemas, scripts, index, gap log)." +
        `${routerClause}\n`,
      "utf8",
    );
  }

  if (hosting === "local-stdio" && !standDown) {
    const mcp = await renderTree({
      templateDir: TEMPLATES_MCP,
      destDir: join(renderDir, "mcp-server"),
      context,
      onCollision: "skip",
    });
    result.created.push(...mcp.created);
    result.unchanged.push(...mcp.unchanged);
    result.collisions.push(...mcp.collisions);
  }

  if (!standDown) {
    await reindex.run({ root: renderDir });
    await assembleManifest.run({ root: renderDir });
    await doctor.run({ root: renderDir });
  }

  summary(result, output);
  return 0;
}
