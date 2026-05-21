# Visual scripting committed for H2/H3, schema designed for visual-builder-readiness now

Date: May 7, 2026
Rationale: Visual scripting (Blueprints model) is a Tier 1 differentiator for designer/storyteller adoption. Authoring at MVP is YAML/TOML files plus Python extension hooks. Schema must be deterministic and graph-shaped (no imperative steps embedded; imperative logic goes in registered Python extensions with explicit interfaces). Visual builder UI is H2 or H3 priority work, built on top of the same schema. Schema is source of truth, visual editor is one possible UI.
Section: Cross-cutting
Status: Watchpoint