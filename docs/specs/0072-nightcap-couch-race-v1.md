# Nightcap Couch Race v1 — Parent Spec

**Status**: Approved

**Author**: Claude (founder-directed design session) | **Date**: 2026-07-15

---

# References

- Related ADRs: `docs/decisions/0013-nightcap-couch-race-v1-launch-target.md` (charter), `docs/decisions/0010-nightcap-gameplay-pivots-post-playtest.md` (origin), ADR-0003 (web runtime), ADR-0009 (mini-game boundary)
- Architecture sections: `docs/architecture/03-arc-execution.md`, `04-knowledge-graph.md`, `07-character-behavior.md`, `08-event-system.md`
- Related specs: 0071 `docs/specs/0071-live-loop-ai-character-dialogue.md` (live-loop AI character dialogue — direct dependency for AW-283; introduced by PR #225, not yet on main at time of writing — merge PR #225 before starting AW-283), 0066 (continuity evals), 0069 (visual design system), 0068 (quality bar)
- PRD sections: `docs/prd/03-scope.md` (amended MVP definition)
- Story bible: `docs/story-bibles/nightcap-couch-race.md` (canonical experience definition)
- Design record: `docs/superpowers/specs/2026-07-15-nightcap-couch-race-design.md`

---

# Overview

Defines the v1 Couch Race experience: a 2–8 player, 20–40 minute, six-beat competitive-investigator arc where all players race to solve a murder committed by an AI suspect, played on a TV shared display plus phones. Parent spec for epic M5-I; child tasks AW-281–AW-286 carry implementation detail.

---

# In Scope

- Couch Race ArcDefinition (six beats) and deterministic case generation (AW-281)
- Interrogation platform capability: rounds, deterministic question-intent menus, token scarcity (AW-282)
- Knowledge-gated suspect answers, claim/provenance ledger, deterministic contradiction detection (AW-283)
- Race scoring, accusation state, lockout, Last Call endgame, superlatives (AW-284)
- TV and phone rendering on the existing web runtime with extended privacy matrix (AW-285)
- Rehearsal 1 retarget and narrative-task (AW-276–280) beat alignment (AW-286)

# Out of Scope

- Free-text or voice question input (open question)
- Teams and co-op competition-dial positions (configurable structure only; implementations deferred)
- Imposter Variant (killer-among-players) work of any kind
- Victim interrogation (séance mechanic — open question)
- Tier 2 art/animation/sound beyond spec 0069 sequences (M5-G)
- Continuity/recap features (Nightcap Continuity stays v1.1 per D-051)
- Pricing implementation beyond existing per-session cost tracking

---

# Acceptance Criteria

- [ ] Headless harness completes full six-beat sessions at player counts 2 and 8; deterministic replay reproduces case and scores under a fixed seed.
- [ ] Suspect answers pass the AW-272 eval batch with zero knowledge leaks on clean seeds; seeded lies are catchable and false flags reject deterministically.
- [ ] All session end paths reachable and tested (first-correct + table lock-in; countdown expiry; early all-locked).
- [ ] Real-device thin slice playable via local tunnel: join under 30s, extended privacy matrix passes, interrogation p95 latency recorded.
- [ ] Per-session cost telemetry captures interrogation generation spend; founder can read per-case cost.
- [ ] Rehearsal operations docs updated; founder rehearsal executed with blocker log.

---

# Case Resolution Architecture

Deterministic case resolution ships in `engine/case/` (arc-agnostic
resolver interface, `ResolvedCase` domain models) with Nightcap-
specific case content in `nightcap/case_skeletons/` (3 authored
skeletons: locked-room poisoning, alibi-collapse strangulation,
pre-conspiracy fall) and `nightcap/case_taxonomy/` (motive / method /
evidence / lie-topic / cast-pool tables). The resolver asserts two
invariants at case-close:

- **Solvability** — genuine clue chain uniquely identifies the culprit.
- **Lie falsifiability** — every authorized falsehood is contradicted
  by at least one clue in the resolved distribution.

Proof stack (Level 3, per the design memo):

- Runtime invariant assertions in the resolver
  (`engine/case/invariants.py`).
- 1000-seed property sweep per skeleton (3000 cases total),
  including explicit skeleton-coverage assertions
  (`engine/tests/test_case_property_sweep.py`).
- Synthetic-detective solver (`engine/case/solver.py`), verified to
  win over 300 seeds in CI (`engine/tests/test_case_solver.py`).

The resolver is wired into the headless harness at the introduction
beat (`engine/harness/runner.py`), branching on
`ArcDefinition.play_mode == PlayMode.detective_race`. The existing
Imposter-Variant participant-killer assignment path is unchanged for
`play_mode == PlayMode.imposter` arcs.

Cast size scales with player count (`nightcap/case_resolution_config.json`):
2-4 players → 4 suspects, 5-6 → 5 suspects, 7-8 → 6 suspects. A
skeleton may override via `cast_size_override`.

See:
- Design memo: `docs/superpowers/specs/2026-07-17-aw-281-case-resolution-design.md`
- Implementation plan: `docs/superpowers/plans/2026-07-17-aw-281-couch-race-arc-and-case-generation.md`
- Module README: `engine/case/README.md`
- Skeleton content: `nightcap/case_skeletons/README.md`
- Taxonomy content: `nightcap/case_taxonomy/README.md`

---

# Test Plan

- Unit: arc transitions, case-resolution invariants (lie falsifiability, clue-chain sufficiency), token accounting, scoring paths, contradiction determinism.
- Integration: full API session loop with interrogation rounds; SSE audience filtering for tells and private evidence.
- Evals: AW-272 batch over ≥10 synthetic Couch Race sessions.
- Manual: real-device rehearsal per AW-286.

---

# Risks and Unknowns

**Risks**:
- Generated-case fairness inconsistency: players lose trust if a case is unsolvable or a lie uncatchable. Mitigation: resolution-time validation invariants + AW-272 gate.
- Suspect-answer latency breaks the TV moment. Mitigation: fast-tier routing, prompt-cached case context, measured p95 budget.
- Intent menus feel constraining. Mitigation: evidence-unlocked intents widen the space; free-text logged as follow-on.

**Unknowns**:
- Optimal question-token economy per beat (tune in rehearsal).
- Whether contradiction-flagging needs a cooldown beyond the false-flag penalty.

---

# Open Questions

Tracked in `docs/product/open-questions-log.csv`: product name; distribution channel; free-text interrogation timing; victim interrogatability.
