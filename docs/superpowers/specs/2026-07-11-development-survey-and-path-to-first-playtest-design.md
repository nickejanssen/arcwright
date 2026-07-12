# Development Survey and Path to First Playtest

> Current version: v1.0
> Last updated: 2026-07-11
> Status: Approved
> Canonical path: docs/superpowers/specs/2026-07-11-development-survey-and-path-to-first-playtest-design.md

## Purpose

Full-repo development survey (health, roadmap position, gaps, cleanup) and the
approved plan for getting Arcwright + Nightcap from "built" to "played by real
humans," staged through cleanup, a one-command local rehearsal, playtest-critical
gaps, cloud deploy, and the M6 qualifying-session chain.

## Survey Findings (2026-07-11)

### Roadmap position

- M1 through M4 are closed on GitHub, including the full M4-E mini-game
  interaction layer.
- M5 is in flight: M5-E (behavior hardening) done; M5-F (Tell Me Something
  True) built end-to-end (AW-262 through AW-265 merged) with only Rehearsal 2
  (AW-266) remaining; M5-A/B/C/D/G/H and AW-269 open.
- **Correction to the record: Rehearsal 1 (AW-259, with AW-231 and AW-254) was
  closed on 2026-06-27 without being executed.** No real-human Nightcap session
  has ever run. The M4 exit gate ("real humans playing end-to-end on real
  devices") has not actually been passed. No filled blocker log exists.

### Why Rehearsal 1 did not happen

The founder runbook (`docs/roadmap/operations/rehearsal-1-runbook.md`) is 415
lines, requires a Cloudflare account, DNS records, a named tunnel, and five
concurrently running terminals. It is not executable by a non-infrastructure
operator working alone. This is the primary blocker to validation and the
anchor of this plan.

### Code health

- Python: 507 tests pass, **6 fail on main**:
  - 5 in `api/tests/test_costs_api.py` (`SessionStateError: Unknown arc:
    'test-arc'`) — an arc-registry validation change broke the cost-summary
    test fixtures.
  - 1 in `api/tests/test_mini_games_api.py`
    (`test_tmst_spotlight_phase_state_is_authorized_for_reconnect`) — the TMST
    reconnect payload returns the player's input submission alongside the
    vote; either a submission-filtering regression or a stale expectation from
    the AW-265 merge. Must be diagnosed, not assumed.
- Ruff lint and format: clean. Routing evals: pass.
- TypeScript: `sdk`, `dashboard`, and `nightcap-web` all typecheck;
  `nightcap-web` 98/98 tests pass.
- ~44k pytest deprecation warnings (httpx TestClient deprecation, asyncio
  policy under Python 3.14). Non-blocking; noisy.

### Gaps and misses

1. **Issue #138 (player drop → AI takeover mid-session)** — architecture
   §5.5 behavior, explicitly a v1 playtest need, unnumbered (AW-NNN) and in no
   epic. A session with one dropout currently has no recovery path.
2. **Issue #137** — hardcoded `"arrival"` fallback beat in
   `engine/session/service.py`; platform-agnosticism violation (same family
   as fixed AW-256).
3. **Task-ID collision** — closed issue #190 was titled "AW-270: Nightcap
   Rehearsal Lobby"; AW-270 now means "Authorial Intent Block" (#202).
4. **Stale status metadata** — roadmap manifest and task files say
   "planned"/"Planned" for long-closed work; GitHub is the only accurate
   tracker.
5. **Stale local branches** — ~10 local branches; most are squash-merged and
   deletable. `docs/cloud-deploy-runbook-expansion` (2026-07-11) holds real
   unmerged runbook work, parked per the ADR-0012 rollout plan.

### Playtest readiness verdict

Not ready today. Ready for Rehearsal 1 after Phases 0–1 below (days of work).
Outside qualifying sessions (M6) unlock after Phases 2–4.

## Decisions Made In This Session

- Rehearsal path: **both, staged** — one-command local rehearsal now to
  unblock Rehearsal 1; cloud deploy (AW-269) before Rehearsal 2 / M6.
- Cleanup: **full cleanup sprint** (tests, branches, statuses, ID collision).
- Deliverables must include a founder operator guide: which sessions to start,
  which skills to run, which commands to type.

## Plan

### Phase 0 — Restore truth (cleanup sprint)

1. Fix the 5 costs-API test failures: update or repair the `test-arc` fixture
   path against the current arc registry so the suite reflects real API
   behavior.
2. Diagnose and fix the TMST reconnect failure: determine whether
   `my_submissions` should exclude input submissions during spotlight phase
   (code fix) or the test expectation is stale (test fix); fix accordingly.
3. Correct the rehearsal record: file a new task (successor to AW-259; new
   AW number, no reuse) stating Rehearsal 1 has not run; reference it from
   AW-259/#176. Update the M4 milestone notes so the exit gate reads
   "pending real-human validation."
4. Sync status metadata: roadmap manifest `status` fields and task-file
   `Status:` headers updated to match GitHub (complete for M1–M4 tasks,
   in-progress/planned for M5/M6).
5. Resolve the AW-270 collision: annotate the manifest and the closed #190
   record so AW-270 unambiguously means Authorial Intent Block.
6. Branch hygiene: delete squash-merged local branches
   (`claude/hungry-pare-0ca5a7`, `claude/thirsty-edison-7eada6`,
   `claude/quirky-poincare-da6f1c`, `pr-205`, `pr-151`,
   `chore/dashboard-build-artifacts`, `task/AW-105-knowledge-graph-api`,
   `task/AW-6-full-alembic-migration`, `docs/aw-254-gate-aw-257-precursor`,
   `docs/m1-epic-e-spec-refinements`) after verifying content is in main;
   open a PR for `docs/cloud-deploy-runbook-expansion`.
7. Optional, low priority: silence the two dominant deprecation-warning
   sources via test configuration.

Exit gate: `pytest engine/tests api/tests tests` fully green; `git branch`
shows only `main` plus intentional work branches; manifest statuses truthful.

### Phase 1 — One-command rehearsal, then run Rehearsal 1

1. **`make rehearsal` orchestration** (new script, e.g.
   `scripts/rehearsal.py` or shell + Make target):
   - Boots Postgres + API via docker compose.
   - Runs `alembic upgrade head`.
   - Builds/starts the Nightcap web experience.
   - Opens a **cloudflared quick tunnel** (`cloudflared tunnel --url`) — no
     account, no DNS, no named tunnel.
   - Health-checks every layer (DB, API, web, tunnel) with clear failure
     messages naming the failed layer and the fix.
   - Prints exactly two URLs: the host/shared-display URL and the player join
     URL, plus the session join code.
   - Companion `make rehearsal-stop` to tear everything down.
2. **One-page runbook** replacing the 415-line procedure: the command, the
   two URLs, what to do during the session (host beats, mini-game moments,
   accusation/reveal), and a wrap section that captures the blocker log into
   `docs/roadmap/operations/` (from the existing template).
3. **Synthetic dry run**: drive a full session through the REST-backed
   session loop (AW-255 harness) against the `make rehearsal` stack to prove
   the exact stack humans will touch.
4. **Founder solo smoke test**: founder + two phone browser tabs, 15 minutes.
5. **Rehearsal 1**: founder + at least 3 invitees, real devices, both
   production mini-games (Crime Scene Smash, Evidence Locker). Blocker log
   filled and committed. The successor rehearsal task closed honestly with
   outcomes recorded.

Exit gate: blocker log committed; M4 exit gate genuinely passed.

### Phase 2 — Playtest-critical gaps

1. Number and implement issue #138 (player drop → AI takeover): host-triggered
   participant conversion endpoint, `is_ai_controlled` flip, behavior engine
   pickup of existing profile and knowledge state, host UI choice
   (convert vs. absent + narrator acknowledgement).
2. Fix issue #137: derive fallback beat from `arc_definition.beats[0].beat_id`
   instead of the hardcoded `"arrival"`.
3. Triage Rehearsal 1 blocker log into M5 tasks; schedule fixes ahead of
   Rehearsal 2.

### Phase 3 — Cloud deploy (AW-269), then Rehearsal 2

1. Merge the parked cloud-deploy runbook expansion; finish deploy automation
   (Cloudflare Workers web runtime per ADR-0003/D-067, GCP backend, Firebase
   auth, secrets handling per the Hard Rules — founder approval required for
   anything touching credentials).
2. Deploy; re-run the synthetic dry run against cloud infrastructure.
3. Run Rehearsal 2 (AW-266): promote TMST to active, real-human four-phase
   session on cloud infra, blocker log again.

### Phase 4 — M6 gate chain (outside playtests)

In dependency order: AW-232/233 (adversarial safety playtest + remediation),
AW-234 (gross margin by player count), AW-236–239 (live inspection views),
AW-272 (continuity/coherence eval suite), M5-G (visual identity, Tier 2
polish), AW-235 (second arc schema design). Then M6-A (playtest runbook,
instrumentation checklist, founder final rehearsal AW-242) and AW-243 (five
outside qualifying sessions) feeding AW-244 (H1 proof analysis).

## Founder Operator Guide (your next steps)

Each phase maps to a session you start and a skill you invoke. One phase per
session; review the PR each produces.

1. **Phase 0 session**: start a new Claude Code session in this repo and say
   "Execute Phase 0 of docs/superpowers/specs/2026-07-11-development-survey-and-path-to-first-playtest-design.md
   using the implementation plan" (the plan file pairs with this spec). The
   session uses `/superpowers-extended-cc:execute-plan`.
2. **Phase 1 session**: same pattern for Phase 1. When it completes, you run
   `make rehearsal` yourself, do the 15-minute solo smoke test, then schedule
   real humans.
3. **Rehearsal 1**: follow the new one-page runbook. Capture blockers as you
   go (the wrap section tells you where).
4. **Phase 2 session**: paste the blocker log in and ask for triage + the #138
   / #137 implementation via `/implement` (one task per session).
5. **Phase 3 session**: cloud deploy. This touches secrets — the session will
   stop and ask you for approvals; that is expected.
6. **Rehearsal 2, then Phase 4**: work the M6 gate chain one task at a time
   with `/implement`, reviewed with `/review-pr`.

## Error Handling / Risks

- The TMST reconnect failure may be a product bug shipped in AW-265; Phase 0
  must diagnose before choosing code-fix vs. test-fix.
- `make rehearsal` must fail loudly per layer; a silent partial boot would
  recreate the five-terminal debugging problem it exists to remove.
- Cloudflared quick tunnels are ephemeral and unauthenticated by design;
  acceptable for Rehearsal 1 (trusted invitees), not for M6 outside sessions
  — those run on the Phase 3 cloud deployment.
- Reusing AW numbers is prohibited going forward (AW-270 collision is the
  cautionary case); new tasks take the next free number.

## Testing

- Phase 0: full Python suite green is the acceptance criterion itself.
- Phase 1: the synthetic REST-loop dry run is the automated acceptance test
  for the rehearsal stack; script health checks are manually verified once by
  the founder smoke test.
- Phase 2: unit tests written with the #138/#137 changes per
  `docs/conventions/testing.md`.

## References

- `docs/roadmap/index.json` (manifest), `docs/roadmap/operations/rehearsal-1-runbook.md`
- Issues #137, #138, #176 (AW-259), #183 (AW-266), #188 (AW-269)
- ADR-0003 / D-067 (Cloudflare runtime), D-065 (local-tunnel Rehearsal 1),
  ADR-0012 (narrative fidelity), D-051 (Continuity v1.1 boundary)
