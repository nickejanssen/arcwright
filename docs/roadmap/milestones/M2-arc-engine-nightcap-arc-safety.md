# M2: Arc Engine + Nightcap Arc + Safety

**Status:** Exit Gate Satisfied (2026-06-14)
**Build-order coverage:** #4 arc execution, #5 safety, #7 character behavior

## Summary

This milestone is the first one that spends meaningful AI tokens. It builds the actual Nightcap arc flow, content-safety enforcement, and character behavior on top of the deterministic core from M1.

## Epics

- [M2-A: Nightcap Web Experience Runtime Decision Gate](../epics/M2-A-external-platform-decision-gate.md)
- [M2-B: Arc Execution Engine](../epics/M2-B-arc-execution-engine.md)
- [M2-C: Nightcap Arc Runtime](../epics/M2-C-nightcap-arc-runtime.md)
- [M2-D: Content Safety Pipeline](../epics/M2-D-content-safety-pipeline.md)
- [M2-E: Character Behavior Engine](../epics/M2-E-character-behavior-engine.md)

## Exit Gate

- Nightcap arc runs all eight beats in the harness
- Killer is assigned through the constrained-random v1 assignment interface
- Reveal fires
- AI dialogue never leaks knowledge state
- L1 hard stops and L2 classification fire before generation

## Exit Evidence

The M2 exit gate was proven offline by AW-214 (see [#67](https://github.com/nickejanssen/arcwright/issues/67)). The proof artifact is `engine/tests/test_m2_exit_harness.py`, which walks all eight Story Circle beats deterministically, asserts killer assignment in The Arrival and reveal recording in The Truth, asserts L1-then-L2-then-main routing ordering with negative tests for each gate, asserts that the knowledge graph is queried before dialogue generation and that unknown-fact leakage is caught, and asserts that every model key resolves through `config/routing_table.json` with `litellm.acompletion` patched to fail. The rationale for landing the eight-beat encoding inside AW-214 (closing the AW-205 deferral) is recorded in ADR [`0007-m2-exit-harness-and-nightcap-eight-beats.md`](../../decisions/0007-m2-exit-harness-and-nightcap-eight-beats.md). The implementation spec is [`docs/specs/0037-aw-214-m2-exit-harness.md`](../../specs/0037-aw-214-m2-exit-harness.md).
