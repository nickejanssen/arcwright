import { mkdtempSync, readFileSync, readdirSync } from "node:fs";
import { tmpdir } from "node:os";
import { fileURLToPath } from "node:url";
import { join } from "node:path";

import { describe, expect, it } from "vitest";

import { loadBank } from "../interview/bank.js";
import { Engine } from "../interview/engine.js";
import type { Question } from "../interview/types.js";
import { buildContext } from "./context.js";
import { renderTree } from "./render.js";

const TMPL = fileURLToPath(new URL("./fixtures/tmpl", import.meta.url));
const bank = loadBank();

function tempDir(): string {
  return mkdtempSync(join(tmpdir(), "team-ai-render-"));
}

function pick(q: Question): unknown {
  if (q.type === "multi_select") {
    if (Array.isArray(q.default)) return q.default;
    const first = q.options[0];
    return first ? [first.value] : [];
  }
  return q.default ?? q.options[0]?.value ?? "x";
}

function fullRun(overrides: Record<string, unknown> = {}): Engine {
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

const ctxA = { team: { name: "Alpha", mission: "Ship things", slug: "alpha" }, driver: "lexical" };
const ctxB = { team: { name: "Beta", mission: "Ship more", slug: "beta" }, driver: "graph" };

describe("renderTree", () => {
  it("first render creates every file and records manifest entries", async () => {
    const dest = tempDir();
    const res = await renderTree({ templateDir: TMPL, destDir: dest, context: ctxA });

    expect(res.created).toEqual(["README.md", "nested/NOTES.txt", "nested/config.yaml"]);
    expect(res.unchanged).toEqual([]);
    expect(res.collisions).toEqual([]);
    expect(res.manifestEntries.map((e) => e.path)).toEqual([
      "README.md",
      "nested/NOTES.txt",
      "nested/config.yaml",
    ]);
    expect(readFileSync(join(dest, "README.md"), "utf8")).toContain("# Alpha");
    expect(readFileSync(join(dest, "nested/config.yaml"), "utf8")).toContain("driver: lexical");
    expect(readFileSync(join(dest, "nested/NOTES.txt"), "utf8")).toBe(
      "static file, no templating\n",
    );
    // .keep only asserts the directory
    expect(readdirSync(join(dest, "placeholder"))).toEqual([]);
  });

  it("second render with a matching prior manifest is all unchanged", async () => {
    const dest = tempDir();
    const first = await renderTree({ templateDir: TMPL, destDir: dest, context: ctxA });
    const second = await renderTree({
      templateDir: TMPL,
      destDir: dest,
      context: ctxA,
      priorManifest: first.manifestEntries,
    });
    expect(second.unchanged).toEqual(["README.md", "nested/NOTES.txt", "nested/config.yaml"]);
    expect(second.created).toEqual([]);
    expect(second.updated).toEqual([]);
    expect(second.collisions).toEqual([]);
  });

  it("re-renders a pristine prior output as updated", async () => {
    const dest = tempDir();
    const first = await renderTree({ templateDir: TMPL, destDir: dest, context: ctxA });
    const res = await renderTree({
      templateDir: TMPL,
      destDir: dest,
      context: ctxB,
      priorManifest: first.manifestEntries,
    });
    expect(res.updated).toEqual(["README.md", "nested/config.yaml"]);
    expect(res.unchanged).toEqual(["nested/NOTES.txt"]);
    expect(res.collisions).toEqual([]);
    expect(readFileSync(join(dest, "README.md"), "utf8")).toContain("# Beta");
  });

  it("never overwrites a hand-edited output; records a collision", async () => {
    const dest = tempDir();
    const first = await renderTree({ templateDir: TMPL, destDir: dest, context: ctxA });
    const { writeFileSync } = await import("node:fs");
    writeFileSync(join(dest, "README.md"), "hand edited, do not touch\n", "utf8");

    const res = await renderTree({
      templateDir: TMPL,
      destDir: dest,
      context: ctxB,
      priorManifest: first.manifestEntries,
    });
    expect(res.collisions).toEqual(["README.md"]);
    expect(res.updated).toEqual(["nested/config.yaml"]);
    expect(res.siblingsWritten).toEqual([]);
    expect(readFileSync(join(dest, "README.md"), "utf8")).toBe("hand edited, do not touch\n");
  });

  it("onCollision 'siblings' writes a .team-ai-new file and leaves the original", async () => {
    const dest = tempDir();
    const first = await renderTree({ templateDir: TMPL, destDir: dest, context: ctxA });
    const { writeFileSync } = await import("node:fs");
    writeFileSync(join(dest, "README.md"), "mine\n", "utf8");

    const res = await renderTree({
      templateDir: TMPL,
      destDir: dest,
      context: ctxB,
      priorManifest: first.manifestEntries,
      onCollision: "siblings",
    });
    expect(res.collisions).toEqual(["README.md"]);
    expect(res.siblingsWritten).toEqual(["README.md.team-ai-new"]);
    expect(readFileSync(join(dest, "README.md"), "utf8")).toBe("mine\n");
    expect(readFileSync(join(dest, "README.md.team-ai-new"), "utf8")).toContain("# Beta");
  });

  it("dryRun performs no writes but still classifies", async () => {
    const dest = tempDir();
    const res = await renderTree({
      templateDir: TMPL,
      destDir: dest,
      context: ctxA,
      dryRun: true,
    });
    expect(res.created).toEqual(["README.md", "nested/NOTES.txt", "nested/config.yaml"]);
    expect(readdirSync(dest)).toEqual([]);
  });

  it("render.ts source contains no file-removal calls", () => {
    const src = readFileSync(fileURLToPath(new URL("./render.ts", import.meta.url)), "utf8");
    expect(src).not.toMatch(/\b(unlink|rmdir|rmSync)\b/);
    expect(src).not.toMatch(/\brm\(/);
    expect(src).not.toMatch(/\.rm\b/);
  });

  it("emits a warning for a missing top-level context key", async () => {
    const dest = tempDir();
    const res = await renderTree({
      templateDir: TMPL,
      destDir: dest,
      context: { team: { name: "x" } },
    });
    expect(res.warnings.some((w) => w.includes("missing context key 'driver'"))).toBe(true);
  });
});

describe("buildContext", () => {
  it("maps a completed interview to the template context", () => {
    const engine = fullRun({
      "team.name": "Platform",
      "team.mission": "Run the platform",
      "agents.domains": "billing, onboarding",
      "arch.index_driver": "decide-later",
    });
    const ctx = buildContext(engine, { today: new Date("2026-01-01T00:00:00Z") });

    const team = ctx.team as { name: string; slug: string; mission: string };
    expect(team.name).toBe("Platform");
    expect(team.slug).toBe("platform");
    expect(ctx.driver).toBe("lexical");
    expect(Array.isArray(ctx.namespaces)).toBe(true);
    expect((ctx.namespaces as string[]).length).toBeGreaterThan(0);
    expect(ctx.reviewByDate).toBe("2026-06-30");
    expect((ctx.domains as { slug: string }[])[0]?.slug).toBe("billing");
  });
});
