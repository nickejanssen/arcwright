import {
  existsSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  rmSync,
  statSync,
  utimesSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { afterEach, describe, expect, it, vi } from "vitest";

import { writeIndexLock, DEFAULT_INDEX_LOCK } from "../retrieval/index-lock.js";
import { run } from "./remap-namespaces.js";

const log = vi.spyOn(console, "log").mockImplementation(() => undefined);
const error = vi.spyOn(console, "error").mockImplementation(() => undefined);
const dirs: string[] = [];

function setup(mappingBody = "namespaces:\n  platform: alpha\nfiles: {}\n"): {
  instance: string;
  kb: string;
  doc: string;
  mapping: string;
  top: string;
} {
  const top = mkdtempSync(join(tmpdir(), "team-ai-remap-command-"));
  dirs.push(top);
  const instance = join(top, "instance");
  const kb = join(top, "kb");
  mkdirSync(instance, { recursive: true });
  mkdirSync(kb, { recursive: true });
  writeIndexLock(instance, {
    ...DEFAULT_INDEX_LOCK,
    kb: { root: "../kb", exclude: [] },
  });
  const doc = join(kb, "a.md");
  writeFileSync(doc, "---\nid: platform.docs.a\nnamespace: platform\n---\nBody\n", "utf8");
  const mapping = join(top, "mapping.yaml");
  writeFileSync(mapping, mappingBody, "utf8");
  return { instance, kb, doc, mapping, top };
}

afterEach(() => {
  log.mockClear();
  error.mockClear();
  for (const dir of dirs.splice(0)) rmSync(dir, { recursive: true, force: true });
});

describe("remap-namespaces run", () => {
  it("rejects invalid mapping values before writing an output", async () => {
    const fixture = setup("namespaces:\n  platform: 42\nfiles: {}\n");
    const out = join(fixture.top, "proposal.yaml");
    const original = readFileSync(fixture.doc, "utf8");

    expect(await run({ instance: fixture.instance, mapping: fixture.mapping, out })).toBe(1);
    expect(existsSync(out)).toBe(false);
    expect(readFileSync(fixture.doc, "utf8")).toBe(original);
  });

  it("rejects an output path that aliases the mapping file", async () => {
    const fixture = setup();
    const original = readFileSync(fixture.mapping, "utf8");

    expect(
      await run({
        instance: fixture.instance,
        mapping: fixture.mapping,
        out: fixture.mapping,
      }),
    ).toBe(1);
    expect(readFileSync(fixture.mapping, "utf8")).toBe(original);
  });

  it("rejects an artifact path inside the KB", async () => {
    const fixture = setup();
    const original = readFileSync(fixture.doc, "utf8");

    expect(
      await run({
        instance: fixture.instance,
        mapping: fixture.mapping,
        out: fixture.doc,
      }),
    ).toBe(1);
    expect(readFileSync(fixture.doc, "utf8")).toBe(original);
  });

  it("rejects an output and inventory collision before creating either", async () => {
    const fixture = setup();
    const artifact = join(fixture.top, "artifact.txt");

    expect(
      await run({
        instance: fixture.instance,
        mapping: fixture.mapping,
        out: artifact,
        inventory: artifact,
      }),
    ).toBe(1);
    expect(existsSync(artifact)).toBe(false);
  });

  it("refuses to overwrite an existing artifact with different content", async () => {
    const fixture = setup();
    const out = join(fixture.top, "proposal.yaml");
    writeFileSync(out, "keep me\n", "utf8");

    expect(await run({ instance: fixture.instance, mapping: fixture.mapping, out })).toBe(1);
    expect(readFileSync(out, "utf8")).toBe("keep me\n");
  });

  it("leaves an existing identical proposal byte-identical", async () => {
    const fixture = setup();
    const out = join(fixture.top, "proposal.yaml");
    expect(await run({ instance: fixture.instance, mapping: fixture.mapping, out })).toBe(0);
    const old = new Date("2000-01-01T00:00:00.000Z");
    utimesSync(out, old, old);
    const before = statSync(out).mtimeMs;

    expect(await run({ instance: fixture.instance, mapping: fixture.mapping, out })).toBe(0);
    expect(statSync(out).mtimeMs).toBe(before);
  });
});
