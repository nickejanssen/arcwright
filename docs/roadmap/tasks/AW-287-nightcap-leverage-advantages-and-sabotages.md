# AW-287: Nightcap Leverage Advantages And Sabotages

**Milestone / Epic:** M5 / M5-I
**Size:** L
**Status:** Planned

## Plain-English Summary

Implement Leverage: an earned resource, separate from question allowances, that players spend on authored advantages (Deep Read, Follow the Thread, Sting Operation) or sabotages (Rattle the Witness, Listen In, Make Them Wait) against rivals. Built as a platform-neutral interaction-modifier capability that Nightcap configures, per the design catalog in `docs/product/nightcap-leverage-advantages-sabotages.md` and the approved implementation spec at `docs/specs/0075-aw287-nightcap-leverage-advantages-sabotages.md`.

## Why This Matters

Founder-approved design direction (recorded in the Leverage design doc's "Scope decision" section and D-075) identifies Leverage as core to the Couch Race competitive loop: it creates prediction/counterprediction tension, visible table moments, and player-to-player agency beyond the base question economy. AW-283's contradiction-catch and answer-generation behavior is specified to vary by active Leverage effect (e.g., Listen In, Sting Operation), so this capability is a build-order dependency for AW-283, not an optional add-on.

## Player Impact

Players earn Leverage from mini-games and other accomplishments, then spend it to sharpen their own investigation (advantages) or interfere with a rival's (sabotages) — always within the fairness contract: no effect changes canonical case truth, deletes evidence, or creates an unfalsifiable clue.

## Business Value

Differentiates the race from a static Q&A loop; the economy is a second lever (alongside question tokens) for tuning session pacing and replay variation without new content production.

## Technical Scope

- Generic engine state model `ResourceBalance` (platform-neutral name; Nightcap configures its display name as "Leverage") per player: earned/spent/current amount, bank cap, protected floor. Balances are **public** (visible to all players, per founder decision). See the naming contract note below and spec 0075 for the full engine-vs-configuration split.
- Deterministic effect resolution for the six launch-set effects (three advantages: Deep Read, Follow the Thread, Sting Operation; three sabotages: Rattle the Witness, Listen In, Make Them Wait), each configured from the family definitions in the design doc's "Final top five advantages/sabotages" section. **Call Their Bluff is replaced by Make Them Wait** (also one of the design doc's Final top five sabotages) for the v1 launch set: Call Their Bluff requires challenging a "public theory" a player has advanced, but no public-theory state, event, or input exists anywhere in the platform (AW-282's interaction runtime only supports authored target/question selections, no free text), so it has no deterministic input contract today. Make Them Wait needs no new state — it reorders an already-queued interaction.
- Targeting eligibility and per-interaction modifier limits: no player receives more than one offensive modifier on a single interaction; at most one information-control sabotage (e.g. Listen In) may land on a given player per beat; a player who was just sabotaged receives a temporary protection window until another player is targeted or the next interaction window opens.
- Saboteur identity: revealed to the target **after the sabotaged interaction resolves**, not instantly — except Sting Operation, whose payoff is exposing its source as soon as it counters a sabotage (that immediate exposure is the effect's defining behavior, not a general rule).
- Leverage **carries between beats** for the whole session (does not expire at beat transitions), bounded by the bank cap guardrail.
- Per-effect visibility follows the effect's own documented behavior (Listen In: private to the saboteur; Sting Operation: exposes its source; public-facing effects like Rattle the Witness are visible to the table since they alter a public answer) — there is no single global public/private toggle.
- Existing ContentEvent audience routing (public/private) carries all Leverage events; no new event-audience primitive.
- Telemetry: grants, spends, targets, outcomes, counterplay, and player recovery, without storing unnecessary private content. No pre-committed "best" excitement-signal — capture broadly, tune post-rehearsal.
- Mini-game victories feed the Leverage economy per the existing guardrail (every player has a protected earn path; victories may award more but never leave a non-winner permanently empty).

## Human Collaboration Contract

**Interaction profile:** Creative collaboration.

**Founder input:** Effect catalog and family selection (already substantively
completed via a founder-directed design session, recorded in the Leverage
design doc), plus the remaining unknowns: balance visibility, saboteur-reveal
timing, and cross-beat persistence.

**Required phases:** Discovery and catalog design are complete (design doc,
2026-07-18). This task's remaining collaboration requirement is: confirm the
resolved unknowns durably (this task file + D-075), present a low-cost
representative-interaction walkthrough (a session-shaped example of 2-3
effects firing) before full implementation, and pause for explicit direction
on that walkthrough before building the complete resolution engine.

**Gates:** Pause for explicit direction after the representative-interaction
walkthrough and the implemented thin slice. Research and reversible
preparation may continue while the founder is unavailable, but no additional
effect-behavior choice or full implementation may proceed without it.

**Evidence:** Preserve the design doc, the resolved-unknowns record (this
file, D-075), the walkthrough artifact and founder feedback, explicit
checkpoint approvals, dates, and owner actions.

## Acceptance Criteria

- [ ] Question allowances and Leverage balances are separate state concepts.
- [ ] Leverage grants, spends, caps, floors, and expiry resolve deterministically.
- [ ] A configured advantage or sabotage cannot change canonical case truth or delete evidence.
- [ ] Every sabotage has a documented recovery or counterplay path.
- [ ] Public answers and private observations pass audience-filtering tests.
- [ ] The knowledge graph is checked before any generated character response affected by a Leverage effect.
- [ ] Mini-game rewards cannot create an unrecoverable lead (bank cap + protected floor enforced).
- [ ] A seeded replay produces the same resource balances and effect outcomes.
- [ ] Games without Leverage configuration remain unaffected.
- [ ] Telemetry records grants, spends, targets, outcomes, counterplay, and player recovery without storing unnecessary private content.
- [ ] Saboteur identity is withheld from the target until the sabotaged interaction resolves, except Sting Operation's immediate-exposure payoff.
- [ ] Leverage balances persist across beat transitions within a session.
- [ ] Leverage balances are visible to all players.

## Tests/Verification

- `pytest engine/tests/` Leverage resolution, targeting, and telemetry tests pass, including audience-filtering leak tests and the danger-combination limits (one offensive modifier per interaction, one information-control sabotage per player per beat, post-target protection window).

## Dependencies

- AW-281 (arc and case resolution)
- AW-282 (interaction director/runtime — Leverage plugs into the interaction-modifier seam AW-282 was deliberately built to leave open)
- AW-215/AW-216 event system

## Must Not Do

- Do not let a Leverage effect change canonical case truth, delete evidence, or create an unfalsifiable clue.
- Do not let an AI model choose targets, decide whether a sabotage succeeded, or infer session state.
- Do not implement effects outside the six launch-set effects (Deep Read, Follow the Thread, Sting Operation, Rattle the Witness, Listen In, Make Them Wait) without a separate approval — the other four families, and Call Their Bluff specifically, are catalog reference only for v1.
- Do not build team/co-op sabotage toggles — v1 has no team/co-op configuration.
- Do not put Nightcap-specific effect or resource names (Leverage, Deep Read, Sting Operation, etc.) in engine schemas, class names, or module names. The engine exposes only generic concepts — `ResourceBalance`, resource spend, interaction modifier, targeting eligibility, deterministic effect resolution, public/private outcome audience, counterplay window — per the design doc's "Future implementation shape" section and spec 0075. Nightcap-specific names live only in Nightcap's arc/effect configuration, never in `engine/` class or field names.

## Architecture References

- `docs/product/nightcap-leverage-advantages-sabotages.md` (full catalog, filtering rationale, guardrails, and swap review)
- `docs/specs/0075-aw287-nightcap-leverage-advantages-sabotages.md` (approved implementation spec — runtime contract, generic/Nightcap naming split, test plan)
- `docs/decisions/0015-nightcap-leverage-advantages-sabotages.md` (ADR — architecture boundary and consequences)
- `docs/specs/0074-aw282-structured-interaction-loop.md` and `docs/decisions/0014-structured-interaction-resolution.md` (the interaction-modifier seam this plugs into)
- `docs/architecture/03-arc-execution.md`, `docs/architecture/08-event-system.md`, `docs/architecture/11-telemetry.md`

## Playtest Relevance

Direct: Leverage is a primary lever for whether the race feels alive and whether player-to-player interference lands as exciting rather than frustrating (fun-rubric observation).
