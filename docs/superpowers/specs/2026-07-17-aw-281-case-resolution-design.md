# AW-281 — Case Resolution Design (Founder Round)

**Status:** Approved direction (founder, 2026-07-17)
**Author:** Claude (brainstorming session with founder, AW-281 kickoff)
**Date:** 2026-07-17
**Parent design:** `docs/superpowers/specs/2026-07-15-nightcap-couch-race-design.md`
**Parent spec:** `docs/specs/0072-nightcap-couch-race-v1.md`
**Task file:** `docs/roadmap/tasks/AW-281-couch-race-arc-definition-and-case-generation.md` (#235)

---

## Problem

The parent spec 0072 names "generated-case fairness inconsistency" as the
central quality risk of the Couch Race v1 launch. AW-281 must ship both
the six-beat arc JSON *and* a case-resolution pipeline that provably
produces solvable, fair, catchable-lie cases from a seed. The task is
Size-L and this design fixes the architectural decisions before code.

## Founder decisions recorded in this session

Four multiple-choice rounds resolved the architecture:

### 1. Authorship line (which axes of a case are authored)

**Author axes 1-4; generate axes 5-6.**

- **Axis 1 — Case archetype** (authored): the *shape* of the crime
  (locked-room poisoning, alibi-collapse strangulation, pre-conspiracy
  fall). 3 archetypes for v1.
- **Axis 2 — Clue-chain pattern** (authored): the *sequence of
  deductions* a solver must perform. Each archetype names its own.
- **Axis 3 — Lie shape per suspect role** (authored): what each
  non-culprit *type* of suspect lies about (location-at-time,
  relationship-to-victim, what-they-saw).
- **Axis 4 — Reveal shape** (authored): the rhythm of the Truth beat's
  narrative — which reveal-tropes fire in which order.
- **Axis 5 — Specific evidence text** (generated): the actual words on
  the clue card, from taxonomy tables + per-wrapper voice library.
- **Axis 6 — Character names + motive connective tissue** (generated):
  per-suspect names, per-victim identity, motive text, relationship
  graph specifics.

Rationale: this is the anti-slop model applied to case content —
authored where signature matters (structure and reveal), generated where
variety scales (specifics and voice). Every generated case rests on an
authored skeleton.

### 2. Code architecture

**New `engine/case/` module** with an arc-agnostic resolver interface:

```python
def resolve(arc_definition, seed, participant_count) -> ResolvedCase
```

- The engine's case module carries no murder-mystery vocabulary. Types
  are `ResolvedCase`, `CastMember`, `EvidenceEntry`,
  `AuthorizedFalsehood` — role and truth values are string fields
  populated by arc-specific content, not schema.
- Arc-specific content (skeletons, taxonomies, per-wrapper voice slots)
  lives entirely in `nightcap/case_skeletons/` and
  `nightcap/case_taxonomy/`.
- Daily Case and the future Imposter Variant reuse the same resolver
  interface with their own skeleton + taxonomy content.
- Follows the same pattern as `engine/routing/` (arc-agnostic router +
  `config/routing_table.json` for content).

### 3. Cast size

**Scales with player count:**

| Players | Cast size |
| --- | --- |
| 2-4 | 4 suspects |
| 5-6 | 5 suspects |
| 7-8 | 6 suspects |

A case skeleton may override with an explicit `cast_size` field if the
archetype requires it (e.g., a Big Top skeleton might carry 6 suspects
regardless of player count).

### 4. Fairness proof stack — Level 3

Three-layer proof, additive:

1. **Runtime invariant assertions** inside the resolver. Every
   `ResolvedCase` passes through two invariant checks before being
   returned:
   - **Solvability:** the genuine clue chain, applied by a
     rational-actor solver, uniquely identifies the culprit.
   - **Lie falsifiability:** every authorized falsehood is contradicted
     by at least one clue in the resolved clue distribution.
   Violations raise `CaseInvariantError` at resolve time.
2. **Property-based tests over 1000+ seeds.** A test loop generates
   1000 cases per archetype (3000 total), asserts both invariants
   hold, and checks the taxonomic distributions are non-degenerate
   (no seed produces an empty motive, no clue is orphan-typed).
3. **Synthetic detective solver.** A bounded rational-actor solver in
   `engine/case/solver.py`. Given a resolved case + intended clue
   distribution, it plays through the case:
   - It reads all group clues, receives its private clues, and requests
     interrogation intents against each suspect.
   - It maintains a suspect-suspicion score based on clues seen and
     contradictions detected.
   - It "wins" if it uniquely identifies the culprit before its
     intent budget expires.
   Runs in CI (`engine/tests/test_case_solver.py`) over 100 seeds per
   archetype. The solver's win rate is asserted ≥ 100% (i.e., every
   case must be solvable by a rational player from the intended
   distribution). The solver becomes a reusable asset later: hint
   engine (v1.1), difficulty tuner, replay verifier.

Level 4 (live-eval canary in CI) is future scope for M6 qualifying
sessions.

### 5. Cast-rail typing

Suspects are unified-model AI characters at runtime (per architecture
principle 4). At resolve time they are `CastMember`s with role slots
(`role: "suspect" | "victim"`) — the mapping to full character records
is done by the character-behavior pipeline (existing AW-211/212), not
the case resolver.

---

## Non-Goals

Explicitly out of scope for AW-281:

- **Interrogation round mechanics** (question intent menus, tokens,
  round order) — belongs to AW-282.
- **Suspect answer generation and contradiction detection** — belongs
  to AW-283 (depends on spec 0071 live-loop dialogue).
- **Race scoring and accusation state** — belongs to AW-284.
- **TV/phone rendering** — belongs to AW-285.
- **Rehearsal execution** — belongs to AW-286.
- **Live-session (REST) integration** of the resolver — this task
  wires the *harness* runner only; the live path picks up the same
  resolver at the AW-282 wiring.
- **New engine dependencies.** The property tests use plain seeded
  random loops, not Hypothesis or another new library. (Would trigger
  the AGENTS.md Hard Rule for new dependencies.)
- **Free-text interrogation input.** Menu-driven only in v1
  (bible §6, spec 0072).
- **Teams / co-op competition dial** implementations
  (bible §9 — configurable structure only).

---

## Deliverables from this design

Feeds the plan at
`docs/superpowers/plans/2026-07-17-aw-281-couch-race-arc-and-case-generation.md`.
