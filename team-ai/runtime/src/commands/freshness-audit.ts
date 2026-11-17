// Deterministic (reads the real clock only when --today is absent). No model calls.
//
// Reports stale, orphaned, and unowned KB docs as JSON. With --fail-on-stale it
// also sets a non-zero exit when stale docs exist (for CI). --open-issues would
// file GitHub issues for the stale docs, but the live path is intentionally NOT
// implemented in this task: there is no fetch, no @octokit, no network call
// anywhere here. Filing issues is an ops burden we do not want enabled by
// default, and a GitHub client belongs in its own task with its own review.

import { renderIssueDrafts, auditFreshness } from "../audit/freshness.js";
import { KbValidationError, loadKb } from "../kb/loader.js";
import type { KbDoc } from "../kb/types.js";
import { resolveKbScope } from "../retrieval/index-lock.js";

export interface FreshnessAuditOptions {
  root?: string;
  instance?: string;
  failOnStale?: boolean;
  openIssues?: boolean;
  repo?: string;
  today?: string;
}

const TODAY_FORMAT = /^\d{4}-\d{2}-\d{2}$/;

function parseToday(value: string | undefined): Date {
  if (value === undefined) return new Date();
  if (!TODAY_FORMAT.test(value)) {
    throw new Error(`--today must be YYYY-MM-DD, got '${value}'`);
  }
  const parsed = new Date(`${value}T00:00:00Z`);
  if (Number.isNaN(parsed.getTime())) {
    throw new Error(`--today is not a real date: '${value}'`);
  }
  return parsed;
}

export async function run(opts: FreshnessAuditOptions): Promise<number> {
  const scope =
    opts.instance === undefined
      ? { root: opts.root ?? "kb", exclude: [] }
      : resolveKbScope(opts.instance);

  let today: Date;
  try {
    today = parseToday(opts.today);
  } catch (err) {
    console.error(err instanceof Error ? err.message : String(err));
    return 1;
  }

  let docs: KbDoc[];
  try {
    docs = await loadKb(scope.root, { exclude: scope.exclude });
  } catch (err) {
    if (err instanceof KbValidationError) {
      console.error(
        `cannot audit freshness until KB front matter is valid ` +
          `(${err.failures.length} invalid document(s)); run 'team-ai validate-kb'`,
      );
      return 1;
    }
    console.error(err instanceof Error ? err.message : String(err));
    return 1;
  }

  // No knownRoles yet: role validation needs the role catalog. A future
  // `--roles <file>` flag can supply it; until then only empty owners are
  // flagged as unowned.
  const report = auditFreshness(docs, { today });

  console.log(JSON.stringify(report, null, 2));

  if (opts.openIssues ?? false) {
    const drafts = renderIssueDrafts(report);
    const live = Boolean(process.env.GITHUB_TOKEN) && Boolean(opts.repo);
    if (live) {
      console.error(
        `--open-issues live mode is not implemented yet; ${drafts.length} draft(s) available`,
      );
    } else {
      console.error(
        `would open ${drafts.length} issue(s) ` +
          `(dry run — set GITHUB_TOKEN and --repo to actually open them)`,
      );
    }
    return 0;
  }

  if (opts.failOnStale ?? false) {
    return report.stale.length > 0 ? 1 : 0;
  }

  return 0;
}
