# Story Bibles

This directory contains active story bibles for Arcwright experiences that still use that authority model, plus compatibility redirects for archived Nightcap bibles.

## Current authorities

- **Nightcap:** `docs/gdd/nightcap/README.md` — the Master GDD is the current Nightcap design source of truth. The two Nightcap files retained in this directory are archive redirects only.
- **Monster RPG:** `monster-rpg.md`
- **Daily Case:** `daily-case.md`

## Nightcap archive

The former Nightcap Couch Race and Imposter Story Bibles are preserved under `docs/archive/nightcap-story-bibles/`. Their old paths remain as redirect stubs so historical ADRs, specs, plans, and Git links do not break.

Archived Nightcap content never overrides the current GDD, even when an archived file contains `Current`, `Accepted`, or other historical authority labels.

## Rules

- For Nightcap gameplay/product-design work, start at `docs/gdd/nightcap/README.md`.
- For other experiences, use the current experience-specific authority identified by this README and the relevant PRD/ADR.
- Implementation changes still require the relevant current specs, architecture constraints, and durable approval evidence; a GDD does not silently rewrite deployed behavior.
- Preserve historical documents rather than deleting them when authority changes.
