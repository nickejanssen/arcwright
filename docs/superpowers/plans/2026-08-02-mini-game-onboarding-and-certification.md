# Mini-game Onboarding and Certification Implementation Plan

> **For Codex:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to execute
> this plan task by task. Do not begin without separate founder approval.

**Goal:** Turn the existing mini-game skill, helper, template, loader, renderer
kit, and CI checks into one coherent path from prototype import to certified
deployment.

**Architecture:** Extend existing machinery. Do not create a second CLI,
registry, validator, renderer kit, or skill. Automated certification proves
contract readiness; founder review and rehearsals prove gameplay and visual
quality.

**Required approved spec:** docs/specs/0080-mini-game-onboarding-preview-and-certification.md

---

## Task 1: Preflight and Baseline

Execute the program mainline safety gate. Confirm contracts and adapters have
passed their checkpoint. Run:

    python docs/skills/arcwright-minigame/scripts/minigame_tool.py validate nightcap/mini_games
    python -m pytest engine/tests/test_mini_game_models.py -q
    npm --prefix nightcap-web test

Pause for implementation approval.

## Task 2: Correct the Existing Authoring Contract

**Files:**

- Modify: docs/skills/arcwright-minigame/SKILL.md
- Modify: .agents/skills/arcwright-minigame/SKILL.md only if launcher metadata changes
- Modify: docs/conventions/mini-game-authoring.md
- Modify: docs/agents/USAGE.md
- Modify: README.md
- Modify: docs/architecture/09-developer-api.md

Write documentation checks or targeted assertions first where the repo supports
them. Correct:

- stale claims that AW-250 through AW-254 are unbuilt;
- the nonexistent engine/mini_games/schemas.py reference;
- universal Python simulation language, replacing it with adapter-aware rules;
- lifecycle promotion being treated as certification;
- missing mini-game skill discovery;
- stale API and SDK claims.

Preserve thin launchers and one canonical skill.

Verify:

    rg -n "AW-250.*unbuilt|engine/mini_games/schemas.py" docs .agents README.md
    git diff --check

Commit:

    git commit -m "docs(arc): update minigame onboarding contract"

## Task 3: Extend the Single Helper Tool

**Files:**

- Modify: docs/skills/arcwright-minigame/scripts/minigame_tool.py
- Create: engine/tests/test_mini_game_tool.py
- Modify: nightcap/mini_games/_template/manifest.json
- Modify: nightcap/mini_games/_template/definitions/0.1.0.json
- Create: nightcap/mini_games/_template/client/renderer.ts
- Modify: nightcap/mini_games/_template/README.md

Write failing command tests for:

- scaffold package;
- scaffold experience registration;
- scaffold story opportunity;
- validate exact version;
- validate package integrity digest and retirement behavior;
- validate adapter support;
- validate trusted-host capability without issuing public credentials;
- validate player range and fallback;
- validate consequence mappings;
- validate theme and renderer declarations;
- validate public-safe context, telemetry, safety, and generation budgets;
- reject active but incomplete packages;
- report required human gates.

Implement subcommands inside the existing helper. Do not duplicate Pydantic
validation rules in the CLI.

Verify and commit:

    python -m pytest engine/tests/test_mini_game_tool.py engine/tests/test_mini_game_models.py -q
    git commit -m "feat(arc): extend minigame authoring tool"

## Task 4: Make Package Discovery Experience-aware

**Files:**

- Modify: nightcap-web/scripts/discover-mini-games.mjs
- Modify: nightcap-web/tests/mini-game-registry.test.ts
- Modify: nightcap-web/tests/mini-game-asset-route.test.ts
- Modify: nightcap-web/src/mini-games/registry-bindings.ts

Write failing tests proving:

- experience root is an input;
- fixtures are excluded from production by default;
- lifecycle is enforced;
- active packages without renderers fail;
- exact package version is bundled;
- duplicate IDs and version drift fail.

Implement parameterized discovery. Keep Nightcap as the first consumer, not a
hardcoded platform assumption.

Verify and commit:

    npm --prefix nightcap-web test
    git commit -m "fix(nightcap): validate minigame discovery"

## Task 5: Add Local Preview

**Files:**

- Modify: docs/skills/arcwright-minigame/scripts/minigame_tool.py
- Create: nightcap-web/src/mini-games/preview.ts
- Create: nightcap-web/tests/mini-game-preview.test.ts
- Modify: nightcap-web/src/mini-games/stage.ts

Write tests for:

- phone, shared-display, and host projection;
- host-authoritative launch payload;
- theme and accessibility variants;
- active, timeout, completed, error, and reconnect states;
- no private payload on unauthorized surfaces;
- no production session or external model call.

Implement a deterministic fixture-driven preview. Preview must not pretend to
be a real gameplay or device acceptance test.

Verify and commit:

    npm --prefix nightcap-web test
    npm --prefix nightcap-web run typecheck
    git commit -m "feat(nightcap): preview minigame packages"

## Task 6: Add Certification Report

**Files:**

- Modify: docs/skills/arcwright-minigame/scripts/minigame_tool.py
- Create: engine/mini_games/certification.py
- Create: engine/tests/test_mini_game_certification.py
- Create: docs/specs/schemas/mini-game-readiness-report.schema.json

Write failing tests for report fields and blocking rules:

- package, registration, opportunity, adapter, and result contract;
- exact-version delivery;
- package integrity, retirement, rollback, and resume compatibility;
- deterministic replay;
- completion, timeout, cancellation, and fallback;
- consequence idempotency;
- trusted-host authority and forged-result rejection when applicable;
- privacy and reconnect;
- public-safe knowledge projection and content-safety coverage;
- privacy-safe lifecycle telemetry;
- generation cost, latency, retry, caching, and fallback budgets when
  applicable;
- accessibility and performance;
- supported player counts;
- required creative artifact approval;
- required real-device and real-human evidence;
- lifecycle promotion recommendation.

Automated checks must emit Not Run for human gates, never Passed.
Certification evidence does not replace production telemetry.

Verify and commit:

    python -m pytest engine/tests/test_mini_game_certification.py -q
    git commit -m "feat(arc): certify minigame readiness"

## Task 7: Add Command Wrappers and CI

**Files:**

- Modify: Makefile
- Modify: make.cmd
- Modify: .github/workflows/ci.yml

Add wrappers around the one helper for scaffold, preview, validate, and certify.
Add CI jobs for:

- engine and API mini-game tests;
- production package discovery;
- renderer builds;
- readiness schema validation;
- active-package certification blockers.

Do not add dependencies without explicit approval.

Verify CI commands locally, run git diff --check, and commit:

    git commit -m "test(arc): enforce minigame certification"

## Task 8: Run a Synthetic Developer Onboarding

**Files:**

- Create: docs/examples/mini-games/synthetic-host-game
- Create: docs/guides/mini-game-getting-started.md
- Create: docs/roadmap/operations/mini-game-onboarding-walkthrough.md

Use the tool exactly as a new developer would:

1. import or scaffold;
2. register;
3. author opportunity;
4. choose host_authoritative;
5. preview;
6. validate;
7. simulate;
8. certify.

Record elapsed steps, confusion, missing guidance, and resulting report. Fix
only defects inside this plan's scope.

The walkthrough validates an internal protocol and developer workflow. Do not
publish public credentials, engine-specific SDKs, a marketplace, billing, or a
multi-tenant package trust system in this plan.

## Task 9: Reconcile and Pause

Run all focused checks, update spec 0080, the program plan, roadmap issue, and
GitHub tracker with exact evidence. Request review. Pause before Nightcap
package migration.
