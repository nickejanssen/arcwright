import { execFileSync } from "node:child_process";
import { mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

import { renderTree } from "./render.js";

const MCP_DIR = fileURLToPath(new URL("../../templates/mcp-server", import.meta.url));

function tempDir(): string {
  return mkdtempSync(join(tmpdir(), "team-ai-mcp-"));
}

const context = {
  team: { name: "Platform", slug: "platform" },
  hosting: "local-stdio",
};

describe("templates/mcp-server", () => {
  it("renders a server.mjs that passes node --check and registers all five tools", async () => {
    const dest = tempDir();
    const res = await renderTree({ templateDir: MCP_DIR, destDir: dest, context });
    expect(res.warnings).toEqual([]);

    const server = readFileSync(join(dest, "server.mjs"), "utf8");
    for (const tool of ["kb_search", "kb_get", "kb_manifest", "kb_coverage_gap", "kb_freshness"]) {
      expect(server).toContain(tool);
    }
    expect(server).not.toContain("../src");
    expect(server).not.toMatch(/from "\.\.?\//);

    const checkPath = join(dest, "server.check.mjs");
    writeFileSync(checkPath, server, "utf8");
    expect(() => execFileSync("node", ["--check", checkPath])).not.toThrow();
  });

  it("never shells out through npx and resolves the CLI from TEAM_AI_CLI", async () => {
    const dest = tempDir();
    await renderTree({ templateDir: MCP_DIR, destDir: dest, context });
    const server = readFileSync(join(dest, "server.mjs"), "utf8");

    expect(server).not.toMatch(/\bnpx\b/);
    expect(server).toContain("TEAM_AI_CLI");
    expect(server).toContain("fileURLToPath");
    expect(server).toContain('"--instance", ROOT');
  });

  it("renders a package.json that parses with the slug name and stdio bin", async () => {
    const dest = tempDir();
    await renderTree({ templateDir: MCP_DIR, destDir: dest, context });
    const pkg = JSON.parse(readFileSync(join(dest, "package.json"), "utf8")) as {
      name: string;
      type: string;
      bin: Record<string, string>;
      dependencies: Record<string, string>;
    };
    expect(pkg.name).toBe("platform-kb-mcp");
    expect(pkg.type).toBe("module");
    expect(Object.values(pkg.bin)).toContain("server.mjs");
    expect(pkg.dependencies["@modelcontextprotocol/sdk"]).toBeDefined();
  });

  it("ships a node_modules gitignore", async () => {
    const dest = tempDir();
    await renderTree({ templateDir: MCP_DIR, destDir: dest, context });
    expect(readFileSync(join(dest, ".gitignore"), "utf8")).toContain("node_modules/");
  });
});
