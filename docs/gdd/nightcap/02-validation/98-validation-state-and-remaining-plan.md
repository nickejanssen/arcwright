# Nightcap — Validation State & Remaining Plan

**Status:** PROCESS / CONTINUATION PLAN — not game canon  
**Checkpoint:** 05 / Session B

## Current Progress Estimates

Planning estimates only; intentionally unchanged:

- **Foundational GDD definition:** approximately **90%**.
- **End-to-end design + validation plan:** approximately **80%**.

The cross-system architecture is materially clearer, but major empirical gates remain unresolved.

## What Has Just Been Completed

### Cross-system cohesion pass

The Checkpoint 04 integration-map recommendation was adopted as a supporting design-control method and used to audit the full Nightcap loop.

Major formerly under-specified seams now have current architectural direction:

- WATCH → HUNT,
- HUNT → THINK,
- THINK → bounded action,
- Case Board / memory → THINK,
- Minigames → REACT → murder-facing play,
- Espionage → REACT / HUNT,
- REACT → re-entry,
- THINK → Last Call → Case File / Structured Reconstruction,
- Structured Reconstruction → Truth → Verdict → Postmortem,
- player-count invariants at 2 vs. larger groups.

`06-story-reactivity-reentry.md` now gives REACT an explicit system owner.

The subsequent adversarial pass also clarified the Arcwright/Nightcap runtime boundary, endgame knowledge bookkeeping, culprit-reveal sequencing, Leverage sourcing risk, Group Rescue wording, Postmortem observability boundaries, deterministic Structured Reconstruction, Spotlight ownership, and hidden case-graph analytics.

### Documentation consolidation

Checkpoint 05 adds/updates concise authoritative one-pagers so the cohesion decisions live in system documents rather than only in conversation or supporting rationale.

### External test infrastructure

The GitHub Pages paper-test harness, Jotform survey, and associated testing infrastructure have been built in a separate workflow.

The GDD session should not re-engineer that infrastructure.

## Time-to-Fun Evidence So Far

Paper Test #2 still provides **negative/diagnostic evidence**, not validation.

1. **v1 — FAILED AS TEST INSTRUMENT**
   - mid-play research/essay questions,
   - too little real investigation,
   - over-signposting,
   - poor representation of Nightcap.

2. **v2 — REVISE AND RERUN**
   - game-first structure improved,
   - detective feeling and desire to continue remained weak.

3. **v2.1 — REVISE AND RERUN**
   - independent third-party tester,
   - Fun = 2/5,
   - Detective Feeling = 2/5,
   - Wanted to Continue = Maybe,
   - Action Clarity = Mostly Confusing,
   - five investigation actions / more options were not sufficient.

4. **Additional early qualitative autonomy signal**
   - creator reports that players liked autonomy and reaching their own conclusions rather than feeling hand-held,
   - source details are limited in this checkpoint,
   - treat as directional TESTING evidence only,
   - do not use it to excuse confusing action design.

## Important Non-Conclusions

Current tests do **not** establish that Nightcap itself is unfun.

Earlier prototypes omitted or weakly represented major pillars such as meaningful rivalry, information warfare, Leverage, social bluffing, strong story reactivity, and a representative competitive/minigame pulse.

A failed prototype must first be diagnosed as:

1. a Nightcap design failure,
2. an unrepresentative implementation,
3. or an invalid test instrument.

Do not rewrite canon until evidence distinguishes those possibilities credibly.

## Gate 1 — Representative Time-to-Fun / Cohesion

**ACTIVE:** Paper Test #2 v2.2.

The external harness should implement a fuller representative slice so the existing survey follows a meaningful play experience.

Current test-specific requirements are maintained in `98b-paper-test-02-v2.2-handoff-requirements.md`.

## Remaining Validation Order

### Gate 1 — Representative Time-to-Fun / Cohesion

Active now.

Goal: demonstrate that a small but representative slice containing multiple real Nightcap pillars can generate detective play, competitive energy, and desire to continue.

### Gate 2 — Memory Support vs. Auto-Solving

**BLOCKED until Gate 1 passes.**

Compare lean/basic history against approved baseline memory support without changing the underlying mystery challenge.

### Gate 3 — Same Case Challenge at 2 vs. 4 Players

Test whether the same intellectual Case Challenge works at both counts by scaling opportunity architecture rather than making the two-player mystery easier.

### Gate 4 — Mixed-Skill Competition

Test broad investigator skill expression + volatile tactical state without hidden rubber-banding or loser bonuses.

### Gate 5 — Group Rescue Exploitability

Test whether unanimous rescue stays rare/helpful instead of becoming routine optimal play or grief fuel.

### Gate 6 — Room-Compatible Minigame Pool

Test whether accessibility filtering preserves enough variety, spectacle, and fair skill expression.

## Parallel GDD Continuation

The integration pass is complete enough to stop adding cohesion laws merely for completeness.

Recommended next GDD sequence:

1. **Checkpoint 05 consolidation** — COMPLETED by this package.
2. Run a **full-GDD adversarial/cohesion pass** across the authoritative pages, focusing on contradictions, duplicated responsibilities, hidden player-work burden, and unvalidated assumptions.
3. Resolve only material issues surfaced by that pass; do not reopen settled decisions for novelty.
4. Continue Gate 1 external testing in parallel.
5. Interpret representative v2.2 evidence before opening Gate 2.
6. Harden player-count scaling through Gate 3 before deciding the V1 upper bound.
7. Continue remaining validation gates.
8. Run representative whole-session tests before calling the GDD hardened.

## Major OPEN Areas

- V1 upper player-count bound.
- 7–8-player viability.
- Detailed player-count-specific case scaling.
- Production/content budgets.

## High-Value TESTING Areas

- representative Time-to-Fun / core-loop cohesion,
- autonomy vs. action clarity,
- exact Leverage costs/frequency,
- repeated-targeting / Counterintel balance without automatic pity protection,
- Case Board UX,
- Structured Reconstruction interaction grammar and accepted-solution authoring,
- exact minigame frequency/reward calibration,
- investigation and Spotlight distribution/calibration,
- Arcwright case-graph complexity/traversal analytics,
- runtime,
- quarterbacking countermeasures,
- Postmortem generation,
- endgame pacing,
- difficulty-pressure calibration,
- memory support,
- mixed-skill competitiveness,
- two-player same-challenge scaling,
- group rescue,
- accessibility-compatible minigame breadth.

## Evidence Rule

Repeated representative evidence has more authority than intuition.

A DECIDED design may be reopened when evidence justifies it. One exploratory participant or one prototype convenience normally produces a **TEST FINDING**, not a permanent law.
