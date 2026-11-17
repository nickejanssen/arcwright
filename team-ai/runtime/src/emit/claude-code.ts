// Deterministic. No model calls. No network.
//
// Emit a generated instance as a Claude Code plugin layout: one agent markdown
// file per agent (YAML front matter from the `AgentDef`, the instruction body
// underneath) plus a minimal `.claude-plugin/plugin.json` that names the agents
// and skills the plugin ships.

import { mkdirSync, writeFileSync } from "node:fs";
import { dirname } from "node:path";

import { stringify as stringifyYaml } from "yaml";

import { resolveWithin } from "../generator/contain.js";
import type { ModelTier } from "../schema/types.js";
import { packageVersion } from "../version.js";
import type { EmitAgent, EmitInput } from "./index.js";

export interface EmitClaudeCodeOptions {
  filePrefix?: string;
  pluginManifest?: boolean;
  builtinSearch?: boolean;
  corpusTokens?: Record<string, number>;
  searchCommand?: string;
}

const BUILTIN_SEARCH_TOOLS = ["Read", "Grep", "Glob"];

// An agent told to run the ranked-search command needs a tool that can run it.
// Listing the command in the host's permission file pre-authorises it; it does
// not grant the tool. Without this, the agents holding the largest corpora are
// instructed to use their only viable retrieval strategy and cannot execute it.
const RANKED_SEARCH_TOOLS = [...BUILTIN_SEARCH_TOOLS, "Bash"];
const INVALID_FILE_PREFIX = /[<>:"/\\|?*]/;

function validateFilePrefix(filePrefix: string | undefined): void {
  if (filePrefix === undefined || filePrefix.length === 0) return;
  if (
    filePrefix.includes("..") ||
    filePrefix === "." ||
    INVALID_FILE_PREFIX.test(filePrefix) ||
    [...filePrefix].some((char) => char.charCodeAt(0) < 0x20)
  ) {
    throw new Error("filePrefix must be a filename-only prefix");
  }
}

// Agent names come from instance files a person can edit, so every path is
// resolved through `resolveWithin` rather than joined blindly.
function write(outDir: string, rel: string, content: string): string {
  const path = resolveWithin(outDir, rel);
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, content, "utf8");
  return path;
}

// The threshold decides the strategy; the emitted text deliberately states no
// token count. An exact count makes every generated agent a function of every
// KB document, so a seven-character edit to one document changes an agent file
// and fails the regeneration check. The number carried no decision value for
// the agent either way — the strategy is already chosen for it here.
const READ_ALL_TOKEN_LIMIT = 25_000;
const DEFAULT_SEARCH_COMMAND = "node ../team-ai/dist/cli.js";

// Claude Code reads `model`; `model_tier` is team-ai's own vocabulary and is
// inert to the host. Mapping one onto the other is what makes a declared cost
// tier real. `none` means the work needs no model judgement at all, so it takes
// the cheapest tier rather than being omitted. An absent `model` inherits the
// session default, which is the expensive outcome this mapping avoids.
const MODEL_FOR_TIER: Record<ModelTier, string> = {
  none: "haiku",
  small: "haiku",
  large: "sonnet",
};

// In Claude Code the host session routes. It sees every agent's description,
// holds the conversation, and can dispatch two specialists in parallel and
// reconcile them. An agent whose job is to hand off would need the Agent tool,
// and a hop through it reloads the host's instruction files, relays the
// question without the conversation, and puts a weaker picker in front of a
// stronger one. Delegating agents stay in the manifest for hosts that do not
// route, and are not emitted here.
function delegates(agent: EmitAgent): boolean {
  return agent.def.kind === "router" || agent.def.max_hops > 0;
}

// Emitted into every agent. A knowledge base records design, scope, intent and
// decisions; it goes stale on status, implementation and history, which have
// owners of their own. An agent that answers those from documents reads a stale
// line as fact, or infers order from numbering, and is believed because it
// cites.
const ANSWER_RULES = [
  "## Answering rules",
  "",
  "Your documents record design, scope, intent and decisions. Answer only those, and only from what the documents say.",
  "",
  "- Task status, whether code exists, what merged or when, and CI results each have an owning source: the issue tracker, the code, git history, CI. For any of them, name the owning source and stop, even when a document appears to state the answer. Documents go stale on these; the owning source does not. Never infer them from dates, numbering or wording.",
  "- Never state a percentage, estimate or score that no document states.",
  "- If you cannot find something, list the exact terms you searched and say it was not found under those terms. Never conclude that it does not exist.",
  "- If two documents disagree, cite both and say that they conflict.",
  "- If you state how many items there are, it must equal the number you list.",
].join("\n");

// The instance's instructions file is written for hosts that provide team-ai's
// own retrieval tools, so its procedure names tools this host does not have.
// Only its `## Domain rules` section carries over: the part that is about the
// domain rather than about the tools.
function domainRules(instructions: string): string {
  const match = /^## Domain rules[^\n]*\n([\s\S]*?)(?=^## |(?![\s\S]))/m.exec(instructions);
  const rules = match?.[1]?.trim() ?? "";
  return rules.length > 0 ? `## Domain rules\n\n${rules}` : "";
}

// Twice an emitted agent was told to do something its tool list could not do —
// run a search command without Bash, hand off without Agent — and both failed
// silently in use. Emit refuses to write such an agent instead.
function assertToolsCoverInstructions(name: string, tools: string[], body: string): void {
  const required = new Set<string>();
  if (/```(?:bash|sh)\b/.test(body)) required.add("Bash");
  if (/\b(?:hand off to|delegate to)\b/i.test(body)) required.add("Agent");
  for (const match of body.matchAll(/`(kb_[a-z_]+)`/g)) required.add(match[1]!);
  const missing = [...required].filter((tool) => !tools.includes(tool));
  if (missing.length > 0) {
    throw new Error(
      `agent ${name}: instructions require ${missing.join(", ")}, which its tools do not grant`,
    );
  }
}

// The single source of truth for "this agent will be told to run ranked search".
// `searchSection` branches on the same predicate, so the tool list and the
// instructions cannot drift apart.
function usesRankedSearch(
  agent: EmitAgent,
  corpusTokens: Record<string, number> | undefined,
): boolean {
  const total = (agent.def.kb_namespaces ?? []).reduce(
    (sum, ns) => sum + ((corpusTokens ?? {})[ns] ?? 0),
    0,
  );
  return total > READ_ALL_TOKEN_LIMIT;
}

function searchSection(
  agent: EmitAgent,
  corpusTokens: Record<string, number> | undefined,
  searchCommand: string,
): string {
  const common = [
    "## Search procedure",
    "",
    "The knowledge base is the Markdown under the KB root in `team-ai/index.lock`.",
    "",
  ];
  const namespaces = agent.def.kb_namespaces;

  if (corpusTokens === undefined) {
    throw new Error("builtin-search emit requires corpus sizes; none were computed");
  }

  const total = namespaces.reduce((sum, namespace) => sum + (corpusTokens[namespace] ?? 0), 0);
  const listing = namespaces
    .map(
      (namespace) => `- search the KB root for \`^namespace: ${namespace}\` to list your documents`,
    )
    .join("\n");

  if (total <= READ_ALL_TOKEN_LIMIT) {
    return [
      ...common,
      "Use Read, Grep, and Glob.",
      "",
      listing,
      "",
      "Your whole corpus is small enough to read in full. Read every one of those documents before answering — do not guess which is relevant, and do not answer from a grep match alone.",
      "",
      "Answer only from those documents, citing paths. If they do not answer the question, say so and name the owner.",
    ].join("\n");
  }

  const namespaceFlags = namespaces.map((namespace) => `--namespace ${namespace}`).join(" ");
  return [
    ...common,
    "Your corpus is far too large to read in full. Use ranked search:",
    "",
    "```bash",
    `${searchCommand} search "<the question, in full>" --root team-ai ${namespaceFlags} --k 8`,
    "```",
    "",
    "Read the files behind the top hits, then answer only from them, citing paths.",
    "Grep is a fallback for an exact string you already know, not a way to find relevant material — it misses any wording the document does not use.",
    "",
    "If nothing scores above the threshold, say you do not know and name the owner.",
  ].join("\n");
}

function frontMatter(input: EmitInput["agents"][number], opts: EmitClaudeCodeOptions): string {
  const builtin = opts.builtinSearch === true;
  const tools = !builtin
    ? input.def.tools
    : usesRankedSearch(input, opts.corpusTokens)
      ? RANKED_SEARCH_TOOLS
      : BUILTIN_SEARCH_TOOLS;
  const meta = {
    name: input.def.name,
    description: input.def.description,
    tools: tools.join(", "),
    // The host otherwise loads its project instruction files into every agent.
    // For an agent that must answer from the knowledge base, those files are an
    // answer source that bypasses retrieval — and a per-dispatch token cost.
    ...(builtin ? { omitClaudeMd: true } : {}),
    kind: input.def.kind,
    model_tier: input.def.model_tier,
    model: MODEL_FOR_TIER[input.def.model_tier],
    kb_namespaces: input.def.kb_namespaces,
    max_hops: input.def.max_hops,
  };
  const body = builtin
    ? [
        searchSection(input, opts.corpusTokens, opts.searchCommand ?? DEFAULT_SEARCH_COMMAND),
        ANSWER_RULES,
        domainRules(input.instructions),
      ]
        .filter((section) => section.length > 0)
        .join("\n\n")
    : input.instructions.trim();
  if (builtin) assertToolsCoverInstructions(input.def.name, tools, body);
  return `---\n${stringifyYaml(meta)}---\n\n${body}${body.length > 0 ? "\n" : ""}`;
}

export function emitClaudeCode(
  input: EmitInput,
  outDir: string,
  opts: EmitClaudeCodeOptions = {},
): string[] {
  validateFilePrefix(opts.filePrefix);
  const written: string[] = [];
  const agents =
    opts.builtinSearch === true ? input.agents.filter((agent) => !delegates(agent)) : input.agents;

  for (const agent of agents) {
    written.push(
      write(
        outDir,
        `.claude/agents/${opts.filePrefix ?? ""}${agent.name}.md`,
        frontMatter(agent, opts),
      ),
    );
  }

  if (opts.pluginManifest !== false) {
    const plugin = {
      name: "team-ai-emitted",
      description: "Agents and skills emitted from a team-ai instance.",
      version: packageVersion(),
      agents: agents.map((a) => `./.claude/agents/${opts.filePrefix ?? ""}${a.name}.md`),
      skills: input.skills.map((s) => s.name),
    };
    written.push(
      write(outDir, ".claude-plugin/plugin.json", `${JSON.stringify(plugin, null, 2)}\n`),
    );
  }

  return written;
}
