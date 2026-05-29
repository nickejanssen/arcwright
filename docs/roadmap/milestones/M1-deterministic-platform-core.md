# M1: Deterministic Platform Core

**Status:** Active  
**Build-order coverage:** #1 session models, #2 knowledge graph, #3 routing, harness scaffold

## Summary

This is Tier 1 deterministic infrastructure: minimal AI cost, no narrative-quality dependence, and maximum unit-test coverage. The goal is the platform skeleton every later milestone stands on.

## Epics

- [M1-A: Scaffolding and infrastructure](../epics/M1-A-scaffolding-and-infrastructure.md)
- [M1-B: Data model](../epics/M1-B-data-model.md)
- [M1-C: Knowledge graph core](../epics/M1-C-knowledge-graph-core.md)
- [M1-D: Model routing abstraction](../epics/M1-D-model-routing-abstraction.md)
- [M1-E: Harness scaffold](../epics/M1-E-harness-scaffold.md)

## Exit Gate

- AW-104 migrates cleanly
- AW-105 knowledge graph passes its full unit suite
- AW-107 routing swaps with zero code change
- AW-110 runs a scripted session deterministically
