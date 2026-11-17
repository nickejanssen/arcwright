// Deterministic orchestration. No model calls. No network.
//
// `team-ai resume` re-opens a completed interview from `team-profile.yaml` and
// asks only the questions that are newly relevant — a question whose `ask_if`
// gate is now true but which the saved profile never answered (typically a
// question added to the bank by a framework upgrade). If nothing new is asked,
// resume writes nothing. Otherwise it re-runs `writeOutputs` and re-renders the
// instance templates non-destructively, exactly as `init` does.

import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";

import { input, checkbox, select } from "@inquirer/prompts";
import { parse as parseYaml } from "yaml";

import { evalAskIf } from "../interview/ask-if.js";
import { loadBank } from "../interview/bank.js";
import { Engine } from "../interview/engine.js";
import type { Question } from "../interview/types.js";
import { writeOutputs } from "../interview/outputs.js";
import { buildContext } from "./context.js";
import { computeExclude, renderEntityFiles, TEMPLATES_INSTANCE } from "./entity-files.js";
import { mergeGeneratedManifest, readGeneratedManifest } from "./generated-manifest.js";
import { renderTree } from "./render.js";
import { stateFromProfile, type ProfileShape } from "./state-from-profile.js";
import type { AnswerSource } from "./init-answers.js";

export interface ResumeOptions {
  dir?: string;
  catalog?: string;
  answers?: AnswerSource;
  output?: (s: string) => void;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function readProfile(dir: string): ProfileShape | null {
  const file = join(dir, "team-profile.yaml");
  if (!existsSync(file)) return null;
  let parsed: unknown;
  try {
    parsed = parseYaml(readFileSync(file, "utf8"));
  } catch {
    return null;
  }
  if (!isRecord(parsed)) return null;
  const answers = isRecord(parsed.answers) ? parsed.answers : {};
  const deferred = Array.isArray(parsed.deferred)
    ? (parsed.deferred as ProfileShape["deferred"])
    : [];
  return { answers, deferred };
}

function resolveOption(question: Question, token: string): string {
  const trimmed = token.trim();
  const byValue = question.options.find((o) => o.value === trimmed);
  if (byValue) return byValue.value;
  if (/^\d+$/.test(trimmed)) {
    const option = question.options[Number.parseInt(trimmed, 10) - 1];
    if (option) return option.value;
  }
  const lower = trimmed.toLowerCase();
  const byLabel = question.options.find((o) => o.label.toLowerCase() === lower);
  if (byLabel) return byLabel.value;
  throw new Error(`'${token}' does not match an option for '${question.id}'`);
}

function resolveAnswer(question: Question, raw: string): unknown {
  if (question.type === "single_select") return resolveOption(question, raw);
  if (question.type === "multi_select") {
    return raw
      .split(",")
      .map((part) => part.trim())
      .filter((part) => part.length > 0)
      .map((part) => resolveOption(question, part));
  }
  return raw;
}

async function promptRaw(question: Question, pull: AnswerSource | undefined): Promise<string> {
  if (pull) return pull(question.id);
  if (question.type === "multi_select") {
    const picked = await checkbox({
      message: question.prompt,
      choices: question.options.map((o) => ({ name: o.label, value: o.value })),
    });
    return picked.join(",");
  }
  if (question.type === "single_select") {
    return select({
      message: question.prompt,
      choices: question.options.map((o) => ({ name: o.label, value: o.value })),
    });
  }
  return input({ message: question.prompt });
}

export async function run(opts: ResumeOptions): Promise<number> {
  const output = opts.output ?? ((s: string): void => console.log(s));
  const dir = opts.dir ?? ".";

  const profile = readProfile(dir);
  if (!profile) {
    output("resume: no team-profile.yaml found; run 'team-ai init' first");
    return 1;
  }

  const bank = loadBank();
  const engine = Engine.load(bank, stateFromProfile(bank, profile));
  const answered = new Set(Object.keys(profile.answers));

  const newlyAnswered: string[] = [];
  for (const question of bank) {
    if (answered.has(question.id)) continue;
    if (!evalAskIf(question.ask_if, engine.effectiveAnswers())) continue;
    output(question.prompt);
    for (;;) {
      const raw = (await promptRaw(question, opts.answers)).trim();
      if (raw.length === 0 && question.allow_defer) {
        engine.skip(question.id);
        break;
      }
      try {
        engine.answer(question.id, resolveAnswer(question, raw));
        break;
      } catch (err) {
        output(err instanceof Error ? err.message : String(err));
        if (opts.answers) {
          // A scripted puller cannot recover from a bad token; stop asking.
          engine.skip(question.id);
          break;
        }
      }
    }
    newlyAnswered.push(question.id);
  }

  if (newlyAnswered.length === 0) {
    output("resume: nothing to update (profile is current)");
    return 0;
  }

  const priorManifest = readGeneratedManifest(dir);
  const priorByPath = new Map<string, string>(priorManifest.map((e) => [e.path, e.sha256]));
  const context = buildContext(
    engine,
    opts.catalog !== undefined ? { instanceCatalogDir: opts.catalog } : {},
  );
  const exclude = computeExclude(context.seed === true, false);

  // `writeOutputs` rewrites the interview docs and the profile, but not the
  // preflight report, which is not derived from answers — preserve it verbatim.
  const preflightPath = join(dir, "docs/preflight.md");
  const preflightDoc = existsSync(preflightPath) ? readFileSync(preflightPath, "utf8") : null;

  await writeOutputs(engine, dir);
  if (preflightDoc !== null) writeFileSync(preflightPath, preflightDoc, "utf8");

  const result = await renderTree({
    templateDir: TEMPLATES_INSTANCE,
    destDir: dir,
    context,
    priorManifest,
    onCollision: "skip",
    exclude,
  });
  renderEntityFiles(context, dir, priorByPath, "skip", result);
  mergeGeneratedManifest(dir, result.manifestEntries);

  output("");
  output(`resume: answered ${newlyAnswered.length} new question(s): ${newlyAnswered.join(", ")}`);
  output(
    `${result.created.length} file(s) created, ${result.updated.length} updated, ` +
      `${result.collisions.length} kept (locally modified).`,
  );
  for (const collision of result.collisions) {
    output(`  kept your version, skipped: ${collision}`);
  }
  output(
    "Run 'team-ai assemble-manifest' and 'team-ai reindex' to refresh the routing table and index.",
  );
  return 0;
}
