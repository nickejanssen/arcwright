# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.6.6] - 2026-09-23

### Removed

- **`emit --agent-hook`**, added in 0.6.5. A `PreToolUse` hook declared in an
  agent's own front matter was measured never to run, in the Claude Code
  desktop app and in the CLI. A hook registered in the host's settings does
  run for subagent tool calls and identifies the agent through `agent_type`;
  instances enforce boundaries there instead.

### Added

- **A counting rule in every emitted agent:** a stated number of items must
  equal the items listed. Live probes returned correct lists under wrong totals.

## [0.6.5] - 2026-09-22

### Added

- **`emit --agent-hook <cmd>`** declares a `PreToolUse` hook, matching
  `Read|Grep|Glob|Bash`, in each emitted agent's own front matter. An instance
  uses it to hold its knowledge-base agents inside the knowledge base
  mechanically, since agents told so in words read files outside it. Declared
  per agent, it runs only for those agents rather than for every tool call the
  host session makes.

## [0.6.4] - 2026-09-22

### Changed

- **Claude Code builtin-search emit no longer writes delegating agents.**
  Routers and group agents (`kind: router` or `max_hops > 0`) stay in the
  manifest for hosts that do not route, but are not emitted for Claude Code,
  whose session routes natively. As emitted they were told to hand off with no
  tool that could, and improvised across several namespaces instead.
- **Emitted agents set `omitClaudeMd: true`,** so an agent that must answer
  from the knowledge base does not answer from the host's project instruction
  files, and does not pay for loading them on every dispatch.

### Added

- **Answering rules in every emitted agent:** status, code existence, merge
  history and CI results are named to their owning source rather than answered
  from documents; no unstated percentages or estimates; an unfound item is
  reported with the terms searched, never as nonexistent; conflicting
  documents are cited together.
- **`## Domain rules` passthrough.** That one section of an agent's
  instructions file is emitted; the rest is written for hosts with team-ai's
  own retrieval tools and is not.
- **Emit refuses an agent whose instructions need a tool it lacks** (a shell
  block without Bash, a hand-off without Agent, a `kb_*` tool not granted).

## [0.5.0] - 2026-09-14

### Changed

- **`better-sqlite3` upgraded from 11.10.0 to 13.0.3.** v13 rewrote the native
  binding on Node-API (N-API) instead of the old node-gyp/prebuild-install
  path, so a single prebuilt binary now runs across Node 22, 24, and later
  majors without a C++ toolchain. `@types/better-sqlite3` moved from 7.6.12 to
  9.6.0 to match. README.md and docs/README.source.md no longer claim Node 24
  needs to compile the native module from source; they now describe Node 22+
  as supported, with Node 22 remaining the `.nvmrc`-pinned default.

## [0.4.0] - 2026-09-14

### Added

- **Manifest topology fields and agent and skill sections.** Manifests now
  preserve domain authority, ownership boundaries, dependencies, and registered
  agents and skills.
- **Deterministic manifest invariant validation.** `validate-manifest` checks
  routers, specialists, namespaces, definitions, and references before use.
- **Instance catalog layering.** `init`, `resume`, and `upgrade` resolve
  instance namespace presets over the framework catalog.
- **Conflict-safe namespace remapping.** `remap-namespaces` plans and applies
  namespace and identifier migrations without partial writes.
- **Committed Claude Code subagents.** `emit --target claude-code` supports
  tracked files, built-in search instructions, and optional plugin manifests.

### Changed

- **Domain SME namespace scope.** Generated domain specialists now use their
  own declared namespace instead of the first namespace in the catalog.
- **Interview answer persistence.** Answers are keyed by question ID so changed
  question banks fail loudly instead of replaying positionally.
- **Knowledge base scope and parsing.** Instances can declare a KB root and
  exclusions; parse failures are reported per file and front matter accepts
  CRLF and bare CR line endings.

### Fixed

- **Local CLI execution.** The MCP server template invokes a configured local
  team-ai build, computes its instance root correctly on Windows, and exposes
  only implemented tools.
- **Source-built CI workflows.** Reusable and generated workflows check out,
  build, and invoke team-ai from source rather than downloading an npm package.
  Generated setup documentation uses the linked local CLI.

### Security

- **The generator and emitters could write outside their output directory.** A
  role or persona name containing `..` segments was joined straight into the
  write path, so a name like `../docs/agents/probe` wrote a file into a
  directory the generator must never touch. Such a name could arrive from a
  hand-edited `team-profile.yaml`, which `resume` and `upgrade` load without
  re-validating answers, or from a catalog file, where a role's `name` is an
  unconstrained string. The interactive interview was not affected, because its
  multi-select answers accept only fixed option values. Role and persona names
  are now validated as a single path segment before anything is written, and
  every generator and emitter write goes through a shared containment check
  that refuses any path resolving outside the output directory.

## [0.3.1] - 2026-09-13

### Fixed

- **`team-ai adopt` misdetected CRLF-opened front matter as missing entirely.**
  `raw.startsWith("---\n")` returns `false` for a file opening with `---\r\n`,
  which real files in the wild do. At apply time that would have prepended a
  second front-matter block on top of a real one instead of leaving the file
  alone. Fixed with a single shared `hasFrontmatter()` (`/^---\r?\n/`) used by
  both plan-time detection and apply-time's own guard, so the two can no
  longer disagree with each other.
- **A single file with front matter that fails strict YAML parsing crashed
  the entire adoption scan.** Once CRLF front matter is correctly detected as
  present, it gets parsed — and a real file's YAML, tolerated by some tooling
  but rejected by this parser, threw an uncaught `YAMLParseError` that
  aborted the whole repo scan instead of flagging just that file.
  `parseFrontmatter` failures now become a normal backfill conflict for a
  human to resolve.

## [0.3.0] - 2026-09-12

### Added

- **`team-ai adopt --interactive` can now correct a backfill item's `status`,
  not just its `owner`.** `inferFrontmatter` always assigns a newly-backfilled
  doc `status: active` — it has no way to know a doc is a placeholder awaiting
  real content (a story-bible stub ahead of its GDD, for example). "edit" now
  also prompts for `status` (`draft | active | deprecated`); blank keeps the
  current value, and an invalid entry is rejected with the original kept
  rather than writing something unvalidated. This is the mechanism for
  telling the KB "this is provisional" instead of adopting placeholder
  content as if it were as authoritative as real, invested-in source
  material.

## [0.2.0] - 2026-09-12

### Changed

- **`team-ai adopt` anchors `review_by` on last git edit, not on "today".**
  Backfilling front matter for a pre-existing doc previously assigned every
  doc a fresh `today + horizonDays` review date, so long-neglected content
  read as freshly reviewed. `review_by` now anchors on the doc's actual last
  git commit date when one is known (one additional single-pass `git log`
  traversal, same shape as the existing author-collection pass), falling
  back to `today` only when there is no git history. Already-overdue content
  now surfaces as overdue immediately on adoption, not six months later.
  `docs/adoption-plan.md` and the `adopt` CLI summary both report an
  "already due for review on arrival" count, and each affected backfill row
  carries a warning label.

## [0.1.0] - 2026-08-30

First tagged release. The deterministic layer and the interview are complete and
tested (~520 tests). Anything needing a running service or a second retrieval
driver ships as an honest stub — see `docs/definition-of-done.md` and the
"Known limitations" section of `README.md`.

### Added

- **Guided interview.** One question bank (`src/interview/questions.yaml`,
  ~25 questions, Acts 0–5, three confirmation gates) driven by a deterministic
  engine. Runs as a CLI (`team-ai init`) or as a Claude skill
  (`skills/scaffold-interview/`). Preflight scans for existing AI infrastructure
  and steers toward extend, coexist, or stand down. Answers persist to
  `team-profile.yaml` for `resume`, `review`, and `upgrade`.
- **Non-destructive generator.** Renders an instance, spoke, attach config, or
  MCP-server template from the team profile and catalog presets. Reconciliation
  diffs template output against hand-edited files and never clobbers them,
  writing `*.team-ai-new` siblings instead.
- **`team-ai adopt`.** Deterministic measurement of an existing repo against the
  framework standard: front-matter backfill plan, namespace map, quality-bar gap
  table, template collisions. Writes only `adoption-plan.yaml` and
  `docs/adoption-plan.md` under `--out`; never writes into the measured repo.
- **18 CLI commands.** 10 deterministic scripts that call no model
  (`validate-kb`, `validate-citations`, `validate-spoke`, `reindex`,
  `assemble-manifest`, `freshness-audit`, `run-evals`, `check-agnostic`,
  `doctor`, `search`) plus 8 interview/generator commands (`init`, `adopt`,
  `spoke`, `attach`, `resume`, `review`, `upgrade`, `emit`).
- **Lexical retrieval.** SQLite FTS5 ranked keyword search behind a
  `RetrievalAdapter` interface. The `vector-embedded`, `vector-pgvector`,
  `vector-hosted`, `graph`, and `hybrid` drivers are real classes whose methods
  throw `NotImplementedError` pointing at the phase-8 index checkpoint.
- **Catalogs.** Four namespace presets (`engineering`, `generic`,
  `generic-partner-facing`, `support`) plus role, persona, and skill catalogs,
  resolved toolkit → org catalog → instance. Custom entries generate a TODO stub,
  never a guess.
- **Agent / skill / persona templates and emitters.** Neutral entity definitions
  in `templates/instance/`; `team-ai emit` targets claude-code, mcp-only, or
  generic surfaces from the same profile.
- **Eval harness.** Replays a golden set for hit rate, routing accuracy, refusal
  behaviour, per-question tier ceiling, and cost per answer, gated against
  `DEFAULT_GATES`. One EXAMPLE golden file ships and is skipped by `run-evals`.
- **Optional local MCP server template** (`templates/mcp-server/`) — a generated
  stdio server, off by default. No hosted or remote server, no auth, no
  deployment.
- **JSON schemas** for every artifact (agent, role, spoke, manifest, golden,
  frontmatter, questions, team-profile, namespace-preset, skill-catalog,
  adoption-plan) with a shared loader and validator.
- **Repo scaffolding**: ESLint flat config, Prettier, lefthook, commitlint,
  reusable GitHub Actions workflows (`ci.yml` plus `validate-kb`,
  `validate-spoke`, `evals` reusable workflows), `CONTRIBUTING.md`,
  `SECURITY.md`, `CODEOWNERS`, Apache-2.0 `LICENSE`.
- **`docs/quality-bar.md`** — the 17 questions the framework is judged against,
  each with the answer the architecture gives and the files that enforce it.
- **Dogfood** (`docs/dogfood-notes.md`) — three runs of the framework against
  itself and the five bugs they fixed.

[Unreleased]: https://github.com/nickejanssen/team-ai/compare/v0.5.0...HEAD
[0.5.0]: https://github.com/nickejanssen/team-ai/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/nickejanssen/team-ai/compare/v0.3.1...v0.4.0
[0.3.1]: https://github.com/nickejanssen/team-ai/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/nickejanssen/team-ai/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/nickejanssen/team-ai/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/nickejanssen/team-ai/releases/tag/v0.1.0
