# Status

**Accepted** (2026-06-14)

---

# Context

Three prior facts converged into this decision:

1. **Product decision is durable and explicit.** D-053 ("Story Circle is a functional platform-native 8-beat template, not decorative metadata") and the May 15, 2026 Nightcap eight-beat decision in `docs/product/decisions-log.csv` commit Nightcap to eight execution beats in 1:1 Story Circle mapping: The Arrival, The Body, The Opening Move, The Dig, The Thread, The Reckoning, The Close, The Truth. The Nightcap story bible Section 4 names and characterizes all eight beats.
2. **AW-205 explicitly deferred the eight-beat encoding.** The AW-205 spec ([docs/specs/0025-aw-205-nightcap-canonical-arc-json.md](../specs/0025-aw-205-nightcap-canonical-arc-json.md)) listed "exactly the eight canonical Nightcap Story Circle beats" as an acceptance criterion, but the merged implementation kept `nightcap/arc.json` at three top-level beats (`introduction`, `investigation`, `reveal`) and recorded the deferral inline via `tone_config.canonical_reference.top_level_beat_model = "three_beat_graph"` with the rationale "Any later internal phase model should be added by a separate task." No follow-up task was ever filed.
3. **M2 exit gate requires eight beats.** AW-214 ([issue #67](https://github.com/nickejanssen/arcwright/issues/67)) and `docs/roadmap/milestones/M2-arc-engine-nightcap-arc-safety.md` both state "Nightcap arc runs all eight beats in the harness" as the M2 exit gate. The first acceptance criterion is "Headless harness completes all eight Nightcap Story Circle beats."

AW-214 is the last open task in M2 and the only remaining gate on closing the M2-B and M2-D epics. Filing a separate precursor task to land the eight-beat encoding before AW-214 would block M2 closure for a full additional cycle with no architectural benefit.

Alternatives considered:

- **File a separate precursor task (AW-2XX).** Cleaner task boundaries but adds a full cycle before M2 can close. Rejected: deferral is six tasks old; the eight-beat work is the M2 exit gate prerequisite by definition.
- **Revise the M2 exit gate to three beats.** Conflicts with D-053 and the May 15 Nightcap decision; would require an overriding ADR plus a story-bible amendment. Rejected: the product decisions are durable, recent, and unambiguous.

---

# Decision

We bundle the eight-beat encoding of `nightcap/arc.json` into AW-214, the M2 Headless Exit Harness task. AW-214 lands the expansion that AW-205 explicitly deferred and adds the headless test that proves the M2 milestone exit gate offline.

Specifically:

1. `nightcap/arc.json` becomes an eight-beat linear graph: `arrival → body → opening_move → dig → thread → reckoning → close → truth`. Each beat carries its Story Circle step (1–8), tension target, structural function, and dramatic purpose from story bible Section 4. The `tone_config.canonical_reference.top_level_beat_model` value flips from `"three_beat_graph"` to `"eight_beat_story_circle"`, with an explicit `beat_to_story_circle_map` recording the 1:1 mapping.
2. The harness reveal-state hook moves from beat `reveal` to beat `truth`. The killer-assignment hook stays at beat 1, now `arrival`. No engine logic changes beyond the constant rename.
3. A new test file `engine/tests/test_m2_exit_harness.py` walks the harness through all eight beats, asserts killer assignment in The Arrival, asserts reveal recording in The Truth, asserts that L1 hard stops and L2 classification run before every main routing call, asserts that no dialogue generation reveals unknown facts, and asserts that no real provider is contacted. Negative tests prove the gates would actually fail if bypassed.
4. Routing assertions cover provider-agnosticism: every model key returned by a generation call is verified to be present in `config/routing_table.json`, and `litellm.acompletion` is patched to raise on any call to confirm zero real provider activity.

---

# Consequences

## Positive consequences

- **M2 exit gate becomes provable.** The harness now walks the canonical eight-beat structure and the headless test enforces every M2 exit criterion: arc execution, killer assignment, reveal firing, safety pre-generation checks, knowledge containment, and budget-first routing.
- **D-053 is honored in code.** The platform now expresses Nightcap's Story Circle structure as data rather than as a deferred TODO. Future story bibles and arc-authoring work can rely on this shape.
- **Future Nightcap work gains a stable, named-beat surface.** Pacing tuning, beat-specific narrator prompts, killer-revelation-window logic, and second-arc design work can all reference specific Story Circle phases instead of guessing which collapsed sub-step they're operating on.
- **AW-205's documented deferral is closed.** The `top_level_beat_model` metadata block is updated rather than left as a stale promise.

## Negative consequences

- **AW-214 is moderately larger than originally sized.** Adds an arc-content rewrite plus mechanical renames in the existing harness, scenario, and batch tests on top of the new exit harness test.
- **Existing harness tests rebind to new transition names.** Anything that referenced `INTRO_TO_INVESTIGATION` or `INVESTIGATION_TO_REVEAL` now references `ARRIVAL_TO_BODY` and `CLOSE_TO_TRUTH`. Mechanical, but a non-trivial diff surface.
- **Beat-graph linearity does not yet exercise branching or convergence.** The eight beats are encoded as a strict linear sequence. Branching (e.g., revelation-window variation) and additional-kill loops remain deferred to later tasks.

## Trade-offs

We gained an accurate eight-beat Nightcap arc, a working M2 exit harness, and a path to closing M2-B and M2-D this cycle. We accepted scope creep on AW-214 to do it.

---

# References

- ADR [0005: L1 hard stop boundary](0005-l1-hard-stop-boundary.md)
- ADR [0004: Pacing telemetry outcome events](0004-pacing-telemetry-outcome-events.md)
- ADR [0002: Harness scenario execution contract](0002-harness-scenario-execution-contract.md)
- ADR [0006: Nightcap Continuity v1.1](0006-nightcap-continuity-v11.md) — confirms "No change to the v1 eight-beat Story Circle skeleton" as a v1.1 non-goal.
- Spec [0025: AW-205 Nightcap canonical arc JSON](../specs/0025-aw-205-nightcap-canonical-arc-json.md) — the spec whose deferred AC this ADR closes.
- Spec [0037: AW-214 M2 Headless Exit Harness](../specs/0037-aw-214-m2-exit-harness.md)
- Roadmap [M2 milestone exit gate](../roadmap/milestones/M2-arc-engine-nightcap-arc-safety.md)
- Story bible [Nightcap Murder Mystery Section 4](../story-bibles/nightcap-murder-mystery.md)
- `docs/product/decisions-log.csv` records D-053 (Story Circle as platform-native 8-beat template) and the May 15, 2026 Nightcap eight-beat decision.
