# AW-247: Killer Tell Tier Selection By Group Size

**Milestone / Epic:** M5 / M5-E
**Size:** M
**Status:** Planned

## Plain-English Summary

Select which tier of killer tells (surface, mid, deep) the killer expresses based on session player-group size, aligning with architecture §7.5.

## Why This Matters

`docs/architecture/07-character-behavior.md S7.5` organizes killer tells in three tiers and says the generative augmentation layer selects which tier to activate based on player-group size: larger groups receive more surface tells (more people to notice them); smaller groups receive more mid and deep tells (fewer witnesses, harder game). AW-211 carries tells in `behavior_profile.tells`, but tier selection is not implemented. Without this, the killer experience does not calibrate fairly across the v1 4-player floor and larger groups, and one or the other will feel either trivial or impossible.

## Player Impact

At small groups, deep tells (only visible to players actively tracking behavior across the full session) reward the kind of intense investigative play small groups can sustain. At larger groups, surface tells (noticeable on reflection) give more eyes more to spot. The mystery stays winnable and stays interesting at every supported player count.

## Business Value

Closes a v1 architecture commitment. Required before M6 qualifying sessions because the qualifying-session bar includes runs across 4 to 6 players (`docs/roadmap/milestones/M6-first-qualifying-sessions.md`).

## Technical Scope

- Add a tell-tier selector that runs at session start as part of the generative augmentation step on `behavior_profile`.
- Selector reads player count from `Session.player_count` and applies a deterministic distribution: smaller groups weight toward mid and deep tiers; larger groups weight toward surface tier. Concrete weights defined in the spec at implementation time.
- Selector mutates the killer's runtime `behavior_profile.tells` to the activated subset (or annotates per-tell `tier` so the prompt assembly layer can format accordingly).
- No new schema. `behavior_profile.tells` already exists; this task formalizes a `tier` field per tell or a parallel `tells_active` subset, decided in spec.
- No new routing-table entries, no new model strings.

## Acceptance Criteria

- [ ] Killer behavior profile carries a tier annotation per tell (surface, mid, deep) at session start.
- [ ] Tier activation is a deterministic function of player count using documented weights.
- [ ] The same authored tell set produces a noticeably different active subset at 4 players versus 8 players in tests.
- [ ] Active tells reach the generation prompt through the existing identity block path; non-active tells do not.
- [ ] No regression on AW-211 (`behavior_profile` assembly) or AW-213 (initiative + NPC-NPC).

## Tests/Verification

- Unit tests cover tier selection at the v1 4-player floor and at the v1 upper bound.
- Unit tests cover tier annotation in the generated runtime profile.
- Unit tests cover prompt assembly with tier-annotated tells.
- Run `python -m pytest engine/tests/test_killer_tell_tiers.py -q` (file name indicative; final path at implementation time).

## Dependencies

- AW-211 (`behavior_profile.tells`)
- AW-206 (killer assignment must be in place so the killer's profile is identifiable)

## Likely Files Affected

engine/characters, engine/tests

## Must Not Do

- Do not change the existing `Character` schema or `behavior_profile` JSONB structure.
- Do not Nightcap-couple the selector. Player-count input is platform-level.
- Do not place provider or model strings outside `config/routing_table.json` and `engine/routing/router.py`.

## Architecture References

- docs/architecture/07-character-behavior.md S7.5
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task hardens the killer experience across the 4 to 6 player range required for M6 qualifying sessions. State at completion which readiness gate it unlocks.
