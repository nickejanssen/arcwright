import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

import { parse as parseYaml } from "yaml";
import { describe, expect, it } from "vitest";

import { validate } from "../schema/validate.js";
import { renderTemplate } from "./render.js";

function tmpl(rel: string): string {
  return readFileSync(
    fileURLToPath(new URL(`../../templates/instance/${rel}`, import.meta.url)),
    "utf8",
  );
}

function renderAgent(rel: string, context: Record<string, unknown>): Record<string, unknown> {
  const { output, warnings } = renderTemplate(tmpl(rel), context, rel);
  expect(warnings).toEqual([]);
  const parsed = parseYaml(output) as Record<string, unknown>;
  return parsed;
}

describe("agent templates", () => {
  it("_domain-sme.yaml renders a valid subagent with max_hops 0", () => {
    const parsed = renderAgent("agents/_domain-sme.yaml.hbs", {
      slug: "billing-api",
      namespace: "platform",
      escalate_to: "unassigned",
    });
    const result = validate("agent", parsed);
    expect(result.ok).toBe(true);
    expect(parsed.name).toBe("billing-api-sme");
    expect(parsed.kind).toBe("subagent");
    expect(parsed.kb_namespaces).toEqual(["platform"]);
    expect(parsed.max_hops).toBe(0);
  });

  it("sme.yaml renders a valid router with max_hops >= 1", () => {
    const parsed = renderAgent("agents/sme.yaml.hbs", { team: { name: "Platform" } });
    const result = validate("agent", parsed);
    expect(result.ok).toBe(true);
    expect(parsed.kind).toBe("router");
    expect(typeof parsed.max_hops).toBe("number");
    expect(parsed.max_hops as number).toBeGreaterThanOrEqual(1);
    expect(parsed.model_tier).toBe("none");
  });

  it("_role.yaml renders a valid role subagent with max_hops 0", () => {
    const parsed = renderAgent("agents/roles/_role.yaml.hbs", {
      name: "architect",
      summary: "Owns technical design and integration decisions",
      model_tier: "large",
      default_namespaces: ["operating", "platform", "patterns", "decisions"],
    });
    const result = validate("agent", parsed);
    expect(result.ok).toBe(true);
    expect(parsed.name).toBe("architect");
    expect(parsed.kind).toBe("subagent");
    expect(parsed.model_tier).toBe("large");
    expect(parsed.kb_namespaces).toEqual(["operating", "platform", "patterns", "decisions"]);
    expect(parsed.max_hops).toBe(0);
  });

  it("SKILL.md templates carry name and tier front matter", () => {
    for (const [skill, tier] of [
      ["kb-answer", "small"],
      ["kb-contribute", "small"],
      ["audit-summary", "small"],
      ["sme-route", "none"],
    ] as const) {
      const { output } = renderTemplate(tmpl(`skills/${skill}/SKILL.md.hbs`), {}, skill);
      expect(output).toContain(`name: ${skill}`);
      expect(output).toContain(`tier: ${tier}`);
    }
  });

  it("persona templates are tone-only and grant nothing", () => {
    for (const persona of ["internal-technical", "partner-facing", "executive-brief"]) {
      const { output } = renderTemplate(tmpl(`personas/${persona}.md.hbs`), {}, persona);
      expect(output).toContain(`name: ${persona}`);
      expect(output).toContain("kind: persona");
      expect(output).toContain("grants: none");
    }
  });
});

it("names only tools the MCP server template implements", () => {
  const server = readFileSync("templates/mcp-server/server.mjs.hbs", "utf8");
  const implemented = new Set([...server.matchAll(/^\s{2}(kb_[a-z_]+):\s*\{/gm)].map((m) => m[1]));
  for (const file of [
    "templates/instance/agents/sme.yaml.hbs",
    "templates/instance/agents/_domain-sme.yaml.hbs",
  ]) {
    const tools = /^tools:\s*\[([^\]]*)\]/m.exec(readFileSync(file, "utf8"))?.[1] ?? "";
    for (const tool of tools
      .split(",")
      .map((t) => t.trim())
      .filter(Boolean)) {
      expect(implemented.has(tool), `${file}: ${tool}`).toBe(true);
    }
  }
});
