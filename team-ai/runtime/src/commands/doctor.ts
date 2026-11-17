// Deterministic. No model calls. No network.
//
// `team-ai doctor` — environment and setup checks.
//
//   --self          framework self-verification (used by CI); exits non-zero on
//                   a real failure
//   --root <dir>    instance directory to check (default "."); report-only,
//                   exits 0 regardless of remaining items
//   --strict        treat "not built yet" (self) and remaining checklist items
//                   (instance) as failures for exit-code purposes
//
// The pure checks live in src/doctor/checks.ts so they can be tested against
// fixture directories without spawning the CLI.

import { runInstanceChecks, runSelfChecks, type CheckResult } from "../doctor/checks.js";

export interface DoctorOptions {
  root?: string;
  self?: boolean;
  strict?: boolean;
}

function render(result: CheckResult, bad: boolean): string {
  const mark = bad ? "✗" : "✓";
  const note = result.note !== undefined ? ` — ${result.note}` : "";
  return `${mark} ${result.label}${note}`;
}

function runSelf(strict: boolean): number {
  const results = runSelfChecks(process.cwd());
  let failures = 0;
  for (const result of results) {
    const bad = strict ? !result.ok || result.skipped === true : !result.ok;
    if (bad) failures += 1;
    console.log(render(result, bad));
  }
  return failures > 0 ? 1 : 0;
}

async function runInstance(root: string, strict: boolean): Promise<number> {
  const results = await runInstanceChecks(root);
  let remaining = 0;
  for (const result of results) {
    const bad = !result.ok;
    if (bad) remaining += 1;
    console.log(render(result, bad));
  }
  console.log(`${remaining} item(s) remaining. See SETUP.md.`);
  return strict && remaining > 0 ? 1 : 0;
}

export async function run(opts: DoctorOptions): Promise<number> {
  const strict = opts.strict === true;
  if (opts.self === true) return runSelf(strict);
  return runInstance(opts.root ?? ".", strict);
}
