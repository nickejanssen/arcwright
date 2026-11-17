import { cpSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

import { afterEach, describe, expect, it } from "vitest";

import { prepareConnectorProbe, scanPreflight } from "./preflight.js";
import { renderPreflight } from "./preflight-report.js";

function fixture(name: string): string {
  return fileURLToPath(new URL(`./fixtures/${name}`, import.meta.url));
}

function source(file: string): string {
  return readFileSync(fileURLToPath(new URL(`./${file}`, import.meta.url)), "utf8");
}

const dirs: string[] = [];

afterEach(() => {
  for (const dir of dirs.splice(0)) rmSync(dir, { recursive: true, force: true });
});

describe("scanPreflight", () => {
  it("pf-extend: extends an existing harness and adopts AGENTS.md", async () => {
    const report = await scanPreflight(fixture("pf-extend"));

    expect(report.assessment).toBe("extend");
    expect(report.existingAssets.agentConfigFile).toBe("AGENTS.md");
    expect(report.existingAssets.routerAgent).toBe("agents/sme.yaml");
    expect(report.found.agentConfig).toContain("AGENTS.md");
    expect(report.found.mcpServers).toContain(".mcp.json");

    expect(report.adoptNote).toBeDefined();
    expect(report.adoptNote).toContain("Adopt AGENTS.md");
    expect(report.adoptNote).toContain("agents/sme.yaml");
  });

  it("pf-bare: finds nothing and lands on coexist", async () => {
    const report = await scanPreflight(fixture("pf-bare"));

    expect(report.assessment).toBe("coexist");
    expect(report.found.mcpServers).toEqual([]);
    expect(report.found.agentConfig).toEqual([]);
    expect(report.found.vectorStore).toEqual([]);
    expect(report.found.orgSearch).toEqual([]);
    expect(report.found.skillsPlugins).toEqual([]);
    expect(report.existingAssets.agents).toEqual([]);
    expect(report.existingAssets.kbDocCount).toBe(0);
    expect(report.adoptNote).toBeUndefined();
  });

  it("pf-standdown: org search present, no agent config, clean stand-down", async () => {
    const report = await scanPreflight(fixture("pf-standdown"));

    expect(report.assessment).toBe("stand-down");
    expect(report.found.orgSearch.length).toBeGreaterThan(0);
    expect(report.found.agentConfig).toEqual([]);
    expect(report.adoptNote).toBeUndefined();
    expect(report.rationale).toMatch(/stand|contribute/i);
  });

  it("counts documents from the declared KB root and skips exclusions", async () => {
    const dir = mkdtempSync(join(tmpdir(), "team-ai-preflight-"));
    dirs.push(dir);
    cpSync("src/kb/fixtures/kb", join(dir, "docs"), { recursive: true });
    mkdirSync(join(dir, "docs", "archive"), { recursive: true });
    writeFileSync(join(dir, "docs", "archive", "bad.md"), "no front matter", "utf8");
    writeFileSync(
      join(dir, "index.lock"),
      "driver: lexical\nchunk:\n  split_on: [h2, h3]\n  target_tokens: 800\n  hard_cap: 1200\nembedding: null\nkb:\n  root: docs\n  exclude: [archive/]\n",
      "utf8",
    );

    const report = await scanPreflight(dir);
    expect(report.existingAssets.kbDocCount).toBe(3);
  });

  it("treats a malformed index.lock as zero KB documents instead of aborting", async () => {
    const dir = mkdtempSync(join(tmpdir(), "team-ai-preflight-"));
    dirs.push(dir);
    writeFileSync(join(dir, "index.lock"), "driver: ''\n", "utf8");

    await expect(scanPreflight(dir)).resolves.toMatchObject({
      existingAssets: { kbDocCount: 0 },
    });
  });
});

describe("prepareConnectorProbe", () => {
  it("detects a github connector and prepares five sample questions", async () => {
    const probe = await prepareConnectorProbe(fixture("pf-extend"));

    expect(probe.connectorDetected).toBe("github");
    expect(probe.sampleQuestions).toHaveLength(5);
    expect(probe.manualSteps.length).toBeGreaterThan(0);
    expect(probe.recordSlot).toBe("not-run");
  });

  it("returns null when no connector is configured", async () => {
    const probe = await prepareConnectorProbe(fixture("pf-bare"));

    expect(probe.connectorDetected).toBeNull();
    expect(probe.sampleQuestions).toEqual([]);
    expect(probe.manualSteps).toEqual([]);
    expect(probe.recordSlot).toBe("not-run");
  });
});

describe("renderPreflight", () => {
  it("renders the PREFLIGHT body with the assessment and adopt note", async () => {
    const body = renderPreflight(await scanPreflight(fixture("pf-extend")));

    expect(body).toContain("PREFLIGHT");
    expect(body).toContain("Assessment:");
    expect(body).toContain("Adopt AGENTS.md");
  });

  it("renders a stand-down assessment", async () => {
    const body = renderPreflight(await scanPreflight(fixture("pf-standdown")));

    expect(body).toContain("PREFLIGHT");
    expect(body).toContain("Assessment: STAND-DOWN");
  });
});

describe("preflight makes no model or retrieval calls", () => {
  it("preflight.ts and preflight-report.ts contain no fetch / anthropic / search( calls", () => {
    for (const file of ["preflight.ts", "preflight-report.ts"]) {
      const text = source(file);
      expect(text, file).not.toMatch(/\bfetch\s*\(/);
      expect(text, file).not.toMatch(/anthropic/i);
      expect(text, file).not.toMatch(/\bsearch\s*\(/);
    }
  });
});
