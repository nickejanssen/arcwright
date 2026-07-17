# engine/case/ — Arc-Agnostic Case Resolution

## Purpose

Deterministic case resolution for arcs where case content (culprit,
victim, cast, evidence, authorized falsehoods, reveal shape) must be
resolved at session start from a seed.

Introduced by AW-281 for the Couch Race arc (Nightcap v1). Reusable by
Daily Case (single-suspect variant) and the future Imposter Variant
(player-culprit variant) with their own skeleton + taxonomy content.

## Vocabulary policy (READ BEFORE ADDING FIELDS)

This module carries **no murder-mystery vocabulary in schema**. Field
names are generic (`role`, `evidence_type`, `topic`); arc content
populates them with strings.

Bad (do not add):
- `killer_id`, `murder_method`, `murder_time`

Good:
- `culprit_id` (the character responsible for the case's central act)
- `role: str` (arc content sets it to `"suspect"` / `"victim"` /
  `"witness"` / whatever the arc needs)

Known engine-level exceptions predating this module:
- `engine/arc/models.py` fields `killer_assignment`,
  `killer_knows_they_did_it`, `murder_timing_range` are legacy
  Imposter-Variant terms tracked as violations in issue #220 / spec
  0070. This module does not add new ones.

## Public API

```python
from engine.case import (
    resolve,
    ResolvedCase,
    CastMember,
    EvidenceEntry,
    AuthorizedFalsehood,
    CaseSkeleton,
    CaseInvariantError,
    CaseResolutionError,
)

case = resolve(arc_definition, seed=42, participant_count=4)
```

## Invariants (enforced at resolve time)

Every ResolvedCase satisfies:

1. **Solvability.** The genuine clue chain, applied by a rational-actor
   solver over the intended clue distribution, uniquely identifies the
   culprit.
2. **Lie falsifiability.** Every `AuthorizedFalsehood.contradicted_by`
   list is non-empty AND every referenced `EvidenceEntry` is present
   in the resolved case.

Violations raise `CaseInvariantError`.

## Fairness proof stack (AW-281)

- Level 1 — Runtime invariant assertions (this module).
- Level 2 — Property-based tests over 1000+ seeds
  (`engine/tests/test_case_property_sweep.py`).
- Level 3 — Synthetic detective solver
  (`engine/case/solver.py`, tested in
  `engine/tests/test_case_solver.py`).
