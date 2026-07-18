# engine/case/, Arc-Agnostic Case Resolution

## Purpose

Deterministic case resolution for arcs where case content (culprit,
cast, a case-truth fact graph, evidence, authorized falsehoods, reveal
shape) must be resolved at session start from a seed.

Introduced by AW-281 for the Couch Race arc (Nightcap v1). Reusable by
Daily Case (single-suspect variant) and the future Imposter Variant
(player-culprit variant) with their own skeleton and taxonomy content.

## Vocabulary policy (READ BEFORE ADDING FIELDS)

This module carries **no murder-mystery vocabulary in schema**. Field
names are generic (`role`, `evidence_type`, `topic`, `predicate`); arc
content populates them with strings.

Bad (do not add):
- `killer_id`, `murder_method`, `murder_time`

Good:
- `culprit_id` (the character responsible for the case's central act)
- `role: str` (arc content sets it to `"suspect"`, `"victim"`,
  `"witness"`, or whatever the arc needs)
- `CaseFact.predicate: str` (arc content sets it to `"method"`,
  `"motive"`, `"twist"`, `"secret"`, `"relationship"`, or whatever
  the arc's case-truth graph needs)

Known engine-level exceptions predating this module:
- `engine/arc/models.py` fields `killer_assignment`,
  `killer_knows_they_did_it`, `murder_timing_range` are legacy
  Imposter-Variant terms tracked as violations in issue #220 / spec
  0070. This module does not add new ones.

Note: a `victim_id` field was intentionally dropped from `ResolvedCase`
under this policy. Arcs that need a victim populate a `CastMember` with
`role="victim"` and look it up via `ResolvedCase.members_by_role("victim")`.
Likewise, `EvidenceEntry` uses `points_toward` and `points_away_from`
rather than `implicates` and `exonerates`.

This applies to data pools and content templates too, not just field
names: character names, role-archetype tags, lie claim sentences, and
every other piece of creative content must load from the arc's own
taxonomy directory (e.g. `nightcap/case_taxonomy/`) via
`load_taxonomy()`, never live as hardcoded constants in this module.
This module also never hardcodes a path into any single arc's content:
the case-resolution config is located through
`resolve_case_resolution_config_path`, an arc-agnostic prefix-match
registry (`config/case_resolution_registry.json`, mirroring
`engine/arc/registry.py`'s pattern), and the resolver validates the
loaded config's `arc_id_prefix` against the arc actually being
resolved before using any of its content.

## Public API

```python
from engine.case import (
    resolve,
    ResolvedCase,
    CastMember,
    EvidenceEntry,
    AuthorizedFalsehood,
    CaseFact,
    CaseSkeleton,
    CaseInvariantError,
    CaseResolutionError,
    synthetic_detective,
    SolverVerdict,
)

case = resolve(arc_definition, seed=42, participant_ids=["p1", "p2", "p3", "p4"])
```

## The case-truth fact graph

`ResolvedCase.facts: list[CaseFact]` is the ground-truth record beyond
the player-facing evidence and lie surface: the resolved method, the
motive, per-suspect secrets, per-suspect relationships to the victim,
and a deterministic twist (a promoted secret that reorders suspicion
without changing whodunit). Each fact carries `known_by`, the
participant or cast member ids who know it at session start, feeding
the platform's mandatory pre-generation knowledge-state query once
AW-283 wires character generation to this graph. Evidence and lie text
is generated from this same graph so player-facing content stays
traceable to one source of truth. Look up facts with
`ResolvedCase.facts_by_predicate(predicate)`.

## Invariants (enforced at resolve time)

Every ResolvedCase satisfies:

1. **Solvability.** The genuine clue chain, using the resolver's own
   `points_toward`/`points_away_from` bookkeeping, uniquely narrows to
   the culprit. This is the resolver checking its own internal
   consistency, not a proof that a human player can solve the case.
2. **Lie falsifiability.** Every `AuthorizedFalsehood.contradicted_by`
   list is non-empty, every referenced `EvidenceEntry` is present in
   the resolved case, and that evidence's text names the lying
   speaker (verified by the resolver's own construction, and checked
   directly by `engine/tests/test_case_resolver.py`).

Violations raise `CaseInvariantError`.

## Fairness proof stack (AW-281)

- Level 1, runtime invariant assertions (this module, above).
- Level 2, property-based tests over exactly 1000 seeds per authored
  skeleton (`engine/tests/test_case_property_sweep.py`), using
  `resolve()`'s `forced_skeleton_id` test-only override so the sweep
  size is exact, not an approximation of the seeded pick's
  distribution.
- Level 3, the synthetic detective solver
  (`engine/case/solver.py`, tested in
  `engine/tests/test_case_solver.py`). This is the non-circular,
  player-observable proof: `synthetic_detective(case, participant_id)`
  never reads `points_toward`/`points_away_from`, it derives
  suspicion purely from the evidence text actually visible to that
  one participant (`ResolvedCase.visible_evidence_for`), matching
  suspect display names inside the text. A case with meaningless or
  blank evidence text correctly fails this solver even though it
  would still pass Level 1's label-based invariant, that gap is
  exactly why both levels exist.
