# Question flow cheat sheet

One page. Full logic lives in `src/interview/engine.ts`; questions in
`src/interview/questions.yaml`.

## The six acts

| Act | Name | Question ids | Produces |
| --- | --- | --- | --- |
| 0 | Preflight | `pre.assessment`, `pre.overlap`, `pre.probe_result` | extend / coexist / stand-down verdict |
| 1 | Mode and team context | `mode`, `ctx.org_path`, `team.name`, `team.mission`, `team.size`, `team.surfaces`, `team.sources`, `team.consumers` | team identity |
| 2 | Knowledge model | `kb.substrate`, `kb.namespaces`, `kb.catalog_override`, `kb.sources_strategy`, `kb.sensitivity`, `kb.write_back` | knowledge layout |
| 3 | Architecture and cost | `arch.index_driver`, `kb.graph_questions`, `arch.hosting`, `arch.language`, `arch.ci`, `arch.topology`, `arch.model_tiers`, `arch.cache` | architecture decisions |
| 4 | Agents, subagents, personas, skills | `agents.roles`, `agents.domains`, `agents.personas`, `agents.skills`, `agents.strictness`, `agents.seed` | agent plan |
| 5 | Handoff | — | `team-profile.yaml` |

## The three gates

| After act | Gate | Confirms |
| --- | --- | --- |
| 2 | Gate 1 — strategy | preflight, team identity, substrate, driver, namespaces, catalog, sources, sensitivity, write-back |
| 3 | Gate 2 — architecture | driver, hosting, file-tree note |
| 4 | Gate 3 — agent plan | domain subagents, role subagents, personas, skills, eval namespace count |

Nothing is written until Gate 3 is confirmed.

## Controls (type at any question)

| Word | Effect |
| --- | --- |
| `back` | undo the last answer |
| `skip` | alias for `defer` |
| `why` | print the question's `why` text (cites `docs/quality-bar.md`) |
| `save` | stop; emit the partial profile to resume later |

## First-class answers

- **`defer`** — on questions with `allow_defer: true`. Records a TODO, applies
  the `default`, moves on. The deferred item shows in every gate summary with a
  revisit checkpoint.
- **`recommend`** — on questions with a `recommend` value. Takes the recommended
  option and always prints `recommend_why`.

## Branching

- `ask_if` gates a question: `always`, `<id> == "v"`, `<id> != "v"`,
  `<id> in ["a","b"]`, `has(<id>,"v")`, with `()`, `&&`, `||`.
- `implies` on a chosen option pre-fills later answers; the user can still
  override by answering that question directly.
- `implies.warn` is not a pre-fill — it surfaces the option's downside once.
