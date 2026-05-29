# M2: Arc Engine + Nightcap Arc + Safety

**Status:** Planned  
**Build-order coverage:** #4 arc execution, #5 safety, #7 character behavior

## Summary

This milestone is the first one that spends meaningful AI tokens. It builds the actual Nightcap arc flow, content-safety enforcement, and character behavior on top of the deterministic core from M1.

## Epics

- Arc execution engine
- Content safety pipeline
- Character behavior engine

## Exit Gate

- Nightcap arc runs all three beats in the harness
- Killer is assigned
- Reveal fires
- AI dialogue never leaks knowledge state
- L1 hard stops and L2 classification fire before generation
