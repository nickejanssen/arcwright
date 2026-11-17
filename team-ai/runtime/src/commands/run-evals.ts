// Deterministic. No model calls.
//
// `team-ai run-evals` — replays every golden question under <root>/<golden>
// through the deterministic router and retrieval index, then prints a metric
// table (or the raw EvalReport JSON with --json) and exits non-zero when any
// gate fails or an answer exceeds its tier ceiling.
//
// Example files (first line contains "EXAMPLE", case-insensitive) are skipped:
// a fresh instance ships the example but no real golden set, and that is not an
// error. See docs/architecture.md §16.

import { readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";

import { parse as parseYaml } from "yaml";

import type { GoldenQuestion } from "../schema/types.js";
import { validate } from "../schema/validate.js";
import { computeReport, type EvalOutcome, type EvalReport } from "../evals/metrics.js";
import { loadGates, runGoldenFile } from "../evals/run.js";

export interface RunEvalsCommandOptions {
  root?: string;
  golden?: string;
  json?: boolean;
}

const GOLDEN_SUFFIX = ".golden.yaml";

function toPosix(path: string): string {
  return path.split(/[\\/]/).join("/");
}

function firstLine(text: string): string {
  return text.split(/\r?\n/, 1)[0] ?? "";
}

function errMessage(err: unknown): string {
  return err instanceof Error ? err.message : String(err);
}

interface CollectResult {
  questions: GoldenQuestion[];
  skipped: string[];
  error?: string;
}

function listGoldenFiles(dir: string): { files: string[] } | { error: string } {
  try {
    const files = readdirSync(dir, { withFileTypes: true })
      .filter((entry) => entry.isFile() && entry.name.endsWith(GOLDEN_SUFFIX))
      .map((entry) => entry.name)
      .sort();
    return { files };
  } catch (err) {
    return { error: `cannot read golden directory ${toPosix(dir)} — ${errMessage(err)}` };
  }
}

function collectQuestions(dir: string): CollectResult {
  const listed = listGoldenFiles(dir);
  if ("error" in listed) {
    return { questions: [], skipped: [], error: listed.error };
  }

  const questions: GoldenQuestion[] = [];
  const skipped: string[] = [];

  for (const file of listed.files) {
    const raw = readFileSync(join(dir, file), "utf8");
    if (firstLine(raw).toUpperCase().includes("EXAMPLE")) {
      skipped.push(file);
      continue;
    }

    let parsed: unknown;
    try {
      parsed = parseYaml(raw);
    } catch (err) {
      return { questions, skipped, error: `${file}: invalid YAML — ${errMessage(err)}` };
    }
    if (!Array.isArray(parsed)) {
      return { questions, skipped, error: `${file}: expected a YAML list of golden questions` };
    }
    for (const [index, item] of parsed.entries()) {
      const result = validate("golden", item);
      if (!result.ok) {
        return {
          questions,
          skipped,
          error: `${file}[${index}]: ${result.errors[0] ?? "invalid golden question"}`,
        };
      }
      questions.push(result.value);
    }
  }

  return { questions, skipped };
}

function pct(value: number): string {
  return `${(value * 100).toFixed(1)}%`.padStart(7);
}

function questionProblems(outcome: EvalOutcome): string[] {
  const problems: string[] = [];
  if (!outcome.refuseExpected && !outcome.hit) problems.push("expected path not in top 8");
  if (!outcome.citationsValid) problems.push("a cited path did not resolve");
  if (!outcome.routeCorrect) problems.push(`routed to '${outcome.routedTo}'`);
  if (!outcome.namespaceOk) problems.push("routed namespace != expect_namespace");
  if (!outcome.tierOk) problems.push(`tier '${outcome.tier}' exceeds ceiling`);
  if (outcome.refuseExpected && !outcome.refuseCorrect) problems.push("did not refuse");
  return problems;
}

interface MetricRow {
  name: string;
  value: number;
  threshold: number;
  pass: boolean;
}

function printReport(report: EvalReport): void {
  const { metrics, gates } = report;
  const gateRow = (name: string, value: number): MetricRow => {
    const gate = gates[name];
    return { name, value, threshold: gate?.threshold ?? 0, pass: gate?.pass ?? false };
  };
  const rows: MetricRow[] = [
    gateRow("hitRate", metrics.hitRate),
    gateRow("citationValidity", metrics.citationValidity),
    gateRow("coverage", metrics.coverage),
    {
      name: "tierCeiling",
      value: metrics.tierCeiling,
      threshold: 1,
      pass: metrics.tierCeiling === 1,
    },
  ];

  console.log(`golden questions: ${metrics.count}`);
  console.log("");
  console.log("metric             value   threshold  result");
  for (const entry of rows) {
    console.log(
      `${entry.name.padEnd(18)} ${pct(entry.value)}  ${pct(entry.threshold)}    ` +
        (entry.pass ? "PASS" : "FAIL"),
    );
  }

  console.log("");
  console.log("coverage by namespace:");
  for (const [namespace, value] of Object.entries(report.coverageByNamespace).sort()) {
    console.log(`  ${namespace.padEnd(24)} ${pct(value)}`);
  }

  const staleQuestions = report.outcomes.filter((outcome) => outcome.sourceChangedSinceGenerated);
  if (staleQuestions.length > 0) {
    console.log("");
    console.log("questions whose source document changed since they were written:");
    for (const outcome of staleQuestions) console.log(`  ${outcome.id}`);
  }

  const failing = report.outcomes
    .map((outcome) => ({ outcome, problems: questionProblems(outcome) }))
    .filter((entry) => entry.problems.length > 0);

  if (failing.length > 0) {
    console.log("");
    console.log("failing questions:");
    for (const entry of failing) {
      console.log(`  ${entry.outcome.id}: ${entry.problems.join("; ")}`);
    }
  }

  console.log("");
  console.log("diagnostics (reported, not gated — these describe the");
  console.log("deterministic harness, which is not the delivery path):");
  console.log(`routingAccuracy   ${pct(metrics.routingAccuracy)}`);
  console.log(`refusalRate       ${pct(metrics.refusalRate)}`);
  console.log(`namespaceAccuracy ${pct(metrics.namespaceAccuracy)}`);

  console.log("");
  console.log(report.pass ? "PASS" : "FAIL");
}

export async function run(opts: RunEvalsCommandOptions): Promise<number> {
  const root = opts.root ?? ".";
  const goldenDir = opts.golden ?? "evals/golden";
  const dir = join(root, goldenDir);
  const shown = toPosix(dir);

  const { questions, skipped, error } = collectQuestions(dir);
  for (const file of skipped) {
    console.log(`skipping ${file} (example file — first line contains EXAMPLE)`);
  }
  if (error !== undefined) {
    console.error(error);
    return 1;
  }
  if (questions.length === 0) {
    console.log(`no golden questions found (add <namespace>.golden.yaml files under ${shown})`);
    return 0;
  }

  const outcomes = await runGoldenFile(questions, { instanceDir: root });
  const report = computeReport(outcomes, loadGates(root));

  if (opts.json === true) {
    console.log(JSON.stringify(report, null, 2));
    return report.pass ? 0 : 1;
  }

  printReport(report);
  return report.pass ? 0 : 1;
}
