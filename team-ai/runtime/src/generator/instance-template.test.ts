import { mkdtempSync, readFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { fileURLToPath } from "node:url";
import { join } from "node:path";

import { parse as parseYaml } from "yaml";
import { afterEach, describe, expect, it, vi } from "vitest";

import { loadBank } from "../interview/bank.js";
import { Engine } from "../interview/engine.js";
import type { Question } from "../interview/types.js";
import * as validateKb from "../commands/validate-kb.js";
import { readIndexLock } from "../retrieval/index-lock.js";
import { buildContext } from "./context.js";
import { renderTree } from "./render.js";

const TEMPLATE_DIR = fileURLToPath(new URL("../../templates/instance", import.meta.url));
const bank = loadBank();

const log = vi.spyOn(console, "log").mockImplementation(() => undefined);
const error = vi.spyOn(console, "error").mockImplementation(() => undefined);
afterEach(() => {
  log.mockClear();
  error.mockClear();
});

function pick(q: Question): unknown {
  if (q.type === "multi_select") {
    if (Array.isArray(q.default)) return q.default;
    const first = q.options[0];
    return first ? [first.value] : [];
  }
  return q.default ?? q.options[0]?.value ?? "x";
}

function fullRun(overrides: Record<string, unknown>): Engine {
  const engine = new Engine(bank);
  for (let guard = 0; guard < 500; guard += 1) {
    const step = engine.next();
    if (step === null) break;
    if (step.kind === "gate") {
      engine.confirmGate(step.gate);
      continue;
    }
    engine.answer(step.question.id, overrides[step.question.id] ?? pick(step.question));
  }
  return engine;
}

async function renderFixture(): Promise<string> {
  const engine = fullRun({
    "team.name": "platform",
    "team.mission": "Run the shared platform",
    "agents.domains": "billing, onboarding",
  });
  const ctx = buildContext(engine, { today: new Date("2026-01-01T00:00:00Z") });
  const dest = mkdtempSync(join(tmpdir(), "team-ai-instance-"));
  const res = await renderTree({ templateDir: TEMPLATE_DIR, destDir: dest, context: ctx });
  expect(res.warnings).toEqual([]);
  expect(res.collisions).toEqual([]);
  return dest;
}

describe("templates/instance", () => {
  it("renders seed docs with front matter that passes validate-kb --schema-only", async () => {
    const dest = await renderFixture();
    const code = await validateKb.run({ root: join(dest, "kb"), schemaOnly: true });
    expect(code).toBe(0);
    expect(log).toHaveBeenCalledWith("OK 5 document(s)");
  });

  it("renders a validate workflow that parses as YAML and calls the reusable workflow", async () => {
    const dest = await renderFixture();
    const raw = readFileSync(join(dest, ".github/workflows/validate.yml"), "utf8");
    const parsed = parseYaml(raw) as { jobs: Record<string, { uses?: string }> };
    expect(parsed.jobs["validate-kb"]?.uses).toBe(
      "nickejanssen/team-ai/.github/workflows/validate-kb.reusable.yml@v0",
    );
    expect(raw).toContain("validate-kb.reusable.yml@v0");
  });

  it("renders an index.lock that readIndexLock accepts", async () => {
    const dest = await renderFixture();
    const lock = readIndexLock(dest);
    expect(lock.driver).toBe("lexical");
    expect(lock.chunk.split_on).toEqual(["h2", "h3"]);
    expect(lock.chunk.target_tokens).toBe(800);
    expect(lock.chunk.hard_cap).toBe(1200);
    expect(lock.embedding).toBeNull();
  });

  it("does not emit the underscore-prefixed template partials", async () => {
    const dest = await renderFixture();
    const { existsSync } = await import("node:fs");
    expect(existsSync(join(dest, "agents/_domain-sme.yaml"))).toBe(false);
    expect(existsSync(join(dest, "agents/roles/_role.yaml"))).toBe(false);
    expect(existsSync(join(dest, "agents/sme.yaml"))).toBe(true);
  });

  it("renders the manifest fragment with one entry per domain", async () => {
    const dest = await renderFixture();
    const fragment = parseYaml(
      readFileSync(join(dest, "agents/manifest.fragment.yaml"), "utf8"),
    ) as { domains: { id: string; subagent: string; kb_namespace: string }[] };
    expect(fragment.domains.map((d) => d.id)).toEqual(["billing", "onboarding"]);
    expect(fragment.domains[0]?.subagent).toBe("billing-sme");
  });

  it("renders each domain namespace and falls back for unmatched domains", async () => {
    const engine = fullRun({
      "team.name": "platform",
      "team.mission": "Run the shared platform",
      "agents.domains": "platform, billing",
    });
    const ctx = buildContext(engine, { today: new Date("2026-01-01T00:00:00Z") });
    const dest = mkdtempSync(join(tmpdir(), "team-ai-instance-"));
    const res = await renderTree({ templateDir: TEMPLATE_DIR, destDir: dest, context: ctx });
    expect(res.warnings).toEqual([]);
    expect(res.collisions).toEqual([]);

    const fragment = parseYaml(
      readFileSync(join(dest, "agents/manifest.fragment.yaml"), "utf8"),
    ) as { domains: { id: string; kb_namespace: string }[] };
    expect(fragment.domains.map(({ id, kb_namespace }) => ({ id, kb_namespace }))).toEqual([
      { id: "platform", kb_namespace: "platform" },
      { id: "billing", kb_namespace: "operating" },
    ]);
  });
});
