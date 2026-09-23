---
id: productroadmap.roadmap.epics.m1-e-harness-scaffold
namespace: product-roadmap
title: "M1-E: Harness Scaffold"
owner: Nico Janssen
status: active
review_by: "2026-11-28"
sensitivity: internal
source: authored
tags: []
supersedes: []
---

# M1-E: Harness Scaffold

**Milestone:** M1  

## What This Epic Covers

Provide the first headless simulation harness that can instantiate, step, script, and repeat a session deterministically without UI.

## Tasks

- [AW-110: Headless session runner core](../tasks/AW-110-simulation-harness-skeleton.md)
- [AW-111: Scripted synthetic player driver](../tasks/AW-111-scripted-synthetic-player-driver.md)
- [AW-112: Deterministic replay and batch runner](../tasks/AW-112-deterministic-replay-and-batch-runner.md)

## Epic Exit Criteria

- A headless deterministic session runner exists
- Synthetic player scenarios are scriptable
- Seeded runs are repeatable
- Batch runner can execute 10 headless sessions without UI

