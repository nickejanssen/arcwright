// Runs the dashboard's tests with Node's own test runner and no test
// framework. Node 20 (the version CI uses) cannot run TypeScript, and the
// dashboard's tsconfig does not emit, so each test file is bundled with
// esbuild first. esbuild comes with Vite; happy-dom is the repo's root tooling
// package (the same one nightcap-web's tests use). Neither is a dashboard
// dependency.

import { spawnSync } from "node:child_process";
import { mkdirSync, readdirSync, rmSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { build } from "esbuild";

const testsDir = dirname(fileURLToPath(import.meta.url));
const dashboardDir = resolve(testsDir, "..");
const outDir = join(dashboardDir, "node_modules", ".cache", "dashboard-tests");

function findTests(dir) {
  const found = [];
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const path = join(dir, entry.name);
    if (entry.isDirectory()) found.push(...findTests(path));
    else if (/\.test\.tsx?$/.test(entry.name)) found.push(path);
  }
  return found;
}

const entryPoints = findTests(testsDir);
if (entryPoints.length === 0) {
  console.error("no test files found under dashboard/tests");
  process.exit(1);
}

rmSync(outDir, { recursive: true, force: true });
mkdirSync(outDir, { recursive: true });

await build({
  entryPoints,
  outdir: outDir,
  outbase: testsDir,
  bundle: true,
  format: "esm",
  platform: "node",
  target: "node20",
  jsx: "automatic",
  logLevel: "warning",
  // Dependencies load from node_modules at run time; only our own code and the
  // mini-game packages are bundled.
  packages: "external",
  alias: {
    "@arcwright/mini-game-kit": join(
      dashboardDir,
      "src",
      "mini-game-kit",
      "index.ts",
    ),
  },
  // The bundles are ES modules inside a folder with no package.json type.
  outExtension: { ".js": ".mjs" },
});

const compiled = readdirSync(outDir, { recursive: true })
  .map((name) => join(outDir, String(name)))
  .filter((path) => path.endsWith(".test.mjs"));

const result = spawnSync(
  process.execPath,
  [
    "--import",
    pathToFileURL(join(testsDir, "node20-globals.mjs")).href,
    "--test",
    ...compiled,
  ],
  {
    stdio: "inherit",
    env: { ...process.env, DASHBOARD_DIR: dashboardDir },
  },
);
process.exit(result.status ?? 1);
