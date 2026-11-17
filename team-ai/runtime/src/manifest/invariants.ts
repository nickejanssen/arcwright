// Deterministic. No model calls. No network.
//
// Checks the topology properties the manifest schema cannot express. team-ai has
// no agent runtime, so it cannot enforce hop limits while agents run; it can
// refuse to ship a configuration that violates them.

import type { AgentDef, Manifest } from "../schema/types.js";

export interface InvariantViolation {
  rule: string;
  subject: string;
  message: string;
}

const UNASSIGNED = "unassigned";

function sameList(a: string[], b: string[]): boolean {
  return a.length === b.length && a.every((value, i) => value === b[i]);
}

export function checkManifestInvariants(
  manifest: Manifest,
  definitions: Map<string, AgentDef>,
): InvariantViolation[] {
  const out: InvariantViolation[] = [];
  const agents = manifest.agents ?? [];
  if (agents.length === 0) return out;

  const names = new Set(agents.map((a) => a.name));
  const push = (rule: string, subject: string, message: string): void => {
    out.push({ rule, subject, message });
  };

  for (const [filenameStem, definition] of definitions) {
    if (definition.name !== filenameStem) {
      push(
        "definition-name-mismatch",
        filenameStem,
        `definition name '${definition.name}' does not match filename '${filenameStem}.yaml'`,
      );
    }
  }

  const routers = agents.filter((a) => a.kind === "router");
  if (routers.length !== 1) {
    push("one-router", "agents", `expected exactly one router, found ${routers.length}`);
  }
  for (const router of routers) {
    if (definitions.get(router.name)?.model_tier !== "none") {
      push("router-model-tier", router.name, "router definition must have model_tier: none");
    }
  }

  const specialistNamespaces = new Map<string, string>();
  for (const agent of agents.filter((a) => a.tier === 3)) {
    if (agent.max_hops !== 0 || agent.kb_namespaces.length !== 1) {
      push(
        "specialist-terminal",
        agent.name,
        "tier-3 agents need max_hops 0 and exactly one namespace",
      );
    }
    const ns = agent.kb_namespaces[0];
    if (ns !== undefined) {
      const owner = specialistNamespaces.get(ns);
      if (owner !== undefined) {
        push(
          "specialist-namespace-unique",
          agent.name,
          `namespace '${ns}' is also owned by ${owner}`,
        );
      } else {
        specialistNamespaces.set(ns, agent.name);
      }
    }
  }

  for (const domain of manifest.domains) {
    if (!names.has(domain.subagent)) {
      push("domain-subagent", domain.id, `subagent '${domain.subagent}' is not a manifest agent`);
    }
    if (
      domain.escalate_to !== undefined &&
      domain.escalate_to !== UNASSIGNED &&
      !names.has(domain.escalate_to)
    ) {
      push("escalate-to", domain.id, `escalate_to '${domain.escalate_to}' is not a manifest agent`);
    }
  }

  for (const agent of agents) {
    if (
      agent.escalate_to !== undefined &&
      agent.escalate_to !== UNASSIGNED &&
      !names.has(agent.escalate_to)
    ) {
      push("escalate-to", agent.name, `escalate_to '${agent.escalate_to}' is not a manifest agent`);
    }
    const definition = definitions.get(agent.name);
    if (definition === undefined) {
      if (!(agent.source === "authored" && agent.path)) {
        push("definition-missing", agent.name, "no agents/<name>.yaml definition");
      }
      continue;
    }
    if (
      definition.max_hops !== agent.max_hops ||
      !sameList(definition.kb_namespaces, agent.kb_namespaces)
    ) {
      push(
        "definition-mismatch",
        agent.name,
        "definition max_hops or kb_namespaces disagree with the manifest",
      );
    }
  }

  return out;
}
