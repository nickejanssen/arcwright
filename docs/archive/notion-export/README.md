# Notion Export Archive

This directory preserves raw Notion exports and historical workspace artifacts that previously lived directly in `docs/`.

## Purpose

The archive keeps original context available without mixing raw exports into the canonical documentation root.

## Rules

- Do not delete archived files during cleanup.
- Do not treat archived files as canonical when a split doc exists under `docs/prd/`, `docs/architecture/`, `docs/roadmap/`, `docs/specs/`, or `docs/decisions/`.
- Historical relative links inside archived files may still point to old root-level locations. Prefer the canonical folder map in [../../README.md](../../README.md) when navigating active docs.
- If a raw export contains newer context than canonical docs, promote the content into the canonical location and cite the export in the change summary.
- For AI cost control, do not scan this directory unless canonical docs are silent or the task explicitly requires source recovery.
