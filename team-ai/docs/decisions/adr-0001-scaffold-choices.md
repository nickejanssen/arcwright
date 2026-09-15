# ADR 0001: Scaffold choices

- **Status:** Accepted
- **Date:** 2026-09-15

## Context

An interview was run on 2026-09-15 to stand up this team's AI capability.
This record captures the choices that departed from the defaults, so the next
person understands why they were made.

## Decision

- **pre.assessment**: extend — Reuses the agent config and connectors already in place. Nothing new to maintain beyond the knowledge layer.
- **team.size**: 1-3
- **team.surfaces**: coding-agent
- **team.sources**: github
- **team.consumers**: engineers
- **kb.namespaces**: custom
- **arch.topology**: single-repo
- **arch.model_tiers**: strict
- **agents.seed**: no

## Consequences

- Every choice above is reversible except namespace names, which are cheap to
  rename but touch every doc id.
- Deferred items were left at their applied defaults and are revisited at the
  checkpoints recorded in `docs/architecture.md`.

## References

- `docs/architecture.md`
- `docs/strategy.md`
