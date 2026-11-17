// Deterministic. No model calls. No network.
//
// The Act 0 preflight scan (interview-spec.md §4, architecture.md §4). It reads
// the target repo's filesystem only, classifies what already exists as
// extend / coexist / stand-down, and reports which existing assets a later
// generator run must preserve (design-of-record §18).

import type { Dirent } from "node:fs";
import { readdir, readFile, stat } from "node:fs/promises";
import { basename, join } from "node:path";

import { parse as parseYaml } from "yaml";

import { KbValidationError, loadKb } from "../kb/loader.js";
import { resolveKbScope } from "../retrieval/index-lock.js";
import {
  AGENT_CONFIG_DIRS,
  AGENT_CONFIG_FILES,
  MCP_CONFIG_FILES,
  ORG_SEARCH_MARKERS,
  SKILL_PLUGIN_DIRS,
  VECTOR_ENV_HINTS,
} from "./preflight-signals.js";

export interface ExistingAssets {
  agentConfigFile?: string;
  routerAgent?: string;
  agents: string[];
  kbDocCount: number;
  skills: string[];
}

export interface PreflightReport {
  found: {
    mcpServers: string[];
    agentConfig: string[];
    vectorStore: string[];
    orgSearch: string[];
    skillsPlugins: string[];
  };
  existingAssets: ExistingAssets;
  assessment: "extend" | "coexist" | "stand-down";
  rationale: string;
  adoptNote?: string;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function toPosix(path: string): string {
  return path.split(/[\\/]/).join("/");
}

async function pathExists(target: string): Promise<boolean> {
  try {
    await stat(target);
    return true;
  } catch {
    return false;
  }
}

async function existingFrom(dir: string, candidates: readonly string[]): Promise<string[]> {
  const out: string[] = [];
  for (const rel of candidates) {
    if (await pathExists(join(dir, rel))) out.push(rel);
  }
  return out;
}

// `.env`, `.env.example`, `.env.local` — report the matched hint prefix(es), not
// the raw keys, so nothing sensitive is echoed into docs/preflight.md.
async function scanVectorEnv(dir: string): Promise<string[]> {
  const hits = new Set<string>();
  for (const file of [".env", ".env.example", ".env.local"]) {
    let content: string;
    try {
      content = await readFile(join(dir, file), "utf8");
    } catch {
      continue;
    }
    for (const rawLine of content.split(/\r?\n/)) {
      const line = rawLine.trim();
      if (line.length === 0 || line.startsWith("#")) continue;
      const eq = line.indexOf("=");
      if (eq < 0) continue;
      let key = line.slice(0, eq).trim();
      if (key.startsWith("export ")) key = key.slice("export ".length).trim();
      const upper = key.toUpperCase();
      for (const hint of VECTOR_ENV_HINTS) {
        if (upper.startsWith(hint)) hits.add(hint);
      }
    }
  }
  return [...hits].sort((a, b) => a.localeCompare(b));
}

async function listAgentFiles(dir: string): Promise<string[]> {
  const out: string[] = [];
  for (const root of ["agents", ".claude/agents"]) {
    let entries: string[];
    try {
      entries = await readdir(join(dir, root), { recursive: true });
    } catch {
      continue;
    }
    for (const entry of entries) {
      if (/\.(ya?ml|md)$/i.test(entry)) out.push(`${root}/${toPosix(entry)}`);
    }
  }
  return out.sort((a, b) => a.localeCompare(b));
}

async function detectRouterAgent(dir: string, agentPaths: string[]): Promise<string | undefined> {
  for (const rel of agentPaths) {
    try {
      const parsed: unknown = parseYaml(await readFile(join(dir, rel), "utf8"));
      if (isRecord(parsed) && parsed.kind === "router") return rel;
    } catch {
      // not YAML / unreadable — fall through to the filename heuristic
    }
    const stem = basename(rel).replace(/\.[^.]+$/, "");
    if (/sme|router/i.test(stem)) return rel;
  }
  return undefined;
}

// Prefer AGENTS.md when both it and CLAUDE.md exist — AGENTS.md is the
// authoritative file in this ecosystem.
async function pickAgentConfigFile(dir: string): Promise<string | undefined> {
  const hasAgents = await pathExists(join(dir, "AGENTS.md"));
  const hasClaude = await pathExists(join(dir, "CLAUDE.md"));
  if (hasAgents && hasClaude) return "AGENTS.md";
  for (const file of AGENT_CONFIG_FILES) {
    if (await pathExists(join(dir, file))) return file;
  }
  return undefined;
}

async function countKbDocs(dir: string): Promise<number> {
  try {
    const scope = resolveKbScope(dir);
    return (await loadKb(scope.root, { exclude: scope.exclude })).length;
  } catch (err) {
    // Best effort: a partially-invalid KB still means "a KB exists here".
    if (err instanceof KbValidationError) return err.failures.length;
    return 0;
  }
}

async function listSkills(dir: string): Promise<string[]> {
  const names = new Set<string>();
  for (const root of ["skills", ".claude/skills"]) {
    const abs = join(dir, root);
    let entries: Dirent[];
    try {
      entries = await readdir(abs, { withFileTypes: true });
    } catch {
      continue;
    }
    for (const entry of entries) {
      if (entry.isDirectory() && (await pathExists(join(abs, entry.name, "SKILL.md")))) {
        names.add(entry.name);
      }
    }
  }
  return [...names].sort((a, b) => a.localeCompare(b));
}

function assess(
  found: PreflightReport["found"],
  assets: ExistingAssets,
): { assessment: PreflightReport["assessment"]; rationale: string } {
  const hasAgentConfig = found.agentConfig.length > 0;
  const hasOrgSearch = found.orgSearch.length > 0;
  const bigKb = assets.kbDocCount > 20;

  // Org enterprise-search marker present and no compatible harness → lean
  // stand-down. An existing large KB only reinforces it.
  if (hasOrgSearch && !hasAgentConfig) {
    const kbClause = bigKb
      ? ` An existing knowledge base of ${assets.kbDocCount} documents is already in place.`
      : "";
    return {
      assessment: "stand-down",
      rationale:
        `Org enterprise-search markers (${found.orgSearch.join(", ")}) are present and no ` +
        `compatible agent config was found.${kbClause} The cheaper honest path is to contribute ` +
        `documents to that search and generate only the manifest, agents, personas, and skills layers.`,
    };
  }

  // A compatible harness exists → extend it. If an org search also exists, keep
  // building but flag the overlap in the rationale.
  if (hasAgentConfig) {
    const base =
      `A compatible agent harness already exists (${found.agentConfig.join(", ")}); ` +
      `team-ai will register alongside it rather than creating a parallel config.`;
    const overlap = hasOrgSearch
      ? ` An org enterprise-search marker (${found.orgSearch.join(", ")}) is also present: ` +
        `if your team's questions are mostly "where is the doc", contributing to that ` +
        `deployment may matter more than a new index.`
      : "";
    return { assessment: "extend", rationale: base + overlap };
  }

  const partial: string[] = [];
  if (found.mcpServers.length > 0) partial.push(`MCP config (${found.mcpServers.join(", ")})`);
  if (found.vectorStore.length > 0) {
    partial.push(`vector-store env hints (${found.vectorStore.join(", ")})`);
  }
  if (found.skillsPlugins.length > 0) {
    partial.push(`skill directories (${found.skillsPlugins.join(", ")})`);
  }
  const partialClause = partial.length > 0 ? ` Partial signals: ${partial.join("; ")}.` : "";
  return {
    assessment: "coexist",
    rationale:
      `No existing agent harness or org enterprise-search marker was conclusive.${partialClause} ` +
      `team-ai will generate a standalone setup and record the boundary in docs/architecture.md.`,
  };
}

export async function scanPreflight(dir: string): Promise<PreflightReport> {
  const found: PreflightReport["found"] = {
    mcpServers: await existingFrom(dir, MCP_CONFIG_FILES),
    agentConfig: [
      ...(await existingFrom(dir, AGENT_CONFIG_FILES)),
      ...(await existingFrom(dir, AGENT_CONFIG_DIRS)),
    ],
    vectorStore: await scanVectorEnv(dir),
    orgSearch: await existingFrom(dir, ORG_SEARCH_MARKERS),
    skillsPlugins: await existingFrom(dir, SKILL_PLUGIN_DIRS),
  };

  const agents = await listAgentFiles(dir);
  const routerAgent = await detectRouterAgent(dir, agents);
  const agentConfigFile = await pickAgentConfigFile(dir);

  const existingAssets: ExistingAssets = {
    agents,
    kbDocCount: await countKbDocs(dir),
    skills: await listSkills(dir),
  };
  if (agentConfigFile !== undefined) existingAssets.agentConfigFile = agentConfigFile;
  if (routerAgent !== undefined) existingAssets.routerAgent = routerAgent;

  const { assessment, rationale } = assess(found, existingAssets);
  const report: PreflightReport = { found, existingAssets, assessment, rationale };

  if (assessment === "extend" && agentConfigFile !== undefined) {
    let note = `Adopt ${agentConfigFile} — register alongside it, do not create a parallel config.`;
    if (routerAgent !== undefined) {
      note += ` An existing SME/router (${routerAgent}) is present; team-ai will not generate a second one.`;
    }
    report.adoptNote = note;
  }

  return report;
}

// Detects connectors and prepares the probe steps only. It never calls a model
// or runs retrieval — see docs/design/2026-08-30-team-ai-framework-design.md §3.
// The operator runs the probe by hand and records the outcome at
// `pre.probe_result` in the interview.

const PROBE_RECORD_SLOT = "not-run" as const;

const SAMPLE_QUESTIONS: string[] = [
  "Where is the document that explains <a core workflow your team owns>?",
  "Which file defines <a key configuration value or default>?",
  "What does the onboarding material say about <a first-week task>?",
  "Where is the decision record for <a past architectural choice>?",
  "Who owns <a specific system or component>, and where is that written down?",
];

function probeSteps(connector: string): string[] {
  return [
    `1. Point your ${connector} connector at the docs/ directory of this repo (or the small structured document set you want to test).`,
    `2. Open the client where the ${connector} connector is configured (Claude Code, a Claude app, or your IDE).`,
    "3. Ask each of the 5 sample questions above, replacing the <...> placeholder with a real topic from your docs.",
    "4. For each answer, record whether it returned BOTH a usable answer and a findable source path.",
    "5. Count how many of the 5 questions produced a cited, usable answer.",
    "6. Report that count at the interview question pre.probe_result (continue / scale back to documents only / stop here).",
  ];
}

function collectServerKeys(parsed: unknown): string[] {
  if (!isRecord(parsed)) return [];
  const keys: string[] = [];
  for (const container of ["mcpServers", "servers"]) {
    const block = parsed[container];
    if (isRecord(block)) keys.push(...Object.keys(block));
  }
  return keys;
}

export async function prepareConnectorProbe(dir: string): Promise<{
  connectorDetected: string | null;
  sampleQuestions: string[];
  manualSteps: string[];
  recordSlot: "not-run";
}> {
  let connectorDetected: string | null = null;

  for (const rel of [...MCP_CONFIG_FILES, ".claude/mcp.json"]) {
    let parsed: unknown;
    try {
      parsed = JSON.parse(await readFile(join(dir, rel), "utf8"));
    } catch {
      continue;
    }
    const haystack = collectServerKeys(parsed).join(" ").toLowerCase();
    if (haystack.includes("github")) {
      connectorDetected = "github";
      break;
    }
    if (haystack.includes("gdrive") || haystack.includes("drive")) {
      connectorDetected = "drive";
      break;
    }
  }

  if (connectorDetected === null) {
    return {
      connectorDetected: null,
      sampleQuestions: [],
      manualSteps: [],
      recordSlot: PROBE_RECORD_SLOT,
    };
  }

  return {
    connectorDetected,
    sampleQuestions: [...SAMPLE_QUESTIONS],
    manualSteps: probeSteps(connectorDetected),
    recordSlot: PROBE_RECORD_SLOT,
  };
}
