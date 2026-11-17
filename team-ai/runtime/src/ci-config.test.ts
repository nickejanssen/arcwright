import { readdirSync, readFileSync } from "node:fs";
import { parse } from "yaml";
import { describe, expect, it } from "vitest";

describe("ci.yml", () => {
  const doc = parse(readFileSync(".github/workflows/ci.yml", "utf8")) as {
    jobs: Record<string, unknown>;
    permissions?: Record<string, string>;
  };
  it("has the three required jobs", () => {
    expect(Object.keys(doc.jobs).sort()).toEqual(
      ["lint-typecheck-test", "secret-scan", "validate"].sort(),
    );
  });
  it("is read-only by default", () => {
    expect(doc.permissions?.contents).toBe("read");
  });
});

interface ReusableWorkflow {
  on?: { workflow_call?: { inputs?: Record<string, { default?: unknown; type?: string }> } };
  permissions?: Record<string, string>;
  jobs?: Record<string, unknown>;
}

const REUSABLE = ["validate-kb", "validate-spoke", "evals"] as const;
const DOCUMENTED_INPUTS: Record<string, string> = {
  "node-version": "22",
  root: ".",
  "team-ai-ref": "v0",
};

describe.each(REUSABLE)("%s.reusable.yml", (name) => {
  const doc = parse(
    readFileSync(`.github/workflows/${name}.reusable.yml`, "utf8"),
  ) as ReusableWorkflow;

  it("is triggered by workflow_call", () => {
    expect(doc.on?.workflow_call).toBeDefined();
  });

  it("declares the three documented inputs with their defaults", () => {
    const inputs = doc.on?.workflow_call?.inputs ?? {};
    expect(Object.keys(inputs).sort()).toEqual(Object.keys(DOCUMENTED_INPUTS).sort());
    for (const [key, expected] of Object.entries(DOCUMENTED_INPUTS)) {
      expect(inputs[key]?.default, `${name} input ${key} default`).toBe(expected);
      expect(inputs[key]?.type, `${name} input ${key} type`).toBe("string");
    }
  });

  it("is read-only", () => {
    expect(doc.permissions?.contents).toBe("read");
  });

  it("defines at least one job", () => {
    expect(Object.keys(doc.jobs ?? {}).length).toBeGreaterThan(0);
  });
});

describe("evals.reusable.yml", () => {
  const raw = readFileSync(".github/workflows/evals.reusable.yml", "utf8");
  it("uploads the eval report as an artifact even on failure", () => {
    expect(raw).toContain("actions/upload-artifact@v4");
    expect(raw).toContain("if: always()");
    expect(raw).toContain("run-evals");
    expect(raw).toContain("--json");
  });
});

describe("no workflow runs the unrelated npm package", () => {
  const files = [
    ...readdirSync(".github/workflows").map((f) => `.github/workflows/${f}`),
    ...readdirSync("templates", { recursive: true })
      .map(String)
      .filter((f) => f.endsWith(".hbs"))
      .map((f) => `templates/${f}`),
  ];
  it.each(files)("%s does not call npx team-ai", (file) => {
    expect(readFileSync(file, "utf8")).not.toMatch(/npx\s+(--yes\s+)?team-ai/);
  });
});
