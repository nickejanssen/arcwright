import { afterEach, describe, expect, it, vi } from "vitest";

import { run } from "./validate-kb.js";

const log = vi.spyOn(console, "log").mockImplementation(() => undefined);
const error = vi.spyOn(console, "error").mockImplementation(() => undefined);

afterEach(() => {
  log.mockClear();
  error.mockClear();
});

describe("validate-kb", () => {
  it("passes a valid corpus with --schema-only", async () => {
    const code = await run({ root: "src/kb/fixtures/kb", schemaOnly: true });
    expect(code).toBe(0);
    expect(log).toHaveBeenCalledWith("OK 3 document(s)");
  });

  it("passes a valid corpus with relation checks", async () => {
    const code = await run({ root: "src/kb/fixtures/kb" });
    expect(code).toBe(0);
    expect(log).toHaveBeenCalledWith("OK 3 document(s), relations valid");
  });

  it("fails and prints one line per invalid document", async () => {
    const code = await run({ root: "src/kb/fixtures/kb-broken", schemaOnly: true });
    expect(code).toBe(1);
    expect(error).toHaveBeenCalledTimes(2);
    const printed = error.mock.calls.map((c) => String(c[0])).join("\n");
    expect(printed).toContain("operating/missing-owner.md");
    expect(printed).toContain("platform/bad-status.md");
  });

  it("fails on a broken relation target", async () => {
    const code = await run({ root: "src/commands/fixtures/kb-bad-relations" });
    expect(code).toBe(1);
    expect(error).toHaveBeenCalledWith(
      "kb.platform.a: relation 'depends_on' value 'kb.platform.missing' — unknown doc id",
    );
  });

  it("does not run relation checks under --schema-only", async () => {
    const code = await run({ root: "src/commands/fixtures/kb-bad-relations", schemaOnly: true });
    expect(code).toBe(0);
    expect(log).toHaveBeenCalledWith("OK 1 document(s)");
  });

  it("fails with a friendly message when the root does not exist", async () => {
    const code = await run({ root: "src/kb/fixtures/does-not-exist", schemaOnly: true });
    expect(code).toBe(1);
    expect(String(error.mock.calls[0]?.[0])).toContain("KB root not found");
  });

  it("defaults --root to kb and --schema-only to false", async () => {
    const code = await run({});
    // No kb/ directory at the repo root in the test working dir.
    expect(code).toBe(1);
    expect(String(error.mock.calls[0]?.[0])).toContain("KB root not found");
  });
});
