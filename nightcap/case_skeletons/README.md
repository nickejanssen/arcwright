# Nightcap Case Skeletons

Authored axes 1–4 case content for the Couch Race arc (AW-281 / spec 0072).

- **Axis 1 — archetype** (`archetype`)
- **Axis 2 — clue-chain pattern** (`clue_chain_pattern`)
- **Axis 3 — lie shapes per suspect role** (`lie_shapes_by_role`)
- **Axis 4 — reveal shape** (`reveal_shape`)

Axes 5 (evidence text) and 6 (character names / motives) are GENERATED
from `nightcap/case_taxonomy/` (see that folder's README).

## v1 launch skeleton set

- `locked_room_poisoning.json`
- `alibi_collapse.json`
- `pre_conspiracy_fall.json`

Adding a new skeleton: author the four axes, run
`pytest engine/tests/test_case_skeleton_content.py -v`, then the
resolver picks it up automatically.

## Suspect archetype-roles (used by `lie_shapes_by_role`)

Inherited from the Imposter Variant bible §3:
- `intimate` — closest to victim
- `deflector` — hiding something unrelated
- `observer` — social edges, sees what others miss
- `obvious_suspect` — surface-level motive everyone recognizes
