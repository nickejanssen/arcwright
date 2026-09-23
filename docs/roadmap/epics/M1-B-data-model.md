---
id: productroadmap.roadmap.epics.m1-b-data-model
namespace: product-roadmap
title: "M1-B: Data Model"
owner: Nico Janssen
status: active
review_by: "2026-11-26"
sensitivity: internal
source: authored
tags: []
supersedes: []
---

# M1-B: Data Model

**Milestone:** M1  
**GitHub:** [Issue #4](https://github.com/nickejanssen/arcwright/issues/4)

## What This Epic Covers

Implement the platform data model and the first full migration, including all core platform tables and pgvector-enabled columns required by the architecture.

## Tasks

- [AW-103: SQLAlchemy models for all platform tables](../tasks/AW-103-sqlalchemy-models-for-all-platform-tables.md)
- [AW-104: First full Alembic migration](../tasks/AW-104-first-full-alembic-migration.md)

## Epic Exit Criteria

- All architecture-defined tables have models
- The first full migration upgrades and downgrades cleanly

