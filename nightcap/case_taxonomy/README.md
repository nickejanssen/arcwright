# Nightcap Case Taxonomy

Axes 5-6 generative content library (AW-281 / spec 0072). Case
skeletons in `nightcap/case_skeletons/` are the authored *shape*;
this folder is the generative *specifics* the resolver draws from.

Tables:
- `motive_families.json` - motive family + narrative variants
- `method_families.json` - method family + vessels/objects/locations + traces
- `evidence_types.json` - evidence type registry
- `lie_topics.json` - lie topic registry
- `location_pool.json` - per-case place anchors (`id` + display `label`)
- `time_pool.json` - per-case time anchors, ordered (`id` + display `label`);
  the resolver assigns dense `time_ordinal`s from this list's order

Adding to a taxonomy: append entries, run
`pytest engine/tests/test_case_loader.py -v`, and the resolver picks
them up.
