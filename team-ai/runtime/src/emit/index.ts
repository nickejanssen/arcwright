// Deterministic. No model calls. No network.
//
// `loadEmitInput` reads a generated instance into the neutral shape the three
// emitters consume: agent definitions with their instruction bodies, skills,
// personas, and the routing manifest. Emitters translate this shape into a
// target platform's on-disk convention — they never re-derive it.

import { existsSync, readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";

import { parse as parseYaml } from "yaml";

import { validate } from "../schema/validate.js";
import type { AgentDef, Manifest } from "../schema/types.js";

export interface EmitAgent {
  name: string;
  def: AgentDef;
  instructions: string;
}

export interface EmitNamed {
  name: string;
  body: string;
}

export interface EmitInput {
  agents: EmitAgent[];
  skills: EmitNamed[];
  personas: EmitNamed[];
  manifest: Manifest | null;
}

function listFiles(dir: string): string[] {
  if (!existsSync(dir)) return [];
  return readdirSync(dir, { withFileTypes: true })
    .filter((entry) => entry.isFile())
    .map((entry) => entry.name)
    .sort((a, b) => (a < b ? -1 : a > b ? 1 : 0));
}

function listDirs(dir: string): string[] {
  if (!existsSync(dir)) return [];
  return readdirSync(dir, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => entry.name)
    .sort((a, b) => (a < b ? -1 : a > b ? 1 : 0));
}

function loadAgents(instanceDir: string): EmitAgent[] {
  const agentsDir = join(instanceDir, "agents");
  const out: EmitAgent[] = [];
  for (const file of listFiles(agentsDir)) {
    if (!file.endsWith(".yaml")) continue;
    const name = file.slice(0, -".yaml".length);
    const parsed: unknown = parseYaml(readFileSync(join(agentsDir, file), "utf8"));
    const result = validate("agent", parsed);
    if (!result.ok) continue;
    const mdPath = join(agentsDir, `${name}.md`);
    const instructions = existsSync(mdPath) ? readFileSync(mdPath, "utf8") : "";
    out.push({ name, def: result.value, instructions });
  }
  return out;
}

function loadSkills(instanceDir: string): EmitNamed[] {
  const skillsDir = join(instanceDir, "skills");
  const out: EmitNamed[] = [];
  for (const name of listDirs(skillsDir)) {
    const skillFile = join(skillsDir, name, "SKILL.md");
    if (!existsSync(skillFile)) continue;
    out.push({ name, body: readFileSync(skillFile, "utf8") });
  }
  return out;
}

function loadPersonas(instanceDir: string): EmitNamed[] {
  const personasDir = join(instanceDir, "personas");
  const out: EmitNamed[] = [];
  for (const file of listFiles(personasDir)) {
    if (!file.endsWith(".md")) continue;
    out.push({
      name: file.slice(0, -".md".length),
      body: readFileSync(join(personasDir, file), "utf8"),
    });
  }
  return out;
}

function loadManifest(instanceDir: string): Manifest | null {
  const manifestPath = join(instanceDir, "manifest.yaml");
  if (!existsSync(manifestPath)) return null;
  const parsed: unknown = parseYaml(readFileSync(manifestPath, "utf8"));
  const result = validate("manifest", parsed);
  return result.ok ? result.value : null;
}

export function loadEmitInput(instanceDir: string): Promise<EmitInput> {
  return Promise.resolve({
    agents: loadAgents(instanceDir),
    skills: loadSkills(instanceDir),
    personas: loadPersonas(instanceDir),
    manifest: loadManifest(instanceDir),
  });
}
