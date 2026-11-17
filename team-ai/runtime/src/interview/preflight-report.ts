// Deterministic. No model calls. No network.
//
// renderPreflight turns a PreflightReport into the body of docs/preflight.md,
// matching the layout in interview-spec.md §4: a PREFLIGHT header, a Found
// bullet list (checkmark for present, cross for checked-but-absent), an
// Assessment line with the rationale, the adopt note, and a connector-probe
// section.

import type { PreflightReport } from "./preflight.js";

const PRESENT = "✓";
const ABSENT = "✗";

function foundLines(found: PreflightReport["found"]): string[] {
  const row = (ok: boolean, present: string, absent: string): string =>
    ok ? `  ${PRESENT} ${present}` : `  ${ABSENT} ${absent}`;

  return [
    row(
      found.mcpServers.length > 0,
      `MCP config present: ${found.mcpServers.join(", ")}`,
      "No MCP config detected",
    ),
    row(
      found.agentConfig.length > 0,
      `Agent config present: ${found.agentConfig.join(", ")}`,
      "No existing agent config detected",
    ),
    row(
      found.vectorStore.length > 0,
      `Vector-store env hints: ${found.vectorStore.join(", ")}`,
      "No existing vector store detected",
    ),
    row(
      found.orgSearch.length > 0,
      `Org enterprise-search markers: ${found.orgSearch.join(", ")}`,
      "No org enterprise-search marker detected",
    ),
    row(
      found.skillsPlugins.length > 0,
      `Skill / plugin directories: ${found.skillsPlugins.join(", ")}`,
      "No skill or plugin directories detected",
    ),
  ];
}

function connectorSection(found: PreflightReport["found"]): string[] {
  if (found.mcpServers.length === 0) {
    return ["Connector probe", "  No repo or drive connector detected. Nothing to probe."];
  }
  return [
    "Connector probe",
    `  Connector config detected (${found.mcpServers.join(", ")}).`,
    "  Run prepareConnectorProbe for the 5 sample questions and the manual steps.",
    "  This scan runs no model and no retrieval; the operator records the outcome at pre.probe_result.",
  ];
}

export function renderPreflight(report: PreflightReport): string {
  const { found, existingAssets, assessment, rationale } = report;
  const out: string[] = ["PREFLIGHT", "", "Found", ...foundLines(found), ""];

  out.push(`Assessment: ${assessment.toUpperCase()}`);
  for (const line of rationale.split(/\r?\n/)) out.push(`  ${line}`);

  if (report.adoptNote !== undefined) {
    out.push("", `  ${report.adoptNote}`);
  }

  out.push(
    "",
    "Existing assets",
    `  agent config file: ${existingAssets.agentConfigFile ?? "none"}`,
    `  router / SME agent: ${existingAssets.routerAgent ?? "none"}`,
    `  agent definitions: ${existingAssets.agents.length}`,
    `  KB documents: ${existingAssets.kbDocCount}`,
    `  skills: ${existingAssets.skills.length > 0 ? existingAssets.skills.join(", ") : "none"}`,
    "",
    ...connectorSection(found),
    "",
  );

  return out.join("\n");
}
