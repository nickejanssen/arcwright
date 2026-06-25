---
name: arcwright-minigame
description: Add, import, validate, fit-check, test, and promote a mini-game package in the Arcwright repo as a single gated lifecycle. Use whenever someone wants to bring a mini-game into the platform or move one along its lifecycle, even if they only say "add a mini-game", "import this game", "new puzzle/clue mini-game", "scaffold a Nightcap mini-game", "validate my mini-game package", "does this mini-game fit the story", "is this on-spec", "promote the mini-game to playtest/active", or hands over a zip or folder of a game to ingest. Keeps the engine boundary from ADR 0009 intact: Python owns timers, scoring, submissions, outcomes, clue unlocking, and persistence; clients only render and submit; AI never decides outcomes. Author packages under <experience>/mini_games/, defaulting to nightcap/mini_games/.
---

# Arcwright Mini-game Integrator

## Overview

Bring one mini-game into the repo, or move one along its lifecycle, as a single
ordered workflow with pause points between phases. The phases are
**design-intake → scaffold/import → validate → fit-check → test → promote**.
Each phase has a clear stop-and-report gate so a human can steer before the
next phase changes more state.

This skill is deliberately one workflow rather than five separate skills. The
phases share one piece of state (the package path), the surface is small, and a
single mental model avoids cold-start re-derivation on every step. Run only the
phases the user needs; you do not have to start at phase 1 every time. If the
user says "validate my package", jump to phase 2.

When the user brings a game concept, sample web game, pasted prototype, or
design sketch, begin with Phase 0 unless they explicitly ask to skip design and
implement. A browser game can be a useful reference, but it is not the
authoritative mini-game runtime. Treat it as material to extract mechanics,
visual direction, assets, and player intent from, then map those into the
Arcwright package and runtime boundary.

### What already exists vs. what does not

Read this before promising anything. The authoring foundation is built; the
runtime is not.

- **Built (AW-249):** the generic schema in `engine/mini_games/models.py`
  (`MiniGameManifest`, `MiniGameDefinition`, `MiniGameBinding`, lifecycle and
  enum types), the package loader in `engine/mini_games/loader.py`
  (`load_mini_game_package`, `load_mini_game_catalog`), the per-experience
  package layout under `<experience>/mini_games/<game_id>/`, and a copyable
  `_template/`.
- **Not built yet (AW-250 → AW-254, Planned):** the deterministic runtime,
  persistence (`mini_game_runs`, `mini_game_submissions`), the API and events,
  the TypeScript SDK, and web rendering.

The practical consequence: today you can **author and validate** a mini-game,
**check its fit**, and **promote its lifecycle metadata**. You cannot **run**
one, and you cannot write a real end-to-end playability test. Say this plainly
rather than faking a usability pass. The test phase is built to grow into
runtime tests as those tasks ship.

## The Non-negotiable Boundary (ADR 0009)

Every phase enforces these. A change that erodes one is a blocker, not a
preference. Source: `docs/decisions/0009-mini-game-runtime-boundary.md` and
`docs/architecture/08-event-system.md`.

- Python owns authoritative timers, submission validation, scoring, outcomes,
  clue unlocking, and persistence. Clients render authorized state and submit
  actions only.
- AI never chooses outcomes or mutates canonical session state. Authored,
  generative, and hybrid content all resolve **before** deterministic
  execution.
- Every definition carries a delayed clue fallback so a timeout or failed
  puzzle can never make the mystery unsolvable.
- In v1, behavioral outputs are neutral metrics or deterministic, game-scoped
  observations only. They must not affect killer assignment or any
  cross-session behavior. That wiring is approved only for v1.1 and must not be
  built here.
- `client/` is a presentation workspace. Timers, scoring, and clue logic must
  never live there.

If a requested mini-game needs any of those guarantees broken, stop and say so.
Do not design around the boundary.

## How to collaborate on design

Mini-game design is a product and architecture pass before it is an
implementation pass. Be direct, push back on weak fit, and flag scope creep,
privacy risk, IP concern, and boundary violations early. Ask concise questions
instead of filling important blanks. Prefer a clear recommendation with brief
reasoning over a neutral list when the trade-off is obvious.

Respect creative ownership. Mechanics, systems, scoring, schemas, edge cases,
player-count scaling, and structural in-world justification are in scope for
the agent. Final narrator voice, scripted prose, character content, and
worldbuilding belong to the human author unless they explicitly delegate them.
For diegetic framing, propose scaffolding and mark where the author should
write final copy.

Keep design passes credit-conscious. Read the smallest canonical docs needed,
say which files you read, and say plainly when a file could not be read. Do not
silently infer engine contracts from memory.

## Choosing the experience

Packages are experience-scoped. Default to `nightcap/mini_games/` because that
is the only experience with mini-games today. If the user names another
experience (for example a future `monster-rpg`), use
`<experience>/mini_games/` instead, but first confirm that experience actually
has a `mini_games/` directory with a `_template/`. Do not invent a new
experience tree on your own; cross-experience sharing and any third-party studio
packaging story are unbuilt and out of MVP scope. If the user asks for that,
name it as out of scope and ask whether to proceed single-experience for now.

## Phase 0: Design Intake and Lock

Goal: turn a concept or sample game into a locked mini-game brief before files
are created or changed. Do not start coding in this phase unless the user
explicitly asks for implementation.

First, read the relevant canonical docs: `docs/README.md`,
`docs/prd/02-requirements.md`, `docs/decisions/0009-mini-game-runtime-boundary.md`,
`docs/story-bibles/nightcap-murder-mystery.md`, and the relevant mini-game
specs. If the game may touch surfaces, events, or arc execution, also read
`docs/architecture/03-arc-execution.md` and
`docs/architecture/08-event-system.md`.

Then walk the user through the smallest useful set of decisions. For a mature
concept, ask only what is missing. For a loose concept, work through these in
order:

- **Concept:** working title, logline, core verb, and why it belongs in a
  murder mystery party game.
- **Nightcap role:** target beat range, clue-gate vs pure social opener,
  investigative payload, and in-world justification.
- **Player model:** individual, collaborative, group, competitive, or mixed;
  player-count behavior for 4, 5, 6, 7, and 8 players.
- **Scoring and outcomes:** what earns points, whether score is throwaway
  per-game feedback or affects standing later, success, failure, tie, timeout,
  and abort behavior.
- **Two-surface contract:** what appears on phone, shared display, and host
  view; which information must remain private; what the browser may render or
  submit.
- **Authoritative rules:** which timers, scoring, submissions, randomization,
  clue unlocks, and fallback decisions Python must own.
- **Content strategy:** authored, generative, or hybrid content; provenance of
  any facts, clues, symbols, boards, prompts, or level seeds.
- **Behavioral outputs:** neutral v1 metrics to log, with names and payload
  shape; confirm they are not wired into killer assignment until approved v1.1
  work.
- **Fallback:** delayed clue fallback, clue variant, host override, and how the
  story remains solvable if every player fails or stalls.
- **Replay variance:** what changes between sessions without changing the
  authored contract.
- **Assets and prototype intake:** source files, art, sound, interaction
  affordances, IP ownership, and any existing browser logic that must be moved
  behind the engine boundary.

For competitive arcade-style games, be especially strict about score meaning.
A high score can create table energy, but it should either gate a clue, create
an investigative lead, or produce a neutral behavioral signal. If it is only a
detached arcade score, recommend a stronger Nightcap framing before packaging.

End this phase with a compact locked brief:

- game ID and title
- package lifecycle target
- participation mode, content mode, player count, and target duration
- target beat or beat range
- clue, fallback, and outcome contract
- two-surface contract
- authoritative engine responsibilities
- allowed client responsibilities
- behavioral outputs
- unresolved human-authored copy or story items
- docs, spec, issue, or ADR needs

If the user asks for a handoff prompt instead of implementation, generate a
copy-paste-ready build prompt from the locked brief. The handoff must require
the next agent to read `AGENTS.md`, read canonical docs, inspect existing
mini-games, create or update a spec before implementation when scope is new,
respect ADR 0009, run validation, and avoid em dashes.

## Phase 1: Scaffold or Import

Goal: produce a valid package directory in `draft` lifecycle. Do **not** touch
`<experience>/arc.json` here. Arc bindings come only at promotion, and only when
the game is lifecycle-ready.

### Git-native scaffold (default and preferred)

The repo's authoring model is a version-controlled package copied from
`_template/`, not a zip blob. Prefer this path.

1. Pick a `game_id`: lowercase kebab-case, matching `^[a-z0-9]+(?:-[a-z0-9]+)*$`.
   It must equal the directory name; the catalog loader rejects mismatches.
2. Scaffold the package with the helper script:

   ```bash
   python docs/skills/arcwright-minigame/scripts/minigame_tool.py scaffold \
     --experience nightcap --game-id my-game --title "My Game"
   ```

   This copies `<experience>/mini_games/_template/` to
   `<experience>/mini_games/my-game/`, stamps the `game_id` and `title` in both
   `manifest.json` and `definitions/0.1.0.json`, and validates the result. If
   the helper cannot run (for example on a host without Python), copy
   `_template/` by hand and edit the two JSON files so their `game_id` matches
   the directory name.
3. If Phase 0 produced a locked brief, map those decisions into
   `definitions/0.1.0.json`. If not, ask the author for the values that the
   schema needs, then edit the definition. Ask as a short multiple-choice batch,
   not a long interrogation, because each maps to a typed field:

   - `mechanic_type` (kebab-case label for the puzzle type)
   - `participation_mode`: `individual` | `collaborative` | `group`
   - `content_mode`: `authored` | `generative` | `hybrid`
     - `authored` and `hybrid` require `authored_content`.
     - `generative` and `hybrid` require `generation_constraints`.
   - `min_players` / `max_players` (min cannot exceed max)
   - `duration_seconds`
   - `behavioral_outputs`: neutral, game-scoped metrics only (see the boundary)
   - `clue_fallback`: `delay_seconds`, `clue_variant` (`full` | `reduced`),
     `host_override`. This is required and is the safety net.
4. Put presentation prototypes in `client/` and static files in `assets/`. Add
   every asset path to `manifest.json.asset_paths`; the loader fails if a listed
   asset is missing. Client files may demonstrate presentation and input shape,
   but must not decide authoritative timers, scores, outcomes, clue fallback, or
   clue unlocks.

### Zip / external import

If the user hands over a zip or an out-of-tree folder, treat it as a normalize
step, not a new model: unpack it, then map its contents into the standard
package shape above (scaffold first, then move authored rules into
`definitions/<semver>.json`, presentation into `client/`, static files into
`assets/`). Once it is a normal package, the rest of the workflow is identical.
Flag anything in the import that assumes client-side scoring/timing/state, since
that violates the boundary and must be reworked before it can ship. If the
prototype is an interactive browser game, preserve useful visuals and input
affordances, but move authoritative game semantics into the locked definition
and future Python runtime contract.

**Pause and report** the package path, the chosen field values, and anything
the author still has to fill in. Then continue.

## Phase 2: Validate

Goal: prove the package is internally consistent before anyone reviews it.

```bash
python docs/skills/arcwright-minigame/scripts/minigame_tool.py validate \
  nightcap/mini_games/my-game
```

The helper calls `engine.mini_games.load_mini_game_package`. Equivalent inline
call if you prefer not to use the script:

```python
from pathlib import Path
from engine.mini_games import load_mini_game_package
load_mini_game_package(Path("nightcap/mini_games/my-game"))
```

To check a whole experience catalog for duplicate IDs and directory/`game_id`
mismatches, point the helper at the `mini_games/` directory (or pass
`--catalog`); it calls `load_mini_game_catalog`, which loads only
`active` packages and skips `draft`, `playtest`, and `retired` authoring
packages.

Translate any failure into plain language and the fix. Common ones:

- directory name does not equal `manifest.game_id`
- `definition_path` does not point at `definitions/<current_version>.json`
- `content_mode` set without the matching `authored_content` /
  `generation_constraints`
- `min_players` greater than `max_players`
- a listed asset path is missing on disk
- duplicate `behavioral_outputs` keys
- bad semver or non-kebab-case `game_id`

**Pause and report** pass/fail with the exact errors and next steps. Do not
proceed to fit-check on a package that does not load.

## Phase 3: Fit-check (creative and product)

Goal: confirm the game belongs in the experience and respects scope. This is
the repeatable checklist version of "would the storytellers, world-builders, and
product owners sign off". For authoritative product, story, scope, or
architecture answers, invoke the `arcwright-sme` skill rather than guessing.

Check and record evidence for each:

- **Story fit:** consistent with `docs/story-bibles/nightcap-murder-mystery.md`
  (tone, world, the clue/investigation loop). Note section references.
- **Scope approval:** mini-games are protected Nightcap v1 scope under D-058
  (`docs/product/decisions-log.csv`). A new mechanic that goes beyond that needs
  durable approval evidence (a decision-log entry plus an ADR or approved spec)
  before it is treated as build scope. If it is missing, flag it; do not invent
  approval.
- **Boundary compliance:** delayed clue fallback present and sane; no
  canonical-state logic implied on the client; behavioral outputs neutral and
  game-scoped; no killer-assignment or cross-session influence.
- **Diegetic fit:** the game has a structural in-world reason to happen at the
  selected beat. The author can supply final voice, but the interaction cannot
  feel like an unrelated arcade mode dropped into the room.
- **Playability sanity:** player count and duration are realistic for a party
  session; failure or timeout still advances the arc via the fallback.

**Pause and report** a fit verdict (fits / fits with changes / does not fit)
with per-item evidence and the canonical doc paths.

## Phase 4: Test

Goal: run every check that is meaningful today, and name the ones that are not
possible yet so no one mistakes the gap for a pass.

Run, from the repo root:

```bash
pytest engine/tests/test_mini_game_models.py -q
python docs/skills/arcwright-minigame/scripts/minigame_tool.py validate <package_path>
python -m ruff check engine
python -m ruff format --check engine
```

If the catalog test suite fails, check whether a package was promoted to
`active` without the corresponding catalog expectations being updated. Draft
and playtest packages are authoring-only and should stay out of the production
catalog until promotion is intentional.

Then state clearly: end-to-end runtime, persistence, API/SDK, and on-device
usability tests **cannot run yet** because AW-250 through AW-254 are not built.
Do not synthesize a fake "the game is playable" result. When those tasks land,
extend this phase with their integration tests.

**Pause and report** which checks passed, which are blocked, and why, separating
new failures from pre-existing ones.

## Phase 5: Promote (gated, optional)

Goal: advance lifecycle metadata and, only when ready, bind the game into the
arc. Do this only when the author explicitly asks and the prior phases passed.

Lifecycle is metadata, not a directory move: `draft → playtest → active →
retired`. Rules:

- A definition becomes **immutable once it enters `playtest`**. To change a
  playtested or active game, create a new semantic version
  (`definitions/<new-semver>.json`) and point `manifest.current_version` and
  `definition_path` at it. Never edit a playtested definition in place.
- Bump `lifecycle` in `manifest.json` one step at a time and re-run phase 2.
- `draft` and `playtest` packages are authoring-only and stay out of the
  production catalog. `active` packages are discoverable through
  `load_mini_game_catalog`.
- Only when promoting to a lifecycle the implementing spec requires, add a
  version-pinned `MiniGameBinding` (`binding_id`, `game_id`, `version`) to the
  experience arc (for Nightcap, `nightcap/arc.json`). A draft package must never
  be added to the arc.

**Pause and report** the lifecycle change, any new version created, and whether
an arc binding was added.

## Stop Conditions

- A request that requires breaking the ADR 0009 boundary (client-side scoring,
  AI deciding outcomes, no fallback, v1 behavioral wiring into killer
  assignment).
- A new mechanic or scope with no durable approval evidence.
- A package that will not load through the engine loader.
- A concept that cannot explain its Nightcap purpose beyond "fun on its own".
- A request to create a brand-new experience tree or cross-experience/
  third-party sharing model (out of MVP scope) without explicit direction.

## Platform Notes

This skill is platform-neutral so it runs in Claude Code, the Claude app,
Codex, and ChatGPT. Codex and ChatGPT pick it up via
`agents/openai.yaml`.

- The helper script is a convenience for hosts that can run Python from the repo
  root. Where Python is unavailable, every step has a manual equivalent: copy
  `_template/`, edit the JSON, and reason about the schema in
  `engine/mini_games/models.py`. The engine remains the single source of truth
  for field rules; the script never re-encodes them.
- Use the host's file and git tooling when present. If absent, ask the user to
  paste the package files and continue with the same workflow.
- Treat this file as the procedure of record. Read canonical docs
  (`docs/decisions/0009-mini-game-runtime-boundary.md`, the story bible, the
  story-relevant specs `docs/specs/0046`–`0051`) when a phase needs detail.
