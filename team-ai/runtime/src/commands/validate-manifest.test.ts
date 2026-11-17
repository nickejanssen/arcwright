import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { stringify as stringifyYaml } from "yaml";
import { afterEach, describe, expect, it, vi } from "vitest";

import { run } from "./validate-manifest.js";

const log = vi.spyOn(console, "log").mockImplementation(() => undefined);
const error = vi.spyOn(console, "error").mockImplementation(() => undefined);
const dirs: string[] = [];

function instance(manifest: unknown, agents: Record<string, unknown> = {}): string {
  const root = mkdtempSync(join(tmpdir(), "team-ai-validate-manifest-"));
  dirs.push(root);
  writeFileSync(join(root, "manifest.yaml"), stringifyYaml(manifest));
  if (Object.keys(agents).length > 0) {
    mkdirSync(join(root, "agents"));
    for (const [file, definition] of Object.entries(agents)) {
      writeFileSync(join(root, "agents", file), stringifyYaml(definition));
    }
  }
  return root;
}

afterEach(() => {
  log.mockClear();
  error.mockClear();
  for (const dir of dirs.splice(0)) rmSync(dir, { recursive: true, force: true });
});

describe("validate-manifest", () => {
  it("passes a manifest without agents and prints the compatibility note", async () => {
    const root = instance({ domains: [] });

    expect(await run({ root })).toBe(0);
    expect(log).toHaveBeenCalledWith(
      "validate-manifest: OK (no agents section; topology invariants not checked)",
    );
  });

  it("rejects a definition whose internal name does not match its filename", async () => {
    const root = instance(
      {
        domains: [],
        agents: [
          {
            name: "safety-sme",
            tier: 1,
            kind: "router",
            max_hops: 0,
            kb_namespaces: ["safety"],
          },
        ],
      },
      {
        "wrong-name.yaml": {
          name: "safety-sme",
          kind: "router",
          description: "safety",
          model_tier: "none",
          kb_namespaces: ["safety"],
          tools: [],
          max_hops: 0,
          instructions_file: "agents/safety-sme.md",
        },
      },
    );

    expect(await run({ root })).toBe(1);
    const printed = error.mock.calls.map((c) => String(c[0])).join("\n");
    expect(printed).toContain("[definition-name-mismatch]");
    expect(printed).toContain("safety-sme: [definition-missing]");
  });
});
