# Nightcap External Playtest Harness

> Current version: v2.2
> Last updated: 2026-08-28
> Status: In Progress — representative instrument implemented on PR #299, pending integration/live verification
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
- [ ] Dependency-free playtest runtime and fixture tests pass on the final branch head.
- [ ] Repository CI, CodeQL, and roadmap verification pass on the final branch head.
- [ ] Jotform hidden telemetry additions and post-submit reveal redirect are confirmed after the edit completes.
- [ ] Final merged GitHub Pages deployment is live-smoke-tested.

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
