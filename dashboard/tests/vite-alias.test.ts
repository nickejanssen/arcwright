// AW-329: the dashboard's real Vite config lets a package renderer find the
// kit by the name @arcwright/mini-game-kit, and the registry bindings find the
// Tell Me Something True package and its definition by path.

import assert from "node:assert/strict";
import { join } from "node:path";
import test from "node:test";
import { build } from "vite";

const dashboardDir = process.env.DASHBOARD_DIR ?? process.cwd();

test("a Vite build with the dashboard config bundles the packages' own renderer", async () => {
  const output = await build({
    root: dashboardDir,
    configFile: join(dashboardDir, "vite.config.ts"),
    logLevel: "silent",
    build: {
      write: false,
      minify: false,
      lib: {
        entry: join(dashboardDir, "src", "mini-games", "registry-bindings.ts"),
        formats: ["es"],
        fileName: "bindings",
      },
    },
  });
  const outputs = Array.isArray(output) ? output : [output];
  const code = outputs
    .flatMap((o) => ("output" in o ? o.output : []))
    .map((chunk) => ("code" in chunk ? chunk.code : String(chunk.source)))
    .join("\n");

  assert.match(code, /tell-me-something-true/, "renderer and definition found");
  assert.match(code, /tmst-shell/, "the package's own screen code is bundled");
  assert.doesNotMatch(
    code,
    /fixture-individual/,
    "test fixtures are not shipped",
  );
});
