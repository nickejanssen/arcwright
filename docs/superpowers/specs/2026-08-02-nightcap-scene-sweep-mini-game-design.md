# Nightcap "Scene Sweep" Hidden-Object Mini-Game Design

> Current version: v0.1
> Last updated: 2026-08-02
> Status: Founder-approved design (brainstorming session, 2026-08-02)
> Canonical path: docs/superpowers/specs/2026-08-02-nightcap-scene-sweep-mini-game-design.md

**Author**: Claude, founder-directed design session

## References

- [AW-249 Mini-game authoring foundation](../../specs/0046-aw-249-nightcap-mini-game-authoring-foundation.md)
- [AW-250 Mini-game content resolution and safety](../../specs/0047-aw-250-mini-game-content-resolution-and-safety.md)
- [AW-251 Mini-game runtime persistence and clue gating](../../specs/0048-aw-251-mini-game-runtime-persistence-and-clue-gating.md)
- [0068 Game experience quality bar](../../specs/0068-game-experience-quality-bar.md)
- [0069 Nightcap visual design system](../../specs/0069-nightcap-visual-design-system.md)
- [0061 Tell Me Something True (schema and pattern precedent)](../../specs/0061-aw-258-tell-me-something-true.md)
- [Mini-game runtime boundary ADR](../../decisions/0009-mini-game-runtime-boundary.md)
- [Nightcap murder mystery story bible](../../story-bibles/nightcap-murder-mystery.md)
- [AW-288 Couch Race mini-game beat coverage](../../roadmap/tasks/AW-288-couch-race-mini-game-beat-coverage-and-tmst-acceleration.md) (beat-placement precedent, not binding on this spec)
- Existing packages for pattern precedent: `nightcap/mini_games/crime-scene-smash/`, `nightcap/mini_games/evidence-locker-402/`, `nightcap/mini_games/tell-me-something-true/`
- Existing engine code read for feasibility: `engine/mini_games/models.py`, `engine/mini_games/runtime.py`, `engine/mini_games/plugins/_social_truth_bluff.py`

## Overview

Scene Sweep is a new Nightcap mini-game: a phone-and-shared-display hidden-object hunt built around a real investigation. Players independently pan around a wide illustrated scene on their own phone, tapping objects to claim them, while the shared display shows the entire scene at once with everyone's claims appearing live and unlabeled. Exactly one object on the board is the real piece of evidence; the rest are decoys that look and feel identical when claimed. The truth is withheld until a single staged reveal at the end of the round.

This is a fourth mechanic type alongside the three that already exist (`match-3-clue-race`, `evidence-locker-breach`, `social-truth-bluff`), fitting the same package schema (AW-249), the same runtime lifecycle (AW-251), and the same stateful-plugin pattern Tell Me Something True already proved out. No engine capability is new; this spec is a new mechanic plugin plus new authored/generated content within the existing platform.

## Locked design decisions

These were converged on interactively (mockups + confirmed choices) during the 2026-08-02 brainstorming session and are not open questions:

1. **Search style**: structured hunt with a delight reveal, not a full living Hidden-Folks panorama and not pure spot-the-difference. The object list is a named, authorable set of targets; finding one gets a small reveal moment, not a whole scene of independently-animated micro-interactions.
2. **Surface split**: the shared display always shows the *entire* scene at once (the "answer key" view the room watches) with live, unlabeled claim markers and collective progress. Each phone is an independent pannable viewport into the *same coordinate space*, with a minimap showing the player's current position in the full scene, plus a text list of object names with checkmarks as things get found by anyone.
3. **Claim rule**: race-to-claim. Whoever taps an object first claims it; it's gone for everyone else. This reuses Crime Scene Smash's existing claim-and-broadcast pattern.
4. **Art strategy — three-layer split**:
   - **Backgrounds** are pre-produced, reusable *set pieces* per theme (a small library of rooms, e.g. "the study," "the kitchen," "the garden"), commissioned once per theme and mixed/reused across sessions rather than one bespoke scene per session.
   - **Objects** are a reusable library of investigative archetype roles (see below), each needing one small icon-scale asset *per theme* — cheap relative to background art, decoupled from full-scene illustration cost.
   - **Flavor** (what the real object specifically *is* this session, its reveal quip, the clue text) is generated per session within the same hybrid `authored_content` / `generation_constraints` pattern Tell Me Something True already uses. The AI never decides scene layout, object positions, or whether the scene is solvable — that stays authored and deterministic, per the platform's human-arc-primacy principle.
5. **Object roles are investigative archetypes, not literal props.** The phone's list shows roles like "The Murder Weapon" or "The Motive," not prop names — the specific object behind each role is theme-and-session-specific and generated. Confirmed archetype pool (10 candidates; launch pool trims to what's needed per session, see Object Model below): The Murder Weapon, The Motive, The Alibi Breaker, The Forgery, The Struggle, The Secret Correspondence, The Missing Piece, The Witness's Trace, The Method, The Last Words.
6. **Single hidden real object, revealed only at the end.** Exactly one object on the board is genuine each round; the rest are decoys drawn from the same archetype pool. All claims look and feel identical during play — no immediate "you found the real one" signal. The truth surfaces once, in a staged shared-display moment at the end of the round (spec 0068's "spectacle resolution: results land on the shared display as a moment, not dumped").
7. **The round never ends early.** Claiming the real object does not finalize the run. The round always runs to the full deadline or until every object on the board has been claimed, whichever comes first — nobody's search gets cut short by someone else's early find.
8. **Clue model**: the real object's discovery gates one clue for the room (mirrors Evidence Locker's single-success-condition pattern), not a per-object distinct-clue model and not a multi-object pooled-threshold model. If the real object is never claimed before the deadline, the existing `DelayedClueFallback` pattern releases a reduced clue instead.
9. **Round ceiling**: 90-120 seconds, matching spec 0068's existing mini-game duration standard. No documented exception needed.
10. **Difficulty**: scales with player count only (more players -> more decoys -> a bigger scene to search). No separate difficulty tiers (no Evidence Locker-style routine/pressure/redline modes) for v1 of this game.
11. **Fairness (P4) is knowingly not enforced.** Spec 0068's pillar P4 ("every player gets >=1 private moment that only they could act on") is not specifically guaranteed by this design — a fast player can claim more objects than a slow one. This is an explicit founder decision, not an oversight: the shared spectacle of the board filling up live is the intended fun, not a guarantee of personal claims. Recorded here so a future reader does not mistake this for a missed requirement.
12. **Beat/arc placement is out of scope for this package**, consistent with AW-249's own boundary. Story bible beat B4 ("The Dig") is a plausible candidate for whoever later binds this into an arc, but that decision belongs to a downstream binding task (the pattern AW-254 and AW-288 already followed for other games), not to this design.

## Package identity

| Field | Value |
|---|---|
| `game_id` | `scene-sweep` (working title; trivially renamed at authoring time) |
| `title` | "Scene Sweep" |
| `mechanic_type` | `evidence-search-race` (new; registered in the engine's closed `MechanicRegistry` alongside the three existing types) |
| `participation_mode` | `individual` (each player searches on their own phone, same as Crime Scene Smash) |
| `content_mode` | `hybrid` |
| `min_players` / `max_players` | 4 / 8, matching the platform's existing floor and the other three shipped games |
| `duration_seconds` | 105 (midpoint of the 90-120s ceiling; tunable within that band during implementation) |

## Object model

**Archetype pool (authored, up to 10):** The Murder Weapon, The Motive, The Alibi Breaker, The Forgery, The Struggle, The Secret Correspondence, The Missing Piece, The Witness's Trace, The Method, The Last Words.

**Per-round selection:** each round draws a subset from the pool sized to the player count (see table below), replay variance comes from *which* subset gets drawn and *which one* is designated real, the same "replay_variance" authoring pattern Crime Scene Smash and Tell Me Something True already use (board seed / fact category rotation).

**Starting object-count estimate by player count** (playtest-calibration estimate, not final — same status TMST's own `duration_seconds` carries in its definition today, to be recalibrated after a real session):

| Players | Total objects on board | Of which real |
|---|---|---|
| 4 | 5 | 1 |
| 5 | 6 | 1 |
| 6 | 7 | 1 |
| 7 | 8 | 1 |
| 8 | 8 | 1 |

**Per-theme art requirement**: each archetype in the active launch pool needs one small icon-scale asset per launch theme (bounded matrix: archetypes x launch themes), independent of background art. This is a follow-on art-production task routed through the visual design system (spec 0069) and the founder-approved art direction brief (AW-267) — this spec defines the requirement, it does not produce the art.

## Round flow and runtime behavior

1. **`create_run`**: same as every mechanic — validates `mechanic_type` against the closed registry, validates behavioral outputs, sets the deadline from `duration_seconds`.
2. **`start_run` / `initialize_state`** (new `StatefulMechanicPlugin.initialize_state`): selects the round's object subset from the resolved content, designates one as real (deterministically seeded, never by a model call), and publishes the opening scene state (object positions, archetype labels) to all surfaces. No player yet knows which object is real.
3. **`on_submission`** (claim attempt): payload identifies an `object_id` and a tap position. The plugin checks `state.claimed_object_ids` (tracked in `MiniGameRun.clue_unlock_record["runtime_state"]`, the same slot TMST's plugin already uses); if the object is already claimed, the submission is rejected with a `rejection_reason` (idempotent, matches the platform's existing submission-acceptance contract). If not yet claimed, the object is marked claimed for that player, a `MechanicEventDirective` broadcasts the claim (audience: `all`) with the object's *position* but not its real/decoy status, and a private acknowledgement confirms the claim to the tapping player.
4. **`is_threshold_met`**: true once every object on the board has been claimed (natural exhaustion); otherwise false until the deadline. There is no early-finalize path tied to the real object specifically — this directly implements Locked Decision #7.
5. **`on_deadline_expired`**: standard timeout path, same as the other three games.
6. **`score` / finalize**: examines the accepted submissions; if the real `object_id` is among them, the outcome is `success` and the finder's participant is recorded (behavioral output only, not a privileged knowledge grant); otherwise `fallback`. The existing `_finalize_run` machinery in `engine/mini_games/runtime.py` is unchanged — it already handles clue extraction by `ClueVariant` (full on success, reduced on fallback via `DelayedClueFallback`), mandatory `assert_knowledge` for every eligible participant, and the private-delivery-to-all-participants pattern. This plugin only needs to produce the right `outcome` dict; no runtime changes are needed.
7. **Staged reveal**: the `mini_game_finalized` event (already emitted to `AudienceTarget.all`) carries the narrator's reveal line — which archetype was real, who found it (success case) or that time ran out (fallback case) — as its payload, giving the shared display its one dramatic moment per spec 0068's "spectacle resolution" standard.

## Content generation and clue integration

- `authored_content` carries: background asset references (the room library), the full archetype-role catalog with per-background hitbox/position authoring, the claim mechanic description, surface contracts per surface (phone/shared_display/host, mirroring TMST's existing `surface_contract` shape), and the `fallback_contract`.
- `generation_constraints` governs what gets generated per session: which archetype is designated real *must resolve from that session's actual case data* (the arc's already-generated killer, weapon, motive, etc. — AW-250's content-resolution layer), never invented independently by the mini-game. This is the same non-negotiable every existing hybrid-content mini-game already follows: the model dresses up resolved state, it never decides state. Freely generated within that boundary: the specific in-fiction identity of each object per theme (e.g. "letter opener" vs "laser scalpel" for The Murder Weapon), decoy reveal quips, and narrator intro/reveal lines per theme (diegetic-wrapper pattern, same shape as TMST's `diegetic_wrappers`).
- Clue delivery, knowledge-graph assertion, and the reduced-clue fallback reuse `engine/mini_games/runtime.py` unchanged, as described above.

## Behavioral outputs

| Key | Scope | Type | Derived |
|---|---|---|---|
| `completion-time-ms` | participant | integer | false |
| `decoys-claimed` | participant | integer | false |
| `real-object-claimed` | run | boolean | false |

Per the platform's v1 architecture constraint, these are session-scoped observations only and do not feed killer assignment (unchanged from every other shipped mini-game).

## Performance and quality-bar acceptance criteria

Folded in directly as acceptance criteria (not left implicit) to answer "how do we know this is world-class, performant, and fair to the story" without more design-phase discussion:

- Local input feedback (tap response, claim acknowledgement) renders in under ~100ms per spec 0068's mini-game feel standard, instrumented via the mini-game kit's existing `reportPerf()` hook.
- An explicit asset-size budget is defined for the pannable background image before implementation begins (panning a large image on a phone is the one place this game could feel janky if unbudgeted).
- Generation constraints are verified in tests to reference real session case data for the "which archetype is real" decision, never generic filler text.
- Concurrent-tap arbitration is tested directly: two near-simultaneous claims on the same `object_id` must resolve to exactly one accepted submission.
- A headless harness run exercises both the success path (real object claimed before deadline) and the fallback path (deadline expires first) at both 4 and 8 players.
- Backgrounds and archetype icon sets are flagged as a follow-on art-production task through spec 0069 / AW-267, not produced by this spec.

## Testing strategy

- Unit tests on the new `evidence-search-race` plugin: payload validation, claim arbitration (double-claim rejection), `is_threshold_met` (board exhaustion vs. deadline), `score` outcome correctness for both success and fallback.
- Schema tests: a template/fixture package under `nightcap/mini_games/` validates against AW-249's `MiniGameManifest` / `MiniGameDefinition` models, same as the three existing games.
- Runtime integration tests reusing the existing `MiniGameRuntime` test harness (create_run -> start_run -> concurrent submit_action -> finalize), asserting `assert_knowledge` fires for every eligible participant exactly once per unlocked clue.
- Headless multi-player harness run at 4 and 8 players, both outcome paths.
- No new API, SDK, or web-rendering test surface is defined by this spec — those land in the implementation plan as their own testable units (new renderer for the pan/zoom + minimap phone surface, new shared-display component for the full-scene view and staged reveal), following the same web-kit contracts (`MiniGameRenderer`, `SurfaceHandler`) Tell Me Something True's renderer already uses.

## Out of scope

- Runtime/engine capability changes: none required. This spec is a new plugin and new content within the existing `MechanicRegistry`, `MiniGameRuntime`, and package schema.
- Difficulty tiers (explicitly decided against for v1, see Locked Decision #10).
- Arc/beat binding (explicitly out of scope, see Locked Decision #12).
- Final art production (icons and backgrounds) — flagged as follow-on work through the existing visual design system and art direction pipeline, not designed or produced here.
- Killer-assignment integration for behavioral outputs (platform-wide v1.1 concern, not specific to this game).
- Difficulty/pacing tuning beyond the stated starting estimates — explicitly deferred to real playtest data.

## Risks and open questions

**Risks:**

- The starting object-count table is an estimate; if wrong, either the board feels sparse (too easy to stumble onto the real object) or overcrowded on a phone-sized pannable viewport (frustrating to search). Mitigated by treating the numbers as calibration estimates from the start (Locked Decision #10's numbers are explicitly not final) and revisiting after the first real session, the same posture TMST already takes with its own `duration_seconds`.
- Panning performance on lower-end phones is the single largest technical risk to the "performant" bar; the explicit asset-size budget acceptance criterion exists specifically to catch this before it becomes a live-session problem.
- Because P4 is knowingly not enforced (Locked Decision #11), a session with a wide skill/reflex spread among players could make the round feel lopsided. Accepted risk per founder direction, not something this spec attempts to mitigate further.

**Open questions**: none blocking implementation planning. Object-count tuning, exact archetype-pool trim size, and specific theme icon sets are implementation-time and playtest-time decisions, not open design questions.
