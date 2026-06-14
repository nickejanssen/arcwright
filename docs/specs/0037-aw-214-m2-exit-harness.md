# AW-214: M2 Headless Nightcap Exit Harness

**Status**: Approved

**Author**: Claude (Arcwright SME) | **Date**: 2026-06-14

---

# References

- Related ADRs: [`docs/decisions/0007-m2-exit-harness-and-nightcap-eight-beats.md`](../decisions/0007-m2-exit-harness-and-nightcap-eight-beats.md), [`docs/decisions/0005-l1-hard-stop-boundary.md`](../decisions/0005-l1-hard-stop-boundary.md)
- Architecture sections: [`docs/architecture/03-arc-execution.md`](../architecture/03-arc-execution.md), [`docs/architecture/15-development-guide.md`](../architecture/15-development-guide.md)
- Related specs: [`docs/specs/0025-aw-205-nightcap-canonical-arc-json.md`](0025-aw-205-nightcap-canonical-arc-json.md), [`docs/specs/0035-aw-212-knowledge-constrained-dialogue-pipeline.md`](0035-aw-212-knowledge-constrained-dialogue-pipeline.md)
- Roadmap milestone: [`docs/roadmap/milestones/M2-arc-engine-nightcap-arc-safety.md`](../roadmap/milestones/M2-arc-engine-nightcap-arc-safety.md)
- Roadmap task: [`docs/roadmap/tasks/AW-214-m2-headless-nightcap-exit-harness.md`](../roadmap/tasks/AW-214-m2-headless-nightcap-exit-harness.md)
- GitHub issue: [#67](https://github.com/nickejanssen/arcwright/issues/67)
- Product decisions: D-053 and the May 15, 2026 Nightcap eight-beat decision in `docs/product/decisions-log.csv`

---

# Overview

AW-214 is the M2 milestone-closing task. It expands `nightcap/arc.json` to the eight canonical Story Circle beats per ADR 0007 and lands a deterministic headless harness that proves every M2 exit-gate criterion offline, without spending real provider tokens.

---

# In Scope

- Replace the three-beat `nightcap/arc.json` (`introduction`, `investigation`, `reveal`) with the canonical eight beats from story bible Section 4: `arrival`, `body`, `opening_move`, `dig`, `thread`, `reckoning`, `close`, `truth`, in a strict linear `beat_graph`.
- Carry per-beat metadata from the story bible into the arc: Story Circle step (1–8), structural function, dramatic purpose, emotional target, information goal, tension target, character emphasis, and beat-level `pacing_config`.
- Update `tone_config.canonical_reference.top_level_beat_model` to `"eight_beat_story_circle"` and record the `beat_to_story_circle_map`.
- Move the harness reveal-state hook from `reveal` to `truth` and the killer-assignment guard from `introduction` to `arrival`. No engine behavior change beyond constant renames.
- Update existing harness/runner, harness/scenario, and harness/batch tests to drive transitions over the new beat IDs and exit conditions.
- Add `engine/tests/test_m2_exit_harness.py`, a new end-to-end test file that proves the M2 exit gate.
- Add ADR `docs/decisions/0007-m2-exit-harness-and-nightcap-eight-beats.md` documenting the scope rationale.
- Update `docs/roadmap/milestones/M2-arc-engine-nightcap-arc-safety.md` to mark the exit gate satisfied and link the ADR and this spec.

---

# Out of Scope

- Non-linear arc structure for Nightcap (branching, additional-kill loops, revelation-window variation). Deferred to later tasks.
- Schema changes to `ArcDefinition`, `BeatDefinition`, or any other engine model.
- New routing keys, new prompts, new safety classifiers, or new content-rails categories.
- Database migrations, new ORM tables, or schema changes.
- API or SDK changes; dashboard work.
- Real-provider integration tests or anything that spends real tokens.
- Nightcap Continuity v1.1 work (recap artifact, group-memory record, durable cross-session state). Deferred per ADR 0006.

---

# Acceptance Criteria

The acceptance criteria mirror the M2 milestone exit gate in
[`docs/roadmap/milestones/M2-arc-engine-nightcap-arc-safety.md`](../roadmap/milestones/M2-arc-engine-nightcap-arc-safety.md).

- [x] **Eight beats traversed end to end.** The harness walks `arrival → body → opening_move → dig → thread → reckoning → close → truth` deterministically. Proven by `test_headless_harness_walks_all_eight_story_circle_beats`.
- [x] **Killer assignment lands in The Arrival.** `runtime_state.role_assignments["killer"]` is populated when participants are set, and `resolved_generative_elements["killer_assignment"]` records the seed and candidate participants. Proven by `test_headless_harness_records_killer_assignment_during_arrival` and confirmed deterministic by `test_same_seed_and_participants_produce_same_killer_assignment`.
- [x] **Reveal fires in The Truth.** `runtime_state.reveal_state.is_revealed is True` with `revealed_by == "authored_conditions"` after the close→truth transition. Proven by `test_headless_harness_records_reveal_when_truth_lands` and `test_full_happy_path_reaches_truth`.
- [x] **Safety pipeline order is enforced before every generation.** L1 hard stops, then L2 classification, then main routing — never out of order. Proven by `test_safety_pipeline_runs_l1_then_l2_before_main_routing`.
- [x] **L1 short-circuits when triggered.** A prompt that trips a hard stop never reaches the main routing layer. Proven by `test_safety_pipeline_short_circuits_on_l1_hard_stop`.
- [x] **L2 short-circuits when classifier blocks.** A prompt blocked by L2 never reaches the main routing layer. Proven by `test_safety_pipeline_short_circuits_on_l2_block`.
- [x] **Knowledge graph is queried before dialogue generation.** Dialogue assembly calls `get_character_knowledge` before any model call. Proven by `test_dialogue_pipeline_queries_knowledge_graph_before_generation`.
- [x] **Knowledge leak detection catches unknown facts.** A canned generation that mentions an unknown fact raises `KnowledgeConstraintViolation`. Proven by `test_dialogue_pipeline_rejects_unknown_fact_leak` and `test_find_unknown_fact_leak_flags_unknown_fact_appearance`.
- [x] **All routing calls resolve to `routing_table.json` keys only.** Every successful generation returns a `model_used` present in `config/routing_table.json` (or a safety-layer sentinel). Proven by `test_end_to_end_harness_records_only_routing_table_models`.
- [x] **Zero real provider tokens spent.** `litellm.acompletion` is patched to raise; if any path reached it, the test would fail. Asserted in every safety, dialogue, and end-to-end test in the file.
- [x] **All existing engine tests still pass.** Full suite is green (199 tests).

---

# Test Plan

- Run `pytest engine/tests/test_m2_exit_harness.py -q` — the new file (10 tests).
- Run `pytest engine/tests/ -q` — the full engine suite, including the migrated harness/runner/scenario/batch tests.
- Run `python -m ruff check engine/harness engine/tests`.
- Run `python -m ruff format --check engine/harness engine/tests`.
- Manually verify the new arc.json validates by loading it: `python -c "from engine.arc.models import ArcDefinition; ArcDefinition.model_validate_json(open('nightcap/arc.json').read())"`.

---

# Risks and Unknowns

**Risks**:

- Existing references to the old beat IDs (`introduction`, `investigation`, `reveal`) in tests not yet covered by this work could break silently. Mitigated by running the full engine suite and by checking the grep results before merging.
- Future tasks that assumed the three-beat shape may need to be revisited. There are no open work items today that depend on the old shape, but downstream telemetry dashboards (out of repo) may carry stale beat IDs.

**Unknowns**:

- Whether downstream M3 work (ContentEvent + bus) will rely on the named beat IDs versus the Story Circle step numbers. Both are now available; either is fine.
- Whether the linear graph will need to evolve for branching at M5 (character behavior hardening) or M6 (qualifying playtests). Deferred until a concrete branching requirement lands.

---

# Open Questions

- None blocking. The eight-beat structure is locked by D-053 and the May 15, 2026 Nightcap decision; the linear traversal is sufficient for M2 exit and for everything M3 needs.
