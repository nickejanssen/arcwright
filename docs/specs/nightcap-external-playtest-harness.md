# Nightcap External Playtest Harness

> Current version: v2.2
> Last updated: 2026-08-30
> Status: Branch implementation verified locally; PR #299 baseline deployed; Playtest Lab catalog deployment pending merge to main
> Canonical path: docs/specs/nightcap-external-playtest-harness.md

---

# Overview

Nightcap Paper Test #2 v2.2 is the **Representative Time-to-Fun / Cohesion Test**. It preserves the disposable static external-testing harness while replacing the thin earlier fixture with a materially fuller non-canon microcase, **The Last Toast**.

This spec governs research tooling and the test fixture only. It does not alter the authoritative Nightcap GDD or convert fixture convenience into product rules.

# Infrastructure preserved

- Static HTML/CSS/vanilla JavaScript under `playtests/nightcap-paper-test-02-v2.2/`.
- No framework, build step, backend, database, auth, or new dependency.
- GitHub Pages deployment through the existing workflow.
- Jotform form `262397917027062` as the central research/submission store.
- Anonymous session-scoped run ID and coarse device/browser classification.
- `sessionStorage` for accidental-refresh re-entry.
- Readable URL-prefilled telemetry rather than a new analytics service.

# Current Playtest Lab implementation evidence

The v2.2 fixture shipped to `main` through PR #299, merged on 2026-08-29 as commit `ebe944a7e6ab61c9aeb49e3946f2a6d1b7f07a89`. GitHub reported success for CI, CodeQL, roadmap verification, and the Nightcap Playtest Pages workflow on that merge commit.

The Playtest Lab branch adds the durable catalog, static site builder, safe Steward CLI, and Playtest Lab skills on top of PR #299. Local verification on the branch head confirmed:

- `playtests/catalog.json` validates through `python scripts/playtest_tool.py --json validate`.
- `python -m pytest scripts/tests -q --basetemp .pytest-tmp-task6-scripts` passed all Playtest Lab Python tests.
- `node --test playtests/nightcap-paper-test-02-v2.2/tests/runtime.test.mjs playtests/nightcap-paper-test-02-v2.2/tests/fixture.test.mjs` passed all runtime and fixture tests.
- `python scripts/playtest_tool.py --json build --output _site` generated the homepage, Nightcap catalog page, immutable v2.2 route, and legacy alias locally.
- `python scripts/verify_tasks.py` passed the roadmap verifier.
- `python -m ruff check scripts/playtest_catalog.py scripts/build_playtest_site.py scripts/playtest_tool.py scripts/tests` and `python -m ruff format --check scripts/playtest_catalog.py scripts/build_playtest_site.py scripts/playtest_tool.py scripts/tests` passed.

Live GitHub Pages verification on 2026-08-30 found the deployed root URL reachable, but the new Playtest Lab routes were not yet live because the branch had not been merged to `main` and deployed:

- `https://nickejanssen.github.io/arcwright/`: HTTP 200.
- `https://nickejanssen.github.io/arcwright/?reveal=1`: HTTP 200 for the currently deployed root-hosted PR #299 fixture.
- `https://nickejanssen.github.io/arcwright/nightcap/`: GitHub Pages 404.
- `https://nickejanssen.github.io/arcwright/nightcap/paper-test-02/v2.2/`: GitHub Pages 404.
- `https://nickejanssen.github.io/arcwright/nightcap/paper-test-02/v2.2/?reveal=1`: GitHub Pages 404.

Task 6 review fix round 1 attempted read-only browser verification of the deployed root and root `?reveal=1` routes. The connected browser runtime returned `No browser is available` before navigation, so browser-rendered verification remains pending. The HTTP status evidence above came from read-only network GET checks rather than an interactive browser session.

The local source route still supports the authorized reveal flag through `app.js`, and the local build contains `_site/nightcap/paper-test-02/v2.2/index.html`. The deployed reveal route must be retested after the Playtest Lab branch reaches `main` and the Pages workflow succeeds.

# Approved v2.2 fixture direction

**Fixture:** The Last Toast — NON-CANON TEST FIXTURE.

**Test player model:** one real solo tester plus one visible deterministic authored rival, Rhea Pike. Authored rival behavior is a research proxy for competitive pressure and must not be interpreted as proof of multiplayer behavior.

**Mystery architecture:** simple crime, layered proof. Sebastian Vale is killed by a substituted medication dose before/around the toast; champagne is misdirection rather than an elaborate murder mechanism. The intended solve requires the equivalent of killer + substitution/core-act proof + opportunity/access + a broken account.

**Suspects:** Mara Voss, Dr. Theo Bell, Celeste Vale, and Julian Cross. Each has a concrete suspicious behavior, a credible motive/secret, and information that complicates the obvious interpretation.

# Representative flow

1. **WATCH:** short cinematic opening with four observable irregularities.
2. **HUNT 1:** player follows one thing they actually noticed.
3. **HUNT 2:** the first discovery opens a concrete follow-up question.
4. **Competitive interruption:** Rhea visibly pursues an unchosen lead and reacts to the player's first move.
5. **PLAY:** story-wrapped Effects Tray observation minigame contests first access to Sebastian's effects.
6. **Consequence:** winner gets first access. A loss still leaves redundant proof routes.
7. **REACT / Leverage:** spend one bounded advantage to learn Rhea's direction, or save it for a private Julian follow-up. Rival knowledge does not become owned proof.
8. **HUNT 3:** investigate under the changed competitive state.
9. **Story reaction:** Theo/corridor behavior changes the room and creates new investigative intent.
10. **HUNT 4:** test a claim, route, object, or suspect.
11. **HUNT 5:** one final open investigative commitment.
12. **LAST CALL:** investigation closes; Rhea commits without revealing whether she is correct.
13. **CASE FILE:** select killer, critical act/mechanism proof, opportunity/access proof, and failed statement/cover story using owned evidence where proof ownership matters.
14. **POST-PLAY RESEARCH:** existing Jotform survey receives baseline ratings before the truth is shown.
15. **THE TRUTH:** survey completion redirects back to the static reveal route (`?reveal=1`).

Target runtime is roughly 15–20 minutes for an engaged first-time tester. Experiential completeness is more important than enforcing a timer.

# Evidence principles

- **Equal solvability, unequal information:** Rhea may know something the tester does not own; minigame outcome changes temporary access rather than truth.
- **Redundant truth:** mechanism, access, movement, and contradiction each have multiple proof routes. No single minigame result or mandatory clue is the only path.
- **Knowledge ≠ Proof:** the minigame-loss state explicitly distinguishes seeing Rhea react from owning her evidence.
- **No correctness confirmation:** no suspect is cleared or confirmed and no clue is ranked for importance before the Case File.
- **Player-owned deduction:** discoveries state observations/facts, not the inference the tester should draw.

# Telemetry

Existing telemetry is preserved:

`prototype_version`, `run_id`, `started_at`, `completed_at`, `duration_seconds`, `action_sequence`, `investigation_branches`, `discoveries`, `pulse_result`, `case_commitment`, `final_next_interest`, `device_class`, `browser_class`, `completion_status`.

The representative test adds four lightweight fields:

- `time_to_first_investigation_seconds`
- `major_investigations`
- `event_sequence`
- `abandonment_point`

The event stream records opening completion, five major investigation selections, rival lead, minigame result, Leverage choice, story reaction, Last Call, Case File commitment, and survey handoff without adding research prompts during gameplay.

The corrected Jotform prefill map on the Playtest Lab branch maps the fourteen generated legacy fields to the live form's observed Unique Names:

- `prototype_version` -> `q13_textbox11`
- `run_id` -> `q14_textbox12`
- `started_at` -> `q15_textbox13`
- `completed_at` -> `q16_textbox14`
- `duration_seconds` -> `q17_textbox15`
- `action_sequence` -> `q18_textbox16`
- `investigation_branches` -> `q19_textbox17`
- `discoveries` -> `q20_textbox18`
- `pulse_result` -> `q21_textbox19`
- `case_commitment` -> `q22_textbox20`
- `final_next_interest` -> `q23_textbox21`
- `device_class` -> `q24_textbox22`
- `browser_class` -> `q25_textbox23`
- `completion_status` -> `q26_textbox24`

The four v2.2 fields keep readable parameter names: `q28_time_to_first_investigation_seconds`, `q29_major_investigations`, `q30_event_sequence`, and `q31_abandonment_point`.

Read-only Jotform connector inspection on 2026-08-30 confirmed form `262397917027062` is enabled, titled `Nightcap Paper Test #2 - Post-Play Research`, has 31 questions, and has 2 submissions. The form metadata lists all 18 telemetry labels. Submission analysis found values populated for `time_to_first_investigation_seconds`, `major_investigations`, and `event_sequence`; it found empty values for `prototype_version`, `run_id`, `started_at`, `completed_at`, `duration_seconds`, `action_sequence`, `investigation_branches`, `discoveries`, `pulse_result`, `case_commitment`, `final_next_interest`, `device_class`, `browser_class`, `completion_status`, and `abandonment_point`. No controlled Jotform response was submitted during Task 6, so end-to-end received-value coverage and post-submit redirect behavior remain unconfirmed.

# Re-entry and state

Exact current state is persisted for discoveries, rival/minigame stages, Leverage, five investigation stages, and partial Case File selections. A refresh must not replay or double-count a completed major choice or minigame result.

# Acceptance criteria

- [x] Existing hosting/survey/telemetry architecture preserved.
- [x] Fresh The Last Toast fixture replaces Room With No Door.
- [x] Four meaningful suspects are presented.
- [x] Scene-first observation drives the first investigative act.
- [x] Five major investigation commitments exist.
- [x] Named deterministic rival creates bounded pressure and reacts to player behavior.
- [x] One story-wrapped skill minigame contests temporary first access.
- [x] Losing the minigame preserves viable proof routes.
- [x] One bounded Leverage decision has a real opportunity cost.
- [x] Story reaction reshapes the next investigative decision.
- [x] No explicit theory/research checkpoint occurs before Case File.
- [x] Case File captures killer + mechanism/core proof + access + failed account.
- [x] Baseline survey occurs before truth/reveal.
- [x] Refresh-safe state prevents duplicate major actions/minigame resolution.
- [x] No production Nightcap/engine/API/SDK/dashboard code is modified.
- [x] Dependency-free playtest runtime and fixture tests pass on the Playtest Lab branch head.
- [ ] Repository CI, CodeQL, and roadmap verification pass on the final branch head. Local roadmap verification passed on 2026-08-30, and GitHub CI/CodeQL passed for PR #299, but branch-head CI/CodeQL remains pending until a PR or main run exists for this branch.
- [ ] Jotform hidden telemetry additions and post-submit reveal redirect are confirmed after the edit completes. Connector metadata confirms the 18 labels exist, but the two existing submissions populate only three of the new telemetry fields, and no controlled Task 6 submission was authorized or sent.
- [ ] Final merged GitHub Pages deployment is live-smoke-tested. PR #299's root deployment is live, but the branch's `/nightcap/` and immutable catalog route are not deployed yet.

# QA matrix

The instrument must be exercised across:

- minigame win + Leverage spend;
- minigame win + Leverage save;
- minigame loss + Leverage spend;
- minigame loss + Leverage save;
- Julian investigated early;
- a non-killer/red-herring investigated first;
- a route that reaches Case File without the most direct medication path;
- refresh/re-entry at discovery, minigame consequence, and partial Case File;
- voluntary abandonment;
- mobile-width layout;
- survey handoff and reveal ordering.

Fixture-level automated assertions cover representative suspect count, opening observations, proof redundancy, minigame-loss solvability, red-herring information value, bounded Leverage, and several indirect proof-route combinations.

# Deliberately deferred

Memory Support A/B, advanced Case Board, Heat, full Counterintel, auctions, full Leverage economy, Group Rescue, 2-vs-4 balancing, accessibility minigame filtering, numerical Case Strength, full Postmortem, production AI generation, broad player-count scaling, backend analytics, closed-tab abandonment ingestion, and production multiplayer behavior.

# Remaining research risks

- Authored rival pressure cannot validate actual social multiplayer behavior.
- A static text prototype still understates production cinematic/audio/social presentation.
- Fifteen-to-twenty-minute target runtime is a design estimate until real independent testers establish observed duration.
- Voluntary early exit can be tracked, but silent tab closes cannot be reliably captured without a backend.
- A fuller fixture improves representativeness but does not prove Nightcap is fun; it creates a better instrument for real testers to answer that question.
- Static build checks, local browser-equivalent route inspection, and live Pages GET checks do not establish real-device readiness. Phone, TV, human tester, and post-submit survey evidence remain separate gates.
