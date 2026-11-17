---
name: scaffold-interview
description: Run the team-ai setup interview inside a chat instead of a terminal. Use when someone wants to stand up a team-ai instance but does not want to run the CLI, or wants to answer the setup questions from a phone and hand the result to an engineer.
---

# scaffold-interview

Drive the `team-ai` setup interview as a chat conversation. Same question bank as
`team-ai init`, same branching logic, same three gates — a different
renderer. (`team-ai` means the CLI built from a clone of the framework repo —
never `npx team-ai`, which fetches an unrelated npm package of the same name.) The output is a `team-profile.yaml` an engineer feeds to
`team-ai init --resume`.

This matters for adoption: an engineering manager on another team can finish the
interview from a phone and hand the profile to someone who runs the CLI.

## Source of truth

You are a second renderer for logic that already exists. Do not reinvent it.

- **Questions:** `src/interview/questions.yaml`, bundled with the framework
  alongside this skill. Read it first. It is the single source of truth for both
  runtimes; never fork it or hard-code its contents here.
- **Branching engine:** `src/interview/engine.ts` is the authoritative state
  machine. It defines exactly how `ask_if`, `implies`, `defer`, and `recommend`
  behave. When this file and `engine.ts` disagree, `engine.ts` wins. The summary
  below is a reading aid, not a spec.
- **Gate summaries:** `src/interview/gates.ts` renders the three confirmation
  gates from engine state.

## Branching rules (summary of `engine.ts`)

Walk the bank act by act, in `questions.yaml` order. For each question:

1. **Evaluate `ask_if`.** Skip the question when the gate is false. Grammar
   (string, evaluated against the answers so far):
   - `always` — always ask.
   - `<id> == "value"` and `<id> != "value"` — compare a prior answer.
   - `<id> in ["a", "b"]` — prior answer is one of the listed values.
   - `has(<id>, "value")` — a prior multi_select answer contains `value`.
   - `( <expr> )` for grouping, `<expr> && <expr>`, `<expr> || <expr>`.
2. **Apply `implies`.** When a chosen option carries `implies`, pre-fill those
   later answers. The pseudo-key `warn` is not a pre-fill: it surfaces the
   option's downside once, then respects the choice. A real pre-fill is a
   default the user can still override by answering that later question
   directly — an explicit answer always wins over a pre-fill.
3. **Offer `defer` and `recommend` where allowed.** On any question with
   `allow_defer: true`, "decide later" (`defer`) is a first-class answer: it
   records a TODO, applies the question's `default`, and moves on. On any
   question with a `recommend` value, "take the recommendation" (`recommend`) is
   a first-class answer and always prints `recommend_why`.
4. Record the answer and continue.

Controls the user can type at any question: `back` (undo the last answer),
`skip` (alias for `defer`), `why` (print the question's `why` text), `save`
(stop and emit the partial profile so they can resume later).

## How to run it

- Ask **at most 3 questions per turn** so the conversation stays readable on a
  phone. Prefer the interactive question UI when the client can render it;
  otherwise use a short numbered list per question.
- For each question show the prompt, the options with their tradeoffs, and note
  when `defer` / `recommend` are available.
- Announce each act as you enter it.
- After Act 2, Act 3, and Act 4, stop at the matching gate (below) before going
  on.

## The six acts

Act numbers come from `questions.yaml` (`act:` field) and `interview-spec.md`
§14–15.

- **Act 0 — Preflight.** Questions `pre.*`. How this setup should relate to AI
  infrastructure already in the repo: extend it, coexist, or stand down. The
  stand-down outcome is a valid, valuable end state — if the user picks it, say
  so plainly and stop. Only ask `pre.overlap` / `pre.probe_result` if the
  operator reports that an existing search or connector already covers the
  sources.
- **Act 1 — Mode and team context.** `mode`, `ctx.org_path`, `team.*`. What is
  being set up (new instance / spoke / attach), the owning org path, and the
  team's name, mission, size, surfaces, sources, and consumers.
- **Act 2 — Knowledge model.** `kb.*`. Substrate, namespace layout, catalog
  source, how existing systems are treated (link / sync / import), sensitivity
  tiers, and whether agents can write back.
- **Gate 1 — strategy** (see below).
- **Act 3 — Architecture and cost.** `arch.*` plus `kb.graph_questions`.
  Retrieval driver, whether a server is needed, language, CI, repo topology,
  model-tier aggressiveness, answer cache.
- **Gate 2 — architecture** (see below).
- **Act 4 — Agents, subagents, personas, skills.** `agents.*`. Role hats (only
  for teams of 4+), starting domains, personas, skills, out-of-KB strictness,
  and whether to seed starter docs.
- **Gate 3 — agent plan** (see below).
- **Act 5 — Handoff.** Produce `team-profile.yaml` (below). In a filesystem-only
  CLI run this is where dry-run / write / `team-ai doctor` happen; in chat it is
  the profile handoff.

## The three gates

Render each gate as a **text summary** of the resolved answers so far, with the
deferred list and any acknowledged warnings, then a confirm step. Mirror the
shape produced by `src/interview/gates.ts`.

- **Gate 1 — strategy:** preflight verdict, team identity, substrate, driver,
  namespaces, catalog, sources strategy, sensitivity, write-back.
- **Gate 2 — architecture:** retrieval driver, hosting decision, resulting file
  tree note.
- **Gate 3 — agent plan:** domain subagents, role subagents, personas, skills,
  eval namespace count.

**Nothing is "written" until Gate 3 is confirmed.** If the user stops before
that, use `save` semantics: emit the partial profile and tell them how to
resume. Only after Gate 3 do you produce the final `team-profile.yaml`.

## Producing `team-profile.yaml`

After Gate 3, emit the profile. Shape (validated against
`schemas/team-profile.schema.json`):

```yaml
team_ai_version: <the framework version this skill ships with>
created: <current UTC timestamp, RFC 3339>
answers:
  # every resolved answer, keyed by question id, including pre-filled and
  # deferred ones with their applied default
  mode: instance
  team.name: <...>
  # ...
deferred:
  - question: arch.index_driver
    applied_default: lexical
    revisit: phase-8 checkpoint with eval data
```

Then:

- **If this skill has filesystem access:** write `team-profile.yaml` into the
  target directory and tell the user an engineer can run
  `team-ai init --resume` there.
- **If it does not:** output the YAML in a fenced code block and tell the user
  to save it as `team-profile.yaml` at the instance root and hand it to an
  engineer, who runs `team-ai init --resume` (or pastes the answers into a fresh
  `team-ai init`).

Do not generate the instance tree yourself. The CLI owns generation,
reconciliation, and `doctor`.

## Reference

`reference/question-flow.md` — one-page cheat sheet of the acts, gates, controls,
and the `defer` / `recommend` answers.
