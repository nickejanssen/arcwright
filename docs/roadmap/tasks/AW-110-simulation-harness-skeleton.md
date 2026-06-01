# AW-110: Headless session runner core

**Milestone / Epic:** M1 / E  
**Size:** M  
**Implements:** Arch S3.1, S3.6, S5.2-S5.4, S15.9 #11 (split)  
**Depends on:** AW-105, AW-108

## Build

Create the harness runner core that loads the Nightcap arc, instantiates session state, applies a seeded action stream, and advances the `ArcStateChart` without UI.

## Acceptance Criteria

- [ ] Can start a session and advance it programmatically without UI
- [ ] Session seed is stored in runner state and exposed in the run trace
- [ ] Beat transitions and harness snapshots are recorded for deterministic assertions
- [ ] AI call boundaries remain mockable and optional in the runner core

## Do NOT

- Build scripted synthetic player scenarios yet; that belongs to AW-111
- Build batch statistics or replay UI yet; that belongs to AW-112

## Testing

- Runner initialization and beat-stepping unit tests
- Repeated direct-action run with the same seed and inputs

## Agent Notes

Use current implemented names from Epics C and D: `build_character_generation_context`, `CharacterGenerationContext`, and `engine.routing.logging.generate` if any generation boundary is exercised.
