import { mkdtempSync, readFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

import { parse as parseYaml } from "yaml";
import { describe, expect, it } from "vitest";

import { validate } from "../schema/validate.js";
import { renderTree } from "./render.js";

const SPOKE_DIR = fileURLToPath(new URL("../../templates/spoke", import.meta.url));
const ATTACH_DIR = fileURLToPath(new URL("../../templates/attach", import.meta.url));

function tempDir(): string {
  return mkdtempSync(join(tmpdir(), "team-ai-spoke-attach-"));
}

describe("templates/spoke", () => {
  const context = {
    name: "acme-partner-spoke",
    namespace: "partners/acme-partner",
    owner: "partner-lead",
    core_repo: "github.com/your-org/team-ai-core",
    domain: {
      id: "acme-partner-support",
      description: "Integration and support questions for the Acme partner.",
      subagent: "acme-partner-sme",
    },
  };

  it("renders a spoke.yaml that parses and satisfies the spoke schema", async () => {
    const dest = tempDir();
    const res = await renderTree({ templateDir: SPOKE_DIR, destDir: dest, context });
    expect(res.warnings).toEqual([]);
    expect(res.collisions).toEqual([]);

    const raw = readFileSync(join(dest, "spoke.yaml"), "utf8");
    const parsed = parseYaml(raw) as Record<string, unknown>;
    const check = validate("spoke", parsed);
    expect(check.ok).toBe(true);

    expect(parsed.name).toBe("acme-partner-spoke");
    expect(parsed.kb_namespace).toBe("partners/acme-partner");
    expect((parsed.domains as { subagent: string }[])[0]?.subagent).toBe("acme-partner-sme");
    expect(parsed.exports).toEqual({ skills: [], agents: ["acme-partner-sme"] });
  });

  it("does not emit the underscore-prefixed spoke SME partials, but keeps kb/ and skills/", async () => {
    const dest = tempDir();
    await renderTree({ templateDir: SPOKE_DIR, destDir: dest, context });
    const { existsSync } = await import("node:fs");
    expect(existsSync(join(dest, "agents/_spoke-sme.yaml"))).toBe(false);
    expect(existsSync(join(dest, "kb"))).toBe(true);
    expect(existsSync(join(dest, "skills"))).toBe(true);
  });

  it("renders a validate workflow that calls the reusable spoke workflow", async () => {
    const dest = tempDir();
    await renderTree({ templateDir: SPOKE_DIR, destDir: dest, context });
    const raw = readFileSync(join(dest, ".github/workflows/validate.yml"), "utf8");
    const parsed = parseYaml(raw) as { jobs: Record<string, { uses?: string }> };
    expect(parsed.jobs["validate-spoke"]?.uses).toBe(
      "nickejanssen/team-ai/.github/workflows/validate-spoke.reusable.yml@v0",
    );
  });
});

describe("templates/attach", () => {
  it("renders a .team-ai.yaml with exactly the five attach keys", async () => {
    const dest = tempDir();
    const res = await renderTree({
      templateDir: ATTACH_DIR,
      destDir: dest,
      context: {
        instance: "github.com/your-org/team-ai-core",
        agents: ["billing-sme", "onboarding-sme"],
        skills: ["kb-answer"],
        kb_namespaces: ["operating", "platform"],
      },
    });
    expect(res.warnings).toEqual([]);

    const raw = readFileSync(join(dest, ".team-ai.yaml"), "utf8");
    const parsed = parseYaml(raw) as Record<string, unknown>;
    expect(Object.keys(parsed).sort()).toEqual(
      ["agents", "instance", "kb_namespaces", "mode", "skills"].sort(),
    );
    expect(parsed.mode).toBe("attach");
    expect(parsed.agents).toEqual(["billing-sme", "onboarding-sme"]);
    expect(parsed.kb_namespaces).toEqual(["operating", "platform"]);
  });
});
