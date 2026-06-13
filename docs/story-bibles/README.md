# Story Bibles

This directory contains canonical game and experience story bibles.

## Current Bibles

- [Nightcap murder mystery](nightcap-murder-mystery.md)
- [Monster RPG](monster-rpg.md)

## Rules

- Story bibles define experience-specific narrative structure, tone, mechanics, and content boundaries.
- Platform behavior that generalizes beyond one experience belongs in [../architecture/](../architecture/) or [../prd/](../prd/).
- Implementation work should reference the relevant story bible plus the corresponding PRD and architecture sections.
- Keep story-bible updates scoped to product and narrative decisions. Engine contracts belong in specs and architecture docs.
- Keep canonical story bible filenames stable. Put version, status, and last-updated metadata inside the file instead of creating a new file per version.
- Use git history and [../archive/notion-export/](../archive/notion-export/) for older versions or raw source recovery.
