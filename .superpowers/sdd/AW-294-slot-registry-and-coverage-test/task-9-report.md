# AW-294 Task 9 Report

Status: complete

Scope covered:
- `engine/tests/test_slot_registry.py`
- `nightcap/content/slot_registry.json`

Acceptance criteria satisfied:
- Every `case_anchor` slot is validated against `CaseAnchor.model_fields`.
- Every `case_field` slot is validated against real case model attributes.
- Every `dressing_pack` slot is validated against `DressingPack.model_fields` or the explicit wrapper-scoped exception.
- `identity_aw279`, `session_timer`, and `scoring` are asserted as the exact declared-but-unbuilt set.
- `occasion` remains sourced from `session` and points to `aesthetic_config.selection_model.occasion`.
- `docs/design/line-libraries/` was not edited.

What changed:
- Expanded the slot-registry test to inspect actual model field surfaces instead of only checking source labels.
- Added a strict declaration check for the unbuilt source set.
- Corrected the registry detail for `callback` to `EvidenceEntry.short_label or CaseFact.value` so it names real case-model attributes.

Verification:
- First run: `python -m pytest engine/tests/test_slot_registry.py -v`
- Red result: `test_case_field_slots_map_to_real_case_model_attributes` failed on `callback` because it said `prior EvidenceEntry or CaseFact`, which did not name a real model attribute.
- Fix applied: updated `nightcap/content/slot_registry.json`.
- Final run: `python -m pytest engine/tests/test_slot_registry.py -v`
- Result: 6 passed.

Concerns:
- None for Task 9.
- The registry coverage is now tied to concrete model surfaces, but any later field renames in `engine/case/models.py` or `engine/dressing/models.py` will require updating this test and possibly the registry entry text.

Fix round 2:
- Regression goal: make the unbuilt-source assertion exact per source, not a merged union.
- Red setup: temporarily asserted `scoring` owned `{"count", "minutes"}`.
- Red command: `python -m pytest engine/tests/test_slot_registry.py -v`
- Red output: `test_declared_but_unbuilt_sources_are_exhaustive` failed with `AssertionError: scoring slots mismatch: expected ['count', 'minutes'], got ['count']`
- Green fix: changed the assertion to expect `scoring -> {"count"}` only.
- Green command: `python -m pytest engine/tests/test_slot_registry.py -v`
- Green output: `6 passed in 10.37s`
- Changed files in this fix round:
  - `engine/tests/test_slot_registry.py`
  - `.superpowers/sdd/AW-294-slot-registry-and-coverage-test/task-9-report.md`
