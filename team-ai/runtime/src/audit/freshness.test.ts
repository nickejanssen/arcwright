import { describe, expect, it, vi } from "vitest";

import { auditFreshness, renderIssueDrafts } from "./freshness.js";
import { run } from "../commands/freshness-audit.js";
import type { FrontMatter } from "../schema/types.js";
import type { KbDoc } from "../kb/types.js";

function mkDoc(opts: {
  id: string;
  path?: string;
  owner?: string;
  status?: FrontMatter["status"];
  review_by?: string;
  body?: string;
  isBacklog?: boolean;
  relations?: FrontMatter["relations"];
}): KbDoc {
  const front: FrontMatter = {
    id: opts.id,
    namespace: "x",
    title: opts.id,
    owner: opts.owner ?? "editor",
    status: opts.status ?? "active",
    review_by: opts.review_by ?? "2099-01-01",
    sensitivity: "internal",
    source: "authored",
    tags: [],
    supersedes: [],
    ...(opts.relations ? { relations: opts.relations } : {}),
  };
  return {
    id: opts.id,
    path: opts.path ?? `x/${opts.id}.md`,
    frontmatter: front,
    body: opts.body ?? "",
    headings: [],
    isBacklog: opts.isBacklog ?? false,
  };
}

const TODAY = new Date("2026-06-01T00:00:00Z");

describe("auditFreshness — stale", () => {
  it("flags a doc whose review_by is in the past and not a future one", () => {
    const docs = [
      mkDoc({ id: "past", review_by: "2025-01-01" }),
      mkDoc({ id: "future", review_by: "2099-01-01" }),
    ];
    const report = auditFreshness(docs, { today: TODAY });
    const staleIds = report.stale.map((i) => i.id);
    expect(staleIds).toContain("past");
    expect(staleIds).not.toContain("future");
    expect(report.stale.find((i) => i.id === "past")?.reason).toBe("review_by 2025-01-01 passed");
  });

  it("excludes deprecated and backlog docs from stale", () => {
    const docs = [
      mkDoc({ id: "dep", review_by: "2000-01-01", status: "deprecated" }),
      mkDoc({ id: "backlog", review_by: "2000-01-01", isBacklog: true }),
    ];
    const report = auditFreshness(docs, { today: TODAY });
    expect(report.stale).toHaveLength(0);
  });
});

describe("auditFreshness — orphaned", () => {
  it("flags an unreferenced non-index doc but not one cited by another body", () => {
    const docs = [
      mkDoc({ id: "orphan", path: "x/orphan.md" }),
      mkDoc({ id: "cited", path: "x/cited.md" }),
      mkDoc({ id: "citer", path: "x/citer.md", body: "See [it](x/cited.md) for details." }),
    ];
    const report = auditFreshness(docs, { today: TODAY });
    const ids = report.orphaned.map((i) => i.id);
    expect(ids).toContain("orphan");
    expect(ids).not.toContain("cited");
    expect(report.orphaned.find((i) => i.id === "orphan")?.reason).toBe(
      "not referenced by any document",
    );
  });

  it("does not flag index-named docs even when unreferenced", () => {
    const docs = [mkDoc({ id: "ov", path: "x/overview.md" })];
    const report = auditFreshness(docs, { today: TODAY });
    expect(report.orphaned).toHaveLength(0);
  });

  it("does not flag a doc referenced via another doc's relations.depends_on", () => {
    const docs = [
      mkDoc({ id: "kb.target", path: "x/target.md" }),
      mkDoc({
        id: "kb.dependent",
        path: "x/dependent.md",
        relations: { depends_on: ["kb.target"] },
      }),
    ];
    const report = auditFreshness(docs, { today: TODAY });
    expect(report.orphaned.map((i) => i.id)).not.toContain("kb.target");
  });

  it("resolves citations loosely across a leading kb/ prefix", () => {
    const docs = [
      mkDoc({ id: "cited", path: "x/cited.md" }),
      mkDoc({ id: "citer", path: "x/citer.md", body: "[x](kb/x/cited.md)" }),
    ];
    const report = auditFreshness(docs, { today: TODAY });
    expect(report.orphaned.map((i) => i.id)).not.toContain("cited");
  });

  it("excludes backlog docs from orphaned", () => {
    const docs = [mkDoc({ id: "bl", path: "x/bl.md", isBacklog: true })];
    const report = auditFreshness(docs, { today: TODAY });
    expect(report.orphaned).toHaveLength(0);
  });
});

describe("auditFreshness — unowned", () => {
  it("flags an empty owner", () => {
    const docs = [mkDoc({ id: "no-owner", owner: "   " })];
    const report = auditFreshness(docs, { today: TODAY });
    expect(report.unowned).toHaveLength(1);
    expect(report.unowned[0]?.reason).toBe("owner is empty");
  });

  it("flags an owner not in knownRoles when the set is provided", () => {
    const docs = [mkDoc({ id: "ghost", owner: "ghost-role" })];
    const report = auditFreshness(docs, { today: TODAY, knownRoles: new Set(["editor"]) });
    expect(report.unowned).toHaveLength(1);
    expect(report.unowned[0]?.reason).toBe("owner 'ghost-role' is not a known role");
  });

  it("does not flag a non-empty unknown owner when knownRoles is absent", () => {
    const docs = [mkDoc({ id: "ghost", owner: "ghost-role" })];
    const report = auditFreshness(docs, { today: TODAY });
    expect(report.unowned).toHaveLength(0);
  });

  it("skips backlog docs even with an empty owner", () => {
    const docs = [mkDoc({ id: "bl", owner: "", isBacklog: true })];
    const report = auditFreshness(docs, { today: TODAY });
    expect(report.unowned).toHaveLength(0);
  });
});

describe("auditFreshness — summary", () => {
  it("counts each bucket and records asOf as YYYY-MM-DD", () => {
    const docs = [
      mkDoc({ id: "s", path: "x/s.md", review_by: "2025-01-01" }),
      mkDoc({ id: "o", path: "x/o.md" }),
      mkDoc({ id: "u", path: "x/u.md", owner: "" }),
    ];
    const report = auditFreshness(docs, { today: TODAY });
    expect(report.summary).toEqual({
      total: 3,
      stale: report.stale.length,
      orphaned: report.orphaned.length,
      unowned: report.unowned.length,
      asOf: "2026-06-01",
    });
    expect(report.summary.stale).toBe(1);
    expect(report.summary.unowned).toBe(1);
  });
});

describe("renderIssueDrafts", () => {
  it("produces one draft per stale item with the expected title and labels", () => {
    const docs = [
      mkDoc({ id: "a", path: "x/a.md", review_by: "2025-01-01", owner: "editor" }),
      mkDoc({ id: "b", path: "x/b.md", review_by: "2024-02-03", owner: "steward" }),
    ];
    const report = auditFreshness(docs, { today: TODAY });
    const drafts = renderIssueDrafts(report);
    expect(drafts).toHaveLength(2);
    expect(drafts[0]?.title).toBe("Refresh KB doc: x/a.md");
    expect(drafts[0]?.labels).toEqual(["kb-freshness"]);
    expect(drafts[0]?.body).toContain("editor");
    expect(drafts[0]?.body).toContain("2025-01-01");
    expect(drafts[0]?.body).toContain("assigned to owner");
  });
});

describe("freshness-audit CLI", () => {
  const log = vi.spyOn(console, "log").mockImplementation(() => undefined);
  const error = vi.spyOn(console, "error").mockImplementation(() => undefined);

  function reset(): void {
    log.mockClear();
    error.mockClear();
  }

  it("prints the report as JSON and exits 0 by default", async () => {
    reset();
    const code = await run({ root: "src/kb/fixtures/kb", today: "2099-01-01" });
    expect(code).toBe(0);
    const report = JSON.parse(String(log.mock.calls[0]?.[0])) as {
      stale: unknown[];
      summary: { total: number; asOf: string };
    };
    expect(report.summary.total).toBe(3);
    expect(report.summary.asOf).toBe("2099-01-01");
    expect(report.stale).toHaveLength(3);
  });

  it("exits 1 with --fail-on-stale when stale docs exist", async () => {
    reset();
    const code = await run({ root: "src/kb/fixtures/kb", today: "2099-01-01", failOnStale: true });
    expect(code).toBe(1);
  });

  it("exits 0 with --fail-on-stale when nothing is stale", async () => {
    reset();
    const code = await run({ root: "src/kb/fixtures/kb", today: "2020-01-01", failOnStale: true });
    expect(code).toBe(0);
  });

  it("dry-runs --open-issues without a token and never touches the network", async () => {
    reset();
    const hadToken = "GITHUB_TOKEN" in process.env;
    const prev = process.env.GITHUB_TOKEN;
    delete process.env.GITHUB_TOKEN;
    try {
      const code = await run({ root: "src/kb/fixtures/kb", today: "2099-01-01", openIssues: true });
      expect(code).toBe(0);
      const stderr = error.mock.calls.map((c) => String(c[0])).join("\n");
      expect(stderr).toContain("would open 3 issue(s)");
      expect(stderr).toContain("dry run");
    } finally {
      if (hadToken && prev !== undefined) process.env.GITHUB_TOKEN = prev;
    }
  });

  it("reports live mode as not implemented when token and repo are set", async () => {
    reset();
    const hadToken = "GITHUB_TOKEN" in process.env;
    const prev = process.env.GITHUB_TOKEN;
    process.env.GITHUB_TOKEN = "x";
    try {
      const code = await run({
        root: "src/kb/fixtures/kb",
        today: "2099-01-01",
        openIssues: true,
        repo: "acme/kb",
      });
      expect(code).toBe(0);
      const stderr = error.mock.calls.map((c) => String(c[0])).join("\n");
      expect(stderr).toContain("live mode is not implemented");
    } finally {
      if (hadToken && prev !== undefined) process.env.GITHUB_TOKEN = prev;
      else delete process.env.GITHUB_TOKEN;
    }
  });

  it("rejects a malformed --today", async () => {
    reset();
    const code = await run({ root: "src/kb/fixtures/kb", today: "nope" });
    expect(code).toBe(1);
  });

  it("returns 1 when KB front matter is invalid", async () => {
    reset();
    const code = await run({ root: "src/kb/fixtures/kb-broken", today: "2020-01-01" });
    expect(code).toBe(1);
  });
});
