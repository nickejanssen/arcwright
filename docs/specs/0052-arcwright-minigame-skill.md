# Arcwright Mini-game Integration Skill

**Status**: Done

**Author**: Claude | **Date**: 2026-06-22

---

# References

- Related docs: `AGENTS.md`, `docs/README.md`
- Related ADRs: `docs/decisions/0009-mini-game-runtime-boundary.md`
- Architecture sections: `docs/architecture/03-arc-execution.md`, `docs/architecture/08-event-system.md`, `docs/architecture/15-development-guide.md`
- Related specs: `docs/specs/0046-aw-249-nightcap-mini-game-authoring-foundation.md`, `docs/specs/0030-arcwright-doc-bundler-skill.md`, `docs/specs/0018-github-task-implementer-skill.md`
- Story bible: `docs/story-bibles/nightcap-murder-mystery.md`
- Product decisions: `docs/product/decisions-log.csv` (D-058)
- GitHub issue: #159

---

# Overview

Add a repo-tracked, platform-neutral skill `arcwright-minigame` that walks an
agent through bringing a mini-game into the platform as a single gated lifecycle:
scaffold/import, validate, fit-check, test, and promote. The skill operationalizes
the AW-249 authoring foundation and enforces the ADR 0009 runtime boundary so
mini-game integration is consistent and safe across Claude Code, Claude, Codex,
and ChatGPT.

---

# In Scope

- Add a canonical skill at `docs/skills/arcwright-minigame/`
- Add a thin Codex launcher at `.agents/skills/arcwright-minigame/`
- Add an `agents/openai.yaml` interface for Codex and ChatGPT discovery
- Add a reusable helper script that scaffolds a package from `_template` and
  validates packages and catalogs through the existing engine loader, without
  re-encoding the schema
- Drive a five-phase workflow with pause-and-report gates: scaffold/import,
  validate, fit-check, test, promote
- Enforce the ADR 0009 boundary in every phase (Python owns timers, scoring,
  submissions, outcomes, clue unlocking, and persistence; clients render and
  submit only; AI never decides outcomes; a delayed clue fallback is required;
  no v1 behavioral wiring into killer assignment)
- Default to `nightcap/mini_games/`, parameterized by experience
- Keep the skill usable by Claude Code, Claude, Codex, ChatGPT, or any agent that
  can read repository files and run local commands

---

# Out of Scope

- Implementing the mini-game runtime, persistence, API/events, SDK, or web
  rendering (AW-250 through AW-254)
- v1.1 behavioral wiring into killer assignment or cross-session behavior
- New experience trees or a third-party studio packaging and sharing model
- Changes to engine schema, model routing, prompts, or eval behavior
- Adding dependencies
- Treating any zip or external folder as a new model rather than normalizing it
  into the standard package shape

---

# Acceptance Criteria

- [x] Repo contains `docs/skills/arcwright-minigame/SKILL.md`
- [x] A thin Codex launcher exists at `.agents/skills/arcwright-minigame/SKILL.md`
- [x] An `agents/openai.yaml` interface exists for the skill
- [x] A reusable helper script exists at
      `docs/skills/arcwright-minigame/scripts/minigame_tool.py` that scaffolds
      from `_template` and validates via `engine.mini_games`, with no schema
      re-encoding
- [x] The skill enforces the ADR 0009 boundary in every phase
- [x] The skill requires a delayed clue fallback on every definition
- [x] The skill defaults to `nightcap/mini_games/`, is experience-parameterized,
      and flags cross-experience and third-party packaging as out of scope
- [x] The skill is explicit that the runtime is unbuilt and refuses to fake
      runtime or playability tests
- [x] No new dependencies are added; `engine/` and `nightcap/arc.json` are
      untouched by this change
- [x] `pytest engine/tests/test_mini_game_models.py` passes

---

# Test Plan

- Smoke-test the helper: scaffold a throwaway package, validate it, validate the
  catalog, then remove it and confirm a clean tree.
- Run `pytest engine/tests/test_mini_game_models.py`.
- Benchmark the skill with the skill-creator eval loop across representative
  prompts (authored scaffold, generative content mode, and a boundary-violation
  refusal), comparing with-skill versus no-skill runs.

Result of the eval loop: with-skill 100 percent versus no-skill 88 percent
assertion pass rate. The skill prevented two regressions the no-skill baseline
produced: weakening an engine test to make the suite pass, and binding a draft
mini-game into `nightcap/arc.json`.

---

# Risks and Unknowns

**Risks**:
- The runtime is unbuilt, so the test phase cannot prove playability; an agent
  could overstate readiness if it ignores the skill's honesty rule.
- Authoring the first real production package legitimately breaks
  `test_reserved_directories_are_not_loaded_as_production_catalog`; an agent
  could weaken that test instead of attributing it to AW-254. The skill calls
  this out explicitly.

**Unknowns**:
- How a multi-experience or third-party studio packaging model should work once
  it leaves MVP scope.
- Which integration tests the test phase should add once AW-250 through AW-254
  land.

---

# Open Questions

- Should the skill grow an explicit promotion sub-command in the helper script
  once the lifecycle and arc-binding flow is exercised by a real production game?
