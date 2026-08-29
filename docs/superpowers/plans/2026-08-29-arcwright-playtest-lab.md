# Arcwright Playtest Lab Implementation Plan

> Execute this plan with the superpowers:subagent-driven-development skill when the founder selects that execution mode. The plan is implementation-ready for inline execution as well.

## Goal

Deliver Option C: a minimal Arcwright homepage with Playtests prominent, while preserving immutable versioned test URLs and leaving room for additional games and concurrent experiments.

## Architecture

The repository remains the source of truth for catalog metadata, playable artifacts, research-instrument mappings, and operating rules. A deterministic Python build composes a static Pages site. The browser harness remains a non-canon test fixture. Jotform receives research answers plus harness telemetry through a versioned field map. A thin Playtest Steward CLI routes human or agent requests to explicit, reviewable operations.

## Tech stack

- Python 3.11 standard library for catalog validation, site generation, and the Steward CLI.
- Existing browser harness JavaScript and Node test runner for telemetry URL behavior.
- GitHub Pages Actions for static publishing.
- Jotform as the external research instrument; no secrets or credentials in the repository.

## Specifications and constraints

- Design document: docs/superpowers/specs/2026-08-29-arcwright-playtest-lab-design.md.
- Harness spec: docs/specs/nightcap-external-playtest-harness.md.
- Canonical docs: docs/README.md, relevant PRD and architecture sections, and docs/story-bibles/nightcap-couch-race.md.
- Never alter production engine behavior for this static test-lab task.
- Never silently rewrite an archived test or its instrument mapping.
- Keep provider and model names out of new files.
- Do not submit a real Jotform response without explicit action-time confirmation.

## Task 0: establish the implementation baseline

Files: Git state only.

1. Use the Codex app to create or select a branch named codex/playtest-lab from the merged remote main commit containing PR #299 (ebe944a7...). The current worktree is detached and behind that commit, so do not implement from its stale checkout.
2. Preserve design commit abf8d82 by cherry-picking it if it is not already reachable from the branch.
3. Confirm the merged harness files, workflow, and tests are present; confirm no .claude, .codex, or .cursor files are staged.
4. Record the exact base SHA in implementation notes or the PR description.

## Task 1: repair and test the Jotform telemetry contract

Files:

- Modify playtests/nightcap-paper-test-02-v2.2/config.js.
- Modify playtests/nightcap-paper-test-02-v2.2/README.md.
- Add or modify playtests/nightcap-paper-test-02-v2.2/tests/runtime.test.mjs.

Implementation:

1. Add a focused failing test for buildFeedbackUrl() that asserts all 18 telemetry keys map to the Jotform parameter names observed from the live form.
2. Map the 14 generated legacy textbox fields exactly:

   prototype_version -> q13_textbox11
   run_id -> q14_textbox12
   started_at -> q15_textbox13
   completed_at -> q16_textbox14
   duration_seconds -> q17_textbox15
   action_sequence -> q18_textbox16
   investigation_branches -> q19_textbox17
   discoveries -> q20_textbox18
   pulse_result -> q21_textbox19
   case_commitment -> q22_textbox20
   final_next_interest -> q23_textbox21
   device_class -> q24_textbox22
   browser_class -> q25_textbox23
   completion_status -> q26_textbox24

3. Keep the four newer names unchanged: q28_time_to_first_investigation_seconds, q29_major_investigations, q30_event_sequence, and q31_abandonment_point.
4. Document the generated-field exception and the read-only prefill verification in the harness README.
5. Run the Node runtime and fixture tests. Perform a public-form read-only probe to confirm the hidden controls still exist and are not user-editable. Only after an explicit action-time confirmation, run one controlled submission and verify the received values through the Jotform connector.

Acceptance criteria: the focused test fails before the map change, passes after it, all existing harness tests pass, the mapping is documented, and no unconfirmed external submission occurs.

Commit: fix(playtests): repair Jotform telemetry mapping.

## Task 2: add a manifest-driven playtest catalog

Files:

- Add playtests/catalog.json.
- Add scripts/playtest_catalog.py.
- Add scripts/tests/__init__.py.
- Add scripts/tests/test_playtest_catalog.py.

Implementation:

1. Define a JSON catalog with schema version, generated-at policy, current test references, and one entry for Nightcap Paper Test #2 v2.2.
2. Each entry must include id, game, version, title, summary, status, route, source_dir, instrument_id, instrument_version, and published.
3. Implement load_catalog(path: Path) -> dict, validate_catalog(catalog: dict, repo_root: Path) -> list[str], and current_tests(catalog: dict) -> list[dict].
4. Validate unique IDs, safe relative routes and source paths, semver-like versions, allowed statuses, existing source directories, and no more than one current entry per game.
5. Add tests for valid data, duplicate IDs, missing artifacts, invalid routes, and multiple current entries.

Acceptance criteria: catalog validation is deterministic, reports actionable errors without mutating files, and the current Nightcap entry points to the existing immutable v2.2 artifact.

Commit: feat(playtests): add manifest-driven catalog.

## Task 3: generate the minimal Arcwright Playtest Lab site

Files:

- Add playtests/site/index.html.
- Add playtests/site/nightcap/index.html.
- Add playtests/site/catalog.js.
- Add playtests/site/styles.css.
- Add scripts/build_playtest_site.py.
- Add scripts/tests/test_build_playtest_site.py.
- Modify .github/workflows/nightcap-playtest-pages.yml.

Implementation:

1. Add a failing build test for build_site(manifest_path: Path, template_dir: Path, output_dir: Path, repo_root: Path) -> None.
2. Generate a clean _site output containing:
   - /index.html: minimal Arcwright identity, Playtests as the primary destination, and current tests first.
   - /nightcap/index.html: Nightcap catalog with current and historical entries.
   - /nightcap/paper-test-02/v2.2/: copied immutable harness artifact.
   - /catalog.json or equivalent generated catalog data for future consumers.
3. Use path-safe relative links that work under the repository Pages base path /arcwright/.
4. Preserve the fixture existing reveal behavior and mark it as non-canon.
5. Update the workflow to install Python 3.11, run catalog validation and site tests, build _site, and upload _site rather than a single fixture directory.
6. Keep the site generation static and dependency-free.

Acceptance criteria: local build output contains all required routes, old artifact URLs remain stable, current entries are visibly prioritized, and the workflow validates before deployment.

Commit: feat(playtests): publish manifest-driven pages site.

## Task 4: add Playtest rules and a safe Steward CLI

Files:

- Add playtests/AGENTS.md.
- Add scripts/playtest_tool.py.
- Add scripts/tests/test_playtest_tool.py.

Implementation:

1. Document naming, immutable versioning, archive rules, canon boundaries, telemetry requirements, instrument versioning, deployment checks, and founder approval gates in playtests/AGENTS.md.
2. Implement subcommands list, validate, new, archive, and build, plus --json output and stable exit codes: 0 success, 2 invalid input, 1 operational failure.
3. Make list and validate read-only. Make new create only a scaffold after validating an unused ID and explicit metadata. Make archive require an exact ID and preserve the artifact and history. Make build delegate to the deterministic site builder.
4. Reject attempts to overwrite existing versions, mutate archived entries, add secrets, or add creative content through the CLI.

Acceptance criteria: CLI tests cover happy paths, invalid input, and immutable/archive guards; help text is usable by Codex, Claude, and humans without provider-specific assumptions.

Commit: feat(playtests): add steward catalog tooling.

## Task 5: create model-agnostic Playtest skills and contracts

Files:

- Add docs/skills/arcwright-playtest-steward/SKILL.md.
- Add docs/skills/arcwright-playtest-harness/SKILL.md.
- Add docs/skills/arcwright-playtest-research/SKILL.md.
- Add docs/skills/arcwright-playtest-publishing/SKILL.md.
- Add thin launchers under .agents/skills/ for each canonical skill.
- Add scripts/tests/test_playtest_skill_contract.py.

Implementation:

1. Read and follow the skill-creator instructions before authoring these skills.
2. Keep canonical behavior platform-neutral and launchers thin.
3. Define Steward routing, harness preflight and telemetry checks, research-instrument versioning and evidence capture, and publishing/catalog verification.
4. Require canonical-doc-first routing, explicit approval before external writes, and evidence-backed status reporting.
5. Define the Steward as an organizer and router, not an autonomous creative author. It may create scaffolds and update metadata only through reviewed commands.
6. Add contract tests for required sections, no provider/model literals, and references to the CLI and approval gates.

Acceptance criteria: all skills are discoverable by Codex and Claude, contract tests pass, and instructions do not bypass Arcwright architecture or human approval gates.

Commit: feat(playtests): add model-agnostic steward skills.

## Task 6: reconcile canonical docs and perform verification

Files:

- Modify docs/specs/nightcap-external-playtest-harness.md.
- Modify docs/product/decisions-log.csv using the next unused decision ID after inspection.
- Update docs/decisions/README.md or add an ADR only if the final implementation changes an architectural decision.
- Update docs/roadmap/index.json only if the roadmap verifier requires a durable task-state change.

Implementation:

1. Reconcile harness status and acceptance checks with merged PRs, the deployed Pages URL, and the corrected telemetry map.
2. Record the approved Option C homepage/catalog direction as a durable product decision with references to the design and plan.
3. Run focused Python and Node tests, catalog validation, build verification, and applicable repository lint/type checks.
4. Verify deployed /, /nightcap/, and immutable version route in the browser. Confirm ?reveal=1 remains available for authorized verification.
5. Inspect the live Jotform form and submissions through the connector. Report exactly which telemetry fields were observed and which controlled-run fields were or were not populated.
6. Do not claim real-device readiness from static build or browser checks.

Acceptance criteria: repository checks pass, live routes resolve, docs reflect evidence rather than intention, and the final report separates package validation, deployment verification, connector evidence, and remaining founder/device gates.

Commit: docs(playtests): reconcile Playtest Lab evidence.

## Plan self-review

- Option C is the only homepage scope; later games and concurrent tests are represented through catalog entries and routes.
- Jotform repair precedes new catalog/site behavior and is protected by a failing test plus an action-time confirmation gate.
- No production engine/API modules are changed.
- Every implementation task starts with a focused test or contract check.
- Archived artifacts remain immutable and URLs remain permanent.
- Detached/stale worktree handling is explicit.
- Final completion claims require verification evidence.
