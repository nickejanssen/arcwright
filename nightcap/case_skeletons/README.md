# Nightcap Case Skeletons

Authored axes 1-4 case content for the Couch Race arc (AW-281, spec 0072).

- **Axis 1, archetype** (`archetype`) plus **method family**
  (`method_family_id`, ties the archetype to a specific
  `nightcap/case_taxonomy/method_families.json` entry so generated
  evidence stays coherent with the authored crime, a poisoning case
  never draws a suffocation trace)
- **Axis 2, clue-chain pattern** (`clue_chain_pattern`)
- **Axis 3, lie shapes per suspect role** (`lie_shapes_by_role`)
- **Axis 4, reveal shape** (`reveal_shape`)

Axes 5 (evidence text) and 6 (character names, motives, secrets,
relationships) are GENERATED from `nightcap/case_taxonomy/` (see that
folder's README) and assembled into the case-truth fact graph
(`ResolvedCase.facts`, see `engine/case/README.md`).

## v1 launch skeleton set

- `locked_room_poisoning.json` (method family: `poison`)
- `alibi_collapse.json` (method family: `suffocation`)
- `pre_conspiracy_fall.json` (method family: `fall`)

Adding a new skeleton: author the four axes plus a `method_family_id`
that names a real entry in `method_families.json`, run
`pytest engine/tests/test_case_skeleton_content.py -v`, then the
resolver picks it up automatically.

## Suspect archetype-roles (used by `lie_shapes_by_role`)

Inherited from the Imposter Variant bible section 3:
- `intimate`, closest to victim
- `deflector`, hiding something unrelated
- `observer`, social edges, sees what others miss
- `obvious_suspect`, surface-level motive everyone recognizes
