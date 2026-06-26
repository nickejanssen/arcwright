#!/usr/bin/env node
// Manifest-scan based mini-game discovery and bundler.
//
// 1. Walks ../nightcap/mini_games/<game-id> and ../nightcap/mini_games/_fixtures/<game-id>
//    looking for manifest.json + client/renderer.ts pairs.
// 2. Generates a virtual registry-bindings module via esbuild plugin.
// 3. Runs esbuild on browser-entry.ts to produce dist/static/mini-games.js.
// 4. Copies each package's definition JSON to dist/static/mini-games/definitions/.
// 5. Asserts per-package and total bundle size budgets; exits non-zero on breach.

import { readFile, mkdir, readdir, copyFile } from "node:fs/promises";
import { existsSync } from "node:fs";
import { gzipSync } from "node:zlib";
import { fileURLToPath } from "node:url";
import { dirname, join, relative, resolve } from "node:path";
import { build as esbuild } from "esbuild";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const NIGHTCAP_WEB_ROOT = resolve(__dirname, "..");
const REPO_ROOT = resolve(NIGHTCAP_WEB_ROOT, "..");
const MINI_GAMES_ROOT = resolve(REPO_ROOT, "nightcap", "mini_games");
const KIT_ENTRY = resolve(
  NIGHTCAP_WEB_ROOT,
  "src",
  "mini-game-kit",
  "index.ts",
);
const KIT_ROOT = resolve(NIGHTCAP_WEB_ROOT, "src", "mini-game-kit");
const BROWSER_ENTRY = resolve(
  NIGHTCAP_WEB_ROOT,
  "src",
  "mini-games",
  "browser-entry.ts",
);
const BUNDLE_OUT = resolve(
  NIGHTCAP_WEB_ROOT,
  "dist",
  "static",
  "mini-games.js",
);
const DEFINITIONS_OUT = resolve(
  NIGHTCAP_WEB_ROOT,
  "dist",
  "static",
  "mini-games",
  "definitions",
);

// Budgets per spec 0050 Design Notes. esbuild emits one bundled JS for all
// registered renderers, so the gzip ceiling here covers the entire shipped
// payload. When mini-games start shipping as separate chunks the per-package
// budget will be enforced per output instead.
const BUNDLE_GZIP_BUDGET_BYTES = 30 * 1024;
const BUNDLE_UNCOMPRESSED_BUDGET_BYTES = 100 * 1024;

async function listDirEntries(dir) {
  if (!existsSync(dir)) return [];
  const entries = await readdir(dir, { withFileTypes: true });
  return entries.filter((e) => e.isDirectory()).map((e) => e.name);
}

async function findPackages() {
  const packages = [];
  const topLevel = await listDirEntries(MINI_GAMES_ROOT);
  for (const name of topLevel) {
    const pkgDir = join(MINI_GAMES_ROOT, name);
    if (name === "_fixtures") {
      const fixtures = await listDirEntries(pkgDir);
      for (const fixture of fixtures) {
        const dir = join(pkgDir, fixture);
        const pkg = await tryReadPackage(dir);
        if (pkg) packages.push(pkg);
      }
      continue;
    }
    if (name === "_template") continue;
    const pkg = await tryReadPackage(pkgDir);
    if (pkg) packages.push(pkg);
  }
  return packages;
}

async function tryReadPackage(dir) {
  const manifestPath = join(dir, "manifest.json");
  const rendererPath = join(dir, "client", "renderer.ts");
  if (!existsSync(manifestPath) || !existsSync(rendererPath)) {
    return null;
  }
  const manifest = JSON.parse(await readFile(manifestPath, "utf8"));
  const definitionPath = join(dir, manifest.definition_path);
  if (!existsSync(definitionPath)) {
    console.warn(
      `[discover] skip ${manifest.game_id}: missing definition at ${manifest.definition_path}`,
    );
    return null;
  }
  return {
    gameId: manifest.game_id,
    version: manifest.current_version,
    lifecycle: manifest.lifecycle,
    dir,
    rendererPath,
    definitionPath,
  };
}

function importIdentifier(gameId) {
  // Convert kebab-case game-id to camelCase identifier.
  return `${gameId.replace(/[^a-zA-Z0-9]+(.)/g, (_, c) => c.toUpperCase())}Renderer`;
}

function buildRegistryBindingsContents(packages) {
  const lines = [
    "// Virtual module produced by scripts/discover-mini-games.mjs.",
    'import { defaultRegistry } from "./registry.js";',
  ];
  for (const pkg of packages) {
    lines.push(
      `import ${importIdentifier(pkg.gameId)} from "${pkg.rendererPath.replace(/\\/g, "/")}";`,
    );
  }
  for (const pkg of packages) {
    lines.push(`defaultRegistry.register(${importIdentifier(pkg.gameId)});`);
  }
  return lines.join("\n") + "\n";
}

async function bundleEntry(packages) {
  await mkdir(dirname(BUNDLE_OUT), { recursive: true });
  const virtualBindingsContents = buildRegistryBindingsContents(packages);
  const result = await esbuild({
    entryPoints: [BROWSER_ENTRY],
    outfile: BUNDLE_OUT,
    bundle: true,
    format: "esm",
    target: ["es2022"],
    platform: "browser",
    sourcemap: false,
    minify: true,
    legalComments: "none",
    metafile: true,
    logLevel: "warning",
    alias: {
      "@arcwright/mini-game-kit": KIT_ENTRY,
    },
    plugins: [
      {
        name: "kit-subpath",
        setup(build) {
          build.onResolve(
            { filter: /^@arcwright\/mini-game-kit\// },
            (args) => ({
              path: resolve(
                KIT_ROOT,
                args.path.replace(/^@arcwright\/mini-game-kit\//, ""),
              ),
            }),
          );
        },
      },
      {
        name: "registry-bindings-virtual",
        setup(build) {
          build.onResolve({ filter: /registry-bindings\.js$/ }, () => ({
            path: "virtual:registry-bindings",
            namespace: "registry-bindings-virtual",
          }));
          build.onLoad(
            {
              filter: /^virtual:registry-bindings$/,
              namespace: "registry-bindings-virtual",
            },
            () => ({
              contents: virtualBindingsContents,
              resolveDir: dirname(BROWSER_ENTRY),
              loader: "ts",
            }),
          );
        },
      },
    ],
  });
  return result;
}

async function copyDefinitions(packages) {
  for (const pkg of packages) {
    const outDir = join(DEFINITIONS_OUT, pkg.gameId);
    await mkdir(outDir, { recursive: true });
    await copyFile(pkg.definitionPath, join(outDir, `${pkg.version}.json`));
    // Also write a stable "latest.json" alias.
    await copyFile(pkg.definitionPath, join(outDir, "latest.json"));
  }
}

function bytesToKb(bytes) {
  return (bytes / 1024).toFixed(2);
}

async function checkBudgets(metafile) {
  const outputs = metafile?.outputs ?? {};
  let totalBytes = 0;
  const breaches = [];
  for (const [path, info] of Object.entries(outputs)) {
    if (!path.endsWith(".js")) continue;
    totalBytes += info.bytes;
    const buf = await readFile(path);
    const gz = gzipSync(buf).length;
    if (gz > BUNDLE_GZIP_BUDGET_BYTES) {
      breaches.push(
        `bundle gzip ${bytesToKb(gz)}KB exceeds budget ${bytesToKb(BUNDLE_GZIP_BUDGET_BYTES)}KB`,
      );
    }
    console.log(
      `[discover] bundle ${relative(REPO_ROOT, path)}: ${bytesToKb(info.bytes)}KB uncompressed, ${bytesToKb(gz)}KB gzipped`,
    );
  }
  if (totalBytes > BUNDLE_UNCOMPRESSED_BUDGET_BYTES) {
    breaches.push(
      `total uncompressed ${bytesToKb(totalBytes)}KB exceeds budget ${bytesToKb(BUNDLE_UNCOMPRESSED_BUDGET_BYTES)}KB`,
    );
  }
  if (breaches.length > 0) {
    console.error("[discover] size budget breached:");
    for (const b of breaches) console.error(`  - ${b}`);
    process.exit(1);
  }
}

async function main() {
  const packages = await findPackages();
  if (packages.length === 0) {
    console.warn("[discover] no mini-game packages found");
  } else {
    console.log(
      `[discover] found ${packages.length} package(s): ${packages.map((p) => p.gameId).join(", ")}`,
    );
  }
  const result = await bundleEntry(packages);
  await copyDefinitions(packages);
  await checkBudgets(result.metafile);
  console.log("[discover] done");
}

await main();
