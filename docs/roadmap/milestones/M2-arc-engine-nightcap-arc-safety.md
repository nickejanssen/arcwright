# M2: Arc Engine + Nightcap Arc + Safety

**Status:** Planned  
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

- Nightcap arc runs all three beats in the harness
- Killer is assigned
- Reveal fires
- AI dialogue never leaks knowledge state
- L1 hard stops and L2 classification fire before generation
