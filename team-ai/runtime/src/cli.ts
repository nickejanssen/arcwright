import { pathToFileURL } from "node:url";

import { Command, Option } from "commander";

import * as adopt from "./commands/adopt.js";
import { loadAnswerFile } from "./generator/init-answers.js";
import * as assembleManifest from "./commands/assemble-manifest.js";
import * as checkAgnostic from "./commands/check-agnostic.js";
import * as doctor from "./commands/doctor.js";
import * as emit from "./commands/emit.js";
import * as freshnessAudit from "./commands/freshness-audit.js";
import * as attach from "./generator/attach.js";
import * as init from "./generator/init.js";
import * as resume from "./generator/resume.js";
import * as review from "./generator/review.js";
import * as spoke from "./generator/spoke.js";
import * as upgrade from "./generator/upgrade.js";
import * as reindex from "./commands/reindex.js";
import * as remapNamespaces from "./commands/remap-namespaces.js";
import * as runEvals from "./commands/run-evals.js";
import * as search from "./commands/search.js";
import * as validateCitations from "./commands/validate-citations.js";
import * as validateKb from "./commands/validate-kb.js";
import * as validateManifest from "./commands/validate-manifest.js";
import * as validateSpoke from "./commands/validate-spoke.js";
import { packageVersion } from "./version.js";

// Each command module owns its option parsing and exposes a single
// `run(opts): Promise<number>` that returns a process exit code. Adding a
// command later is: create `src/commands/<name>.ts` exporting `run`, then add
// one `registerCommand(...)` call below.
interface CommandRegistration<Options> {
  name: string;
  description: string;
  configure: (command: Command) => void;
  run: (opts: Options) => Promise<number>;
}

// `--answers` arrives as a file path on the CLI; `init.run` wants the resolved
// puller. Everything else maps straight through.
type InitCliOptions = Omit<init.InitOptions, "answers" | "output"> & { answers?: string };

// Commander option collector for a repeatable, comma-splittable `--namespace`.
function collectNamespace(value: string, previous: string[]): string[] {
  const parts = value
    .split(",")
    .map((part) => part.trim())
    .filter((part) => part.length > 0);
  return previous.concat(parts);
}

function registerCommand<Options>(
  program: Command,
  registration: CommandRegistration<Options>,
): void {
  const command = program.command(registration.name).description(registration.description);
  registration.configure(command);
  command.action(async (opts: Options) => {
    process.exit(await registration.run(opts));
  });
}

export function buildProgram(): Command {
  const program = new Command();
  program
    .name("team-ai")
    .description("Forkable framework for standing up a team's AI capability")
    .version(packageVersion());

  registerCommand(program, {
    name: "validate-kb",
    description: "Validate knowledge-base front matter and cross-document relations",
    configure: (command) => {
      command
        .option("--root <dir>", "knowledge-base root directory", "kb")
        .option(
          "--instance <dir>",
          "instance directory; KB root and exclusions come from its index.lock",
        )
        .option("--schema-only", "validate front matter only; skip relation checks", false);
    },
    run: validateKb.run,
  });

  registerCommand(program, {
    name: "validate-manifest",
    description: "Check manifest topology invariants against agent definitions",
    configure: (command) => {
      command.option("--root <dir>", "instance root directory", ".");
    },
    run: validateManifest.run,
  });

  registerCommand(program, {
    name: "validate-citations",
    description: "Check that markdown citations resolve to knowledge-base documents",
    configure: (command) => {
      command.option("--root <dir>", "repository root containing kb/ and/or agents/", ".");
    },
    run: validateCitations.run,
  });

  registerCommand(program, {
    name: "validate-spoke",
    description: "Check a spoke repo against the spoke contract",
    configure: (command) => {
      command.option("--root <dir>", "spoke repo root directory", ".");
    },
    run: validateSpoke.run,
  });

  registerCommand(program, {
    name: "reindex",
    description: "Rebuild the retrieval index for an instance directory",
    configure: (command) => {
      command.option("--root <dir>", "instance root directory containing kb/", ".");
    },
    run: reindex.run,
  });

  registerCommand(program, {
    name: "remap-namespaces",
    description: "Rewrite KB namespace and id values from a mapping file (proposal unless --apply)",
    configure: (command) => {
      command
        .option(
          "--instance <dir>",
          "instance directory whose index.lock declares the KB scope",
          ".",
        )
        .option("--mapping <file>", "YAML mapping: namespaces and per-file overrides")
        .option("--out <file>", "where to write the proposal", "remap-proposal.yaml")
        .option("--inventory <file>", "also write a tab-separated inventory")
        .option("--apply", "write the changes; refuses while any conflict exists", false);
    },
    run: remapNamespaces.run,
  });

  registerCommand(program, {
    name: "assemble-manifest",
    description: "Merge the instance manifest fragment and spoke configs into manifest.yaml",
    configure: (command) => {
      command
        .option("--root <dir>", "instance root directory", ".")
        .option("--check", "verify manifest.yaml is current without writing it", false);
    },
    run: assembleManifest.run,
  });

  registerCommand(program, {
    name: "freshness-audit",
    description: "Report stale, orphaned, and unowned knowledge-base documents as JSON",
    configure: (command) => {
      command
        .option("--root <dir>", "knowledge-base root directory", "kb")
        .option(
          "--instance <dir>",
          "instance directory; KB root and exclusions come from its index.lock",
        )
        .option("--fail-on-stale", "exit non-zero when stale documents exist", false)
        .option("--open-issues", "draft GitHub issues for stale docs (dry run only)", false)
        .option("--repo <owner/name>", "target repository for --open-issues live mode")
        .addOption(
          new Option("--today <YYYY-MM-DD>", "override today's date (testing)").hideHelp(),
        );
    },
    run: freshnessAudit.run,
  });

  registerCommand(program, {
    name: "run-evals",
    description: "Replay the golden eval set: hit rate, routing accuracy, refusal, tier ceiling",
    configure: (command) => {
      command
        .option("--root <dir>", "instance root directory", ".")
        .option("--golden <dir>", "golden set directory, relative to --root", "evals/golden")
        .option("--json", "emit the EvalReport as JSON instead of a table", false);
    },
    run: runEvals.run,
  });

  registerCommand(program, {
    name: "check-agnostic",
    description: "Fail if shipped framework source contains a team's proper nouns",
    configure: () => undefined,
    run: checkAgnostic.run,
  });

  registerCommand(program, {
    name: "doctor",
    description: "Run environment and setup checks (--self for framework CI, else an instance)",
    configure: (command) => {
      command
        .option("--root <dir>", "instance root directory to check", ".")
        .option("--self", "run framework self-verification instead of an instance check", false)
        .option("--strict", "treat not-built-yet and remaining items as failures", false);
    },
    run: doctor.run,
  });

  registerCommand<InitCliOptions>(program, {
    name: "init",
    description: "Run the interview and generate an instance without overwriting human work",
    configure: (command) => {
      command
        .option("--dir <dir>", "target directory to generate into", ".")
        .option("--catalog <dir>", "instance catalog directory layered over the framework catalog")
        .option("--dry-run", "classify what would be written; write nothing", false)
        .option("--resume", "resume a saved interview instead of starting fresh", false)
        .option(
          "--answers <file>",
          "keyed YAML mapping by question id (legacy positional lists also supported)",
        )
        .addOption(
          new Option(
            "--on-conflict <mode>",
            "coexistence strategy when files or an existing harness collide",
          ).choices(["adopt-existing", "siblings", "subdir", "abort"]),
        )
        .addOption(
          new Option(
            "--preflight-target <dir>",
            "directory to preflight-scan (testing)",
          ).hideHelp(),
        );
    },
    run: (opts: InitCliOptions): Promise<number> => {
      const { answers, ...rest } = opts;
      const initOpts: init.InitOptions = { ...rest };
      const loaded = typeof answers === "string" ? loadAnswerFile(answers) : undefined;
      if (loaded) initOpts.answers = loaded.pull;
      return init.run(initOpts).then((code) => {
        if (loaded) {
          for (const key of loaded.unusedKeys()) {
            console.error(
              `WARNING: answers file entry '${key}' was never asked (pre-filled or skipped)`,
            );
          }
        }
        return code;
      });
    },
  });

  registerCommand(program, {
    name: "adopt",
    description:
      "Measure an existing repo against the framework standard and generate a deterministic adoption plan",
    configure: (command) => {
      command
        .option("--root <dir>", "existing repo root to measure", ".")
        .option("--out <dir>", "directory to write the adoption plan into", ".")
        .option("--horizon-days <n>", "review-by horizon for backfilled front matter", "180")
        .option("--namespace-map <file>", "YAML file of folder: namespace overrides")
        .option(
          "--include-archived",
          "also measure docs under archive/ and notion-export/ (skipped by default)",
          false,
        )
        .option("--interactive", "walk the written plan and record approvals into it", false)
        .option("--apply", "write the approved parts of the plan into the repo", false);
    },
    run: adopt.run,
  });

  registerCommand(program, {
    name: "spoke",
    description: "Scaffold a thin spoke repo and check it against the spoke contract",
    configure: (command) => {
      command
        .option("--dir <dir>", "target directory to generate into", ".")
        .option("--force", "overwrite an existing spoke.yaml pre-check", false);
    },
    run: spoke.run,
  });

  registerCommand(program, {
    name: "attach",
    description: "Write a .team-ai.yaml so a repo can consume an existing instance (attach mode)",
    configure: (command) => {
      command
        .option("--dir <dir>", "target directory to write into", ".")
        .option("--force", "overwrite an existing .team-ai.yaml pre-check", false);
    },
    run: attach.run,
  });

  registerCommand(program, {
    name: "resume",
    description: "Re-open a saved interview and ask only the newly relevant questions",
    configure: (command) => {
      command
        .option("--dir <dir>", "instance directory containing team-profile.yaml", ".")
        .option("--catalog <dir>", "instance catalog directory layered over the framework catalog");
    },
    run: resume.run,
  });

  registerCommand(program, {
    name: "review",
    description: "Replay the three interview gate summaries from team-profile.yaml (read-only)",
    configure: (command) => {
      command.option("--dir <dir>", "instance directory containing team-profile.yaml", ".");
    },
    run: review.run,
  });

  registerCommand(program, {
    name: "upgrade",
    description:
      "Refresh the framework plumbing (CI, eval gates, SETUP, index.lock chunk) in place",
    configure: (command) => {
      command
        .option("--dir <dir>", "instance directory containing team-profile.yaml", ".")
        .option("--catalog <dir>", "instance catalog directory layered over the framework catalog");
    },
    run: upgrade.run,
  });

  registerCommand(program, {
    name: "emit",
    description: "Translate an instance into a target platform's agent layout",
    configure: (command) => {
      command
        .addOption(
          new Option("--target <target>", "output format").choices([
            "claude-code",
            "mcp-only",
            "generic",
          ]),
        )
        .option("--dir <dir>", "instance directory", ".")
        .option("--out <dir>", "output directory (should be gitignored)", "emitted")
        .option("--file-prefix <prefix>", "prefix for emitted Claude Code agent file names", "")
        .option("--no-plugin-manifest", "do not write .claude-plugin/plugin.json")
        .option(
          "--builtin-search",
          "give agents Read, Grep, Glob and a namespace lookup section",
          false,
        )
        .option(
          "--allow-tracked",
          "emitted output is intentionally committed; skip the gitignore warning",
          false,
        )
        .option("--search-command <cmd>", "command used by generated agents for ranked search");
    },
    run: emit.run,
  });

  // `search` takes a positional argument, which the shared helper does not
  // model, so it is registered directly.
  program
    .command("search")
    .description("Query the retrieval index and print ranked hits")
    .argument("<query>", "search query text")
    .option("--root <dir>", "instance root directory containing kb/", ".")
    .option("--k <n>", "maximum number of hits", (value) => Number.parseInt(value, 10), 8)
    .option(
      "--namespace <ns>",
      "restrict to namespace(s); repeatable or comma-separated",
      collectNamespace,
      [],
    )
    .option("--json", "emit the raw Hit[] as JSON", false)
    .action(async (query: string, opts: search.SearchCommandOptions) => {
      process.exit(await search.run(query, opts));
    });

  return program;
}

export async function main(argv: string[] = process.argv): Promise<void> {
  await buildProgram().parseAsync(argv);
}

// Run when invoked directly (`node dist/cli.js …`). The installed binary calls
// `main()` from `bin/team-ai.js` instead.
if (import.meta.url === pathToFileURL(process.argv[1] ?? "").href) {
  void main();
}
