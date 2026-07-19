# AW-287 Nightcap Leverage Advantages And Sabotages

**Status**: Approved

**Author**: Arcwright product and engineering | **Date**: 2026-07-18

---

# References

- Related ADRs: `docs/decisions/0015-nightcap-leverage-advantages-sabotages.md`, `docs/decisions/0014-structured-interaction-resolution.md`, `docs/decisions/0008-content-event-type-layering.md`
- Architecture sections: `docs/architecture/03-arc-execution.md`, `docs/architecture/08-event-system.md`, `docs/architecture/11-telemetry.md`
- Related specs: `docs/specs/0072-nightcap-couch-race-v1.md`, `docs/specs/0074-aw282-structured-interaction-loop.md`
- Product and story context: `docs/roadmap/tasks/AW-287-nightcap-leverage-advantages-and-sabotages.md`
- Design record: `docs/product/nightcap-leverage-advantages-sabotages.md`
- Discovery and approvals: `docs/product/aw287-discovery-and-checkpoints.md`, `docs/product/decisions-log.csv` D-075

---

# Overview

AW-287 defines a game-agnostic resource/effect capability: players earn a generic resource balance and spend it on authored interaction modifiers (advantages that sharpen their own play, sabotages that interfere with a rival's) against the interaction runtime AW-282 already built. Nightcap configures this capability as "Leverage" with a six-effect launch set. No game-specific vocabulary appears in engine code.

---

# In Scope

- Pydantic schemas for a generic `ResourceBalance` (current amount, bank cap, protected floor, grant/spend history) and a generic `InteractionModifierEffect` (family, target eligibility rule, deterministic resolution behavior, outcome audience).
- Deterministic effect resolution for six Nightcap-configured effects: **Deep Read**, **Follow the Thread**, **Sting Operation** (advantages); **Rattle the Witness**, **Listen In**, **Make Them Wait** (sabotages).
- Targeting eligibility checks and the danger-combination guardrails: at most one offensive modifier per interaction; at most one information-control sabotage (Listen In) per target per beat; a post-target protection window after a player is sabotaged, until another player is targeted or the next interaction window opens.
- Saboteur-identity delivery: withheld from the target until the sabotaged interaction resolves (per-question, not per-round), except Sting Operation's immediate, target-private exposure of its source.
- Resource-balance persistence across beat transitions within a session, bounded by a configured bank cap.
- Public balance readout (`ResourceBalance` totals routed to all players/shared display) and per-effect outcome audience routing through AW-282/AW-215/AW-216's existing public/private ContentEvent fanout — no new audience primitive.
- Telemetry events for grants, spends, targets, outcomes, counterplay, and player-recovery, without storing unnecessary private content.
- Mini-game reward integration: a mini-game result may grant a `ResourceBalance` credit, subject to the "every player has a protected earn path" guardrail.
- Nightcap arc configuration mapping the six generic effects to their player-facing names, copy, and family metadata.

---

# Out of Scope

- **Call Their Bluff.** Requires challenging a "public theory" a player has publicly advanced; no public-theory state, event, or input model exists in the platform, and AW-282 prohibits free text. Replaced in the v1 launch set by Make Them Wait (see ADR-0015). Defining a public-theory contract is a separate, later approval.
- The other four advantage families and four sabotage families beyond the six launch-set effects (Compare Notes, Sharpen the Question, Call the Next Witness, Join the Pressure, Contingency Plan / Close the Angle, Jam the File, Loose Lips, Pick Their Pocket, Raise the Stakes, Conditional Trap) — catalog reference only for v1.
- Team/co-op sabotage toggles — v1 has no team/co-op configuration (top-level scope boundary).
- AI-driven target selection, sabotage-success adjudication, or any generation call that could infer session state or mutate canonical case truth.
- New database migrations beyond the `ResourceBalance`/effect-log tables this spec defines (schema-only; no unrelated schema changes).
- TypeScript/SDK/dashboard rendering of Leverage UI — that is AW-285 scope, consuming the ContentEvents this spec emits.
- Suspect answer-generation content changes — AW-283 consumes Leverage's effect outcomes (e.g., "this answer was generated under an active Rattle the Witness effect") but this spec does not define answer-generation behavior itself.

---

# Runtime Contract

## State model

- `ResourceBalance`: `player_id`, `current_amount`, `bank_cap`, `protected_floor`, `session_id`. One row per player per session. Persists across beat transitions; no reset event on beat change.
- `ResourceGrant` / `ResourceSpend`: append-only ledger entries referencing `ResourceBalance`, with `source` (mini-game id, or none), `amount`, `beat_id`, `timestamp`. Grants respect the "protected earn path" guardrail: every player has at least one non-mini-game-gated way to earn a floor amount per session (exact floor value is an implementation-plan tuning parameter, not fixed here).
- `InteractionModifierEffect`: `effect_key` (generic, e.g. `insight.deep_read`, `sabotage.rattle_witness`), `family` (Insight | Access | Tempo | Counterplay | Risk-and-reward | Witness-pressure | Information-control | Economy | Mind-game), `cost`, `target_eligibility_rule`, `resolution_behavior`, `outcome_audience_rule`.
- `EffectActivation`: `effect_key`, `activator_id`, `target_id` (nullable — Deep Read and Follow the Thread self-target), `interaction_window_id` (references AW-282's `InteractionResolution.window_id`), `resolved_at`, `source_reveal_at` (nullable — null until the reveal condition fires).

## Targeting eligibility

Before an effect activation is accepted, the engine checks, in order:
1. Activator has sufficient `current_amount` (>= `cost`), and spending would not drop them below `protected_floor` unless the effect explicitly permits it.
2. For sabotages: target does not already carry an unexpired post-target protection flag.
3. For sabotages: target's current interaction does not already carry another offensive modifier (the one-offensive-modifier-per-interaction guardrail).
4. For Listen In specifically: target has not already received an information-control sabotage this beat.

Any failed check rejects the activation deterministically with a typed reason; no partial application.

## Resolution and reveal timing

- Non-Sting-Operation sabotages: the effect's mechanical outcome (a more guarded answer, a delayed interaction, a copied private observation) is delivered through its normal audience routing (public if it modifies a public answer; private to the recipient if it copies private content) as soon as the affected interaction resolves. The saboteur's identity (`EffectActivation.activator_id`) is exposed to the target only once `source_reveal_at` is set, which the engine sets at the same moment the affected `InteractionResolution.window_id` resolves — not earlier.
- Sting Operation: when it counters a sabotage, `source_reveal_at` for the countered sabotage's `EffectActivation` is set immediately, and the exposure event routes privately to the Sting Operation user only (not table-wide).

## Balance visibility

`ResourceBalance.current_amount` for every player is included in a public ContentEvent (shared-display + all-players audience) on every grant or spend — no private-balance mode exists in v1.

## Effect definitions (launch set)

| Effect key | Family | Target | Resolution behavior | Outcome audience |
|---|---|---|---|---|
| `advantage.deep_read` | Insight | Self | Sharpens the activator's next private observation on their own upcoming question. | Private to activator |
| `advantage.follow_the_thread` | Access | Self | Unlocks one contextual follow-up question bounded by the answer just resolved. | Public answer request, same as any AW-282 question |
| `advantage.sting_operation` | Counterplay | Self (armed in advance) | Weakens the next sabotage targeting the activator and exposes its source immediately. | Weakened-effect outcome per the countered sabotage's own audience; source exposure private to activator |
| `sabotage.rattle_the_witness` | Witness pressure | Rival's next question | Character answers more guarded for one target interaction; no factual content is altered or withheld beyond guardedness. | Guarded answer is public (it's a normal answer); saboteur identity revealed to target after resolution |
| `sabotage.listen_in` | Information control | Rival's next private observation | Saboteur receives a copy of the target's next private observation. | Copy delivered privately to saboteur; saboteur identity revealed to target after resolution |
| `sabotage.make_them_wait` | Tempo | Rival's queued interaction | Moves the target's interaction later within the current round (never beyond it); the interaction still resolves with full value. | Reorder is a public state change (interaction order is visible on the shared display); saboteur identity revealed to target after resolution |

---

# Human Collaboration Contract

**Interaction profiles:** Creative collaboration.

**Classification rationale:** The effect catalog, tuning, and player-facing feel are subjective design choices requiring founder direction, per `docs/conventions/human-collaboration.md`.

**Required founder inputs:**
- Effect catalog and family selection (design doc, founder-directed session).
- Balance visibility, saboteur-reveal timing, cross-beat persistence, per-effect visibility (D-075).
- Representative-interaction walkthrough review, including the per-question reveal-scope decision and Sting-Operation-exposure-is-private-to-user decision (`docs/superpowers/specs/2026-07-18-aw287-leverage-walkthrough.md`).

**Phase gates:**
- Discovery and catalog design: complete (design doc, D-075).
- Representative-interaction walkthrough: complete, approved 2026-07-18.
- Implemented thin slice: pending — pause for explicit founder direction before this spec's acceptance criteria are treated as met.

**Review package:** The walkthrough artifact explained each decision's player-facing consequence and flagged two open judgment calls, both resolved by the founder before this spec was written.

**Approval evidence:** D-075 (`docs/product/decisions-log.csv`), `docs/product/aw287-discovery-and-checkpoints.md`, `docs/decisions/0015-nightcap-leverage-advantages-sabotages.md`.

**Owner actions:** None external; implementation owned by the session executing this spec.

---

# Acceptance Criteria

- [ ] `ResourceBalance` and question allowances (AW-282) are separate, independently-persisted state concepts.
- [ ] Grants, spends, caps, floors, and expiry resolve deterministically; no model call decides an outcome.
- [ ] No effect can change canonical case truth, delete evidence, or create an unfalsifiable clue (property-based or seeded test asserting invariance of case-truth fields across all six effects).
- [ ] Every sabotage has a documented, testable recovery or counterplay path (Sting Operation counters; post-target protection window recovers from repeat targeting).
- [ ] Public and private effect outcomes pass the existing AW-282/AW-230 audience-filtering leak tests, extended to cover all six effect outcome types.
- [ ] The knowledge graph is queried before any generated character response affected by a Leverage effect (Rattle the Witness), consistent with the AGENTS.md Key Engine Constraint.
- [ ] Mini-game rewards cannot create an unrecoverable lead: bank cap and protected floor enforced in a seeded multi-beat test.
- [ ] A seeded replay produces identical `ResourceBalance` and `EffectActivation` state given identical inputs.
- [ ] An arc/game with no Leverage configuration is provably unaffected (existing AW-281/282 tests pass unmodified with Leverage config absent).
- [ ] Telemetry captures grants, spends, targets, outcomes, counterplay, and recovery events without any private-content field.
- [ ] Saboteur identity is withheld from the target until the sabotaged interaction resolves in a per-question test (two questions queued for the same target; reveal fires after the first, not both).
- [ ] Sting Operation exposes its source immediately and only to the Sting Operation user (a test asserting the table-wide event does not carry the source).
- [ ] `ResourceBalance.current_amount` persists unchanged across a beat-transition test.
- [ ] No `engine/` class, field, or module name contains a Nightcap-specific term (Leverage, Deep Read, Sting Operation, etc.) — a repo-wide grep-based test enforcing this.

---

# Test Plan

- Unit tests: `ResourceBalance` grant/spend arithmetic, bank cap enforcement, protected-floor enforcement, each of the six effects' targeting-eligibility checks (including rejection paths).
- Integration tests: full interaction-window resolution with an active sabotage (verifying reveal timing), with an active Sting Operation counter (verifying immediate private exposure), and with the one-offensive-modifier-per-interaction guardrail actually rejecting a second offensive effect.
- Audience-filtering tests: extend the existing AW-230/AW-282 privacy-matrix test harness with the six new event types (public balance updates, private Listen In copies, guarded-answer public deliveries, post-resolution saboteur reveals, Sting Operation private exposures, Make Them Wait reorder events).
- Determinism tests: seeded replay producing byte-identical `ResourceBalance`/`EffectActivation` state across two runs.
- Manual testing: none required — all behavior is deterministic and covered by automated tests per the AGENTS.md testing conventions.

---

# Risks and Unknowns

**Risks**:
- Danger-combination guardrails add real-time eligibility-checking complexity to every interaction resolution; a missed check could let a disallowed combination through undetected until a specific test exercises it.
- Public balance visibility could make a runaway leader's dominance more visible and demoralizing rather than exciting — a fun-rubric risk to watch at the AW-287 thin-slice review and Rehearsal 1 (AW-286).

**Unknowns**:
- The exact bank-cap and protected-floor numeric values are implementation-plan tuning parameters, not fixed by this spec; they will be set during Task 15 (AW-287 implementation plan) and are expected to be revised after rehearsal telemetry.
- Which telemetry signal best predicts that sabotage felt exciting rather than frustrating is explicitly deferred to post-rehearsal analysis (D-075), not a pre-implementation blocker.

---

# Open Questions

- Q1: Should a future Leverage family (post-launch) introduce a private-catch or private-balance variant? Deliberately not built speculatively now (per the walkthrough's resolution) — revisit only if a specific future effect needs it.
- Q2: Does Call Their Bluff (or an equivalent public-theory mechanic) get its own future spec once AW-284's accusation/theory state matures enough to support a bounded public-theory contract? Logged for a later product decision, not this spec's scope.
